---
name: define
description: Define or revise Honeycomb task agreements. Use when creating tasks, amending their outcome, scope, dependencies, or proof, or closing abandoned work.
---

# Define

Agree on what must become true, what may change, and how to verify it.

## Steps

### 1. Agree

Inspect the project. Establish:

- **Outcome:** what must become true.
- **Scope:** what may change—and what must not.
- **Proof:** conditions and their verification.

Resolve consequential unknowns or get explicit acceptance of them. Obtain task approval before execution.

### 2. Create

Run `define` with exactly these six fields on stdin:

```json
{
  "id": "example",
  "parent": null,
  "depends_on": [],
  "outcome": "Developers can list ready tasks.",
  "scope": "Read records only; no state changes.",
  "proof": [{
    "condition": "Only eligible tasks appear, sorted by ID.",
    "verification": "Compare output against expected IDs for eligible and blocked tasks."
  }]
}
```

Continue with **Execute**.

### Amend

Coordinate with the owner. Run `amend <id>` with a nonblank reason and changed fields:

```json
{
  "reason": "Replace an abandoned prerequisite.",
  "depends_on": ["replacement"]
}
```

Define replacement dependencies first. Review affected work and related tasks.

### Close

Stop the owner’s work, then run `close <id>`.

Closure abandons the task and unfinished descendants. It preserves all work and does not stop processes or revert code.

## Rules

**Creation**
- IDs: 1–128 ASCII letters, digits, `_`, or `-`; start with a letter or digit.
- Outcome, scope, condition, and verification must be nonblank.
- Include at least one proof item with exactly `condition` and `verification`.
- The CLI initializes state and results. Do not supply managed fields.
- Existing tasks are never overwritten. The CLI does not record approval.

**Amendment**
- Only open or running tasks without closed ancestors can change.
- Only `outcome`, `scope`, `depends_on`, and `proof` are editable.
- Omitted fields stay unchanged; lists replace previous lists. Do not supply proof results.
- Every amendment clears proof and its commit binding. Repeat all checks and human judgments.
- New unfinished dependencies pause affected work and block proof and integration.
- The previous record and reason are retained atomically, without nested history.
- Invalid or no-op amendments write nothing.
- Related tasks and Git work are not changed automatically.

**Closure**
- Done descendants stay done. Outside dependents remain blocked.
- Closed children stop blocking their parent; the parent’s requirements still apply.
- Closure is terminal. Replacement work needs a new task ID and agreement.
- Records, proof history, branches, worktrees, and dirty work remain.

## Recovery

Closing a done task is an error. Otherwise closure needs no readiness, clean workspace, or passing proof.

Closure is not atomic: the root closes first, blocking work below it. After interruption, repeat `close <id>`. Do not reopen tasks or edit records.
