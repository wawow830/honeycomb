"""Disposable Git fixtures; no developer identity or signing setup required."""

import subprocess


def git(root, *args):
    result = subprocess.run(
        ["git", "-C", str(root), "-c", "user.name=Honeycomb Test",
         "-c", "user.email=test@example.invalid", "-c", "commit.gpgsign=false", *args],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode:
        raise AssertionError(result.stderr)
    return result.stdout.strip()


def init_repository(root):
    git(root, "init", "-b", "main")
    (root / ".gitignore").write_text(".honeycomb/\n")
    git(root, "add", ".gitignore")
    git(root, "commit", "-m", "Initial commit")
