# Open questions and possible experiments

Research date: 2026-09-14. **No workflow is adopted here.** These are questions for alignment after research and candidate ways to obtain missing evidence.

## Decisions research cannot make for the human

1. **What counts as accepted quality?** Existing tests, operational behavior, security, compatibility, comprehensibility, and maintainability may impose different constraints. What would count as an unacceptable regression?
2. **What kind of speed matters most?** Elapsed delivery time, human effort, throughput, or cost-adjusted throughput? Which costs may increase to gain speed?
3. **Which determinism matters?** Stable procedure and authority, comparable environments, reproducible acceptance, or identical generated artifacts?
4. **How should human taste be expressed and revisited?** References, alternatives, direct edits, critique, or explicit decisions? Sole human authority is fixed; the interaction mechanism is not.
5. **Where else should human decisions be required?** Intent changes, architecture, implementation, review, risky operations, or release? No answer has been assumed.
6. **What is the minimum useful structure?** Which records prevent repeated mistakes, and which merely consume attention and context?

## Competing hypotheses worth testing

| Question | Compare | Observe |
|---|---|---|
| Does context help? | No added file; concise necessary constraints/docs; generated repository overview | Acceptance, missed requirements, retrieval failures, token/attention costs. Motivated by [S08–S09](sources.md#s08). |
| How much planning pays? | Direct execution; short explicit acceptance statement; more detailed spec | Misinterpretations, unrequested scope, rework, total elapsed time. Motivated by [S12–S13](sources.md#s12). |
| When do multiple agents help? | One agent; parallel independent work; coordinated roles | Accepted results, integration defects, elapsed time, compute, human effort. Motivated by [S10–S12](sources.md#s10). |
| Does extra review improve outcomes? | Same implementation with different validation/review approaches | Defects found and missed, false alarms, repair burden, taste acceptance, reviewer understanding. Motivated by [S04](sources.md#s04), [S07](sources.md#s07), [S16](sources.md#s16). |
| Which scaffolding remains necessary? | Remove one component at a time after a model/harness change | Lost capabilities versus reduced overhead. Motivated by [S12](sources.md#s12). |
| Do gains survive maintenance? | Follow-up change by another developer, then longer observation | Change effort, regressions, understanding, recovery cost—not just original delivery. Motivated by [S05–S07](sources.md#s05). |

These are proposed comparisons, not an implementation backlog or a requirement to run every experiment.

## Conditions for informative comparisons

- Choose representative work before seeing which method succeeds. Include bugs, features, refactors, integration work, and both familiar and unfamiliar areas as relevant.
- Agree intended scope and quality constraints before comparing outputs; do not let extra features masquerade as greater productivity.
- Distinguish **equal compute** comparisons from **equal elapsed-time** comparisons. Both can be useful, but they answer different questions.
- Record human effort, failed/abandoned attempts, setup cost, and follow-up rework. Handle overlapping supervision explicitly.
- Control versions and resources; repeat runs where stochastic variation could reverse a conclusion. Report uncertainty and failure distributions, not only the best example.
- Avoid repeatedly solving the same task with the same developer without accounting for learning effects. Randomization or matched tasks can help, but a small local study still has limited statistical power.
- Keep taste judgment with the human. If preferences evolve, record the change rather than retroactively treating all earlier outputs as failures under an unchanged specification.
- Do not convert “no observed defects” into “no quality compromise.” Longer-term and uncommon failures require different evidence.

These conditions are synthesis from the reviewed methodological limitations, especially [S02](sources.md#s02), [S04–S05](sources.md#s04), and [S14–S17](sources.md#s14), rather than a validated evaluation protocol.

## Evidence gaps to keep visible

- Compute-matched, real-repository comparisons of single versus multiple agents.
- Human approval-policy experiments measuring both attention and escaped defects.
- Long-term maintenance and human-understanding outcomes with current autonomous agents.
- Validation across substantially different stacks, team sizes, legacy systems, and operational risk.
- Requirements discovery, release safety, incident response, and ongoing production ownership—not just implementation.
- Reproducible end-to-end agent runs under hosted-model changes.
- Proof that automated evaluators preserve quality outside the behavior they explicitly check.

**Next alignment point:** decide what the goal means operationally and which uncertainties matter most before selecting stages, artifacts, tools, or agent roles.
