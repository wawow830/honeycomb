---
name: define
description: Define or revise Honeycomb task agreements. Use when creating tasks, amending their outcome, scope, dependencies, or proof, or closing abandoned work.
---

# Define

Read [Honeycomb](../honeycomb/SKILL.md) for shared setup, boundaries, and
composition rules. This skill owns task agreements and their lifecycle changes.

## Task agreement

Before execution, inspect the project and agree on:

- **Outcome:** what must become true.
- **Scope:** what may change and what must not.
- **Proof:** conditions and how each will be checked.

Resolve consequential unknowns or have the requester explicitly accept them.
The requester approves the overall task. Subtasks within its boundaries need
no separate approval.

Use one record shape at every depth: `id`, `parent`, `depends_on`, `outcome`,
`scope`, and `proof`. Send exactly these six fields to `define`. IDs are 1–128
ASCII letters, digits, underscores, or hyphens, starting with a letter or digit.
Outcome, scope, condition, and verification must be nonblank. Proof must contain
at least one item with exactly `condition` and `verification`.

Tooling initializes `state: "open"` and each proof `result: null`. Do not supply
managed fields or edit task records directly. Use `amend` for explicit changes;
plans may evolve without silently changing the agreement or retaining stale proof.

## Create a task

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
Existing tasks are never overwritten. Continue with [Execute](../execute/SKILL.md).

## Amend a task

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
  human judgments, even if the code did not change. Follow [Prove](../prove/SKILL.md)
  to bind a fresh snapshot, then repeat all checks and requested judgments before
  integration.
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

## Close a task

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
