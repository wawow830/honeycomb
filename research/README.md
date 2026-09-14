# Agent-assisted development: concrete cases, not a workflow

**Research date: 2026-09-14.** This replaces the earlier broad survey with development histories, code/test inspection, failure cases, and a local reproduction.

> **How are developers actually achieving fast, high-quality agent-assisted development, what makes it work, and where does it fail?**

The brief remains: exceptional speed without sacrificing quality or taste; maximum practical determinism; explicit boundaries and structure; stack independence; simplicity. **Only humans decide taste. Other human involvement remains undecided.** No workflow, framework, agent count, or approval policy is adopted here.

## Start with the cases

| Work | What the evidence reveals | Read |
|---|---|---|
| Hardening a database-library release | Agent review found real defects; repair introduced others. Old query tests passed despite broken semantics. | [sqlite-utils](01-release-hardening.md) |
| Porting an existing model into a browser | Reference comparisons enabled progress; Safari and deployment exposed failures those comparisons could not catch. | [Moebius](02-browser-port.md) |
| Building a compiler with sixteen agents | Parallel work stalled on a shared blocker; changing failure localization made separate work possible. Public source is not the complete verification harness. | [Compiler](03-parallel-compiler.md) |
| Unattended changes in a large existing codebase | Stripe reports a combination of programmed steps, agent implementation, bounded retries, inherited infrastructure, and human review. Internal traces are unavailable. | [Stripe](04-unattended-maintenance.md) |
| Shipping a native-app feature | A human discarded generated code, redesigned state, and changed the UI approach after repeated failed fixes. | [Ghostty](05-human-judgment-and-rejection.md) |
| Submitting a small compatibility fix | Six line replacements still left integration and submission work unfinished; the maintainer rejected it. | [GRDB.swift](05-human-judgment-and-rejection.md) |
| Investigating security reports | One plausible demonstration did not use the alleged vulnerable library; a later AI-associated report reached real code and led to a fix. | [curl](05-human-judgment-and-rejection.md) |

## The strongest directly checked result

For sqlite-utils PR #768, this review ran pinned before/after code in an isolated environment:

- Old code, old query tests: **5 passed**.
- Old code, revised query tests: **9 failed, 8 passed**.
- Fixed code, the same revised tests: **17 passed**.

An additional probe still found a qualification to the documented guarantee. This is evidence that the repair addressed particular failures—not that the library became defect-free. [Commands, revisions, environment, and results](06-reproduction.md).

## What the cases suggest

The useful changes were often specific: check persistence through another connection; provide a working reference; expose hard-to-reach UI states; inspect the real browser; isolate independently diagnosable failures; stop repeating an unsuccessful approach; make a human product decision.

That is more applicable than “use more agents,” “write better specs,” or “add review.” Each intervention has prerequisites and a boundary beyond which it does not establish quality. [Cross-case findings and unresolved choices](07-findings.md).

**No defensible universal speed multiplier emerges.** These records show useful work, plausible acceleration mechanisms, and real costs—but not complete, comparable accounting of accepted output, failed attempts, human attention, infrastructure, and long-term quality.

## Audit the research

- [Source and artifact register](sources.md): exact links, pinned revisions, what was inspected, and what was not.
- [Method and misinformation checks](method.md): selection, searches, exclusions, extraction problems, and limits.

The seven cases are deliberately selected, not a representative sample. Vendor deployment reports, maintainer accounts, public artifacts, and locally executed checks are kept distinct. The aim is to establish what is worth considering **before** designing the workflow with you.
