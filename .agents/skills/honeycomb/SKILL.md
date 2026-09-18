---
name: honeycomb
description: Coordinate structured agent-assisted development with Honeycomb. Use when asked to use Honeycomb or choose the next step in its task workflow.
---

# Honeycomb

Deliver verified, accepted changes.

**Define → Execute → Prove → Integrate**

## Steps

1. **Define:** agree on outcome, scope, and proof.
2. **Execute:** implement in a task workspace.
3. **Prove:** verify the combined result.
4. **Integrate:** land the exact verified revision.

Read the relevant skill before acting. Handle task bookkeeping yourself.

All commands use:

```sh
python3 .agents/skills/honeycomb/scripts/honeycomb.py <command>
```

Run inside the intended project or its worktree. `ready` lists eligible tasks without changing them.

## Rules

- Requester approves the task. Subtasks within its boundaries need no separate approval.
- Humans decide taste. Never grant approval for someone else.
- Changes to outcome, scope, or proof need approval. Dependency-only changes within scope do not.
- Never edit task records directly or bypass gates.
- Order conflicting scopes. If independence is unclear, work sequentially.
- Independent implementation may run concurrently. Coordinate bookkeeping and Git mutations; do not overlap them with CLI operations. Only integrations sharing a target are serialized.

**Task structure**
- Store `parent`; derive children.
- Parents must exist. New children cannot have a done or closed parent, or a closed ancestor.
- Dependencies must be unique existing siblings. Roots count as siblings.
- No parent or dependency cycles. Put cross-branch dependencies between parents.
- Success: `open → running → done`.
- Abandonment: `open` or `running → closed`.
- Only `done` satisfies dependencies.

**Setup**
- Requires Python 3.10+, Git, Unix locks, and a committed local `main`.
- Requires a non-bare main checkout with a `.git` directory.
- Version all five skills; ignore `/.honeycomb/`. Commit setup before execution without disturbing existing configuration or unrelated work.
- All worktrees share the main checkout’s task records and workspaces.

**Limits**
- The CLI trusts reported approvals and results. It does not authenticate evidence or control actions outside its gates.
- Proof covers commits, not ignored files or external state.
- No automatic launcher, verifier, or general crash recovery.
- Exit codes: `0` success, `2` error. Prove also uses `1` for incomplete or failed proof.

## Recovery

Never force-delete work or reset branches to pass a retry. If recovery is unclear, stop for inspection.
