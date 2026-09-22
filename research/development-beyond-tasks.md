# Development beyond isolated agent tasks

Research notes, 2026-09-22. Follow-up to [the first review](agent-development.md), extending into discovery, coordination, evolution, and recovery.

This is a targeted evidence review, not a systematic review or an architecture proposal. Discovery and evolution were investigated independently in parallel; key claims were cross-checked against primary texts. Older human-development studies identify problems worth investigating, not proven solutions for agents. Recent benchmarks demonstrate behavior in their test conditions, not production reliability.

## 1. A requirement can be an invention, an observation, or a negotiated choice

Ferrari et al. studied 30 graduate software-engineering students, many also working professionally, interviewing a role-playing researcher about a fictional summer-camp system, then examining related applications. Analysts introduced both potentially important omissions, such as privacy, and unsupported assumptions about users and features. The study did not validate the resulting requirements against stakeholder needs or product usefulness. Participants were asked to generate many stories, which could itself encourage invention. More requirements therefore did not establish better discovery. [1]

An earlier field study interviewed six developers and five clients and surveyed 37 practitioners and 32 end users. Access to knowledgeable staff was constrained by ordinary business operations; authorized representatives did not necessarily understand the work being computerized. Some apparently unclear requirements involved absent perspectives or conflicting interests, not merely imprecise wording. This was a small, non-random, partly self-reported sample—not a causal comparison of elicitation methods. [2]

Seven small-company case studies found viable but markedly different requirements practices: verbal coordination, disposable prototypes, paid discovery, and contractual specification. The authors offer competing explanations for their success; the study cannot establish which practice is best. These were surviving firms in one metropolitan area, studied largely through leadership interviews. [3]

**Implication to test:** distinguish a proposed possibility from an evidenced need and an authorized decision. Compare additional requester conversation with access to actual work examples and other affected perspectives. Measure validated omissions, unwanted functionality, and stakeholder time—not question or story counts. This does not justify exhaustive questioning or involving everyone continuously.

## 2. Experiments need a decision and a defensible measure

Microsoft's experimentation report includes an Office Online redesign with 64% fewer users clicking Buy. But the redesign displayed prices that the control concealed: extra control clicks might simply have been price inquiries. Purchases were not measured. Randomization established an effect on clicks, not which design produced more sales. The report also discusses instrumentation costs and low-traffic limitations; those cost-benefit arguments come from operating experience, not randomized comparisons of experimentation policies. [4]

Stronger causal evidence comes from an adjacent field. Four randomized trials covering 759 firms compared entrepreneurial training approaches. Both groups learned research techniques, including interviews, surveys, and A/B testing. Treatment added explicit theories, derived hypotheses, and belief updating. Project termination increased 9.8 percentage points; pivoting once became more common, but pivoting more than twice became less common. Pooled revenue increased, although most individual-trial revenue estimates were imprecise. [5]

These trials concern volunteer firms across industries, not agent development. The intervention bundles several practices. Terminating more projects does not establish that every termination was correct; revenue is not profit.

**Implication to test:** compare decision-linked evidence gathering with open-ended iteration at equal budgets. State what observation would change a decision, then measure downstream benefit after research costs. Count useful ideas wrongly rejected as well as weak ideas abandoned. This supports neither mandatory A/B tests nor endless experimentation.

## 3. Information boundaries and coordination topology are different questions

Ko et al. observed 17 developers in approximately 90-minute sessions at one large software company. Common information needs included awareness of artifacts and coworkers. Searches for design intent and program behavior were frequently deferred; unavailable coworkers sometimes held the only accessible knowledge. This is descriptive evidence about information access, not proof that recording every discussion would solve it. [6]

Parnas supplies a useful conceptual distinction, not an empirical agent result: decompose around difficult or changeable design decisions rather than execution stages. His paper explicitly separates good decomposition from hierarchical organization. Applied to agents, the hypothesis is that deciding what work can be separated and what knowledge must cross a boundary matters independently of whether agents have managers. [7]

Empirical coordination evidence is mixed:

- Cataldo et al. associated coordination aligned with technical dependencies with shorter change-resolution times. This was observational human-team evidence, not a causal test of an agent hierarchy. [8]
- A longitudinal analysis of 25 open-source projects found negligible relationships between its motif-based coordination-congruence measure and bugs or churn. Its measures and outcomes differ from the earlier work, so this is a meaningful qualification, not an exact replication. [9]
- *Towards a Science of Scaling Agent Systems*, revision 3, compares 260 configurations across six benchmarks, five architectures, and three model families. Results differ by task. Its strongest robust statistical finding is capability saturation: stronger single-agent baselines leave less benefit from coordination. Other proposed effects weaken under cluster-robust inference. Software and terminal benchmarks use only 20 instances each, with wide per-configuration uncertainty. The paper does not establish a universal threshold or organization for software development. [10]

**Implication to test:** compare a strong single-agent baseline with alternative decompositions and coordination arrangements under the same resource budget. Include integration failures, duplicated investigation, human repair, and cost. Neither “flat swarms” nor “agent companies” deserve to be the default conclusion from this evidence.

## 4. Continuing development means inheriting previous mistakes

SWE-Milestone evaluates 98 graded milestones across seven dependency-rich repositories. In independent evaluation, each task starts from the canonical repository state; continuous evaluation carries forward the agent's own changes. The paper reports independent-task scores above 80%, but a maximum continuous score of 38.03%. **This is a composite feature/regression score, not a completion rate.** [11]

The comparison is informative but not neutral: requirements were refined through agent dry runs, helping establish isolated solvability. Histories were deliberately selected for dependencies. Submissions are one-shot per milestone, and later repairs do not retroactively change earlier scores. These are hours-long reconstructed histories, not months of production ownership.

Importantly, the authors observe useful context reuse and functioning compaction alongside accumulating defects. The failure is not adequately described as simply “the agent forgot.” A remembered but damaged codebase can still obstruct subsequent work.

SWE-CI evaluates 100 base/target pairs from 68 Python repositories through up to 20 repair rounds. Its average “233 days and 71 commits” describes historical distance between snapshots—not agent runtime or 71 separately arriving requirements. Feedback comes from a fixed future test suite. Agents can inspect those tests but are explicitly prohibited from executing them; verification occurs in the external loop. Most models avoid all regressions in fewer than a quarter of evaluated sequences, but two Opus models exceed half: regression is not inevitable. Selection excludes dependency-changing spans and cases where target tests cannot launch against the old code. [12]

**Implication to test:** evaluate sequences of changes against the state agents actually leave behind. Separately measure feature progress, persistent regressions, repair cost, and success on the next dependent change. Compare retained history with fresh investigation after intervening changes or session replacement; accurate current understanding matters more than recall of past decisions.

## 5. Recovery and correct diagnosis are not interchangeable

SREGym injects 90 incident scenarios across five Kubernetes applications. It evaluates three agent systems, with one system tested using two models, over three repetitions per scenario, with and without background disturbances. Runs have a 30-minute timeout. Mitigation is checked against system health; diagnosis uses an LLM judge validated against expert judgments on 100 outputs. [13]

Claude Code's combined diagnosis-and-mitigation success falls from 60.7% without noise to 53.7% with noise, while mitigation alone remains around 76%. Across configurations, agents mitigate 35–59% of cases even after an incorrect initial diagnosis. Trajectories include both symptom-matching fixes and revisions prompted by real feedback. The specialized SRE system leads on mitigation, while a general coding agent leads on the combined measure.

These are controlled incidents in relatively small applications, not production field evidence. The evaluation does not establish prevention of recurrence, customer impact, or maintainability of emergency fixes.

**Implication to test:** follow a recovered service into a recurrence test and another dependent change. Assess diagnosis, restoration, residual damage, and human takeover cost separately. A green health check should not silently become a claim of durable understanding.

## 6. Human oversight is a capability to evaluate, not a free fallback

A randomized study assigned 52 Python programmers unfamiliar with Trio to coding with or without a GPT-4o chat assistant—not an autonomous coding agent. AI access reduced immediate post-task quiz performance (Cohen's d = 0.738, p = .01), without a statistically significant average completion-time improvement. Under the 35-minute limit, four control participants did not finish the second task, versus none with AI; the nonsignificant time result does not establish equivalent completion outcomes. Interaction patterns involving greater conceptual engagement had better learning outcomes, but those patterns were observational subgroups, not randomized treatments. [14]

This measures short-term acquisition of an unfamiliar library, not years-long deskilling or demonstrated failure to supervise agents. It nevertheless challenges the assumption that producing a solution necessarily gives its human owner enough understanding to inspect or repair it.

Anthropic's observational telemetry report also complicates the equation of experience with human absence. More experienced Claude Code users both enabled full auto-approval more often and interrupted more turns. These groups differ in users and tasks; the report does not show whether takeover was successful or cheap. [15]

Actual multi-month repository evidence remains different again: a matched observational adoption study found increased commit counts and lines added in agent-first repositories, but not significant average gains in repositories with prior observable AI-IDE use. Those outcomes measure code-production activity, not useful delivery. Complexity rose in both groups; warning growth was statistically significant only in the agent-first group. Unobserved AI use and pre-treatment differences weaken causal attribution. Complexity and warnings are maintenance-risk proxies, not measured repair costs. [16]

**Implication to test:** include a later debugging or takeover exercise when evaluating delegation. Count context reconstruction and repair effort rather than treating human intervention as an unlimited safety net. This does not establish a mandatory human role or approval policy.

## What this changes for Honeycomb

A useful next evaluation should follow work across boundaries that isolated-task benchmarks remove:

**A proposed change → evidence that it is worth making → implementation → operation → a subsequent change.**

This is an evaluation scope, not a required linear workflow. Discovery, implementation, and operation can overlap; stopping or reversing a change can be a good outcome.

Test contrasting situations: unfamiliar versus familiar domains, independent versus coupled changes, and clean versus already-damaged inherited state. Keep model and resource budgets comparable. Report useful outcomes, unwanted work, regressions, human effort, and recovery costs separately rather than collapsing them into code volume or uninterrupted runtime.

The central hypothesis is that Honeycomb should improve the result of **successive development decisions**, including their downstream consequences—not merely the execution of each decision in isolation. The evidence motivates testing that hypothesis; it does not select an interface, memory representation, agent hierarchy, or human/agent division of labor.

Still thin: discovery of genuinely worthwhile unrecognized problems, resolution of conflicting stakeholder interests, reliable takeover, and sustained autonomous operation over real elapsed months or years. Research cannot supply the user's preferences about these trade-offs.

## Sources

1. Ferrari, Spoletini & Debnath (2022), [How Do Requirements Evolve During Elicitation?](https://arxiv.org/pdf/2208.00825) — exploratory laboratory study; methods and validity threats consulted.
2. Al-Rawas & Easterbrook (1996), [Communication Problems in Requirements Engineering: A Field Study](https://www.cs.toronto.edu/~sme/papers/1996/NASA-IVV-96-002.pdf) — interviews, observations, and questionnaires.
3. Aranda, Easterbrook & Wilson (2007), [Requirements in the Wild: How Small Companies Do It](https://www.cs.toronto.edu/~sme/papers/2007/REinthewild.pdf) — seven exploratory company case studies.
4. Kohavi, Crook & Longbotham (2009), [Online Experimentation at Microsoft](https://exp-platform.com/Documents/ExP_DMCaseStudies.pdf) — first-party report of online experiments; Office Online case and limitations consulted.
5. Camuffo et al. (2024), [A Scientific Approach to Entrepreneurial Decision-Making: Large-Scale Replication and Extension](https://doi.org/10.1002/smj.3580), [open full text](https://openaccess.city.ac.uk/id/eprint/32437/) — four randomized field trials; intervention and pooled results consulted.
6. Ko, DeLine & Venolia (2007), [Information Needs in Collocated Software Development Teams](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/icse07_ko.pdf) — field observation.
7. Parnas (1972), [On the Criteria To Be Used in Decomposing Systems into Modules](https://wstomv.win.tue.nl/edu/2ip30/references/criteria_for_modularization.pdf) — conceptual worked examples, not an empirical trial.
8. Cataldo, Herbsleb & Carley (2008), [Socio-Technical Congruence: A Framework for Assessing the Impact of Technical and Work Dependencies on Software Development Productivity](https://herbsleb.org/web-pubs/pdfs/cataldo-socio-2008.pdf) — observational coordination study.
9. Mauerer et al., [In Search of Socio-Technical Congruence: A Large-Scale Longitudinal Study](https://arxiv.org/abs/2105.08198), [full text consulted](https://www.se.cs.uni-saarland.de/publications/docs/MJT+21.pdf) — counterevidence, 25 open-source projects; discussion and validity threats consulted.
10. [Towards a Science of Scaling Agent Systems](https://arxiv.org/html/2512.08296v3) — April 2026 revision; benchmark comparison, robustness checks, and limitations consulted. Earlier summaries describe a smaller study.
11. [SWE-Milestone: Evaluating AI Agents on Continuous Software Evolution](https://arxiv.org/html/2603.13428v4) — July 2026 revision; benchmark construction, scoring, and evaluation protocol consulted.
12. [SWE-CI: Evaluating Agent Capabilities in Maintaining Codebases via Continuous Integration](https://arxiv.org/html/2603.03823v1) — March 2026 benchmark preprint; selection criteria and supplied agent prompts consulted.
13. [SREGym](https://arxiv.org/html/2605.07161v1) — May 2026 incident-recovery benchmark preprint; result tables, diagnosis judging, and limitations consulted.
14. [How AI Impacts Skill Formation](https://arxiv.org/html/2601.20245) — randomized coding/library-learning study; main experiment, exploratory analyses, and limitations consulted.
15. Anthropic, [Measuring AI agent autonomy in practice](https://www.anthropic.com/research/measuring-agent-autonomy), [methods appendix](https://cdn.sanity.io/files/4zrzovbb/website/55e4d2de6eb39b3a9259c3f74843f86b1a12e265.pdf) — February 2026 vendor observational report.
16. [AI IDEs or Autonomous Agents? Measuring the Impact of Coding Agents on Software Development](https://arxiv.org/html/2601.13597) — January 2026 repository-level observational study with matched difference-in-differences analysis; data through November 2025.
