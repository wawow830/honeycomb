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
spec = importlib.util.spec_from_file_location("honeycomb", COMMAND)
honeycomb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(honeycomb)


class ExecuteCommandTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="honeycomb execute ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.home = self.root / ".honeycomb"
        self.tasks = self.home / "tasks"
        self.tasks.mkdir(parents=True)
        init_repository(self.root)

    def store(self, task_id, state="open", dependencies=(), filename=None, parent=None):
        record = {
            "id": task_id,
            "outcome": "Preserve fields — including Unicode.",
            "scope": "Prepare execution.",
            "parent": parent,
            "depends_on": list(dependencies),
            "proof": [{"condition": "Works", "verification": "Run tests", "result": None}],
            "state": state,
            "metadata": {"nested": [True, None, 42]},
        }
        path = self.tasks / (filename or f"{task_id}.json")
        path.write_text(json.dumps(record), encoding="utf-8")
        return path

    def workspace(self, task_id="target"):
        return self.home / "worktrees" / task_id

    def run_command(self, *args, data=None, cwd=None):
        return subprocess.run(
            [sys.executable, str(COMMAND), *args],
            cwd=cwd or self.root, input=data,
            capture_output=True, text=True, timeout=10,
        )

    def snapshot(self, root=None):
        return {
            str(path.relative_to(self.root)): (path.read_bytes(), path.stat().st_mtime_ns)
            for path in (root or self.root).rglob("*") if path.is_file()
        }

    def assert_rejected(self, *args, cwd=None, message=None):
        before = self.snapshot()
        result = self.run_command(*args, cwd=cwd)
        self.assertEqual(result.returncode, 2, result)
        self.assertEqual(result.stdout, "")
        self.assertIn("error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        if message:
            self.assertIn(message, result.stderr)
        self.assertEqual(self.snapshot(), before)

    def assert_no_workspace(self):
        self.assertFalse(self.workspace().exists())
        self.assertNotIn("honeycomb/target", git(self.root, "branch", "--list"))
        self.assertNotIn(str(self.workspace()), git(self.root, "worktree", "list", "--porcelain"))

    def test_root_prepares_workspace_and_changes_only_record_state(self):
        path = self.store("target")
        self.store("unrelated")
        self.store("dependent", dependencies=["target"])
        before = self.snapshot(self.tasks)
        record = json.loads(path.read_text())
        main = git(self.root, "rev-parse", "main")
        result = self.run_command("execute", "target")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, f"{self.workspace()}\n")
        self.assertEqual(result.stderr, "")
        self.assertEqual(json.loads(path.read_text()), {**record, "state": "running"})
        after = self.snapshot(self.tasks)
        key = str(path.relative_to(self.root))
        del before[key], after[key]
        self.assertEqual(after, before)
        self.assertEqual(git(self.workspace(), "branch", "--show-current"), "honeycomb/target")
        self.assertEqual(git(self.workspace(), "rev-parse", "HEAD"), main)
        self.assertEqual(git(self.root, "rev-parse", "main"), main)
        self.assertEqual(git(self.root, "branch", "--show-current"), "main")
        self.assertFalse((self.workspace() / ".honeycomb").exists())
        self.assertEqual(self.run_command("ready").stdout, "unrelated\n")

    def test_child_uses_parent_commit_not_main_or_uncommitted_work(self):
        self.store("parent")
        result = self.run_command("execute", "parent")
        self.assertEqual(result.returncode, 0, result.stderr)
        parent = self.workspace("parent")
        (parent / "feature").write_text("committed parent work")
        git(parent, "add", "feature")
        git(parent, "commit", "-m", "Parent work")
        (parent / "feature").write_text("uncommitted parent work")
        parent_head = git(parent, "rev-parse", "HEAD")
        self.store("target", parent="parent")
        # Discovery from a linked worktree still uses the main checkout's records.
        result = self.run_command("execute", "target", cwd=parent)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(git(self.workspace(), "rev-parse", "HEAD"), parent_head)
        self.assertEqual((self.workspace() / "feature").read_text(), "committed parent work")
        self.assertEqual((parent / "feature").read_text(), "uncommitted parent work")
        self.assertNotEqual(parent_head, git(self.root, "rev-parse", "main"))
        self.assertFalse((self.root / "feature").exists())

    def test_main_target_not_current_branch_or_same_named_tag(self):
        git(self.root, "checkout", "-b", "other")
        (self.root / "other").write_text("other branch")
        git(self.root, "add", "other")
        git(self.root, "commit", "-m", "Other branch")
        git(self.root, "tag", "main")
        (self.root / "dirty").write_text("leave alone")
        self.store("target")
        result = self.run_command("execute", "target")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(git(self.workspace(), "rev-parse", "HEAD"),
                         git(self.root, "rev-parse", "refs/heads/main"))
        self.assertFalse((self.workspace() / "other").exists())
        self.assertEqual((self.root / "dirty").read_text(), "leave alone")
        self.assertEqual(git(self.root, "branch", "--show-current"), "other")

    def test_all_dependencies_done(self):
        self.store("A", "done")
        self.store("B", "done")
        path = self.store("target", dependencies=["A", "B"])
        result = self.run_command("execute", "target")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(path.read_text())["state"], "running")

    def test_each_unfinished_dependency_blocks_execute(self):
        self.store("A", "done")
        for state in ("open", "running"):
            with self.subTest(state=state):
                self.store("B", state)
                self.store("target", dependencies=["A", "B"])
                self.assert_rejected("execute", "target", message="not ready")

    def test_running_and_done_tasks_are_rejected(self):
        for state in ("running", "done"):
            with self.subTest(state=state):
                self.store("target", state)
                self.assert_rejected("execute", "target", message="not ready")

    def test_repeated_execute_is_rejected(self):
        self.store("target")
        result = self.run_command("execute", "target")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_rejected("execute", "target", message="not ready")

    def test_unknown_id_is_rejected(self):
        self.store("target")
        for task_id in ("missing", "", "../outside", "/absolute"):
            with self.subTest(task_id=task_id):
                self.assert_rejected("execute", task_id, message="unknown task")

    def test_uses_record_id_not_filename(self):
        path = self.store("target", filename="different.json")
        result = self.run_command("execute", "target")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(path.read_text())["state"], "running")
        self.assertEqual(list(self.tasks.iterdir()), [path])

    def test_legacy_record_without_parent_executes_as_root(self):
        path = self.store("target")
        record = json.loads(path.read_text())
        del record["parent"]
        path.write_text(json.dumps(record))
        result = self.run_command("execute", "target")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(path.read_text()), {**record, "state": "running"})
        self.assertEqual(git(self.workspace(), "rev-parse", "HEAD"),
                         git(self.root, "rev-parse", "main"))

    def test_unsafe_stored_id_or_parent_cannot_be_used_as_a_path(self):
        self.store("../outside", state="running", filename="safe.json")
        self.store("target", parent="../outside")
        self.assert_rejected("execute", "target", message="cannot be used for execution")
        self.store("../outside", filename="safe.json")
        self.assert_rejected("execute", "../outside", message="cannot be used for execution")
        self.assertFalse((self.home / "outside").exists())

    def test_invalid_stored_records_or_graph_prevent_execute(self):
        self.store("target")
        cases = (
            "{", "[]",
            '{"id":"bad","state":"invalid","depends_on":[]}',
            '{"id":"bad","state":"pending","depends_on":[]}',
            '{"id":"target","state":"open","depends_on":[]}',
            '{"id":"bad","state":"open","depends_on":["missing"]}',
            '{"id":"bad","state":"done","depends_on":["bad"]}',
            '{"id":"bad","state":"open","depends_on":["target","target"]}',
            '{"id":"bad","id":"other","state":"open","depends_on":[]}',
            '{"id":"bad","state":"open","depends_on":[],"extra":NaN}',
        )
        for raw in cases:
            with self.subTest(raw=raw):
                (self.tasks / "bad.json").write_text(raw)
                self.assert_rejected("execute", "target")
        (self.tasks / "bad.json").write_bytes(b"\xff")
        self.assert_rejected("execute", "target")

    def test_missing_or_non_directory_storage(self):
        self.tasks.rmdir()
        self.assert_rejected("execute", "target", message="task directory not found")
        self.assertFalse(self.tasks.exists())
        self.tasks.write_text("not a directory")
        self.assert_rejected("execute", "target", message="task directory not found")

    def test_exactly_one_id_required_and_start_removed(self):
        self.store("target")
        for args in (("execute",), ("execute", "target", "extra"),
                     ("ready", "target"), ("define", "target"), ("start", "target")):
            with self.subTest(args=args):
                self.assert_rejected(*args)

    def test_define_execute_ready_integration(self):
        task = {
            "id": "new-task", "outcome": "Example", "scope": "Example",
            "parent": None, "depends_on": [],
            "proof": [{"condition": "Works", "verification": "Run tests; require exit 0."}],
        }
        defined = self.run_command("define", data=json.dumps(task))
        self.assertEqual(defined.returncode, 0, defined.stderr)
        self.assertEqual(self.run_command("ready").stdout, "new-task\n")
        executed = self.run_command("execute", "new-task")
        self.assertEqual(executed.returncode, 0, executed.stderr)
        self.assertEqual(self.run_command("ready").stdout, "")
        record = json.loads((self.tasks / "new-task.json").read_text())
        self.assertEqual(record, {
            **task, "state": "running",
            "proof": [{**item, "result": None} for item in task["proof"]],
        })

    def test_existing_branch_is_never_reused_or_reset(self):
        self.store("target")
        git(self.root, "branch", "honeycomb/target")
        self.assert_rejected("execute", "target", message="branch already exists")

    def test_conflicting_branch_namespace_leaves_existing_branch_alone(self):
        path = self.store("target")
        before = path.read_bytes()
        git(self.root, "branch", "honeycomb")
        tip = git(self.root, "rev-parse", "honeycomb")
        result = self.run_command("execute", "target")
        self.assertEqual(result.returncode, 2, result)
        self.assertEqual(result.stdout, "")
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(git(self.root, "rev-parse", "honeycomb"), tip)
        self.assert_no_workspace()

    def test_existing_workspace_is_never_reused(self):
        self.store("target")
        self.workspace().mkdir(parents=True)
        (self.workspace() / "keep").write_text("user work")
        self.assert_rejected("execute", "target", message="workspace already exists")

    def test_dangling_workspace_symlink_is_rejected(self):
        self.store("target")
        self.workspace().parent.mkdir()
        self.workspace().symlink_to(self.root / "missing")
        self.assert_rejected("execute", "target", message="workspace already exists")
        self.assertTrue(self.workspace().is_symlink())

    def test_missing_main_is_rejected_without_changes(self):
        self.store("target")
        git(self.root, "branch", "-m", "other")
        self.assert_rejected("execute", "target")
        self.assert_no_workspace()

    def test_missing_parent_branch_is_rejected_without_changes(self):
        self.store("parent", state="running")
        self.store("target", parent="parent")
        self.assert_rejected("execute", "target")
        self.assert_no_workspace()

    def test_caller_outside_repository_is_rejected(self):
        with tempfile.TemporaryDirectory() as outside:
            home = Path(outside) / ".honeycomb"
            (home / "tasks").mkdir(parents=True)
            source = self.store("target")
            destination = home / "tasks" / "target.json"
            destination.write_bytes(source.read_bytes())
            before = destination.read_bytes()
            self.assert_rejected("execute", "target", cwd=outside)
            self.assertEqual(destination.read_bytes(), before)
            self.assertFalse((home / "worktrees").exists())

    def test_record_write_failure_rolls_back_preparation(self):
        path = self.store("target")
        before = path.read_bytes()
        with patch.object(honeycomb.os, "replace", side_effect=OSError("write failed")):
            with self.assertRaisesRegex(OSError, "write failed"):
                honeycomb.execute_task(self.tasks, "target")
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(list(self.tasks.iterdir()), [path])
        self.assert_no_workspace()
        # An ordinary failure is retryable without manual cleanup.
        result = self.run_command("execute", "target")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_checkout_failure_cleans_branch_and_leaves_task_open(self):
        path = self.store("target")
        before = path.read_bytes()
        # Git may create a branch/worktree before post-checkout fails.
        hook = self.root / ".git" / "hooks" / "post-checkout"
        hook.write_text("#!/bin/sh\nexit 1\n")
        hook.chmod(0o755)
        git(self.root, "config", "core.hooksPath", str(hook.parent))
        result = self.run_command("execute", "target")
        self.assertEqual(result.returncode, 2, result)
        self.assertEqual(result.stdout, "")
        self.assertEqual(path.read_bytes(), before)
        self.assert_no_workspace()

    def test_cleanup_never_discards_unexpected_work(self):
        path = self.store("target")
        before = path.read_bytes()

        def fail_write(*args):
            (self.workspace() / "keep").write_text("unexpected work")
            raise OSError("write failed")

        with patch.object(honeycomb, "replace_task", side_effect=fail_write):
            with self.assertRaisesRegex(ValueError, "cleanup failed"):
                honeycomb.execute_task(self.tasks, "target")
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual((self.workspace() / "keep").read_text(), "unexpected work")
        self.assertIn("honeycomb/target", git(self.root, "branch", "--list"))


if __name__ == "__main__":
    unittest.main()
