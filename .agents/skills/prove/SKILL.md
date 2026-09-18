---
name: prove
description: Verify a Honeycomb task against its agreed proof conditions and record observed results. Use when checking completed work, collecting human judgments, or repeating verification after changes.
---

# Prove

Follow [Honeycomb's shared rules](../honeycomb/SKILL.md).

## 1. Prepare

Wait for dependencies to be done and children to be done or closed.
Commit the task's changes and include the current target commit in its branch:

- Root target: `refs/heads/main`.
- Child target: `refs/heads/honeycomb/<parent>`.

Merge and resolve conflicts in the task workspace—not the target.

## 2. Bind, then verify

Run **before verification** to bind proof to clean task and target commits:

```sh
python3 .agents/skills/honeycomb/scripts/honeycomb.py prove example
```

Perform every displayed check in the task workspace. The CLI displays instructions;
it does not execute them. Check the claimed behavior, not a substitute.
Verify the combined outcome: children's passes do not prove their parent.
For human judgments, ask in the conversation and wait for the answer.

## 3. Record

Record each observed result by its displayed 1-based item number:

```sh
python3 .agents/skills/honeycomb/scripts/honeycomb.py prove example --item 1 --result true
```

Use `true` for passed or approved, `false` for failed or rejected, and `null` for
unproven or unanswered. Implementation being finished is not a pass.
When all conditions pass, continue with [Integrate](../integrate/SKILL.md).

## Retry and exit codes

Dirty work or changed task/target commits invalidate all results, including human
judgments. Commit changes, include the current target, bind again, and repeat
verification. Never restore old booleans without repeating checks and judgments.

Exit codes: **0** all passed; **1** incomplete or failed; **2** error or stale result.
Exit 1 while collecting proof is normal; it does not mean recording failed.
For failed checks, follow [Execute's recovery guidance](../execute/SKILL.md#recovery).
