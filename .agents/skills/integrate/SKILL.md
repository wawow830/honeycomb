---
name: integrate
description: Integrate an exactly verified Honeycomb task into its target branch. Use when proof has passed and the change is ready to land, or when recovering an interrupted integration.
---

# Integrate

Follow [Honeycomb's shared rules](../honeycomb/SKILL.md).
Complete [Prove](../prove/SKILL.md) first.

## Land the change

```sh
python3 .agents/skills/honeycomb/scripts/honeycomb.py integrate example
```

Requires a running task, done dependencies, done or closed children, all proof
items true, clean workspaces, and unchanged proven commits.

The CLI fast-forwards the target to the exact proven commit, then marks the task
done. Only integration completes work and unblocks dependents.
Branches and worktrees remain.

## Recovery

If the target advanced, merge it into the task workspace and repeat Prove.
Never merge unproven work into the target to resolve conflicts.

If Git advanced but saving `done` failed, inspect the target, establish fresh
proof, repeat verification, and retry integration. Follow the shared recovery rules.
