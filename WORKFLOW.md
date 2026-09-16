# Honeycomb workflow

## Principles

- Speed means less time to a verified, accepted change—not more code.
- One workflow; effort scales with risk.
- Make the process predictable. Verify agent output.
- Stay stack-agnostic. Keep structure simple.

## Workflow

```text
Define → Execute → Prove → Integrate
```

Same workflow and commands at every depth:
`define`, `execute`, `prove`, `integrate`.

This is the target design, not the current CLI contract. Tooling is not yet
fully aligned; this document does not change implementation.

### 1. Define

Inspect the project. Record outcome, scope, and proof.
Resolve consequential unknowns or have them explicitly accepted.

The requester approves the overall task before execution. Agents may define
subtasks within its boundaries without separate approval.

One record shape for every task:

```yaml
id: C
parent: T
depends_on: [A, B]
outcome: "..."
scope: "..."
proof:
  - condition: "Invalid input leaves records unchanged"
    verification: "Run python3 -m unittest tests.test_rejection; require exit 0."
    result: null
  - condition: "Interaction feels right"
    verification: "Ask the requester to try the interaction and approve it."
    result: null
state: open
```

`define` stores the task as `open`, with proof results initialized to `null`.
`scope` states what may change and what must not.

### 2. Execute

```text
execute(task)
  require open
  require dependencies done
  require parent running, unless root
  prepare branch + worktree from target
  mark running
  launch owner
```

One agent owns each task:

```text
implement directly
OR
define children
execute children through this same workflow
wait until all children are done
```

Start with one task. Split only when parts can be proven and integrated
separately, and splitting enables parallel work or reduces risk—not merely
by file, layer, or agent count.

### 3. Prove

```text
prove(task)
  require running
  require all children done
  prepare combined change against current target
  follow each verification instruction
  record results
```

`verification` contains plain-language instructions, interpreted by the agent,
not automatically dispatched by type. There are no reserved verifier strings.

```text
null  → unproven
true  → passed
false → failed
```

Results must come from the specified check or person, not an agent's unsupported
claim. The agent may relay approval, never grant it on someone else's behalf.
Reviews happen in the existing conversation.

If required approval has no answer, the result stays `null`. Integration waits.

Completed children do not prove their parent. Every condition must be proven.
Conditions, verification instructions, and results stay together in `proof`;
no separate evidence field or report.

### 4. Integrate

```text
integrate(task)
  require running
  require every proof result true
  require change and target unchanged since proof
  merge exact proven change into target
  mark done
```

Target is the parent's branch; roots target `main`. Derive it from `parent`;
no separate merge-target field.

Integrate one task at a time per target. If the change or target moves, return
to **Prove**. Earlier results cannot authorize integration of a changed result.

## Hierarchy and dependencies

```text
main
└── T
    ├── A
    ├── B
    └── C  depends_on: [A, B]
```

```text
A and B execute in parallel
A and B prove and integrate into T
C executes from updated T
C proves and integrates into T
T proves the combined result and integrates into main
```

- `parent` is `null` or an existing task ID.
- Dependencies connect siblings only; roots count as siblings.
- Parent links and dependencies must be acyclic.
- Cross-branch dependencies belong between parents, not their internals.
- Scope conflicts require ordering; unclear independence means sequential execution.
- Store `parent`; derive children.
- Store `depends_on`; derive readiness and `blocks`.

No separate planning document or stored readiness state.

## State and responsibility

```text
open → running → done
```

Only integration marks a task done and unblocks dependents. Failed proof leaves
the task running, not in another state.

```text
Requester → approves intent and requested judgments
Agent     → implements, decomposes, follows verification instructions
Tooling   → enforces transitions and stores results
```

Agents request updates through tooling; they do not directly edit task state.

Store records once in `.honeycomb/tasks/` at the main checkout root.
Gitignore `.honeycomb/`; do not create worktree-local copies.
The launcher sets an absolute `HONEYCOMB_DIR` before dispatch; child agents
inherit it across worktrees. Tooling uses `$HONEYCOMB_DIR/tasks/`.

## Boundaries and retries

```text
Inside approved boundaries → proceed
Approved outcome, scope, or proof must change → request approval

Failed proof → Execute → Prove
Merge conflict → fix conflict → Prove
Required approval unanswered → wait
```

Fix merge conflicts while preserving the task's agreement, then prove the
combined change again. If the fix requires changing the agreement, request
approval.

Retries stay within the running task; they do not restart its lifecycle.
