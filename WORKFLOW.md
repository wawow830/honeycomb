# Honeycomb workflow

## Principles

- Speed means less time to a verified, accepted change—not more code.
- One workflow; effort scales with risk.
- Make the process predictable. Verify agent output.
- Developers own intent and acceptance; agents own execution.
- Stay stack-agnostic. Keep structure simple.

## Task

One record shape, whether split or not:

| Field | Meaning |
| --- | --- |
| `id` | Unique task ID. |
| `outcome` | What must be achieved? |
| `scope` | What may change—and what must not? |
| `proof` | Which checks and human judgments establish success? |
| `depends_on` | Direct prerequisite task IDs. |
| `subtasks` | Smaller tasks, only when split. |

## Workflow

```text
Define → Execute → Prove
           │
           ├─ unsplit: implement
           └─ split: run subtasks through this same workflow
```

One agent owns each task. Splitting changes execution, not the workflow.

**Delegate an outcome; receive a proven result.**
The owner handles its task's internals and returns the combined result to its parent.

### 1. Define

Inspect the project. Fill the task's outcome, scope, and proof.
Resolve consequential unknowns or have them explicitly accepted.

**The developer approves the overall task before execution.**
Subtasks need no individual approval.

### 2. Execute

Wait for dependencies, then do the work:

- **Unsplit:** the owner implements.
- **Split:** the owner coordinates subtasks, without duplicating their implementation.

Start with one task. Split only when each part can be proven and merged separately,
and splitting enables parallel work or reduces risk—not merely by file, layer,
or agent count.

Agents own decomposition and execution order within the overall task's boundaries:

```text
Inside approved boundaries → proceed.
Overall outcome, scope, or proof must change → stop and request approval.
```

#### Scheduling

Generate the DAG from task records. Store `depends_on`; derive `blocks`.
No separate planning document.

- Node: task. Edge `A → B`: B waits for A.
- Dependencies determine order; scope conflicts require choosing an order.
- Unclear independence means sequential execution.
- Tooling validates the graph, detects cycles, and selects ready tasks.

**Depend on complete results, not another task's internals.**

```text
T
├─ A
│  └─ A1
└─ B       depends_on: [A]
   └─ B1
```

If B1 needs A1, B waits for all of A. A1 stays inside A.
A returns its proven result to T; B starts from updated T.

```text
pending → running → done
```

`ready` is computed: pending with every dependency done.
Failed proof means unfinished—not another state.

Each owner controls only its direct subtasks' state. Workers return evidence,
not competing state. A subtask owner is its parent's worker and, when split,
its children's coordinator.

The parent uses two operations:

```text
start(task)
  require pending + dependencies done
  mark running
  prepare branch and worktree from current parent
  dispatch owner

finish(task, evidence)
  require running
  verify proof against current parent
  merge into parent
  mark done
```

Same rules at every depth.

Store task records once in `.honeycomb/tasks/` at the main checkout root.
Gitignore `.honeycomb/`; do not create worktree-local copies.

The launcher resolves the absolute path before dispatching agents:

```sh
export HONEYCOMB_DIR="$(pwd)/.honeycomb"
```

Run this from the main checkout root. Child agents inherit the variable,
including when launched in other worktrees. Task tooling uses
`$HONEYCOMB_DIR/tasks/` and enforces direct-parent state ownership.

Run ready tasks in parallel; isolate implementations in separate Git worktrees.

#### Branches

**One task, one branch.**

```text
main
└─ task
   ├─ subtask A
   └─ subtask B
```

Every task targets its parent's branch; the overall task targets `main`.
The hierarchy determines the merge target—no separate field.
Integrate one task at a time per parent branch.

### 3. Prove

Prove against the parent branch's current state, then merge into it.
Completing subtasks does not prove the parent task.

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

Developer acceptance belongs inside the overall task's proof. Present the behavior,
limitations, and evidence, with concrete examples or changes to review—not a generic
sign-off request.

Evidence stays in the task record. No separate report.

**Done = proof proven.**

The parent marks a task done after its proven change is merged into the parent's
branch. Dependents become ready from state; no separate release operation.
