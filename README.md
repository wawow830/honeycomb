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

## What can run next?

Requires Python 3.10+, with no third-party packages.

From the main checkout, set the shared record location:

```sh
export HONEYCOMB_DIR="$PWD/.honeycomb"
mkdir -p "$HONEYCOMB_DIR/tasks"
python3 honeycomb.py ready
```

Records are intended to be tool-managed: developers approve tasks and give
feedback rather than edit files. JSON needs no additional parser dependency.
Record-writing tooling is not implemented yet.

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
Records must remain unchanged while the command reads them; concurrent
coordination is outside this command's scope.

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
