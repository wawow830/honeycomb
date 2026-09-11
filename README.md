# honeycomb

A repeatable workflow for agentic coding, from a bounded task to a reviewed pull request.

Honeycomb currently provides instructions and templates. It has no application stack, test runner, or automated agent execution.

## Start here

1. Create an issue with the **Agent task** template. Write observable acceptance criteria.
2. Open the repository in your coding agent and ask it to read [AGENTS.md](AGENTS.md).
3. Give it the issue and the [implementation prompt](docs/prompts.md#implement-a-task).
4. Have it implement, verify, and prepare a draft PR using the [workflow](docs/workflow.md).
5. Run the [review prompt](docs/prompts.md#review-a-change) in a fresh session, address findings, and review the PR before merging.

The issue template becomes available in GitHub's issue chooser after this change lands on the default branch.

## Files

- [AGENTS.md](AGENTS.md): instructions for coding agents.
- [Workflow](docs/workflow.md): stages, completion criteria, and recovery.
- [Prompts](docs/prompts.md): implementation, review, and resume prompts.
- [Task template](.github/ISSUE_TEMPLATE/agent-task.md): scope and acceptance criteria.
- [PR template](.github/pull_request_template.md): evidence and handoff.

## First coding task

Define what Honeycomb should build, choose its language and runtime, and add one working vertical slice. Include reproducible setup, one meaningful test, and the commands for verifying it. Then add those commands to AGENTS.md and CI.

Until that task is complete, agents must report application checks as unavailable. A documentation review is not evidence that application code works.
