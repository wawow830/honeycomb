---
name: validate
description: "Determine with the human whether the idea is worth pursuing and feasible."
disable-model-invocation: true
---

1. Read the input YAML and its references.
2. Create `validate/` in the destination pass directory.
3. Use the project's harness and model adapters to start `recon` and `research` agents in parallel, with the same input and working directory.
4. Wait for both agents to stop, confirm normal completion, then read `validate/recon.yaml` and `validate/research.yaml` from that directory.
5. Determine with the human whether the idea is worth pursuing and feasible, resolving scope and tradeoffs using the findings.
6. Write `validate/validate.yaml` in the destination pass directory using [TEMPLATE.yaml](TEMPLATE.yaml).
