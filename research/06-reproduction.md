# Local verification record: sqlite-utils PR #768

Run **2026-09-14**, Linux x86-64, CPython **3.14.7**, SQLite **3.51.2**. This is a small artifact verification, not a productivity experiment or a complete library audit. [Case interpretation](01-release-hardening.md) · [Upstream sources](sources.md#sqlite-utils)

## What was held constant

- **Before:** `04f8971546418962aaf6579d4028c7117d6c3a20`, the merge of PR #767.
- **After:** `0566a9f128e19475f5cb423043820fb4119051cc`, the merge of PR #768.
- Same installed dependencies and interpreter.
- For the decisive comparison, identical **after-version tests** against each implementation.
- Read-only package/test sources; disposable temporary directory; no network or host home directory inside the test sandbox.
- Package imported directly from the selected source directory, not a separately installed sqlite-utils release.

## Results

| Code | Query tests | Exit | Result |
|---|---|---:|---|
| Before | Before | 0 | 5 passed |
| Before | After | 1 | 9 failed, 8 passed |
| After | After | 0 | 17 passed |

Failures on the old implementation covered rejected updates, rejected DDL, rejected writes inside a transaction, four transaction/control statements, and unconsumed/partially consumed `INSERT ... RETURNING` results. The failure output included the actual wrong row values—not just a generic exception.

### Additional probe on the fixed implementation

```python
from sqlite_utils import Database

db = Database(memory=True)
print(list(db.query("pragma user_version")))
try:
    db.query("pragma user_version = 5")
except ValueError:
    print("Rejected with ValueError")
print(list(db.query("pragma user_version")))
db.close()
```

Observed output:

```text
[{'user_version': 0}]
Rejected with ValueError
[{'user_version': 5}]
```

The fixed implementation deliberately handles PRAGMAs separately. The probe demonstrates a qualification to the documentation’s general no-side-effects claim, **not** that the nine reproduced repairs failed. It is not an assertion about later releases.

## Rerun recipe

Requires `uv`, Python 3.14, and `bwrap` on a Linux system with the `/usr` layout used below. Dependency download requires network access; **test execution does not**. Inspect downloaded third-party code before running it. This sandbox configuration was usable on this host; adapt mounts on other systems rather than silently running unsandboxed.

Create a fresh temporary directory, download regular package/test files from pinned archives, and install only supporting dependencies:

```bash
mkdir -p /tmp
cd "$(mktemp -d /tmp/honeycomb-sqlite-check.XXXXXX)"
python3 - <<'PY'
import io
import pathlib
import tarfile
import urllib.request

refs = {
    "before": "04f8971546418962aaf6579d4028c7117d6c3a20",
    "after": "0566a9f128e19475f5cb423043820fb4119051cc",
}
for name, sha in refs.items():
    url = f"https://codeload.github.com/simonw/sqlite-utils/tar.gz/{sha}"
    data = urllib.request.urlopen(url, timeout=60).read()
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        for member in archive:
            relative = pathlib.PurePosixPath(*pathlib.PurePosixPath(member.name).parts[1:])
            if (not member.isfile() or ".." in relative.parts
                or not relative.parts
                or relative.parts[0] not in ("sqlite_utils", "tests")):
                continue
            output = pathlib.Path(name) / relative
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(archive.extractfile(member).read())
PY
uv venv --python /usr/bin/python3 venv
uv pip install --python venv/bin/python \
  click==8.5.0 click-default-group==1.2.4 hypothesis==6.168.0 \
  iniconfig==2.3.0 packaging==26.3 pip==26.2.1 pluggy==1.6.0 \
  pygments==2.21.0 pytest==9.1.1 python-dateutil==2.9.0.post0 \
  six==1.17.0 sortedcontainers==2.4.0 sqlite-fts4==1.0.3 tabulate==0.10.0
```

Execute each selected implementation against the chosen test directory:

```bash
sandbox() {
  code="$1"
  shift
  bwrap \
    --ro-bind /usr /usr \
    --symlink usr/lib64 /lib64 --symlink usr/lib /lib --symlink usr/bin /bin \
    --proc /proc --dev /dev --tmpfs /tmp \
    --unshare-all --die-with-parent --clearenv \
    --setenv PATH /venv/bin:/usr/bin --setenv HOME /tmp \
    --setenv PYTHONPATH "/$code" --setenv PYTHONDONTWRITEBYTECODE 1 \
    --ro-bind "$PWD/venv" /venv \
    --ro-bind "$PWD/before" /before --ro-bind "$PWD/after" /after \
    --chdir /tmp /venv/bin/python "$@"
}
run_tests() {
  sandbox "$1" -m pytest "/$2/tests/test_query.py" \
    -q --import-mode=importlib -p no:cacheprovider
}
run_tests before before
run_tests before after  # Expected nonzero exit: this is the regression check.
run_tests after after
sandbox after -c 'import sys, sqlite3, sqlite_utils; print(sys.version); print(sqlite3.sqlite_version); print(sqlite_utils.__file__)'
```

The probe above can be supplied to `sandbox after -c` as a quoted multiline Python string. It requires no additional files or dependencies.

### Source-file SHA-256 checksums

```text
before/sqlite_utils/db.py
7534547b210dd6ee4c7a610a776aec96506bdc5f129af2292ceda8e3663f6d99

after/sqlite_utils/db.py
74bb2163dd127d4a6058955d5a17114803d02db7d224293fcb43dee460dbe9d6

before/tests/test_query.py
5036dc502c3958e134bbdede777d69abe14628bc94509ca117c1768c607be8a5

after/tests/test_query.py
8843c7bd836c0761b50331d1e4adae1b2d1c1336760e6baa5ca307e17c701ca0
```

## What this does not reproduce

The original model sessions, the full release review, original July dependency versions, all Python/SQLite configurations, the complete test suite, or real application workloads. It does not measure time saved, prove model-review independence, or establish absence of other defects.

Raw local test logs and fetched evidence were retained under `/tmp/honeycomb-rewrite/` during this session. They are temporary, not durable repository artifacts; pinned source links, the essential outputs, checksums, and the rerun recipe above are the persistent record.
