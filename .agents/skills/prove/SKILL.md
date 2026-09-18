---
name: prove
description: Verify a Honeycomb task against its agreed proof conditions and record observed results. Use when checking completed work, collecting human judgments, or repeating verification after changes.
---

# Prove

Read [Honeycomb](../honeycomb/SKILL.md) for shared setup, boundaries, and
composition rules.

## Bind the revision

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

## Verify and record

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

Failed proof leaves the task running: fix within that workspace and repeat
proof. When all conditions pass, continue with [Integrate](../integrate/SKILL.md).
