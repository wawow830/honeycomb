---
name: honeycomb
description: "Use agentic coding in software development"
disable-model-invocation: true
---

Unbulleted instructions execute in order.
Consecutive bullet-point instructions at the same indentation execute in parallel.

| Form | Meaning |
| --- | --- |
| `skill:<name>` | Load the named skill's instructions. |
| `spawn:<agent> <prompt>` | Start the agent with the prompt without waiting. Model slug comes from `honeycomb/MODELS.md`. Returns nothing. |
| `wait:<until-condition>` | Wait until the condition holds. |
| `if <condition>` / `else` | Execute the applicable indented block. |
| `while <condition>` | Execute the indented block while the condition holds. |
| `assert <condition>` | Require the condition to hold before proceeding. |
| `<var-name> = <value>` | Assign a value. |
