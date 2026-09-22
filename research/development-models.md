# Development mechanics and candidate decision policies

A proposal under the [agreed brief](../BRIEF.md), not an agreed architecture. The research motivates the [failure cases](development-beyond-tasks.md); it does not validate this design.

“Stewardship,” “initiatives,” and “negotiation” can coexist. They become distinguishable proposals only when they change who can redirect work, what must be reconciled, and what happens when people or agents disagree.

## A common work mechanism

This mechanism supports discovery, implementation, and operation without requiring them to occur in that order. A prototype can use existing agents, versioned project records, runnable workspaces, and operational tools. It does not require permanent agent conversations or a new model capability.

### Work starts with a question or discrepancy

A request, observation, incident, or technical finding opens a work record. It contains the source, current question or intended outcome, granted authority, resource limit, and a named owner. An owner is a continuing responsibility, not necessarily one agent session. Humans and agents can originate and perform work.

A proposal without enough evidence can fund an investigation rather than an implementation. An agent-generated interpretation remains distinguishable from the observation or request it interprets. A mandate is not assumed complete: missing authority or unresolved priorities can themselves require a decision before work proceeds.

### A work owner chooses an action using inspectable inputs

The owner examines relevant source, deployed behavior, earlier decisions, original observations, and other active work. A decision record states the alternatives considered—including leaving things unchanged—the chosen action, supporting evidence, and important uncertainty. Records are for consequential choices, not every edit or command.

A person can make the choice; an agent can make it within delegated authority. An agent review receives the current sources, permitted actions, constraints, budget, and competing proposals—not just another agent's conclusion. It must expose which observations support its choice and which consequences remain untested. This is an implementable review operation, not a claim that its reasoning is reliable.

If missing information could change the choice, the owner can inspect, ask, instrument, or prototype within budget. Building may be the investigation. If needed access or authority is unavailable, the record stays unresolved rather than acquiring an invented answer. The owner can still act under explicitly permitted uncertainty; exhaustive evidence is not a prerequisite.

### Changes inherit actual state

A runnable workspace identifies its source revision, relevant configuration and schema, and the observations used to represent the deployed system. Those observations have provenance and timestamps; they are not assumed complete.

Before applying a change, an assigned integration custodian compares that basis with current source and operational observations. Known intervening code, configuration, schema, and emergency changes must be incorporated, shown irrelevant, or left as an explicit blocker. Suspected dependencies suggested by agents require examination; a dependency list is not proof of complete impact analysis.

For an emergency change made outside the ordinary source workflow, the custodian records what actually changed, reconciles the maintained configuration or source, and constructs a usable test environment before resuming affected work. Data effects may require repair or migration; rebasing a branch cannot reconcile them. Remaining discrepancies stay visible.

### Delivery includes follow-through and transfer

The work owner supplies checks suited to the claim: behavioral checks, structural inspection, representative workload results, or observations from affected people. A passing suite is not sufficient evidence for every kind of change. The integration custodian checks combined effects and release readiness; the externally granted permissions still govern deployment and other real-world actions. Owner and custodian can be the same participant where appropriate.

After a release or operational intervention, the owner compares observed consequences with the decision that justified it. Unexpected results can reopen the problem or change its interpretation. Successful recovery can close the immediate incident while leaving diagnosis or recurrence prevention open.

A finished or cancelled initiative must name who accepts remaining operating, repair, migration, and withdrawal responsibilities. Until transfer is accepted, the record retains its existing owner and unresolved obligations. Ending an agent run does not clear them; another run or person must take them up under an available budget. Assigning responsibility does not establish that it was fulfilled.

## Three policies to compare

The common mechanism deliberately does not settle who directs consequential changes. These policies can be compared with the same external permissions and resource limits. They do not grant authority the project does not possess.

| Policy | How work can change direction | How disagreement is handled | Expected cost or failure |
| --- | --- | --- | --- |
| **Project-wide steering** | A continuing project steward reviews outcome changes and reallocates work. Owners retain discretion over implementation within that direction. | The steward compares the competing evidence against current commitments and records a decision within its mandate. It can suspend intersecting work; conflicts beyond its authority remain unresolved. | Concentrated reconstruction and decision work; a mistaken interpretation can shape the whole project. |
| **Delegated outcome work** | Each initiative has an outcome envelope, budget, stop conditions, and discretion to change approach or stop without project-wide replanning. Changing the envelope requires renewed allocation. | Owners resolve overlaps where their mandates permit. An integration custodian blocks incompatible releases and routes unresolved trade-offs to the recorded authority. One initiative cannot silently redirect another. | More independent exploration, but duplicated inquiry, integration disputes, and abandoned maintenance obligations. |
| **Commitment-gated change** | Implementation can vary within accepted expectations. Changing a protected expectation requires explicit amendment by affected commitment holders or an authority already entitled to override it. | Alternatives are made concrete through examples, prototypes, or migration rehearsals. Evidence informs the decision; it cannot manufacture consent. Without authorized resolution, that amendment remains blocked. | More attention to transferred costs and conflicting interests, but representation and negotiation may dominate development. |

For example, new evidence may undermine an active direction. Under steering, it triggers project-level reconsideration. Under delegation, an owner can stop or redirect within its envelope while unrelated initiatives continue. Under commitment gating, existing protected expectations remain in force until amended—even if a replacement appears technically superior. This is an observable difference, not a different label for an agent manager.

No policy requires humans to occupy only approval roles. Investigation, design, integration, and direction-setting can each involve people, agents, or both. Real stakeholder access, legitimate authority, and judgments outside available evidence must not be silently supplied by a simulated persona.

## What remains unproven

The common mechanism may impose more record-keeping and reconciliation than it saves. The policies may fit different kinds of work or be useful in combination. None has been shown superior.

A comparison must carry the actual resulting software forward through uncertain needs, conflicting expectations, coupled changes, and recovery followed by another change. Include routine work where extra process is merely overhead. Compare with a strong existing agent setup under comparable resource limits and information access; report human investigation, steering, integration, and takeover explicitly.

The next design decision is whether these mechanics are useful enough to prototype—not which UI, database, hierarchy, or autonomy level to declare final.
