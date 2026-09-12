# Optional: run the workflow with Herdr

Herdr is a coordination surface, **not a reason to create more agents**. Use it only when delegation passes the workflow's independence, verification, and attention-budget tests. No new workspace, tab, worktree, or platform is required.

The installed CLI is the authority; this recipe was checked against the CLI available during the design session. It is not an auto-deployment script.

## 1. Verify caller context and learn the available commands

```bash
test "${HERDR_ENV:-}" = 1
```

**If that fails, stop: you are not inside a Herdr-managed pane.** Do not inspect or control another focused session from outside it.

When it passes:

```bash
herdr --help
herdr agent
herdr pane
herdr pane layout --current
herdr agent list
```

Do not run bare `herdr` for discovery. Prefer `--current` or explicit IDs; UI focus may belong to someone else.

## 2. Create one helper, only if useful

Choose a split from the caller's geometry: right for a wide pane, down for a narrow/tall pane. Avoid repeatedly creating unusable columns/rows. Preserve the working directory and user focus:

```bash
# Example only: choose the direction after inspecting the layout.
herdr pane split --current --direction down --cwd "$PWD" --no-focus
```

Read the new pane ID from `.result.pane.pane_id`. Do not predict it from the sidebar. Check that the new shell is ready, then start a supported agent using a unique live name:

```bash
# Replace RETURNED_PANE_ID. Choose the kind you actually use.
herdr agent start slice-reviewer --kind pi --pane RETURNED_PANE_ID
```

Starting an agent does not create layout. Leave pre-existing agents alone unless they have been assigned to this work. In a shared checkout, use a read-only reviewer while the builder remains the sole writer.

## 3. Delegate a bounded decision

Customize this prompt with the real card and comparison boundary:

```bash
herdr agent prompt slice-reviewer \
  "Read the assigned ship card and current diff. Read-only review: verify acceptance behavior, consequential failure paths, and release/recovery assumptions. Do not edit files, create agents, deploy, or modify other panes. Return only actionable findings with evidence and severity; say which checks you actually ran." \
  --wait --timeout 120000
```

A real task should identify its baseline revision, relevant files, allowed test commands, and time/cost budget; use the [task packet](templates/agent-task.md) when needed. **Read-only source review does not imply tests are side-effect-free:** authorize an isolated test target and any writes/service calls before running them. Never use production as an inferred test target. Avoid changing the diff under a reviewer without explicitly providing the updated revision and re-review boundary.

`--wait` waits for a settled lifecycle state, not proof of a correct result. A prompt delivered to an already-working agent can have its wait satisfied by the currently active turn; avoid ambiguous queued assignments. Herdr does not automatically notify the coordinator when work finishes.

Inspect the result:

```bash
herdr agent get slice-reviewer
herdr agent read slice-reviewer --source recent-unwrapped --lines 100
```

If blocked or a wait fails, inspect state and output before sending input. **The wait timeout is not an execution cancellation or spend cap.** Track the task deadline separately; after inspection, interrupt through the agent surface when appropriate and preserve a safe handoff for incomplete work. Enforce spending/tool limits outside the prompt where available. `unknown` is not completion. Some alternate-screen agents cannot provide long history reads while working; wait for settled state or use `--source visible` to inspect the current screen.

If completed output is truncated, increase the line count once. Alternate-screen history may still be unavailable. **Only after that failed read**, ask the agent to write the complete response to a temporary Markdown file and reply with its path; read that file directly. Do not confuse a missing transcript with an empty review.

## 4. Integrate, verify, and stop expanding the topology

The owner accepts/rejects findings against the contract and reruns required checks on the combined revision. Agent agreement does not replace a trusted test oracle or competent risk acceptance.

Do not start another builder while review is the bottleneck. Stop unnecessary helper work when its decision has been answered. Close only panes you created, after their useful work is complete; never close unrelated panes or stop the Herdr server as cleanup.

For an ordinary test/server process, use an explicitly targeted `pane run` and `pane read`, not an agent just to occupy a terminal. Production operations still require their normal authorization and recovery controls.
