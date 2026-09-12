# Honeycomb: idea → ship → verified value

**Acceleration means useful outcomes sooner—not more code per hour.**

The workflow: **one owner, one valuable bet, one thin slice, one next proof.**

| Step | Do | Leave with |
|---|---|---|
| **Choose** | Name the user problem or obligation; check a cheaper no-build option | Outcome, evidence, appetite, risk owner |
| **Probe** | Test the assumption most likely to kill the bet | Build, revise, or stop decision |
| **Shape** | Define one end-to-end slice and its consequential failure cases | Acceptance examples, checks, release/recovery route |
| **Build** | Use one builder; add agents only for genuinely independent work | Small integrated change, not a giant generated diff |
| **Verify** | Check actual behavior against a trusted contract | Evidence tied to the combined revision |
| **Release** | Expose safely and help the intended users reach it | Working user path, monitoring owner, containment plan |
| **Observe** | Compare real behavior with the predeclared outcome | Keep, expand, revise, retire, or explicitly inconclusive |

**When review, user access, or deployment is the bottleneck, stop generating more code and fix that constraint.**

## Use it now

1. Pick one real problem or obligation. Copy the [ship card](templates/ship-card.md)—or use your existing issue. Fill only what the next decision needs.
2. Take the smallest decisive next action; consult the relevant gate in the [operating playbook](WORKFLOW.md).
3. Use the [worked example](EXAMPLE.md) only if the steps feel abstract.
4. Record the baseline and run the [measurement pilot](MEASUREMENT.md) before claiming a speedup.

For a tiny, understood, low-risk fix, this can be enough:

```text
Owner/outcome: Who needs what corrected?
Acceptance: What observable result proves it?
Check/recovery: How will we verify and undo/contain it?
Result: What actually happened, at what elapsed time and total effort?
```

“Tiny” means low consequence and authorized—not just a small diff; use the [risk route](WORKFLOW.md#risk-routing) when unsure. No mandatory second agent, new tracker, workflow software, or approval meeting. Adopt the minimal routine, then add **one constraint-specific improvement**—not this entire documentation package as a ceremony.

## Deeper references—read when needed

- [Bounded agent task](templates/agent-task.md): scope, permissions, evidence, stop rules.
- [Herdr recipe](HERDR.md): optional coordination without agent sprawl.
- [Evidence and limitations](EVIDENCE.md): primary sources, including conflicting AI-productivity findings.
- [Review record](REVIEW.md): failure cases used to challenge the design.
- [Session work log](WORKLOG.md): the requested full-hour design window.

**Scope:** AI-assisted software work for a solo builder/small team, with explicit maintenance, incident, and high-consequence routes. This repository is a workflow design, not an application or a demonstrated productivity result. All example outcomes are fictional; real acceleration must survive a comparable delivery trial.
