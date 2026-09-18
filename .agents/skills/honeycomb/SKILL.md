---
name: honeycomb
description: Coordinate structured agent-assisted development with Honeycomb. Use when asked to use Honeycomb or choose the next step in its task workflow.
---

# Honeycomb

Deliver verified, accepted changes. Scale effort with risk, not ceremony.

| Step | Purpose |
| --- | --- |
| [Define](../define/SKILL.md) | Agree on outcome, scope, and proof. |
| [Execute](../execute/SKILL.md) | Implement or delegate in a task workspace. |
| [Prove](../prove/SKILL.md) | Verify the combined result. |
| [Integrate](../integrate/SKILL.md) | Land the exact verified revision. |

Read the relevant skill before acting. Handle the CLI yourself; the requester
should not need to operate it.

## Shared rules

- Requester approves the task; subtasks within it need no separate approval.
  Humans decide taste. Never grant approval on someone else's behalf.
- Get approval to change outcome, scope, or proof; record it with Define.
  Dependency-only changes within scope need no approval. Wait for required answers.
- Never edit task records directly or bypass gates.
- Order conflicting scopes. Unclear independence means sequential work.
- Independent implementation may run in parallel; coordinate bookkeeping and Git
  mutations. Do not run these concurrently with CLI operations. The CLI serializes
  only integrations sharing a target.
- Never force-delete work or reset branches to pass a retry. If recovery is unclear,
  stop for inspection.

## Task structure

- Same workflow at every depth. Store `parent`; derive children.
- New children need an existing parent that is neither done nor closed.
  No ancestor may be closed.
- Dependencies are unique existing siblings; roots count as siblings.
  Cross-branch dependencies belong between parents. No parent or dependency cycles.
- Success: `open → running → done`. Abandon: `open` or `running → closed`.
  Failed proof stays running. Only `done` satisfies dependencies.

## Setup and commands

Requires Python 3.10+, Git, Unix locks, and a committed local `main`.
Use a non-bare main checkout with a `.git` directory—not a separate Git directory.

Version all five skills under `.agents/skills/`; ignore `/.honeycomb/`.
Commit setup before execution. Preserve existing configuration and unrelated work.

The CLI is `scripts/honeycomb.py` relative to this skill. Examples run from the
checkout root; run inside the intended project or its worktree:

```sh
python3 .agents/skills/honeycomb/scripts/honeycomb.py ready
```

The working directory selects the repository. All worktrees share the main
checkout's `.honeycomb/tasks/` and `.honeycomb/worktrees/`; no local copies or
environment variables are needed. `define` creates storage. On a fresh project,
`ready` succeeds without output or writes.

## Limits

The CLI trusts reported approvals and results; it does not authenticate evidence
or control actions outside its gates. Proof covers commits, not ignored files or
external state. There is no automatic launcher, verifier, or general crash recovery.

Exit codes: 0 success, 2 error. Prove also returns 1 for incomplete or failed proof.
