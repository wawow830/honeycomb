---
name: recon
description: "Gather repository findings and verification baselines for validation."
disable-model-invocation: true
---

Use the shared meanings in [DICTIONARY.md](../honeycomb/DICTIONARY.md).

1. Read the input YAML and its references.
2. Explore repository behavior, conventions, and constraints relevant to the idea.
3. Identify available verification methods and observe their baselines.
4. Write `=/pass-<n>/validate/recon.yaml` for the destination pass, recording specific locations and findings for downstream use. Use only `reconnaissance` and `verification` from [TEMPLATE.yaml](../validate/TEMPLATE.yaml).
