---
name: honeycomb
description: "Use agentic coding in software development"
disable-model-invocation: true
---

Unbulleted instructions execute in order.
Consecutive bullet-point instructions at the same indentation execute in parallel.

Parallel execution applies to bullet-point instructions in skill procedures and node `instructions`, not descriptive lists or YAML sequences.

| Form | Meaning |
| --- | --- |
| `skill:<name>` | Load the named skill's instructions. |
| `agent spawn <id> <model> <cwd> <prompt>` | Start a fresh agent with the caller-chosen ID, model, working directory, and initial prompt. Nonblocking; returns nothing. Model slug comes from `//honeycomb/MODELS.md`. |
| `agent kill <id>` | Terminate the agent. |
| `agent set-model <id> <model>` | Change the model for subsequent prompts. |
| `agent prompt queue <id> <prompt>` | Queue a prompt to run after the current prompt. Nonblocking. |
| `agent prompt interrupt <id> <prompt>` | Stop current execution and process the new prompt. Nonblocking. |
| `agent list` | Return agent IDs, models, working directories, and execution states, distinguishing normal completion from interruption or termination. |
| `wait: <condition>` | Wait until the condition holds. |
| `if <condition>` / `else` | Execute the applicable indented block. |
| `while <condition>` | Execute the indented block while the condition holds. |
| `assert <condition>` | Require the condition to hold before proceeding. |
| `<var-name> = <value>` | Assign a value. |

### Agent lifecycle

An agent is **finished** when execution has stopped, whether normally, interrupted, killed, or crashed. Its assigned prompt is **complete** only when it reaches normal completion. Completion implies finished; finished does not imply completion. Agent completion does not establish node completion, which requires verified goals and published deliverables in the tracker.

`wait: agent <id> is finished` waits for execution to stop, not for successful work. The harness adapter uses native waiting or polls `agent list`. There is no separate `agent wait` command.

The model supplied to `agent spawn` must be configured before its initial prompt runs. The adapter may configure it during creation or create the agent, set its model, then submit the prompt.

### Paths

| Prefix | Relative to |
| --- | --- |
| `//` | Repository root in the agent's current worktree. |
| `./` | Agent working directory. |
| `~/` | User home directory. |
| `/` (without a second `/`) | Filesystem root; an absolute path. |

`//` is Honeycomb notation, not native shell expansion. Skills and adapters resolve it before passing paths to filesystem tools. Invocation inputs and repository-file references in YAML use `//` so they remain independent of the agent's working directory.

Honeycomb launches Validate through Human review in the destination pass directory through the harness adapter. Stage output paths beginning with `./` are relative to that working directory, not the input file's directory. Idea executes in the production directory, and Ship is launched there. Worker outputs belong to their node input's pass, in the worker's worktree.
