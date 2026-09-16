import importlib.util
import json
import os
from pathlib import Path
import select
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


class IntegrateCommandTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.home = self.root / ".honeycomb"
        self.tasks = self.home / "tasks"
        init_repository(self.root)
        self.initial = git(self.root, "rev-parse", "HEAD")
        self.define("T")
        self.execute("T")
        self.workspace = self.home / "worktrees" / "T"
        self.commit(self.workspace, "feature")
        self.prove("T")
        self.tip = git(self.workspace, "rev-parse", "HEAD")

    def run_command(self, *args, data=None, cwd=None):
        return subprocess.run(
            [sys.executable, str(COMMAND), *args], cwd=cwd or self.root,
            env={**os.environ, "HONEYCOMB_DIR": str(self.home)}, input=data,
            capture_output=True, text=True, timeout=10,
        )

    def define(self, task_id, parent=None, depends_on=None):
        result = self.run_command("define", data=json.dumps({
            "id": task_id, "parent": parent, "depends_on": depends_on or [],
            "outcome": "Deliver the feature", "scope": "Feature only",
            "proof": [
                {"condition": "Checks pass", "verification": "Run the tests"},
                {"condition": "Design accepted", "verification": "Ask the requester"},
            ],
        }))
        self.assertEqual(result.returncode, 0, result.stderr)

    def execute(self, task_id):
        result = self.run_command("execute", task_id)
        self.assertEqual(result.returncode, 0, result.stderr)

    def prove(self, task_id):
        result = self.run_command("prove", task_id)
        self.assertIn(result.returncode, (0, 1), result.stderr)
        for item in (1, 2):
            result = self.run_command("prove", task_id, "--item", str(item), "--result", "true")
            self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertEqual(result.returncode, 0, result.stderr)

    def load(self, task_id="T"):
        return json.loads((self.tasks / f"{task_id}.json").read_text())

    def store(self, task, task_id="T"):
        (self.tasks / f"{task_id}.json").write_text(json.dumps(task))

    def commit(self, workspace, filename):
        (workspace / filename).write_text(f"{filename}\n")
        git(workspace, "add", filename)
        git(workspace, "commit", "-m", filename)

    def snapshot(self):
        # Lock files persist by design; no other rejection-side writes are allowed.
        return {
            str(path.relative_to(self.root)): path.read_bytes()
            for path in self.root.rglob("*")
            if path.is_file() and "honeycomb-locks" not in path.parts
        }

    def reject(self, *args, message=None):
        before = self.snapshot()
        result = self.run_command("integrate", *args)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertNotIn("Traceback", result.stderr)
        if message:
            self.assertIn(message, result.stderr)
        self.assertEqual(self.snapshot(), before)
        return result

    def test_exact_fast_forward_then_done_and_dependent_ready(self):
        self.define("next", depends_on=["T"])
        other = (self.tasks / "next.json").read_bytes()
        before = self.load()
        result = self.run_command("integrate", "T", cwd=self.workspace)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")
        self.assertEqual(self.load(), {**before, "state": "done"})
        self.assertEqual(git(self.root, "rev-parse", "HEAD"), self.tip)
        self.assertEqual(git(self.root, "status", "--porcelain"), "")
        self.assertEqual((self.root / "feature").read_text(), "feature\n")
        self.assertEqual((self.tasks / "next.json").read_bytes(), other)
        self.assertEqual(self.run_command("ready").stdout, "next\n")
        self.reject("T", message="not running")

    def test_record_write_happens_after_target_moves(self):
        replace = honeycomb.replace_task

        def verify_order(path, record):
            self.assertEqual(git(self.root, "rev-parse", "HEAD"), self.tip)
            self.assertEqual(self.load()["state"], "running")
            replace(path, record)

        with patch.object(honeycomb, "replace_task", side_effect=verify_order):
            honeycomb.integrate_task(self.tasks, "T")
        self.assertEqual(self.load()["state"], "done")

    def test_resolves_id_from_record_not_filename(self):
        (self.tasks / "T.json").rename(self.tasks / "different.json")
        result = self.run_command("integrate", "T")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.tasks / "T.json").exists())
        self.assertEqual(json.loads((self.tasks / "different.json").read_text())["state"], "done")

    def test_child_integrates_into_parent_before_parent_can_finish(self):
        self.define("child", parent="T")
        self.reject("T", message="unfinished children")
        self.execute("child")
        child_workspace = self.home / "worktrees" / "child"
        self.commit(child_workspace, "child-feature")
        self.prove("child")
        child_tip = git(child_workspace, "rev-parse", "HEAD")
        result = self.run_command("integrate", "child")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(git(self.root, "rev-parse", "HEAD"), self.initial)
        self.assertEqual(git(self.workspace, "rev-parse", "HEAD"), child_tip)
        self.assertEqual(self.load("child")["state"], "done")
        self.reject("T", message="repeat proof")
        self.prove("T")
        result = self.run_command("integrate", "T")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(git(self.root, "rev-parse", "HEAD"), child_tip)

    def test_invalid_arguments_unknown_task_and_nonrunning_states(self):
        self.reject()
        self.reject("T", "extra")
        self.reject("missing", message="unknown task")
        for state in ("open", "done"):
            task = self.load()
            task["state"] = state
            self.store(task)
            self.reject("T", message="not running")

    def test_all_proof_items_must_be_true(self):
        for value in (None, False):
            task = self.load()
            task["proof"][1]["result"] = value
            self.store(task)
            self.reject("T", message="incomplete or failed")

    def test_invalid_proof_or_graph_is_rejected(self):
        original = self.load()
        for proof in ([], None, [{"result": True}], [
            {"condition": "Works", "verification": "Check", "result": 1},
        ]):
            self.store({**original, "proof": proof})
            self.reject("T", message="proof")
        self.store({**original, "depends_on": ["missing"]})
        self.reject("T", message="missing dependency")

    def test_missing_or_malformed_binding_is_rejected(self):
        original = self.load()
        for snapshot in (None, {}, True, {"task": self.tip},
                         {"task": self.tip, "target": self.initial, "extra": True}):
            self.store({**original, "proof_snapshot": snapshot})
            self.reject("T", message="repeat proof")
        del original["proof_snapshot"]
        self.store(original)
        self.reject("T", message="repeat proof")

    def test_changed_task_commit_is_rejected(self):
        self.commit(self.workspace, "later")
        self.reject("T", message="repeat proof")

    def test_changed_target_commit_is_rejected(self):
        self.commit(self.root, "later")
        self.reject("T", message="repeat proof")

    def test_matching_snapshot_cannot_bypass_fast_forward_requirement(self):
        self.commit(self.root, "later")
        task = self.load()
        task["proof_snapshot"]["target"] = git(self.root, "rev-parse", "HEAD")
        self.store(task)
        self.reject("T", message="does not include current target")

    def test_dirty_task_and_target_checkouts_are_preserved(self):
        for workspace in (self.workspace, self.root):
            for mode in ("untracked", "unstaged", "staged"):
                with self.subTest(workspace=workspace, mode=mode):
                    path = workspace / ("untracked" if mode == "untracked" else ".gitignore")
                    original = path.read_bytes() if path.exists() else None
                    path.write_text("local work\n")
                    if mode == "staged":
                        git(workspace, "add", ".gitignore")
                    self.reject("T")
                    if mode == "staged":
                        git(workspace, "reset", "HEAD", "--", ".gitignore")
                    if original is None:
                        path.unlink()
                    else:
                        path.write_bytes(original)

    def test_unfinished_git_operation_is_preserved(self):
        for workspace in (self.workspace, self.root):
            marker = Path(git(workspace, "rev-parse", "--path-format=absolute", "--git-path", "MERGE_HEAD"))
            marker.write_text(self.initial + "\n")
            self.reject("T", message="unfinished Git operation")
            marker.unlink()

    def test_local_ignored_file_is_not_overwritten(self):
        exclude = self.root / ".git" / "info" / "exclude"
        exclude.write_text("feature\n")
        (self.root / "feature").write_text("local ignored content\n")
        before = self.load()
        result = self.run_command("integrate", "T")
        self.assertEqual(result.returncode, 2, result.stderr)
        # Git may update ORIG_HEAD even when it refuses the fast-forward.
        self.assertEqual(self.load(), before)
        self.assertEqual(git(self.root, "rev-parse", "HEAD"), self.initial)
        self.assertEqual((self.root / "feature").read_text(), "local ignored content\n")

    def test_uses_explicit_ref_when_target_not_checked_out(self):
        git(self.root, "checkout", "-b", "other")
        self.commit(self.root, "other-change")
        other_tip = git(self.root, "rev-parse", "HEAD")
        git(self.root, "tag", "main")
        (self.root / "local").write_text("preserve this")
        result = self.run_command("integrate", "T")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(git(self.root, "rev-parse", "refs/heads/main"), self.tip)
        self.assertEqual(git(self.root, "rev-parse", "HEAD"), other_tip)
        self.assertEqual((self.root / "local").read_text(), "preserve this")
        self.assertFalse((self.root / "feature").exists())

    def test_updates_target_checked_out_elsewhere(self):
        git(self.root, "checkout", "-b", "other")
        checkout = self.home / "elsewhere"
        git(self.root, "worktree", "add", str(checkout), "main")
        result = self.run_command("integrate", "T")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(git(checkout, "rev-parse", "HEAD"), self.tip)
        self.assertTrue((checkout / "feature").exists())
        self.assertEqual(git(checkout, "status", "--porcelain"), "")
        self.assertEqual(git(self.root, "rev-parse", "HEAD"), self.initial)

    def test_empty_change_can_complete(self):
        self.define("empty")
        self.execute("empty")
        self.prove("empty")
        result = self.run_command("integrate", "empty")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(git(self.root, "rev-parse", "HEAD"), self.initial)
        self.assertEqual(self.load("empty")["state"], "done")

    def test_merge_failure_does_not_mark_done(self):
        run_git = honeycomb.git
        before = self.snapshot()

        def fail_merge(repository, *args):
            if "merge" in args:
                raise ValueError("simulated merge failure")
            return run_git(repository, *args)

        with patch.object(honeycomb, "git", side_effect=fail_merge):
            with self.assertRaisesRegex(ValueError, "simulated merge failure"):
                honeycomb.integrate_task(self.tasks, "T")
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.run_command("integrate", "T").returncode, 0)

    def test_unchecked_target_update_failure_does_not_mark_done(self):
        git(self.root, "checkout", "-b", "other")
        run_git = honeycomb.git
        before = self.snapshot()

        def fail_update(repository, *args):
            if args[0] == "update-ref":
                self.assertEqual(args, ("update-ref", "refs/heads/main", self.tip, self.initial))
                raise ValueError("simulated ref update failure")
            return run_git(repository, *args)

        with patch.object(honeycomb, "git", side_effect=fail_update):
            with self.assertRaisesRegex(ValueError, "simulated ref update failure"):
                honeycomb.integrate_task(self.tasks, "T")
        self.assertEqual(self.snapshot(), before)

    def test_ancestry_error_does_not_write_records_or_move_branches(self):
        before = self.snapshot()
        with patch.object(honeycomb, "git_is_ancestor", side_effect=ValueError("Git failed")):
            with self.assertRaisesRegex(ValueError, "Git failed"):
                honeycomb.integrate_task(self.tasks, "T")
        self.assertEqual(self.snapshot(), before)

    def test_multiple_target_checkouts_are_rejected(self):
        git(self.root, "worktree", "add", "--force", str(self.home / "duplicate"), "main")
        self.reject("T", message="multiple worktrees")

    def test_missing_workspace_or_target_is_rejected(self):
        git(self.root, "branch", "-m", "other")
        self.reject("T")
        git(self.root, "branch", "-m", "main")
        git(self.root, "worktree", "remove", str(self.workspace))
        self.reject("T")

    def test_record_failure_after_merge_leaves_running_and_can_be_reproven(self):
        before = self.load()
        with patch.object(honeycomb, "replace_task", side_effect=OSError("disk full")):
            with self.assertRaisesRegex(ValueError, "target advanced but task was not marked done"):
                honeycomb.integrate_task(self.tasks, "T")
        self.assertEqual(self.load(), before)
        self.assertEqual(git(self.root, "rev-parse", "HEAD"), self.tip)
        self.reject("T", message="repeat proof")
        self.prove("T")
        result = self.run_command("integrate", "T")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.load()["state"], "done")

    def test_merge_configuration_and_hooks_cannot_create_unproven_changes(self):
        git(self.root, "config", "merge.ff", "false")
        git(self.root, "config", "merge.autoStash", "true")
        git(self.root, "config", "branch.main.mergeOptions", "--squash")
        hooks = self.home / "hooks"
        hooks.mkdir()
        hook = hooks / "post-merge"
        hook.write_text("#!/bin/sh\ntouch hook-ran\n")
        hook.chmod(0o755)
        git(self.root, "config", "core.hooksPath", str(hooks))
        result = self.run_command("integrate", "T")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.root / "hook-ran").exists())
        self.assertEqual(git(self.root, "rev-parse", "HEAD"), self.tip)

    def test_same_target_waits_then_rechecks_current_state(self):
        # Announce lock attempts so the test does not depend on process startup speed.
        script = '''
import sys
from pathlib import Path
from contextlib import contextmanager
sys.path.insert(0, sys.argv[1])
import honeycomb
original = honeycomb.integration_lock
@contextmanager
def announced(*args):
    print("waiting", flush=True)
    with original(*args):
        print("locked", flush=True)
        yield
honeycomb.integration_lock = announced
try:
    honeycomb.integrate_task(Path(sys.argv[2]), "T")
except ValueError as error:
    print(str(error), file=sys.stderr)
    sys.exit(2)
'''
        with honeycomb.integration_lock(self.root, "main"):
            process = subprocess.Popen(
                [sys.executable, "-c", script, str(COMMAND.parent), str(self.tasks)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            )
            self.addCleanup(lambda: process.poll() is None and process.kill())
            self.assertTrue(select.select([process.stdout], [], [], 10)[0])
            self.assertEqual(process.stdout.readline(), "waiting\n")
            self.assertEqual(select.select([process.stdout], [], [], 0.2)[0], [])
            # Simulate another integrator's target update under the same lock.
            git(self.root, "merge", "--ff-only", self.tip)
        stdout, stderr = process.communicate(timeout=10)
        self.assertEqual(stdout, "locked\n")
        self.assertEqual(process.returncode, 2, stderr)
        self.assertIn("repeat proof", stderr)
        self.assertEqual(self.load()["state"], "running")

    def test_different_targets_have_independent_locks(self):
        self.define("child", parent="T")
        self.execute("child")
        self.prove("child")
        with honeycomb.integration_lock(self.root, "main"):
            result = self.run_command("integrate", "child")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.load("child")["state"], "done")


if __name__ == "__main__":
    unittest.main()
