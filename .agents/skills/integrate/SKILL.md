---
name: integrate
description: Integrate an exactly verified Honeycomb task into its target branch. Use when proof has passed and the change is ready to land, or when recovering an interrupted integration.
---

# Integrate

Read [Honeycomb](../honeycomb/SKILL.md) for shared setup, boundaries, and
composition rules. Complete [Prove](../prove/SKILL.md) before integration.

## Integrate the verified revision

```sh
python3 .agents/skills/honeycomb/scripts/honeycomb.py integrate example
```

Requires a running task, all dependencies done, all children done or closed,
all proof items true, clean workspaces, and unchanged proven commits.
Fast-forwards the target to the exact proven task commit, then marks the task
done. Roots target `main`; children target their parent's branch. Only integration
completes a task and unblocks dependents. Branches and worktrees are retained.

Do not bypass failed gates by editing records or manually moving the target.
If the target advanced, combine it into the task branch and repeat
[Prove](../prove/SKILL.md). Resolve conflicts in the task workspace, never by
merging unproven work into the target.

## Interrupted integration

If integration advanced Git but could not save `done`, inspect the target,
establish fresh proof, repeat verification, then retry integration. Never
force-delete work or reset branches to make a retry pass. Stop for inspection
when recovery is unclear.
