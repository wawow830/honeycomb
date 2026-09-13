---
name: honeycomb
description: "Use agentic coding in software development"
disable-model-invocation: true
---

# Honeycomb

Honeycomb turns ideas into shipped software through specialized agents, verification, and human judgment. Skills pass work through YAML; adapters provide project-specific operations.

Idea → Validate → Define → Plan → Implement → QA → Human review → Ship.

## Syntax

### Instructions

Keywords are backticked Titlecase actions, including judgment such as `Compare`. Plain text expresses intent; backticked arguments specify exact content or references.

```text
`Write` code that satisfies condition A and condition B.
`Write` `=/validate/`.
```

- A period outside backticks ends an instruction.
- Instructions run in order; sibling bullet instructions run in parallel.
- Indentation groups conditional and loop bodies.
- A trailing `/` makes `Write` create a directory rather than a file.

### References

| Form | Meaning |
| --- | --- |
| `input` | Supplied YAML file. |
| `//` | Current worktree's repository root. |
| `=/` | Agent working directory. |
| `^/` | Skill directory. |
| `<role>_model` | Model from `//honeycomb/MODELS.md`. |
| `<role>_id` | Unique, stable ID per skill invocation and production/pass. |

Resolve references and `<placeholders>` before tool calls. Explicit assignments override automatic bindings; role names use underscores.

[setup](SETUP.md)
