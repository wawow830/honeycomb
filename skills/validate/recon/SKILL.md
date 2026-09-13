---
name: recon
description: "Gather repository findings and verification baselines for validation."
disable-model-invocation: true
---

1. Read the input YAML and its references.
2. Explore repository behavior, conventions, and constraints relevant to the idea.
3. Identify available verification methods and observe their baselines.
4. Write `validate/recon.yaml` in the destination pass directory, recording specific locations and findings for downstream use. Use only `reconnaissance` and `verification` from [TEMPLATE.yaml](../TEMPLATE.yaml).
