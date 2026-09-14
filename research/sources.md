# Primary-source register

All sources accessed **2026-09-14**. Dates identify publication or the specific manuscript revision, not necessarily when work occurred. Findings below are authors’ reported results, not independently reproduced results.

Evidence types are intentionally separate: **controlled experiment**, **observational study**, **benchmark experiment/audit**, and **engineering field report** answer different questions. An arXiv posting does not by itself establish peer review.

## S01

**METR — Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity** · 2025-07-10 · randomized field experiment.

[Primary report](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/) · [Paper](https://arxiv.org/abs/2507.09089)

- **Observed:** 16 experienced maintainers, 246 real tasks in familiar repositories. Allowing AI increased completion time by 19%; developers nevertheless believed it had accelerated them. Tools were primarily Cursor with Claude 3.5/3.7 Sonnet.
- **Scope:** February–June 2025 tools and a specialized population; not a verdict on contemporary agents or all developers. The authors explicitly reject that generalization.
- **Useful for:** separating perceived acceleration from observed task time. Read with S02, not alone.

## S02

**METR — We are Changing our Developer Productivity Experiment Design** · 2026-02-24 · field-experiment follow-up and methodological disclosure.

[Primary report and dataset links](https://metr.org/blog/2026-02-24-uplift-update/)

- **Observed:** 57 developers, 143 repositories, 800+ tasks. Estimated time changes were −18% for returning developers (interval −38% to +9%) and −4% for new developers (−15% to +9%).
- **Scope:** selective participation/task submission, lower compensation, noncompletion, and concurrent-agent time accounting undermine interpretation. Authors consider the data only very weak evidence for the size of current gains.
- **Useful for:** contemporary measurement design. This is not a clean causal reversal of S01.

## S03

**Cui et al. — The Effects of Generative AI on High-Skilled Work: Evidence from Three Field Experiments with Software Developers** · February 2025 manuscript · randomized field experiments.

[Author-hosted manuscript at MIT](https://economics.mit.edu/sites/default/files/inline-files/draft_copilot_experiments.pdf)

- **Observed:** pooled experiments at Microsoft, Accenture, and a Fortune 100 company, 4,867 developers. Preferred instrumental-variable estimate: 26.08% more completed tasks for tool users (SE 10.3%).
- **Scope:** estimates treatment on the treated under the analysis assumptions, not a 26% reduction in task time. Earlier completion-style Copilot, uneven adoption, noisy individual experiments, and post-registration. Microsoft-affiliated coauthors and company-run trials.
- **Useful for:** credible positive productivity evidence with a clearly different population, treatment, and outcome from S01.

## S04

**AI Writes Faster Than Humans Can Review: A Longitudinal Study of an Enterprise 2x Mandate** · 2026-07-02, v1 · observational longitudinal case study/preprint.

[Abstract and date](https://arxiv.org/abs/2607.01904v1) · [Full text](https://arxiv.org/html/2607.01904v1)

- **Observed:** 802 developers and 196,212 PRs, January 2024–April 2026. Per-capita throughput reached 2.09× baseline; per-reviewer load roughly doubled; automated review overtook human review; merge/revert rates remained stable.
- **Scope:** one unusually AI-supportive company, nonrandom adoption, and a PR-count target that could influence behavior. Difference-in-differences supports an adoption association, not exact causal attribution. Quality proxies are coarse and short-horizon; gains concentrated in newer code.
- **Useful for:** substantial contemporary gains and downstream bottleneck migration, without equating PRs with delivered value.

## S05

**Borg et al. — Echoes of AI: Investigating the Downstream Effects of AI Assistants on Software Maintainability** · v3, 2026-02-26; first submitted 2025-07-01 · preregistered two-phase study.

[Version/date](https://arxiv.org/abs/2507.00788v3) · [Full text read](https://arxiv.org/html/2507.00788v3) · [Journal record](https://doi.org/10.1007/s10664-026-10889-1)

- **Observed:** 151 participants, 95% professionals. New developers were randomly assigned to evolve previously produced Java code without AI; no significant subsequent completion-time or code-quality difference was detected.
- **Scope:** experiment conducted in late 2024, small application, short handoff horizon, not modern autonomous agents. Phase-one speed observations were not the randomized handoff result. Authors disclose CodeScene and software-delivery consulting interests; CodeHealth is one measure used.
- **Useful for:** counterevidence to inevitable maintainability degradation. No significant difference is not proof of equivalence or long-term safety. Journal text was inaccessible; claims here use v3.

## S06

**Shen and Tamkin — How AI Impacts Skill Formation** · first submitted 2026-01-28; v2 2026-02-01 · randomized experiment.

[Paper metadata](https://arxiv.org/abs/2601.20245v2) · [Authors’ research report read](https://www.anthropic.com/research/AI-assistance-coding-skills)

- **Observed:** 52 mostly junior Python developers learning Trio. Immediate quiz scores averaged 50% with AI versus 67% without: **17 percentage points**, not 17% relatively. Completion-time improvement was not statistically significant.
- **Scope:** unfamiliar library, small sample, immediate assessment, sidebar assistant rather than autonomous coding agent. Interaction-pattern associations were qualitative, not randomized treatment comparisons.
- **Useful for:** distinguishing completing work from acquiring the competence needed to supervise it. Anthropic-authored research.

## S07

**(Im)Paired Programming: Coding Agents Improve Productivity but Harm Understanding** · 2026-07-29, v1 · randomized user study/preprint.

[Date/abstract](https://arxiv.org/abs/2607.26375v1) · [Full text](https://arxiv.org/html/2607.26375v1)

- **Observed:** 54 CS students built a website using either an editing agent or a restricted snippet chatbot. Agent users achieved better initial task accuracy but worse comprehension; extension performance without the agent did not show a clear corresponding benefit.
- **Scope:** students, one web-development setting, GPT-4.1/Aider-based interface, constrained comparison chatbot, and some LLM-assisted scoring/question generation. Not professional longitudinal evidence. Copy-paste and auto-accept associations are not causal intervention results.
- **Useful for:** testing whether nominal human involvement actually preserves understanding.

## S08

**Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?** · first submitted 2026-02-12; v2 2026-06-23 · controlled benchmark study/preprint.

[Version/date](https://arxiv.org/abs/2602.11988v2) · [Full text](https://arxiv.org/html/2602.11988v2)

- **Observed:** 300 SWE-bench Lite tasks plus 138 CTXbench tasks; four agent–model pairings. No statistically significant general success improvement from context files. Generated files increased inference costs by roughly 20–23%; human-written files outperformed generated ones.
- **Scope:** Python repositories, one completion per condition, benchmark tests rather than broader quality. Instructions induced more testing/exploration; their usefulness is not measured solely by task success. The June revision is more qualified than “AGENTS.md makes agents worse.”
- **Useful for:** separating necessary local instructions from redundant generated documentation.

## S09

**Vercel — AGENTS.md outperforms skills in our agent evals** · 2026-01-27 · vendor benchmark experiment.

[Primary report](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals)

- **Observed:** version-matched Next.js documentation with an always-present 8 KB index achieved 100% pass rate on the reported suite; explicitly prompted skills reached 79%; baseline and unprompted skills 53%. Skills were not invoked in 56% of cases.
- **Scope:** framework-knowledge gaps, not general repository guidance. Behavior-based tests and retries are described, but sample/model/budget detail is insufficient for broad inference. Not a guarantee or universal argument against skills.
- **Useful for:** evidence that access to missing knowledge and reliable retrieval can matter.

## S10

**Google Research — Towards a science of scaling agent systems: When and why agent systems work** · 2026-01-28 report on a December 2025 paper · controlled architecture benchmark study.

[Research report](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/) · [Underlying paper](https://arxiv.org/abs/2512.08296)

- **Observed:** 180 configurations across model families. Central coordination improved financial-reasoning performance 80.9% relatively; multi-agent variants degraded sequential PlanCraft performance by 39–70%.
- **Scope:** finance, browsing, planning, and tool-use benchmarks—not repository development. Coordination taxes and error propagation are informative mechanisms, but numeric thresholds do not transfer automatically to coding.
- **Useful for:** rejecting agent count as a stand-alone optimization target.

## S11

**Cursor/NVIDIA — Speeding up GPU kernels by 38% with a multi-agent system** · 2026-04-14 · engineering experiment with published artifacts.

[Primary report and solution-repository link](https://cursor.com/blog/multi-agent-kernels)

- **Observed:** three-week optimization across 235 kernel problems on B200 hardware; 1.38× geometric-mean runtime improvement over single-agent-optimized PyTorch baselines. A planner redistributed workers using benchmark feedback; coordination protocol lived in one Markdown file.
- **Scope:** 38% is **kernel execution improvement**, not developer time saved. Languages, search budgets, and approaches differ; not a compute-matched test isolating multi-agent benefits. Vendor-authored; artifacts were not rerun in this review.
- **Useful for:** feasibility of parallel agent search with measurable objectives and anti-cheating validation.

## S12

**Anthropic — Harness design for long-running application development** · 2026-03-24 · first-person engineering experiments.

[Primary report](https://www.anthropic.com/engineering/harness-design-long-running-apps)

- **Observed:** planner/generator/evaluator, file-based contracts, and browser QA found concrete functional defects. One full run cost $200/6 hours versus $9/20 minutes solo, with substantially different scope and outcomes. Later models allowed removal of resets and sprint scaffolding; some evaluation became unnecessary overhead.
- **Scope:** tuned demos on a particular stack, unequal budgets, subjective assessment, no broad randomized comparison. Rising aesthetic scores sometimes disagreed with the author’s preferences.
- **Useful for:** both adding and removing structure based on failure analysis; not evidence for delegating taste.

## S13

**OpenAI — Harness engineering: leveraging Codex in an agent-first world** · 2026-02-11 · production field report.

[Primary report](https://openai.com/index/harness-engineering/)

- **Observed:** internal product with real users, roughly 1,500 merged PRs over five months. Short context index, versioned plans/docs, isolated per-worktree applications, agent-visible observability, and mechanical architectural checks.
- **Scope:** greenfield, substantial environment investment, estimated “one-tenth the time” without measured counterfactual, no multi-year evidence. Minimal blocking merge gates and optional human PR review are local choices, not established best practices.
- **Useful for:** concrete agent-accessible feedback mechanisms and the costs hidden behind “agents write the code.”

## S14

**Anthropic — Quantifying infrastructure noise in agentic coding evals** · 2026-02-05 · controlled infrastructure experiments.

[Primary report](https://www.anthropic.com/engineering/infrastructure-noise)

- **Observed:** same model/harness/tasks, six resource configurations: Terminal-Bench 2.0 scores differed by six percentage points. Resource guarantees and hard limits changed both failure rates and viable strategies. Supporting SWE-bench experiment: 227 problems, ten samples each.
- **Scope:** mainly Claude and selected benchmarks. No universal memory multiplier follows; environment controls do not prove deterministic model output.
- **Useful for:** treating resource policy, runtime, latency, and timeouts as experimental variables.

## S15

**Horace He / Thinking Machines Lab — Defeating Nondeterminism in LLM Inference** · 2025-09-10 · systems experiment with implementation.

[Primary article and implementation link](https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/)

- **Observed:** 1,000 temperature-zero Qwen completions yielded 80 unique outputs; batch-invariant kernels made all 1,000 identical. Demonstration performance tradeoffs are reported separately on an 8B model.
- **Scope:** controlled inference stack, hardware, and model—not arbitrary hosted APIs or complete agent workflows. Batch-sensitive numerical reduction is a demonstrated cause, not a blanket explanation for every source of nondeterminism.
- **Useful for:** rejecting both “temperature zero guarantees determinism” and “deterministic inference is impossible.”

## S16

**OpenAI — Separating signal from noise in coding evaluations** · 2026-07-08 · benchmark audit.

[Primary audit](https://openai.com/index/separating-signal-from-noise-coding-evaluations/)

- **Observed:** estimates approximately 30% of SWE-Bench Pro tasks are broken. Pipeline flagged 286 tasks; each flagged task received five human reviews alongside investigator-agent analysis. Problems include overly strict/low-coverage tests and underspecified/misleading prompts.
- **Scope:** model-vendor audit, pipeline-selected subset, reviewer judgment. Estimated prevalence should be attributed, not treated as universal benchmark failure rate. OpenAI withdrew its earlier recommendation to adopt this benchmark.
- **Useful for:** checking the validity of the verifier, including false failures and false passes.

## S17

**SWE-Bench Pro Verified: A Reliable Benchmark for Software Engineering Agents** · 2026-09-08, v1 · benchmark revision and evaluation/preprint.

[Date/abstract](https://arxiv.org/abs/2609.08149v1) · [Full text and artifact links](https://arxiv.org/html/2609.08149v1)

- **Observed:** preserves 731 tasks, refines 102, and adds controls against solution leakage through Git objects, local artifacts, metadata, and network retrieval. Some model scores fall substantially under the protected setup.
- **Scope:** very recent preprint; authors acknowledge incomplete domain blocking, possible residual local information, and uncorrected task issues. Does not establish an ungameable benchmark.
- **Useful for:** current evidence that evaluation-time information access and test quality materially affect apparent coding capability.

## S18

**Anthropic — How we contain Claude across products** · 2026-05-25 · security engineering field report and incident analysis.

[Primary report](https://www.anthropic.com/engineering/how-we-contain-claude)

- **Observed:** roughly 93% of permission prompts approved; OS sandboxing reduced prompts 84% in reported telemetry. Describes pre-consent config execution failures and exfiltration through an allowed API domain; remediation changed the enforced boundary, not just instructions.
- **Scope:** vendor telemetry, no randomized approval-policy comparison. Sandboxes, proxies, mounts, and exceptions can themselves be flawed; an allowed domain is not an intrinsically safe capability.
- **Useful for:** distinguishing human attention, probabilistic behavioral safeguards, and externally enforced authority.

## S19

**StrongDM — Software Factories and the Agentic Moment; The Principles** · undated living pages as retrieved · first-person field report/operating philosophy.

[Factory report](https://factory.strongdm.ai/) · [Principles](https://factory.strongdm.ai/principles)

- **Reported approach:** no human code writing/review; specifications and external holdout scenarios drive feedback loops, using behavioral replicas of third-party services. Agents had previously exploited narrow tests. “Satisfaction” is a probabilistic outcome assessment rather than merely a green test suite.
- **Scope:** no controlled productivity/defect comparison on these pages or independent validation of replica fidelity. The suggested $1,000 token spend is **per engineer per day**, an advocacy statement—not an efficiency result or recommendation here. The 2025 team-formation date is not the page publication date.
- **Useful for:** a genuinely different human-involvement model and concrete verifier-separation idea, with substantial unanswered cost and assurance questions.
