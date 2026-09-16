import copy
import importlib.util
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


COMMAND = Path(__file__).resolve().parents[1] / "honeycomb.py"
SPEC = importlib.util.spec_from_file_location("honeycomb", COMMAND)
honeycomb = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(honeycomb)


def python_command(code):
    return f"{shlex.quote(sys.executable)} -c {shlex.quote(code)}"


def check(code="pass", result=None):
    return {
        "condition": "Command establishes the condition.",
        "verification": {"run": python_command(code)},
        "result": result,
    }


def review(result=None):
    return {
        "condition": "Developer accepts the result — including its wording.",
        "verification": {"review": "developer"},
        "result": result,
    }


class ProveCommandTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.home = self.root / ".honeycomb"
        self.tasks = self.home / "tasks"
        self.tasks.mkdir(parents=True)
        self.record = {
            "id": "target", "state": "running", "depends_on": [],
            "outcome": "Verify the change.", "scope": "Proof only.",
            "proof": [check(), review()], "metadata": {"keep": [1, None]},
        }
        self.path = self.tasks / "different-filename.json"
        self.store()
        (self.tasks / "unrelated.json").write_text(json.dumps({
            "id": "unrelated", "state": "done", "depends_on": [],
        }))

    def store(self):
        self.path.write_text(json.dumps(self.record), encoding="utf-8")

    def load(self):
        return json.loads(self.path.read_text())

    def run_command(self, *args, data=None, home=None):
        env = {**os.environ, "HONEYCOMB_DIR": str(self.home) if home is None else home}
        return subprocess.run(
            [sys.executable, str(COMMAND), *args], cwd=self.root,
            env=env, input=data, capture_output=True, text=True, timeout=10,
        )

    def snapshot(self):
        return {
            str(path.relative_to(self.root)): (path.read_bytes(), path.stat().st_mtime_ns)
            for path in self.root.rglob("*") if path.is_file()
        }

    def assert_rejected(self, *args, home=None):
        before = self.snapshot()
        result = self.run_command(*args, home=home)
        self.assertEqual(result.returncode, 2, result)
        self.assertEqual(result.stdout, "")
        self.assertIn("error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_checks_record_actual_results_and_report_numbered_reviews(self):
        before = self.snapshot()
        result = self.run_command("prove", "target")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(result.stdout, f"1: exit_code: 0\n2: review: {self.record['proof'][1]['condition']}\n")
        self.assertEqual(result.stderr, "")
        expected = copy.deepcopy(self.record)
        expected["proof"][0]["result"] = {"exit_code": 0}
        self.assertEqual(self.load(), expected)
        after = self.snapshot()
        key = str(self.path.relative_to(self.root))
        del before[key], after[key]
        self.assertEqual(after, before)

    def test_all_commands_run_even_after_failure(self):
        self.record["proof"] = [check("raise SystemExit(7)"), check(), check("raise SystemExit(2)")]
        self.store()
        result = self.run_command("prove", "target")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual([p["result"] for p in self.load()["proof"]], [
            {"exit_code": 7}, {"exit_code": 0}, {"exit_code": 2},
        ])
        self.assertEqual(result.stdout, "1: exit_code: 7\n2: exit_code: 0\n3: exit_code: 2\n")

    def test_all_proven_returns_zero_without_marking_done(self):
        self.record["proof"] = [check(), review({"accepted": True})]
        self.store()
        result = self.run_command("prove", "target")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "1: exit_code: 0\n")
        self.assertEqual(self.load()["state"], "running")
        self.assertEqual(self.load()["proof"][1]["result"], {"accepted": True})

    def test_rerun_replaces_old_pass_and_old_failure(self):
        for code, old, actual in (("raise SystemExit(4)", 0, 4), ("pass", 4, 0)):
            with self.subTest(code=code):
                self.record["proof"] = [check(code, {"exit_code": old})]
                self.store()
                result = self.run_command("prove", "target")
                self.assertEqual(result.returncode, 0 if actual == 0 else 1)
                self.assertEqual(self.load()["proof"][0]["result"], {"exit_code": actual})

    def test_command_uses_callers_cwd_environment_and_closed_stdin(self):
        code = (
            "import os, pathlib, sys; "
            f"assert pathlib.Path.cwd() == pathlib.Path({str(self.root)!r}); "
            f"assert os.environ['HONEYCOMB_DIR'] == {str(self.home)!r}; "
            "assert sys.stdin.read() == ''; "
            "print('command stdout'); print('command stderr', file=sys.stderr)"
        )
        self.record["proof"] = [check(code)]
        self.store()
        result = self.run_command("prove", "target", data="not a review decision")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "1: exit_code: 0\n")
        self.assertIn("command stdout", result.stderr)
        self.assertIn("command stderr", result.stderr)

    def test_shell_commands_are_supported(self):
        self.record["proof"] = [check()]
        self.record["proof"][0]["verification"]["run"] = "false || true"
        self.store()
        self.assertEqual(self.run_command("prove", "target").returncode, 0)

    def test_missing_executable_records_failure(self):
        self.record["proof"] = [check()]
        self.record["proof"][0]["verification"]["run"] = "honeycomb_nonexistent_check_928374"
        self.store()
        result = self.run_command("prove", "target")
        self.assertEqual(result.returncode, 1)
        self.assertNotEqual(self.load()["proof"][0]["result"]["exit_code"], 0)

    def test_review_updates_only_selected_item_without_running_commands(self):
        self.record["proof"][0] = check("raise RuntimeError('must not run')")
        self.store()
        for decision, accepted in (("--accept", True), ("--reject", False)):
            with self.subTest(decision=decision):
                before = self.snapshot()
                expected = self.load()
                result = self.run_command("prove", "target", "--review", "2", decision)
                self.assertEqual(result.returncode, 1)  # Command remains unproven.
                self.assertEqual(result.stderr, "")
                expected["proof"][1]["result"] = {"accepted": accepted}
                self.assertEqual(self.load(), expected)
                self.assertNotIn("exit_code:", result.stdout)
                self.assertEqual("2: review:" in result.stdout, not accepted)
                after = self.snapshot()
                key = str(self.path.relative_to(self.root))
                del before[key], after[key]
                self.assertEqual(after, before)

    def test_accepting_final_review_completes_proof_not_task(self):
        self.record["proof"][0]["result"] = {"exit_code": 0}
        self.store()
        result = self.run_command("prove", "target", "--review", "2", "--accept")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(self.load()["state"], "running")

    def test_review_only_without_decision_leaves_record_untouched(self):
        for stored_result in (None, {"accepted": False}, {"accepted": True}):
            with self.subTest(result=stored_result):
                self.record["proof"] = [review(stored_result)]
                self.store()
                before = self.snapshot()
                result = self.run_command("prove", "target")
                self.assertEqual(result.returncode, 0 if stored_result == {"accepted": True} else 1)
                self.assertEqual(self.snapshot(), before)

    def test_reject_invalid_cli_before_execution(self):
        for args in (
            (), ("target", "extra"), ("target", "--accept"), ("target", "--reject"),
            ("target", "--review", "2"), ("target", "--review", "2", "--accept", "--reject"),
            ("target", "--review", "zero", "--accept"),
            *(("target", "--review", n, "--accept") for n in ("-1", "0", "1", "3")),
        ):
            with self.subTest(args=args):
                self.assert_rejected("prove", *args)

    def test_reject_unknown_or_nonrunning_task(self):
        self.assert_rejected("prove", "unknown")
        for state in ("pending", "done"):
            self.record["state"] = state
            self.store()
            self.assert_rejected("prove", "target")
            self.assert_rejected("prove", "target", "--review", "2", "--accept")

    def test_validate_entire_proof_before_commands_or_review_update(self):
        marker = self.root / "executed"
        first = check(f"from pathlib import Path; Path({str(marker)!r}).touch()")
        invalid_items = [
            None, {}, {**review(), "condition": " "},
            {**review(), "verification": "Run tests"},
            {**check(), "verification": {"run": "echo\x00bad"}},
            {**review(), "verification": {"run": "true", "review": "developer"}},
            {**review(), "verification": {"review": "agent"}},
            {**review(), "result": True}, {**review(), "result": {"accepted": 1}},
            {**check(), "result": {"exit_code": False}},
            {**check(), "result": {"exit_code": 0.0}},
            {**check(), "result": {"accepted": True}},
            {**check(), "result": {"exit_code": 0, "extra": True}},
        ]
        for item in invalid_items:
            with self.subTest(item=item):
                self.record["proof"] = [first, review(), item]
                self.store()
                self.assert_rejected("prove", "target")
                self.assert_rejected("prove", "target", "--review", "2", "--accept")
                self.assertFalse(marker.exists())
        for proof in (None, [], {}, [check() | {"extra": True}]):
            self.record["proof"] = proof
            self.store()
            self.assert_rejected("prove", "target")

    def test_invalid_stored_graph_prevents_proof(self):
        for raw in (
            "{", "[]",
            '{"id":"other","state":"pending","depends_on":["missing"]}',
            '{"id":"other","state":"done","depends_on":["other"]}',
            '{"id":"target","state":"pending","depends_on":[]}',
            '{"id":"other","id":"duplicate","state":"done","depends_on":[]}',
            '{"id":"other","state":"done","depends_on":[],"extra":NaN}',
        ):
            with self.subTest(raw=raw):
                (self.tasks / "invalid.json").write_text(raw)
                self.assert_rejected("prove", "target")

    def test_invalid_or_missing_storage(self):
        for home in ("", ".honeycomb", str(self.root / "missing")):
            self.assert_rejected("prove", "target", home=home)

    def test_ids_resolve_from_record_not_path(self):
        self.record["id"] = "../outside"
        self.record["proof"] = [check()]
        self.store()
        result = self.run_command("prove", "../outside")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.load()["proof"][0]["result"], {"exit_code": 0})
        self.assertFalse((self.home / "outside.json").exists())

    def test_interruption_does_not_leave_old_command_passes(self):
        self.record["proof"] = [check(result={"exit_code": 0}), check(result={"exit_code": 0})]
        self.store()
        with patch.object(honeycomb.subprocess, "run", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                honeycomb.prove_task(self.tasks, "target")
        self.assertEqual([item["result"] for item in self.load()["proof"]], [None, None])

    def test_failed_atomic_replace_preserves_record_and_cleans_temporary_file(self):
        before = self.snapshot()
        with patch.object(honeycomb.os, "replace", side_effect=OSError("simulated failure")):
            with self.assertRaises(OSError):
                honeycomb.prove_task(self.tasks, "target", review=2, accepted=True)
        self.assertEqual(self.snapshot(), before)

    def test_add_start_prove_integration(self):
        task = {
            "id": "new", "outcome": "Example", "scope": "Example",
            "parent": None, "depends_on": [],
            "proof": [{k: v for k, v in item.items() if k != "result"} for item in (check(), review())],
        }
        added = self.run_command("add", data=json.dumps(task))
        self.assertEqual(added.returncode, 0, added.stderr)
        self.assertEqual(self.run_command("start", "new").returncode, 0)
        self.assertEqual(self.run_command("prove", "new").returncode, 1)
        accepted = self.run_command("prove", "new", "--review", "2", "--accept")
        self.assertEqual(accepted.returncode, 0, accepted.stderr)
        record = json.loads((self.tasks / "new.json").read_text())
        self.assertEqual(record["state"], "running")
        self.assertEqual([item["result"] for item in record["proof"]], [
            {"exit_code": 0}, {"accepted": True},
        ])
        self.assertEqual(self.run_command("ready").stdout, "")


if __name__ == "__main__":
    unittest.main()
