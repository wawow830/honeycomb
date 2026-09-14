# Structure and coordination

Research date: 2026-09-14. These are competing mechanisms and evidence, not prescribed stages or agent roles.

## 1. Context files: what information is being added?

Two contemporary evaluations appear contradictory:

- A controlled study of repository context files found no statistically significant general success improvement, while generated files increased inference costs roughly 20–23%. Agents followed instructions, doing more testing and exploration, but did not find relevant files faster. Human-written files outperformed generated ones. [S08](sources.md#s08)
- Vercel’s version-matched Next.js documentation index achieved 100% on its reported suite, compared with 53% without documentation and 79% with explicitly prompted skills. Unprompted skills frequently went unused. [S09](sources.md#s09)

They test different interventions. A summary of discoverable repository information is not the same as access to missing, version-specific API knowledge. The former study has broader controlled task coverage but is Python-only; the latter addresses a narrower knowledge gap and publishes less experimental detail.

**Hypothesis, not established reconciliation:** benefit depends on whether the material supplies necessary information or merely repeats existing information/adds obligations. Test task commands, constraints, documentation pointers, and generated overviews separately rather than treating the filename as the intervention.

The repository study also cannot establish that extra testing was worthless simply because benchmark success did not improve. Its endpoint does not cover every nonfunctional requirement.

## 2. Specifications and durable state: multiple viable approaches

### OpenAI: environment and repository as the shared working context

The harness report describes a short context index, deeper versioned documentation, execution plans, per-worktree applications, inspectable telemetry, and mechanically enforced architecture boundaries. Early progress was constrained by an underspecified environment, not only model capability. [S13](sources.md#s13)

This demonstrates feasibility in a greenfield, heavily supported project. It does not validate the exact folder hierarchy, layered architecture, optional human review, or estimated 10× acceleration for other teams.

### Anthropic: explicit handoffs, then removal of scaffolding

A planner/generator/evaluator harness used files for communication and negotiated testable sprint contracts. Browser QA caught actual broken interactions, including display-only features. [S12](sources.md#s12)

However, the headline comparison spent $200 and six hours versus $9 and twenty minutes, and produced different scopes. It does not isolate the value of role separation from extra time, tokens, specification detail, or scope expansion.

As models improved, the author removed context resets and sprint decomposition. For tasks within the generator’s reliable range, an evaluator could become overhead; at harder boundaries it still caught omissions.

**Interpretation:** a structured process need not have a permanently fixed number of stages. Both the addition and removal of structure require evidence. Simplicity cannot be inferred just from fewer agents, nor quality from more artifacts.

### StrongDM: specifications and external scenarios, no human code review

StrongDM reports non-interactive development driven by specifications, external holdout scenarios, feedback loops, and behavioral replicas of services. Humans do not write or review code in its stated operating model. [S19](sources.md#s19)

This is an important alternative to assuming humans must approve every patch. But the pages provide no controlled defect/productivity comparison, and faithful service replicas plus independent scenario evaluation are substantial engineering investments. The advocated token expenditure is not evidence of efficiency. A model’s “satisfaction” estimate also cannot inherit authority over human taste.

**Open issue:** how little specification is sufficient without permitting agents to silently invent product intent? The reports demonstrate strategies, not a universal answer.

## 3. Agent count is not the causal mechanism

Google Research compared 180 agent configurations: coordination helped parallelizable financial reasoning and hurt strictly sequential planning. Those are not coding tasks, so the effect sizes are not coding-workflow predictions. They nevertheless provide controlled evidence that communication and fragmented context can consume useful reasoning budget. [S10](sources.md#s10)

Cursor/NVIDIA supplies a coding-specific positive case: a planner redistributed kernel optimization work across workers, with benchmark feedback and anti-cheating checks. Results were measurable and code was published. But the comparison also changes implementation languages and search resources; it does not establish that multiple agents beat a compute-matched single agent. [S11](sources.md#s11)

**Questions suggested by the evidence:**

- Can subtasks genuinely proceed independently, or do they require continually renegotiated interfaces?
- Does parallelism reduce elapsed time while increasing total cost or integration failures?
- Is a reviewer finding new defects, or echoing the generator’s assumptions?
- Is the limiting resource search capacity, feedback latency, environment access, or human decisions?

These are more diagnostic than choosing “one agent” or “a team of agents” upfront.

## 4. Human involvement: competing models remain open

| Model to investigate | Potential advantage | Unresolved cost/risk |
|---|---|---|
| Continuous human steering | Early clarification and correction | Interruptions, attention demand, superficial approval |
| Human decisions at selected boundaries | Less interruption; deliberate judgment | Bad boundary selection; work proceeds on wrong assumptions |
| Human intent/taste with autonomous implementation and validation | Long uninterrupted execution | Weak specifications/verifiers, latent defects, reduced understanding |

The table is an analytical comparison, not a set of proven outcomes. The field reports support feasibility of different models; comprehension experiments and approval telemetry expose reasons that human presence alone is insufficient. [S06–S07](sources.md#s06), [S18](sources.md#s18)

Nothing here resolves the user’s undecided approval policy. Taste remains human-controlled under every candidate.

## 5. Stack independence: portable questions, unproven universal machinery

The evidence spans Python repositories, a Java application, Next.js, full-stack browser apps, and CUDA kernels. That is diversity, not validation of one portable workflow.

A possible distinction is a stack-independent description of intent, permissions, observations, and acceptance, with stack-specific build/test/runtime mechanisms. This is a **design hypothesis** derived from the reports, not an established standard. No framework or repository layout is selected by this review.
