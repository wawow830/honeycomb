---
name: execute
description: Execute an approved Honeycomb task in its isolated workspace. Use when starting implementation, decomposing work, or delegating tasks to agents.
---

# Execute

Implement an approved task in its workspace.

## Steps

1. Run `execute <id>`.
2. Work in the printed workspace.
3. Implement directly, or define and execute children. Show consequential design choices early; align with the requester before hardening them.
4. Test throughout implementation. Finish or close every child, then continue with **Prove** for final verification.

You own the task unless you delegate it. Give delegates the task ID, workspace, and Honeycomb skill.

## Rules

- The task must be open, dependencies done, and its parent running unless root.
- Execution creates `honeycomb/<id>` and a worktree from the target’s committed tip.
- Split only when parts can be verified and integrated separately, and splitting improves parallelism or reduces risk.
- Do not split merely by file, layer, or agent count.
- No launcher or multiple agents are required.

## Recovery

Fix failed proof or merge conflicts in the running workspace. Do not execute again.

Preparation failures normally roll back new resources. Inspect partial state after interruptions.
