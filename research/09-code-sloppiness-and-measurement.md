# Code sloppiness: measure the trajectory, not just the test result

**Ingested 2026-09-15.** Sebastian's ["If coding is solved, what now?: Measuring the sloppiness of code"](https://earendil.com/posts/measuring-code-sloppiness/) is a practitioner essay, not a controlled study. Its central concern fits the existing cases: an implementation can satisfy an executable contract while making the next change harder, and the latter property is difficult to evaluate without human judgment. The article points to [SlopCodeBench](https://arxiv.org/html/2603.24755v1) for its quantitative measures. The linked paper's version 1 and the article were read; the benchmark was not rerun locally.

## What the article argues

The article separates three kinds of evaluation:

- **AI judges:** a numerical score or pairwise preference is not treated as a reliable substitute for evaluation. In particular, the author describes pairwise preferences changing when candidate labels are renamed.
- **Human judges:** human review is presented as the strongest route for readability and taste, but too expensive to scale to millions of lines or to broad model comparisons.
- **Simple proxies:** change in lines of code (LOC) is described as a surprisingly useful sloppiness signal, with the warning that optimizing directly for LOC would trigger Goodhart's law.

The article then introduces two measures from SlopCodeBench:

- **Verbosity** = the number of source lines in the union of AST-Grep-flagged lines and clone lines, divided by LOC. The paper uses 137 hand-written AST-Grep rules for patterns judged unnecessarily verbose and deduplicates lines hit by multiple rules.
- **Erosion** measures concentration of complexity in already-complex functions. For callable `f`, `mass(f) = CC(f) × sqrt(SLOC(f))`; erosion is the fraction of total mass belonging to functions with `CC(f) > 10`.

These are deliberately different signals. Verbosity targets duplication and unnecessary structure; erosion targets the accumulation of branching and size in a few functions. Neither is a complete measure of maintainability, taste, coupling, or correctness.

## What the linked paper actually reports

The article links version 1 of SlopCodeBench, not the later version currently shown as latest on arXiv. At the linked revision, the benchmark has 20 language-agnostic problems and 93 checkpoints, evaluated on the Python track across 11 models. The agent receives an external specification and its previous workspace at each checkpoint; the conversation context, installed packages, shell history, and session state do not carry over. The workspace does. Tests are hidden and interact through a subprocess or served API, so internal interfaces and architecture are not prescribed.

The paper reports:

- No run solves a complete problem end-to-end: its strict criterion requires every checkpoint and regression test to pass. This is the precise meaning behind the article's shorthand “0% pass rate”; it does **not** mean that no individual checkpoint ever passed.
- The highest strict checkpoint solve rate is 17.2% for Opus 4.6. Erosion increases over problem progress in 80% of trajectories, and verbosity in 89.8%.
- Across the reported snapshots, agent code averages **0.33 ± 0.10** verbosity and **0.68 ± 0.20** erosion. The 48-repository maintained-human panel averages **0.15 ± 0.06** and **0.31 ± 0.17**, respectively.
- The benchmark's `anti_slop` and `plan_first` prompts improve the starting quality of some trajectories, but the paper reports that degradation slopes remain similar. Cleaner code did not produce a consistent pass-rate improvement in that experiment and could cost more.

The paper's design makes a useful failure mode visible: a feature can pass the current checkpoint while its implementation creates future architectural work. A `code_search` example hardcodes early rule kinds, then faces pressure from later language and AST requirements. The benchmark carries that implementation forward instead of replacing it with a reference solution, preserving the cost of the earlier decision.

## Evidence boundaries

This is stronger evidence than an anecdotal “agents write bloated code” claim, but it is not a universal slop meter or a production defect study.

- The measures are engineered operationalizations. The AST-Grep rules, clone detector, cyclomatic-complexity threshold, callable extraction, and SLOC conventions all affect the result. A score is meaningful only with those conventions and a comparable code population.
- The human comparison is a calibration panel, not a matched human solution to the same specifications. Repository age, domain, size, architecture, and development process differ from the benchmark tasks. The paper itself does not establish that a 0.68 erosion score causes a particular maintenance cost.
- The benchmark evaluates Python implementations despite language-agnostic task design. Its hidden tests and problem construction are useful controls, but they are still a synthetic evaluation setting rather than a random sample of software work.
- The article's broad claims about near-perfect correctness, industry practice, and code volume are rhetoric or attributed observation, not independently measured evidence in the article. The benchmark establishes a particular iterative quality gap, not the claim that coding is generally solved.
- A low score is not automatically good software. Shorter code can hide coupling, poor naming, missing validation, or compressed intent. Conversely, repetition can be an intentional boundary or a readability choice. The article's own warning about optimizing LOC applies to these metrics too.

The article also links [Bias in the Loop: Auditing LLM-as-a-Judge for Software Engineering](https://arxiv.org/html/2604.16790). That separate paper studies pairwise code judgments across generation, repair, and test-generation tasks and reports sensitivity to order and prompt cues, including changed verdicts under controlled prompt perturbations. It supports caution about judge outputs, but it does not show that every AI review is useless: accuracy can be high in some settings, and executable or human checks remain separate evidence.

## Implications for Honeycomb — candidates, not adopted changes

This source sharpens the difference between **behavioral proof** and **structural acceptability**:

| Honeycomb boundary | Candidate addition | Limit |
|---|---|---|
| Define | State any architectural or maintainability constraints that matter for the task, not only the external behavior. | Do not prescribe an architecture when the developer has intentionally left it open. |
| Execute | Keep an eye on diff size, repeated logic, complexity hotspots, and whether each extension preserves a usable separation of concerns. | LOC and static metrics are sensors or prompts for review, not automatic quality judgments. |
| Prove | For work where maintainability is part of the outcome, include a concrete structural review criterion in `proof`, alongside behavioral checks. | The developer must accept taste and design; a metric or judge cannot certify it. |
| Workflow design | Measure quality over a sequence of changes when investigating agent performance, rather than evaluating only the final artifact. | This is an evaluation method, not a required stage or metric for every task. |

The strongest transferable point is not “add an anti-slop prompt” or “gate on erosion.” It is: **passing tests and preserving a codebase are related but distinct outcomes**. Prompting can improve an initial implementation in the paper, but did not prevent later degradation. If structural quality matters, it needs an explicit owner, an observable review target, and—where useful—a calibrated sensor whose limitations are understood.

That reinforces the current workflow's human acceptance requirement and its warning that proof must establish the claimed outcome rather than a convenient substitute. It does not change `WORKFLOW.md`, select a universal metric, or justify replacing human taste with an LLM judge.
