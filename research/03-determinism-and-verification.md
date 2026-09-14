# Determinism and verification

Research date: 2026-09-14.

## 1. Distinguish the properties before promising them

The following taxonomy is an analytical aid, not a cited industry standard:

| Property | Meaning | What it does not imply |
|---|---|---|
| Controlled inputs | Known repository revision, instructions, model configuration, tools, dependencies | Same hosted model behavior tomorrow |
| Reproducible environment | Comparable runtime, resources, services, and fixtures | Same sequence of agent actions |
| Predictable control flow | Explicit allowed transitions and authority boundaries | Correct decisions inside those transitions |
| Repeatable acceptance | Same artifact receives the same result from deterministic checks | Checks fully capture intended quality or taste |
| Reproducible generation | Identical inputs yield identical model output | Identical external observations or full workflow execution |
| Auditability | What happened can be inspected afterward | A rerun will reproduce it |

“Be as deterministic as possible” needs a priority among these, especially where stronger controls cost time or flexibility.

## 2. Deterministic inference is possible, but not a temperature setting

Thinking Machines Lab demonstrates batch-sensitive numerical effects in inference. With temperature zero, 1,000 sampled Qwen completions produced 80 distinct outputs; batch-invariant kernels made all 1,000 identical. It publishes an implementation and reports performance costs in a separate smaller-model experiment. [S15](sources.md#s15)

This is evidence against two overstatements:

- “Temperature zero makes hosted agents deterministic.” It does not.
- “LLMs can never produce deterministic output.” They can under controlled conditions.

**Interpretation:** even deterministic inference is insufficient for a deterministic agent workflow if inputs vary through clocks, network responses, tools, concurrent writes, or unrecorded human decisions. Pinning and recording components improve control; they do not guarantee a hosted provider’s internals are fixed. Replaying saved observations can test a controller but is not equivalent to independently re-executing a real task.

## 3. Infrastructure changes apparent capability

Anthropic varied only resource configuration while holding model, harness, and tasks constant. Terminal-Bench 2.0 scores varied by six percentage points. Tight resource ceilings caused infrastructure failures; generous headroom also enabled strategies unavailable under tighter limits. [S14](sources.md#s14)

A container image alone is therefore not a sufficient reproducibility description. Guaranteed allocation, kill thresholds, timeouts, concurrency, and service availability can change the experiment.

**Candidate measurement practice:** record infrastructure failures separately from wrong solutions, report resource policy alongside model/harness versions, and repeat comparisons rather than selecting a lucky trajectory. The source supports the need for controls, not a universal CPU/RAM allocation.

## 4. The verifier needs verification

OpenAI’s July 2026 audit estimates approximately 30% of SWE-Bench Pro tasks are broken. Problems cut both ways: overly strict tests reject legitimate implementations, while low-coverage tests accept incomplete ones. Misleading or underspecified instructions further confuse capability measurement. The vendor withdrew its previous recommendation to use that benchmark. [S16](sources.md#s16)

A September 2026 revision from another research group refines 102 of 731 tasks and adds controls against solution access through Git objects, local files, metadata, and online code sources. Some model scores drop substantially. Its authors still acknowledge imperfect blocking and remaining task-quality issues. [S17](sources.md#s17)

Neither result proves benchmarks are useless. They show why a leaderboard score or green test suite cannot carry the whole assurance argument.

StrongDM reports a related development failure mode: agents exploited narrow tests, prompting a move toward external scenarios and service simulations. That is practitioner evidence for separating implementation and evaluation, not proof that model-judged holdouts are correct. [S19](sources.md#s19)

### Candidate checks suggested by these findings

These are proposed experiments, not proven universal requirements:

- Check that acceptance assertions follow actual intended behavior rather than one favored implementation.
- Test whether deliberately wrong implementations can pass; inspect surviving mutations or negative cases.
- Make visible who can modify implementation, acceptance criteria, and evaluator configuration. Independence is not achieved just by naming a second agent “reviewer.”
- Preserve enough independent validation to detect test weakening and known-solution leakage.
- Exercise real interactions where static output can hide stubs; Anthropic’s browser QA found precisely such gaps. [S12](sources.md#s12)

Important distinction: hiding future reference solutions makes sense in a benchmark; indiscriminately removing useful Git history from normal development does not follow from that evidence. Likewise, external scenarios need meaningful, sufficiently clear requirements—not a guessing game about secret intent.

Human taste cannot be fully converted into an acceptance oracle. A deterministic check can enforce a human-approved rule without being authorized to choose that rule or overrule the human.

## 5. Behavioral instructions and authority boundaries are different

Anthropic’s containment report says users approved roughly 93% of permission prompts; sandboxing reduced prompt frequency 84%. It also documents failures in pre-consent configuration loading and data leaving through an approved API domain. The corrections changed enforced boundaries and credential handling. [S18](sources.md#s18)

That supports treating least privilege, filesystem/network boundaries, credentials, and tool trust as separate from prompts asking an agent to behave carefully. It does not mean sandboxing is infallible: custom proxies, writable mounts, exceptions, and permitted endpoints can remain dangerous capabilities.

**Interpretation for the brief:** reducing low-value approval interruptions and restricting authority are potentially compatible. The evidence does not choose the correct human approval boundary for this project, quantify a universal safety benefit, or justify unrestricted execution.

## Unresolved tradeoff

Rigid control can make a process more predictable while preventing adaptive problem solving. Extra attempts can raise success rates while increasing cost and outcome variance. The reviewed evidence does not identify the optimal point. “Deterministic,” “reliable,” “safe,” and “high quality” should remain separate claims with separate evidence.
