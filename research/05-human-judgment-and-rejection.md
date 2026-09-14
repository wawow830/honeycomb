# Cases: what humans accepted, changed, and rejected

These cases counterbalance successful demos with inspectable repair and rejection histories. They occurred in **2025**, so they are evidence of mechanisms and concrete outcomes—not current model capability ceilings. [Sources](sources.md#ghostty)

## A. Ghostty: the original UI approach did not survive

**Work:** replace disruptive macOS update windows with unobtrusive in-terminal update notifications. **Outcome:** [PR #9116](https://github.com/ghostty-org/ghostty/pull/9116) merged October 10, 2025, after 21 commits spanning October 8–10. The merged diff covers 21 files. Source, tests, selected public Amp transcripts, and the maintainer’s account were inspected; the macOS application was not run here.

### The actual development sequence

Mitchell Hashimoto selected Sparkle’s custom-driver interface and initially requested UI planning rather than asking an agent to implement the whole feature at once.

An agent built a titlebar accessory. Manual use exposed hit-testing problems with native tabs. The agent tried changing the hit region and layer ordering. Hashimoto’s response to an apparent fix was: **“It’s no longer showing up at all.”** Further attempts still conflicted with platform behavior.

The human then changed the design: use a bottom-right overlay for incompatible window styles. The merged code disables the titlebar update accessory for the affected styles and selects the alternative. This is a successful **change in approach**, not evidence that the agent solved the original layout requirement.

The backend also required intervention. Hashimoto’s account says he discarded the first implementation and manually redesigned the state representation as a tagged union. That rejection is reported by him; the inspected backend transcript alone does not show the later manual rewrite.

During final review, the human stopped an agent’s concurrency-related changes—“Undo all the main actor stuff”—and rejected destructive truncation of error strings in favor of presentation-level handling.

### Feedback artifacts—and their limits

The merged repository includes state/view-model tests and an update simulator with cancellation and error scenarios. A simulator makes otherwise inconvenient states reachable for inspection, but the presence of seven scenarios does not mean seven end-to-end tests were executed successfully.

The final agent summary names a `ProgressTests.swift` file absent from the merged PR’s file list. The visible final build command pipes `zig build` into `tail`; an empty output and successful pipeline status are not independently robust evidence of a successful build, much less executed unit tests. Later human edits may explain differences between the summary and the merged artifact. **Read the final artifact, not just the agent’s completion report.**

Hashimoto reports about eight hours and $15.98. Those are author estimates, not independently audited effort or evidence of a counterfactual speedup. Merge is verified; delivery in a stable release was not separately verified here.

### Applicability

For UI and platform work, this case shows a human selecting layout, deciding what behavior is acceptable, changing a failing approach, and simplifying architecture. Agents supplied implementations and iterations. It fits the brief’s human taste authority; it does not establish that the same amount of human code involvement is always required.

It transfers best where the developer can inspect target-platform behavior and is allowed to revise the design. It does not justify claiming that a non-negotiable original requirement was met by delivering a different one.

## B. GRDB.swift: a small patch still externalized unfinished work

**Work:** fix Linux linkage involving SQLite snapshot APIs. **Outcome:** [PR #1795](https://github.com/groue/GRDB.swift/pull/1795), opened July 19, 2025, closed unmerged the same day. One commit replaced six lines across five files. The PR disclosed Claude Code generation. No public agent transcript or execution log substantiated its compatibility claims. [Sources](sources.md#grdb)

The patch changed production feature guards to exclude ordinary Linux builds while retaining explicit snapshot opt-in. The maintainer’s response was not simply “AI is unwelcome”:

> “The idea is worth pursuing, but the execution is lacking.”

He asked the contributor to check the generated changes and follow the submission checklist rather than expecting him to instruct the bot. The PR also targeted `master` while the checklist requested `development`, testing, and a successful smoke test.

Source inspection reveals a separate integration concern: production guards were changed, but the snapshot tests retained the old guards and still called the affected API. **This mismatch was not rerun or identified by the maintainer as the reason for rejection.** GitHub returned no check runs for the head commit; that does not prove no local testing occurred.

A 2026 rejection study supplied this lead. Reading the actual discussion qualifies a superficial “anti-AI rejection” interpretation: the idea was welcome, while unfinished validation and contribution requirements were not. This one PR cannot establish a general rejection rate.

**Applicability:** tiny diffs can still require platform verification, corresponding test changes, and integration ownership. Neither small patch size nor a convincing PR description demonstrates readiness. There is no recorded repair in this PR and no measured maintainer labor time.

## C. curl: a convincing crash in the wrong program

**Work:** investigate a reported security defect. **Outcome:** [HackerOne #3242005](https://hackerone.com/reports/3242005), July 9, 2025, classified Not Applicable. Original report, public discussion, and contemporaneous curl source were inspected; the reproducer was not executed. [Sources](sources.md#curl)

The report alleged a use-after-free in curl’s OpenSSL keylog callback. Its demonstration linked OpenSSL, **not libcurl**, freed an object, and manually called its own callback on that freed object.

Three maintainers engaged. One asked why the demonstration did not use libcurl; another requested a curl example. Daniel Stenberg pointed out that the alleged `SSL_get_ex_data()` access did not exist in libcurl. The actual callback discards the `ssl` parameter and forwards the log line. The reporter eventually conceded that the demonstration did not affect libcurl directly. No curl fix resulted.

**Attribution limit:** the reporter acknowledged ChatGPT assistance for writing and severity classification but claimed manual discovery. There is no public transcript establishing that an agent generated the faulty reproducer. This is an **AI-assisted invalid report**, not proven autonomous-agent misconduct.

The roughly four-and-a-half-hour interval until closure is elapsed time, not human labor. The record demonstrates three maintainers’ involvement, not their total time spent.

### Counterevidence: AI-associated findings can be valid

Later in 2025, [report #3294999](https://hackerone.com/reports/3294999) supplied a reproducer exercising curl’s actual cookie-handling path. The [official advisory for CVE-2025-9086](https://curl.se/docs/CVE-2025-9086.html) credits Google Big Sleep and Stenberg and records a fix in curl 8.16.0. The advisory and report were inspected, not rerun. Stenberg’s October account also acknowledged useful AI-assisted findings.

**Applicability:** require the demonstrated failure to reach the actual target under the claimed conditions. A plausible explanation, crash trace from substitute code, or authoritative severity label does not establish that. Conversely, AI provenance is not grounds to dismiss a reproducible defect. The difference is the evidence connecting claim, target, and behavior.
