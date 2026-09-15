"""Read-only task readiness command. Uses only the Python standard library."""

import argparse
import json
import os
from pathlib import Path
import sys


STATES = {"pending", "running", "done"}


def load_tasks(directory):
    """Load one JSON object per task file and validate scheduling fields."""
    if not directory.is_dir():
        raise ValueError(f"task directory not found: {directory}")

    tasks = {}
    for path in sorted(directory.glob("*.json")):
        try:
            task = json.loads(path.read_text(encoding="utf-8"))
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["ready"], help="list ready task IDs, one per line")
    parser.parse_args()
    home = os.environ.get("HONEYCOMB_DIR")
    if not home or not Path(home).is_absolute():
        parser.exit(2, "error: HONEYCOMB_DIR must be an absolute path\n")
    try:
        ready = ready_tasks(load_tasks(Path(home) / "tasks"))
    except (ValueError, OSError) as error:
        parser.exit(2, f"error: {error}\n")
    for task_id in ready:
        print(task_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
