# Honeycomb workflow — draft

## Objective

Maximize genuine high-quality production while minimizing elapsed time, without sacrificing quality or human taste. AI slop is unacceptable.

Agents receive small, bounded assignments with specific instructions, deterministic external verification where applicable, and strong feedback loops. Reconnaissance makes the repository legible and informs subsequent work.

This document proposes package contents and skill procedures. Stage labels are descriptive placeholders, not final bee-themed skill names. Bee terminology belongs only in skill names.

```text
Idea → Validate → Define → Plan → Implement → QA → Human review → Ship
```

Define includes human approval of the definition. In-scope QA findings and human-requested changes feed back through Plan → Implement → QA. Required changes to goals, non-goals, or acceptance expectations return through Validate → Define for renewed human approval before planning. Human approval permits Ship even with nonblocking feedback. Ship only ships approved work.

## Instructions and handoffs

Skills use plain English. State ordering and parallel work explicitly where they matter.

Every newly dispatched agent receives exactly `/skill:<specific-skill> <YAML_FILE>` as its initial prompt, using the input file's absolute path.

Each skill except the entry-point `honeycomb` reads one YAML input package and writes one separate YAML output package. Supporting files and child-agent handoffs are allowed; no mandatory envelope or paired wrapper is required.

Skills specify output locations. Stage handoffs require normal prompt completion and a readable output matching the skill's package contract.

## Shared vocabulary

YAML structures inter-agent communication; shared dictionaries establish what its terms mean.

- The [Honeycomb dictionary](../skills/honeycomb/DICTIONARY.md) defines workflow terms. Skills reference this single source rather than copying it into each production.
- The `dictionary` in `define.yaml` defines production-specific domain terms and is part of the human-approved specification.

Define only terms whose ambiguity could change the outcome. Reuse them consistently in specifications, assignments, and findings. Resolve missing or conflicting meanings with the human rather than silently choosing an interpretation. Changing an approved domain meaning requires renewed human approval of `define` before planning.

## Ownership

| YAML packages | Tracker |
| --- | --- |
| Intent and task definition | Work items and dependency edges |
| Reconnaissance and work instructions | Ownership and work status |
| Verification evidence and review findings | Human approval decisions |
| References to source material and work items | Links to the relevant artifacts |

References connect the two without copying their state. In particular, YAML does not contain a second DAG, task-status field, or approval flag.

The production ticket's artifact links associate each `define` with the specific `validate` input that produced it. Downstream skills use that association to resolve the relevant `validate` output.

Git contains the implementation and production artifacts. `.honeycomb/` is not gitignored. Entry-point Honeycomb creates the production ticket, branch, and artifact directory before Idea. The ticket ID identifies the production throughout the workflow.

## Adapters

Skills describe abstract operations. Project adapters translate them into concrete operations without changing their meaning.

Examples:

| Abstract operation | Adapter translation |
| --- | --- |
| Start an agent | `honeycomb/MODELS.md` maps roles to models. `honeycomb/HARNESS.md` starts agents with caller-chosen IDs, working directories, and prompts, configuring the model before the initial prompt runs. Starting an agent does not wait for it to finish. |
| Control and observe agents | `honeycomb/HARNESS.md` describes termination, model changes for subsequent prompts, nonblocking prompt queuing and interruption, and listing agents with their IDs, models, working directories, and execution states. |
| Wait for an agent | `honeycomb/HARNESS.md` uses native waiting or polling to observe when execution stops, distinguishing normal completion from interruption or failure. |
| Resolve a tracker ticket | `honeycomb/TRACKER.md` resolves ticket references to the relevant GitHub or Linear ticket. |
| Take a frontier node | `honeycomb/TRACKER.md` supplies the concrete procedure for selecting a node with satisfied dependencies and taking ownership so another worker cannot take the same node. |
| Prepare a worker workspace | The project's workspace adapter creates an isolated Git worktree and branch for the worker, with its node input and references available, and resolves prerequisite code and evidence through the tracker nodes' branch and artifact links. |
| Publish the implementation and evidence | The project's workspace adapter commits the worker's implementation and evidence on its branch and makes them available to downstream workers. The tracker node links that branch and its evidence. |
| Complete the node | The tracker adapter marks the node complete once its goals and verification are satisfied and its deliverables are published. |
| Integrate worker branches | The project's workspace adapter combines worker branches, including their implementation and evidence, and advances the production branch only to a combined result that passes the integration node's verification and preserves already integrated work, including under concurrent integration. |

These are Markdown translations, not an additional adapter framework. Core skills contain no harness-, model-, tracker-, or application-stack-specific commands.

## Production setup — entry-point Honeycomb

Upon receiving the human's idea, entry-point Honeycomb establishes the production before executing the stages:

1. Create the production's tracker ticket for the human's idea.
2. Use the ticket ID to create the production branch and `.honeycomb/<production-id>/` directory.
3. Use that branch and directory to execute the workflow, starting with Idea.

The ticket tracks the production from the start. Define later attaches the formal definition to this existing ticket for human approval.

## Artifact conventions — proposed

Production artifacts live under `.honeycomb/<production-id>/` in the repository, where `<production-id>` is the ticket ID established during production setup.

```text
.honeycomb/<production-id>/
├── idea.yaml
├── pass-<n>/
│   ├── validate/
│   │   ├── validate.yaml
│   │   ├── recon.yaml
│   │   └── research.yaml
│   ├── define.yaml
│   ├── plan/
│   │   ├── plan.yaml
│   │   └── nodes/
│   │       └── <node-id>.yaml
│   ├── implement/
│   │   ├── implement.yaml
│   │   └── nodes/
│   │       └── <node-id>.yaml
│   ├── qa.yaml
│   └── review.yaml
└── ship.yaml
```

Entry-point Honeycomb creates the first pass before Validate and chooses the next unused pass number for each feedback iteration. It launches Validate through Human review with the destination pass directory as their working directory through the harness adapter. Their output paths are relative to that directory, not the input file's directory. Only stages executed in that pass write outputs there. Unchanged inputs reference their existing artifacts in earlier passes rather than copying them.

```text
Working directory: `/path/to/repository/.honeycomb/task-123/pass-002/`
Prompt: `/skill:plan /path/to/repository/.honeycomb/task-123/pass-001/qa.yaml`
Output: `plan/plan.yaml`
```

Implementation worker outputs live in the same pass as their node inputs, mirroring `plan/nodes/` under `implement/nodes/`. Repair work gets new tracker nodes, rather than rewriting previous results.

`idea.yaml` and `ship.yaml` belong to the production, not a pass. Idea executes in the production directory, and Honeycomb launches Ship there. `ship` references the approved pass's `review`.

Resolve repository-file references in YAML from the current worktree's repository root, and links within a skill from its directory. References identify specific artifacts, not a mutable `latest.yaml` alias. The examples below use illustrative tracker IDs and repository paths.

## 1. Idea — entry-point Honeycomb

### Purpose

Capture the human's idea.

### Input

The human's idea, not a YAML file.

### Output: `idea.yaml`

```yaml
idea: |
  Users want to export their filtered search results for use in their existing workflow.
references:
  - docs/product/search.md
```

### Procedure

1. Read what the human says and identify their intended outcome. Ask clarifying questions where needed rather than assume answers.
2. Write the understood idea to `idea.yaml` in the production directory.

The output contains `idea` and, when supplied by the human, `references`. It does not contain a task definition, plan, or branching.

## 2. Validate

### Purpose

Determine with the human whether the idea is worth pursuing and feasible, resolving scope and tradeoffs using evidence.

`validate` is both the human-facing validation agent and the coordinator. It delegates repository exploration and external research to separate `recon` and `research` agents, which run concurrently with the same input and destination pass directory.

`recon` writes `validate/recon.yaml` containing `reconnaissance` and `verification`. `research` writes `validate/research.yaml` containing `research`. `validate` uses their findings and the human discussion to produce its output below.

### Input

`idea` YAML, or `qa` or `review` YAML containing required changes to the approved scope. For `review`, these are changes requested by the human.

### Output: `validate/validate.yaml`

```yaml
idea: .honeycomb/task-123/idea.yaml

decisions:
  - question: What should the export contain?
    answer: All results matching the active filters, not just the visible page.
    rationale: The human needs the complete filtered dataset.

reconnaissance:
  - location: src/search/filters.ts
    finding: Defines the existing filtering behavior that export must preserve.

research: []

verification:
  - method: Search compatibility tests
    execution: <repository-specific command>
    prerequisites: <required setup>
    baseline: <observed result>
```

- `idea`: Reference to the `idea` YAML; do not repeat its contents.
- `decisions`: Questions resolved with the human, their answers, and rationale. Covers value, scope, constraints, and human taste.
- `reconnaissance`: Repository findings needed downstream, with specific file references and explanations.
- `research`: External findings and sources, when needed.
- `verification`: Available verification methods, how to execute them, prerequisites, and observed baseline results.

These fields contain resolved decisions and supporting evidence, not a task definition or plan. Record specific reconnaissance and research findings so downstream agents can reuse them. The example is abbreviated.

### Procedure

1. Read the idea and its references. For feedback input, read the feedback, its referenced `define`, and the associated `validate` output and idea.
2. Create `validate/` in the destination pass directory.
3. Use the project's harness and model adapters to start `recon` and `research` agents in parallel, with the same input and working directory.
4. Wait for both agents to stop, confirm normal completion, and read `validate/recon.yaml` and `validate/research.yaml`.
5. Determine with the human whether the idea is worth pursuing and feasible, resolving scope and tradeoffs using the findings.
6. Write `validate/validate.yaml`.

## 3. Define

### Purpose

Capture the full, human-approved specification of the intended result. Settle choices that determine the outcome, leaving implementation planning to Plan.

### Input

`validate` YAML.

### Output: `define.yaml`

```yaml
id: <production ticket ID>

intent: |
  <Who wants this, what they want, and why it matters.>

goals:
  - <Outcome to achieve>

non_goals:
  - <Explicitly excluded outcome>

dictionary:
  <domain_term>: |
    <Agreed meaning that distinguishes this term from plausible alternatives.>

specification: |
  <Full agreed description of the result.
  Organize according to the task.
  Include relevant behavior, qualities, examples,
  and the reasoning behind important decisions.>

constraints:
  - <Boundary the solution must respect>

success:
  - <Observable condition demonstrating the intended outcome>

failure:
  - <Unacceptable outcome or consequence>

references:
  - location: <path or URL>
    relevance: |
      <What applies, and whether it is a requirement,
      an illustration, or background context.>
```

`specification` carries the detail; the surrounding fields make intent and boundaries easy to find rather than repeating the entire specification. `id` is the existing production ticket's ID. `dictionary` maps domain terms to their agreed meanings; use an empty mapping when no terms need clarification. Workflow vocabulary remains in the shared Honeycomb dictionary.

Downstream agents should understand the full agreed intent from this document and its explicit references without reconstructing the conversation. The human reviews and approves the whole specification, not merely its goals or success conditions. Approval remains in the tracker.

### Procedure

1. Read `validate`, its referenced idea, and relevant references.
2. Draft the full specification using the structure above and the existing production ticket's ID.
3. Review it with the human. Resolve gaps and ambiguous terms rather than inventing answers, and revise until it captures their intended result, including relevant detail and rationale. Record agreed domain meanings in `dictionary` and use those terms consistently.
4. Write `define.yaml` and link it from the existing production ticket, associating it with its specific `validate` input.
5. Present the complete specification for human approval through the tracker and wait for approval.

Planning requires approval of the referenced definition, not a generic approval of the idea.

## 4. Plan

### Purpose

Plan how the task will be implemented.

Plan settles decisions other assignments must rely on; Implement settles decisions contained within its assignment. Module responsibilities, function names, and data types belong in Plan when they form shared contracts, not merely because they are design decisions. Specify enough to make assignments independently executable without prewriting their code. Work requiring constant joint design may belong in one node.

Represent the work as a DAG of small, bounded, independently verifiable nodes. Feature work uses vertical slices: each delivers an end-to-end outcome across the layers needed for that outcome, including verification. Do not divide feature work into separate frontend, backend, and test nodes merely by layer. Integration is ordinary DAG work that combines and verifies existing work.

### Input

An approved `define`, or `qa` or `review` YAML referencing `define` and containing in-scope QA findings or human-requested changes.

### Output: `plan/plan.yaml`

```yaml
define: .honeycomb/task-123/pass-001/define.yaml

approach: |
  Reuse existing filtering and permission logic.
  Extend the existing download mechanism for CSV export.

nodes:
  - id: node-124
    goals:
      - Users can export all results matching their active filters from the search interface.
    scope:
      includes:
        - Filtered CSV export, its search-interface action, and verification.
      excludes:
        - Changes to search filtering or permission rules.
        - Integration of other nodes' branches onto the production branch.
    instructions: |
      Read the existing filtering behavior and search interface patterns in the references.
      Implement export using the existing filtering and permission behavior.
      Connect export to the existing search interface using the agreed interaction patterns.
      Add coverage for exporting filtered results and enforcing permissions through this interaction.
      Run verification and record the results.
    verification:
      - Run the search compatibility tests using the execution details established in Validate.
      - Verify that the export interaction includes all matching results and excludes unauthorized records.
    references:
      - .honeycomb/task-123/pass-001/define.yaml
      - .honeycomb/task-123/pass-001/plan/plan.yaml
      - .honeycomb/task-123/pass-001/validate/validate.yaml
      - src/search/filters.ts
      - src/search/
      - tests/search/
```

The output contains `define`, `approach`, and `nodes`. `approach` explains the overall implementation decisions and how the work fits together; node instructions specify individual assignments. Both reuse the agreed meanings in `define.dictionary`.

Each node contains:

- `id`: The node's tracker ticket ID.
- `goals`: The node's intended outcomes within the approved definition.
- `scope`: `includes` and `excludes` state the work this node does and does not own. Scope bounds responsibility, not necessarily files or layers.
- `instructions`: A YAML literal block containing plain-English instructions, with ordering and parallel work stated where needed.
- `verification`: How to verify the node's outcomes.
- `references`: The relevant `define`, the containing `plan`, and specific context needed to execute the node without repeating reconnaissance or research.

Clear assignments have `goals`, `instructions`, and `references`; `scope` makes them bounded; `verification` makes them testable.

Dependencies, agent ownership, and status live only in the tracker. Plan does not implement.

### Procedure

1. Read the approved `define` and relevant `validate` output. For QA or review input, also read its findings and implementation evidence. Use the human's tracker decision to distinguish required review changes from nonblocking feedback.
2. Establish the overall implementation `approach`: what changes, what is reused, and how the pieces fit together. Settle shared commitments between assignments while leaving local design decisions to workers.
3. Divide the required work into small, bounded, independently verifiable nodes, using vertical slices for feature work.
4. Create the nodes and dependencies in the tracker, including ordinary integration nodes that combine worker branches and evidence onto the production branch.
5. Give each node goals, scope, instructions, verification, references, and the prerequisites that make it executable at the frontier.
6. Check that the DAG is acyclic and covers the required work, including the definition's relevant goals, success, and failure.
7. Write `plan/plan.yaml` and link it from the tracker nodes.

## 5. Implement

### Purpose

Implement the task using the plan.

Plan creates and changes the DAG and its shared commitments. Implement executes the assignments, including local design decisions within their scope and those commitments.

Honeycomb invokes `implement` once per plan. Two ordinary skills encapsulate implementation:

- `implement`: Take open frontier nodes through the tracker, write each assigned node to YAML, spawn workers, wait for completion, and write one aggregate `implement` YAML for QA.
- `implement-worker`: Read one assigned node YAML, implement and verify that node, and write its evidence YAML.

Both use the standard `/skill:<specific-skill> <YAML_FILE>` invocation.

### Input

`plan` YAML. `implement` selects and assigns work; each `implement-worker` receives only its assigned node YAML.

### Output: `implement/implement.yaml`

```yaml
plan: .honeycomb/task-123/pass-001/plan/plan.yaml
revision: <git commit>
evidence:
  - .honeycomb/task-123/pass-001/implement/nodes/node-124.yaml
  - .honeycomb/task-123/pass-001/implement/nodes/node-125.yaml
  - .honeycomb/task-123/pass-001/implement/nodes/node-126.yaml
```

The output contains `plan`, `revision`, and `evidence`. `revision` identifies the Git commit containing the complete implementation. Worker outputs are referenced rather than copied.

QA, Human review, and Ship follow their existing package references to this source revision. The tracker associates human approval with that result; downstream packages do not repeat `revision`.

### `implement` procedure

1. Read `plan` and its approved `define`.
2. Assign open frontier nodes through the tracker. Extract each selected node into `plan/nodes/<node-id>.yaml` beside its input plan, and start a separate `implement-worker` agent with that file through the project adapters. Run independent nodes concurrently.
3. Monitor workers and the tracker, dispatching newly available frontier nodes until all plan nodes are complete.
4. Wait for all dispatched workers to stop and confirm that all nodes are complete and their implementation is present on the production branch.
5. Write `implement/implement.yaml` with the `plan` reference, the complete implementation's Git commit as `revision`, and references to worker outputs as `evidence`.

Each implementation worker uses an isolated Git worktree and branch. Plan's ordinary integration nodes combine implementation and evidence onto the production branch through the workspace adapter's safe update operation. Workspace creation, concrete Git operations, and any serialization strategy belong to the adapter.

### `implement-worker` input: `.honeycomb/<production-id>/pass-<n>/plan/nodes/<node-id>.yaml`

Each node YAML belongs to the directory containing its input `plan.yaml`. The input is the selected node itself, containing `id`, `goals`, `scope`, `instructions`, `verification`, and `references`, including the relevant `define` and containing `plan`. The node bounds responsibility, not visibility: workers read the specification and plan for intent, shared commitments, and neighboring work, but execute only their assigned node. Shared decisions remain in the plan rather than being copied into every node. Ownership and dependencies remain in the tracker.

### `implement-worker` output: `.honeycomb/<production-id>/pass-<n>/implement/nodes/<node-id>.yaml`

```yaml
id: node-124
changes:
  - Implemented the filtered export interaction.
verification:
  - method: Search compatibility tests
    result: All tests passed.
    evidence: <supporting evidence reference>
```

The worker output contains `id`, `changes`, and `verification`. Verification records methods, observed results, and supporting evidence, not tracker status.

### `implement-worker` procedure

1. Read the node and its references.
2. Execute its instructions and verification to satisfy its goals within scope.
3. Publish the implementation and evidence.
4. Complete the node.

Each node gets a separate worker. Workers execute assigned nodes rather than selecting work from the DAG. Completion means the node's implementation and evidence are committed and accessible through its tracker links, not merely present in a private worktree. Node completion does not constitute independent QA or production acceptance.

### YAML inter-agent communication

```text
Plan YAML → implement
               ├→ node YAML → implement-worker → evidence YAML
               ├→ node YAML → implement-worker → evidence YAML
               ├→ node YAML → implement-worker → evidence YAML
               └→ aggregate implement YAML → QA
```

Files are passed by reference, not through chat or agent return values. No separate assignment wrapper is needed. YAML carries content and evidence; the tracker owns dependencies, ownership, status, and artifact links.

## 6. QA

### Purpose

Assure the implementation's quality.

QA uses a separate agent and produces qualitative findings, not repair nodes. Plan turns in-scope findings into further work.

Define and QA are primarily qualitative: Define expresses goals, non-goals, success, failure, and quality expectations; QA assesses whether the implementation fulfills them and meets a general quality standard.

Plan and Implement are primarily quantitative: Plan translates the definition into bounded work with meaningful deterministic verification; Implement uses tests, type checks, CI, and other external verifiers in a fast feedback loop. Passing checks does not establish qualitative quality.

These are emphases, not exclusive responsibilities: engineering judgment and executable verification are needed throughout. QA exercises independent engineering judgment within human intent and taste.

### Input

The `implement` YAML provides `revision` and a reference to `plan`, which references `define`. QA uses `define`, relevant `validate` output, and the complete implementation at `revision`, including its tests. Worker verification evidence is not required context.

### Output: `qa.yaml`

```yaml
define: .honeycomb/task-123/pass-001/define.yaml
implement: .honeycomb/task-123/pass-001/implement/implement.yaml
findings:
  - observation: <the specific shortcoming>
    evidence:
      - <relevant code, observed behavior, reference, or engineering reasoning>
    consequence: <why this matters to the implementation or human outcome>
```

- `define`: Reference to the approved task definition.
- `implement`: Reference to the implementation handoff being assessed.
- `findings`: Substantiated shortcomings, each containing `observation`, `evidence`, and `consequence`.

In-scope findings return to Plan. Scope-changing feedback returns through Validate → Define for renewed approval before planning. An empty `findings` list proceeds to Human review.

### Procedure

1. Read `define` and relevant `validate` output.
2. Inspect the complete implementation and tests in repository context.
3. Investigate how well the implementation fulfills human intent and achieves high quality.
4. Write `qa.yaml` with findings explaining each shortcoming, its supporting evidence or reasoning, and its practical consequence.

Evaluation of this procedure remains deferred; its reliability is not established.

## 7. Human review

### Purpose

Review the implementation and end result with the human against the idea.

### Input

`qa` with no outstanding findings. Its `implement` reference identifies the source revision whose implementation and end result the human reviews. Resolve `idea` through the relevant `validate` output.

### Output: `review.yaml`

```yaml
define: .honeycomb/task-123/pass-001/define.yaml
qa: .honeycomb/task-123/pass-002/qa.yaml
findings:
  - The export action is unnecessarily difficult to discover.
```

- `define`: Reference to the approved task definition.
- `qa`: Reference to the preceding assessment and implementation.
- `findings`: The human's feedback, recorded faithfully, including the distinction between required changes and nonblocking suggestions.

The human's decision controls routing and stays in the tracker. Findings alone imply neither approval nor a requirement for another repair pass.

### Procedure

1. Read `qa`, `define`, relevant `validate` output, and its referenced idea.
2. Present the implementation and end result to the human for review against the idea, including their intent and taste.
3. Discuss the review until the human approves the result or identifies actionable required changes. Continue the conversation rather than inventing repairs while the decision is withheld or changes are unclear.
4. Write `review.yaml` with the human's findings.
5. Record the human's decision against the result identified by `revision` in `implement`, and link the review in the tracker.

Approval of the reviewed result permits Ship, even with nonblocking feedback. Human-requested in-scope changes go to Plan; requested scope changes return through Validate → Define for renewed approval before planning. Human review does not merge.

## 8. Ship

### Purpose

Ship.

### Input

`review` for an end result approved by the human in the tracker.

### Output: `ship.yaml`

```yaml
review: .honeycomb/task-123/pass-003/review.yaml
results:
  - <merge reference>
  - <release reference>
  - <deployment reference>
```

`results` records references to the deliveries actually performed. Approval and work status remain in the tracker.

### Procedure

1. Read `review` and follow its references to `revision` in `implement`.
2. Confirm that the result being shipped is that revision and has human approval in the tracker.
3. Ship through the project's shipping adapter.
4. Write `ship.yaml` in the production directory and link it from the production ticket.

The adapter defines the project's delivery operations: merge, release, deploy, publish, as applicable. Ship ships approved work. It does not conduct human review or produce repair findings.

## Feedback flow

```text
Plan → Implement → QA
                   ├─ in-scope findings → Plan
                   ├─ scope-changing feedback → Validate → Define → Plan
                   └─ no findings → Human review
                                    ├─ approved, with or without nonblocking feedback → Ship
                                    ├─ in-scope changes requested → Plan
                                    ├─ scope changes requested → Validate → Define → Plan
                                    └─ decision withheld or requested changes unclear → Continue conversation
```

Entry-point Honeycomb starts a new pass for QA findings or human-requested changes and routes the required work according to whether it fits the approved `define`. Nonblocking feedback accompanying approval does not start another pass. Changes to goals, non-goals, or acceptance expectations require revalidation and a new human-approved `define` before planning; Plan does not change the approved scope.

Plan handles both in-scope QA findings and in-scope human-requested changes using the same planning procedure. Every repair node gets a fresh implementation agent, and QA independently assesses the complete revised implementation again before human review.

There is no separate retry policy, non-progress detector, blocked-work protocol, or repair-planning skill.
