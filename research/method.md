# Research method and misinformation checks

**Research date:** 2026-09-14. **Question:** How are developers actually achieving fast, high-quality agent-assisted development, what makes it work, and where does it fail?

This rewrite replaces the earlier broad literature summary. It is an **artifact-led, purposive case investigation**, not a systematic review, representative survey, or selection of a preferred workflow.

## Selection

Search covered current 2025–2026 material. Cases were chosen for inspectable work and useful contrasts: existing code versus new work; public libraries versus an internal codebase; interactive versus unattended execution; accepted changes versus failed approaches and rejected submissions.

The seven cases are sqlite-utils, Moebius, a compiler experiment, Stripe, Ghostty, GRDB.swift, and curl. Two involve the same developer; those are not independent evidence about developer populations. The cases span several stacks but do not validate a stack-independent implementation.

An older case with an actual diff and review history was preferred over a recent unsupported productivity headline. Case dates remain prominent; 2025 failures are not described as the ceiling of September 2026 models.

## Investigation procedure

1. Discover reports through SearXNG, then follow original project, study, or developer links rather than treating summaries as evidence.
2. Identify the actual unit of work and inspect linked PRs, revisions, transcripts, code, tests, and reviewer responses where available.
3. Reconstruct human decisions, agent actions, available feedback, failure, repair, and acceptance. Separate the final artifact from intermediate generated output.
4. Seek contradictory evidence within the same record and from later outcomes. Read stated limitations, not only success sections.
5. Reproduce a bounded claim where feasible: sqlite-utils’ query regressions on pinned before/after revisions, plus an additional contract probe.
6. Write conditional applicability and missing prerequisites. Do not infer a speedup, optimal agent count, or approval policy from a successful example.

One parallel investigation covered Ghostty, GRDB, and curl. Its output was an evidence dossier with primary links and inspection limits, not a second vote confirming the same conclusions. A later review checked the case notes. The SQLite recipe itself was rerun from the Markdown instructions.

Tools: SearXNG, Trafilatura, w3m, direct GitHub/HackerOne APIs, source archives, and sandboxed Python tests. No real accounts, production resources, or upstream repositories were modified.

## Discovery queries, retained for transparency

Representative queries from this pass:

- `Simon Willison coding agent real project transcript tests 2026`
- `AI coding agent production case study failure pull request 2026 developer`
- `site:simonwillison.net 2026 "port" "transcript"`
- `site:simonwillison.net 2026 "bug" "transcript"`
- `site:anthropic.com engineering building c compiler agents 2026 tests gcc`
- `"claudes-c-compiler" "tests" "missing"`
- `agent developer workflow 2026 real traces refactoring migration Stripe minions Spotify honk`

These are not an exhaustive search strategy; they reveal accessibility and selection bias. Search results led to further artifact inspection, not directly to factual claims.

## Misinformation filters actually applied

| Tempting claim | What inspection changed |
|---|---|
| “The compiler repository documents its integration tests” | The pinned complete tree has no documented `tests/` directory, and a human warning says generated docs may be false. |
| “The agent’s final summary proves those tests shipped” | A Ghostty test file named in a summary is absent from the merged PR file list. |
| “One-shot means no iteration or human review” | Stripe describes local loops, bounded CI repair, human scrutiny, and possible manual completion. |
| “The fix passes all its new tests, so the documented guarantee holds” | The local sqlite-utils PRAGMA probe exposes a qualification not checked by those passing tests. |
| “The maintainer rejected the idea because AI wrote it” | GRDB’s actual response welcomes the idea but objects to execution and submission quality. |
| “A convincing crash report establishes a curl defect” | The invalid demonstration did not use libcurl; contemporaneous source contradicts its attribution. |
| “AI-associated curl reports are all useless” | A later target-specific report and official advisory document a credited, resolved defect. |
| “PR count or a token bill proves productivity” | Attempt counts, comparable accepted scope, human work, infrastructure, and downstream defects are missing. |

These are not accusations that every misleading claim was intentionally deceptive. Some arise from incomplete summaries, changed artifacts, definitions, or honestly mistaken reports.

## Retrieval problems and evidence boundaries

- Text extraction sometimes omitted substantive content. Stripe initially returned only metadata/biography; complete article Markdown was recovered from embedded page data. Anthropic’s list of compiler limitations required the fuller text view.
- Some transcript tool details were collapsed or truncated. The register states what was actually visible; no claim is made to have audited every command or token.
- Automatically inferred dates are not reliable. PR timestamps, pinned revisions, visible dates, and stated study periods were preferred; an old event discovered through a 2026 paper remains an old event.
- Screenshots and author assertions are not substitutes for execution. Only the stated SQLite checks were executed locally.
- Several artifacts were themselves agent-authored. They can reveal the process but cannot independently certify their own correctness.

## Remaining limits

Success/publication bias, English-language and search-index bias, incomplete private-system visibility, and substantial reliance on unusually experienced maintainers. Failure examples were deliberately sought, so the collection is not a balanced estimate of success frequency either.

Long-term maintenance, production incidents, organizational learning, requirements discovery, and operations remain weakly covered. There is no controlled local agent-productivity experiment, multi-agent cost comparison, or complete security/taste evaluation.

## September 15 ingestion supplement

[Project harnesses and pstack](08-project-harness-and-pstack.md) follows three user-supplied X links rather than a new discovery search. The three articles represent two author accounts. Direct X HTML exposed the article bodies; structured FxTwitter responses supplied embedded code, link destinations, and modification metadata. Neither transport is counted as independent corroboration. Images were not visually audited.

Follow-up inspection covered Semet's linked taxonomy and selected public pstack/Atlas artifacts, pinned to their current revisions. Those snapshots are not assumed to match publication-time versions. Atlas's complete tree and explicit README disclaimer establish that its driver is intentionally absent. After source inspection, a bounded local probe ran pstack's plan validator on its own unfilled skeleton; it passed. This establishes a structural-check limitation, not that the operational workflow accepts unfinished plans. No pstack installation, live agent run, private product access, or cloud provisioning was performed.

The supplement distinguishes transferable mechanisms from vendor/model policies and compares them with the now-existing `WORKFLOW.md` without modifying it. The original cases and their research-date conclusions remain historical; the only additional execution is the documented validator probe.

**The result is concrete evidence about particular practices and boundaries—not proof of exceptional speed without compromise.** The source register and reproduction record make the strongest claims inspectable and the missing evidence explicit.
