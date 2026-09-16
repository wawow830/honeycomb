import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


COMMAND = Path(__file__).resolve().parents[1] / "honeycomb.py"


class HierarchyTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.home = self.root / ".honeycomb"
        self.tasks = self.home / "tasks"
        self.tasks.mkdir(parents=True)

    def task(self, task_id, parent=None, dependencies=()):
        return {
            "id": task_id, "outcome": "Example", "scope": "Example",
            "parent": parent, "depends_on": list(dependencies),
            "proof": [{"condition": "Works", "verification": {"run": "true"}}],
        }

    def store(self, task_id, parent=None, dependencies=(), state="pending", filename=None):
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

    def test_add_root_child_and_grandchild(self):
        for task_id, parent in (("T", None), ("A", "T"), ("A1", "A")):
            with self.subTest(task_id=task_id):
                task = self.task(task_id, parent)
                before = self.snapshot()
                result = self.run_command("add", task=task)
                self.assertEqual(result.returncode, 0, result.stderr)
                path = self.tasks / f"{task_id}.json"
                record = json.loads(path.read_text())
                self.assertEqual(record, {
                    **task, "state": "pending",
                    "proof": [{**item, "result": None} for item in task["proof"]],
                })
                after = self.snapshot()
                del after[str(path.relative_to(self.root))]
                self.assertEqual(after, before)
        # Parent execution gates are outside this change's scope.
        self.assertEqual(self.run_command("ready").stdout, "A\nA1\nT\n")

    def test_sibling_dependencies_at_each_depth(self):
        self.store("T", state="running")
        self.store("A", "T", state="done")
        self.store("A1", "A", state="done")
        for task in (self.task("U", dependencies=["T"]),
                     self.task("B", "T", ["A"]),
                     self.task("A2", "A", ["A1"])):
            result = self.run_command("add", task=task)
            self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_command("ready")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "A2\nB\n")

    def test_cross_branch_and_ancestor_dependencies_rejected_on_add(self):
        self.store("T")
        self.store("A", "T")
        self.store("B", "T")
        self.store("A1", "A")
        for parent, dependencies in (("B", ["A1"]), ("A", ["A"]),
                                     (None, ["A"]), ("T", ["A1"])):
            with self.subTest(parent=parent, dependencies=dependencies):
                self.assert_rejected("add", task=self.task("new", parent, dependencies),
                                     message="not a sibling")

    def test_new_task_requires_parent_and_rejects_invalid_parent(self):
        task = self.task("new")
        del task["parent"]
        self.assert_rejected("add", task=task, message="expected exactly")
        for parent in ("missing", "new", "", "two words", 0, False, [], {}):
            with self.subTest(parent=parent):
                self.assert_rejected("add", task=self.task("new", parent))

    def test_invalid_parent_does_not_create_storage(self):
        self.tasks.rmdir()
        self.home.rmdir()
        self.assert_rejected("add", task=self.task("new", "missing"), message="missing parent")
        self.assertFalse(self.home.exists())

    def test_invalid_hierarchy_blocks_every_command_without_execution(self):
        path = self.store("target", state="running")
        task = json.loads(path.read_text())
        task["proof"] = [
            {"condition": "Must not execute", "verification": {"run": "touch executed"}, "result": None},
            {"condition": "Review", "verification": {"review": "developer"}, "result": None},
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
                for args in (("ready",), ("start", "available"), ("prove", "target"),
                             ("prove", "target", "--review", "2", "--accept"), ("add",)):
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
        for task in (self.task("root", dependencies=["legacy"]), self.task("child", "legacy")):
            result = self.run_command("add", task=task)
            self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_command("ready")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "child\nroot\n")
        self.assertEqual((path.read_bytes(), path.stat().st_mtime_ns), before)

    def test_start_and_prove_preserve_parent(self):
        self.store("parent", state="running")
        path = self.store("child", "parent")
        self.assertEqual(self.run_command("start", "child").returncode, 0)
        result = self.run_command("prove", "child")
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(path.read_text())
        self.assertEqual(record["parent"], "parent")
        self.assertEqual(record["state"], "running")
        self.assertEqual(record["proof"][0]["result"], {"exit_code": 0})

    def test_deep_hierarchy_without_recursion_limit(self):
        # Lexical order visits the deepest child first, exercising a long walk.
        for number in range(1100):
            self.store(f"T{number:04}", f"T{number + 1:04}" if number < 1099 else None,
                       state="pending" if number == 0 else "running")
        result = self.run_command("ready")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "T0000\n")
        self.store("T1099", "T0000", state="running")
        self.assert_rejected("ready", message="parent cycle")


if __name__ == "__main__":
    unittest.main()
