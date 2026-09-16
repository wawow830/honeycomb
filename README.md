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
      "verification": {"run": "python3 -m unittest discover -s tests -p test_ready.py"}
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
- Proof must contain at least one item with exactly `condition` and `verification`.
  The condition is a nonblank string. Verification contains exactly
  `{"run": "<command>"}` (a nonblank command) or `{"review": "developer"}`.
  Legacy verification strings are no longer accepted by `add` or `prove`.
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

### Start a ready task

```sh
python3 honeycomb.py start list-ready
```

`start <id>` requires a pending task with every dependency done. It validates
stored records and the dependency graph, then changes only that task's `state`
to `running`. Other fields and other records stay unchanged.
Success produces no output and exit code `0`.

Unknown or unready tasks and invalid stored graphs produce an error on stderr
and exit code `2`, without changing records. Starting an already running task
is rejected. IDs are resolved from records, not filenames.

This command only records the transition. It does not dispatch agents, perform
Git operations, verify proof, or enforce approval or ownership.

### Prove a running task

Run from the task's checkout so checks see the intended code:

```sh
python3 /path/to/honeycomb.py prove list-ready
```

`prove <id>` validates the stored graph and the task's entire proof, then runs
all command checks in order, even after failures. Commands run through the shell
in the caller's working directory and environment, with closed stdin. Command
output goes to stderr; stdout reports proof item numbers and actual exit codes:

```text
1: exit_code: 0
2: review: Developer accepts the wording.
```

Results stay in the proof item: `{"exit_code": 0}` passes; any other exit code
fails. Each run clears old command results first and saves each new result
atomically. An interrupted run leaves uncompleted checks unproven.

Unaccepted developer reviews are returned with **1-based proof item numbers**.
The agent asks in the existing conversation, then relays the developer's decision:

```sh
python3 honeycomb.py prove list-ready --review 2 --accept
python3 honeycomb.py prove list-ready --review 2 --reject
```

These commands record `{"accepted": true}` or `{"accepted": false}` in only
that review's result. They do not rerun commands. No developer answer means no
update. Plain `prove` never grants or changes review decisions.
The interface trusts the agent's relay; it does not authenticate the developer.

Exit codes for both forms:

- `0`: every proof item passes.
- `1`: proof remains incomplete (failed check, unrun check, rejected or unanswered review).
- `2`: invalid invocation, record, graph, or storage/launch error.

Invalid input is rejected before executing commands or modifying records.
Only running tasks can be proven. The command changes proof results, not task
state; it does not merge, mark done, or release dependents.

Verification commands are trusted code, not sandboxed: they can modify files and
inherit credentials. No timeout is imposed. Do not use checks that mutate task
records. Results are not bound to a Git revision; after code changes, rerun checks
and obtain renewed review where affected. Passing a command proves it exited `0`,
not that the command adequately tests its condition.

### Limitations

Keep `HONEYCOMB_DIR` pointing at the main checkout when using worktrees.
Do not run record writers concurrently with any command. Exclusive file
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
