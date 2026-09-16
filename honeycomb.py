"""Define, list, start, and record proof for tasks. Python standard library only."""

import argparse
import json
import os
from pathlib import Path
import re
import sys
import tempfile


STATES = {"open", "running", "done"}


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
            raise ValueError(f"{task_id}: state must be open, running, or done")
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


def validate_hierarchy(tasks):
    """Validate parent references and cycles; legacy records are roots."""
    for task_id, task in tasks.items():
        parent = task.get("parent")
        if parent is not None:
            if not isinstance(parent, str) or not parent or any(c.isspace() for c in parent):
                raise ValueError(f"{task_id}: parent must be null or a task ID")
            if parent not in tasks:
                raise ValueError(f"{task_id}: missing parent {parent}")

    # Walk each parent link once, without depending on Python's recursion limit.
    visited = set()
    for task_id in tasks:
        chain = set()
        current = task_id
        while current is not None and current not in visited:
            if current in chain:
                raise ValueError("parent cycle detected")
            chain.add(current)
            current = tasks[current].get("parent")
        visited.update(chain)


def ready_tasks(tasks):
    """Validate hierarchy and dependencies before returning sorted ready IDs."""
    validate_hierarchy(tasks)
    remaining = {}
    dependents = {task_id: [] for task_id in tasks}
    for task_id, task in tasks.items():
        remaining[task_id] = len(task["depends_on"])
        for dependency in task["depends_on"]:
            if dependency not in tasks:
                raise ValueError(f"{task_id}: missing dependency {dependency}")
            if tasks[dependency].get("parent") != task.get("parent"):
                raise ValueError(f"{task_id}: dependency {dependency} is not a sibling")
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
        if task["state"] == "open"
        and (task.get("parent") is None or tasks[task["parent"]]["state"] == "running")
        and all(tasks[dependency]["state"] == "done" for dependency in task["depends_on"])
    )


def validate_proof(proof, *, stored=False):
    """Validate plain-language verification and nullable boolean results."""
    if not isinstance(proof, list) or not proof:
        raise ValueError("proof must be a nonempty list")
    fields = {"condition", "verification"} | ({"result"} if stored else set())
    for number, item in enumerate(proof, 1):
        if not isinstance(item, dict) or set(item) != fields:
            raise ValueError(f"proof item {number}: expected exactly {', '.join(sorted(fields))}")
        condition = item["condition"]
        if not isinstance(condition, str) or not condition.strip():
            raise ValueError(f"proof item {number}: condition must be a nonempty string")
        verification = item["verification"]
        if not isinstance(verification, str) or not verification.strip():
            raise ValueError(f"proof item {number}: verification must be a nonempty string")
        if stored and item["result"] is not None and type(item["result"]) is not bool:
            raise ValueError(f"proof item {number}: result must be null, true, or false")


def define_task(directory, task):
    """Validate an approved task and store it without replacing existing records."""
    fields = {"id", "outcome", "scope", "parent", "depends_on", "proof"}
    if not isinstance(task, dict) or set(task) != fields:
        raise ValueError("expected exactly: id, outcome, scope, parent, depends_on, proof")
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
    validate_proof(proof)

    tasks = load_tasks(directory) if directory.exists() else {}
    ready_tasks(tasks)
    if task_id in tasks:
        raise ValueError(f"duplicate task id: {task_id}")
    record = {
        **task,
        "state": "open",
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
    replace_task(paths[task_id], record)


def replace_task(path, record):
    """Replace a record atomically; concurrent writers remain unsupported."""
    content = json.dumps(record, indent=2) + "\n"
    temporary = None
    try:
        # Write fully before replacing; this is not a concurrent-writer lock.
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent,
            prefix=".task-", suffix=".tmp", delete=False,
        ) as output:
            temporary = Path(output.name)
            output.write(content)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def prove_task(directory, task_id, *, item=None, result=None):
    """Show proof or record one observed result; never execute instructions."""
    paths = {}
    tasks = load_tasks(directory, paths=paths)
    ready_tasks(tasks)
    if task_id not in tasks:
        raise ValueError(f"unknown task: {task_id}")
    task = tasks[task_id]
    if task["state"] != "running":
        raise ValueError(f"task is not running: {task_id}")
    if any(
        child.get("parent") == task_id and child["state"] != "done"
        for child in tasks.values()
    ):
        raise ValueError(f"task has unfinished children: {task_id}")
    proof = task.get("proof")
    validate_proof(proof, stored=True)
    if item is not None:
        if type(item) is not int or not 1 <= item <= len(proof):
            raise ValueError("item must name a proof item number (1-based)")
        if result is not None and type(result) is not bool:
            raise ValueError("result must be null, true, or false")
        proof[item - 1]["result"] = result
        replace_task(paths[task_id], task)
    elif result is not None:
        raise ValueError("result requires item")

    for number, entry in enumerate(proof, 1):
        print(f"{number}: {entry['condition']}")
        print(f"   verification: {entry['verification']}")
        print(f"   result: {json.dumps(entry['result'])}")
    return 0 if all(entry["result"] is True for entry in proof) else 1


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
    commands.add_parser("define", help="define a task from JSON stdin")
    start = commands.add_parser("start", help="mark a ready task running")
    start.add_argument("id", help="task ID")
    prove = commands.add_parser("prove", help="show proof or record one observed result")
    prove.add_argument("id", help="task ID")
    prove.add_argument("--item", type=int, help="1-based proof item number")
    prove.add_argument("--result", choices=("true", "false", "null"), help="observed result")
    args = parser.parse_args()
    if args.command == "prove" and ((args.item is None) != (args.result is None)):
        parser.error("--item and --result must be supplied together")
    home = os.environ.get("HONEYCOMB_DIR")
    if not home or not Path(home).is_absolute():
        parser.exit(2, "error: HONEYCOMB_DIR must be an absolute path\n")
    try:
        directory = Path(home) / "tasks"
        if args.command == "define":
            task = json.load(sys.stdin, object_pairs_hook=unique_object, parse_constant=invalid_constant)
            define_task(directory, task)
            return 0
        if args.command == "start":
            start_task(directory, args.id)
            return 0
        if args.command == "prove":
            return prove_task(
                directory, args.id, item=args.item,
                result=json.loads(args.result) if args.result is not None else None,
            )
        ready = ready_tasks(load_tasks(directory))
    except (ValueError, OSError) as error:
        parser.exit(2, f"error: {error}\n")
    for task_id in ready:
        print(task_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
