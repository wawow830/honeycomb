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

Records are tool-managed: developers approve tasks and give feedback rather than
edit files. JSON needs no additional parser dependency.

### Add an approved task

```sh
python3 honeycomb.py add <<'JSON'
{
  "id": "list-ready",
  "outcome": "Developers can list tasks ready to run.",
  "scope": "Read records only. No dispatch or state changes.",
  "depends_on": [],
  "proof": [
    {
      "condition": "Only pending tasks with all dependencies done are listed.",
      "verification": "Run CLI readiness tests; require exit code 0."
    }
  ]
}
JSON
```

`add` reads one JSON object from stdin, validates it, and creates
`$HONEYCOMB_DIR/tasks/<id>.json`. It creates the directory if needed.
Success produces no output and exit code `0`.

- All five input fields are required; extra fields are rejected.
- New IDs use 1–128 ASCII letters, digits, underscores, or hyphens,
  starting with a letter or digit. This keeps filenames safe.
- Outcome and scope must be nonblank strings.
- Dependencies must be unique existing task IDs; cycles are rejected.
- Proof must contain at least one condition. Each item contains exactly
  `condition` and `verification`, both nonblank strings.
- The command sets `state` to `pending` and each proof `result` to `null`.
  Callers cannot supply these managed fields.

Invalid input, duplicate IDs, invalid stored graphs, and existing destination
files produce an error on stderr and exit code `2`, without changing records.
Existing tasks are never overwritten.

Approval is a workflow requirement, not enforced by this command.
It does not start tasks, verify proof, or perform Git operations.

### What can run next?

```sh
mkdir -p "$HONEYCOMB_DIR/tasks"
python3 honeycomb.py ready
```

Store one JSON object per `.json` file in `$HONEYCOMB_DIR/tasks/`.
The command reads three fields; other task fields are left alone:

```json
{"id": "B", "state": "pending", "depends_on": ["A"]}
```

IDs must be unique, nonempty strings without whitespace. Every dependency must
name an existing task. States are `pending`, `running`, or `done`.

The command prints sorted IDs of pending tasks whose dependencies are all done.
No ready tasks means empty output and success. Invalid records, missing
references, or cycles produce an error on stderr and exit code `2`, with no
partial results. The command never changes records or starts work. Readiness
assumes recorded states are accurate; it does not verify proof or Git history.

Keep `HONEYCOMB_DIR` pointing at the main checkout when using worktrees.
Do not run record writers concurrently with either command. Exclusive file
creation prevents overwrites, but graph reads and writes are not a transaction.
Concurrent coordination and recovery from interrupted writes are not implemented.

### Try it without touching project records

```sh
demo=$(mktemp -d)
mkdir "$demo/tasks"
printf '%s\n' '{"id":"A","state":"done","depends_on":[]}' > "$demo/tasks/A.json"
printf '%s\n' '{"id":"B","state":"pending","depends_on":["A"]}' > "$demo/tasks/B.json"
printf '%s\n' '{"id":"C","state":"pending","depends_on":["B"]}' > "$demo/tasks/C.json"
printf '%s\n' '{"id":"D","state":"running","depends_on":[]}' > "$demo/tasks/D.json"
HONEYCOMB_DIR="$demo" python3 honeycomb.py ready
# B
```

### Tests

```sh
python3 -m unittest discover -s tests -v
```
