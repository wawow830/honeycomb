# What current agent-development approaches miss

Research notes, 2026-09-22. This is an evidence review, not a Honeycomb architecture proposal.

Question: what does research on actual development reveal that task-oriented coding-agent demonstrations and benchmarks miss?

Follow-up: [Development beyond isolated agent tasks](development-beyond-tasks.md) extends this review into discovery, coordination, evolution, and recovery.

## 1. Requirements are developed during the interaction

**Evidence.** SWE-chat records roughly 6,000 real sessions. Its annotations classify understanding existing code as a more frequent specific intent than creating code (19.0% versus 13.4% of prompts). In its Claude Code analysis, users push back after about 39% of turns; proactive clarification occurs in only 1.1–2.6% of turns across coding modes. People remain actively involved even when agents write virtually all committed code. [1]

A subsequent study of the same corpus associates newly stated requirements with increased deletion/replacement of earlier agent code. Crucially, it distinguishes discovering additional requirements from correcting failures against already-stated requirements. [2]

**Bounds.** This is not a representative sample of all development: it contains opt-in public Entire CLI logs, is heavily weighted toward Claude Code, and misses many abandoned sessions. Many classifications use LLM judges. Deleted code is not necessarily wasted work. The late-requirements study measures an association, not proof that a requirement caused each deletion; it is not an independent corpus.

**Implication to investigate.** Development cannot safely be modeled only as execution of a complete initial brief. But neither study establishes that exhaustive questioning or a mandatory specification gate is the answer. Learning through implementation may be useful.

## 2. Continuity requires more than a longer conversation

**Evidence.** Anthropic's long-running-agent experiments report incomplete work abandoned across context boundaries, later sessions prematurely declaring completion, and locally tested features failing end-to-end. Their interventions include small increments, progress artifacts, repeatable environment startup, and browser-driven checks. The report explicitly leaves single-agent versus multi-agent superiority unresolved. [3]

OpenAI's five-month internal-product report describes a failed giant-instruction-file approach. It instead uses a short navigation document, versioned project knowledge, mechanical architectural constraints, and runnable per-worktree applications with accessible logs, metrics, and traces. It also reports recurring cleanup to counter pattern replication and drift. [4]

**Bounds.** These are vendor engineering reports, not controlled comparisons. Their applications and constraints are specific. OpenAI explicitly does not establish coherence over years, and its estimated speedup has no controlled counterfactual.

**Implication to investigate.** An agent needs access to the relevant state and means of checking it. Increasing context size or retaining transcripts does not by itself establish freshness, correctness, or completeness. The precise representation remains a design question.

## 3. Behavioral checks can miss the purpose of engineering work

**Evidence.** SWE Atlas evaluates codebase understanding, test writing, and refactoring. In its refactoring analysis, models would score roughly 60–80% using tests alone, but perform substantially worse when assessed for completing the structural work. Examples include leftover obsolete code and incomplete updates across call sites. Test-writing failures include weak assertions that still pass after the target code is broken. [5]

**Bounds.** The suite contains 284 curated tasks across 18 repositories. Some grading uses expert-authored rubrics evaluated by LLM judges. It remains single-turn and excludes major areas such as operations, infrastructure, and security. These results are diagnostic, not a general ranking of development systems.

**Implication to investigate.** Completion evidence must match the claim. Preserving behavior does not establish that a refactor succeeded; a green generated test suite does not establish its ability to detect regressions.

## 4. Coordination topology is not settled

**Evidence.** Cursor reports that equal-status agents coordinating through a shared file suffered contention, fragile locking, and avoidance of difficult work. Planners and workers improved its experiments. Conversely, an added integrator role became a bottleneck and was removed. Drift still required periodic fresh starts. [6]

**Bounds.** These are self-reported large-scale coding experiments, not controlled evidence for a universally best organization. Code volume and commit counts do not establish product usefulness or long-term maintainability. One large migration still required review.

**Implication to investigate.** My earlier blanket advice against agent hierarchies was unjustified. So would be making a hierarchy mandatory. Coordination should be compared on actual dependencies, integration failures, useful outcomes, cost, and intervention—not the number of simultaneously active agents.

## 5. Faster selected tasks and better development are different measurements

**Evidence.** DORA's author summary of its 2025 research reports positive associations between AI adoption and delivery throughput/product performance, alongside a negative association with delivery stability. It describes nearly 5,000 survey respondents and over 100 hours of qualitative data. [7]

METR distinguishes speedup on the old task mix, speedup on the new AI-enabled task mix, and increased value when task selection can change. These quantities need not agree. Testing only yesterday's tasks can miss new opportunities; measuring impressive new tasks can overstate their value. [8]

**Bounds.** DORA's relationships are observational, not isolated causal effects. METR's task-substitution argument is an analytical model with explicit assumptions, not an experimental measurement of a particular tool.

**Implication to investigate.** A ground-up redesign should not be judged only by how fast it processes an unchanged backlog. Conversely, automatically generating more work is not evidence of improvement.

## Counterevidence and overclaims to avoid

- **“AI makes developers slower.”** METR's early-2025 randomized study found a 19% slowdown among 16 experienced maintainers working on familiar repositories. Its February 2026 update explicitly says later estimates are unreliable because of participation/task selection and concurrent-agent time measurement. It considers increased speedup plausible. The original finding is not a current universal estimate. [9, 10]
- **“Agent-written changes are inherently worse.”** A study of 489 Python repositories compared balanced samples of 2,275 merged agent and 2,275 merged human PRs and found mostly non-significant differences in estimated defect proneness. This is observational, uses imperfect bug-origin inference, and concerns accepted changes under existing review—not unattended generation. It nevertheless contradicts a blanket claim. [11]
- **“Low code survival measures failure.”** SWE-chat's line-attribution measures miss semantic reuse and useful exploratory work. Its own limitations warn against equating those proxies with developer value. [1]
- **“More questions would solve collaboration.”** Neither observational correction counts nor requirement-associated rework establish an optimal clarification policy. Questions themselves consume attention; requirements can legitimately emerge later. [1, 2]

## Still unresolved

The reviewed evidence is strongest around coding sessions, repository changes, and delivery practices. It is weaker on problem selection, product discovery, conflicting stakeholder needs, and years-long operation and evolution. Missing evidence is not proof that current tools cannot support these activities.

It does not identify one best agent organization, a required human/agent division of work, or the right interface for Honeycomb. Those should remain hypotheses rather than conclusions smuggled into the design.

## Sources

1. [SWE-chat: Coding Agent Interactions From Real Users in the Wild](https://arxiv.org/html/2604.20779) — observational corpus and preprint; methods, results, and limitations consulted.
2. [Requirements After the First Edit](https://arxiv.org/html/2609.03028v1) — observational reanalysis plus limited controlled experiments; preprint.
3. [Anthropic: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) — November 2025 engineering report.
4. [OpenAI: Harness engineering](https://openai.com/index/harness-engineering/) — February 2026 engineering report.
5. [SWE Atlas: Benchmarking Coding Agents Beyond Issue Resolution](https://arxiv.org/html/2605.08366v1) — benchmark preprint; methods, analysis, and limitations consulted.
6. [Cursor: Scaling long-running autonomous coding](https://cursor.com/blog/scaling-agents) — engineering report.
7. [DORA authors: Announcing the 2025 DORA Report](https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report) — author summary; the full report was not reviewed.
8. [METR: Task Substitution and Uplift](https://metr.org/blog/2026-05-08-task-substitution-and-uplift/) — May 2026 analytical note.
9. [METR: Early-2025 experienced developer study](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/) — randomized trial, author report.
10. [METR: Changing our developer productivity experiment design](https://metr.org/blog/2026-02-24-uplift-update/) — February 2026 follow-up and methodological limitations.
11. [How Do AI Coding Agents Contribute to Software Development?](https://arxiv.org/html/2607.21832v1) — observational PR study; methodology and validity threats consulted. Publication is in 2026; collected data ends in November 2025.
