# Idea → evidence → ship → value

**Optimize the time until a real user gets a verified benefit—not the speed at which an agent produces a plausible artifact.**

This is a default for a solo builder or a small software team using AI. It is not a promise of a particular speedup, a mandatory technology stack, or permission for unattended production changes. The numeric limits below are **starting heuristics to test**, not research-established constants.

## The operating rule

> Keep one valuable bet moving. Find the uncertainty or queue currently preventing its delivery. Take the smallest safe action that removes it. Verify the result. Repeat.

An active bet needs **one accountable human owner, one outcome, one thin slice, one next proof, and one stop condition**. Execution/integration can be delegated within that owner's authority. The same person can wear several hats; do not create a department or an agent for each step.

```text
CAPTURE → PROBE → READY → BUILD ↔ VERIFY → RELEASE → OBSERVE
             │                │             │          │
             └─ stop/reframe  └─ shrink     └─ revert   ├─ keep/expand
                                                       ├─ revise
                                                       └─ retire
```

These are states of one work item, not seven handoffs or approval meetings. Existing evidence can satisfy a gate immediately. Preauthorize routine reversible execution and automate deterministic gates within explicit limits; reserve human decisions for product judgment, material risk, and actions not already authorized. A trivial fix does not need a discovery workshop. A prototype can be the probe; it is not automatically production code.

**Three things must remain distinct:**
- **Built:** the implementation passes appropriate checks.
- **Shipped:** the intended cohort can use it, with operational checks and an owner.
- **Validated:** the predeclared outcome has credible supporting evidence.

A deployment is not necessarily a release; a release is not necessarily a benefit.

## 1. Capture the bet, not the feature list

From competing ideas, first honor real incidents and obligations; then shortlist the few with the strongest evidence of meaningful benefit or costly delay. Compare plausible benefit, uncertainty, full lifecycle cost, and the cheapest next proof against doing nothing. Use ranges and judgment, not precise scores built from guesses.

Answer the first section of a [ship card](templates/ship-card.md) only to the depth needed for the next investment decision. This is a **logical record**: an existing issue with these answers is enough; no duplicate document is required. Record:

- **User and situation:** who encounters which recurring difficulty, and when?
- **Observed problem:** a recent example, current workaround, and baseline if known. Label guesses.
- **Desired change:** one observable user or business outcome, measured over a defined window.
- **Route to users:** the first reachable cohort, invitation/onboarding route, and feedback owner.
- **Appetite and boundaries:** maximum discretionary time/cost worth risking, explicit non-goals, and unacceptable harm. Reserve capacity for safe shutdown, support, refunds, or data obligations before creating exposure.

Example: “Finance operators need a correct monthly export without spending 20 minutes repairing it” is actionable. “Build an AI finance dashboard” is not yet a bet.

Before writing software, ask whether deletion, clearer instructions, configuration, an existing tool, or a manual service solves the problem more cheaply. Include adoption, migration, security, and ongoing support in that comparison. Reuse is not free merely because the license is free.

**Decision:** pursue, park with a reason/revisit trigger, or decline. Do not maintain an endlessly groomed graveyard of speculative features.

## 2. Probe the assumption that could kill the bet

Ask what is least known and most consequential:

| Uncertainty | Smallest useful proof | What it does **not** prove |
|---|---|---|
| Is the problem worth solving? | Observe the current task; inspect a real workaround, support case, or cost | That every user has the same problem |
| Will people adopt/pay? | Offer a bounded pilot or real purchase at stated terms; record actual response | That compliments or a waitlist equal demand |
| Can they use it? | Watch a representative user attempt the task on a sketch/prototype without coaching | Production correctness or broad accessibility |
| Can we build/integrate it? | A disposable spike against the actual API/data shape in a safe environment | That a happy-path demo is reliable |
| Can we operate it responsibly? | Check permissions, costs, data handling, legal constraints, deployment and recovery | That a model-generated checklist is an expert sign-off |

Choose **one next experiment**, with a decision threshold and expiry **before** seeing its result. Use the cheapest fidelity that can change the decision. Do not run every row by ritual. Obtain required consent/authorization and minimize data collection; discovery does not bypass privacy or external-action boundaries.

If the risk is low and the slice itself is cheaper than a separate study, release that slice to a consenting small cohort as the experiment. If the downside is high, obtain stronger evidence first. User recruitment lead time is real work: start it early, not after the code is finished.

**Exit:** evidence supports the next bounded investment; or revise/stop. An inconclusive result remains inconclusive. A killed bad idea is a good decision, but do not book its hypothetical avoided cost as realized customer value.

## 3. Make one thin slice ready

A product slice is **one complete user journey through the necessary layers**, not “all the database,” “all the frontend,” or a pile of infrastructure with nobody able to use it. Necessary enabling increments and maintenance are allowed within a bounded parent bet or documented obligation; verify the control/dependency they deliver without inventing immediate user value.

Specify on the same card:

1. **Acceptance examples:** inputs, observable result, and relevant failure/abuse behavior. Include a real or sanitized representative fixture. The owner approves what correctness means.
2. **Non-goals and claim boundary:** excluded users, inputs, conditions, and capabilities; preserve essential security, accessibility, and data integrity. Validation will apply only inside the tested boundary.
3. **Change boundary:** relevant modules, existing patterns, integration contracts, dependencies, and one writer/integrator.
4. **Verification:** exact commands/manual checks, the test environment, and an independent source of expected results.
5. **Release and learning:** destination/cohort, permissions, deploy/recovery route, success signal, guardrails, and observation date.

Read the relevant code and run the current checks **before** changing it. Record pre-existing failures instead of hiding them. For a greenfield project, prove the smallest deployable walking skeleton early—using non-sensitive data—and exercise its recovery path. This discovers missing credentials, hosting constraints, and deployment problems before most of the implementation exists.

For ordinary reversible work, start with a slice that can be built, reviewed, and released within roughly one working day. If it cannot, find a narrower user/cohort/input range or an independently useful first step. Do not meet the limit by omitting necessary assurance. A large migration may need several compatible increments and a longer lead time.

**Ready gate:** the builder can explain what to change, how to tell it worked, who will use it, and how to stop or recover. No invented requirements or unresolved critical access dependency.

## 4. Build with bounded AI assistance

Start with **one builder**. Use AI for concrete, verifiable work: navigating an unfamiliar module, proposing a small patch, translating an approved contract into tests, reproducing an error, or researching a bounded question.

When delegating, give it a [task packet](templates/agent-task.md): outcome, relevant paths and baseline revision, acceptance examples, scope, allowed actions, commands, output format, and escalation conditions. A short prompt linking an adequate issue can suffice. No delegation means no packet. Link to durable context; do not paste the entire repository or a transcript of obsolete decisions.

Enforce consequential boundaries with available sandboxing, least-privilege credentials, scoped tool access, and protected release controls—not prompts alone. Do not provide production secrets to a builder that does not need them. Use existing controls rather than building an orchestration platform first.

Work in short loops:

```text
read relevant context → demonstrate expected/failing behavior → smallest change
→ run targeted checks → inspect the diff → integrate → repeat
```

Keep the main branch releasable; integrate small verified changes rather than letting long-lived branches accumulate. Existing protected-branch/review policy still applies. An unfinished capability can remain disabled behind a temporary flag; the flag needs an owner and removal condition.

**Stop the loop when:**
- a required assumption turns out false;
- the change crosses the approved scope or risk class;
- the diagnostic budget is being consumed without new discriminating evidence;
- review cannot keep up with generated changes;
- the agreed time/cost appetite is reached.

Then obtain new evidence, reduce scope, switch approach/tool, ask the owner, or stop discretionary investment. **Stopping does not cancel existing customer, security, cleanup, or recovery obligations.** Execute the funded safe disposition. Never make “try harder with more agents” the automatic response.

### When parallel agents actually help

Use another agent only when it removes a current constraint and its output can be checked cheaply. Good candidates: read-only evidence gathering, independent failure-case design, or an isolated implementation behind an agreed interface.

A rough decision test:

```text
parallel time ≈ setup + longest independent task + integration + verification
```

Compare that with doing the same accepted work serially; also count human attention, token cost, contention, and rework. This is a planning heuristic, not a speedup guarantee.

**Default topology:** one owner/integrator, one builder, and a temporary independent reviewer when warranted. Start with no more than two concurrent agent assignments per human owner. Raise that only after measured end-to-end gains without a growing review queue.

- One writer per shared file set. In a shared checkout, other agents are read-only unless disjoint ownership is explicit. Avoid concurrent Git mutations. Tests can also mutate files, databases, ports, and services: use an isolated test environment or explicitly approve those side effects; never infer production-test permission from “review.”
- Isolated branches/worktrees can separate writers when intentionally set up; they do not eliminate interface or merge conflicts.
- Define interfaces and integration order before parallel implementation.
- A reviewer checks the contract and actual behavior, not whether the builder's explanation sounds convincing. Another model is a useful check, not an independent ground truth.
- No agent creates more agents, deploys, spends beyond the allowance, accesses secrets, or changes permissions merely because it can.

See [Herdr coordination](HERDR.md) for the optional terminal mechanics. The workflow also works without a multiplexer.

## 5. Verify the result, not the completion message

The builder supplies a small diff plus evidence: revision, commands, exit/results, environment, and limitations. A green checkmark or “done” message is not proof.

Verification is proportional to risk, but always connects behavior to the accepted contract:

- **Correctness:** exercise the real user path and the consequential failure paths. For a bug, show that the regression test detects the original defect where practical.
- **Independence:** derive expected results from the contract, domain rules, trusted fixtures, or observed baseline—not merely from the implementation under test. Also challenge whether the contract represents the intended users; technical correctness cannot establish demand or representativeness. Consequential domain contracts need a competent challenger. Do not weaken an assertion just to turn it green.
- **Integration:** rerun relevant checks on the combined revision. Two individually passing branches can fail together.
- **User experience:** for UI work, use the actual supported interface; check keyboard access, comprehensible errors, and appropriate loading/empty states. A screenshot alone cannot verify behavior.
- **Safety and operability:** check changed authorization/data boundaries, secrets, dependencies, logging, migrations, and rollback/containment as applicable.
- **Scope:** remove accidental refactors and speculative features; explain new complexity.

Automate cheap, deterministic checks. Keep a fast local feedback path; run slower required suites before release or in CI. Do not build a custom test platform before a simple reproducible command will do.

**Exit:** an accountable owner accepts evidence for the approved risk level; there are no unresolved release-blocking defects. Record residual risk explicitly. If you cannot verify it within the appetite, shrink it—do not relabel it safe.

## 6. Release deliberately, with distribution included

Before exposure, the card must identify:

- the exact verified revision/artifact and authorized release mechanism;
- the initial cohort and how those users will find and use the change;
- the smoke check and user-visible health signals;
- the owner watching those signals and able to act;
- a stop threshold and a rehearsed rollback, disable, or containment route;
- the outcome observation window and follow-up appointment.

A small reversible change may need only the normal deployment path, a smoke test, and a known previous version. A larger change may need a staged rollout, representative traffic, specialist approval, and compatibility tests. Do not impose a universal “5% for 10 minutes” rule: low traffic and delayed jobs can make that meaningless. A feature flag is not a remedy for destructive writes already performed.

Prefer backward-compatible data changes: expand first, migrate safely, verify, and remove old behavior later. **User cohort size and data blast radius are separate.** A small rollout can still damage a shared database. Application rollback does not necessarily restore data.

Destructive execution requires tested recovery within declared acceptable data-loss and recovery-time limits, or explicit competent authorization of necessary irreversibility with containment evidence (for example, required deletion). Check concurrent writers, old readers/workers, delayed jobs, partial failure, interruption and reconciliation. Declare operation-specific completion criteria: deletion may require identity/shared-record scope, replicas/caches/backups, and prevention of resurrection after restore—not just “the job succeeded.” Do not require restoring data that must remain deleted. Make destructive cleanup a separate gate after compatibility evidence. If these conditions are unmet, hold the destructive step; “only one tenant” is not a substitute.

After deployment, verify the **deployed** path and telemetry. Send the promised invitation, onboarding help, or release note. A feature nobody can reach is unfinished delivery.

**Release gate:** the intended cohort has working access, the deployed acceptance/smoke path and required health checks pass, and the operational owner has accepted monitoring/recovery responsibility. Record the release time; do not yet claim product success.

## 7. Observe, decide, and improve the constraint

At the prebooked checkpoint, inspect behavior against the original outcome and guardrails:

- **Keep/expand:** useful behavior is supported by evidence and harm/cost is acceptable.
- **Revise:** identify the limiting assumption; fund one more bounded experiment only if justified.
- **Retire:** remove or disable the failed experiment and unnecessary flag/infrastructure.
- **Inconclusive:** name the missing evidence and set a justified next deadline—or stop. Do not quietly promote it to success.

For tiny populations, direct observation of real tasks can be more honest than a fake-significant A/B test. State every validation claim as **claim + cohort + conditions + horizon**. Distinguish a pilot usability result from retention or commercial validation. Expansion beyond that boundary requires another decision; it does not inherit proof. Higher-risk or broad product claims require stronger evidence and appropriate analysis.

**Benefit is not proof of acceleration.** An execution trial compares the same accepted user outcome/cohort and assurance bar; an allocation trial compares realized outcomes under comparable opportunity pools, time/budgets, and horizons while allowing choices to differ. A simpler implementation can be faster; reducing the promised user outcome is not like-for-like delivery. Declare the baseline, full cost boundary, and harm limits; preserve parent timestamps, amendments, failed/parked attempts, and support costs. A biased before/after comparison remains a suggestive local signal. See the two [measurement questions](MEASUREMENT.md#choose-the-question-execution-or-allocation).

Review the flow briefly each week. Ask: **Where did the oldest valuable item wait? What caused rework? Which single change would remove the most delay?** Choose one improvement and compare subsequent results. [Measurement](MEASUREMENT.md) explains the clocks and guardrails.

## Flow rules that prevent the workflow becoming overhead

- **One active delivery slice per owner by default.** Discovery and read-only verification can support it; ten half-finished features cannot.
- **Review before starting more implementation.** A full review queue is a stop signal for generation, not a reason to launch another builder. Apply the shared-capacity policy below; per-builder WIP limits alone cannot protect one overloaded reviewer.
- **Count blocked work.** Mark blocker, owner, next action, and escalation time. Waiting does not disappear from lead time. If a dependency truly prevents progress, deliberately park the item and record the substitution; do not create hidden WIP.
- **Separate delivery WIP, decision queues, and scheduled observations.** A monthly outcome window need not freeze implementation. Admit new work only if named owners have capacity for upcoming observation, review, and support duties. Keep due dates visible; service overdue decisions before new discretionary starts. Parking never deletes an obligation. Incidents and mandatory work can preempt a slice explicitly, without resetting its clock.
- **Work backward from user benefit.** If the current constraint is distribution, recruitment, approval, or diagnosis, that is the work. Code generation can be idle.
- **Do not restart the record at each gate.** One logical record evolves; tests, CI logs, previews, and dashboards are linked evidence, not copied into five status reports. For multiple slices/releases, keep linked child records and an append-only revision/exposure/decision history. Preserve the parent outcome, original cohort/window, and amendments. Slice closure is not the parent outcome decision.
- **Delete process that cannot explain which failure it prevents or decision it improves.** Do not remove statutory, contractual, or necessary safety controls in the name of speed.

### Make the shared constraint a serviced queue

For review, approval, user testing, or any scarce shared service:

1. **Name its owner and protect real capacity.** Reserve review/test windows and agree a response window. Do not assume a busy person becomes available because an agent finishes.
2. **Admit work against that capacity.** Set a shared queue cap from observed service time and available attention, leaving room for variability/rework. If service time is unknown, start with one ready item and learn. Before launching more builders, check that their outputs have a credible finishing slot. If none exists, improve the existing evidence, help drain the queue, or resolve capacity with the accountable lead.
3. **Pull deliberately.** Urgent safety/obligations first; otherwise follow explicit value/cost-of-delay priorities, oldest first within a priority. Expedites require an explicit tradeoff. Poorly prepared packets return to their owner with the missing evidence named; their preparation cost does not vanish from accounting.
4. **Act on age, not just count.** If the agreed response window is missed, stop new discretionary arrivals. The service owner removes competing work, assigns a qualified alternate, or explicitly defers/re-scopes the bet and gives a new decision time. Never auto-approve because a deadline elapsed.

For example, four builders can each obey WIP=1 and still overload a reviewer. If a reviewer has 60 minutes/day and packets take about 20 minutes, the nominal capacity is only three/day **before** variability and repair—not four concurrent agents' worth of unlimited output. These are illustrative numbers, not targets. If qualified capacity cannot be obtained, that constraint remains real; a swarm does not remove it.

## Risk routing

The accountable owner assigns risk **at capture** using consequences, data sensitivity, reversibility, and blast radius—not patch size. Reassess when scope or evidence changes; the highest applicable consequence governs. Unresolved disagreement blocks the disputed exposure and goes to the competent domain/security/operational authority. A solo owner lacking that expertise must obtain review, reduce capability, or not release. A copy edit to consent terms is not automatically low risk.

**Risk and authorization are different.** Risk determines assurance; authorization determines which actor may do which action in which environment and limits. Standing permission can cover routine local work or an established automated release path. New approval is required for actions outside those limits—not for every repetition inside them. Credentials and passing tests do not grant authority.

| Lane | Examples | Required adaptation |
|---|---|---|
| Tiny/reversible | Copy fix, local utility, well-understood low-impact bug | Collapse the card to outcome, acceptance, checks, recovery, result. Reuse existing evidence; no mandatory second agent. |
| Ordinary product work | Reversible feature using established architecture | Use the main loop and a small initial cohort. |
| High consequence | Payments, permissions, sensitive data, destructive migration, safety-critical or regulated behavior | Obtain accountable domain/security/compliance review; define threat/failure models, audit evidence, compatibility and recovery or authorized-containment evidence. Fast drafting never substitutes for assurance. |
| Maintenance/obligation | Dependency support expiry, certificate rotation, restore drill, required data retention/deletion | Use documented exposure, obligation, deadline, or reliability objective instead of a demand hypothesis. Verify the required control; apply the appropriate consequence tier too. Do not claim hypothetical avoided incidents as realized value. |
| Incident/security emergency | Active outage or exploitation | Contain/restore first under the incident process. Record authorization and timeline; follow with regression checks and learning. Do not wait for demand discovery. |

**Do less speculative work. Shorten feedback. Finish the whole path. Measure what survived contact with users.**
