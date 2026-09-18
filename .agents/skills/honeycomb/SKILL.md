---
name: honeycomb
description: Structure agent-assisted software work as approved tasks with explicit scope, verification, and guarded Git integration. Use when asked to use Honeycomb or to define, execute, prove, or integrate Honeycomb tasks in this project.
---

# Honeycomb

Speed means less time to a verified, accepted change—not more code.
Use one workflow at every depth; scale effort with risk, not ceremony.

```text
Define → Execute → Prove → Integrate
```

You handle task bookkeeping through the bundled CLI. The requester should not
need to operate it. Instructions guide your behavior; the CLI enforces its
own gates, not everything an agent can do outside it.

## Setup and location

Requires Python 3.10+ and Git. Execution needs a local `main` branch with at least
one commit; integration needs Unix advisory locks (`fcntl.flock`). The repository
must have a non-bare main checkout with its Git directory at `.git`.
Separate Git directories and bare-main repositories are not supported.

The skill lives at `.agents/skills/honeycomb/`. Version the whole skill directory
and add `/.honeycomb/` to the project's `.gitignore`. Commit this setup before
execution so new task worktrees include the skill. Do not overwrite existing
project configuration or commit unrelated work.

Resolve `scripts/honeycomb.py` relative to this file. Run it with Python from
inside the intended project or one of its worktrees. Examples below assume the
checkout root:

```sh
python3 .agents/skills/honeycomb/scripts/honeycomb.py ready
```

The **current working directory** selects the repository, not the script's
location. Git identifies its main checkout. All worktrees share that checkout's
`.honeycomb/tasks/` and `.honeycomb/worktrees/`; no environment variables or
worktree-local copies are needed. `define` creates storage. `ready` on a fresh
project succeeds with no output and creates nothing.

## Task agreement

Before execution, inspect the project and agree on:

- **Outcome:** what must become true.
- **Scope:** what may change and what must not.
- **Proof:** conditions and how each will be checked.

Resolve consequential unknowns or have the requester explicitly accept them.
The requester approves the overall task. Subtasks within its boundaries need
no separate approval. Humans decide taste; agents can propose and implement.

Use one record shape at every depth: `id`, `parent`, `depends_on`, `outcome`,
`scope`, and `proof`. Send exactly these six fields to `define`. IDs are 1–128
ASCII letters, digits, underscores, or hyphens, starting with a letter or digit.
Outcome, scope, condition, and verification must be nonblank. Proof must contain
at least one item with exactly `condition` and `verification`.

Tooling initializes `state: "open"` and each proof `result: null`. Do not supply
managed fields or edit task records directly. Use `amend` for explicit changes;
plans may evolve without silently changing the agreement or retaining stale proof.

## 1. Define

Use a task-specific agreement, not this example unchanged:

```sh
python3 .agents/skills/honeycomb/scripts/honeycomb.py define <<'JSON'
{
  "id": "example",
  "parent": null,
  "depends_on": [],
  "outcome": "Developers can list ready tasks.",
  "scope": "Read records only; no dispatch or state changes.",
  "proof": [
    {
      "condition": "Only eligible tasks are listed, in stable order.",
      "verification": "Exercise eligible and blocked tasks; compare output to the expected sorted IDs."
    }
  ]
}
JSON
```

`define` stores the agreement; it does not obtain or authenticate approval.
Existing tasks are never overwritten.

## 2. Execute

```sh
python3 .agents/skills/honeycomb/scripts/honeycomb.py execute example
```

Requires an open task, completed dependencies, and a running parent unless root.
Creates branch `honeycomb/<id>` and a worktree from the target's committed tip,
marks the task running, and prints the absolute worktree path.

**Continue work in that workspace.** The command does not launch an agent.
The current agent owns the task unless explicitly delegated using available
agent tools. Give a delegated owner the task ID, workspace, and this skill.
Do not add a launcher or require multiple agents just to follow this workflow.

Implement directly, or define children and execute them through this same loop.
Split only when parts can be proven and integrated separately and splitting
allows useful parallelism or reduces risk—not merely by file, layer, or agent
count. Parent completion waits for all children to be done or closed.

## 3. Prove

Wait for all dependencies to be done, finish or explicitly close all children,
commit the task's changes, and include the current target commit in the task
branch. Resolve any conflicts in the task workspace, not by merging unproven
work into the target.

```sh
python3 .agents/skills/honeycomb/scripts/honeycomb.py prove example
```

Run this **before verification**. It binds proof to the clean task and target
commits and displays numbered conditions, instructions, and results. If the
target is not included, merge it into the task branch, resolve and commit, then
run `prove` again. Root target: `refs/heads/main`; child target:
`refs/heads/honeycomb/<parent>`.

Perform every specified check in the task workspace. Verification is plain
language interpreted by you; the CLI does not run checks. Check the claimed
behavior, not a convenient substitute.

Record each observed outcome using its displayed 1-based item number:

```sh
python3 .agents/skills/honeycomb/scripts/honeycomb.py prove example --item 1 --result true
```

- `null`: unproven or unanswered.
- `true`: the specified check passed or the specified person approved.
- `false`: failed or rejected.

Never record `true` merely because implementation is finished. For a human
judgment, ask in the existing conversation and wait for the actual answer.
You may relay approval, never grant it on another person's behalf.

Children's passes do not prove the parent. Verify the combined outcome against
all of the parent's conditions. Dirty work or changed task/target commits
invalidate prior results. Re-establish the snapshot and repeat verification;
do not restore old booleans without repeating their checks or judgments.

`prove` exits **0** when all items pass, **1** when incomplete or failed, and
**2** for errors or an outdated supplied result. Exit 1 is normal while collecting
proof; it does not mean that recording an individual result failed.

## 4. Integrate

```sh
python3 .agents/skills/honeycomb/scripts/honeycomb.py integrate example
```

Requires a running task, all dependencies done, all children done or closed,
all proof items true, clean workspaces, and unchanged proven commits.
Fast-forwards the target to the exact proven task commit, then marks the task
done. Roots target `main`; children
target their parent's branch. Only integration completes a task and unblocks
dependents. Branches and worktrees are retained.

Do not bypass failed gates by editing records or manually moving the target.
If the target advanced, combine it into the task branch and repeat proof.

## Amending a task

Use `amend` to revise an open or running task without replacing its identity or
workspace. Obtain requester approval before changing outcome, scope, or proof.
Dependency-only changes within the approved boundaries need no new approval.
The CLI records the amendment; it does not obtain or authenticate approval.

Send a nonblank `reason` and one or more of `outcome`, `scope`, `depends_on`, and
`proof`. Omitted fields stay unchanged. Lists are replaced in full; proof items
use the same `condition` and `verification` shape as `define`, without results.

For example, after defining a replacement prerequisite with the same parent:

```sh
python3 .agents/skills/honeycomb/scripts/honeycomb.py amend example <<'JSON'
{
  "reason": "The original prerequisite was abandoned; use its replacement.",
  "depends_on": ["replacement"]
}
JSON
```

- IDs, parents, states, and other managed fields cannot be amended. Done and
  closed tasks, and tasks beneath a closed ancestor, cannot be amended.
- Dependencies must still be unique existing siblings and must not form a cycle.
  Only `done` satisfies a dependency; referencing a closed task leaves work blocked.
- Every amendment clears **all** proof results and the commit binding, including
  human judgments, even if the code did not change. Run `prove` to bind a fresh
  snapshot, then repeat all checks and requested judgments before integration.
- The task's `amendments` list retains each reason and the entire preceding record
  under `previous`, excluding that record's amendment history to avoid nesting.
  Old proof is historical only; it never authorizes current integration.
- Record changes and history are written atomically. Invalid input and amendments
  that change nothing are rejected without writes.

Coordinate with the task owner before amending. If a running task gains an
unfinished dependency, pause affected work until that dependency is done;
`prove` and `integrate` refuse while it remains unfinished. Incorporate the
current target before fresh proof as usual. Amendment does not merge or undo
code, stop agents, or alter children or dependents. Review existing work and
child plans against the revised agreement; amend or close them explicitly if needed.
Branches, workspaces, and dirty work are preserved. Do not amend concurrently
with other record writers or Git mutations.

## Closing a task

When a task is no longer worth pursuing within the approved scope:

```sh
python3 .agents/skills/honeycomb/scripts/honeycomb.py close example
```

`close` marks an open or running task and all its unfinished descendants
`closed`. Completed descendants remain `done`. Dependents outside the subtree
are untouched and remain blocked: only `done` satisfies a dependency. Use
`amend` to redirect an active dependent to a replacement prerequisite if needed.

Closed tasks are terminal: no execution, proof, integration, new children, or
ID reuse. A replacement needs a new task and agreement. Repeating `close` is
safe and finishes any interrupted subtree closure; closing a done task is an
error. Closure does not require readiness, clean workspaces, or passing proof.

A closed child no longer blocks its parent's proof or integration, but the
parent must still meet its original outcome, scope, and proof. Closing a failed
approach is not permission to drop a requirement; request approval for a scope
change. Retained proof results are history, not successful completion.

Closure changes only task states. Records, proof snapshots and results,
branches, worktrees, and uncommitted changes are preserved. It neither reverts
already-integrated work nor stops agents or processes; coordinate stopping any
owner before closing its task. Do not run closure concurrently with other
record writers or Git mutations.

Subtree writes are not atomic as a group. The root is closed first, blocking
execution, proof, integration, and new children throughout its subtree even if
later writes fail or the command is interrupted. Retry `close` with the same
ID to finish; do not edit records or reopen tasks to recover.

## Composition and responsibility

- Store `parent`; derive children. Parents must exist and cannot be done or
  closed when adding children; no ancestor may be closed. Parent links must be
  acyclic.
- Dependencies are unique existing siblings; roots count as siblings.
  Dependencies must be acyclic. Cross-branch dependencies belong between parents,
  not their internals.
- Scope conflicts require ordering. Unclear independence means sequential work.
- Success is `open → running → done`. Either `open` or `running` can instead
  become terminal `closed`. Failed proof leaves the task running.
- Requester approves intent and requested judgments; agent implements,
  decomposes, and verifies; tooling enforces transitions and stores results.

## Boundaries and recovery

Inside approved boundaries, proceed. If outcome, scope, or proof must change,
request approval, then record the change with `amend`. Never silently edit the
agreement or bypass its gates. Dependency-only plan changes within the approved
boundaries may be amended without new approval.

Failed proof or a merge conflict means fix within the running task, then repeat
proof—not execute the task again. Required approval without an answer means wait.

Only integrations sharing a target are serialized. Do not run other record
writers or Git mutations concurrently with CLI operations. Implementation in
independent worktrees may proceed in parallel; coordinate bookkeeping and merges.

Preparation failures normally roll back new resources safely. Interruptions can
leave partial state. If integration advanced Git but could not save `done`,
inspect the target, establish fresh proof, repeat verification, then retry
integration. Never force-delete work or reset branches to make a retry pass.
Stop for inspection when recovery is unclear.

The CLI trusts recorded results; it does not authenticate reviewers or establish
that a boolean has evidence. Proof covers committed content, not ignored files
or external environment state. There is no automatic agent launcher, verifier,
general crash recovery, or enforcement outside the CLI. All commands other than
`prove` exit 0 on success and 2 on error.
