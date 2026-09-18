---
name: execute
description: Execute an approved Honeycomb task in its isolated workspace. Use when starting implementation, decomposing work, or delegating tasks to agents.
---

# Execute

Read [Honeycomb](../honeycomb/SKILL.md) for shared setup, boundaries, and
composition rules. Start with an approved task from [Define](../define/SKILL.md).

## Prepare the workspace

```sh
python3 .agents/skills/honeycomb/scripts/honeycomb.py execute example
```

Requires an open task, completed dependencies, and a running parent unless root.
Creates branch `honeycomb/<id>` and a worktree from the target's committed tip,
marks the task running, and prints the absolute worktree path.

**Continue work in that workspace.** The command does not launch an agent.
The current agent owns the task unless explicitly delegated using available
agent tools. Give a delegated owner the task ID, workspace, and the
[Honeycomb](../honeycomb/SKILL.md) entry skill.
Do not add a launcher or require multiple agents just to follow this workflow.

## Implement or decompose

Implement directly, or use [Define](../define/SKILL.md) to create children and
execute them through this same loop. Split only when parts can be proven and
integrated separately and splitting allows useful parallelism or reduces risk—not
merely by file, layer, or agent count. Parent completion waits for all children
to be done or closed.

When implementation is ready, continue with [Prove](../prove/SKILL.md).
Failed proof or a merge conflict means fix within the running task, then repeat
proof—not execute the task again.

## Preparation failures

Preparation failures normally roll back new resources safely. Interruptions can
leave partial state. Never force-delete work or reset branches to make a retry
pass. Stop for inspection when recovery is unclear.
