# Agentic coding workflow

Use one task branch and one PR for a bounded outcome. A person defines the desired result; the agent handles implementation and evidence; a person decides whether to merge.

## Stages

| Stage | Work | Exit condition |
| --- | --- | --- |
| Define | Describe the problem, scope, exclusions, and observable acceptance criteria in an issue or task brief. | The agent can tell whether the task is complete. |
| Inspect and plan | Read repository guidance and relevant code. Identify files, dependencies, risks, and checks. | A short plan links the proposed change to the criteria. |
| Implement | Make focused changes on a task branch. Add tests for changed behavior where applicable. | The intended behavior is implemented and the diff stays within scope. |
| Verify | Run the relevant checks and inspect the diff. Check each acceptance criterion. | Evidence is recorded; failures and unavailable checks are explicit. |
| Review | Use a fresh review session when available. Address actionable findings and repeat affected checks. | Findings are resolved or documented for the human decision. |
| Handoff | Prepare a draft PR with results, limitations, and any manual checks. | A person has enough evidence to review and choose whether to merge. |

These stages are a working process, not an installed background service. Templates do not enforce permissions, CI, or branch protection.

## Keep tasks small enough to finish

A useful task names one observable result, such as "reject an empty task title and show an error." Split work when it has unrelated outcomes or cannot be reviewed as one coherent change.

For a small fix, a few plan bullets in the agent session are enough. For a longer task, keep a task-specific note under docs/tasks/ with decisions and verification evidence. Create that directory only when needed.

Ask about ambiguities that affect product behavior. Choose routine implementation details from existing repository conventions.

## Verification

For each acceptance criterion, record its evidence. Prefer a behavioral test, a reproducible command, or a specific manual check.

Once code exists, run the repository's documented focused tests and required checks. Add CI using those same commands after the runtime is chosen. Configure required checks and human review through repository settings if the owner wants enforced merge gates.

For today's documentation-only repository, verify relative links, template structure, and consistency across instructions. There is no application test suite to run.

A failing check keeps the change in draft unless a person explicitly accepts the limitation. Passing tests support a review decision; they do not authorize a merge.

## Review

Give the reviewer the task, base and head references, diff, and evidence. A fresh session reduces dependence on the implementer's assumptions. Focus on incorrect behavior, regressions, missing tests, and unmet acceptance criteria.

Record findings with a file location, concrete failure scenario, and severity. Fix the underlying issue and rerun affected checks. If no fresh reviewer is available, label the result as self-review and leave human review pending.

## Recovery

- If requirements conflict, identify the conflicting statements and ask one focused question.
- If access or dependencies block a check, record the exact blocker and which criteria remain unverified.
- If repeated fixes fail, follow the retry limit in AGENTS.md and leave a handoff.
- If the session ends, preserve the branch and record the commit, unfinished work, checks, and next action.
- If the base branch changes, integrate it without discarding others' work and rerun checks affected by the update.

## Optional automation later

After one task has completed this process, automate the steps that proved useful. Start with CI. Add an agent runner only after choosing the coding tool, invocation method, credentials, allowed actions, cost limit, and timeout behavior.

Any future event-driven runner should validate the triggering actor, treat issue text as untrusted input, use limited credentials, prevent duplicate runs, and stop at a reviewable PR. This starter does not install such a runner.
