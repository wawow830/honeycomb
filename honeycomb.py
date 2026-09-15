"""Create, list, and start tasks. Uses only the Python standard library."""

import argparse
import json
import os
from pathlib import Path
import re
import sys
import tempfile


STATES = {"pending", "running", "done"}


def load_tasks(directory, *, paths=None):
    """Validate stored tasks; optionally collect their source paths by ID."""
    if not directory.is_dir():
        raise ValueError(f"task directory not found: {directory}")

    tasks = {}
    for path in sorted(directory.glob("*.json")):
        try:
            task = json.loads(
                path.read_text(encoding="utf-8"),
                object_pairs_hook=unique_object,
                parse_constant=invalid_constant,
            )
        except (ValueError, OSError) as error:
            raise ValueError(f"{path.name}: {error}") from error
        if not isinstance(task, dict):
            raise ValueError(f"{path.name}: expected a task object")
        task_id = task.get("id")
        if not isinstance(task_id, str) or not task_id or any(c.isspace() for c in task_id):
            raise ValueError(f"{path.name}: id must be a nonempty string without whitespace")
        if task_id in tasks:
            raise ValueError(f"duplicate task id: {task_id}")
        if not isinstance(task.get("state"), str) or task["state"] not in STATES:
            raise ValueError(f"{task_id}: state must be pending, running, or done")
        dependencies = task.get("depends_on")
        if not isinstance(dependencies, list) or any(
            not isinstance(dependency, str) or not dependency for dependency in dependencies
        ):
            raise ValueError(f"{task_id}: depends_on must be a list of task IDs")
        if len(set(dependencies)) != len(dependencies):
            raise ValueError(f"{task_id}: duplicate dependency")
        tasks[task_id] = task
        if paths is not None:
            paths[task_id] = path
    return tasks


def ready_tasks(tasks):
    """Validate the entire dependency graph before returning sorted ready IDs."""
    remaining = {}
    dependents = {task_id: [] for task_id in tasks}
    for task_id, task in tasks.items():
        remaining[task_id] = len(task["depends_on"])
        for dependency in task["depends_on"]:
            if dependency not in tasks:
                raise ValueError(f"{task_id}: missing dependency {dependency}")
            dependents[dependency].append(task_id)

    queue = [task_id for task_id, count in remaining.items() if count == 0]
    visited = 0
    while queue:
        task_id = queue.pop()
        visited += 1
        for dependent in dependents[task_id]:
            remaining[dependent] -= 1
            if remaining[dependent] == 0:
                queue.append(dependent)
    if visited != len(tasks):
        raise ValueError("dependency cycle detected")

    return sorted(
        task_id
        for task_id, task in tasks.items()
        if task["state"] == "pending"
        and all(tasks[dependency]["state"] == "done" for dependency in task["depends_on"])
    )


def add_task(directory, task):
    """Validate an approved task and store it without replacing existing records."""
    fields = {"id", "outcome", "scope", "depends_on", "proof"}
    if not isinstance(task, dict) or set(task) != fields:
        raise ValueError("expected exactly: id, outcome, scope, depends_on, proof")
    task_id = task["id"]
    if not isinstance(task_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}", task_id):
        raise ValueError("id must be 1–128 letters, digits, underscores, or hyphens; start with a letter or digit")
    for field in ("outcome", "scope"):
        if not isinstance(task[field], str) or not task[field].strip():
            raise ValueError(f"{field} must be a nonempty string")
    dependencies = task["depends_on"]
    if not isinstance(dependencies, list) or any(
        not isinstance(dependency, str) or not dependency or any(c.isspace() for c in dependency)
        for dependency in dependencies
    ):
        raise ValueError("depends_on must be a list of task IDs")
    if len(set(dependencies)) != len(dependencies):
        raise ValueError("duplicate dependency")
    proof = task["proof"]
    if not isinstance(proof, list) or not proof:
        raise ValueError("proof must be a nonempty list")
    for item in proof:
        if not isinstance(item, dict) or set(item) != {"condition", "verification"}:
            raise ValueError("each proof item must contain exactly condition and verification")
        if any(not isinstance(value, str) or not value.strip() for value in item.values()):
            raise ValueError("condition and verification must be nonempty strings")

    tasks = load_tasks(directory) if directory.exists() else {}
    ready_tasks(tasks)
    if task_id in tasks:
        raise ValueError(f"duplicate task id: {task_id}")
    record = {
        **task,
        "state": "pending",
        "proof": [{**item, "result": None} for item in proof],
    }
    ready_tasks({**tasks, task_id: record})
    content = json.dumps(record, indent=2) + "\n"
    directory.mkdir(parents=True, exist_ok=True)
    # Exclusive creation protects existing paths, even if filenames differ from IDs.
    with (directory / f"{task_id}.json").open("x", encoding="utf-8") as output:
        output.write(content)


def start_task(directory, task_id):
    """Mark one ready task running, preserving its other fields."""
    paths = {}
    tasks = load_tasks(directory, paths=paths)
    ready = ready_tasks(tasks)
    if task_id not in tasks:
        raise ValueError(f"unknown task: {task_id}")
    if task_id not in ready:
        raise ValueError(f"task is not ready: {task_id}")

    record = {**tasks[task_id], "state": "running"}
    content = json.dumps(record, indent=2) + "\n"
    temporary = None
    try:
        # Write fully before replacing; this is not a concurrent-writer lock.
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=directory,
            prefix=".start-", suffix=".tmp", delete=False,
        ) as output:
            temporary = Path(output.name)
            output.write(content)
        os.replace(temporary, paths[task_id])
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def unique_object(pairs):
    """Reject ambiguous JSON input instead of silently keeping the last value."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def invalid_constant(value):
    raise ValueError(f"invalid JSON constant: {value}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("ready", help="list ready task IDs")
    commands.add_parser("add", help="add a task from JSON stdin")
    start = commands.add_parser("start", help="mark a ready task running")
    start.add_argument("id", help="task ID")
    args = parser.parse_args()
    home = os.environ.get("HONEYCOMB_DIR")
    if not home or not Path(home).is_absolute():
        parser.exit(2, "error: HONEYCOMB_DIR must be an absolute path\n")
    try:
        directory = Path(home) / "tasks"
        if args.command == "add":
            task = json.load(sys.stdin, object_pairs_hook=unique_object, parse_constant=invalid_constant)
            add_task(directory, task)
            return 0
        if args.command == "start":
            start_task(directory, args.id)
            return 0
        ready = ready_tasks(load_tasks(directory))
    except (ValueError, OSError) as error:
        parser.exit(2, f"error: {error}\n")
    for task_id in ready:
        print(task_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
