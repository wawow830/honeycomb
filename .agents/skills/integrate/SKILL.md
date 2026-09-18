---
name: integrate
description: Integrate an exactly verified Honeycomb task into its target branch. Use when proof has passed and the change is ready to land, or when recovering an interrupted integration.
---

# Integrate

Land the exact verified revision.

## Steps

1. Complete **Prove**.
2. Run `integrate <id>`.

The CLI fast-forwards the target and marks the task done. Branches and worktrees remain.

## Rules

Integration requires:

- A running task.
- Done dependencies.
- Done or closed children.
- Every proof item passing.
- Clean workspaces.
- Unchanged proven commits.

Only integration completes a task and unblocks dependents.

## Recovery

**Target advanced:** merge it into the task workspace and repeat Prove.

**Git advanced but saving `done` failed:** inspect the target, establish fresh proof, repeat verification, then retry integration.

Never resolve conflicts by merging unproven work into the target.
