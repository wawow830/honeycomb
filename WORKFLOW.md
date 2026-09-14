# Honeycomb workflow

## Principles

- Speed means less time to a verified, accepted change—not more code.
- One workflow; effort scales with risk.
- Make the process predictable. Verify agent output.
- Developers own intent and acceptance; agents own execution.
- Stay stack-agnostic. Keep structure simple.

## Splitting work

Start with one change. Split only when:

- Each part can be proven and merged separately.
- Splitting enables parallel work or reduces risk.

Do not split merely by file, layer, or agent count.

## Change record

One record per change:

| Field | Meaning |
| --- | --- |
| `id` | Unique change ID. |
| `outcome` | What must change for the user? |
| `scope` | What may change—and what must not? |
| `proof` | Which checks and human judgments establish success? |
| `depends_on` | Direct prerequisite change IDs. |

Agents inspect the project to fill the record, not produce another document.
Consequential unknowns must be resolved or explicitly accepted.

**No implementation without an approved change record.**

## Execution boundary

One agent owns each change from approval to proof.

```text
Inside approved boundaries → proceed.
Outcome, scope, or proof must change → stop and request approval.
```

## Dependencies and parallelism

Generate the DAG from change records. No separate planning document.

- Node: approved change.
- Edge `A → B`: B waits for A.
- Dependencies determine order; scope conflicts require choosing an order.
- Unclear independence means sequential execution.

Store `depends_on`; derive `blocks`. Do not maintain both.
Tooling validates the graph, detects cycles, and selects ready nodes.

Run ready nodes in separate Git worktrees. Integrate one at a time,
proving each change against current `main` before merging.

## Progress

Only approved changes enter the execution DAG.

```text
pending → running → done
```

`ready` is computed: pending with every dependency done.
Failed proof means unfinished—not another state.

## Proof format

```yaml
proof:
  - run: "<verification command>"
    exit_code: null
  - review: "<acceptance criterion>"
    accepted: null
```

- Runner records `exit_code`; `0` passes.
- Developer records `accepted`; `true` passes.
- `null` means unproven.
- Every item must pass.

## Completion

**Done = proof proven.**

Developer acceptance belongs inside the agreed proof.
Evidence stays in the change record. No separate report.

Mark the node done after its proven change is merged. The scheduler releases
newly ready dependents; the completing agent does not edit other nodes.
