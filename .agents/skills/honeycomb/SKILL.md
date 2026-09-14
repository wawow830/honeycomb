---
name: honeycomb
description: "Use agentic coding in software development"
disable-model-invocation: true
---

Resolve `^/path` from the project root in the current worktree and `=/path` from the production root, `^/.honeycomb/<production-id>/`.
Resolve skill-local references from `.agents/skills/<skill-name>/`.
Resolve path prefixes before passing paths to filesystem tools or adapters.

Read [DICTIONARY.md](DICTIONARY.md).
Follow [SETUP.md](SETUP.md).

Create the production ticket using the project adapters. Use its ID as `<production-id>` when creating the production branch and `^/.honeycomb/<production-id>/`.
Use that branch and production directory, and follow [idea](../idea/SKILL.md) to capture the human's intent.

Create `=/pass-<n>/` using the next unused pass number.
Run Validate → Define → Plan → Implement → QA → Review using separate stage agents and the project's model and harness adapters.
Launch stages in the destination pass directory, supplying each input YAML's resolved absolute path through `/skill:<stage> <YAML_FILE>`. Use the destination pass number for `<n>` in output paths, even when inputs belong to earlier passes.
Use each stage's YAML output as the next stage's input.
Wait for each agent to finish as intended and read its output before proceeding.
Require human approval of the referenced `define` in the tracker before Plan.
Proceed to Review only when QA has no outstanding findings.

For QA findings or human-requested changes, create another pass using the next unused number. Supply the triggering `qa` or `review` to Plan for changes within the approved specification, or to Validate followed by Define for changes to it.
Keep references to unchanged artifacts in their earlier passes.
Clarify withheld review decisions or unclear required changes with the human.

Run Ship in the production directory when the human approves the reviewed result in the tracker, including when feedback is nonblocking.
Supply the approved `review` as its input.
Ship only that approved result and report the delivery results.
