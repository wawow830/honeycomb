# Project harnesses and pstack: make verification usable, then plan with evidence

**Ingested 2026-09-15.** Three user-supplied posts, representing two author accounts. These are practitioner guidance and self-reports, not three independent development case studies. This supplement compares them with the existing research and [Honeycomb workflow](../WORKFLOW.md); it does not change that workflow.

## Sources at a glance

| Source | Date | Main contribution |
|---|---|---|
| Gaetan Semet, [Building Agentic Project Harness](https://x.com/gsemetfr/status/2077498943085117460) | July 15, 2026; article modified August 9 | Project-owned guidance, executable checks, quality gates, and maintenance |
| Lauren / @poteto, [The Complete Guide to pstack Pt. 1](https://x.com/poteto/status/2094457600259842065) | August 31, 2026 | A maintained CLI and feature map for exercising the real application |
| Lauren / @poteto, [The Complete Guide to pstack Pt. 2](https://x.com/poteto/status/2097732320606507506) | September 9, 2026 | Ground intent, investigate history, prototype alternatives, then sequence verifiable changes |

All three article bodies were read from the X pages. Structured article data supplied links, code blocks, and modification metadata. Selected linked public artifacts were inspected at pinned revisions; screenshots and private production work were not independently verified. [Full inspection register](sources.md#project-harness-and-pstack).

## 1. Semet: the project owns the controls

Semet separates the agent product's built-in harness from the project's own layer. His taxonomy, explicitly borrowed from [Harness engineering for coding agent users](https://martinfowler.com/articles/harness-engineering.html), distinguishes:

- **Guides:** context and constraints provided before an action.
- **Sensors:** observations that detect problems after an action.
- **Computational controls:** scripts, tests, linters, structural checks.
- **Inferential controls:** model-interpreted guidance and model-based review.
- **Quality gates:** points where required checks must pass before proceeding.

His concrete implementation suggestions are a short `AGENTS.md` index, progressively loaded project guidance, and one command launcher shared by humans, agents, and CI. He uses `just`; the transferable property is a canonical command interface, not that particular tool. Start with one preflight target, splitting checks by cost and scope only when the feedback loop becomes too slow. Convert important architectural rules, such as allowed module imports, into executable checks with actionable errors.

He also proposes off-cycle maintenance of guidance, documentation, dependencies, requirements, and the harness itself. Repeated session failures become inputs to a later harness-improvement pass rather than more instructions pasted into every task.

**Evidence boundary:** this is a design account, not an inspected project implementation or measured cost comparison. The article's 98% harness/2% loop split, daily token-cost figures, fixed guidance line limits, and claims about instruction retention are not established here. Runtime behavior is tool-specific; plain Markdown is not guaranteed enforcement. Polling CI status can be computational while agent-driven diagnosis and repair remain inferential.

The linked taxonomy is more cautious about behavioral correctness than a slogan like “LLM will cheat”: it explicitly says neither control type reliably catches misunderstood intent and that generated tests alone are insufficient grounds for trust. That distinction matches the [sqlite-utils reproduction](06-reproduction.md).

## 2. pstack Part 1: verification is maintained infrastructure

The central proposal is not “ask the agent to test.” Give it reusable tools that can launch, health-check, drive, observe, and clean up the actual product. A small CLI replaces repeated throwaway scripts; useful properties include structured output, descriptive errors, composable commands, discoverable help, and dry-run support for destructive operations.

Pair that CLI with a **feature map**: a scoped index of user-visible capabilities, how to reach them, how to drive them, and relevant prerequisites or traps. This describes behavior rather than merely listing source files. Authentication, seeded data, feature flags, build freshness, and runtime isolation are part of the verification environment.

The article recommends cloud agents over local worktrees for scaling, routine maintenance of the verification skill, and later automation of bug reproduction or repeated performance probes. These recommendations depend on working environments and adequate coverage; parallelism does not create either.

### What the linked artifacts actually contain

At `cursor/plugins@be432a9`, the inspected creation skill requires:

- Inspect the repository's real launch commands and existing drivers before inventing tooling.
- Use real user paths, observe side effects as well as visible output, and verify what a dry-run actually skips.
- Health-check the correct build and instance; isolate ports, profiles, and state.
- Execute the generated skill end to end on one mapped feature before delivery.
- Clean up failed attempts and successful runs without deleting the evidence.

The maintenance skill separates **documentation drift**, **harness gaps**, and **product regressions**. It limits edits to the verification directory, uses parallel read-only source inspection, and gives one coordinator ownership of live driving. It must not rewrite documentation to conceal broken product behavior. Unlike the article's daily recommendation, the inspected creation skill suggests a cadence only if requested.

The linked Atlas repository at `d5abe70` is explicitly fictional. Its README and skill say the driver scripts are intentionally omitted; the complete Git tree confirms no `control-atlas.mjs`. Its feature index and Preferences example demonstrate a documentation shape, **not a runnable verifier or evidence of production effectiveness**.

**Evidence boundary:** “2,000 PRs a month,” the later 2,462-PR figure, and “100–1000x” output are author claims, not independently measured productivity. No complete accounting of failed attempts, accepted scope, human attention, infrastructure cost, or downstream defects was inspected. More repetitions also do not establish independent samples or eliminate a shared measurement error.

## 3. pstack Part 2: resolve uncertainty before prescribing implementation

The article identifies two recurring problems: misunderstood intent and insufficient context. Its proposed responses are concrete:

1. Have the agent restate a noisy report in plain language before implementing; catch misunderstandings without prematurely imposing a diagnosis.
2. Separate **how it works** from **why it was built that way**. Inspect runtime paths and historical evidence; recall prior sessions where useful.
3. Work backward from caller experience: a tutorial, usage example, or public API sketch can expose an awkward design before implementation.
4. Compare throwaway prototypes with observable behavior instead of accepting the first design or endlessly debating an abstract plan.
5. For larger work, ground constraints, sketch competing interfaces, compare candidates, implement, and redesign when repeated evidence undermines the sketch.
6. Once the design is understood, split execution into small units with explicit proof.

The article distinguishes tutorial, how-to, reference, and explanation using Diátaxis. Its broader point is to give the agent a concrete target that a human can understand, not to require four documents for every task. Historical transcripts supply leads, not guaranteed truth about the current checkout.

### The public implementation is opinionated, not a minimal generic workflow

The inspected prototype playbook explicitly treats the prototype as a throwaway decision instrument, separate from production source. The architecture skill requires structurally distinct candidates but makes its human checkpoint **opt-in**. Its redesign guidance treats repeated workarounds as a signal requiring judgment, not proof that every cast or edge case invalidates an architecture.

The current multi-phase planning playbook requires ten live lanes on a named model, performance checks, screenshots, orchestration ticks, and a detailed plan skeleton. It starts execution only on the operator's explicit go. These are specific policies, not evidence that all tasks need that overhead. The article and inspected repository snapshot need not describe exactly the same version.

### Bounded local check: an unfilled plan passes the validator

After reading `check-plan.mjs`, this ingestion ran it against the verbatim Markdown skeleton from the same pinned planning playbook, with placeholders still unfilled:

```text
1 PR sections, 0 problems
exit_code=0
```

Reproduce from `cursor/plugins@be432a96ed36e48d05f44bf375864355f62263f9`:

```bash
python - <<'PY'
from pathlib import Path
p = Path('pstack/skills/poteto-mode/playbooks/multi-phase-plan.md').read_text()
skeleton = p.split('````markdown\n', 1)[1].split('\n````', 1)[0]
Path('/tmp/pstack-unfilled-plan.md').write_text(skeleton + '\n')
PY
node pstack/skills/poteto-mode/scripts/check-plan.mjs /tmp/pstack-unfilled-plan.md
```

The script checks headings, required phrases, lane numbering, evidence-path syntax, and similar structure. It does not establish that placeholders are resolved, evidence exists, dependencies are valid, or behavior passes. This is **not** a reproduced failure of a production run: the playbook separately instructs the agent to fill the template. It is a concrete boundary on what the automated validator proves.

## Implications for Honeycomb — candidates, not adopted changes

| Idea worth retaining | Fit or tension with the current workflow |
|---|---|
| Canonical project commands plus a real-surface driver | Makes `proof.run` useful; requires project-specific adapters, not a mandated stack or launcher |
| A small maintained feature map | Helps select reachable scenarios and evidence; can become stale duplicated documentation if not kept grounded |
| Restatement, usage sketches, bounded prototypes | Makes consequential unknowns observable during Define; prototype scope still needs approval under Honeycomb |
| Small independently verifiable changes | Supports existing decomposition; ten verification lanes per task are not justified by these sources |
| Check/build/instance provenance | Evidence must describe the version and environment actually exercised, not an agent's completion summary |
| Harness maintenance that cannot alter product behavior | A separately scoped ordinary task, not another permanent workflow stage |
| Keep taste with the developer | Demonstrate alternatives for human choice; an agent cross-judge is not human acceptance |

**Do not silently import:** cloud-only execution in place of Honeycomb's worktrees; opt-in approval in place of its required overall approval; fixed lane counts, model names, daily sweeps, or mandatory performance gates for every change. Worktrees isolate code, not running processes or data; cloud placement is a separate resource/isolation decision. Additional documents are not automatically better than Honeycomb's single task record.

The strongest synthesis is **make important behavior cheap to exercise and hard to misreport; use those observations to resolve uncertainty before scaling execution**. These sources add practical implementation ideas to findings [1, 2, 5, and 6](07-findings.md), but do not establish a speed multiplier, stack-independent verifier, or exemption from developer acceptance.
