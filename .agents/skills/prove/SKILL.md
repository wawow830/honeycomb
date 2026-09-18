---
name: prove
description: Verify a Honeycomb task against its agreed proof conditions and record observed results. Use when checking completed work, collecting human judgments, or repeating verification after changes.
---

# Prove

Verify the combined result against the agreement.

## Steps

1. Finish dependencies and finish or close children.
2. Commit changes and include the current target commit:
   - Root: `refs/heads/main`.
   - Child: `refs/heads/honeycomb/<parent>`.
3. Run `prove <id>` **before verification**.
4. Perform every displayed check in the task workspace.
5. Record each observed result:

```text
prove <id> --item <number> --result true|false|null
```

When every condition passes, continue with **Integrate**.

## Rules

- Resolve merges in the task workspace, never the target.
- The CLI binds proof to clean task and target commits; it does not execute checks.
- Check the claimed behavior, not a substitute.
- Children’s passes do not prove the parent.
- Ask for required human judgments and wait for answers.
- `true` means passed or approved; `false` means failed or rejected; `null` means unanswered or unproven.
- Finished implementation is not proof.

## Recovery

Dirty work or changed task/target commits invalidate every result, including human judgments.

Commit, include the current target, bind again, and repeat verification. Never restore old results without repeating their checks.

Exit codes: `0` all passed, `1` incomplete or failed, `2` error or stale result. Exit `1` does not mean recording failed.
