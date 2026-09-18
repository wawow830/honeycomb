---
name: honeycomb
description: Coordinate structured agent-assisted development with Honeycomb. Use when asked to use Honeycomb or choose the next step in its task workflow.
---

# Honeycomb

Speed means less time to a verified, accepted change—not more code.
Use one workflow at every depth; scale effort with risk, not ceremony.

```text
Define → Execute → Prove → Integrate
```

You handle task bookkeeping through the shared CLI. The requester should not
need to operate it. Instructions guide your behavior; the CLI enforces its
own gates, not everything an agent can do outside it.

## Skills

Read the relevant skill before acting:

- [Define](../define/SKILL.md): agree on and create tasks; amend or close them.
- [Execute](../execute/SKILL.md): prepare a workspace, implement, and delegate.
- [Prove](../prove/SKILL.md): verify the combined outcome and record results.
- [Integrate](../integrate/SKILL.md): integrate the exact verified change.

## Setup and location

Requires Python 3.10+ and Git. Execution needs a local `main` branch with at least
one commit; integration needs Unix advisory locks (`fcntl.flock`). The repository
must have a non-bare main checkout with its Git directory at `.git`.
Separate Git directories and bare-main repositories are not supported.

Install all five skill directories together under `.agents/skills/`. Version
them and add `/.honeycomb/` to the project's `.gitignore`. Commit this setup
before execution so new task worktrees include the skills. Do not overwrite
existing project configuration or commit unrelated work.

The shared CLI stays in this skill. Resolve `scripts/honeycomb.py` relative to
this file. Run it with Python from inside the intended project or one of its
worktrees. Command examples in all five skills assume the checkout root:

```sh
python3 .agents/skills/honeycomb/scripts/honeycomb.py ready
```

The **current working directory** selects the repository, not the script's
location. Git identifies its main checkout. All worktrees share that checkout's
`.honeycomb/tasks/` and `.honeycomb/worktrees/`; no environment variables or
worktree-local copies are needed. `define` creates storage. `ready` on a fresh
project succeeds with no output and creates nothing.

## Composition and responsibility

- Store `parent`; derive children. Parents must exist and cannot be done or
  closed when adding children; no ancestor may be closed. Parent links must be
  acyclic.
- Dependencies are unique existing siblings; roots count as siblings.
  Dependencies must be acyclic. Cross-branch dependencies belong between parents,
  not their internals.
- Scope conflicts require ordering. Unclear independence means sequential work.
- Success is `open → running → done`. Either `open` or `running` can instead
  become terminal `closed`. Failed proof leaves the task running.
- Requester approves intent and requested judgments; agent implements,
  decomposes, and verifies; tooling enforces transitions and stores results.
- Humans decide taste; agents can propose and implement.

## Boundaries

Inside approved boundaries, proceed. If outcome, scope, or proof must change,
request approval, then use [Define](../define/SKILL.md) to record an amendment.
Dependency-only plan changes within the approved boundaries need no new approval.
Never silently edit task records or bypass gates. Required approval without an
answer means wait.

Only integrations sharing a target are serialized. Do not run other record
writers or Git mutations concurrently with CLI operations. Implementation in
independent worktrees may proceed in parallel; coordinate bookkeeping and merges.

The CLI trusts recorded results; it does not authenticate reviewers or establish
that a boolean has evidence. Proof covers committed content, not ignored files
or external environment state. There is no automatic agent launcher, verifier,
general crash recovery, or enforcement outside the CLI. All commands other than
`prove` exit 0 on success and 2 on error.
