---
name: validate
description: "Determine with the human whether the idea is worth pursuing and feasible."
disable-model-invocation: true
---

Use the shared meanings in [DICTIONARY.md](../honeycomb/DICTIONARY.md).

1. Read the input YAML and its references.
2. Create `=/pass-<n>/validate/` for the destination pass.
3. Use the project's harness and model adapters to start `recon` and `research` agents in parallel, with the same input and working directory.
4. Wait for both agents to stop, confirm normal completion, then read `=/pass-<n>/validate/recon.yaml` and `=/pass-<n>/validate/research.yaml`.
5. Determine with the human whether the idea is worth pursuing and feasible, resolving scope and tradeoffs using the findings.
6. Write `=/pass-<n>/validate/validate.yaml` using [TEMPLATE.yaml](TEMPLATE.yaml).
