import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


COMMAND = Path(__file__).resolve().parents[1] / "honeycomb.py"


class StartCommandTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.home = self.root / ".honeycomb"
        self.tasks = self.home / "tasks"
        self.tasks.mkdir(parents=True)

    def store(self, task_id, state="pending", dependencies=None, filename=None):
        record = {
            "id": task_id,
            "outcome": "Preserve fields — including Unicode.",
            "scope": "Only change state.",
            "depends_on": [] if dependencies is None else dependencies,
            "proof": [{"condition": "Works", "verification": "Run tests", "result": None}],
            "state": state,
            "metadata": {"nested": [True, None, 42]},
        }
        path = self.tasks / (filename or f"{task_id}.json")
        path.write_text(json.dumps(record), encoding="utf-8")
        return path

    def run_command(self, *args, home=None, data=None):
        environment = os.environ.copy()
        environment["HONEYCOMB_DIR"] = str(self.home) if home is None else home
        return subprocess.run(
            [sys.executable, str(COMMAND), *args],
            cwd=self.root, env=environment, input=data,
            capture_output=True, text=True, timeout=10,
        )

    def snapshot(self):
        return {
            str(path.relative_to(self.root)): (path.read_bytes(), path.stat().st_mtime_ns)
            for path in self.root.rglob("*") if path.is_file()
        }

    def assert_rejected(self, *args, home=None, message=None):
        before = self.snapshot()
        result = self.run_command(*args, home=home)
        self.assertEqual(result.returncode, 2, result)
        self.assertEqual(result.stdout, "")
        self.assertIn("error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        if message:
            self.assertIn(message, result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_ready_task_changes_only_state(self):
        path = self.store("target")
        self.store("unrelated")
        self.store("dependent", dependencies=["target"])
        before = self.snapshot()
        record = json.loads(path.read_text())
        result = self.run_command("start", "target")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")
        self.assertEqual(json.loads(path.read_text()), {**record, "state": "running"})
        after = self.snapshot()
        key = str(path.relative_to(self.root))
        del before[key], after[key]
        self.assertEqual(after, before)
        ready = self.run_command("ready")
        self.assertEqual(ready.returncode, 0, ready.stderr)
        self.assertEqual(ready.stdout, "unrelated\n")

    def test_all_dependencies_done(self):
        self.store("A", "done")
        self.store("B", "done")
        path = self.store("target", dependencies=["A", "B"])
        result = self.run_command("start", "target")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(path.read_text())["state"], "running")

    def test_each_unfinished_dependency_blocks_start(self):
        self.store("A", "done")
        for state in ("pending", "running"):
            with self.subTest(state=state):
                self.store("B", state)
                self.store("target", dependencies=["A", "B"])
                self.assert_rejected("start", "target", message="not ready")

    def test_running_and_done_tasks_are_rejected(self):
        for state in ("running", "done"):
            with self.subTest(state=state):
                self.store("target", state)
                self.assert_rejected("start", "target", message="not ready")

    def test_repeated_start_is_rejected(self):
        self.store("target")
        result = self.run_command("start", "target")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_rejected("start", "target", message="not ready")

    def test_unknown_id_is_rejected(self):
        self.store("target")
        for task_id in ("missing", "", "../outside", "/absolute"):
            with self.subTest(task_id=task_id):
                self.assert_rejected("start", task_id, message="unknown task")

    def test_uses_record_id_not_filename(self):
        path = self.store("target", filename="different.json")
        result = self.run_command("start", "target")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(path.read_text())["state"], "running")
        self.assertEqual(list(self.tasks.iterdir()), [path])

    def test_stored_id_is_not_used_as_a_path(self):
        path = self.store("../outside", filename="safe.json")
        result = self.run_command("start", "../outside")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(path.read_text())["state"], "running")
        self.assertFalse((self.home / "outside.json").exists())

    def test_invalid_stored_records_or_graph_prevent_start(self):
        self.store("target")
        cases = (
            "{", "[]",
            '{"id":"bad","state":"invalid","depends_on":[]}',
            '{"id":"target","state":"pending","depends_on":[]}',
            '{"id":"bad","state":"pending","depends_on":["missing"]}',
            '{"id":"bad","state":"done","depends_on":["bad"]}',
            '{"id":"bad","state":"pending","depends_on":["target","target"]}',
            '{"id":"bad","id":"other","state":"pending","depends_on":[]}',
            '{"id":"bad","state":"pending","depends_on":[],"extra":NaN}',
        )
        for raw in cases:
            with self.subTest(raw=raw):
                (self.tasks / "bad.json").write_text(raw)
                self.assert_rejected("start", "target")
        (self.tasks / "bad.json").write_bytes(b"\xff")
        self.assert_rejected("start", "target")

    def test_invalid_home(self):
        self.store("target")
        for home in ("", ".honeycomb"):
            with self.subTest(home=home):
                self.assert_rejected("start", "target", home=home)

    def test_missing_or_non_directory_storage(self):
        self.tasks.rmdir()
        self.assert_rejected("start", "target", message="task directory not found")
        self.assertFalse(self.tasks.exists())
        self.tasks.write_text("not a directory")
        self.assert_rejected("start", "target", message="task directory not found")

    def test_exactly_one_id_required_only_for_start(self):
        self.store("target")
        for args in (("start",), ("start", "target", "extra"), ("ready", "target"), ("add", "target")):
            with self.subTest(args=args):
                self.assert_rejected(*args)

    def test_add_start_ready_integration(self):
        task = {
            "id": "new-task", "outcome": "Example", "scope": "Example",
            "parent": None, "depends_on": [],
            "proof": [{"condition": "Works", "verification": {"run": "true"}}],
        }
        added = self.run_command("add", data=json.dumps(task))
        self.assertEqual(added.returncode, 0, added.stderr)
        self.assertEqual(self.run_command("ready").stdout, "new-task\n")
        started = self.run_command("start", "new-task")
        self.assertEqual(started.returncode, 0, started.stderr)
        ready = self.run_command("ready")
        self.assertEqual(ready.returncode, 0, ready.stderr)
        self.assertEqual(ready.stdout, "")
        record = json.loads((self.tasks / "new-task.json").read_text())
        self.assertEqual(record, {
            **task, "state": "running",
            "proof": [{**item, "result": None} for item in task["proof"]],
        })


if __name__ == "__main__":
    unittest.main()
