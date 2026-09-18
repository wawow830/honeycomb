---
name: execute
description: Execute an approved Honeycomb task in its isolated workspace. Use when starting implementation, decomposing work, or delegating tasks to agents.
---

# Execute

Follow [Honeycomb's shared rules](../honeycomb/SKILL.md).
Start with an approved task from [Define](../define/SKILL.md).

## Start

```sh
python3 .agents/skills/honeycomb/scripts/honeycomb.py execute example
```

The task must be open, its dependencies done, and its parent running, unless root.
The CLI creates `honeycomb/<id>` and a worktree from the target's committed tip,
marks the task running, and prints the absolute workspace path.

**Work in that workspace.** You own the task unless you delegate it.
Give a delegate the task ID, workspace, and Honeycomb skill.
Do not add a launcher or require multiple agents for this workflow.

## Build

Implement directly, or Define and Execute children through the same workflow.
Split only when parts can be verified and integrated separately **and** splitting
helps parallelism or reduces risk—not merely by file, layer, or agent count.

Finish or close all children, then continue with [Prove](../prove/SKILL.md).

## Recovery

Failed proof or merge conflict: fix in the running workspace, then repeat proof.
Do not execute the task again.

Preparation failures normally roll back new resources. Inspect partial state
left by interruptions; follow the shared recovery rules.
