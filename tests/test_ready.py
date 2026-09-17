import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


from git_support import init_repository


COMMAND = Path(__file__).resolve().parents[1] / ".agents/skills/honeycomb/scripts/honeycomb.py"


class ReadyCommandTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.tasks = self.root / ".honeycomb" / "tasks"
        self.tasks.mkdir(parents=True)
        init_repository(self.root)

    def task(self, task_id, state="open", dependencies=None, filename=None):
        record = {
            "id": task_id,
            "outcome": "Example outcome",
            "scope": "Example scope",
            "proof": [],
            "depends_on": [] if dependencies is None else dependencies,
            "subtasks": [],
            "state": state,
        }
        path = self.tasks / (filename or f"{task_id}.json")
        path.write_text(json.dumps(record), encoding="utf-8")
        return path

    def run_command(self):
        return subprocess.run(
            [sys.executable, str(COMMAND), "ready"],
            cwd=self.root,
            capture_output=True,
            text=True,
            timeout=10,
        )

    def assert_ready(self, *task_ids):
        result = self.run_command()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "".join(f"{task_id}\n" for task_id in task_ids))
        self.assertEqual(result.stderr, "")

    def assert_invalid(self, message):
        result = self.run_command()
        self.assertEqual(result.returncode, 2, result)
        self.assertEqual(result.stdout, "")
        self.assertIn(message, result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_agreed_example(self):
        self.task("A", "done")
        self.task("B", dependencies=["A"])
        self.task("C", dependencies=["B"])
        self.task("D", "running")
        self.assert_ready("B")

    def test_independent_tasks_sorted_by_id_not_filename(self):
        self.task("Z", filename="1.json")
        self.task("A", filename="2.json")
        self.assert_ready("A", "Z")

    def test_every_dependency_must_be_done(self):
        self.task("A", "done")
        self.task("B", "running")
        self.task("C", dependencies=["A", "B"])
        self.assert_ready()
        self.task("B", "done")
        self.assert_ready("C")

    def test_open_dependency_blocks_task(self):
        self.task("A")
        self.task("B", dependencies=["A"])
        self.assert_ready("A")

    def test_running_and_done_are_not_ready(self):
        self.task("A", "running")
        self.task("B", "done")
        self.assert_ready()

    def test_empty_directory(self):
        self.assert_ready()

    def test_missing_dependency_rejects_all_output(self):
        self.task("available")
        self.task("B", dependencies=["missing"])
        self.assert_invalid("missing dependency missing")

    def test_cycle_rejects_all_output(self):
        self.task("available")
        self.task("A", dependencies=["B"])
        self.task("B", dependencies=["C"])
        self.task("C", dependencies=["A"])
        self.assert_invalid("dependency cycle")

    def test_self_dependency(self):
        self.task("A", dependencies=["A"])
        self.assert_invalid("dependency cycle")

    def test_done_state_does_not_hide_broken_graph(self):
        self.task("A", "done", ["B"])
        self.task("B", "done", ["A"])
        self.assert_invalid("dependency cycle")

    def test_duplicate_ids(self):
        self.task("A")
        self.task("A", filename="duplicate.json")
        self.assert_invalid("duplicate task id")

    def test_duplicate_dependencies(self):
        self.task("A", "done")
        self.task("B", dependencies=["A", "A"])
        self.assert_invalid("duplicate dependency")

    def test_invalid_scheduling_fields(self):
        path = self.task("A")
        valid = json.loads(path.read_text())
        for field, values, message in [
            ("id", [None, 7, "", "two lines\n", []], "id must be"),
            ("state", [None, "pending", "ready", [], 7], "state must be"),
            ("depends_on", [None, "A", [7], [[]], [""]], "depends_on must be"),
        ]:
            for value in values:
                with self.subTest(field=field, value=value):
                    path.write_text(json.dumps({**valid, field: value}))
                    self.assert_invalid(message)
            with self.subTest(field=field, missing=True):
                record = valid.copy()
                del record[field]
                path.write_text(json.dumps(record))
                self.assert_invalid(message)

    def test_malformed_json(self):
        (self.tasks / "bad.json").write_text("{")
        self.assert_invalid("bad.json")

    def test_non_object_record(self):
        (self.tasks / "bad.json").write_text("[]")
        self.assert_invalid("expected a task object")

    def test_invalid_encoding(self):
        (self.tasks / "bad.json").write_bytes(b"\xff")
        self.assert_invalid("bad.json")

    def test_missing_task_directory_is_empty_without_writes(self):
        self.tasks.rmdir()
        self.tasks.parent.rmdir()
        self.assert_ready()
        self.assertFalse(self.tasks.parent.exists())

    def test_task_directory_is_a_file(self):
        self.tasks.rmdir()
        self.tasks.write_text("not a directory")
        self.assert_invalid("task directory not found")

    def test_home_is_a_file(self):
        self.tasks.rmdir()
        self.tasks.parent.rmdir()
        self.tasks.parent.write_text("not a directory")
        self.assert_invalid("Not a directory")

    def test_dangling_task_directory_is_not_an_empty_project(self):
        self.tasks.rmdir()
        self.tasks.symlink_to(self.root / "missing")
        self.assert_invalid("task directory not found")

    def test_dangling_honeycomb_directory_is_not_an_empty_project(self):
        self.tasks.rmdir()
        self.tasks.parent.rmdir()
        self.tasks.parent.symlink_to(self.root / "missing", target_is_directory=True)
        self.assert_invalid("task directory not found")

    def test_read_only_and_repeatable(self):
        self.task("A", "done")
        self.task("B", dependencies=["A"])
        (self.tasks / "notes.txt").write_text("not a task")

        def snapshot():
            return {
                str(path.relative_to(self.root)): (path.read_bytes(), path.stat().st_mtime_ns)
                for path in self.root.rglob("*") if path.is_file()
            }

        before = snapshot()
        self.assert_ready("B")
        self.assert_ready("B")
        self.assertEqual(snapshot(), before)

    def test_long_dependency_chain(self):
        for number in range(1100):
            self.task(
                f"T{number}",
                "done" if number < 1099 else "open",
                [f"T{number - 1}"] if number else [],
            )
        self.assert_ready("T1099")


if __name__ == "__main__":
    unittest.main()
