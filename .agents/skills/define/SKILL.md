---
name: define
description: Define or revise Honeycomb task agreements. Use when creating tasks, amending their outcome, scope, dependencies, or proof, or closing abandoned work.
---

# Define

Follow [Honeycomb's shared rules](../honeycomb/SKILL.md).

## Agree

Inspect the project, then agree on:

- **Outcome:** what must become true.
- **Scope:** what may change and what must not.
- **Proof:** conditions and how each will be checked.

Resolve consequential unknowns or have the requester explicitly accept them.
Get overall task approval before execution. The CLI records agreements, not approval.

## Create

Send exactly these six fields, using a task-specific agreement:

```sh
python3 .agents/skills/honeycomb/scripts/honeycomb.py define <<'JSON'
{
  "id": "example",
  "parent": null,
  "depends_on": [],
  "outcome": "Developers can list ready tasks.",
  "scope": "Read records only; no dispatch or state changes.",
  "proof": [
    {
      "condition": "Only eligible tasks appear, sorted by ID.",
      "verification": "Exercise eligible and blocked tasks; compare the output with expected IDs."
    }
  ]
}
JSON
```

IDs: 1–128 ASCII letters, digits, `_` or `-`, starting with a letter or digit.
Outcome, scope, condition, and verification must be nonblank. Include at least
one proof item, with exactly `condition` and `verification`.

The CLI sets `state: "open"` and proof results to `null`; do not supply managed
fields. Existing tasks are never overwritten. Continue with [Execute](../execute/SKILL.md).

## Amend an agreement

Coordinate with the owner; follow the shared approval rules.
Send a nonblank `reason` and changes to `outcome`, `scope`, `depends_on`, or `proof`.
Omitted fields stay unchanged. Lists replace previous lists. Proof has no results.

```sh
python3 .agents/skills/honeycomb/scripts/honeycomb.py amend example <<'JSON'
{
  "reason": "The original prerequisite was abandoned; use its replacement.",
  "depends_on": ["replacement"]
}
JSON
```

Define the replacement sibling first.

- Amend only open or running tasks without a closed ancestor.
- IDs, parents, and managed fields cannot change. Invalid or no-op edits write nothing.
- **Every amendment clears proof and its commit binding**, even without code changes.
  Bind again with
  [Prove](../prove/SKILL.md); repeat all checks and human judgments.
- New unfinished dependencies pause affected work and block proof and integration.
- Work is preserved; `amendments` retains the reason and previous record atomically,
  without nested history. Historical proof cannot authorize integration.

Amendment does not merge, undo, stop agents, or update related tasks.
Review existing work and related tasks; amend or close those tasks separately if needed.

## Close abandoned work

Coordinate stopping its owner first:

```sh
python3 .agents/skills/honeycomb/scripts/honeycomb.py close example
```

- Closes the task and unfinished descendants. Done descendants stay done;
  outside dependents stay blocked. Amend dependents if needed.
- Closed children no longer block the parent. Its requirements still apply.
- Preserves records, proof history, branches, worktrees, and dirty work.
  Does not revert code or stop processes.
- Closure is terminal: no execution, proof, integration, new children, or ID reuse.
  Replacement work needs a new task and agreement.

### Closure recovery

Closing done tasks is an error. Otherwise closure needs no readiness, clean work,
or passing proof, and repeating it is safe.

Subtree closure is not atomic. The root closes first, blocking execution, proof,
integration, and new children below it. After interruption, repeat `close` with
the same ID. Do not edit records or reopen tasks.
