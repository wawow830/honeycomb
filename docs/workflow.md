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
| Numbered list | Execute the steps in order. |
| `skill:<name>` | Load the named skill's instructions. |
| `run:<prompt>` | Start an agent with the prompt. Returns nothing. |
| `wait:<until-condition>` | Wait until the condition holds. |
| `if <condition>` / `else` | Execute the applicable block. |
| `parallel` | Execute the indented actions concurrently. |
| `while <condition>` | Execute the indented block while the condition holds. |
| `assert <condition>` | Require the condition to hold before proceeding. |
| `<var-name> = <value>` | Assign a value. |

Every dispatched agent receives exactly:

```text
/skill:<specific-skill> <YAML_FILE>
```

`run:` starts work; `wait:` synchronizes it. A numbered step containing `run:` does not implicitly wait for the agent to finish.

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

Git contains the implementation and production artifacts. `.honeycomb/` is not gitignored. Production work uses its own branch; the branching and workspace strategy is settled before Idea finishes.

## Adapters

Skills describe abstract operations. Project adapters translate them into concrete operations without changing their meaning.

Examples:

- `run:<prompt>` means start an agent with that prompt; `HARNESS.md` can translate it into `herdr agent start …`.
- `ticket:<id>` references a tracker work item; `TRACKER.md` can translate it into the relevant GitHub or Linear reference.
- Taking a frontier node means selecting a node with satisfied dependencies and taking ownership so another worker cannot take the same node. The tracker adapter supplies the concrete procedure.
- `MODELS.md` supplies model selection for the work being dispatched.

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

### Input

The human's idea, not a YAML file.

### Output: `idea.yaml`

```yaml
id: task-123
idea: Allow users to export their filtered search results.
references:
  - docs/product/search.md
branching:
  base: main
  production: task-123
  workspace_strategy: Separate worker workspaces and branches for parallel work.
```

The branching fields record the agreed strategy; they do not prescribe one universal strategy.

### Procedure

1. Capture the idea and its supporting references from the human.
2. Load the project adapters needed for this production.
3. Settle the production branch and worker workspace strategy with the human.
4. Create the production's tracker record and branch using that strategy.
5. Write `idea.yaml`.

## 2. Validate

### Input

Idea YAML.

### Output: `validated-<n>.yaml`

```yaml
idea: .honeycomb/task-123/idea.yaml
intent: Export exactly the results matching the user's current search filters.
scope:
  - The existing search-results interface and export endpoint.
taste:
  - Follow the existing results-toolbar interaction and visual patterns.
repository:
  - path: src/search/
    relevance: Filtering, result retrieval, and toolbar implementation.
  - path: tests/search/
    relevance: Existing compatibility and interaction coverage.
constraints:
  - Preserve existing permissions and filtering semantics.
verification:
  - method: Run the existing search compatibility checks.
    baseline: Passing on the production's starting revision.
references:
  - docs/product/search.md
```

The fields are an outline, not a limit on reconnaissance. Include the concrete facts downstream work needs: interfaces, commands, patterns, prerequisites, research sources, and agreed decisions where relevant.

### Procedure

1. Read the idea and its references.
2. Reconnoiter the relevant repository areas and verification infrastructure.
3. Research externally when answering the idea's questions requires it.
4. Validate the idea and intended experience with the human, including taste and unwanted approaches.
5. Answer downstream questions about scope, constraints, prerequisites, implementation context, and verification. Resolve material uncertainty rather than passing it downstream.
6. Write the validated YAML with specific navigation and instructions, not a general repository essay.

## 3. Define

### Input

Validated YAML.

### Output: `definition-<n>.yaml`

```yaml
id: task-123
validated: .honeycomb/task-123/validated-001.yaml
objective: Let users export their current filtered search results.
goals:
  - id: useful-export
    description: Produce an export usable in the user's existing workflow.
non_goals:
  - Scheduled or recurring exports.
success_criteria:
  - id: filter-correctness
    requirement: Exported records match the active filters and permissions.
    assessment: deterministic
    method: Exercise the established filtering and permission cases.
    evidence: Passing check results tied to the implementation revision.
  - id: maintainability
    requirement: Reuse established search behavior without unnecessary abstractions.
    assessment: agent
    method: Review against the repository patterns identified in validation.
    evidence: Independent review with relevant code references.
  - id: interaction-quality
    requirement: The export interaction meets the agreed toolbar behavior and taste.
    assessment: human
    method: Review the implemented interaction against the agreed references.
    evidence: Human review of the implementation revision.
failure_criteria:
  - id: unauthorized-export
    requirement: Export exposes records the user cannot access.
    assessment: deterministic
    method: Exercise the established access-control cases.
    evidence: Results identifying any unauthorized records returned.
```

Assessment methods are not restricted to a closed list. Goals may also carry assessment information when useful. Success criteria state what must hold; failure criteria state what must not occur.

### Procedure

1. Read the validated context and relevant references.
2. State the objective, goals, non-goals, success criteria, and failure criteria.
3. Give each criterion a specific assessment method and required evidence. Preserve human-owned judgments rather than substituting agent judgments.
4. Check that the definition is bounded, internally consistent, and verifiable.
5. Write the definition YAML and present that exact artifact for human approval through the tracker.
6. `wait:<human approval of this definition artifact>`

Planning requires approval of the referenced definition, not a generic approval of the idea.

## 4. Plan

### Input

An approved definition, or a review YAML containing findings and a reference to the definition.

### Output: `plan-<n>.yaml`

```yaml
definition: .honeycomb/task-123/definition-001.yaml
source: .honeycomb/task-123/definition-001.yaml
assignments:
  - ticket: node-124
    objective: Implement the filtered export endpoint.
    criteria:
      - filter-correctness
      - unauthorized-export
      - maintainability
    instructions:
      - Reuse the existing filtering and permission path identified in validation.
      - Add coverage for the established filtering and access-control cases.
      - Run the relevant verification and record the results.
    context:
      - src/search/
      - tests/search/
```

For repair planning, `source` references the review artifact. Dependencies live only in the tracker. Instructions reference definition criteria instead of restating them.

### Procedure

1. Read the approved definition and validated context.
2. If the input is a review, read its findings and implementation evidence.
3. Divide the required work into small, bounded, independently verifiable outcomes.
4. Create the work items and dependency edges in the tracker. Integration, if needed, is an ordinary node with its own instructions and verification.
5. Give each node specific instructions, relevant context, applicable criteria, and verification work. Establish the prerequisites that make it executable when it reaches the frontier.
6. Check that the graph is acyclic and collectively covers the required work.
7. Write the plan YAML and associate its assignments with the tracker nodes.

## 5. Implement

### Input

Plan YAML.

### Output: `implementation-<n>.yaml`

```yaml
definition: .honeycomb/task-123/definition-001.yaml
plan: .honeycomb/task-123/plan-001.yaml
implementation_revision: def5678
evidence:
  - .honeycomb/task-123/implementation/node-124.yaml
  - .honeycomb/task-123/implementation/node-125.yaml
  - .honeycomb/task-123/implementation/node-126.yaml
```

Implement covers the entire process from the plan to the complete implementation. It may produce intermediate node YAML files, but finishes with one YAML file for QA. Evidence references preserve the detail without copying node results or the tracker DAG.

### Procedure

1. Read the plan and its approved definition.
2. While the plan has unfinished work in the tracker:
   1. If there is open frontier work, start separate node agents, each with `/skill:<node-skill> <plan-YAML>`. Use parallel execution for independent work when it reduces time without compromising quality.
   2. `wait:<a running node agent has finished>`
3. Assert that all nodes are complete and their implementation is present on the production branch. Integration work, when needed, has already been executed as ordinary DAG nodes.
4. Write one implementation YAML identifying the complete implementation revision and referencing the node evidence.

### Node agent procedure

Each node agent reads the plan YAML and writes `implementation/<node-id>.yaml`.

```yaml
plan: .honeycomb/task-123/plan-001.yaml
ticket: node-124
implementation_revision: abc1234
changes:
  - Added the export endpoint using existing filtering and permission behavior.
evidence:
  - criterion: filter-correctness
    method: Existing filtering cases plus export coverage.
    result: All cases passed.
    reference: .honeycomb/task-123/evidence/node-124-tests.txt
```

1. Resolve the production through the plan's definition reference and use the tracker to take the next open frontier node belonging to this plan.
2. Read that node's assignment, the applicable definition criteria, and the necessary referenced context.
3. Use the workspace established by the production's branching strategy.
4. Implement this node only, following its instructions and the repository's established patterns.
5. Run the relevant external verification and use its feedback to satisfy the assignment.
6. Record the implementation revision and concrete verification evidence in the output YAML.
7. Link the output from the tracker node and complete the node once its assignment is satisfied.

Each node gets a separate implementation agent. Node completion does not constitute independent QA or production acceptance. A check result is evidence, not a copy of tracker work status.

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

1. Read the approved definition and its context in a fresh agent context.
2. Read the implementation YAML and its referenced evidence, and inspect the complete implementation.
3. Independently execute applicable deterministic verification and perform the required agent assessments. Do not accept implementer claims as sufficient evidence.
4. Assess both success criteria and failure criteria against the identified implementation revision.
5. Write concrete findings, criterion assessments, and evidence to QA YAML. Identify criteria requiring human review without inventing a human verdict.
6. Link the review artifact in the tracker. Leave repair decomposition to Plan.

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

1. Read the definition, complete implementation evidence, and independent QA review.
2. Assert that required automated and agent assessments are satisfied for the implementation under review.
3. Present the implementation and evidence to the human, including the human-owned criteria and taste constraints.
4. `wait:<the human has reviewed the implementation and provided a decision and any findings>`
5. Write the human assessments and findings to review YAML without converting them into repair assignments.
6. Associate the human decision and review artifact with the reviewed revision in the tracker.

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

1. Read the human review YAML and its referenced QA evidence.
2. Assert that the implementation being shipped is the implementation independently reviewed and approved by the human in the tracker.
3. Merge using the agreed project procedure.
4. Write the ship YAML and link it from the production's tracker record.

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
