# honeycomb

## Goals
- turbo speed development
- without compromise of quality or taste
- be as deterministic as possible
    - clear bounds
    - clear input/processing/output
    - everything must follow a structure
- stack agnostic
- simplicity rules

## Usage

Requires Python 3.10+, with no third-party Python packages. `execute`, `prove`,
and `integrate` also require Git and a local `main` branch with at least one
commit. `integrate` requires Unix advisory file locks (`fcntl.flock`).

From the main checkout, set the shared record location:

```sh
export HONEYCOMB_DIR="$PWD/.honeycomb"
```

Records are tool-managed JSON. Keep this absolute path when using worktrees;
records are shared, not copied into each checkout. Keep `.honeycomb/` gitignored.

### Define a task

```sh
python3 honeycomb.py define <<'JSON'
{
  "id": "list-ready",
  "outcome": "Developers can list tasks ready to run.",
  "scope": "Read records only. No dispatch or state changes.",
  "parent": null,
  "depends_on": [],
  "proof": [
    {
      "condition": "Only open tasks with all dependencies done and a running parent (unless root) are listed.",
      "verification": "Run python3 -m unittest discover -s tests; require exit 0."
    }
  ]
}
JSON
```

`define` reads one JSON object from stdin, validates it, and creates
`$HONEYCOMB_DIR/tasks/<id>.json`. Success is silent, with exit code `0`.

- Exactly the six input fields above are required.
- IDs use 1–128 ASCII letters, digits, underscores, or hyphens,
  starting with a letter or digit.
- Outcome, scope, proof conditions, and verification instructions must be
  nonblank strings. Proof must contain at least one item.
- `parent` is `null` or an existing task ID. Store `parent`, not children.
  Defining a child under a `done` parent is rejected without changing records.
- Dependencies are unique existing sibling IDs; roots count as siblings.
  Parent links and dependencies must be acyclic.
- Each input proof item contains exactly `condition` and `verification`.
  Verification is plain language, with no reserved strings or typed actions.
- Tooling initializes `state: "open"` and every proof `result: null`.
  Callers cannot supply managed fields.

Invalid input, invalid stored graphs, duplicate IDs, and existing destination
files produce exit code `2`, without changing records. Tasks are never overwritten.

The requester approves overall intent before execution. Subtasks within its
boundaries need no separate approval. `define` stores records; it does not enforce
approval, start tasks, run verification, or perform Git operations.

### List ready tasks

```sh
mkdir -p "$HONEYCOMB_DIR/tasks"
python3 honeycomb.py ready
```

Prints sorted IDs of open tasks whose dependencies are all done and whose parent
is running (unless root). No ready tasks means empty output and success. Invalid
records or graphs produce exit code `2` with no partial output. This command
never changes records.

Scheduling reads `id`, `state`, `parent`, and `depends_on`; it does not validate
proof. Stored IDs must be unique, nonempty strings without whitespace. States
are `open`, `running`, and `done`. Missing `parent` still means root.
Every command validates parent references, sibling dependencies, and cycles.

### Prepare task execution

```sh
python3 honeycomb.py execute list-ready
```

`execute <id>` checks readiness, creates a branch and worktree, then marks the
task `running`. Success prints the absolute workspace path and exits `0`.
All other record fields and other tasks remain unchanged.

```text
branch:    honeycomb/<id>
workspace: $HONEYCOMB_DIR/worktrees/<id>
target:    main (root) or honeycomb/<parent> (child)
```

Children require a running parent; every dependency must be done. Preparation
starts from the target's committed tip, not uncommitted work. The current checkout
and target branch are left unchanged. No agent is launched; no proof or merge runs.

`HONEYCOMB_DIR` must sit directly inside the main repository checkout. It selects
the repository regardless of the caller's directory. Keep using that same absolute
path from task worktrees. Records resolve by ID, not filename; execution requires
both task and parent IDs to satisfy the `define` ID format.

Unknown or unready tasks, invalid graphs, missing target branches, and existing
task branches or workspace paths are rejected with exit code `2`, without writes.
Existing workspaces and branches are never reused or reset.

Preparation or record-write failure leaves the task `open`. Newly created resources
are rolled back when safe; cleanup never force-deletes a worktree. If cleanup fails,
the error requests inspection before retrying. Process termination can leave partial
preparation; automatic crash recovery and concurrent execution are not supported.

### Show or record proof

```sh
python3 honeycomb.py prove list-ready
python3 honeycomb.py prove list-ready --item 1 --result true
python3 honeycomb.py prove list-ready --item 1 --result false
python3 honeycomb.py prove list-ready --item 1 --result null
```

Run `prove <id>` **before verification**. It captures the task and target commits
in a tool-managed `proof_snapshot: {"task": "<commit>", "target": "<commit>"}`,
then displays every condition, instruction, and result with **1-based item numbers**.
The task workspace must be clean and on its task branch in the shared repository.
Staged, unstaged, and untracked changes prevent proof.

The current target commit must already be an ancestor of the task commit.
`prove` checks this with `git merge-base --is-ancestor`; it never merges.
If the target is missing, merge it into the task branch in the task workspace,
resolve conflicts and commit, then retry `prove` before verification.

Follow the verification instructions in the task workspace, then record results
with `--item` and `--result` together. Results are `null` (unproven), `true`
(passed), or `false` (failed). Every item must be true for proof to pass.

Every call rechecks the snapshot:

- Dirty task workspace or target not included: clear **all** results and the
  snapshot, then reject proof. No supplied result is recorded.
- Clean workspace with target included, but either commit changed or no snapshot:
  clear all results and capture a new snapshot. A supplied result is rejected;
  repeat verification before recording it.
- Same commits, clean workspace, and target included: show results or update only
  the selected item.
- An ancestry check returning anything other than `0` (included) or `1` (missing)
  is a Git error; stop without recording results.

Without flags, `prove` can therefore write to establish or invalidate a snapshot.
An unchanged snapshot causes no write. Record changes use atomic replacement.
Both forms require a running task with all children done and validate its entire
proof before output or writes. Unfinished children cause exit code `2` without
writes. Completed children permit parent proof; they do not supply it. Leaves
have no child-completion requirement. Neither form executes verification
instructions or changes task state.

The agent follows the instructions and records the observed outcome. Requested
human judgments happen in the existing conversation; the agent may relay an
answer but cannot grant someone else's approval. No answer leaves the result
`null`. Tooling trusts this relay; it does not authenticate the verifier or
establish that a supplied boolean is supported by evidence.

Exit codes for both forms:

- `0`: every proof item is true.
- `1`: proof is incomplete or failed; a supplied result was still stored.
- `2`: invalid input, Git/workspace, record, graph, or storage error, or a supplied
  result belongs to an outdated snapshot. No supplied result is recorded; stale
  results may have been cleared.

### Integrate a proven task

```sh
python3 honeycomb.py integrate list-ready
```

`integrate <id>` requires a running task, all children done, and every proof
result `true`. It rechecks the clean task workspace, exact task/target snapshot,
and target ancestry before moving Git. Missing or stale proof is rejected;
run `prove` and repeat verification before retrying.

The target is `main` for roots or `honeycomb/<parent>` for children. Integration
fast-forwards it to the exact proven task commit, then marks the task `done`.
No merge commit is created. Other record fields and other tasks stay unchanged.
Success is silent and exits `0`; errors exit `2`.

- If the target is checked out, its checkout must be clean with no unfinished
  Git operation. Integration updates that checkout without switching branches.
  It does not stash, overwrite ignored files, or run merge hooks. Branch-specific
  merge options are ignored to enforce the fast-forward operation.
- If the target is not checked out, integration updates its local ref using
  compare-and-swap. The caller's checkout is untouched.
- Integrations sharing a target wait on the same advisory lock in the repository's
  Git directory. After acquiring it, they reload records and recheck proof.
  Different targets have separate locks. Lock files persist; OS locks release
  when the process exits.

Rejected preconditions do not change task records or branches. A failed Git
operation may update Git bookkeeping such as `ORIG_HEAD`. If Git advances but
saving `done` fails, the task stays running; integration does not roll back the
branch. Inspect the target, run `prove`, repeat verification, then retry
`integrate`. A process interruption between the Git update and record update
requires the same recovery. Worktrees and task branches are retained.

### Compatibility

This is a breaking contract change:

- `define` replaces `add`; no alias remains.
- `execute` replaces `start`; no state-only alias remains.
- Previously running tasks are not assigned branches or worktrees retroactively.
- `open` replaces `pending`; stored `pending` states are rejected.
- `verification` is text, not a `run`/`review` object.
- `result` is `null`/`true`/`false`, not an exit-code or acceptance object.
- `prove --item N --result ...` replaces `--review N --accept|--reject`.
- Proof requires the task workspace prepared by `execute`. Run `prove <id>` before
  verification; unbound historical passes are cleared, not adopted.

Existing records are not rewritten and no migration command is provided.
Old proof shapes cannot be used with `prove`; scheduling still leaves proof
fields alone. Do not treat converting an old result as fresh verification.

### Limitations

The CLI only partially implements the target workflow in `WORKFLOW.md`.
`execute` prepares workspaces but does not launch agents. Agents prepare combined
changes and perform verification; `integrate` enforces the final fast-forward.
Readiness and child-completion gates trust recorded states, not Git history.

Proof binds committed task content to the target's committed tip, not uncommitted
work in the target checkout, ignored files, or external environment state. Changes
are detected on `prove` and `integrate`, not watched continuously. Proof requires
the target to be included but does not combine branches.

Only integration-versus-integration concurrency is coordinated. Do not run other
record writers or Git mutations concurrently with these commands. The integration
lock is advisory; external tools do not honor it. Git and record updates are not
one transaction. Exclusive creation prevents overwrites and atomic replacement
avoids partial records; automatic crash recovery is not implemented.

### Tests

```sh
python3 -m unittest discover -s tests -v
```
