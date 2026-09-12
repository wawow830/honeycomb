# Review record and remaining uncertainty

## What was reviewed

Two AI reviewers were used sequentially in one helper pane:

1. **Research/adversarial reviewer:** independently gathered evidence, challenged the first design, audited measurement, and walked through eight failure scenarios.
2. **Fresh-context usability reviewer:** began from `README.md`, did not read prior reviews or the work log, and compared the design with a strong simple baseline: **one issue, one builder, tests, deploy, user feedback**.

The reviewers did not edit repository files. Findings were evaluated rather than accepted automatically. Primary claims and calculations were checked separately. Different sessions reduce shared conversational assumptions; they do **not** establish independent ground truth or replace a competent human/domain review.

All scenario results below are **tabletop policy checks**, not executed product, security, migration, or user tests.

## Material findings and resulting changes

| Challenge | Final design response |
|---|---|
| A one-tenant rollout can still corrupt a shared database | Separate user cohort from data/system blast radius; gate destructive execution and cleanup independently |
| A restored snapshot may lose legitimate intervening writes or take too long | Declare acceptable loss/time and test recovery against those limits, not merely “restore worked” |
| Legally required deletion cannot always have a rollback | Allow competent authorization of necessary irreversibility, with containment and operation-specific completion evidence; address shared ownership, replicas/backups and resurrection as applicable |
| The investment budget ends but users still depend on the feature | Protect safe-disposition capacity; cancellation does not cancel customer, security, support, or data obligations |
| Maintenance has no demand-validation story | Accept a documented obligation/exposure/control objective without inventing immediate customer value |
| A months-long outcome window appears to freeze delivery | Separate implementation WIP, decision queues, scheduled observations, and support capacity |
| Daily releases overwrite one experiment's history | Keep parent/child links and append-only revisions, exposure, thresholds, decisions and follow-up |
| A correct fixture does not represent all intended users | Scope every validation claim to cohort, conditions and horizon; challenge the domain contract separately from implementation |
| “Read-only reviewer” runs tests that mutate a shared database | Require isolated test targets or explicitly approved side effects, plus exact tested revisions |
| A lower completed-item median hides more stalled work | Compare eligible cohorts at equal follow-up; retain accepted/total, abandoned and pending counts |
| New work looks cheap because old work has months of support costs | Match follow-up cutoffs and track outstanding obligations; keep shared costs once, not zero or twice |
| Like-for-like tasks exclude the benefit of choosing different work | Separate execution-efficiency trials from allocation-effectiveness trials; rejected ideas receive no hypothetical output credit |

## Cold-reader challenge: does this beat the simple baseline?

The fresh reviewer found the initial bottleneck rule incomplete: **“stop generating” prevents a larger review queue but does not give the reviewer capacity.**

The revised [shared-service policy](WORKFLOW.md#make-the-shared-constraint-a-serviced-queue) adds an owner, protected capacity, a shared admission cap, pull priority, a response window, and an action when queue age exceeds it. The policy cannot conjure expertise or attention; the responsible person must actually reserve or obtain that capacity.

The reviewer also identified confusing risk/permission language and duplicated card fields. The final design distinguishes **standing authorization** from actions requiring **new approval**; inherited owner/outcome/cohort/permission fields are not rewritten at each gate.

Follow-up review found these identified policy gaps addressed and no remaining blocker to a **minimal adoption trial**. This was not a claim of demonstrated acceleration.

## Scenario checks

| Scenario | Expected handling in the reviewed design |
|---|---|
| Empty repository, no credible problem or users | Find/observe a reachable user and test the bet; no automatic scaffolding |
| Tiny reversible copy fix | Existing issue, acceptance, checks, authorized release/recovery, result; no full card or second agent |
| Certificate expires tonight | Explicit obligation preempts discretionary work; preserve interrupted timestamps |
| Three-month retention result, daily releases | Continue only within follow-up/support capacity; retain cohort/window and exposure history |
| Destructive migration with delayed old workers | Hold destructive cleanup until relevant compatibility/recovery evidence exists |
| Required irreversible deletion | Obtain competent authority and scoped completion/containment evidence; do not demand restoration of data that must stay deleted |
| Two agents pass separately, combined revision fails | Integration failure blocks exposure regardless of earlier agent reports |
| Four of ten attempts finish quickly; six remain pending | Report the whole cohort; completed median alone cannot establish improvement |
| Eight agents affordable, reviewer overloaded | Stop new arrivals and service the actual constraint, not the available token budget |
| Routine action preauthorized, production action outside limits | Execute the former within bounds; obtain new authority for the latter |

The [worked export example](EXAMPLE.md) deliberately includes an authorization defect and a failed user-outcome threshold. “Plausible patch,” “tests pass,” and “some users improved” cannot quietly become “the experiment met its target.”

## Process deliberately removed or not added

- No application, dashboard, agent scheduler, workflow engine, or new CI platform was built to demonstrate activity.
- No mandatory discovery session, second agent, or delegation packet for a trivial fix.
- No duplicated “start tomorrow” section, fixed-minute capture ceremony, or universal retry count.
- No requirement to read every appendix before using the minimal routine.
- No fictional value points, universal AI multiplier, or unsupported statistical certainty.
- A suggestion to bypass the prescribed Herdr output-retrieval fallback was **not** adopted: the supplied operating skill requires trying terminal retrieval first.

## What remains unproven

The repository did not supply a product, market, users, operating environment, or baseline. This design cannot supply those facts. It also cannot certify a particular recovery mechanism, deletion operation, test suite, or deployment.

The main adoption risk is adding administration faster than it removes uncertainty and waiting. Start with the compact routine and one constraint-specific intervention. Charge reading/setup/maintenance effort to the trial. Retain the intervention only if the [measurement protocol](MEASUREMENT.md) supports its value under the actual cost and harm constraints.

Documentation consistency, reachable citations, and correct illustrative arithmetic are useful checks—but they are not user value or a shipped software result. See [the work log](WORKLOG.md) for session validation and timing.
