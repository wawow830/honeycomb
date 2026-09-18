import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from git_support import git, init_repository


COMMAND = Path(__file__).resolve().parents[1] / ".agents/skills/honeycomb/scripts/honeycomb.py"
SPEC = importlib.util.spec_from_file_location("honeycomb", COMMAND)
honeycomb = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(honeycomb)


class AmendCommandTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="honeycomb amend ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.tasks = self.root / ".honeycomb" / "tasks"
        init_repository(self.root)
        self.define("target")

    def run_command(self, *args, data=None, raw=None, cwd=None):
        return subprocess.run(
            [sys.executable, str(COMMAND), *args], cwd=cwd or self.root,
            input=json.dumps(data) if raw is None and data is not None else raw,
            capture_output=True, text=True, timeout=10,
        )

    def succeed(self, *args, **kwargs):
        result = self.run_command(*args, **kwargs)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        return result

    def define(self, task_id, parent=None, dependencies=()):
        self.succeed("define", data={
            "id": task_id, "parent": parent, "depends_on": list(dependencies),
            "outcome": "Deliver the agreed outcome", "scope": "Feature only",
            "proof": [
                {"condition": "Works", "verification": "Run the tests"},
                {"condition": "Design accepted", "verification": "Ask the requester"},
            ],
        })

    def load(self, task_id="target"):
        return honeycomb.load_tasks(self.tasks)[task_id]

    def store(self, record):
        (self.tasks / f"{record['id']}.json").write_text(json.dumps(record))

    def workspace(self, task_id="target"):
        return self.root / ".honeycomb" / "worktrees" / task_id

    def snapshot(self):
        # Integration may create its persistent advisory lock, but nothing else.
        return {
            str(path.relative_to(self.root)): (path.read_bytes(), path.stat().st_mtime_ns)
            for path in self.root.rglob("*")
            if path.is_file() and "honeycomb-locks" not in path.parts
        }

    def reject(self, *args, message=None, **kwargs):
        before = self.snapshot()
        result = self.run_command(*args, **kwargs)
        self.assertEqual(result.returncode, 2, result)
        self.assertEqual(result.stdout, "")
        self.assertIn("error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        if message:
            self.assertIn(message, result.stderr)
        self.assertEqual(self.snapshot(), before)

    def amend(self, task_id="target", reason="Revise the plan", **changes):
        result = self.succeed("amend", task_id, data={"reason": reason, **changes})
        self.assertEqual(result.stdout, "")

    def prove(self, task_id="target"):
        result = self.run_command("prove", task_id)
        self.assertEqual(result.returncode, 1, result.stderr)
        for number in range(1, len(self.load(task_id)["proof"]) + 1):
            result = self.run_command("prove", task_id, "--item", str(number), "--result", "true")
            self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertEqual(result.returncode, 0, result.stderr)

    def commit(self, task_id, filename):
        workspace = self.workspace(task_id)
        (workspace / filename).write_text("feature\n")
        git(workspace, "add", filename)
        git(workspace, "commit", "-m", filename)

    def assert_only_task_changed(self, before, filename="target.json"):
        after = self.snapshot()
        key = f".honeycomb/tasks/{filename}"
        del before[key], after[key]
        self.assertEqual(after, before)

    def test_open_task_all_editable_fields_preserve_identity_and_unrelated_records(self):
        self.define("prerequisite")
        self.define("dependent", dependencies=["target"])
        original = self.load()
        original["metadata"] = {"keep": [True, None, "notes — retained"]}
        self.store(original)
        before = self.snapshot()
        proof = [{"condition": "New behavior", "verification": "Exercise the new behavior"}]
        self.amend(outcome="New outcome", scope="New boundary", proof=proof,
                   depends_on=["prerequisite"], reason="Requester approved the revised agreement")
        self.assertEqual(self.load(), {
            **original, "outcome": "New outcome", "scope": "New boundary",
            "depends_on": ["prerequisite"],
            "proof": [{**proof[0], "result": None}], "proof_snapshot": None,
            "amendments": [{"reason": "Requester approved the revised agreement", "previous": original}],
        })
        self.assert_only_task_changed(before)
        self.assertFalse(self.workspace().exists())
        self.assertEqual(self.succeed("ready").stdout, "prerequisite\n")
        self.reject("execute", "target", message="not ready")

    def test_replacement_dependency_recovers_same_task_and_keeps_downstream_links(self):
        for parent in (None, "parent"):
            with self.subTest(parent=parent):
                if parent:
                    self.define(parent)
                    self.succeed("execute", parent)
                suffix = "child" if parent else "root"
                old, replacement, dependent, later = [f"{name}-{suffix}" for name in ("A", "A2", "B", "C")]
                self.define(old, parent)
                self.define(dependent, parent, [old])
                self.define(later, parent, [dependent])
                self.succeed("close", old)
                self.define(replacement, parent)
                self.succeed("execute", replacement)
                self.commit(replacement, replacement)
                self.prove(replacement)
                self.succeed("integrate", replacement)
                self.reject("execute", dependent, message="not ready")
                later_before = self.load(later)
                self.amend(dependent, depends_on=[replacement], reason="Use replacement prerequisite")
                self.assertIn(dependent, self.succeed("ready").stdout.splitlines())
                self.succeed("execute", dependent)
                self.assertEqual((self.workspace(dependent) / replacement).read_text(), "feature\n")
                self.commit(dependent, dependent)
                self.prove(dependent)
                self.succeed("integrate", dependent)
                self.assertEqual(self.load(old)["state"], "closed")
                self.assertEqual(self.load(later), later_before)
                self.assertIn(later, self.succeed("ready").stdout.splitlines())

    def test_each_editable_field_clears_every_result_and_binding(self):
        self.define("done-prerequisite")
        self.succeed("execute", "done-prerequisite")
        self.prove("done-prerequisite")
        self.succeed("integrate", "done-prerequisite")
        self.succeed("execute", "target")
        self.prove()
        original = self.load()
        original["proof"].append({"condition": "Another", "verification": "Check another", "result": None})
        original["proof"][1]["result"] = False
        for changes in (
            {"outcome": "New outcome"}, {"scope": "New scope"},
            {"depends_on": ["done-prerequisite"]},
            {"proof": [{"condition": "New condition", "verification": "New check"}]},
        ):
            with self.subTest(changes=changes):
                self.store(original)
                before = self.snapshot()
                self.amend(**changes)
                record = self.load()
                self.assertTrue(all(item["result"] is None for item in record["proof"]))
                self.assertIsNone(record["proof_snapshot"])
                self.assertEqual(record["amendments"][0]["previous"], original)
                self.assertEqual(record["state"], "running")
                self.assert_only_task_changed(before)

    def test_history_is_ordered_complete_and_not_nested(self):
        self.succeed("execute", "target")
        self.prove()
        first = self.load()
        self.amend(outcome="Revised outcome", reason="First approved change")
        self.prove()
        second = self.load()
        self.amend(scope="Revised scope", reason="Second approved change")
        record = self.load()
        self.assertEqual(record["amendments"], [
            {"reason": "First approved change", "previous": first},
            {"reason": "Second approved change",
             "previous": {key: value for key, value in second.items() if key != "amendments"}},
        ])
        self.assertEqual(record["outcome"], "Revised outcome")
        self.assertEqual(record["scope"], "Revised scope")
        self.assertTrue(all(item["result"] is None for item in record["proof"]))
        self.succeed("close", "target")
        self.assertEqual(self.load()["amendments"], record["amendments"])

    def test_dirty_workspace_and_child_records_are_preserved_from_worktree(self):
        self.succeed("execute", "target")
        self.commit("target", "feature")
        self.prove()
        self.define("child", parent="target")
        workspace = self.workspace()
        (workspace / "feature").write_text("staged")
        git(workspace, "add", "feature")
        (workspace / "feature").write_text("unstaged")
        (workspace / "draft").write_text("untracked")
        before = self.snapshot()
        self.succeed("amend", "target", cwd=workspace,
                     data={"reason": "Approved revision", "scope": "Revised scope"})
        self.assert_only_task_changed(before)
        self.assertEqual(self.load()["state"], "running")
        self.assertFalse((workspace / ".honeycomb").exists())

    def test_amendment_requires_new_binding_and_checks_before_integration(self):
        self.succeed("execute", "target")
        self.commit("target", "feature")
        self.prove()
        old_snapshot = self.load()["proof_snapshot"]
        self.amend(outcome="Approved revised outcome")
        self.reject("integrate", "target", message="incomplete or failed")
        # A late result from the previous verification cannot establish a new binding.
        result = self.run_command("prove", "target", "--item", "1", "--result", "true")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("repeat verification", result.stderr)
        self.assertEqual(self.load()["proof_snapshot"], old_snapshot)
        self.assertTrue(all(item["result"] is None for item in self.load()["proof"]))
        self.reject("integrate", "target", message="incomplete or failed")
        self.prove()
        history = self.load()["amendments"]
        self.succeed("integrate", "target")
        self.assertEqual(self.load()["state"], "done")
        self.assertEqual(self.load()["amendments"], history)
        self.assertEqual(git(self.root, "rev-parse", "HEAD"), old_snapshot["task"])

    def test_running_task_waits_for_added_dependency_and_must_include_its_code(self):
        self.succeed("execute", "target")
        self.commit("target", "own-feature")
        self.prove()
        self.define("prerequisite")
        self.amend(depends_on=["prerequisite"])
        for start in (False, True):
            if start:
                self.succeed("execute", "prerequisite")
            self.reject("prove", "target", message="unfinished dependencies")
            self.reject("prove", "target", "--item", "1", "--result", "true", message="unfinished dependencies")
            self.reject("integrate", "target", message="unfinished dependencies")
        self.commit("prerequisite", "prerequisite-feature")
        self.prove("prerequisite")
        self.succeed("integrate", "prerequisite")
        self.reject("prove", "target", message="does not include current target")
        git(self.workspace(), "merge", "--no-edit", "refs/heads/main")
        self.prove()
        self.succeed("integrate", "target")
        for filename in ("own-feature", "prerequisite-feature"):
            self.assertEqual((self.root / filename).read_text(), "feature\n")

    def test_closed_dependency_does_not_satisfy_running_task(self):
        self.define("prerequisite")
        self.succeed("close", "prerequisite")
        self.succeed("execute", "target")
        self.amend(depends_on=["prerequisite"])
        self.reject("prove", "target", message="unfinished dependencies")
        self.reject("integrate", "target", message="unfinished dependencies")

    def test_invalid_inputs_and_managed_fields_are_rejected_without_writes(self):
        for field, values in {
            "reason": [None, 1, [], "", " \n"],
            "outcome": [None, 1, {}, "", " \n"],
            "scope": [None, False, [], "", "\t"],
            "depends_on": [None, "task", [None], [[]], [""], ["two words"], ["missing"], ["target"]],
            "proof": [None, {}, [], [None], [{}], [{"condition": "Works"}],
                      [{"condition": "", "verification": "Check"}],
                      [{"condition": "Works", "verification": " "}],
                      [{"condition": "Works", "verification": "Check", "result": None}]],
            "id": ["target"], "parent": [None], "state": ["open"],
            "proof_snapshot": [None], "amendments": [[]], "metadata": [{}], "typo": [True],
        }.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    self.reject("amend", "target", data={"reason": "Change", "scope": "New scope", field: value})
        for data in (None, [], 1, "text", {}, {"reason": "Why"}, {"scope": "New scope"}):
            with self.subTest(data=data):
                self.reject("amend", "target", raw=json.dumps(data))
        for raw in ("", "{", "{} {}", '{"reason":"a","reason":"b","scope":"new"}',
                    '{"reason":"a","scope":NaN}', '{"reason":"a","scope":Infinity}'):
            self.reject("amend", "target", raw=raw)

    def test_unchanged_fields_are_not_amendments_and_keep_passes(self):
        self.succeed("execute", "target")
        self.prove()
        original = self.load()
        for changes in (
            {"outcome": original["outcome"]}, {"scope": original["scope"]}, {"depends_on": []},
            {"proof": [{key: item[key] for key in ("condition", "verification")} for item in original["proof"]]},
        ):
            self.reject("amend", "target", data={"reason": "No change", **changes}, message="makes no changes")

    def test_duplicate_nonsibling_and_cyclic_dependencies_are_rejected(self):
        self.define("sibling")
        self.define("child", parent="sibling")
        self.define("dependent", dependencies=["target"])
        self.define("later", dependencies=["dependent"])
        for dependencies in (["sibling", "sibling"], ["child"], ["dependent"], ["later"]):
            self.reject("amend", "target", data={"reason": "Change", "depends_on": dependencies})

    def test_terminal_tasks_and_closed_ancestors_cannot_be_amended(self):
        original = self.load()
        for state in ("done", "closed"):
            self.store({**original, "state": state})
            self.reject("amend", "target", data={"reason": "Change", "scope": "New scope"},
                        message="not open or running")
        self.store(original)
        self.succeed("execute", "target")
        self.define("child", parent="target")
        self.succeed("execute", "child")
        # An interrupted closure may leave an active record beneath a closed ancestor.
        self.store({**self.load(), "state": "closed"})
        self.reject("amend", "child", data={"reason": "Change", "scope": "New scope"}, message="ancestor is closed")

    def test_missing_storage_unknown_ids_and_cli_arguments(self):
        data = {"reason": "Change", "scope": "New scope"}
        for args in (("amend",), ("amend", "target", "extra"), ("amend", "missing"), ("amend", "../outside")):
            self.reject(*args, data=data)
        (self.tasks / "target.json").unlink()
        self.tasks.rmdir()
        self.tasks.parent.rmdir()
        self.reject("amend", "target", data=data, message="task directory not found")
        self.assertFalse(self.tasks.parent.exists())

    def test_invalid_existing_storage_is_not_repaired_by_amendment(self):
        invalid = self.tasks / "invalid.json"
        for raw in (
            "{", "[]", '{"id":"bad","state":"open","depends_on":["missing"]}',
            '{"id":"bad","state":"open","depends_on":["bad"]}',
            '{"id":"bad","state":"open","parent":"missing","depends_on":[]}',
        ):
            invalid.write_text(raw)
            self.reject("amend", "target", data={"reason": "Change", "scope": "New scope"})
        invalid.unlink()
        original = self.load()
        for changes in ({"proof": []}, {"outcome": None}, {"amendments": {}}, {"amendments": None}):
            self.store({**original, **changes})
            self.reject("amend", "target", data={"reason": "Change", "scope": "New scope"})

    def test_record_resolution_and_amendment_do_not_require_git_operations(self):
        (self.tasks / "target.json").rename(self.tasks / "other.json")
        before = self.snapshot()
        with patch.object(honeycomb, "git", side_effect=AssertionError("must not use Git")):
            honeycomb.amend_task(self.tasks, "target", {"reason": "Change", "scope": "New scope"})
        self.assertEqual(self.load()["scope"], "New scope")
        self.assertFalse((self.tasks / "target.json").exists())
        self.assert_only_task_changed(before, filename="other.json")

    def test_atomic_write_failure_preserves_agreement_proof_and_history(self):
        self.succeed("execute", "target")
        self.amend(outcome="First revision")
        self.prove()
        before = self.snapshot()
        with patch.object(honeycomb.os, "replace", side_effect=OSError("disk full")):
            with self.assertRaisesRegex(OSError, "disk full"):
                honeycomb.amend_task(self.tasks, "target", {"reason": "Change", "scope": "New scope"})
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(list(self.tasks.glob(".task-*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
