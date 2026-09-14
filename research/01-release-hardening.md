# Case: release hardening in sqlite-utils

**Work:** an existing database library approaching a compatibility-sensitive major release. **When:** July 4–5, 2026. **Evidence:** maintainer account, merged PRs, pinned code and tests, plus a local before/after reproduction. [Sources](sources.md#sqlite-utils)

## What actually happened

Simon Willison asked Claude Code to review the release candidate before shipping 4.0, emphasizing problems that would become breaking changes if fixed later. The agent produced a review document, including a concrete persistence failure: `delete_where()` left an implicit transaction open, so subsequent operations could appear successful on the same connection but disappear on close.

This was not a one-prompt release. Willison reports **37 prompts**; GitHub confirms **34 commits, 30 changed files, +1,321/−190 lines** in [PR #767](https://github.com/simonw/sqlite-utils/pull/767). He worked through the findings, then used a laptop and GitHub’s PR interface for final review.

A particularly informative human intervention came from reading the documentation changes. They excluded Python’s newer SQLite `autocommit` modes, whose semantics could silently break transaction handling. The resulting implementation **still does not support those modes**: it explicitly rejects such connections with `TransactionError`. The human prompted investigation of an easily overlooked configuration; the repair made the unsupported boundary explicit rather than silently accepting broken behavior.

Then a separate GPT-5.5 review found **two problems in the newly merged changes**:

1. `db.query("update ...")` raised `ValueError` because the statement returned no rows—but only **after committing the update**.
2. `INSERT ... RETURNING` committed only after its result iterator was exhausted. Not iterating, or consuming only its first row, could leave the write uncommitted, contrary to the documentation.

Willison transferred those findings to a fresh Claude session. It confirmed them and produced [PR #768](https://github.com/simonw/sqlite-utils/pull/768), which he merged.

## The mechanism visible in the patch

The earlier implementation called an auto-committing execution method before checking whether the statement returned rows. Its test checked that an exception occurred, **not whether the rejected operation had already changed data**.

The repair executes ordinary queries inside a savepoint, rolling back rejected statements. It also completes row-returning writes before releasing the savepoint when necessary. New tests check observable guarantees:

- Rejected updates and table creation do not persist.
- Rejecting an operation does not destroy earlier work in an explicit transaction.
- Unconsumed and partially consumed `RETURNING` results still commit when promised.
- A **separate database connection** sees the committed data.

That last check matters: reading through the writing connection can conceal a persistence bug.

## What this review independently reproduced

Using the exact pre-fix and merged-fix snapshots, with the same dependencies and isolated, network-disabled execution:

| Implementation | Test file | Result |
|---|---|---|
| Before #768 | Its existing `test_query.py` | **5 passed** |
| Before #768 | #768’s revised `test_query.py` | **9 failed, 8 passed** |
| After #768 | The same revised test file | **17 passed** |

These are local results on Python 3.14.7 / SQLite 3.51.2, **not the project’s full CI results**. Exact revisions, commands, dependencies, and limitations are in [the reproduction record](06-reproduction.md).

A further probe found a remaining qualification: on the fixed snapshot, `db.query("pragma user_version = 5")` raises `ValueError` but changes `user_version` from 0 to 5. The revised tests include that statement but do not assert preservation of the previous value. The implementation explicitly special-cases PRAGMAs; the documentation’s general “rejected statement has no effect” wording is therefore broader than the observed behavior. This is not a claim about the current release, severity, or exploitability.

## Where the human and agent contributions differed

- **Human:** defined the release objective, judged compatibility, selected which findings to act on, checked documentation and code, commissioned another review, and accepted changes.
- **Agents:** inspected the API, generated reproductions, implemented fixes, expanded tests, and drafted documentation.
- **External feedback:** actual SQLite transaction behavior, independent connections, test assertions, and reviewer findings—not the implementation agent saying it was done.

The maintainer’s approximately **$149.25** figure is an estimated API-equivalent cost for the listed main session and its subagents. It is not a measured total for all reviews, all human effort, or the entire release. There is no no-AI comparison establishing time saved.

## Applicability—and limits

**Useful when:** changing persistence, exception behavior, lazy execution, transactions, or a public API in an existing system. Inspect what must remain true after errors, partial consumption, and process/connection boundaries—not just the immediate return value.

**Requires:** someone able to decide the compatibility contract and an executable environment exposing the relevant behavior.

**Does not establish:** that two different models are necessary, that agent review replaces human judgment, or that more review rounds always pay. A second pass with the same model, another human, or purpose-built tests might also have caught these defects. The identifiable benefit here is **specific findings that became discriminating tests**, not a proven benefit from model diversity.
