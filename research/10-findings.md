# Cross-case findings: what is applicable, and under what conditions?

**Updated September 15, 2026.** These conclusions synthesize [the inspected cases](README.md), [project harnesses and pstack](08-project-harness-and-pstack.md), and [code sloppiness and measurement](09-code-sloppiness-and-measurement.md). They are research findings, **not changes to the adopted [Honeycomb workflow](../WORKFLOW.md)**. Confidence refers to the particular mechanism, not a promise of universal productivity gains.

The strongest synthesis is: **make important behavior cheap to exercise and hard to misreport; resolve consequential uncertainty before scaling execution; judge structural quality across changes, not only at a passing checkpoint.** Local reproductions, inspected artifacts, practitioner recommendations, and reported benchmark results support different parts of that conclusion and are distinguished below.

## 1. Check the claimed behavior, not a convenient substitute

**Strong, locally reproduced instance:** sqlite-utils’ old test asserted that a rejected query raised an exception. It passed even though the database changed. The repaired tests checked state preservation and visibility from another connection. A further probe still found an exception to the broad documented guarantee. [Case](01-release-hardening.md)

**Independent instance:** curl’s invalid report crashed substitute code that did not use the alleged vulnerable library. The later valid report exercised actual curl paths and led to a credited fix. [Cases](05-human-judgment-and-rejection.md)

**Applicable distinction:**

| Claimed result | Insufficient substitute | More directly relevant observation |
|---|---|---|
| “The write persists” | Same-connection read | A new connection/process sees it |
| “Rejected input has no effect” | Expected exception | State before and after rejection |
| “The application works in the target browser” | Typecheck, Node test, HTTP 200 | Execute the interaction in that browser |
| “This library has a reachable defect” | Crash in a simplified replacement | Reproducer reaching the actual library path |
| “The change is ready” | Agent’s completion summary | Final diff, relevant checks, accepted behavior |
| “The plan is executable” | Required headings and evidence-path syntax | Resolved steps, valid dependencies, available checks |
| “The code remains maintainable” | Passing behavioral tests or a low complexity score | Structural review and evidence from subsequent changes |

**Additional locally checked boundary:** pstack’s plan validator accepted its own unfilled skeleton. That proves a limit of the structural validator, not that its operational workflow accepts unfinished plans. The linked Atlas example intentionally omits its driver: it demonstrates documentation, not executable verification. [Artifact inspection and probe](08-project-harness-and-pstack.md)

Keep **a specified check, an implemented check, a recorded execution, and evidence establishing the claimed outcome** distinct. None automatically implies the next.

This is not a recommendation to add every possible check. It is a way to identify when a cheap check is answering the wrong question.

## 2. Fast feedback depends on making the right state reachable

Ghostty’s simulator exposed update cancellation/error states without waiting for real releases. Moebius used reference tensors for numerical comparisons, but still needed browser execution. The compiler experiment became more parallelizable when a known-good implementation helped isolate failing file subsets. [Ghostty](05-human-judgment-and-rejection.md), [Moebius](02-browser-port.md), [compiler](03-parallel-compiler.md)

**Interpretation:** a test command is not enough if the agent cannot reproduce the relevant state, distinguish implementation errors from environment failures, or extract a useful failure. The reusable idea is observability of the task’s actual behavior; the fixture, simulator, service, device, or reference implementation remains project-specific.

**Practical extension:** pstack proposes a maintained real-application driver paired with a scoped feature map: how to reach a capability, prerequisites, actions, and observable effects. Its inspected creation skill requires checking the build and instance, isolating runtime state, exercising a mapped feature end to end, and cleaning up without deleting evidence. Semet recommends a canonical command interface shared by humans, agents, and CI. These are concrete infrastructure proposals, not proof that the published examples provide a complete working harness. [Harness research](08-project-harness-and-pstack.md)

Maintenance must distinguish documentation drift, harness gaps, and product regressions. Updating instructions to hide broken behavior would destroy the feedback loop. Worktrees alone do not isolate ports, profiles, services, or data; cloud placement alone does not make verification valid.

**Boundary:** these sources demonstrate artifacts, prescribe checks, or report interventions, not a controlled estimate of time saved by each one. Stack-independent principles still require project-specific drivers and fixtures.

## 3. Autonomy and integration ownership are separate choices

Stripe reports unattended implementation followed by human scrutiny. Hashimoto interleaved agents with manual code changes and design decisions. Willison used little code inspection for a browser experiment but substantial review for a database release. GRDB’s rejected PR shows that submitting generated code does not transfer responsibility for finishing it to the maintainer. [Stripe](04-unattended-maintenance.md), [human decisions](05-human-judgment-and-rejection.md), [sqlite-utils](01-release-hardening.md)

There is no evidence here for one universal human-involvement boundary. The cases do show why “a human was in the loop” is too vague: specifying intent, judging UI, checking a diff, debugging platform behavior, reviewing compatibility, and authorizing publication are different contributions.

**Fixed by the brief:** taste is solely human. An agent may supply alternatives or implement a chosen direction; it does not acquire authority to choose what is tasteful. Ghostty is particularly relevant because the human discovered the preferred design through prototypes rather than fully specifying it upfront.

## 4. More agents help only if there is useful concurrent work

The compiler’s agents stalled on the same blocking defect until the verifier changed. Stripe’s parallelism is largely separate tasks in separate environments. Moebius was a separate project pursued while another agent worked on Datasette—not a team coordinating on one patch.

These are three different kinds of concurrency. None establishes that an elaborate multi-agent organization beats one agent on an ordinary feature at equal cost.

**Applicable question:** what can actually finish independently, and what will still have to be reconciled? A role name or separate context window does not make shared-state work independent.

pstack’s inspected maintenance skill permits parallel read-only inspection but gives one coordinator ownership of live driving—a useful distinction between independent analysis and shared runtime state. Its separate planning playbook mandates ten lanes; that is an opinionated policy, not comparative evidence for an optimal agent count. Reported PR volumes do not resolve the question. [Inspection](08-project-harness-and-pstack.md)

## 5. Simplicity can come from better representation, not fewer safeguards

Hashimoto reports replacing a confused state representation before asking agents to continue. Stripe reports reusing existing developer environments, rules, and tooling rather than creating separate agent equivalents; guidance and tool access are scoped to relevant work. [Ghostty](05-human-judgment-and-rejection.md), [Stripe](04-unattended-maintenance.md)

**Interpretation:** remove ambiguity and duplicated sources of truth before adding more instructions to compensate for them. This is a plausible mechanism supported by these accounts, **not** a measured general advantage of a particular file format, state representation, or framework.

Semet’s short guidance index and shared commands, and pstack’s behavior-oriented feature map, extend this idea: make relevant knowledge and checks discoverable without duplicating every source of truth. Executable architectural rules can produce actionable failures where the constraint is mechanically expressible. Their setup and maintenance costs still matter. [Harness research](08-project-harness-and-pstack.md)

Conversely, the compiler’s published README confidently describes missing integration tests, and Atlas documents a driver it explicitly does not ship. More documentation is not intrinsically more reliable context. These sources do not establish an ideal guidance length, launcher, or document count.

## 6. Determinism is useful at specific boundaries

The cases support a narrower, actionable vocabulary:

- **Control:** required operations are scheduled by code rather than left to an agent’s discretion, as Stripe reports for linting and Git operations.
- **Comparison:** same inputs, fixtures, dependencies, or test subsets make changes easier to evaluate.
- **Authority:** a run can be restricted to an isolated environment rather than relying solely on instructions or permission fatigue.
- **Provenance:** pinned revisions and exact checks let someone inspect what was actually evaluated.

None implies identical model output or identical full runs. A deterministic test can consistently approve the wrong behavior; sqlite-utils supplies a concrete example. A scheduled command can fail. A networked tool can return changing data.

The brief’s goal should not be diluted to “everything follows a template.” Templates describe structure; they do not by themselves enforce execution, authority, or correctness. The pstack validator probe makes this boundary concrete. Likewise, plain Markdown guidance is not a computational gate, and a model-based review remains inferential even when scheduled deterministically. [Harness research](08-project-harness-and-pstack.md)

## 7. Passing behavior and preserving structure are distinct outcomes

**Reported longitudinal evidence:** SlopCodeBench v1 carries each implementation forward through changing requirements. On its Python track, erosion increased in 80% of trajectories and verbosity in 89.8%. No run passed every checkpoint and regression test for a complete problem; individual checkpoints did pass. The paper reports that anti-slop and plan-first prompts improved some starting implementations without preventing similar subsequent degradation slopes. These results were read, **not rerun locally**. [Article, paper, and limits](09-code-sloppiness-and-measurement.md)

The mechanism worth retaining is accumulated design cost: an implementation can meet today’s external contract while making tomorrow’s extension harder. That complements Ghostty’s representation redesign and qualifies any claim that passing tests alone establishes quality.

**Applicable distinction:** LOC, duplication, verbosity, and complexity concentration can direct attention; they cannot certify maintainability or taste. SlopCodeBench’s measures depend on chosen rules and thresholds, and its maintained-human repository panel is not a matched human solution baseline. The reported score differences do not establish a causal production maintenance cost. Optimizing a proxy directly can reward compressed intent or missing safeguards.

Where structural quality matters, identify a concrete review target and an owner: for example, whether the new capability fits the intended module boundaries without duplicating policy. Observe a subsequent change where feasible. Human judgment retains authority over taste; metrics and agent reviews supply evidence or questions, not acceptance. The linked judge-bias study adds evidence of prompt/order sensitivity, not a verdict that all AI review is useless.

## 8. Resolve uncertainty with evidence, not only more specification

Ghostty’s preferred UI emerged through prototypes and human decisions. pstack Part 2 proposes restating intent, separating current behavior from historical rationale, sketching the caller’s experience, and comparing throwaway implementations before prescribing detailed execution. Its inspected prototype playbook keeps decision experiments separate from production source. [Ghostty](05-human-judgment-and-rejection.md), [pstack](08-project-harness-and-pstack.md)

**Interpretation:** distinguish uncertainty about the desired outcome, the existing system, and the feasibility of an approach. A restatement can expose misunderstood intent; source and history can explain constraints; a bounded prototype can reveal behavior or design tradeoffs. A larger plan does not substitute for any of these observations.

**Boundary:** prototypes consume time and may discover changed requirements rather than accelerate fixed-scope delivery. Not every task needs competing architectures, multiple documents, or a prototype. The sources do not justify importing pstack’s fixed lane counts or opt-in human design checkpoint into Honeycomb. Experiments remain within approved scope; the human chooses matters of taste.

## 9. The speed claim is still not established

The cases make useful work and credible acceleration mechanisms visible. They do **not** quantify end-to-end speed without compromised quality:

- PR counts omit unsuccessful attempts and the value/size of tasks.
- Token bills omit human work, subscription effects, and infrastructure.
- Merged code does not establish low long-term defect or maintenance cost.
- A demo can succeed through changed requirements and intensive repair.
- Parallel sessions make elapsed runtime different from human effort.
- A working harness has setup, coverage, and maintenance costs; reported output multipliers do not account for them.
- A passing checkpoint or improved static score does not establish preserved quality across later changes.

This is why two METR reports remain relevant as methodological checks, rather than the centerpiece of this rewrite. The early-2025 randomized study found a 19% slowdown in its experienced-maintainer setting despite perceived acceleration. Its February 2026 follow-up reports evidence suggestive of gains but says participation/task selection and concurrent-agent accounting make the magnitude unreliable. Neither settles contemporary productivity for software developers generally. [Sources](sources.md#productivity-check)

## What would discriminate between candidate practices?

These are optional investigations motivated by unresolved claims, not steps imposed on every task:

| Unresolved claim | Informative comparison |
|---|---|
| Different-model review is especially valuable | Same implementation, equal review budget, same-model versus different-model review; compare confirmed findings and false alarms |
| Extra agent roles reduce delivery time | Comparable independent/coupled tasks, controlled total resources; include integration and human attention |
| More specification prevents waste | Compare additional specification with early executable prototypes; account for requirements discovered through the prototype |
| More autonomous retries are worth it | Record whether successive attempts add confirmed progress or repeat failure, including compute and review cost |
| A new verifier improves quality | Run it on pre-fix or deliberately incorrect implementations as well as accepted ones |
| A maintained harness pays for itself | Compare repeated equivalent verification tasks; include setup, drift repair, wrong-instance errors, and missed regressions |
| A structural metric predicts maintainability | Fix measurement conventions; compare score trajectories with later change effort, regressions, and human review on comparable work |
| Anti-slop instructions preserve quality | Compare sequences of changes, not only initial snapshots; include correctness, structural review, and total cost |

For any speed comparison, keep accepted scope and quality constraints explicit, count abandoned work and repairs, and observe a subsequent change where feasible. A small local comparison cannot prove “no compromise”; it can expose a bad assumption before it becomes a permanent workflow rule.

## Relationship to the current workflow

Honeycomb now specifies Define → Execute → Prove → Integrate, overall task approval, scoped ownership, recorded proof, and integration of the exact proven change. This synthesis does not reopen those decisions or claim the implementation already enforces the target design.

**What remains to establish:** which project-specific checks and runtime isolation make proof meaningful; which structural judgments a task requires; when harness maintenance or prototyping repays its cost; and whether the resulting process improves accepted delivery time across subsequent changes. The research supports investigating these questions, not adding mandatory stages, fixed agent counts, universal metric thresholds, or another framework.
