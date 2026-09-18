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


class CloseCommandTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="honeycomb close ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.tasks = self.root / ".honeycomb" / "tasks"
        self.tasks.mkdir(parents=True)
        init_repository(self.root)

    def agreement(self, task_id, parent=None, dependencies=()):
        return {
            "id": task_id, "parent": parent, "depends_on": list(dependencies),
            "outcome": "Deliver the agreed outcome", "scope": "Do not drop requirements",
            "proof": [{"condition": "Works", "verification": "Run tests"}],
        }

    def store(self, task_id, state="open", parent=None, dependencies=(), filename=None):
        task = self.agreement(task_id, parent, dependencies)
        record = {
            **task, "state": state,
            "proof": [{**item, "result": None} for item in task["proof"]],
            "metadata": {"keep": [True, None, "history — retained"]},
        }
        path = self.tasks / (filename or f"{task_id}.json")
        path.write_text(json.dumps(record))
        return path

    def load(self, task_id):
        return honeycomb.load_tasks(self.tasks)[task_id]

    def workspace(self, task_id):
        return self.root / ".honeycomb" / "worktrees" / task_id

    def run_command(self, *args, task=None, cwd=None):
        return subprocess.run(
            [sys.executable, str(COMMAND), *args], cwd=cwd or self.root,
            input=json.dumps(task) if task is not None else None,
            capture_output=True, text=True, timeout=10,
        )

    def succeed(self, *args, **kwargs):
        result = self.run_command(*args, **kwargs)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        return result

    def snapshot(self, *, ignore_locks=False):
        return {
            str(path.relative_to(self.root)): (path.read_bytes(), path.stat().st_mtime_ns)
            for path in self.root.rglob("*")
            if path.is_file() and not (ignore_locks and "honeycomb-locks" in path.parts)
        }

    def reject(self, *args, message=None, **kwargs):
        # Integration may create its persistent advisory lock, but nothing else.
        ignore_locks = args[0] == "integrate"
        before = self.snapshot(ignore_locks=ignore_locks)
        result = self.run_command(*args, **kwargs)
        self.assertEqual(result.returncode, 2, result)
        self.assertEqual(result.stdout, "")
        self.assertNotIn("Traceback", result.stderr)
        if message:
            self.assertIn(message, result.stderr)
        self.assertEqual(self.snapshot(ignore_locks=ignore_locks), before)

    def prove(self, task_id):
        result = self.run_command("prove", task_id)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.succeed("prove", task_id, "--item", "1", "--result", "true")

    def test_open_or_running_root_changes_only_state_without_git_requirements(self):
        git(self.root, "branch", "-m", "not-main")
        self.store("prerequisite")
        for state in ("open", "running"):
            with self.subTest(state=state):
                path = self.store("target", state, dependencies=["prerequisite"], filename="other.json")
                record = self.load("target")
                # Proof history is retained even when failed or incomplete.
                record["proof"] *= 3
                record["proof"] = [{**item, "result": value}
                                   for item, value in zip(record["proof"], (True, False, None))]
                record["proof_snapshot"] = {"task": "old-task", "target": "old-target"}
                path.write_text(json.dumps(record))
                before = self.snapshot()
                with patch.object(honeycomb, "git", side_effect=AssertionError("must not use Git")):
                    honeycomb.close_task(self.tasks, "target")
                self.assertEqual(self.load("target"), {**record, "state": "closed"})
                after = self.snapshot()
                key = str(path.relative_to(self.root))
                del before[key], after[key]
                self.assertEqual(after, before)

    def test_subtree_only_preserving_done_closed_and_outside_dependents(self):
        self.store("parent", "running")
        self.store("target", "running", "parent", filename="z-root.json")
        self.store("open-child", parent="target", filename="a-child.json")
        self.store("running-child", "running", "target")
        self.store("grandchild", parent="running-child")
        self.store("done-child", "done", "target")
        self.store("closed-child", "closed", "target")
        # Traverse previously closed nodes too, as required by retry.
        self.store("leftover", "running", "closed-child")
        self.store("outside-dependent", parent="parent", dependencies=["target"])
        self.store("unrelated")
        before = honeycomb.load_tasks(self.tasks)
        files = self.snapshot()
        result = self.succeed("close", "target")
        self.assertEqual(result.stdout, "")
        changed = {"target", "open-child", "running-child", "grandchild", "leftover"}
        for task_id, record in before.items():
            expected = {**record, "state": "closed"} if task_id in changed else record
            self.assertEqual(self.load(task_id), expected)
        after = self.snapshot()
        for path, contents in files.items():
            if path.endswith(".json") and json.loads(contents[0])["id"] in changed:
                continue
            self.assertEqual(after[path], contents)
        self.assertEqual(self.succeed("ready").stdout, "unrelated\n")
        self.reject("execute", "outside-dependent", message="not ready")
        before = self.snapshot()
        self.succeed("close", "target")
        self.assertEqual(self.snapshot(), before)

    def test_unready_child_can_close_without_running_parent_or_done_dependencies(self):
        self.store("parent")
        self.store("prerequisite", parent="parent")
        self.store("target", parent="parent", dependencies=["prerequisite"])
        self.succeed("close", "target")
        self.assertEqual(self.load("target")["state"], "closed")
        self.assertEqual(self.load("parent")["state"], "open")
        self.assertEqual(self.load("prerequisite")["state"], "open")

    def test_closed_is_terminal_and_does_not_satisfy_dependencies_at_any_depth(self):
        self.store("parent", "running")
        for task_id, parent in (("root", None), ("child", "parent")):
            with self.subTest(parent=parent):
                self.store(task_id, parent=parent)
                self.succeed("close", task_id)
                self.succeed("define", task=self.agreement(f"after-{task_id}", parent, [task_id]))
                self.reject("execute", f"after-{task_id}", message="not ready")
                self.reject("execute", task_id, message="not ready")
                self.reject("prove", task_id, message="not running")
                self.reject("prove", task_id, "--item", "1", "--result", "true", message="not running")
                self.reject("integrate", task_id, message="not running")
                self.reject("define", task=self.agreement(f"new-{task_id}", task_id), message="ancestor is closed")
                self.reject("define", task=self.agreement(task_id, parent), message="duplicate task id")
        self.assertEqual(self.succeed("ready").stdout, "")

    def test_parent_still_needs_own_proof_after_closing_failed_child(self):
        self.store("parent")
        self.succeed("execute", "parent")
        self.store("child", parent="parent")
        self.succeed("execute", "child")
        child = self.workspace("child")
        (child / "unfinished").write_text("keep my work")
        self.reject("prove", "parent", message="unfinished children")
        self.succeed("close", "child", cwd=child)
        self.assertFalse((child / ".honeycomb").exists())
        self.reject("integrate", "parent", message="incomplete or failed")
        self.prove("parent")
        self.succeed("integrate", "parent")
        self.assertEqual(self.load("parent")["state"], "done")
        self.assertEqual(self.load("child")["state"], "closed")
        self.assertEqual((child / "unfinished").read_text(), "keep my work")

    def test_dirty_work_and_integrated_child_commits_are_preserved(self):
        self.store("parent")
        self.succeed("execute", "parent")
        self.store("child", parent="parent")
        self.succeed("execute", "child")
        child = self.workspace("child")
        (child / "feature").write_text("committed child work")
        git(child, "add", "feature")
        git(child, "commit", "-m", "Child work")
        self.prove("child")
        self.succeed("integrate", "child")
        self.prove("parent")
        parent = self.workspace("parent")
        (parent / "feature").write_text("staged work")
        git(parent, "add", "feature")
        (parent / "feature").write_text("unstaged work")
        (parent / "untracked").write_text("new work")
        (self.root / "main-dirty").write_text("target work")
        self.store("active-child", parent="parent")
        self.succeed("execute", "active-child")
        (self.workspace("active-child") / "draft").write_text("descendant work")
        files = self.snapshot()
        records = honeycomb.load_tasks(self.tasks)
        self.succeed("close", "parent", cwd=parent)
        after = self.snapshot()
        for task_id in ("parent", "active-child"):
            self.assertEqual(self.load(task_id), {**records[task_id], "state": "closed"})
            key = f".honeycomb/tasks/{task_id}.json"
            del files[key], after[key]
        self.assertEqual(after, files)
        self.assertEqual((parent / "feature").read_text(), "unstaged work")
        self.assertEqual(git(parent, "show", "HEAD:feature"), "committed child work")
        self.reject("prove", "parent", message="not running")
        self.reject("integrate", "parent", message="not running")
        self.reject("close", "child", message="task is done")

    def test_interrupted_closure_blocks_descendants_and_retry_finishes(self):
        for failure_after in range(4):
            for error_type in (OSError, KeyboardInterrupt):
                with self.subTest(failure_after=failure_after, error_type=error_type):
                    self.store("root", "running", filename="z-root.json")
                    self.store("middle", "running", "root", filename="a-middle.json")
                    self.store("runner", "running", "middle")
                    self.store("leaf", parent="runner")
                    self.store("unrelated")
                    before = self.snapshot()
                    original_replace = honeycomb.os.replace
                    calls = []

                    def fail_replace(source, destination):
                        if len(calls) == failure_after:
                            raise error_type("interrupted write")
                        calls.append(json.loads(Path(source).read_text())["id"])
                        original_replace(source, destination)

                    with patch.object(honeycomb.os, "replace", side_effect=fail_replace):
                        expected_error = ValueError if error_type is OSError else KeyboardInterrupt
                        with self.assertRaises(expected_error) as caught:
                            honeycomb.close_task(self.tasks, "root")
                    if error_type is OSError:
                        self.assertIn("retry close root", str(caught.exception))
                    self.assertEqual(calls, ["root", "middle", "runner"][:failure_after])
                    self.assertEqual(list(self.tasks.glob(".task-*.tmp")), [])
                    if failure_after == 0:
                        self.assertEqual(self.snapshot(), before)
                    else:
                        self.assertEqual(self.load("root")["state"], "closed")
                        self.assertEqual(self.succeed("ready").stdout, "unrelated\n")
                        self.reject("execute", "leaf", message="not ready")
                        for task_id in ("middle", "runner"):
                            self.reject("prove", task_id)
                            self.reject("prove", task_id, "--item", "1", "--result", "true")
                            self.reject("integrate", task_id)
                            self.reject("define", task=self.agreement("new", task_id), message="ancestor is closed")
                    self.succeed("close", "root")
                    for task_id in ("root", "middle", "runner", "leaf"):
                        self.assertEqual(self.load(task_id)["state"], "closed")
                    self.assertEqual(self.load("unrelated")["state"], "open")
                    before = self.snapshot()
                    self.succeed("close", "root")
                    self.assertEqual(self.snapshot(), before)

    def test_invalid_requests_and_graphs_do_not_write(self):
        self.store("target")
        self.store("done", "done")
        for args in (("close",), ("close", "target", "extra"), ("close", "missing"),
                     ("close", "../outside"), ("close", "done")):
            self.reject(*args)
        invalid = self.tasks / "bad.json"
        for raw in (
            "{", "[]",
            '{"id":"bad","state":"invalid","depends_on":[]}',
            '{"id":"target","state":"open","depends_on":[]}',
            '{"id":"bad","state":"open","depends_on":["missing"]}',
            '{"id":"bad","state":"closed","depends_on":["bad"]}',
            '{"id":"bad","state":"closed","parent":"missing","depends_on":[]}',
            '{"id":"bad","state":"closed","parent":"bad","depends_on":[]}',
        ):
            with self.subTest(raw=raw):
                invalid.write_text(raw)
                self.reject("close", "target")
        invalid.unlink()
        for path in self.tasks.iterdir():
            path.unlink()
        self.tasks.rmdir()
        self.tasks.parent.rmdir()
        self.reject("close", "target", message="task directory not found")
        self.assertFalse(self.tasks.parent.exists())

    def test_legacy_root_and_unsafe_id_resolve_by_record_not_path(self):
        path = self.store("../legacy", filename="safe.json")
        record = self.load("../legacy")
        del record["parent"]
        path.write_text(json.dumps(record))
        self.succeed("close", "../legacy")
        self.assertEqual(json.loads(path.read_text()), {**record, "state": "closed"})
        self.assertEqual(list(self.tasks.iterdir()), [path])

    def test_deep_subtree_without_recursion_limit(self):
        for number in range(1100):
            self.store(f"T{number:04}", "running" if number < 1099 else "open",
                       f"T{number + 1:04}" if number < 1099 else None)
        self.succeed("close", "T1099")
        self.assertTrue(all(task["state"] == "closed" for task in honeycomb.load_tasks(self.tasks).values()))
        self.assertEqual(self.succeed("ready").stdout, "")


if __name__ == "__main__":
    unittest.main()
