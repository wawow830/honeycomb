---
name: recon
description: "Gather repository findings and verification baselines for validation."
disable-model-invocation: true
---

`Read` `input`.
`Read` its references.
`Explore` repository behavior, conventions, and constraints relevant to idea.
`Identify` available verification methods and observe their baselines.
`Record` specific locations and findings for downstream use.
`Write` `=/validate/recon.yaml` using only `reconnaissance` and `verification` from `^/../TEMPLATE.yaml`.
