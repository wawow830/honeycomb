---
name: validate
description: "Determine with the human whether the idea is worth pursuing and feasible."
disable-model-invocation: true
---

```text
`Read` `input`.
`Read` its references.
`Read` `//honeycomb/HARNESS.md`.
`Write` `=/validate/`.

- `Agent Spawn` `recon_id` `recon_model` `=/` `/skill:recon <input>`.
- `Agent Spawn` `research_id` `research_model` `=/` `/skill:research <input>`.

`Wait` agent `recon_id` is finished and agent `research_id` is finished.
`Assert` agents `recon_id` and `research_id` completed their assigned prompts normally.
`Read` `=/validate/recon.yaml` and `=/validate/research.yaml`.
`Determine` with human whether idea is worth pursuing and feasible, resolving scope and tradeoffs using the findings.
`Write` `=/validate/validate.yaml` using `^/TEMPLATE.yaml`.
```
