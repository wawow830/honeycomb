# Agent prompts

Replace angle-bracket placeholders before use. Supply the issue text directly if the agent cannot access GitHub.

## Implement a task

```text
Read AGENTS.md and docs/workflow.md in this repository.

Task: <issue URL or complete task brief>

Inspect the current code and working tree. State the acceptance criteria,
a short implementation plan, and the checks you will use. Ask only about
ambiguities that materially affect the result.

Implement the task on a dedicated branch, preserve unrelated changes, and
verify each criterion. Review your final diff and prepare a draft PR using
the repository template if access allows. Report actual check results and
anything not verified. Leave merging to the repository owner.
```

## Review a change

Use a fresh agent session when possible.

```text
Read AGENTS.md. Review this change against the task and acceptance criteria.

Task: <issue URL or task brief>
Base: <base commit or branch>
Head: <head commit or branch>
Implementation evidence: <PR URL or verification notes>

Inspect the actual diff and relevant surrounding code. Look for concrete
bugs, regressions, missing behavior, and gaps in verification. Do not rely
on the implementation summary as proof.

Report actionable findings with severity, file location, failure scenario,
and suggested verification. State which checks you ran and any limitations.
If there are no findings, say so without implying the code is proven correct.
Do not edit files, post a review, or merge the PR.
```

## Resume a task

```text
Read AGENTS.md and resume this task from the handoff below.
Check the current repository state before relying on the notes.

Task: <issue URL or brief>
Branch and last commit: <branch and SHA>
Completed: <changes and satisfied criteria>
Remaining: <unfinished criteria or review findings>
Verification: <commands, results, and checks not run>
Blocker and attempts: <error, attempted fixes, and current hypothesis>
Next action: <smallest useful step>

Continue the existing plan where it still fits the repository state.
Preserve unrelated changes and report any new blocker precisely.
```
