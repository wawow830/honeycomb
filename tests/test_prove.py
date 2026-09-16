import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from git_support import git, init_repository


COMMAND = Path(__file__).resolve().parents[1] / "honeycomb.py"
SPEC = importlib.util.spec_from_file_location("honeycomb", COMMAND)
honeycomb = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(honeycomb)


def check(result=None):
    return {
        "condition": "Invalid input leaves records unchanged.",
        "verification": "Run rejection tests; require exit 0.",
        "result": result,
    }


def review(result=None):
    return {
        "condition": "Interaction feels right — including its wording.",
        "verification": "Ask the requester to try the interaction and approve it.",
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
            "id": "target", "state": "open", "parent": None, "depends_on": [],
            "outcome": "Verify the change.", "scope": "Proof only.",
            "proof": [check(), review()], "metadata": {"keep": [1, None]},
        }
        self.path = self.tasks / "different-filename.json"
        self.store()
        init_repository(self.root)
        executed = self.run_command("execute", "target")
        self.assertEqual(executed.returncode, 0, executed.stderr)
        self.workspace = self.home / "worktrees" / "target"
        prepared = self.run_command("prove", "target")
        self.assertEqual(prepared.returncode, 1, prepared.stderr)
        self.record = self.load()
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

    def test_show_all_numbered_conditions_instructions_and_results_without_writes(self):
        for value in (None, False, True):
            with self.subTest(value=value):
                self.record["proof"] = [check(value), review(value)]
                self.store()
                before = self.snapshot()
                result = self.run_command("prove", "target")
                self.assertEqual(result.returncode, 0 if value is True else 1, result.stderr)
                expected = "".join(
                    f"{number}: {item['condition']}\n"
                    f"   verification: {item['verification']}\n"
                    f"   result: {json.dumps(item['result'])}\n"
                    for number, item in enumerate(self.record["proof"], 1)
                )
                self.assertEqual(result.stdout, expected)
                self.assertEqual(result.stderr, "")
                self.assertEqual(self.snapshot(), before)

    def test_update_only_selected_result_preserving_all_other_fields_and_records(self):
        for number in (1, 2):
            for raw, value in (("true", True), ("false", False), ("null", None)):
                with self.subTest(number=number, value=value):
                    before = self.snapshot()
                    expected = self.load()
                    result = self.run_command("prove", "target", "--item", str(number), "--result", raw)
                    expected["proof"][number - 1]["result"] = value
                    self.assertEqual(result.returncode, 1, result.stderr)
                    self.assertEqual(self.load(), expected)
                    self.assertIn(f"   result: {raw}\n", result.stdout)
                    after = self.snapshot()
                    key = str(self.path.relative_to(self.root))
                    del before[key], after[key]
                    self.assertEqual(after, before)

    def test_all_proven_returns_zero_without_marking_done(self):
        self.record["proof"] = [check(True), review()]
        self.store()
        result = self.run_command("prove", "target", "--item", "2", "--result", "true")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.load()["state"], "running")
        self.assertEqual(self.run_command("prove", "target").returncode, 0)

    def test_failed_or_cleared_result_makes_proof_incomplete(self):
        for raw, value in (("false", False), ("null", None)):
            with self.subTest(raw=raw):
                self.record["proof"] = [check(True), review(True)]
                self.store()
                result = self.run_command("prove", "target", "--item", "1", "--result", raw)
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIs(self.load()["proof"][0]["result"], value)
                self.assertIs(self.load()["proof"][1]["result"], True)

    def test_instructions_are_never_executed_or_used_as_reserved_strings(self):
        for instructions in ("touch executed", "run", "review", "developer"):
            with self.subTest(instructions=instructions):
                self.record["proof"] = [{**check(), "verification": instructions}]
                self.store()
                before = self.snapshot()
                result = self.run_command("prove", "target", data="yes\n")
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertEqual(self.snapshot(), before)
                result = self.run_command("prove", "target", "--item", "1", "--result", "true")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertFalse((self.root / "executed").exists())

    def test_reject_invalid_cli_without_writes(self):
        for args in (
            (), ("target", "extra"), ("target", "--item", "1"),
            ("target", "--result", "true"), ("target", "--result", "null"),
            ("target", "--review", "2", "--accept"), ("target", "--reject"),
            *(("target", "--item", n, "--result", "true") for n in ("-1", "0", "3", "one", "1.0")),
            *(("target", "--item", "1", "--result", r) for r in ("True", "1", "0", "yes", "", "{}")),
        ):
            with self.subTest(args=args):
                self.assert_rejected("prove", *args)

    def test_reject_unknown_or_nonrunning_task(self):
        self.assert_rejected("prove", "unknown")
        for state in ("open", "done"):
            self.record["state"] = state
            self.store()
            self.assert_rejected("prove", "target")
            self.assert_rejected("prove", "target", "--item", "2", "--result", "true")

    def test_validate_entire_proof_before_display_or_update(self):
        invalid_items = [
            None, {}, {**review(), "condition": " "}, {**review(), "condition": 1},
            *({**check(), "verification": value} for value in
              (None, "", " \n", False, 1, [], {}, {"run": "true"}, {"review": "developer"})),
            *({**check(), "result": value} for value in
              (0, 1, 0.0, "true", [], {}, {"exit_code": 0}, {"accepted": True})),
            {**check(), "extra": True},
            {key: value for key, value in check().items() if key != "result"},
        ]
        for item in invalid_items:
            with self.subTest(item=item):
                self.record["proof"] = [check(), review(), item]
                self.store()
                self.assert_rejected("prove", "target")
                self.assert_rejected("prove", "target", "--item", "2", "--result", "true")
        for proof in (None, [], {}):
            self.record["proof"] = proof
            self.store()
            self.assert_rejected("prove", "target")

    def test_invalid_stored_graph_prevents_proof(self):
        for raw in (
            "{", "[]",
            '{"id":"other","state":"open","depends_on":["missing"]}',
            '{"id":"other","state":"done","depends_on":["other"]}',
            '{"id":"target","state":"open","depends_on":[]}',
            '{"id":"other","id":"duplicate","state":"done","depends_on":[]}',
            '{"id":"other","state":"done","depends_on":[],"extra":NaN}',
            '{"id":"other","state":"pending","depends_on":[]}',
        ):
            with self.subTest(raw=raw):
                (self.tasks / "invalid.json").write_text(raw)
                self.assert_rejected("prove", "target")
                self.assert_rejected("prove", "target", "--item", "1", "--result", "true")

    def test_invalid_or_missing_storage(self):
        for home in ("", ".honeycomb", str(self.root / "missing")):
            self.assert_rejected("prove", "target", home=home)

    def test_ids_resolve_from_record_not_filename(self):
        result = self.run_command("prove", "target", "--item", "1", "--result", "true")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIs(self.load()["proof"][0]["result"], True)
        self.assertFalse((self.tasks / "target.json").exists())

    def test_unsafe_stored_id_cannot_be_used_as_workspace_path(self):
        self.record["id"] = "../outside"
        self.store()
        self.assert_rejected("prove", "../outside")
        self.assert_rejected("prove", "../outside", "--item", "1", "--result", "true")
        self.assertFalse((self.home / "outside.json").exists())

    def test_failed_atomic_replace_preserves_record_and_cleans_temporary_file(self):
        before = self.snapshot()
        with patch.object(honeycomb.os, "replace", side_effect=OSError("simulated failure")):
            with self.assertRaises(OSError):
                honeycomb.prove_task(self.tasks, "target", item=2, result=True)
        self.assertEqual(self.snapshot(), before)

    def test_direct_api_rejects_invalid_item_and_result(self):
        for kwargs in (
            {"item": True, "result": True}, {"item": 1.0, "result": True},
            {"item": 0, "result": None}, {"item": 1, "result": 1},
            {"item": 1, "result": "true"}, {"result": True},
        ):
            with self.subTest(kwargs=kwargs):
                before = self.snapshot()
                with self.assertRaises(ValueError):
                    honeycomb.prove_task(self.tasks, "target", **kwargs)
                self.assertEqual(self.snapshot(), before)

    def mark_all_proven(self):
        for item in (1, 2):
            result = self.run_command("prove", "target", "--item", str(item), "--result", "true")
            self.assertEqual(result.returncode, 0 if item == 2 else 1, result.stderr)

    def assert_unproven(self):
        record = self.load()
        self.assertEqual([entry["result"] for entry in record["proof"]], [None, None])
        self.assertEqual(record["state"], "running")
        return record

    def commit_change(self, workspace, name="change"):
        (workspace / name).write_text("changed\n")
        git(workspace, "add", name)
        git(workspace, "commit", "-m", "Change")

    def test_initial_proof_binds_both_commits_without_moving_git(self):
        self.record.pop("proof_snapshot")
        self.record["proof"] = [check(True), review(True)]
        self.store()
        before = self.snapshot()
        result = self.run_command("prove", "target")
        self.assertEqual(result.returncode, 1, result.stderr)
        record = self.assert_unproven()
        self.assertEqual(record["proof_snapshot"], {
            "task": git(self.workspace, "rev-parse", "HEAD"),
            "target": git(self.root, "rev-parse", "refs/heads/main"),
        })
        after = self.snapshot()
        key = str(self.path.relative_to(self.root))
        del before[key], after[key]
        self.assertEqual(before, after)

    def test_unbound_result_cannot_be_recorded_before_verification_snapshot(self):
        del self.record["proof_snapshot"]
        self.store()
        result = self.run_command("prove", "target", "--item", "1", "--result", "true")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("repeat verification", result.stderr)
        self.assert_unproven()
        result = self.run_command("prove", "target", "--item", "1", "--result", "true")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIs(self.load()["proof"][0]["result"], True)

    def test_task_or_target_commit_change_resets_every_result(self):
        for workspace in (self.workspace, self.root):
            with self.subTest(workspace=workspace):
                self.mark_all_proven()
                previous = self.load()["proof_snapshot"]
                self.commit_change(workspace, "task-change" if workspace == self.workspace else "target-change")
                result = self.run_command("prove", "target")
                self.assertEqual(result.returncode, 1 if workspace == self.workspace else 2, result.stderr)
                record = self.assert_unproven()
                if workspace == self.root:
                    self.assertIsNone(record["proof_snapshot"])
                    git(self.workspace, "merge", "--no-edit", "refs/heads/main")
                    self.assertEqual(self.run_command("prove", "target").returncode, 1)
                    record = self.assert_unproven()
                self.assertNotEqual(record["proof_snapshot"], previous)
                self.assertEqual(record["proof_snapshot"], {
                    "task": git(self.workspace, "rev-parse", "HEAD"),
                    "target": git(self.root, "rev-parse", "refs/heads/main"),
                })

    def test_commit_change_during_verification_rejects_result_and_clears_all(self):
        for workspace in (self.workspace, self.root):
            with self.subTest(workspace=workspace):
                self.mark_all_proven()
                self.commit_change(workspace, "task-change" if workspace == self.workspace else "target-change")
                result = self.run_command("prove", "target", "--item", "2", "--result", "true")
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertEqual(result.stdout, "")
                self.assertIn("snapshot changed" if workspace == self.workspace else "does not include current target",
                              result.stderr)
                self.assert_unproven()

    def assert_target_requires_merge(self, *, update=False, diverged=False):
        if diverged:
            self.commit_change(self.workspace, "task-change")
            self.assertEqual(self.run_command("prove", "target").returncode, 1)
        self.mark_all_proven()
        self.commit_change(self.root, "target-change")
        before = self.snapshot()
        args = ("--item", "1", "--result", "true") if update else ()
        result = self.run_command("prove", "target", *args)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertIn("merge target into task", result.stderr)
        self.assertIsNone(self.assert_unproven()["proof_snapshot"])
        after = self.snapshot()
        key = str(self.path.relative_to(self.root))
        del before[key], after[key]
        self.assertEqual(after, before)  # No Git or unrelated record writes.
        self.assert_rejected("prove", "target", *args)

        # The agent combines branches; prove never does so itself.
        git(self.workspace, "merge", "--no-edit", "refs/heads/main")
        result = self.run_command("prove", "target", "--item", "1", "--result", "true")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("repeat verification", result.stderr)
        self.assert_unproven()
        self.assertEqual(self.run_command("prove", "target").returncode, 1)
        self.mark_all_proven()

    def test_target_ahead_requires_merge_before_display(self):
        self.assert_target_requires_merge()

    def test_target_ahead_requires_merge_before_recording(self):
        self.assert_target_requires_merge(update=True)

    def test_diverged_target_requires_merge_before_display(self):
        self.assert_target_requires_merge(diverged=True)

    def test_diverged_target_requires_merge_before_recording(self):
        self.assert_target_requires_merge(update=True, diverged=True)

    def test_matching_snapshot_does_not_bypass_ancestry_check(self):
        self.commit_change(self.root)
        self.record["proof_snapshot"] = {
            "task": git(self.workspace, "rev-parse", "HEAD"),
            "target": git(self.root, "rev-parse", "HEAD"),
        }
        self.record["proof"] = [check(True), review(True)]
        self.store()
        result = self.run_command("prove", "target", "--item", "1", "--result", "true")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("does not include current target", result.stderr)
        self.assertIsNone(self.assert_unproven()["proof_snapshot"])

    def test_ancestry_git_errors_stop_proof_without_writes(self):
        self.mark_all_proven()
        run = subprocess.run
        for code, stderr in ((128, "fatal: broken repository"), (2, ""), (-15, "")):
            for kwargs in ({}, {"item": 1, "result": True}):
                with self.subTest(code=code, kwargs=kwargs):
                    def fail_ancestry(args, **options):
                        if "--is-ancestor" in args:
                            snapshot = self.load()["proof_snapshot"]
                            self.assertEqual(args[-2:], [snapshot["target"], snapshot["task"]])
                            return subprocess.CompletedProcess(args, code, "", stderr)
                        return run(args, **options)

                    before = self.snapshot()
                    with patch.object(honeycomb.subprocess, "run", side_effect=fail_ancestry):
                        with self.assertRaisesRegex(ValueError, stderr or "git merge-base failed"):
                            honeycomb.prove_task(self.tasks, "target", **kwargs)
                    self.assertEqual(self.snapshot(), before)

    def test_dirty_worktree_refuses_proof_and_clears_old_passes(self):
        for mode in ("unstaged", "staged", "untracked", "deleted"):
            for update in (False, True):
                with self.subTest(mode=mode, update=update):
                    self.mark_all_proven()
                    path = self.workspace / ("new" if mode == "untracked" else ".gitignore")
                    if mode == "deleted":
                        path.unlink()
                    else:
                        path.write_text("changed\n")
                    if mode == "staged":
                        git(self.workspace, "add", ".gitignore")
                    args = ("--item", "1", "--result", "true") if update else ()
                    result = self.run_command("prove", "target", *args)
                    self.assertEqual(result.returncode, 2, result.stderr)
                    self.assertEqual(result.stdout, "")
                    self.assertIn("uncommitted changes", result.stderr)
                    self.assertIsNone(self.assert_unproven()["proof_snapshot"])
                    # Rejecting again must not write the already invalidated record.
                    self.assert_rejected("prove", "target", *args)
                    git(self.workspace, "reset", "--hard", "HEAD")
                    if mode == "untracked":
                        path.unlink()
                    # Returning to the same commits does not restore earlier passes.
                    result = self.run_command("prove", "target")
                    self.assertEqual(result.returncode, 1, result.stderr)
                    self.assert_unproven()

    def test_untracked_files_cannot_be_hidden_by_git_configuration(self):
        self.mark_all_proven()
        git(self.workspace, "config", "status.showUntrackedFiles", "no")
        (self.workspace / "untracked").write_text("new code")
        result = self.run_command("prove", "target")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assert_unproven()

    def test_target_is_parent_branch_not_main_for_child(self):
        task = {
            "id": "child", "parent": "target", "depends_on": [],
            "outcome": "Child", "scope": "Child",
            "proof": [{"condition": "Works", "verification": "Check it"}],
        }
        self.assertEqual(self.run_command("define", data=json.dumps(task)).returncode, 0)
        self.assertEqual(self.run_command("execute", "child").returncode, 0)
        self.assertEqual(self.run_command("prove", "child").returncode, 1)
        self.assertEqual(self.run_command("prove", "child", "--item", "1", "--result", "true").returncode, 0)
        self.commit_change(self.root)
        self.assertEqual(self.run_command("prove", "child").returncode, 0)
        self.commit_change(self.workspace)
        result = self.run_command("prove", "child")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("does not include current target", result.stderr)
        child = json.loads((self.tasks / "child.json").read_text())
        self.assertIsNone(child["proof"][0]["result"])
        self.assertIsNone(child["proof_snapshot"])
        child_workspace = self.home / "worktrees" / "child"
        git(child_workspace, "merge", "--no-edit", "refs/heads/honeycomb/target")
        self.assertEqual(self.run_command("prove", "child").returncode, 1)
        child = json.loads((self.tasks / "child.json").read_text())
        self.assertEqual(child["proof_snapshot"]["target"], git(self.workspace, "rev-parse", "HEAD"))

    def test_uses_local_target_ref_not_current_checkout_or_same_named_tag(self):
        self.mark_all_proven()
        git(self.root, "checkout", "-b", "other")
        self.commit_change(self.root)
        git(self.root, "tag", "main")
        (self.root / "dirty").write_text("uncommitted target work is not part of proof")
        self.assertEqual(self.run_command("prove", "target").returncode, 0)
        self.assertEqual(self.load()["proof_snapshot"]["target"],
                         git(self.root, "rev-parse", "refs/heads/main"))

    def test_missing_workspace_or_target_ref_rejected_without_writes(self):
        git(self.root, "branch", "-m", "other")
        self.assert_rejected("prove", "target")
        git(self.root, "branch", "-m", "main")
        git(self.root, "worktree", "remove", str(self.workspace))
        self.assert_rejected("prove", "target")

    def test_wrong_branch_or_detached_workspace_rejected_without_writes(self):
        git(self.workspace, "checkout", "-b", "wrong")
        self.assert_rejected("prove", "target")
        git(self.workspace, "checkout", "--detach")
        self.assert_rejected("prove", "target", "--item", "1", "--result", "true")

    def test_workspace_must_belong_to_expected_repository(self):
        git(self.root, "worktree", "remove", str(self.workspace))
        self.workspace.mkdir()
        init_repository(self.workspace)
        git(self.workspace, "checkout", "-b", "honeycomb/target")
        self.assert_rejected("prove", "target")

    def test_proof_can_be_recorded_from_task_worktree(self):
        result = subprocess.run(
            [sys.executable, str(COMMAND), "prove", "target", "--item", "1", "--result", "true"],
            cwd=self.workspace, env={**os.environ, "HONEYCOMB_DIR": str(self.home)},
            capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIs(self.load()["proof"][0]["result"], True)

    def test_failed_invalidation_write_preserves_record(self):
        self.mark_all_proven()
        self.commit_change(self.workspace)
        before = self.snapshot()
        with patch.object(honeycomb.os, "replace", side_effect=OSError("write failed")):
            with self.assertRaisesRegex(OSError, "write failed"):
                honeycomb.prove_task(self.tasks, "target")
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.run_command("prove", "target").returncode, 1)
        self.assert_unproven()

    def test_define_execute_prove_integration(self):
        task = {
            "id": "new", "outcome": "Example", "scope": "Example",
            "parent": None, "depends_on": [],
            "proof": [{k: v for k, v in entry.items() if k != "result"} for entry in (check(), review())],
        }
        defined = self.run_command("define", data=json.dumps(task))
        self.assertEqual(defined.returncode, 0, defined.stderr)
        executed = self.run_command("execute", "new")
        self.assertEqual(executed.returncode, 0, executed.stderr)
        self.assertEqual(self.run_command("prove", "new").returncode, 1)
        self.assertEqual(self.run_command("prove", "new", "--item", "1", "--result", "true").returncode, 1)
        self.assertEqual(self.run_command("prove", "new", "--item", "2", "--result", "true").returncode, 0)
        record = json.loads((self.tasks / "new.json").read_text())
        self.assertEqual(record["state"], "running")
        self.assertEqual([entry["result"] for entry in record["proof"]], [True, True])
        self.assertEqual(self.run_command("ready").stdout, "")


if __name__ == "__main__":
    unittest.main()
