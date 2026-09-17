"""Define, execute, prove, and integrate tasks. Standard library only."""

import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile


STATES = {"open", "running", "done"}
TASK_ID = r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}"


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
    if not isinstance(task_id, str) or not re.fullmatch(TASK_ID, task_id):
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
    parent = record["parent"]
    if parent is not None and tasks[parent]["state"] == "done":
        raise ValueError(f"parent is done: {parent}")
    content = json.dumps(record, indent=2) + "\n"
    directory.mkdir(parents=True, exist_ok=True)
    # Exclusive creation protects existing paths, even if filenames differ from IDs.
    with (directory / f"{task_id}.json").open("x", encoding="utf-8") as output:
        output.write(content)


def git(repository, *arguments):
    """Run Git without a shell or interactive input."""
    result = subprocess.run(
        ["git", "--no-optional-locks", "-C", str(repository), *arguments],
        stdin=subprocess.DEVNULL, capture_output=True, text=True,
    )
    if result.returncode:
        raise ValueError(result.stderr.strip() or f"git {arguments[0]} failed")
    return result.stdout.strip()


def git_is_ancestor(repository, ancestor, descendant):
    """Distinguish a missing ancestor from a Git failure."""
    result = subprocess.run(
        ["git", "--no-optional-locks", "-C", str(repository),
         "merge-base", "--is-ancestor", ancestor, descendant],
        stdin=subprocess.DEVNULL, capture_output=True, text=True,
    )
    if result.returncode not in (0, 1):
        raise ValueError(result.stderr.strip() or "git merge-base failed")
    return result.returncode == 0


def task_branch(task_id):
    """Use the same safe identifier contract for branches and workspace names."""
    if not re.fullmatch(TASK_ID, task_id):
        raise ValueError(f"task ID cannot be used for execution: {task_id}")
    return f"honeycomb/{task_id}"


def branch_exists(repository, branch):
    # Listing refs avoids treating an unexpected Git error as a missing branch.
    refs = git(repository, "for-each-ref", "--format=%(refname)", "refs/heads/")
    return f"refs/heads/{branch}" in refs.splitlines()


def discard_workspace(repository, workspace, branch):
    """Roll back only newly created resources; never force-delete a worktree."""
    entries = git(repository, "worktree", "list", "--porcelain", "-z").split("\0")
    if f"worktree {workspace}" in entries:
        git(repository, "worktree", "remove", str(workspace))
    if os.path.lexists(workspace):
        raise ValueError(f"incomplete workspace needs inspection: {workspace}")
    if branch_exists(repository, branch):
        git(repository, "branch", "-D", branch)


def discover_repository():
    """Resolve the current project's main checkout, including from linked worktrees."""
    current = Path.cwd()
    if git(current, "rev-parse", "--is-inside-work-tree") != "true":
        raise ValueError("run Honeycomb inside a Git working tree")
    # Git lists the main worktree first; linked worktrees share its storage.
    first = git(current, "worktree", "list", "--porcelain", "-z").split("\0\0", 1)[0].split("\0")
    if "bare" in first:
        raise ValueError("Honeycomb requires a non-bare main checkout")
    if not first[0].startswith("worktree "):
        raise ValueError("cannot locate the main checkout")
    repository = Path(first[0].removeprefix("worktree ")).resolve()
    if git(repository, "rev-parse", "--is-inside-work-tree") != "true":
        raise ValueError("cannot discover main checkout; separate Git directories are not supported")
    return repository


def task_repository(directory):
    """Resolve the repository from shared storage, not the caller's directory."""
    repository = directory.resolve().parent.parent
    if Path(git(repository, "rev-parse", "--show-toplevel")).resolve() != repository:
        raise ValueError("task storage must be inside .honeycomb at the main checkout root")
    return repository


def current_proof_snapshot(directory, task):
    """Return task/target commits, or None if the task workspace is dirty."""
    branch = task_branch(task["id"])
    target = "main" if task.get("parent") is None else task_branch(task["parent"])
    repository = task_repository(directory)
    workspace = directory.resolve().parent / "worktrees" / task["id"]
    if Path(git(workspace, "rev-parse", "--show-toplevel")).resolve() != workspace:
        raise ValueError(f"not the task workspace: {workspace}")
    common = ("rev-parse", "--path-format=absolute", "--git-common-dir")
    if Path(git(workspace, *common)).resolve() != Path(git(repository, *common)).resolve():
        raise ValueError(f"task workspace belongs to another repository: {workspace}")
    if git(workspace, "symbolic-ref", "-q", "HEAD") != f"refs/heads/{branch}":
        raise ValueError(f"task workspace must be on {branch}")
    snapshot = {
        "task": git(repository, "rev-parse", "--verify", f"refs/heads/{branch}^{{commit}}"),
        "target": git(repository, "rev-parse", "--verify", f"refs/heads/{target}^{{commit}}"),
    }
    if git(workspace, "status", "--porcelain", "--untracked-files=all", "--ignore-submodules=none"):
        return None
    return snapshot


def execute_task(directory, task_id):
    """Prepare a ready task's branch/worktree, then mark it running."""
    paths = {}
    tasks = load_tasks(directory, paths=paths)
    ready = ready_tasks(tasks)
    if task_id not in tasks:
        raise ValueError(f"unknown task: {task_id}")
    if task_id not in ready:
        raise ValueError(f"task is not ready: {task_id}")

    task = tasks[task_id]
    branch = task_branch(task_id)
    target = "main" if task.get("parent") is None else task_branch(task["parent"])
    home = directory.resolve().parent
    repository = task_repository(directory)
    # Resolve an explicit local branch, never an ambiguous tag or remote ref.
    git(repository, "rev-parse", "--verify", f"refs/heads/{target}^{{commit}}")
    workspace = home / "worktrees" / task_id
    if branch_exists(repository, branch):
        raise ValueError(f"task branch already exists: {branch}")
    if os.path.lexists(workspace):
        raise ValueError(f"task workspace already exists: {workspace}")

    workspace.parent.mkdir(parents=True, exist_ok=True)
    try:
        git(repository, "worktree", "add", "--no-track", "-b", branch,
            str(workspace), f"refs/heads/{target}")
        replace_task(paths[task_id], {**task, "state": "running"})
    except (ValueError, OSError) as error:
        try:
            discard_workspace(repository, workspace, branch)
        except (ValueError, OSError) as cleanup_error:
            raise ValueError(
                f"{error}; cleanup failed: {cleanup_error}; inspect {workspace} before retrying"
            ) from error
        raise
    return workspace


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


def require_provable(task, tasks):
    """Require a running task, finished children, and valid proof structure."""
    task_id = task["id"]
    if task["state"] != "running":
        raise ValueError(f"task is not running: {task_id}")
    if any(
        child.get("parent") == task_id and child["state"] != "done"
        for child in tasks.values()
    ):
        raise ValueError(f"task has unfinished children: {task_id}")
    validate_proof(task.get("proof"), stored=True)


def prove_task(directory, task_id, *, item=None, result=None):
    """Bind proof to clean commits, then show or record observed results."""
    paths = {}
    tasks = load_tasks(directory, paths=paths)
    ready_tasks(tasks)
    if task_id not in tasks:
        raise ValueError(f"unknown task: {task_id}")
    task = tasks[task_id]
    require_provable(task, tasks)
    proof = task["proof"]
    if item is not None:
        if type(item) is not int or not 1 <= item <= len(proof):
            raise ValueError("item must name a proof item number (1-based)")
        if result is not None and type(result) is not bool:
            raise ValueError("result must be null, true, or false")
    elif result is not None:
        raise ValueError("result requires item")

    snapshot = current_proof_snapshot(directory, task)
    rejection = None
    if snapshot is None:
        rejection = "task workspace has uncommitted changes; commit or remove them before proof"
    elif not git_is_ancestor(task_repository(directory), snapshot["target"], snapshot["task"]):
        snapshot = None
        rejection = "task branch does not include current target; merge target into task, then retry proof"
    changed = task.get("proof_snapshot") != snapshot
    # Missing bindings never authorize old passes. Dirty or uncombined work
    # invalidates all results, including recorded human judgments.
    if changed or (snapshot is None and any(entry["result"] is not None for entry in proof)):
        for entry in proof:
            entry["result"] = None
        task["proof_snapshot"] = snapshot
        replace_task(paths[task_id], task)
    if rejection is not None:
        raise ValueError(rejection)
    if item is not None:
        if changed:
            raise ValueError("proof snapshot changed; repeat verification before recording results")
        proof[item - 1]["result"] = result
        replace_task(paths[task_id], task)

    for number, entry in enumerate(proof, 1):
        print(f"{number}: {entry['condition']}")
        print(f"   verification: {entry['verification']}")
        print(f"   result: {json.dumps(entry['result'])}")
    return 0 if all(entry["result"] is True for entry in proof) else 1


@contextmanager
def integration_lock(repository, target):
    """Serialize integrations by target, including across shared-storage paths."""
    try:
        import fcntl
    except ImportError as error:
        raise ValueError("integration requires Unix advisory file locks (fcntl.flock)") from error
    common = Path(git(repository, "rev-parse", "--path-format=absolute", "--git-common-dir"))
    path = common / "honeycomb-locks" / f"{target}.lock"
    path.parent.mkdir(parents=True, exist_ok=True)
    # Keep the inode: unlinking it would let waiters lock different files.
    with path.open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def target_workspace(repository, target):
    """Find the target checkout without switching the caller's branch."""
    workspaces = []
    path = None
    for field in git(repository, "worktree", "list", "--porcelain", "-z").split("\0"):
        if field.startswith("worktree "):
            path = Path(field.removeprefix("worktree "))
        elif field == f"branch refs/heads/{target}":
            workspaces.append(path)
    if len(workspaces) > 1:
        raise ValueError(f"target is checked out in multiple worktrees: {target}")
    return workspaces[0] if workspaces else None


def require_integration_workspace(workspace):
    """Do not disturb local work or an unfinished Git operation."""
    if git(workspace, "status", "--porcelain", "--untracked-files=all", "--ignore-submodules=none"):
        raise ValueError(f"integration workspace has uncommitted changes: {workspace}")
    for name in ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "rebase-merge",
                 "rebase-apply", "sequencer", "BISECT_START"):
        path = Path(git(workspace, "rev-parse", "--path-format=absolute", "--git-path", name))
        if path.exists():
            raise ValueError(f"integration workspace has an unfinished Git operation: {workspace}")


def integrate_task(directory, task_id):
    """Fast-forward the target to the exact proven commit, then mark done."""
    tasks = load_tasks(directory)
    ready_tasks(tasks)
    if task_id not in tasks:
        raise ValueError(f"unknown task: {task_id}")
    parent = tasks[task_id].get("parent")
    target = "main" if parent is None else task_branch(parent)
    repository = task_repository(directory)

    with integration_lock(repository, target):
        # A previous integration may have changed both Git and records while waiting.
        paths = {}
        tasks = load_tasks(directory, paths=paths)
        ready_tasks(tasks)
        if task_id not in tasks:
            raise ValueError(f"unknown task: {task_id}")
        task = tasks[task_id]
        if task.get("parent") != parent:
            raise ValueError("task parent changed; retry integration")
        require_provable(task, tasks)
        if not all(item["result"] is True for item in task["proof"]):
            raise ValueError(f"task proof is incomplete or failed: {task_id}")
        snapshot = current_proof_snapshot(directory, task)
        if snapshot is None or task.get("proof_snapshot") != snapshot:
            raise ValueError("proof snapshot changed or workspace is dirty; repeat proof before integration")
        if not git_is_ancestor(repository, snapshot["target"], snapshot["task"]):
            raise ValueError("task branch does not include current target; merge target into task, then retry proof")

        workspace = directory.resolve().parent / "worktrees" / task_id
        require_integration_workspace(workspace)
        checkout = target_workspace(repository, target)
        if checkout is not None:
            require_integration_workspace(checkout)
            # No merge commit, autostash, ignored-file overwrite, or mutating hooks.
            git(checkout, "-c", "core.hooksPath=/dev/null", "-c", "submodule.recurse=false",
                "-c", f"branch.{target}.mergeOptions=",
                "merge", "--ff-only", "--no-autostash", "--no-overwrite-ignore",
                "--no-edit", snapshot["task"])
        else:
            # No index/worktree to update; compare-and-swap the explicit local ref.
            git(repository, "update-ref", f"refs/heads/{target}",
                snapshot["task"], snapshot["target"])

        try:
            expected = {"task": snapshot["task"], "target": snapshot["task"]}
            if current_proof_snapshot(directory, task) != expected:
                raise ValueError("task or target changed during integration")
            if checkout is not None:
                require_integration_workspace(checkout)
            replace_task(paths[task_id], {**task, "state": "done"})
        except (ValueError, OSError) as error:
            raise ValueError(
                f"target advanced but task was not marked done: {error}; "
                "inspect the target, then repeat proof and integration"
            ) from error


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
    execute = commands.add_parser("execute", help="prepare a ready task's branch and worktree")
    execute.add_argument("id", help="task ID")
    prove = commands.add_parser("prove", help="show proof or record one observed result")
    prove.add_argument("id", help="task ID")
    prove.add_argument("--item", type=int, help="1-based proof item number")
    prove.add_argument("--result", choices=("true", "false", "null"), help="observed result")
    integrate = commands.add_parser("integrate", help="fast-forward the target to the proven task")
    integrate.add_argument("id", help="task ID")
    args = parser.parse_args()
    if args.command == "prove" and ((args.item is None) != (args.result is None)):
        parser.error("--item and --result must be supplied together")
    try:
        directory = discover_repository() / ".honeycomb" / "tasks"
        if args.command == "define":
            task = json.load(sys.stdin, object_pairs_hook=unique_object, parse_constant=invalid_constant)
            define_task(directory, task)
            return 0
        if args.command == "execute":
            print(execute_task(directory, args.id))
            return 0
        if args.command == "prove":
            return prove_task(
                directory, args.id, item=args.item,
                result=json.loads(args.result) if args.result is not None else None,
            )
        if args.command == "integrate":
            integrate_task(directory, args.id)
            return 0
        try:
            directory.stat()
        except FileNotFoundError:
            if directory.is_symlink() or (directory.parent.is_symlink() and not directory.parent.exists()):
                raise ValueError(f"task directory not found: {directory}")
            ready = []
        else:
            ready = ready_tasks(load_tasks(directory))
    except (ValueError, OSError) as error:
        parser.exit(2, f"error: {error}\n")
    for task_id in ready:
        print(task_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
