"""Exercise the copied, project-local skill without installation-time configuration."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from git_support import git, init_repository


SKILL = Path(__file__).resolve().parents[1] / ".agents/skills/honeycomb"
SCRIPT = Path(".agents/skills/honeycomb/scripts/honeycomb.py")


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="honeycomb discovery ")
        self.addCleanup(self.temporary.cleanup)
        self.container = Path(self.temporary.name).resolve()
        self.root = self.container / "project with spaces"
        self.root.mkdir()
        init_repository(self.root)
        shutil.copytree(SKILL, self.root / ".agents/skills/honeycomb",
                        ignore=shutil.ignore_patterns("__pycache__"))
        git(self.root, "add", ".agents")
        git(self.root, "commit", "-m", "Install Honeycomb skill")
        self.command = self.root / SCRIPT
        self.home = self.root / ".honeycomb"

    def run_command(self, *args, cwd=None, command=None, task=None, env=None):
        environment = os.environ.copy()
        environment.pop("HONEYCOMB_DIR", None)
        if env:
            environment.update(env)
        return subprocess.run(
            [sys.executable, str(command or self.command), *args],
            cwd=cwd or self.root, env=environment,
            input=json.dumps(task) if task is not None else None,
            capture_output=True, text=True, timeout=10,
        )

    def define(self, task_id="feature", **options):
        result = self.run_command("define", task={
            "id": task_id, "parent": None, "depends_on": [],
            "outcome": "Deliver a greeting", "scope": "Add greeting.txt only",
            "proof": [{"condition": "Greeting is correct", "verification": "Read greeting.txt; require hello"}],
        }, **options)
        self.assertEqual(result.returncode, 0, result.stderr)

    def assert_error(self, result):
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertNotIn("Traceback", result.stderr)

    def test_fresh_install_ready_needs_no_state_setup(self):
        result = self.run_command("ready")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertFalse(self.home.exists())
        self.assertEqual(git(self.root, "status", "--porcelain"), "")

    def test_subdirectory_uses_project_root(self):
        nested = self.root / "src" / "nested"
        nested.mkdir(parents=True)
        self.define(cwd=nested)
        self.assertTrue((self.home / "tasks/feature.json").is_file())
        self.assertFalse((nested / ".honeycomb").exists())
        self.assertEqual(self.run_command("ready", cwd=nested).stdout, "feature\n")

    def test_external_linked_worktree_uses_shared_records(self):
        linked = self.container / "linked checkout"
        git(self.root, "worktree", "add", "-b", "other", str(linked))
        nested = linked / "src"
        nested.mkdir()
        self.define(cwd=nested, command=linked / SCRIPT)
        self.assertEqual(self.run_command("ready").stdout, "feature\n")
        self.assertFalse((linked / ".honeycomb").exists())
        self.assertFalse((nested / ".honeycomb").exists())

    def test_detached_worktree_uses_shared_records(self):
        linked = self.container / "detached"
        git(self.root, "worktree", "add", "--detach", str(linked))
        self.define(cwd=linked, command=linked / SCRIPT)
        self.assertTrue((self.home / "tasks/feature.json").is_file())
        self.assertFalse((linked / ".honeycomb").exists())

    def test_separate_git_directory_is_rejected_before_creating_state(self):
        git(self.root, "init", "--separate-git-dir", str(self.container / "metadata"))
        linked = self.container / "linked"
        git(self.root, "worktree", "add", "-b", "other", str(linked))
        for cwd in (self.root, linked):
            for command in ("ready", "define"):
                result = self.run_command(command, cwd=cwd)
                self.assert_error(result)
                self.assertIn("separate Git directories are not supported", result.stderr)
        self.assertFalse(self.home.exists())
        self.assertFalse((linked / ".honeycomb").exists())
        self.assertFalse((self.container / "metadata/.honeycomb").exists())

    def test_caller_project_wins_over_script_location_and_old_environment(self):
        other = self.container / "other project"
        other.mkdir()
        init_repository(other)
        self.define(cwd=other, env={"HONEYCOMB_DIR": str(self.home)})
        self.assertTrue((other / ".honeycomb/tasks/feature.json").is_file())
        self.assertFalse(self.home.exists())

    def test_nested_repository_does_not_use_outer_records(self):
        self.define()
        nested = self.root / "nested repository"
        nested.mkdir()
        init_repository(nested)
        self.define("inner", cwd=nested)
        self.assertEqual(self.run_command("ready", cwd=nested).stdout, "inner\n")
        self.assertEqual(self.run_command("ready").stdout, "feature\n")

    def test_outside_repository_rejected_without_creating_state(self):
        for command in ("ready", "define", "execute", "prove", "integrate"):
            args = (command,) if command in ("ready", "define") else (command, "feature")
            self.assert_error(self.run_command(*args, cwd=self.container))
        self.assertFalse((self.container / ".honeycomb").exists())
        self.assertFalse(self.home.exists())

    def test_git_metadata_and_bare_repository_rejected(self):
        self.assert_error(self.run_command("ready", cwd=self.root / ".git"))
        bare = self.container / "bare.git"
        git(self.root, "clone", "--bare", str(self.root), str(bare))
        self.assert_error(self.run_command("ready", cwd=bare))
        linked = self.container / "bare-linked"
        git(bare, "worktree", "add", str(linked), "main")
        result = self.run_command("ready", cwd=linked)
        self.assert_error(result)
        self.assertIn("non-bare main checkout", result.stderr)
        self.assertFalse((linked / ".honeycomb").exists())
        self.assertFalse((bare / ".honeycomb").exists())

    def test_unborn_repository_can_define_but_cannot_execute(self):
        unborn = self.container / "unborn"
        unborn.mkdir()
        git(unborn, "init", "-b", "main")
        self.define(cwd=unborn)
        self.assertEqual(self.run_command("ready", cwd=unborn).stdout, "feature\n")
        self.assert_error(self.run_command("execute", "feature", cwd=unborn))
        self.assertFalse((unborn / ".honeycomb/worktrees").exists())

    def test_copied_skill_completes_lifecycle_from_task_worktree(self):
        self.define()
        result = self.run_command("execute", "feature")
        self.assertEqual(result.returncode, 0, result.stderr)
        workspace = Path(result.stdout.strip())
        command = workspace / SCRIPT
        self.assertTrue(command.is_file())
        (workspace / "greeting.txt").write_text("hello\n")
        git(workspace, "add", "greeting.txt")
        git(workspace, "commit", "-m", "Add greeting")
        prepared = self.run_command("prove", "feature", cwd=workspace, command=command)
        self.assertEqual(prepared.returncode, 1, prepared.stderr)
        # Actually perform the defined verification before recording its result.
        self.assertEqual((workspace / "greeting.txt").read_text(), "hello\n")
        proven = self.run_command("prove", "feature", "--item", "1", "--result", "true",
                                  cwd=workspace, command=command)
        self.assertEqual(proven.returncode, 0, proven.stderr)
        integrated = self.run_command("integrate", "feature", cwd=workspace, command=command)
        self.assertEqual(integrated.returncode, 0, integrated.stderr)
        self.assertEqual((self.root / "greeting.txt").read_text(), "hello\n")
        record = json.loads((self.home / "tasks/feature.json").read_text())
        self.assertEqual(record["state"], "done")
        self.assertFalse((workspace / ".honeycomb").exists())
        self.assertEqual(git(self.root, "status", "--porcelain"), "")


if __name__ == "__main__":
    unittest.main()
