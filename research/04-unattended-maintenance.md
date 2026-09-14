# Case: unattended changes inside Stripe

**Work:** changes to a large existing internal codebase, including small on-call issues and migrations. **When:** February 9 and 19, 2026. **Evidence:** two first-person engineering reports by Alistair Gray. Unlike the open-source cases, Stripe’s actual PRs, harness implementation, defect data, and execution logs were not available in the inspected material. Everything about its operation below is **reported, not independently reproduced**. [Sources](sources.md#stripe)

## What “one-shot” actually means here

An engineer invokes a minion from Slack, a ticket, or another internal tool. A run collects context, changes code, executes checks, and produces a branch and prepared PR without interactive steering. The engineer inspects the result and requests review from another engineer. They can also request more agent work or finish an incomplete change manually.

“One-shot” therefore does **not** mean one model completion, no internal iteration, automatic acceptance, or guaranteed success.

The second report says over 1,300 merged PRs per week contained no human-written code. It does not publish the number attempted, the failure rate, net human time saved, escaped defects, or infrastructure costs. This is evidence of reported deployment scale—not a measured speed multiplier or unchanged quality.

## The concrete arrangement

### An inherited working environment

Each run gets an isolated EC2-based developer environment already used by human engineers. A pre-warmed pool supplies source, build/type-check caches, code-generation services, and usable test/runtime tooling. The target is readiness within ten seconds.

That startup figure depends on background provisioning. It is not the time to construct the environment from nothing, and the investment predates these agents.

Production access, real customer data, arbitrary network egress, and destructive tool actions are restricted. Within that boundary, interactive permission prompts are omitted. **No prompts is not the same as no restrictions.** The report does not publish enough detail to independently assess containment effectiveness.

### A mixture of program control and agent decisions

The harness is a customized fork of Goose. Its “blueprints” combine ordinary code steps with open-ended agent tasks:

- “Implement task” and “fix CI failures” are agent-driven.
- Running configured linters and pushing changes are ordinary programmed operations.
- Relevant linked context can be fetched before implementation begins.
- Most repository guidance is scoped by directory or file pattern instead of globally loaded.
- Agents receive selected tools, not all of the nearly 500 tools in the shared internal catalog.

The narrow determinism claim is understandable: the controller, rather than a model’s discretion, schedules required operations. That does not guarantee the operation succeeds, that the lint configuration is correct, or that rerunning the whole task yields identical code.

### A bounded repair budget

Local automatic fixes and lint checks run before expensive CI. After the first CI run, automatically fixable problems are corrected and remaining failures can go back to an agent. There are **at most two CI rounds** before the branch returns to the human.

Stripe attributes this to diminishing returns and compute/time cost. The reports do not present an experiment showing that two is optimal. The important contrast with the compiler case is deliberate: one stops and hands back incomplete work; the other keeps searching to push a capability limit.

## Applicability—and limits

**Useful when:** a request has enough context to proceed unattended and a repository already has dependable commands, usable tests, and a review destination. The general idea can apply to bugs, small features, or migrations; the reviewed report does not disclose their individual success rates.

**Requires:** maintained development environments, accessible internal knowledge, trusted tooling, meaningful access restrictions, and someone responsible for the returned change. A team without those assets cannot assume comparable setup or maintenance cost.

**Does not establish:** that developers need a custom agent framework, a centralized tool server, EC2, or Stripe’s approval policy. Its relevance is a concrete separation between **known procedural steps, uncertain implementation work, and human acceptance**. Whether that separation should take this form in a simpler setting remains a design question.
