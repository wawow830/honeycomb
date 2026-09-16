import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from git_support import git, init_repository


COMMAND = Path(__file__).resolve().parents[1] / "honeycomb.py"


class HierarchyTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.home = self.root / ".honeycomb"
        self.tasks = self.home / "tasks"
        self.tasks.mkdir(parents=True)
        init_repository(self.root)

    def task(self, task_id, parent=None, dependencies=()):
        return {
            "id": task_id, "outcome": "Example", "scope": "Example",
            "parent": parent, "depends_on": list(dependencies),
            "proof": [{"condition": "Works", "verification": "Run tests; require exit 0."}],
        }

    def store(self, task_id, parent=None, dependencies=(), state="open", filename=None):
        task = self.task(task_id, parent, dependencies)
        task["state"] = state
        task["proof"][0]["result"] = None
        path = self.tasks / (filename or f"{task_id}.json")
        path.write_text(json.dumps(task))
        return path

    def run_command(self, *args, task=None):
        return subprocess.run(
            [sys.executable, str(COMMAND), *args],
            input=json.dumps(task) if task is not None else None,
            cwd=self.root, env={**os.environ, "HONEYCOMB_DIR": str(self.home)},
            capture_output=True, text=True, timeout=10,
        )

    def snapshot(self):
        return {
            str(path.relative_to(self.root)): (path.read_bytes(), path.stat().st_mtime_ns)
            for path in self.root.rglob("*") if path.is_file()
        }

    def assert_rejected(self, *args, task=None, message=None):
        before = self.snapshot()
        result = self.run_command(*args, task=task)
        self.assertEqual(result.returncode, 2, result)
        self.assertEqual(result.stdout, "")
        self.assertNotIn("Traceback", result.stderr)
        if message:
            self.assertIn(message, result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_define_root_child_and_grandchild(self):
        for task_id, parent in (("T", None), ("A", "T"), ("A1", "A")):
            with self.subTest(task_id=task_id):
                task = self.task(task_id, parent)
                before = self.snapshot()
                result = self.run_command("define", task=task)
                self.assertEqual(result.returncode, 0, result.stderr)
                path = self.tasks / f"{task_id}.json"
                record = json.loads(path.read_text())
                self.assertEqual(record, {
                    **task, "state": "open",
                    "proof": [{**item, "result": None} for item in task["proof"]],
                })
                after = self.snapshot()
                del after[str(path.relative_to(self.root))]
                self.assertEqual(after, before)
        self.assertEqual(self.run_command("ready").stdout, "T\n")
        for task_id, ready in (("T", "A\n"), ("A", "A1\n"), ("A1", "")):
            result = self.run_command("execute", task_id)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(self.run_command("ready").stdout, ready)

    def test_define_rejects_children_under_done_parents_without_writes(self):
        self.store("root", state="running")
        self.store("unrelated")
        for ancestor in (None, "root"):
            with self.subTest(ancestor=ancestor):
                self.store("parent", ancestor, state="done", filename="different.json")
                self.assert_rejected(
                    "define", task=self.task("late-child", "parent"),
                    message="parent is done: parent",
                )
                self.assertFalse((self.tasks / "late-child.json").exists())

    def test_sibling_dependencies_at_each_depth(self):
        self.store("T", state="running")
        self.store("A", "T", state="running")
        self.store("A1", "A", state="done")
        for task in (self.task("U", dependencies=["T"]),
                     self.task("B", "T", ["A"]),
                     self.task("A2", "A", ["A1"])):
            result = self.run_command("define", task=task)
            self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_command("ready")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "A2\n")
        self.store("A2", "A", ["A1"], state="done")
        self.store("A", "T", state="done")
        self.assertEqual(self.run_command("ready").stdout, "B\n")

    def test_cross_branch_and_ancestor_dependencies_rejected_on_define(self):
        self.store("T")
        self.store("A", "T")
        self.store("B", "T")
        self.store("A1", "A")
        for parent, dependencies in (("B", ["A1"]), ("A", ["A"]),
                                     (None, ["A"]), ("T", ["A1"])):
            with self.subTest(parent=parent, dependencies=dependencies):
                self.assert_rejected("define", task=self.task("new", parent, dependencies),
                                     message="not a sibling")

    def test_new_task_requires_parent_and_rejects_invalid_parent(self):
        task = self.task("new")
        del task["parent"]
        self.assert_rejected("define", task=task, message="expected exactly")
        for parent in ("missing", "new", "", "two words", 0, False, [], {}):
            with self.subTest(parent=parent):
                self.assert_rejected("define", task=self.task("new", parent))

    def test_invalid_parent_does_not_create_storage(self):
        self.tasks.rmdir()
        self.home.rmdir()
        self.assert_rejected("define", task=self.task("new", "missing"), message="missing parent")
        self.assertFalse(self.home.exists())

    def test_invalid_hierarchy_blocks_every_command_without_execution(self):
        path = self.store("target", state="running")
        task = json.loads(path.read_text())
        task["proof"] = [
            {"condition": "Must not execute", "verification": "touch executed", "result": None},
            {"condition": "Review", "verification": "Ask the developer to approve", "result": None},
        ]
        path.write_text(json.dumps(task))
        self.store("available")
        cases = [
            ({"A": ("missing", [])}, "missing parent"),
            ({"A": ("A", [])}, "parent cycle"),
            ({"A": ("B", []), "B": ("C", []), "C": ("A", [])}, "parent cycle"),
            ({"A": (None, []), "B": ("A", ["A"])}, "not a sibling"),
            ({"A": (None, []), "B": (None, []), "C": ("A", []), "D": ("B", ["C"])}, "not a sibling"),
            ({"A": ("target", ["B"]), "B": ("target", ["A"])}, "dependency cycle"),
        ]
        cases.extend(({"A": (parent, [])}, "parent must be")
                     for parent in ("", "two words", 7, False, [], {}))
        for records, message in cases:
            with self.subTest(records=records):
                for task_id, (parent, dependencies) in records.items():
                    # Done states must not hide invalid links.
                    self.store(task_id, parent, dependencies, state="done")
                for args in (("ready",), ("execute", "available"), ("prove", "target"),
                             ("prove", "target", "--item", "2", "--result", "true"), ("define",)):
                    self.assert_rejected(*args, task=self.task("new"), message=message)
                self.assertFalse((self.root / "executed").exists())
                for task_id in records:
                    (self.tasks / f"{task_id}.json").unlink()

    def test_parent_resolves_by_id_not_filename_or_load_order(self):
        self.store("child", "parent", filename="a-child.json")
        self.store("parent", state="running", filename="z-parent.json")
        result = self.run_command("ready")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "child\n")

    def test_legacy_roots_are_compatible_and_not_rewritten(self):
        path = self.store("legacy", state="done")
        record = json.loads(path.read_text())
        del record["parent"]
        path.write_text(json.dumps(record))
        before = (path.read_bytes(), path.stat().st_mtime_ns)
        result = self.run_command("define", task=self.task("root", dependencies=["legacy"]))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_rejected("define", task=self.task("child", "legacy"),
                             message="parent is done: legacy")
        result = self.run_command("ready")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "root\n")
        self.assertEqual((path.read_bytes(), path.stat().st_mtime_ns), before)

    def test_execute_and_prove_preserve_parent(self):
        self.store("parent", state="running")
        git(self.root, "branch", "honeycomb/parent")
        path = self.store("child", "parent")
        self.assertEqual(self.run_command("execute", "child").returncode, 0)
        self.assertEqual(self.run_command("prove", "child").returncode, 1)
        result = self.run_command("prove", "child", "--item", "1", "--result", "true")
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(path.read_text())
        self.assertEqual(record["parent"], "parent")
        self.assertEqual(record["state"], "running")
        self.assertIs(record["proof"][0]["result"], True)

    def test_child_execute_requires_running_parent_and_completed_dependencies(self):
        git(self.root, "branch", "honeycomb/parent")
        for parent_state in ("open", "running", "done"):
            for dependency_state in ("open", "running", "done"):
                with self.subTest(parent=parent_state, dependency=dependency_state):
                    self.store("parent", state=parent_state)
                    self.store("sibling", "parent", state=dependency_state)
                    path = self.store("child", "parent", ["sibling"])
                    before = self.snapshot()
                    ready = self.run_command("ready")
                    self.assertEqual(ready.returncode, 0, ready.stderr)
                    self.assertEqual(self.snapshot(), before)
                    allowed = parent_state == "running" and dependency_state == "done"
                    self.assertEqual("child" in ready.stdout.splitlines(), allowed)
                    if allowed:
                        record = json.loads(path.read_text())
                        result = self.run_command("execute", "child")
                        self.assertEqual(result.returncode, 0, result.stderr)
                        self.assertEqual(json.loads(path.read_text()), {**record, "state": "running"})
                        # Git preparation changes Git files, never other task records.
                        before = {k: v for k, v in before.items() if k.startswith(".honeycomb/tasks/")}
                        after = {k: v for k, v in self.snapshot().items()
                                 if k.startswith(".honeycomb/tasks/")}
                        key = str(path.relative_to(self.root))
                        del before[key], after[key]
                        self.assertEqual(after, before)
                    else:
                        self.assert_rejected("execute", "child", message="not ready")

    def test_unfinished_children_block_both_prove_forms_at_every_depth(self):
        self.store("root", state="running")
        self.store("parent", "root", state="running")
        for task_id in ("root", "parent"):
            self.store("parent", "root", state="done" if task_id == "root" else "running")
            for state in ("open", "running"):
                with self.subTest(task=task_id, child_state=state):
                    self.store("finished", task_id, state="done")
                    self.store("unfinished", task_id, state=state)
                    path = self.tasks / f"{task_id}.json"
                    record = json.loads(path.read_text())
                    record["proof"][0]["result"] = True
                    path.write_text(json.dumps(record))
                    self.assert_rejected("prove", task_id, message="unfinished children")
                    for value in ("true", "false", "null"):
                        self.assert_rejected("prove", task_id, "--item", "1", "--result", value,
                                             message="unfinished children")

    def test_completed_children_allow_parent_proof_but_do_not_supply_it(self):
        self.store("root", state="running")
        for task_id, parent in (("root", None), ("parent", "root")):
            with self.subTest(task=task_id):
                path = self.store(task_id, parent, state="running")
                self.store("A", task_id, state="done")
                self.store("B", task_id, ["A"], state="done")
                self.store("unrelated", state="running")
                self.store("unrelated-child", "unrelated")
                workspace = self.home / "worktrees" / task_id
                target = "main" if parent is None else f"honeycomb/{parent}"
                git(self.root, "worktree", "add", "-b", f"honeycomb/{task_id}",
                    str(workspace), target)
                prepared = self.run_command("prove", task_id)
                self.assertEqual(prepared.returncode, 1, prepared.stderr)
                before = self.snapshot()
                result = self.run_command("prove", task_id)
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertEqual(self.snapshot(), before)
                result = self.run_command("prove", task_id, "--item", "1", "--result", "true")
                self.assertEqual(result.returncode, 0, result.stderr)
                record = json.loads(path.read_text())
                self.assertEqual(record["state"], "running")
                self.assertIs(record["proof"][0]["result"], True)
                after = self.snapshot()
                key = str(path.relative_to(self.root))
                del before[key], after[key]
                self.assertEqual(after, before)

    def test_parent_gate_resolves_id_not_filename(self):
        self.store("parent", state="running", filename="z.json")
        git(self.root, "branch", "honeycomb/parent")
        self.store("child", "parent", filename="a.json")
        self.assert_rejected("prove", "parent", message="unfinished children")
        result = self.run_command("execute", "child")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.run_command("prove", "child").returncode, 1)
        result = self.run_command("prove", "child", "--item", "1", "--result", "true")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_deep_hierarchy_without_recursion_limit(self):
        # Lexical order visits the deepest child first, exercising a long walk.
        for number in range(1100):
            self.store(f"T{number:04}", f"T{number + 1:04}" if number < 1099 else None,
                       state="open" if number == 0 else "running")
        result = self.run_command("ready")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "T0000\n")
        self.store("T1099", "T0000", state="running")
        self.assert_rejected("ready", message="parent cycle")


if __name__ == "__main__":
    unittest.main()
