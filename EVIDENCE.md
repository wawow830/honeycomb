# Evidence, limits, and design choices

Sources checked on **2026-09-12**. This is a targeted primary-source review, not a systematic meta-analysis. Findings from different tasks, populations, tools, and outcome definitions cannot be averaged into a universal “AI speedup.”

## Research findings

### 1. AI can make experienced developers slower—even when they feel faster

**Source:** METR, [Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/), July 2025.

- Randomized AI allowance across 246 real tasks from 16 experienced contributors to mature repositories.
- AI-allowed tasks took **19% longer** on average. Participants subsequently believed AI had made them about **20% faster**.
- **Limit:** a particular experienced-maintainer setting and early-2025 tools. The authors explicitly reject generalizing to all developers, other settings, or future systems.
- **Design consequence:** record actual completion, review, and repair time; do not use perceived speed as the outcome. Equally, do not declare AI universally harmful.

### 2. The later METR evidence does not justify freezing the 2025 verdict

**Source:** METR, [Updated Results from Our Developer Productivity Study](https://metr.org/blog/2026-02-24-uplift-update/), February 2026.

- Later data suggest more favorable effects, but the researchers call the estimate unreliable: participant/task selection changed, compensation changed, and concurrent agents made time accounting difficult.
- Reported raw estimates have uncertainty intervals spanning no effect; the authors regard the data as very weak evidence for the size of the change.
- **Design consequence:** test current tools locally, preserve all eligible attempts, and distinguish wall-clock time from overlapping human/agent work. Neither the old negative result nor the newer suggestive result is a universal current effect size.

### 3. Randomized field experiments also show positive implementation effects

**Source:** Cui et al., [The Effects of Generative AI on High-Skilled Work: Evidence from Three Field Experiments with Software Developers](https://economics.mit.edu/sites/default/files/inline-files/draft_copilot_experiments.pdf); [authors' Microsoft Research page](https://www.microsoft.com/en-us/research/publication/the-effects-of-generative-ai-on-high-skilled-work-evidence-from-three-field-experiments-with-software-developers/).

- Three randomized field experiments at Microsoft, Accenture, and an anonymous Fortune 100 company; 4,867 developers.
- The combined preferred estimate is **26.08% more completed tasks** (SE 10.3 percentage points). The main task measure is completed **pull requests**.
- The headline comes from weighted instrumental-variable estimates addressing imperfect uptake, not a simple “giving everyone access makes everyone 26% faster” comparison. See paper §§2.3 and 4 and Table 2.
- **Limit:** completions are not end-user benefits; quality proxies such as build success are limited. The experiments concern a coding assistant, not every current agent workflow.
- **Design consequence:** AI is a credible implementation lever. It still must earn its cost on accepted work, and PR throughput must not be relabeled customer value.

### 4. Team-level gains can coexist with downstream instability

**Sources:** DORA researchers, [2025 report announcement](https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report); [report landing page](https://dora.dev/dora-report-2025/).

- Nearly 5,000 survey respondents plus qualitative research. The researchers report positive relationships between AI adoption and delivery throughput/product performance, alongside a negative relationship with delivery stability.
- **Limit:** survey associations, not randomized causal estimates. Vendor-sponsored research. The 2025 throughput result differs from the 2024 result; do not mix years' headlines.
- **Design consequence:** pair speed with rework, stability, and user outcomes. Improving the surrounding system matters, but these results do **not** imply an empty repository should first build an internal developer platform.

## Engineering and product practice

These sources inform mechanisms and safeguards. They do not experimentally validate this exact workflow.

### 5. Small batches shorten feedback and make AI output reviewable

**Source:** DORA, [Working in small batches](https://dora.dev/capabilities/working-in-small-batches/).

Guidance emphasizes independently useful/testable increments, early integration, and feedback from users and operations. It warns against generating large AI changes or re-batching small changes before release.

**Applied here:** a narrow end-to-end slice, small integrated diffs, and a deployed feedback loop—not just smaller tickets. The one-day ordinary-slice target is a local starting heuristic, not a universal causal constant.

### 6. Count the whole queue, not just coding work

**Source:** DORA, [Work in process limits](https://dora.dev/capabilities/wip-limits/).

Guidance calls for visibility from idea to customer, capacity-based limits, and resolving downstream constraints instead of increasing WIP to keep people busy.

**Applied here:** one active delivery slice by default; separate review/decision queues and scheduled observation duties. Little's Law is used only as a stable-system accounting relationship, not as a promised throughput multiplier.

### 7. Measurements need tension and context

**Source:** DORA, [Software delivery performance metrics](https://dora.dev/guides/dora-metrics/).

The current guide lists five metrics: change lead time, deployment frequency, failed deployment recovery time, change fail rate, and deployment rework rate. It warns about goals that invite gaming, disparate comparisons, one-metric thinking, and measurement projects that displace improvement.

**Applied here:** outcome, elapsed delivery, total inputs, and quality/harm as separate views. Idea-to-release is deliberately distinguished from DORA's commit-to-production change lead time. No employee ranking or mandatory dashboard build.

### 8. More agents can mean more capacity—and much more overhead

**Source:** Anthropic, [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system).

The authors report a **90.2% improvement on an internal research evaluation**, and token usage of about **15× chat for multi-agent systems**, versus about **4× chat for agents**. They explicitly identify heavily shared context and coding dependencies as poor fits for the approach.

**Limits:** vendor engineering report and internal research tasks, not a controlled equal-budget software-delivery study. Fifteen times **chat** is not fifteen times **a single agent**, nor a universal cost constant.

**Applied here:** default to one builder; add bounded, independently checkable work only when it relieves a constraint. Charge setup, synthesis, integration, verification, and human supervision to the parallel option. Model consensus is not ground truth.

### 9. Discovery can end with “do not build”

**Source:** UK Government Service Manual, [How the discovery phase works](https://www.gov.uk/service-manual/agile-delivery/how-the-discovery-phase-works).

Guidance reframes requested solutions as user problems, examines constraints and existing alternatives, defines success measurement, and treats stopping as a legitimate result.

**Limit:** public-service guidance, not an RCT or a startup timetable. Its typical 4–8-week discovery duration is **not** imported here.

**Applied here:** one cheapest decision-changing probe, early user access, explicit no-build alternatives, and evidence-based stop/reframe decisions. Maintenance and legal obligations have a separate entry route.

**Empirical complement:** Camuffo et al. (2024), [A scientific approach to entrepreneurial decision-making: Large-scale replication and extension](https://openaccess.city.ac.uk/id/eprint/32437/), studies 759 firms across four randomized trials. Training in a scientific approach increased idea termination and supported more selective pivoting. The paper also analyzes revenue, but this workflow does not translate those estimates into a shipping-speed promise. The intervention was entrepreneurial training—not this card, these time budgets, or a trial of AI-assisted software delivery.

### 10. A time appetite should constrain scope, not quality

**Source:** Basecamp, *Shape Up*, [Set Boundaries](https://basecamp.com/shapeup/1.2-chapter-03).

Distinguishes an appetite—what an idea is worth investing—from an estimate of a fixed specification, and advocates narrowing the actual problem.

**Limit:** practitioner method and cases, not a universal optimal cadence. Its team/cycle sizes are not adopted here.

**Applied here:** fund a bounded experiment; vary optional scope while retaining essential safeguards. Reserve resources for safe cancellation and obligations that outlive the appetite.

### 11. Safe rollout depends on observability, exposure, and meaningful duration

**Source:** Google SRE Workbook, [Canarying Releases](https://sre.google/workbook/canarying-releases/), especially canary requirements, population/duration, and metric selection.

Guidance requires a way to expose a subset, evaluate it, and connect that decision to rollout. Representative traffic, delayed effects, attribution, and failure-domain isolation matter.

**Applied here:** no universal canary percentage or duration; verify the deployed path and match observation to the failure mechanism. Separately account for shared-data blast radius and destructive operations. The exact destructive-change gate is a conservative design synthesis, not a quoted canary rule.

### 12. Gates need not become an approval bureaucracy

**Source:** DORA, [Streamlining change approval](https://dora.dev/capabilities/streamlining-change-approval/).

Reports research favoring peer review near the work plus automation; heavyweight external approvals correlate with worse delivery performance, with no evidence in that analysis of lower change failure rates.

**Limit:** observational evidence, not permission to disregard segregation of duties, legal requirements, or material-risk authority.

**Applied here:** automated deterministic checks and preauthorized routine work, with competent human judgment for consequential exposure. Do not manufacture a committee of agents to imitate an approval board.

## What is designed rather than proven

The combined seven-state loop, templates, task packets, initial WIP/concurrency limits, one-day ordinary slice, and two-week pilot are **design choices**. Their rationale is reduced speculative work, shorter queues, earlier verification, and lower coordination burden. Their net effect depends on the user, product, tools, and constraints.

The workflow was independently reviewed and exercised through fictional failure scenarios during this session. That checks internal coherence; it does not establish user adoption, safe production execution, or a measured delivery improvement. Use the [pilot protocol](MEASUREMENT.md#4-test-this-workflow-rather-than-declaring-it-successful) to determine whether it accelerates your actual work.
