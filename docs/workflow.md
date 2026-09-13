# Honeycomb workflow — draft

## Objective

Maximize genuine high-quality production while minimizing elapsed time, without sacrificing quality or human taste. AI slop is unacceptable.

Agents receive small, bounded assignments with specific instructions, deterministic external verification where applicable, and strong feedback loops. Reconnaissance makes the repository legible and answers downstream questions before execution.

This document proposes package contents and skill procedures. Stage labels are descriptive placeholders, not final bee-themed skill names. Bee terminology belongs only in skill names.

```text
Idea → Validate → Define → Plan → Implement → QA → Human review → Ship
```

Define includes human approval of the definition. Findings from QA or Human review feed back through Plan → Implement → QA. Ship only ships approved work.

## Execution language

| Form | Meaning |
| --- | --- |
| Unbulleted instructions | Execute in order. |
| Consecutive bullet-point instructions | Execute in parallel at the same indentation. |
| `skill:<name>` | Load the named skill's instructions. |
| `spawn:<agent> <prompt>` | Start the agent with the prompt without waiting. Model slug comes from `honeycomb/MODELS.md`. Returns nothing. |
| `wait:<until-condition>` | Wait until the condition holds. |
| `if <condition>` / `else` | Execute the applicable indented block. |
| `while <condition>` | Execute the indented block while the condition holds. |
| `assert <condition>` | Require the condition to hold before proceeding. |
| `<var-name> = <value>` | Assign a value. |

Every dispatched agent receives exactly:

```text
/skill:<specific-skill> <YAML_FILE>
```

Each skill except the entry-point `honeycomb` reads one YAML file and writes one separate YAML file. The YAML is the package. There is no mandatory envelope or paired input/output wrapper.

The skill specifies its output location. A stage's output can be supplied directly to another skill. An output file's mere existence is not proof that its writer has finished.

## Ownership

| YAML packages | Tracker |
| --- | --- |
| Intent and task definition | Work items and dependency edges |
| Reconnaissance and work instructions | Ownership and work status |
| Verification evidence and review findings | Human approval decisions |
| References to source material and work items | Links to the relevant artifacts |

References connect the two without copying their state. In particular, YAML does not contain a second DAG, task-status field, or approval flag.

Git contains the implementation and production artifacts. `.honeycomb/` is not gitignored. Each production uses its own branch. Branching is not part of Idea; its placement remains to be aligned.

## Adapters

Skills describe abstract operations. Project adapters translate them into concrete operations without changing their meaning.

Examples:

| Abstract operation | Adapter translation |
| --- | --- |
| `spawn:<agent> <prompt>` | `honeycomb/MODELS.md` maps the abstract agent name to a model slug. `honeycomb/HARNESS.md` translates spawning into a concrete operation such as `herdr agent start …`, using that model and prompt. |
| `ticket:<id>` | `honeycomb/TRACKER.md` resolves the reference to the relevant GitHub or Linear ticket. |
| Take a frontier node | `honeycomb/TRACKER.md` supplies the concrete procedure for selecting a node with satisfied dependencies and taking ownership so another worker cannot take the same node. |

These are Markdown translations, not an additional adapter framework. Core skills contain no harness-, model-, tracker-, or application-stack-specific commands.

## Artifact conventions — proposed

Production artifacts live under `.honeycomb/<production-id>/`.

- `idea.yaml`
- `validated-<n>.yaml`
- `definition-<n>.yaml`
- `plan-<n>.yaml`
- `implementation/<node-id>.yaml`
- `implementation-<n>.yaml`
- `qa-<n>.yaml`
- `review-<n>.yaml`
- `ship-<n>.yaml`

A skill chooses the next unused number for its stage. Each implementation node has its own output path. Repair work gets new tracker nodes, rather than rewriting previous results.

References to files are repository-relative. References identify specific artifacts, not a mutable `latest.yaml` alias. The examples below use illustrative tracker IDs and repository paths.

## 1. Idea — entry-point Honeycomb

### Purpose

Make sense of what the human says. Interpret the human's intent and ask clarifying questions until it is understood, then express the understood idea in YAML. Do not invent requirements or assess feasibility; feasibility belongs to Validate.

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

```text
Read what the human says and identify their intended outcome.
while the human's intent is unclear
  Ask clarifying questions. Do not substitute assumptions for their answers.
Write the understood idea to idea.yaml.
```

The output contains `idea` and, when supplied by the human, `references`. It does not contain a task definition, plan, or branching.

## 2. Validate

### Purpose

Validate the idea with the human. Establishing whether the idea is worth pursuing and understanding how it can be executed go hand in hand: reconnaissance and research inform both. Answer downstream questions before passing the validated YAML to Define.

### Input

Idea YAML.

### Output: `validated-<n>.yaml`

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

- `idea`: Reference to the Idea YAML; do not repeat its contents.
- `decisions`: Questions resolved with the human, their answers, and rationale. Covers value, scope, constraints, and human taste.
- `reconnaissance`: Repository findings needed downstream, with specific file references and explanations.
- `research`: External findings and sources, when needed.
- `verification`: Available verification methods, how to execute them, prerequisites, and observed baseline results.

These fields contain resolved decisions and supporting evidence, not a task definition or plan. Reconnaissance and research must be specific enough that downstream agents do not need to repeat them. The example is abbreviated; actual output answers all downstream questions.

### Procedure

```text
Read the idea and its references.
Validate with the human, using reconnaissance and research to answer questions as they arise.
Continue until downstream questions are answered.
Write the validated YAML.
```

## 3. Define

### Input

Validated YAML.

### Output: `definition-<n>.yaml`

```yaml
id: task-123
goals:
  - Let users export all results matching their active search filters.
non_goals:
  - Scheduled or recurring exports.
success:
  - Deterministic checks confirm that exported records match the active filters and permissions.
  - Independent agent review confirms reuse of established search behavior without unnecessary abstractions.
  - Human review accepts the export interaction against the agreed behavior and taste.
failure:
  - Export exposes records the user cannot access.
  - Export omits matching records or includes records outside the active filters.
```

The output contains exactly five fields:

- `id`: The production's tracker ticket ID, not a separate identity.
- `goals`: Intended outcomes.
- `non_goals`: Explicitly excluded outcomes.
- `success`: Conditions that must hold.
- `failure`: Conditions that must not occur.

Goals, success, and failure can involve deterministic checks, agent review, human review, or other assessment methods. State how they will be assessed where needed, without imposing a separate criterion schema. Human-owned judgments remain human-owned.

### Procedure

```text
Read the validated YAML and relevant references.
Create the production's tracker ticket and use its ID as the definition's id.
Write goals, non-goals, success, and failure from the validated decisions.
Check that the definition is bounded, internally consistent, and verifiable.
Write the definition YAML and present it for human approval through the tracker.
wait:<human approval of this definition artifact>
```

Planning requires approval of the referenced definition, not a generic approval of the idea.

## 4. Plan

### Purpose

Turn the approved definition, or review findings, into a DAG of small, bounded, independently verifiable vertical slices. Each node delivers an end-to-end outcome across the layers needed for that outcome, including verification. Do not divide the work into separate frontend, backend, and test nodes merely by layer.

### Input

An approved definition, or a review YAML containing findings and a reference to the definition.

### Output: `plan-<n>.yaml`

```yaml
definition: .honeycomb/task-123/definition-001.yaml
nodes:
  - id: node-124
    goals:
      - Users can export all results matching their active filters from the search interface.
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
      - .honeycomb/task-123/validated-001.yaml
      - src/search/filters.ts
      - src/search/
      - tests/search/
```

The output contains `definition` and `nodes`. Each node contains:

- `id`: The node's tracker ticket ID.
- `goals`: The node's intended outcomes within the approved definition.
- `instructions`: A YAML literal block containing Honeycomb instructions. Unbulleted instructions execute in order; consecutive bullet-point instructions execute in parallel.
- `verification`: How to verify the node's outcomes.
- `references`: The specific context needed to execute the node without repeating reconnaissance or research.

Dependencies, ownership, and status live only in the tracker. Plan does not implement.

### Procedure

```text
Read the approved definition and relevant Validate output.
if the input is a review
  Read its findings and implementation evidence.
Divide the required work into small, bounded, independently verifiable vertical slices.
Create the nodes and dependencies in the tracker. Integration, if needed, is an ordinary node with its own instructions and verification.
Give each node goals, ordered instructions, verification, and references. Establish the prerequisites that make it executable when it reaches the frontier.
Check that the DAG is acyclic and covers the required work, including the definition's relevant goals, success, and failure.
Write the Plan YAML and link it from the tracker nodes.
```

## 5. Implement

### Purpose

Execute the existing plan and produce the complete implementation. Plan creates and changes the DAG; Implement executes it.

The Implement skill contains two instruction files:

- `SKILL.md`: Spawn workers for open frontier nodes, wait for completion, and write one implementation YAML for QA.
- `WORKER.md`: Take one open frontier node, execute its instructions and verification, and write its node YAML.

### Input

Plan YAML. Each worker receives the same Plan YAML and executes only the node it takes through the tracker.

### Output: `implementation-<n>.yaml`

```yaml
plan: .honeycomb/task-123/plan-001.yaml
evidence:
  - .honeycomb/task-123/implementation/node-124.yaml
  - .honeycomb/task-123/implementation/node-125.yaml
  - .honeycomb/task-123/implementation/node-126.yaml
```

The output contains `plan` and `evidence`. It references the worker outputs rather than copying their contents. QA receives this single YAML file and follows its references.

### `SKILL.md` procedure

```text
Read the Plan YAML and its approved definition.
while the plan has unfinished nodes in the tracker
  if there are open frontier nodes
    Spawn separate workers using WORKER.md and the Plan YAML for the available nodes.
  wait:<a running worker has finished>
wait:<all workers have finished>
assert all nodes are complete and their implementation is present on the production branch
Write one implementation YAML referencing the Plan YAML and worker outputs.
```

Integration, when needed, is executed as ordinary DAG nodes.

### `WORKER.md` output: `implementation/<node-id>.yaml`

```yaml
id: node-124
changes:
  - Implemented the filtered export interaction.
verification:
  - method: Search compatibility tests
    result: All tests passed.
    evidence: .honeycomb/task-123/evidence/node-124-tests.txt
```

The worker output contains `id`, `changes`, and `verification`. Verification records methods, observed results, and supporting evidence, not tracker status.

### `WORKER.md` procedure

```text
Resolve the production through the Plan YAML's definition reference.
Take one open frontier node through the tracker.
Read the node's goals, instructions, verification, and references, and the relevant definition content.
Read prerequisite evidence through the tracker node's artifact links when needed.
Use the production's agreed workspace.
Execute this node's instructions and verification, using verification feedback to satisfy its goals.
Write the node YAML with its id, changes, and verification results.
Link the node YAML from the tracker node and complete the node once its goals and verification are satisfied.
```

Each node gets a separate worker. Node completion does not constitute independent QA or production acceptance.

### YAML inter-agent communication

```text
Plan YAML → SKILL.md
               ├→ WORKER.md → node YAML
               ├→ WORKER.md → node YAML
               └→ WORKER.md → node YAML
               └→ implementation YAML → QA
```

Files are passed by reference, not through chat or agent return values. No separate assignment wrapper is needed. YAML carries content and evidence; the tracker owns dependencies, ownership, status, and artifact links.

## 6. QA

### Input

The single implementation YAML produced by Implement. QA reads the complete implementation and referenced evidence, not only the most recent node's changes.

### Output: `qa-<n>.yaml`

```yaml
definition: .honeycomb/task-123/definition-001.yaml
implementation: .honeycomb/task-123/implementation-001.yaml
implementation_revision: def5678
assessments:
  - criterion: filter-correctness
    evidence:
      - Independently executed the defined filtering checks on def5678.
    finding: Export ignores the active date-range filter.
  - criterion: maintainability
    evidence:
      - Reviewed export and search filtering implementations.
    finding: Export duplicates filtering logic instead of using the established path.
human_review:
  - interaction-quality
```

Every applicable success and failure criterion receives an assessment; this example is abbreviated. Findings describe observed discrepancies and supporting evidence, not repair nodes or prescribed patches. Human-owned assessments remain human-owned.

### Procedure

```text
Read the approved definition and its context in a fresh agent context.
Read the implementation YAML and its referenced evidence, and inspect the complete implementation.
Independently execute applicable deterministic verification and perform the required agent assessments. Do not accept implementer claims as sufficient evidence.
Assess both success criteria and failure criteria against the identified implementation revision.
Write concrete findings, criterion assessments, and evidence to QA YAML. Identify criteria requiring human review without inventing a human verdict.
Link the review artifact in the tracker. Leave repair decomposition to Plan.
```

## 7. Human review

### Input

QA YAML with no outstanding implementation findings.

### Output: `review-<n>.yaml`

```yaml
definition: .honeycomb/task-123/definition-001.yaml
qa: .honeycomb/task-123/qa-002.yaml
implementation_revision: def5678
assessments:
  - criterion: interaction-quality
    evidence:
      - The human exercised the export interaction against the agreed references.
    finding: The export action is unnecessarily difficult to discover.
```

The YAML records human observations and findings faithfully. The tracker owns the decision to approve the identified implementation revision or request changes. An approved review has no outstanding findings; YAML does not duplicate the tracker approval flag.

### Procedure

```text
Read the definition, complete implementation evidence, and independent QA review.
assert required automated and agent assessments are satisfied for the implementation under review
Present the implementation and evidence to the human, including the human-owned criteria and taste constraints.
wait:<the human has reviewed the implementation and provided a decision and any findings>
Write the human assessments and findings to review YAML without converting them into repair assignments.
Associate the human decision and review artifact with the reviewed revision in the tracker.
```

Findings go to Plan. Approval permits Ship. Human review does not merge.

## 8. Ship

### Input

Human review YAML for an implementation approved in the tracker.

### Output: `ship-<n>.yaml`

```yaml
review: .honeycomb/task-123/review-002.yaml
implementation_revision: def5678
merge_reference: https://example.invalid/project/pull/123
```

### Procedure

```text
Read the human review YAML and its referenced QA evidence.
assert the implementation being shipped is the implementation independently reviewed and approved by the human in the tracker
Merge using the agreed project procedure.
Write the ship YAML and link it from the production's tracker record.
```

Ship ships approved work. It does not conduct human review or produce repair findings.

## Feedback flow

```text
Plan → Implement → QA
                   ├─ findings → Plan
                   └─ no findings → Human review
                                    ├─ findings → Plan
                                    └─ approved → Ship
```

Plan handles both QA findings and human findings using the same planning procedure. Every repair node gets a fresh implementation agent, and QA independently assesses the complete revised implementation again before human review.

There is no separate retry policy, non-progress detector, blocked-work protocol, or repair-planning skill.
