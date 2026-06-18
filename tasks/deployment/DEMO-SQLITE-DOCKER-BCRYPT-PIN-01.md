# DEMO-SQLITE-DOCKER-BCRYPT-PIN-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: deployment-packaging-only
- evidence_cost: low
- chosen_runbook: P0-single-lane-story

## Task Plan Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: deployment-packaging-only
- evidence_cost: low
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Prevent the SQLite Docker demo seed step from resolving `bcrypt` 5.x with the current `passlib` 1.7.4 password hashing stack.

This closes only:

1. Add an explicit backend runtime dependency constraint that keeps `bcrypt` below 5.x.
2. Keep tracked backend package metadata synchronized with that runtime constraint.
3. Verify the constrained dependency set can hash the seeded `admin123` password.

## Explicit Non-Closure

This task does not modify seed data contents, password values, auth logic, backend API behavior, database schema/migrations, Docker entrypoint behavior, nginx routing, frontend behavior, or production compose settings.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/deployment/DEMO-SQLITE-DOCKER-BCRYPT-PIN-01.md`
- `backend/pyproject.toml`
- `backend/fpms_api.egg-info/requires.txt`
- `artifacts/DEMO-SQLITE-DOCKER-BCRYPT-PIN-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh DEMO-SQLITE-DOCKER-BCRYPT-PIN-01 lint /bin/zsh -lc 'python3 - <<'"'"'PY'"'"'
import tomllib
from pathlib import Path

deps = tomllib.loads(Path("backend/pyproject.toml").read_text())["project"]["dependencies"]
requires = Path("backend/fpms_api.egg-info/requires.txt").read_text().splitlines()
assert "passlib[bcrypt]>=1.7.4" in deps
assert "bcrypt<5" in deps
assert "passlib[bcrypt]>=1.7.4" in requires
assert "bcrypt<5" in requires
PY'
```

```bash
./scripts/evidence_run.sh DEMO-SQLITE-DOCKER-BCRYPT-PIN-01 test /bin/zsh -lc 'tmpdir=$(mktemp -d /tmp/fpms-bcrypt-pin.XXXXXX); python3 -m venv "$tmpdir"; "$tmpdir/bin/python" -m pip install -q -U pip; reqs="$tmpdir/requirements.txt"; python3 - <<'"'"'PY'"'"' > "$reqs"
import tomllib
from pathlib import Path

deps = tomllib.loads(Path("backend/pyproject.toml").read_text())["project"]["dependencies"]
for dep in deps:
    if dep.startswith("passlib") or dep.startswith("bcrypt"):
        print(dep)
PY
"$tmpdir/bin/python" -m pip install -q -r "$reqs"; "$tmpdir/bin/python" - <<'"'"'PY'"'"'
import importlib.metadata as md

from passlib.context import CryptContext

bcrypt_version = md.version("bcrypt")
assert int(bcrypt_version.split(".", 1)[0]) < 5, bcrypt_version
hashed = CryptContext(schemes=["bcrypt"], deprecated="auto").hash("admin123")
assert hashed.startswith("$2"), hashed
print(f"bcrypt={bcrypt_version}")
PY'
```

```bash
./scripts/task_validate.sh DEMO-SQLITE-DOCKER-BCRYPT-PIN-01
```

## Evidence Path

- `artifacts/DEMO-SQLITE-DOCKER-BCRYPT-PIN-01/results.jsonl`
- `artifacts/DEMO-SQLITE-DOCKER-BCRYPT-PIN-01/summary.md`
- `artifacts/DEMO-SQLITE-DOCKER-BCRYPT-PIN-01/git/diff.patch`
- `artifacts/DEMO-SQLITE-DOCKER-BCRYPT-PIN-01/baseline_allowlist.diff`
- `artifacts/DEMO-SQLITE-DOCKER-BCRYPT-PIN-01/baseline_external_files.txt`

## Done Definition

- Backend runtime dependencies explicitly constrain `bcrypt` below 5.x.
- Tracked backend package metadata contains the same constraint.
- Targeted dependency verification proves the constrained stack hashes `admin123`.
- Task evidence and task gate pass.
