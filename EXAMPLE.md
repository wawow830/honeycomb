# Worked example: a useful export, not a reporting platform

**Fictional tabletop exercise.** The users, times, costs, code paths, and results below are invented to exercise the workflow. No application was built, deployed, or tested in this repository. They are not evidence of acceleration.

## Starting idea

> “Add an AI reporting dashboard to our project-management app.”

That proposal is too broad to delegate. The builder would otherwise have to invent the audience, analytics model, interface, and definition of done.

Assume an existing app already has projects, task records, authenticated memberships, a supported CSV library, CI, and a normal deployment/recovery path. A product owner has access to three project managers. Those conditions matter: this is not a claim that a brand-new company can ship the same thing on the same schedule.

## 1. Turn the proposal into a bet

The owner watches the managers prepare weekly updates. They copy completed tasks into a spreadsheet, then correct omissions and formatting. Recent task durations are 14–16 minutes. The expensive step is extraction, not analysis.

**Bet:** authorized project managers can get a correct list of last week's completed tasks into their existing spreadsheet in no more than three minutes, without coaching.

**First cohort:** these three consenting managers, using their own authorized projects.

**Decision threshold:** at the next weekly reporting cycle, all three independently finish in at most three minutes with correct rows. This is a bounded pilot success criterion, not a powered statistical test or a market-demand claim.

**Hard guardrails:** no unauthorized records, no silently missing supported rows, no executable spreadsheet formulas from untrusted task text, and no logging of exported content.

**Appetite:** up to one working day of elapsed delivery time, six human hours, and $10 of model/tool spend. These are example local choices. Before inviting users, the owner also reserves time to disable the feature, communicate failure, and help them return to the existing export workaround; that responsibility survives the experiment's deadline.

**No-build check:** the current app can copy individual tasks but cannot export the complete filtered list. An existing CSV dependency can handle serialization; a new reporting framework would add adoption and maintenance cost without solving the immediate constraint.

**Non-goals:** AI summaries, charts, scheduling, arbitrary filters, bulk cross-project export, and replacing the managers' spreadsheets.

The proposed investment has already become much smaller. This is good scope selection, **not evidence that an equivalent dashboard was delivered faster**.

## 2. Test the uncertain part first

The riskiest initial assumption is that a plain file solves the real job.

The owner prepares a representative, authorized sample through the existing administrative process. A manager uses it in the actual spreadsheet workflow. They do not need a dashboard; they need a consistent date boundary and a stable column order.

**Decision:** build the narrow export. If the sample had not solved the job, the owner would have revised the contract or stopped before building the UI.

The owner explicitly checks permission and privacy implications. A small export can expose many records; risk is not measured in lines of code. The existing membership rules are the domain authority, and someone competent to challenge them reviews the access contract.

## 3. Make the slice ready

**Journey:** open an authorized project → choose “Export last week's completed tasks” → download CSV → open it in the supported spreadsheet application.

**Claim boundary:** the three pilot managers; one project at a time; the supported timezone rule and spreadsheet application; at most 1,000 matching rows. Over-limit requests must clearly reject, never silently truncate. A larger account or another spreadsheet is outside the initial claim.

**Acceptance examples:**

| Case | Expected result / source of truth |
|---|---|
| Representative project | Exact task IDs and column order match a domain-approved fixture |
| Week boundary | Inclusion/exclusion matches the predeclared timezone and date rule |
| Unauthorized project ID | Denied by server-side authorization; no export data returned |
| Quotes, commas, line breaks, non-ASCII text | Correctly preserved using the supported CSV implementation |
| Formula-like task title | Safe behavior in the supported spreadsheet, checked against the agreed threat model |
| No matching tasks | Understandable empty result, according to the approved contract |
| More than 1,000 matching tasks | Explicit supported-limit error; no misleading partial report |
| Keyboard-only operation | The export action and relevant error message are usable |

The oracle is not “whatever the new query returns.” The fixture's expected IDs are reviewed independently of that query. CSV quoting alone is not assumed to prevent spreadsheet formula execution.

**Ownership:** one agent implements the existing export route and UI action. The owner remains integrator. A temporary read-only reviewer checks authorization, date boundaries, and CSV hazards. There is no second implementation agent competing over the same files.

**Verification commands:** in a real card, name the actual project's targeted test, type/lint, build, and integration commands. Here they are deliberately not fabricated as runnable instructions. Required manual checks use the actual supported browser and spreadsheet. Capture the baseline revision and any already-failing checks first.

**Release preparation:** confirm that the current normal deploy path, previous artifact, existing feature-flag facility, and smoke test work. No new platform, queue, or analytics service is justified for this slice.

## 4. Execute and catch a plausible defect

The builder writes a small patch and passes the happy-path fixture. The reviewer tries a project ID belonging to another account directly against the endpoint.

**Failure:** the UI hides the export action, but the route does not enforce the membership boundary.

This blocks release. The owner does not call it a non-goal, accept “only trusted pilot users,” or let the agent weaken the test. The builder adds server-side enforcement and a regression test. The reviewer checks the corrected path; the owner reruns relevant tests on the combined revision.

The time spent discovering and repairing this defect belongs in the task's effort and rework record. It is not removed to improve the AI speedup number. This does not prove the reviewer was net-positive in every possible task; it shows why the access check matters in this one.

## 5. Release and make the change reachable

The owner approves the verified artifact under the existing release policy. Enable it for the named cohort only. Run the deployed authorized and unauthorized smoke paths; verify health events without collecting exported content.

**Stop conditions:** any confirmed unauthorized disclosure or incorrect supported row set triggers immediate containment and the incident response appropriate to the exposure; availability regression triggers disable/recovery under the normal service policy. A flag can prevent further downloads; it cannot undo a file already disclosed. Privacy response and affected-user communication may still be required.

Send the three managers an invitation with the exact action, supported limits, and feedback route. Schedule observation during the next weekly reporting cycle—not ten minutes after deployment when nobody has the relevant job to do.

Record **released**, not **validated**.

## 6. Observe an honestly disappointing result

At the scheduled cycle, two managers finish correctly in under three minutes. The third takes six minutes because the date label is ambiguous. No technical errors occur, and the file contents match the agreed period.

**Decision:** the predeclared all-three criterion failed. This is not full pilot success, even though the code passed and average task time improved. The owner funds a small label/preview clarification, then checks the ambiguous step again at an appropriate next opportunity. Do not replace “all three” with “two of three” after seeing the data.

The released implementation can remain available to the existing cohort if safe and useful, but broad expansion is not automatically justified. If the extra iteration is not worth its cost, stop discretionary work and honor support/cleanup commitments.

If a later observation passes, the supported claim is limited: “These pilot users completed this specified reporting job under these conditions.” It still does not prove long-term retention, demand for a reporting platform, or benefit for high-volume accounts.

## 7. What would count as acceleration here?

The card retains:

- initial idea capture and funded-bet timestamps;
- the reduction from “dashboard” to “export” and its reason;
- implementation/review/rework effort, including the authorization defect;
- deployment and actual user-exposure times;
- the waiting period until the real weekly task;
- the failed initial outcome and the cost of clarification/support;
- the final decision, evidence boundary, and outstanding obligations.

Without a comparable baseline, **no numerical acceleration claim is justified**. We can say the process avoided building unrequested functionality and caught an unsafe endpoint in this fictional exercise. In a real execution pilot, compare similar accepted outcomes under the same quality/cost/observation boundaries. To test better idea/scope selection, instead compare realized native outcomes across comparable opportunity pools and investment budgets, retaining rejected, unfinished, and failed attempts. Neither test can book a hypothetical unbuilt dashboard as a measured saving.

## If the circumstances change

| Situation | Correct next move |
|---|---|
| No manager can be reached | Resolve access to real users or reconsider the bet; do not invent AI personas as validation |
| The existing product already exports exactly this | Teach/configure the existing path; no feature implementation needed |
| The change requires deleting a shared legacy dataset | Route to the destructive-change gate; verify recovery/irreversibility and delayed writers, regardless of pilot size |
| Reviewer unavailable and authorization cannot be competently checked | Hold exposure, seek expertise, or remove the risky capability—not rubber-stamp it |
| Monthly rather than weekly reporting | Schedule the longer observation and reserve follow-up capacity; other work may proceed without erasing this pending decision |
| Urgent certificate expiry interrupts the slice | Preempt explicitly for the obligation, retain the slice's timestamps, and revise its plan |

**The acceleration mechanism is not a magical prompt. It is less speculation, a smaller coherent change, earlier verification of consequential assumptions, less handoff waiting, and a real decision after release.**
