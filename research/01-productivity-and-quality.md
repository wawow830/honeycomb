# Productivity and quality

Research date: 2026-09-14. This note distinguishes reported evidence from interpretation; it does not choose a workflow.

## 1. “Faster” has incompatible meanings in the literature

| Evidence | What was measured | What it does not establish |
|---|---|---|
| METR’s early-2025 randomized experiment: 19% longer with AI | Time to real task completion by experienced maintainers | Current agents make all developers slower. [S01](sources.md#s01) |
| Three company experiments: 26.08% more completed tasks | Estimated weekly task throughput among tool users | 26% less time per task, or autonomous-agent performance. [S03](sources.md#s03) |
| Enterprise case: 2.09× baseline throughput by April 2026 | Per-capita PR throughput during a broad rollout | Twice the customer value, unchanged long-term quality, or clean causal attribution. [S04](sources.md#s04) |
| Kernel experiment: 1.38× geometric-mean speedup | Execution speed of the resulting kernels | 38% less software-development effort. [S11](sources.md#s11) |

These results should not be averaged into a synthetic productivity number. They differ in denominator, treatment, task selection, tool generation, and study design.

The contemporary METR update is especially important: its point estimates suggest gains, but the researchers say selective participation and task submission make the magnitude unreliable. Developers who refuse to work without AI are increasingly missing from the experiment, as are tasks expected to benefit most. Concurrent agents also make per-task human-time attribution difficult. [S02](sources.md#s02)

**Interpretation:** the relevant question is not “does AI help?” in isolation. It is which work gets completed sooner, at what human and compute cost, under which acceptance standard.

## 2. Quality is not one variable

### Maintainability: meaningful counterevidence to blanket pessimism

In *Echoes of AI*, new developers were randomly assigned to evolve prior solutions. The study found no significant subsequent completion-time or code-quality disadvantage for AI-assisted code. That is evidence against assuming that provenance alone makes code harder to maintain. [S05](sources.md#s05)

It is not proof of equal quality: the application was small, work occurred in late 2024, the maintenance horizon was short, and security and large-scale architecture were not tested. The manuscript’s phase-one speed observations must not be mistaken for the phase-two randomized result.

### Understanding: a different possible cost

The Trio-learning experiment found a 17-percentage-point immediate quiz gap, without a significant time gain. The later student website experiment found better initial output accuracy with an editing agent but lower comprehension. [S06](sources.md#s06), [S07](sources.md#s07)

These findings do not contradict the maintainability study. One asks whether another developer can evolve an artifact; the others ask what its user understands or learns. Good code and weak author understanding can coexist.

Nor do the studies demonstrate that all professional agent users lose expertise. Their populations, interfaces, tasks, and short assessment horizons limit that conclusion. Interaction patterns such as auto-accepting edits were not randomly assigned; requiring a particular review ritual is not an experimentally proven remedy.

### Review: output can move the bottleneck

In the enterprise case, review load roughly doubled and automated review grew while merge/revert rates stayed stable. The authors explicitly warn that those rates miss defects, incidents, and maintainability. The throughput target itself may have changed PR behavior. [S04](sources.md#s04)

OpenAI’s own field report says increasing agent throughput made human QA a bottleneck, motivating agent-visible applications, logs, and metrics. That is a concrete mechanism report, not independent proof that automatic review preserves quality. [S13](sources.md#s13)

## 3. Taste must remain outside an agent’s authority

The brief reserves taste solely for humans. Research cannot replace that decision with an average preference or model score.

Anthropic’s design-loop report illustrates the distinction: scores generally rose, but the author sometimes preferred a middle iteration over the final one; complexity also increased. The evaluator influenced the aesthetic direction through its wording. [S12](sources.md#s12)

**Interpretation:** an agent can generate alternatives or report compliance with a human-approved constraint. That is different from choosing which tradeoff is tasteful, deciding the constraint, or declaring that higher automated scores override the human’s preference. The appropriate human interaction frequency remains open.

## 4. Measurement implications to test, not adopted requirements

A local evaluation could track these separately:

- **Elapsed time to acceptance:** includes waiting, integration, review, and rework—not just agent runtime.
- **Human attention:** active specification, steering, inspection, repair, and recovery time; avoid double-counting shared supervision across concurrent tasks.
- **Accepted scope:** distinguish intended work from unrequested features and PR-count inflation.
- **Technical quality:** failures, regressions, security findings, recovery effort, and a later change task—not only a green suite.
- **Human taste:** explicit acceptance/rejection and revision requests; never delegated to a model judge.
- **Cost:** tokens, infrastructure, repeated attempts, setup, and ongoing workflow maintenance.

These are proposed measurement dimensions motivated by the gaps above, not a validated universal metric. A single scalar could conceal a deterioration in one of the brief’s non-negotiable goals.

## What remains unknown

No reviewed study demonstrates exceptional speed **and** unchanged correctness, security, maintainability, comprehension, and human taste across general software development. There is positive evidence worth pursuing, but “without compromise” still needs project-specific meanings, observations, and failure criteria.
