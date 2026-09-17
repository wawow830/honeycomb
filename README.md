# Honeycomb

Project-local agent workflow: **Define → Execute → Prove → Integrate**.

Goals: faster verified, accepted changes without sacrificing quality or taste;
explicit boundaries and structure; stack independence; simplicity.

## Install in a project

Copy this repository's `.agents/skills/honeycomb/` directory into the same
location in your project:

```text
.agents/skills/honeycomb/    # versioned, self-contained skill
├── SKILL.md                # agent instructions and workflow rules
└── scripts/
    └── honeycomb.py        # deterministic operations
.honeycomb/                # ignored, local runtime state
```

Add `/.honeycomb/` to the project's `.gitignore`. Commit the skill and ignore rule
to the branch used as the execution target before starting tasks. Existing
project files and unrelated work should be preserved.

Requires Python 3.10+ and Git; no third-party Python packages. Execution requires
a local `main` branch with at least one commit. Integration requires Unix
advisory locks (`fcntl.flock`). The main checkout must have its Git directory
at `.git`; separate Git directories and bare-main repositories are not supported.

Open the project in an agent that discovers `.agents/skills/`, and ask it to use
Honeycomb for your request. The agent reads the skill, aligns the task with you,
and handles the CLI. No global installation, agent-specific adapter, or manual
environment setup is needed. Agents without that discovery convention must be
explicitly directed to `SKILL.md`; Honeycomb does not install integrations for them.

**[SKILL.md](.agents/skills/honeycomb/SKILL.md) is the workflow rulebook**, including
approval, task decomposition, verification, and recovery instructions.

## CLI reference

From the project checkout root:

```sh
python3 .agents/skills/honeycomb/scripts/honeycomb.py --help
```

The caller's current directory selects the repository. Git's worktree listing
identifies its main checkout, even when invoked from a linked worktree or nested
subdirectory. Shared records live at `<main-checkout>/.honeycomb/tasks/` and
workspaces at `<main-checkout>/.honeycomb/worktrees/`. Script location does not
select the project. No worktree-local state is created.

All commands validate stored task IDs, states, hierarchy, sibling dependencies,
and cycles before operating. `define` reads one JSON object on stdin; other
commands take arguments. All errors exit 2. Success exits 0, except that `prove`
exits 1 for incomplete or failed proof.

### `define`

The [skill](.agents/skills/honeycomb/SKILL.md#1-define) gives the input shape and
an invocation example. Exactly six input fields are required: `id`, `outcome`,
`scope`, `parent`, `depends_on`, and `proof`.

Creates `tasks/<id>.json`, initializing `state: "open"` and proof results to
`null`. Success is silent. IDs must match `[A-Za-z0-9][A-Za-z0-9_-]{0,127}`.
Outcome, scope, conditions, and verification instructions must be nonblank;
proof must be nonempty. Each input proof item has exactly `condition` and
`verification`. Managed fields cannot be supplied.

Duplicate JSON keys, invalid JSON constants, invalid input or stored graphs,
duplicate IDs, and existing destination files are rejected without changing
records. Exclusive creation prevents overwrites. Storage is created on demand.
Approval is not authenticated or enforced by this command.

### `ready`

Prints sorted IDs of open tasks with all dependencies done and a running parent
(unless root). A fresh project with no task storage, or no ready tasks, succeeds
with empty output. Does not write. Invalid records produce no partial output.

Scheduling validates `id`, `state`, `parent`, and `depends_on`, not proof. Stored
IDs must be unique nonempty strings without whitespace. Missing `parent` is
accepted as a legacy root. Every command checks hierarchy and dependency graphs.

### `execute <id>`

Checks readiness, creates branch `honeycomb/<id>` and its worktree, then marks
the task running. Prints the absolute workspace path. Task and parent IDs must
satisfy the `define` ID format. Target is `main` for a root or
`honeycomb/<parent>` for a child.

Starts from the target's committed tip, not uncommitted work. Existing branches
or workspace paths are rejected, never reused or reset. Current checkout,
target branch, unrelated records, and other record fields remain unchanged.
No agent is launched and no proof or merge runs.

Preparation or record-write failure leaves the task open. Newly created
resources are rolled back when safe; cleanup never force-deletes a worktree.
Cleanup failure requests inspection. Process termination can leave partial
preparation; automatic crash recovery is not implemented.

### `prove <id> [--item N --result true|false|null]`

Both flags must be present together. Requires a running task, all children done,
valid proof, and its prepared workspace. Item numbers are 1-based. Without flags,
prints numbered conditions, instructions, and results; it may also establish or
invalidate a proof snapshot.

The workspace must belong to the shared repository, be on the task branch, and
have no staged, unstaged, or untracked changes. The current target must be an
ancestor of the task commit. The CLI checks ancestry but does not combine branches.

A tool-managed `proof_snapshot: {"task": "<commit>", "target": "<commit>"}` binds
results to exact commits:

- Dirty task workspace or target not included: clear all results and the
  snapshot, then reject. No supplied result is recorded.
- Clean, target included, but either commit changed or no snapshot: clear all
  results and capture a new snapshot. A supplied result is rejected; repeat
  verification before recording it.
- Same commits, clean workspace, target included: display or update one result.
- An ancestry check returning anything other than 0 or 1 is a Git error; stop
  without recording results.

Unfinished children or invalid proof are rejected without writes. With an
unchanged snapshot, displaying results causes no write. Updates use atomic
replacement. Verification instructions are plain language: neither form runs
checks or changes task state.

Exit 0 means every item is true. Exit 1 means incomplete or failed; an individual
supplied result was still stored. Exit 2 means invalid input, Git/workspace,
record, graph, storage, or outdated supplied result. No supplied result is
recorded on exit 2, though stale results may have been cleared.

### `integrate <id>`

Requires a running task, all children done, all results true, the exact current
proof snapshot, a clean task workspace, and target ancestry. Fast-forwards the
target to the proven task commit, then marks the task done. Success is silent.
Other fields and records remain unchanged. Branches and worktrees are retained.

- If checked out, the target workspace must be clean and have no unfinished Git
  operation. Integration updates it without switching branches, stashing,
  overwriting ignored files, or running merge hooks. Branch merge options are
  ignored to enforce fast-forwarding.
- If not checked out, the target ref is updated with compare-and-swap; the caller's
  checkout is untouched.
- Integrations sharing a target wait on an advisory lock in the shared Git
  directory, then reload records and recheck proof. Different targets have
  independent locks. Lock files persist; OS locks release when the process exits.

Rejected preconditions leave branches and records unchanged. A failed Git
operation may update bookkeeping such as `ORIG_HEAD`. Git and records are not
one transaction: if Git advances but saving `done` fails or is interrupted, the
task remains running. Inspect the target, run `prove`, repeat verification, and
retry integration. Integration does not roll back an advanced branch.

## Limits

- The skill guides agent behavior; it cannot prevent bypassing the CLI.
- `execute` prepares workspaces, not agents. `prove` binds and records results,
  not their evidence. The CLI trusts the agent's relay of checks and approvals.
- Readiness and child-completion gates trust recorded states, not Git history.
- Proof binds committed content, not ignored files, uncommitted target work, or
  external environment state. Changes are detected on commands, not continuously.
- Only integration-versus-integration concurrency is coordinated. Other record
  writers and Git mutations must not run concurrently with CLI operations.
  External tools do not honor Honeycomb's advisory locks.
- No amendment, migration, cleanup, or automatic crash-recovery command exists.

## Compatibility

The executable moved from `honeycomb.py` to the skill's `scripts/honeycomb.py`;
there is no root-level wrapper. `HONEYCOMB_DIR` is no longer used. Run commands
inside the intended repository. Every command now requires Git for discovery.
Existing `.honeycomb/tasks/` records at the main checkout remain in place and
are not rewritten by packaging.

Earlier contracts remain unsupported: `add`/`start` aliases, `pending` state,
`run`/`review` verification objects, and non-boolean proof results. Legacy
running tasks are not assigned workspaces retroactively. Unbound historical
passes are cleared, never adopted as fresh proof.

## Development

```sh
python3 -m unittest discover -s tests -v
```

Tests cover transition gates, Git safety, shared-state discovery, and the copied
skill's full CLI lifecycle. They do not establish that an agent reliably follows
the instructions or that every host discovers the skill.

`research/` contains dated evidence and design investigations, not additional
workflow rules.
