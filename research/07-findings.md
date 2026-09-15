# Cross-case findings: what is applicable, and under what conditions?

These are conclusions from [the inspected cases](README.md), **not an adopted workflow**. Confidence refers to the particular mechanism, not a promise of universal productivity gains.

**September 15 supplement:** [Project harnesses and pstack](08-project-harness-and-pstack.md) adds maintained real-surface drivers, feature maps, and prototype-led design to the mechanisms below. Artifact inspection also found an intentionally omitted example driver and a plan validator that passes an unfilled skeleton. These reinforce the distinction between a specified check, an executable check, and proof of behavior. The original findings below retain their September 14 framing; the supplement separately compares them with the subsequent Honeycomb workflow.

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

This is not a recommendation to add every possible check. It is a way to identify when a cheap check is answering the wrong question.

## 2. Fast feedback depends on making the right state reachable

Ghostty’s simulator exposed update cancellation/error states without waiting for real releases. Moebius used reference tensors for numerical comparisons, but still needed browser execution. The compiler experiment became more parallelizable when a known-good implementation helped isolate failing file subsets. [Ghostty](05-human-judgment-and-rejection.md), [Moebius](02-browser-port.md), [compiler](03-parallel-compiler.md)

**Interpretation:** a test command is not enough if the agent cannot reproduce the relevant state, distinguish implementation errors from environment failures, or extract a useful failure. The reusable idea is observability of the task’s actual behavior; the fixture, simulator, service, device, or reference implementation remains project-specific.

**Boundary:** these sources demonstrate the artifacts or report the intervention, not a controlled estimate of time saved by each one.

## 3. Autonomy and integration ownership are separate choices

Stripe reports unattended implementation followed by human scrutiny. Hashimoto interleaved agents with manual code changes and design decisions. Willison used little code inspection for a browser experiment but substantial review for a database release. GRDB’s rejected PR shows that submitting generated code does not transfer responsibility for finishing it to the maintainer. [Stripe](04-unattended-maintenance.md), [human decisions](05-human-judgment-and-rejection.md), [sqlite-utils](01-release-hardening.md)

There is no evidence here for one universal human-involvement boundary. The cases do show why “a human was in the loop” is too vague: specifying intent, judging UI, checking a diff, debugging platform behavior, reviewing compatibility, and authorizing publication are different contributions.

**Fixed by the brief:** taste is solely human. An agent may supply alternatives or implement a chosen direction; it does not acquire authority to choose what is tasteful. Ghostty is particularly relevant because the human discovered the preferred design through prototypes rather than fully specifying it upfront.

## 4. More agents help only if there is useful concurrent work

The compiler’s agents stalled on the same blocking defect until the verifier changed. Stripe’s parallelism is largely separate tasks in separate environments. Moebius was a separate project pursued while another agent worked on Datasette—not a team coordinating on one patch.

These are three different kinds of concurrency. None establishes that an elaborate multi-agent organization beats one agent on an ordinary feature at equal cost.

**Applicable question:** what can actually finish independently, and what will still have to be reconciled? A role name or separate context window does not make shared-state work independent.

## 5. Simplicity can come from better representation, not fewer safeguards

Hashimoto reports replacing a confused state representation before asking agents to continue. Stripe reports reusing existing developer environments, rules, and tooling rather than creating separate agent equivalents; guidance and tool access are scoped to relevant work. [Ghostty](05-human-judgment-and-rejection.md), [Stripe](04-unattended-maintenance.md)

**Interpretation:** remove ambiguity and duplicated sources of truth before adding more instructions to compensate for them. This is a plausible mechanism supported by these accounts, **not** a measured general advantage of a particular file format, state representation, or framework.

Conversely, the compiler’s published README confidently describes missing integration tests. More documentation is not intrinsically more reliable context.

## 6. Determinism is useful at specific boundaries

The cases support a narrower, actionable vocabulary:

- **Control:** required operations are scheduled by code rather than left to an agent’s discretion, as Stripe reports for linting and Git operations.
- **Comparison:** same inputs, fixtures, dependencies, or test subsets make changes easier to evaluate.
- **Authority:** a run can be restricted to an isolated environment rather than relying solely on instructions or permission fatigue.
- **Provenance:** pinned revisions and exact checks let someone inspect what was actually evaluated.

None implies identical model output or identical full runs. A deterministic test can consistently approve the wrong behavior; sqlite-utils supplies a concrete example. A scheduled command can fail. A networked tool can return changing data.

The brief’s goal should not be diluted to “everything follows a template.” Templates describe structure; they do not by themselves enforce execution, authority, or correctness.

## 7. The speed claim is still not established

The cases make useful work and credible acceleration mechanisms visible. They do **not** quantify end-to-end speed without compromised quality:

- PR counts omit unsuccessful attempts and the value/size of tasks.
- Token bills omit human work, subscription effects, and infrastructure.
- Merged code does not establish low long-term defect or maintenance cost.
- A demo can succeed through changed requirements and intensive repair.
- Parallel sessions make elapsed runtime different from human effort.

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

For any speed comparison, keep accepted scope and quality constraints explicit, count abandoned work and repairs, and observe a subsequent change where feasible. A small local comparison cannot prove “no compromise”; it can expose a bad assumption before it becomes a permanent workflow rule.

**What remains open for alignment:** which quality guarantees and authority boundaries the eventual workflow must enforce; which decisions may remain adaptive; and what evidence would justify adding each piece of structure. No stages, tools, agent count, or approval policy have been selected.
