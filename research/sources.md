# Sources and artifact register

Original cases accessed **2026-09-14**; [project harness and pstack supplement](#project-harness-and-pstack) accessed **2026-09-15**. Grouped by evidence chain, not counted as independent corroboration merely because a story has several URLs. A blog, its transcript, and its PR can all describe the **same event**.

**Inspection labels:** “read” means the material was retrieved and examined; “executed” means the specific check was run locally. An agent-authored note or execution summary is attributed evidence, not independent confirmation.

## sqlite-utils

**July 4–5, 2026; existing-library release work.** Used in [01](01-release-hardening.md) and [06](06-reproduction.md).

- **Maintainer account, July 5:** [sqlite-utils 4.0rc2, mostly written by Claude Fable](https://simonwillison.net/2026/jul/5/sqlite-utils-fable/). Read full article, including human interventions, additional review, and cost definition.
- **Initial agent review:** [pinned review document](https://github.com/simonw/sqlite-utils/blob/0c369a447eeaf39084f0d14a45b3eeb7eacb631b/fable-review-4.0rc1.md). Read; findings are agent claims unless separately checked.
- **Release-review changes:** [PR #767](https://github.com/simonw/sqlite-utils/pull/767). GitHub API metadata/body inspected; confirms merge, 34 commits, 30 changed files, +1,321/−190 lines. The 37-prompt figure comes from the maintainer, not Git metadata.
- **Follow-up repair:** [PR #768](https://github.com/simonw/sqlite-utils/pull/768). Metadata, complete patch, documentation, and tests inspected. PR body records attribution to GPT-5.5 review and Claude repair.
- **Before:** [implementation at `04f8971`](https://github.com/simonw/sqlite-utils/blob/04f8971546418962aaf6579d4028c7117d6c3a20/sqlite_utils/db.py) · [old tests](https://github.com/simonw/sqlite-utils/blob/04f8971546418962aaf6579d4028c7117d6c3a20/tests/test_query.py).
- **After:** [implementation at `0566a9f`](https://github.com/simonw/sqlite-utils/blob/0566a9f128e19475f5cb423043820fb4119051cc/sqlite_utils/db.py) · [revised tests](https://github.com/simonw/sqlite-utils/blob/0566a9f128e19475f5cb423043820fb4119051cc/tests/test_query.py) · [API contract](https://github.com/simonw/sqlite-utils/blob/0566a9f128e19475f5cb423043820fb4119051cc/docs/python-api.rst).
- **Executed:** query tests on both snapshots, old tests on old code, and the extra PRAGMA probe. See [environment, results, hashes, and commands](06-reproduction.md).

**Limit:** no original model session rerun, independent cost audit, full CI recreation, or evaluation of later releases. Remote Claude session links in the article were not used as inspected transcript evidence.

## moebius

**June 22, 2026; exploratory model/browser port.** Used in [02](02-browser-port.md).

- **Developer account:** [Porting the Moebius 0.2B image inpainting model to run in the browser](https://simonwillison.net/2026/Jun/22/porting-moebius/). Read, including limited code inspection/learning and publication process.
- **Public conversation export:** [rendered transcript](https://gisthost.github.io/?58039ba5c1ca3ed177e8659168996ee4) · [pinned gist revision](https://gist.github.com/simonw/58039ba5c1ca3ed177e8659168996ee4/7e9e6fba66d274dd517eb2a6052216c58345d02d). The full `index.html` conversation index was retrieved through GitHub’s API and examined, including turns 27–34. Tool-detail pages were not all read; some API responses for them were truncated. Reported numerical validation is not an independently rerun result.
- **Discovery notes:** [pinned `notes.md`](https://github.com/simonw/moebius-web/blob/080be6e737ec976130e260d34707d7d9b7f63d5b/notes.md). Read: reference inference, parity strategy, target/browser failures, and remaining uncertainties. Agent-written.
- **Actual repair:** [cache and deferred-download commit `05c1cbc`](https://github.com/simonw/moebius-web/commit/05c1cbc4894460a70a8bc1718ac6d152219e0f28). Full patch inspected, including `modelcache.ts`, event handlers, and UI text.

**Limit:** model weights were not downloaded and browser inference/parity were not executed. Transcript assertions about numerical accuracy, runtime, or browser API behavior remain attributed unless corroborated by the inspected code.

## compiler

**February 5, 2026; vendor capability experiment.** Used in [03](03-parallel-compiler.md).

- **Experiment report:** [Building a C compiler with a team of parallel Claudes](https://www.anthropic.com/engineering/building-c-compiler), Nicholas Carlini / Anthropic. Read full report, including limitations omitted by initial automated extraction.
- **Published snapshot:** [repository at `6f1b99a`](https://github.com/anthropics/claudes-c-compiler/tree/6f1b99acb2f4ec2414592136c2009fe7713deec3).
- **Inspected files:** [README](https://github.com/anthropics/claudes-c-compiler/blob/6f1b99acb2f4ec2414592136c2009fe7713deec3/README.md) · [Cargo features](https://github.com/anthropics/claudes-c-compiler/blob/6f1b99acb2f4ec2414592136c2009fe7713deec3/Cargo.toml) · [outstanding kernel-link task](https://github.com/anthropics/claudes-c-compiler/blob/6f1b99acb2f4ec2414592136c2009fe7713deec3/current_tasks/fix_x86_standalone_kernel_link_errors.txt).
- **Completeness check:** [recursive Git tree](https://api.github.com/repos/anthropics/claudes-c-compiler/git/trees/6f1b99acb2f4ec2414592136c2009fe7713deec3?recursive=1) returned `truncated: false` and no `tests/` directory.

**Limit:** source snapshot is not the private development harness. No compiler build, Linux boot, performance comparison, or claimed suite pass rate was rerun. Demo limitations and snapshot documentation are different pieces of evidence, not interchangeable statements of current capability.

## stripe

**February 9 and 19, 2026; production engineering field reports.** Used in [04](04-unattended-maintenance.md).

- Alistair Gray: [Minions: Stripe’s one-shot, end-to-end coding agents](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents).
- Alistair Gray: [Part 2](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2).

Both complete article bodies were read after extracting Markdown strings embedded in page data. Ordinary text extraction initially returned metadata and author biography only. Includes unattended execution, human review, inherited environments, deterministic/agent nodes, scoped context/tools, and bounded CI iteration.

**Limit:** Stripe is describing its own private system. No actual internal PR, source implementation, trace, independent cost/defect dataset, or controlled comparison was available in the inspected material. Public Goose source is not evidence that Stripe’s private fork behaves identically. Reported scale is not a measured productivity gain.

## ghostty

**October 8–10, 2025 development; maintainer account and public artifacts.** Used in [05](05-human-judgment-and-rejection.md).

- Mitchell Hashimoto: [Vibing a Non-Trivial Ghostty Feature](https://mitchellh.com/writing/non-trivial-vibing). Read: failed attempts, manual work, redesign, final review, and estimated cost/time.
- [PR #9116](https://github.com/ghostty-org/ghostty/pull/9116): metadata, commit list, complete file diff, comments and review records inspected.
- **Selected public sessions read:** [initial UI](https://ampcode.com/threads/T-9fc3eb88-5aa2-45e4-8f6d-03697f53102d) · [overlay](https://ampcode.com/threads/T-69675325-c5e3-497a-b692-0176744069e9) · [backend](https://ampcode.com/threads/T-d812d8a2-b7af-47ca-a91b-5ce3a18068b2) · [final review/repair](https://ampcode.com/threads/T-e4cc70f0-d222-4c40-a1e7-745025e3dc9c).
- **Merged artifacts read at `989acac`:** [simulator](https://github.com/ghostty-org/ghostty/blob/989acacbf9654586a96a958f3843b089e1d0b94c/macos/Sources/Features/Update/UpdateSimulator.swift) · [view-model tests](https://github.com/ghostty-org/ghostty/blob/989acacbf9654586a96a958f3843b089e1d0b94c/macos/Tests/Update/UpdateViewModelTests.swift) · [state tests](https://github.com/ghostty-org/ghostty/blob/989acacbf9654586a96a958f3843b089e1d0b94c/macos/Tests/Update/UpdateStateTests.swift) · [terminal view](https://github.com/ghostty-org/ghostty/blob/989acacbf9654586a96a958f3843b089e1d0b94c/macos/Sources/Features/Terminal/TerminalView.swift).

**Limit:** selected transcripts, not every linked session; collapsed intermediate work was not fully expanded. No macOS execution, cost audit, or verification of later stable-release delivery. Human edits after sessions mean the generated and merged artifacts need not coincide.

## grdb

**July 19, 2025; rejected compatibility patch.** Used in [05](05-human-judgment-and-rejection.md).

- [GRDB.swift PR #1795](https://github.com/groue/GRDB.swift/pull/1795): metadata, complete patch and comments inspected.
- [Maintainer response](https://github.com/groue/GRDB.swift/pull/1795#issuecomment-3092461936).
- **Pinned submitted code:** [commit `a011321`](https://github.com/groue/GRDB.swift/commit/a011321b1a6f66c9e70f526f96535e3e2f24edc8) · [unchanged snapshot tests](https://github.com/groue/GRDB.swift/blob/a011321b1a6f66c9e70f526f96535e3e2f24edc8/Tests/GRDBTests/DatabaseSnapshotPoolTests.swift#L1-L25) · [submission checklist](https://github.com/groue/GRDB.swift/blob/a011321b1a6f66c9e70f526f96535e3e2f24edc8/.github/PULL_REQUEST_TEMPLATE.md).
- **Research lead:** [2026 rejection study, v1](https://arxiv.org/html/2602.04226v1). Read to locate the case, then checked the primary PR. Its sample is rejected PRs, not all attempted contributions; its categories are not themselves evidence of the maintainer’s entire motivation.

**Limit:** production/test guard mismatch is source-inspection evidence, not a reproduced Linux failure or the maintainer’s stated diagnosis. No public agent execution transcript; no check runs returned does not establish absence of local tests.

## curl

**July–October 2025; invalid report and later valid counterexample.** Used in [05](05-human-judgment-and-rejection.md).

- **Invalid report:** [HackerOne #3242005](https://hackerone.com/reports/3242005) · [original report JSON](https://hackerone.com/reports/3242005.json). Reproducer and attribution disclosure read. Public discussion retrieved through HackerOne’s GraphQL `report(id: 3242005) { activities ... }`, since the ordinary text view omitted it.
- **Contemporaneous source:** [keylog callback at `784c17b`](https://github.com/curl/curl/blob/784c17b7d98caa9b500a56e345c1aadca9d009ed/lib/vtls/openssl.c#L838-L845). Selected using commit history bounded by submission time; callback read rather than assuming the current branch matched.
- Daniel Stenberg, July 14: [Death by a thousand slops](https://daniel.haxx.se/blog/2025/07/14/death-by-a-thousand-slops/). Context read; broad burden/rate estimates not promoted to independently measured results.
- **Counterexample:** [report #3294999](https://hackerone.com/reports/3294999) · [report JSON](https://hackerone.com/reports/3294999.json) · [official CVE-2025-9086 advisory](https://curl.se/docs/CVE-2025-9086.html). Read; target-specific reproduction/trace and recorded remediation distinguish it from the invalid report.
- Stenberg, October 10: [A new breed of analyzers](https://daniel.haxx.se/blog/2025/10/10/a-new-breed-of-analyzers/). Read as explicit counterevidence to universal negative claims.

**Limit:** neither reproducer executed. AI contribution to the invalid reasoning is not established by a model transcript. Submission/closure timestamps are not labor-time measurements. No general valid/invalid rate is inferred.

## productivity-check

**Methodological checks, not workflow case studies.** Used in [10](10-findings.md).

- METR, **July 10, 2025**: [Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/). Primary report reread: 16 developers, 246 randomized real tasks, 19% longer with allowed AI in that setting; subjective estimates disagreed. Primarily early-2025 Cursor/Claude tools.
- METR, **February 24, 2026**: [We are Changing our Developer Productivity Experiment Design](https://metr.org/blog/2026-02-24-uplift-update/). Primary follow-up reread: selection, participation, compensation, scope, and parallel-agent time-accounting limitations make the magnitude of contemporary uplift unreliable.

**Limit:** no statistical reanalysis or replication. The follow-up does not preserve an eternal slowdown verdict or establish a clean universal reversal. The case studies above were not selected to reproduce either study’s population.

## project-harness-and-pstack

**User-supplied sources; accessed September 15, 2026.** Used in [08](08-project-harness-and-pstack.md). Two author accounts, not three independent outcome studies.

### Article bodies

- Gaetan Semet: [post](https://x.com/gsemetfr/status/2077498943085117460) · [article](https://x.com/i/article/2077494546553044992), **Building Agentic Project Harness**, July 15; structured metadata reports modification August 9. Full prose and code examples read from X HTML and structured article data. The linked Medium copy was not separately inspected.
- Lauren / @poteto: [post](https://x.com/poteto/status/2094457600259842065) · [article](https://x.com/i/article/2094151284949688320), **The Complete Guide to pstack Pt. 1**, August 31. Full body and links read, including cloud-over-worktree recommendation and productivity claims.
- Lauren / @poteto: [post](https://x.com/poteto/status/2097732320606507506) · [article](https://x.com/i/article/2094940651607715840), **The Complete Guide to pstack Pt. 2**, September 9. Full body and links read, including research, prototypes, architecture, and planning examples.
- Semet's acknowledged conceptual source: [Harness engineering for coding agent users](https://martinfowler.com/articles/harness-engineering.html), dated April 2, 2026. Full extracted article read, including behavioral-correctness limits. This is part of Semet's evidence chain, not independent confirmation of his implementation or costs.

**Retrieval:** direct public X HTML contained article bodies. FxTwitter's public API supplied structured article blocks, embedded code, link destinations, and metadata at `https://api.fxtwitter.com/<author>/status/<id>`. This second transport is not an independent source. Images were not visually audited; captions are not independent verification of depicted results. Product/plugin links, private sessions, and every linked skill were not exhaustively investigated.

### Selected public artifacts

Pinned **current-at-inspection**, not asserted to be article-time snapshots:

- `cursor/plugins@be432a96ed36e48d05f44bf375864355f62263f9`: full [creation skill](https://github.com/cursor/plugins/blob/be432a96ed36e48d05f44bf375864355f62263f9/pstack/skills/create-verification-skill/SKILL.md), [maintenance skill](https://github.com/cursor/plugins/blob/be432a96ed36e48d05f44bf375864355f62263f9/pstack/skills/maintain-verification-skill/SKILL.md), [prototype playbook](https://github.com/cursor/plugins/blob/be432a96ed36e48d05f44bf375864355f62263f9/pstack/skills/poteto-mode/playbooks/prototype.md), [architecture skill](https://github.com/cursor/plugins/blob/be432a96ed36e48d05f44bf375864355f62263f9/pstack/skills/architect/SKILL.md), and [multi-phase planning playbook](https://github.com/cursor/plugins/blob/be432a96ed36e48d05f44bf375864355f62263f9/pstack/skills/poteto-mode/playbooks/multi-phase-plan.md) read. Instructions demonstrate intended operation, not actual agent compliance.
- [Plan validator](https://github.com/cursor/plugins/blob/be432a96ed36e48d05f44bf375864355f62263f9/pstack/skills/poteto-mode/scripts/check-plan.mjs): complete source read, then **executed** against the unfilled skeleton from the same revision. Returned zero problems and exit code 0. [Reproduction and interpretation](08-project-harness-and-pstack.md#bounded-local-check-an-unfilled-plan-passes-the-validator). No live agent run or product verification was executed.
- `poteto/verification-skill-example@d5abe70d0d8c671672b6cef4069363f26c488feb`: full [README](https://github.com/poteto/verification-skill-example/blob/d5abe70d0d8c671672b6cef4069363f26c488feb/README.md), [verification skill](https://github.com/poteto/verification-skill-example/blob/d5abe70d0d8c671672b6cef4069363f26c488feb/.cursor/skills/verify-atlas/SKILL.md), [feature index](https://github.com/poteto/verification-skill-example/blob/d5abe70d0d8c671672b6cef4069363f26c488feb/.cursor/skills/verify-atlas/references/features/README.md), and [Preferences map](https://github.com/poteto/verification-skill-example/blob/d5abe70d0d8c671672b6cef4069363f26c488feb/.cursor/skills/verify-atlas/references/features/preferences.md) read. [Recursive tree](https://api.github.com/repos/poteto/verification-skill-example/git/trees/d5abe70d0d8c671672b6cef4069363f26c488feb?recursive=1) returned `truncated: false`; no executable driver. The README explicitly calls Atlas fictional and driver scripts intentionally omitted.

**Limit:** no Grok Bot or Cursor production PR audit, cost/defect dataset, cloud-versus-local benchmark, completed architecture arena, or end-to-end execution of the published verification skills. PR volumes and productivity multipliers remain attributed claims. The plan-validator probe tests structural validation only.

## code-sloppiness-and-measurement

**September 10, 2026 article; accessed September 15, 2026.** Used in [09](09-code-sloppiness-and-measurement.md).

- Sebastian: [If coding is solved, what now?: Measuring the sloppiness of code](https://earendil.com/posts/measuring-code-sloppiness/). Full article read through the public HTML and text extraction, including formulas, footnotes, date, and links. It is a practitioner essay and reports the author's research and tests; the article's broad claims about correctness, industry practice, and code volume were not independently established.
- [SlopCodeBench v1](https://arxiv.org/html/2603.24755v1), [abstract/metadata](https://arxiv.org/abs/2603.24755v1), and [project site](https://www.scbench.ai/). Version 1 was read in full enough to inspect the abstract, protocol, metrics, results, limitations expressed in the methodology, and appendices relevant to the article. The article explicitly links v1. The arXiv landing page reports a later v2 as the latest version; v1 claims were not silently mixed with v2 results. The project site was read; no benchmark run or source checkout was obtained/executed.
- [Bias in the Loop: Auditing LLM-as-a-Judge for Software Engineering](https://arxiv.org/html/2604.16790), linked by the article for the candidate-renaming example. Abstract, introduction, methodology, and reported results were read. It reports prompt/order sensitivity in pairwise code judgments across generation, repair, and test-generation tasks; no judge experiment was rerun and its findings are not treated as proof that AI review is categorically unusable.
- **Executed:** no local code, benchmark, judge, or metric calculation. Images and interactive elements on the article and benchmark site were not visually audited.

**Limit:** SlopCodeBench's verbosity and erosion scores depend on hand-authored AST-Grep rules, clone detection, SLOC/complexity extraction, and a chosen threshold. Its repository comparison is a calibration panel rather than a matched human baseline, and its Python-track synthetic tasks do not establish production maintenance cost. The linked judge study is separate evidence about evaluation sensitivity, not an independent assessment of the Earendil article's benchmark claims.
