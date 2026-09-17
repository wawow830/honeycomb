import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


from git_support import init_repository


COMMAND = Path(__file__).resolve().parents[1] / ".agents/skills/honeycomb/scripts/honeycomb.py"


class DefineCommandTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        init_repository(self.root)
        self.home = self.root / ".honeycomb"
        self.tasks = self.home / "tasks"
        self.task = {
            "id": "new-task_1",
            "outcome": "List ready tasks — deterministically.",
            "scope": "Read records only.",
            "parent": None,
            "depends_on": [],
            "proof": [
                {"condition": "Output is correct", "verification": "Run python3 -m unittest; require exit 0."},
                {"condition": "Records are unchanged", "verification": "Ask the requester to inspect and approve."},
            ],
        }

    def run_command(self, command="define", task=None, raw=None):
        return subprocess.run(
            [sys.executable, str(COMMAND), command],
            input=json.dumps(self.task if task is None else task) if raw is None else raw,
            cwd=self.root, capture_output=True, text=True, timeout=10,
        )

    def snapshot(self):
        return {
            str(path.relative_to(self.root)): (path.read_bytes(), path.stat().st_mtime_ns)
            for path in self.root.rglob("*") if path.is_file()
        }

    def assert_rejected(self, **kwargs):
        before = self.snapshot()
        result = self.run_command(**kwargs)
        self.assertEqual(result.returncode, 2, result)
        self.assertEqual(result.stdout, "")
        self.assertIn("error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(self.snapshot(), before)

    def store(self, filename, record):
        self.tasks.mkdir(parents=True, exist_ok=True)
        (self.tasks / filename).write_text(json.dumps(record), encoding="utf-8")

    def test_create_initializes_state_and_every_result(self):
        result = self.run_command()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")
        record = json.loads((self.tasks / "new-task_1.json").read_text())
        self.assertEqual(record, {
            **self.task,
            "state": "open",
            "proof": [{**item, "result": None} for item in self.task["proof"]],
        })
        ready = self.run_command("ready")
        self.assertEqual(ready.returncode, 0, ready.stderr)
        self.assertEqual(ready.stdout, "new-task_1\n")

    def test_dependencies_determine_readiness(self):
        self.store("A.json", {"id": "A", "state": "open", "depends_on": []})
        self.task["depends_on"] = ["A"]
        before = (self.tasks / "A.json").read_bytes()
        result = self.run_command()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.tasks / "A.json").read_bytes(), before)
        self.assertEqual(self.run_command("ready").stdout, "A\n")
        self.store("A.json", {"id": "A", "state": "done", "depends_on": []})
        ready = self.run_command("ready")
        self.assertEqual(ready.returncode, 0, ready.stderr)
        self.assertEqual(ready.stdout, "new-task_1\n")

    def test_duplicate_id_in_any_filename(self):
        for filename in ("new-task_1.json", "different.json"):
            with self.subTest(filename=filename):
                self.store(filename, {"id": self.task["id"], "state": "done", "depends_on": []})
                self.assert_rejected()
                (self.tasks / filename).unlink()

    def test_existing_filename_is_not_overwritten(self):
        self.store("new-task_1.json", {"id": "other", "state": "open", "depends_on": []})
        self.assert_rejected()

    def test_invalid_input_fields(self):
        cases = {
            "id": [None, [], 1, "", "two words", "../escape", "/absolute", "a/b", "a\\b", ".", "a" * 129],
            "outcome": [None, [], 1, "", " \n"],
            "scope": [None, {}, False, "", "\t"],
            "parent": [[], {}, False, 1, "", "two words", "missing", "new-task_1"],
            "depends_on": [None, "A", [None], [[]], [""], ["two words"], ["A", "A"], ["missing"], ["new-task_1"]],
            "proof": [None, {}, [], [None], [{}], [{"condition": "C"}],
                      [{"condition": "C", "verification": "Run tests", "result": None}],
                      [{"condition": "", "verification": "Run tests"}],
                      [{"condition": "C", "verification": " "}],
                      [{"condition": 1, "verification": "Run tests"}],
                      [{"condition": "C", "verification": []}]],
        }
        self.store("baseline.json", {"id": "baseline", "state": "done", "depends_on": []})
        for field, values in cases.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    self.assert_rejected(task={**self.task, field: value})
            with self.subTest(missing=field):
                task = copy.deepcopy(self.task)
                del task[field]
                self.assert_rejected(task=task)

    def test_invalid_verification_instructions(self):
        for verification in (
            None, "", " \n", 0, False, [], {},
            {"run": "true"}, {"review": "developer"},
        ):
            with self.subTest(verification=verification):
                self.assert_rejected(task={
                    **self.task,
                    "proof": [{"condition": "Works", "verification": verification}],
                })

    def test_plain_language_has_no_reserved_verifier_strings(self):
        for text in ("run", "review", "developer", "Ask the designer — then run tests."):
            with self.subTest(text=text):
                self.task["proof"] = [{"condition": "Works", "verification": text}]
                result = self.run_command()
                self.assertEqual(result.returncode, 0, result.stderr)
                path = self.tasks / "new-task_1.json"
                self.assertEqual(json.loads(path.read_text())["proof"][0]["verification"], text)
                path.unlink()

    def test_old_add_command_is_rejected(self):
        self.assert_rejected(command="add")

    def test_unknown_and_managed_fields_are_rejected(self):
        for field, value in (("state", "done"), ("result", True), ("subtasks", []), ("typo", "x")):
            with self.subTest(field=field):
                self.assert_rejected(task={**self.task, field: value})

    def test_invalid_json(self):
        for raw in ("", "{", "[]", "null", "1", "{} {}", '{"id":"A","id":"B"}',
                    '{"id":NaN}', '{"id":Infinity}', '{"id":-Infinity}'):
            with self.subTest(raw=raw):
                self.assert_rejected(raw=raw)
        self.assertFalse(self.home.exists())

    def test_invalid_existing_records_or_graph(self):
        for records in (
            {"A.json": "{"},
            {"A.json": '{"id":"A","state":"bad","depends_on":[]}'},
            {"A.json": '{"id":"A","state":"pending","depends_on":[]}'},
            {"A.json": '{"id":"A","id":"B","state":"done","depends_on":[]}'},
            {"A.json": '{"id":"A","state":"done","depends_on":[],"extra":NaN}'},
            {"A.json": '{"id":"A","state":"done","depends_on":["A","A"]}'},
            {"A.json": '{"id":"A","state":"done","depends_on":[]}',
             "duplicate.json": '{"id":"A","state":"done","depends_on":[]}'},
            {"A.json": '[]'},
            {"A.json": '{"id":"A","state":"done","depends_on":["missing"]}'},
            {"A.json": '{"id":"A","state":"done","depends_on":["B"]}',
             "B.json": '{"id":"B","state":"done","depends_on":["A"]}'},
        ):
            with self.subTest(records=records):
                self.tasks.mkdir(parents=True, exist_ok=True)
                for name, raw in records.items():
                    (self.tasks / name).write_text(raw)
                self.assert_rejected()
                for name in records:
                    (self.tasks / name).unlink()

    def test_task_directory_is_a_file(self):
        self.home.mkdir()
        self.tasks.write_text("leave me alone")
        self.assert_rejected()


if __name__ == "__main__":
    unittest.main()
