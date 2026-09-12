# Measure actual acceleration

## 1. Define the numerator before optimizing the denominator

Interpret “actual productivity ÷ time” as **verified useful output per unit of time**, not activity per unit of time. More commits, prompts, tests, tokens, tickets, or agents are not inherently useful output. A task completed faster is useful only if it was worth doing and meets the same quality bar.

Keep the clocks dimensionally honest:

```text
benefit rate = verified benefit V_H / benefit-observation duration H
latency speedup = T_baseline / T_new  (same accepted outcome and clock boundaries)
```

`H` might be the first four weeks after release for both cohorts. `T` might be idea capture to the equivalent accepted release. **Do not divide benefits accumulated after release by development duration and call that an observed benefit rate.** The benefit rate tests whether the output is actually useful; latency tests how quickly you delivered it. Report both when their units differ.

Where outcomes really are comparable, useful outcomes delivered per calendar week is also a valid throughput measure; its new/baseline ratio is a rate improvement. Do not treat unequal features as interchangeable units. For the **same accepted outcome**, a latency factor above 1 indicates faster delivery only under identical clock boundaries and acceptable quality, effort, cost, and harm constraints. If the baseline is zero or the outcomes are incomparable, report differences and limitations rather than manufacturing a multiplier.

Pick a meaningful native unit when possible: correctly completed user tasks, user minutes saved on a defined job, recovered successful transactions, or incremental contribution margin. Define eligibility, correctness, cohort, baseline, and observation window. Measure the whole user job, including added setup/recovery effort within that horizon; moving work elsewhere is not a saving. Do not add unlike units or invent “value points” to make a dashboard possible.

**Important distinctions:**
- A task-success rate or retention rate is an outcome measure, not a quantity you can casually sum across features.
- Estimated future value belongs in prioritization, clearly marked as an estimate—not in realized output.
- Stopping a bad idea records a useful decision. Its hypothetical saved budget is not booked as realized user value.
- Instrumentation and infrastructure may enable later value without directly producing it. Track their cost and the constraint they remove; do not force a fictional customer-impact claim.
- Benefits from overlapping releases must not be counted twice. When attribution is unclear, measure the product/cohort jointly and say so.

## 2. Keep four views, not one magic score

For routine work, reuse issue timestamps, existing checks, rough effort, and the result. The fuller ledger, matched-cost accounting, and cohort comparison below are for a workflow trial or a decision that warrants that effort—not mandatory administration for every fix.

| View | Record | Why |
|---|---|---|
| **User outcome** | One predeclared behavioral metric, baseline, result, sample/window, and evidence link | Prevents shipping irrelevant work faster |
| **Elapsed delivery** | Capture, commitment, release, and outcome-decision timestamps; current age for unfinished items | Exposes queues and does not erase delayed work |
| **Total inputs** | Human effort, model/tool spend, material running cost, and maintenance/support burden | Prevents buying apparent speed with invisible supervision or debt |
| **Quality/harm** | Release-blocking defects, rework effort, escaped failures, and relevant security/reliability/user-harm guardrails | Prevents “fast” becoming expensive or unsafe later |

Do not turn these into an employee leaderboard. Use them to decide what to change in the system.

### The clocks

- **Captured:** earliest recorded idea/problem entering consideration, even if still vague. Preserve this timestamp when shaped, split, or parked; readiness must not restart the clock. If earlier timing is unknown, say so rather than inventing it.
- **Committed:** the owner funds the bounded investigation or delivery bet. This is a decision, not the first commit to Git.
- **Released:** the stated user cohort can access the intended change; not merely a successful build or dark deployment.
- **Outcome decision:** evidence is reviewed and the bet is marked keep, revise, retire, or inconclusive. Also record when the first credible benefit was observed, if any. A faster inconclusive/stop decision is faster decision-making, not evidence of faster user benefit.

Report **capture → release** for the user's idea-to-ship experience and **commitment → outcome decision** for the funded feedback loop. Keep capture → commitment visible so prioritization delay cannot be hidden. Keep release → observation visible so you do not mistake shipping speed for learning speed. Neither is DORA's change lead time, which starts at a version-control commit and ends at production deployment.

Use timezone-qualified timestamps and wall-clock elapsed time, including queues, blocked periods, nights, and weekends. If working-time analysis is useful, show it separately. For parallel tasks, use real start/end timestamps; do not add overlapping durations to create wall-clock time.

When measuring human effort, sum actual active person-time across **everyone**: discovery, planning, prompting, waiting that requires attention, review, repair, integration, meetings, release, support, and workflow maintenance. Background machine runtime is not human effort. Human work on another card belongs to that other card; do not bill the same hour twice.

Active effort measures attention, not salary expense: if comparing monetary cost, include paid/reserved capacity and fixed costs rather than assuming idle staffing is free. Use coarse daily effort estimates if precise timers are burdensome. Keep one **shared-cost bucket** for setup, cross-feature support, or infrastructure that cannot sensibly be assigned to one card. Once a week, reconcile card effort plus shared effort to actual team person-time. Allocate shared costs once under a declared rule when comparing approaches—or compare the whole team cost rather than forcing false precision.

Compare support, rework, and running costs through **matched post-release horizons**, recording each cutoff and outstanding obligations. Six months of historical support versus one day of new-feature support is not a fair quality/cost comparison. New work with immature follow-up remains provisional.

### A minimal ledger

Use the ship card plus an existing issue tracker or a small table. No analytics integration is required to start.

```text
id | kind/risk | approach/config | captured | committed | released | outcome_decided
status | outcome evidence | human_minutes | model_cost | rework_minutes
blocker/queue | escaped_failure | observation_due
```

`rework_minutes` is a **subset** of human minutes, not extra effort to add twice. Unknown values stay unknown. Unreleased, failed, and abandoned work stays in the ledger. A timestamp missing because the event has not happened is not zero duration.

For a small sample, show each item and its age. Compare prospectively eligible cohorts at equal follow-up, reporting **accepted completions / total eligible**, abandoned and pending counts, plus task/risk mix. An unfinished item's lead time is known only to exceed its current age; do not invent a completion time or silently drop it. With enough comparable observations, add median and upper-tail completed lead time, but never adopt an intervention on that statistic alone. A lower median with more stalled work can be worse, not faster.

## 3. Measure the bottleneck before choosing a tool

For the current oldest valuable item, reconstruct its critical path:

```text
problem/user access → decision → implementation → review → release → feedback
```

Mark where it was actively worked, where it waited, and where it was redone. Assign each wall-clock interval once when making an additive breakdown; parallel work and multitasking otherwise double-count time. An approximate interview/timestamp reconstruction is enough to choose an initial improvement. Precision that costs more than the improvement is not productivity.

**Illustrative arithmetic, not observed results:** suppose a comparable delivery takes 10 hours, of which only 2 hours are coding. Making coding 5× faster changes the total to:

```text
8 hours other work/wait + 2/5 hours coding = 8.4 hours
speedup = 10/8.4 = 1.19×, not 5×
```

An added 1.6 hours of prompting, review, and repair consumes the entire gain. If instead the team can also remove 4 hours of real critical-path waiting, the total becomes 4.4 hours, or 2.27× faster than the original. The exercise identifies leverage; it does not predict that either intervention will work.

The practical diagnosis:

| Observed constraint | First intervention to try | Avoid |
|---|---|---|
| No credible problem or reachable user | Observe a real task; recruit a pilot; reconsider the bet | More scaffolding and synthetic personas |
| Repeated ambiguity/rework | Better acceptance examples and representative fixtures | Longer autonomous implementation runs |
| Review queue grows | Stop new generation; shrink changes; improve review evidence | More builders |
| Deployment/access waits dominate | Prove the existing delivery path; resolve access early | Framework rewrites |
| Runtime failures consume capacity | Reproduce and remove the leading failure cause; improve containment | More feature throughput |
| Too many costly AI retries | Use a stronger bounded approach, better context, or human implementation | Model loyalty or unlimited retries |

Little's Law (`average WIP = average throughput × average time in system`) is useful under its stable-system assumptions. It is not a guarantee that cutting a WIP limit in half doubles throughput, and should not be used to forecast one variable-sized software task.

## 4. Test this workflow rather than declaring it successful

Run a **two-week operational pilot**, extending observation when product outcomes require longer. Two weeks is a convenient initial budget, not a statistically sufficient sample by definition.

### Choose the question: execution or allocation?

**A. Execution efficiency:** hold the accepted user outcome, eligible cohort, assurance bar, and follow-up horizon comparable. Test latency, total effort/cost, quality, and the unfinished tail. “Scope” here means the promised user result—not lines of code or an unnecessarily elaborate implementation. A simpler implementation that preserves that result can genuinely be faster.

**B. Allocation effectiveness:** hold the eligible problem/opportunity pool, investment/time budget, and outcome horizon comparable; let selection and solution scope vary. Record candidates before selection, including rejected, parked, failed, and unfinished bets. This is a light decision log for a bounded trial, not a mandate to groom every speculative idea. Compare realized outcomes in a shared native unit across the whole pool, with total costs and harms—not only selected winners. If outcomes are unlike, report them separately. Not building earns no output credit; redirected capacity counts only when it produces observed benefit, and lower actual spend is a separate gain.

Where feasible, allocate independent bets to decision policies before shaping. Otherwise compare budgeted periods and label learning, changing demand/opportunity mix, and small samples as confounds. Do not force unsafe or commercially harmful randomization.

**A like-for-like task test can assess execution, but cannot establish the workflow's overall benefit from choosing better work.** The steps below are an execution-pilot default; for an allocation pilot, compare whole predeclared opportunity cohorts/budgets rather than matching away the selection mechanism.

### Before the pilot

1. Select a real product/service and a comparable task class. Declare the quality/risk bar and available human/model budget.
2. Use recent task records as a rough baseline if they exist. If not, collect a baseline now and explicitly call it preliminary. Do not invent historical estimates from how fast work “felt.”
3. Pick one intervention: for example, a ready card plus bounded single-agent execution, or an independent reviewer. Record each task's assigned approach and tool/model/configuration, agent count, and review policy before execution; log changes or unknown vendor versions honestly. Do not change model, scope policy, deployment system, and staffing together and credit one tool for the result.
4. Choose a **minimum worthwhile improvement** based on actual switching cost and need; predeclare cost and harm limits. For example, a team might require a 20% lower median comparable lead time without higher rework or spend beyond its allowance. That threshold is a local decision, not a universal recommendation.

### During the pilot

- Log every eligible attempt, including failures, abandonment, and items not finished by the deadline. Preserve the original dates when work is re-scoped. Compare completion fractions at equal follow-up; report the unfinished tail alongside completed-item timings.
- When feasible and safe, allocate comparable tasks to old/new approaches before work starts, stratifying by difficulty/risk. Do not give all the easy work to AI.
- If randomization is impractical, alternate or use a matched before/after comparison and label confounds: learning, changing task mix, model changes, staffing, and release windows.
- Do not repeat the identical task in both conditions with the same person and treat the second attempt as independent; learning contaminates the comparison.
- Check accepted quality in both conditions. “It produced a patch” is not equivalent to “it shipped safely.”
- If the experiment itself costs meaningful effort, include that effort. Never remove required safety controls to create a control group.

### At the checkpoint

Ask separately:

1. Did comparable accepted work reach users sooner?
2. Did credible user outcomes improve—or are they still pending?
3. What happened to total human effort (including shared costs), spend, review queues, escaped failures, and follow-up burden at matched observation cutoffs?
4. Was the improvement large enough to justify adopting the change?

Keep, revise, or abandon the intervention. With a tiny or biased sample, say **“promising local signal”**, not “proved 2× acceleration.” A costly incident or user harm may outweigh a speed gain; averages do not authorize violating a hard guardrail.

Extend or reject an inconclusive pilot based on the expected value of more information—not because the team has emotionally committed to the tool. If the workflow is generating more forms than decisions, collapse it.

## 5. Guard against easy ways to fake progress

- **Clock reset/history overwrite:** a large feature becomes five cards and appears fast, or daily revisions overwrite a months-long experiment. Preserve parent capture/commit times, original cohort/window, and an append-only revision/exposure/decision history. Report the parent user outcome as well as child changes; changed thresholds start a new declared test, not a retroactive success.
- **Easy-task selection:** include the eligible population, not just successful demos.
- **Output inflation:** no-op deployments and extra tests do not automatically add value.
- **Metric substitution:** more clicks may be worse if the user needs more clicks to finish. Measure completed jobs and adverse side effects.
- **Instrumentation change:** compare metric definitions and missing-event rates before trusting a jump.
- **Hidden cost transfer:** include reviewer, operator, user workaround, and support burden—not just builder effort.
- **Premature attribution:** use controls where feasible; otherwise state what other changes could explain the outcome.
- **Unobserved harm:** one quiet hour does not establish data safety, retention, or long-term maintainability. Match observation to the failure and value mechanisms.

**The strongest claim available from this repository alone is that a workflow has been designed and reviewed. Demonstrating actual acceleration still requires the pilot above.**
