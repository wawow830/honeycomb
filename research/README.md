# Agent-assisted software development: research

Research date: **2026-09-14**. Status: **evidence review, not an adopted workflow**.

## Brief

For software developers doing software development. The goals are exceptional speed without sacrificing quality or taste, as much determinism as possible, explicit structure, stack independence, and simplicity.

**Taste belongs solely to the human.** This is a requirement from the brief, not a research finding. Human involvement elsewhere—including planning, code review, approvals, and release—remains undecided.

No particular agent count, framework, specification format, approval policy, or vendor was assumed to be the answer.

## Read the research

1. [Productivity and quality](01-productivity-and-quality.md): measured gains, conflicting results, maintenance, comprehension, and review load.
2. [Structure and coordination](02-structure-and-coordination.md): context files, specifications, single/multiple agents, and production experience.
3. [Determinism and verification](03-determinism-and-verification.md): repeatability, environment controls, evaluation validity, and containment.
4. [Open questions and experiments](04-open-questions.md): what the evidence leaves undecided and how to investigate it.
5. [Source register](sources.md): 19 primary sources, dates/versions, evidence types, findings, and limitations.

## Findings in brief

- **There is no defensible universal speed multiplier.** Controlled studies and field observations measure different populations, tools, tasks, and outcomes. Newer evidence does not justify recycling either “AI makes developers 19% slower” or “AI doubles productivity” as a general rule. [S01–S04](sources.md#s01)
- **Code quality, human understanding, and delivery speed are distinct outcomes.** One controlled handoff study found no significant maintainability disadvantage; other experiments found reduced comprehension. Neither finding cancels the other. [S05–S07](sources.md#s05)
- **More structure is not automatically better—or worse.** Context files can add cost without improving benchmark success; version-matched documentation can solve a genuine knowledge gap. Harness components have both helped and become obsolete as models changed. [S08–S09](sources.md#s08), [S12–S13](sources.md#s12)
- **Multiple agents demonstrate capability, not a universal efficiency advantage.** Benefits depend on task decomposition, coordination, resources, and the evaluator. [S10–S12](sources.md#s10)
- **Determinism has several meanings.** Deterministic inference is technically possible under controlled conditions, but temperature zero alone is insufficient; reproducible environments and predictable gates do not imply identical end-to-end agent behavior. [S14–S15](sources.md#s14)
- **Verification can itself be wrong.** July and September 2026 benchmark audits expose mismatched requirements/tests and answer leakage. A passing check is evidence about that check, not complete assurance. [S16–S17](sources.md#s16)

No reviewed source demonstrates all the brief’s goals together across arbitrary stacks. That is a limit of this review—not proof that the goal is unattainable.

## Method and boundaries

This was a targeted, exploratory review, not a systematic review or meta-analysis. Discovery used SearXNG; primary pages were read using Trafilatura, w3m, and a PDF text extraction. A parallel research pass investigated workflow mechanisms without selecting a preferred architecture. Findings were checked against primary material before inclusion.

Searches covered productivity experiments, agentic development reliability, maintainability, comprehension, context/specification practices, coordination, determinism, evaluation validity, and security. Representative queries included:

- `AI coding agents developer productivity randomized study 2026 2025`
- `agentic software engineering workflow empirical study reliability 2026`
- `AI code maintainability randomized controlled trial 2026 Borg`
- `coding agents reproducibility determinism temperature zero 2026 2025 research`
- `SWE Bench Pro OpenAI July 2026 audit response Scale`
- `StrongDM software factory February 2026 scenarios holdout code not reviewed`

Primary experiments, original papers, and first-person engineering reports were prioritized. Vendor evidence was included but labeled; marketing summaries and search snippets were not treated as verification. Contrary findings and revised conclusions were actively sought. The newest included source is dated **2026-09-08**; publication date and actual study period are distinguished.

Automatic extraction sometimes supplied incorrect dates or omitted mathematical values. Dates were checked against visible publication dates/submission histories where available; unverified dates remain undated. Specific figures use readable primary text or abstract metadata. Publisher access to the maintainability paper failed, so the accessible, explicitly versioned author manuscript is cited instead. Only a DORA landing-page summary was retrieved usefully; no quantitative DORA claim is used here.

Limitations: English-language, search-index and accessibility bias; substantial vendor representation; no independent reproduction of experiments or artifact execution; limited long-term evidence. Coverage is strongest for implementation and validation, weaker for requirements discovery, production operation, regulated development, and multi-year maintenance. These notes do not establish stack-wide transferability or guarantee unchanged quality.
