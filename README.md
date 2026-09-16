# honeycomb

## Goals
- turbo speed development
- without compromise of quality or taste
- be as deterministic as possible
    - clear bounds
    - clear input/processing/output
    - everything must follow a structure
- stack agnostic
- simplicity rules

## Usage

Requires Python 3.10+, with no third-party packages.

From the main checkout, set the shared record location:

```sh
export HONEYCOMB_DIR="$PWD/.honeycomb"
```

Records are tool-managed JSON. Keep this absolute path when using worktrees;
records are shared, not copied into each checkout.

### Define a task

```sh
python3 honeycomb.py define <<'JSON'
{
  "id": "list-ready",
  "outcome": "Developers can list tasks ready to run.",
  "scope": "Read records only. No dispatch or state changes.",
  "parent": null,
  "depends_on": [],
  "proof": [
    {
      "condition": "Only open tasks with all dependencies done and a running parent (unless root) are listed.",
      "verification": "Run python3 -m unittest discover -s tests; require exit 0."
    }
  ]
}
JSON
```

`define` reads one JSON object from stdin, validates it, and creates
`$HONEYCOMB_DIR/tasks/<id>.json`. Success is silent, with exit code `0`.

- Exactly the six input fields above are required.
- IDs use 1–128 ASCII letters, digits, underscores, or hyphens,
  starting with a letter or digit.
- Outcome, scope, proof conditions, and verification instructions must be
  nonblank strings. Proof must contain at least one item.
- `parent` is `null` or an existing task ID. Store `parent`, not children.
- Dependencies are unique existing sibling IDs; roots count as siblings.
  Parent links and dependencies must be acyclic.
- Each input proof item contains exactly `condition` and `verification`.
  Verification is plain language, with no reserved strings or typed actions.
- Tooling initializes `state: "open"` and every proof `result: null`.
  Callers cannot supply managed fields.

Invalid input, invalid stored graphs, duplicate IDs, and existing destination
files produce exit code `2`, without changing records. Tasks are never overwritten.

The requester approves overall intent before execution. Subtasks within its
boundaries need no separate approval. `define` stores records; it does not enforce
approval, start tasks, run verification, or perform Git operations.

### List ready tasks

```sh
mkdir -p "$HONEYCOMB_DIR/tasks"
python3 honeycomb.py ready
```

Prints sorted IDs of open tasks whose dependencies are all done and whose parent
is running (unless root). No ready tasks means empty output and success. Invalid
records or graphs produce exit code `2` with no partial output. This command
never changes records.

Scheduling reads `id`, `state`, `parent`, and `depends_on`; it does not validate
proof. Stored IDs must be unique, nonempty strings without whitespace. States
are `open`, `running`, and `done`. Missing `parent` still means root.
Every command validates parent references, sibling dependencies, and cycles.

### Start a ready task

```sh
python3 honeycomb.py start list-ready
```

`start <id>` changes a ready task's state to `running`, preserving all other
fields and records. Success is silent, with exit code `0`. Unknown or unready
tasks and invalid graphs are rejected with exit code `2`, without writes.
IDs resolve from records, not filenames.

This remains a state-only command, not the planned `execute` command. It does
not prepare worktrees or launch agents. Children require a running parent.

### Show or record proof

```sh
python3 honeycomb.py prove list-ready
python3 honeycomb.py prove list-ready --item 1 --result true
python3 honeycomb.py prove list-ready --item 1 --result false
python3 honeycomb.py prove list-ready --item 1 --result null
```

`prove <id>` displays every condition, verification instruction, and result,
with **1-based item numbers**. Without flags, it never writes.

`--item` and `--result` must be supplied together. Only the selected result
changes, using atomic file replacement. Results are `null` (unproven), `true`
(passed), or `false` (failed). Every item must be true for proof to pass.
Both forms require a running task with all children done and validate its entire
proof before output or writes. Unfinished children cause exit code `2` without
writes. Completed children permit parent proof; they do not supply it. Leaves
have no child-completion requirement. Neither form executes verification
instructions or changes task state.

The agent follows the instructions and records the observed outcome. Requested
human judgments happen in the existing conversation; the agent may relay an
answer but cannot grant someone else's approval. No answer leaves the result
`null`. Tooling trusts this relay; it does not authenticate the verifier or
establish that a supplied boolean is supported by evidence.

Exit codes for both forms:

- `0`: every proof item is true.
- `1`: proof is incomplete or failed; a supplied result was still stored.
- `2`: invalid input, record, graph, or storage error; no result update.

### Compatibility

This is a breaking contract change:

- `define` replaces `add`; no alias remains.
- `open` replaces `pending`; stored `pending` states are rejected.
- `verification` is text, not a `run`/`review` object.
- `result` is `null`/`true`/`false`, not an exit-code or acceptance object.
- `prove --item N --result ...` replaces `--review N --accept|--reject`.

Existing records are not rewritten and no migration command is provided.
Old proof shapes cannot be used with `prove`; scheduling still leaves proof
fields alone. Do not treat converting an old result as fresh verification.

### Limitations

The CLI only partially implements the target workflow in `WORKFLOW.md`.
There is no `execute` orchestration or `integrate` command. Combined-change
preparation and serialized merges remain unimplemented. Readiness and
child-completion gates trust recorded states, not Git history.

Proof results are not bound to a revision or target. After changes, clear affected
results and repeat verification; stored passes do not establish merge safety.

Do not run record writers concurrently with any command. Graph operations are
not transactional. Exclusive creation prevents overwrites and atomic replacement
avoids partial updates; concurrent coordination and interrupted-creation recovery
are not implemented.

### Tests

```sh
python3 -m unittest discover -s tests -v
```
