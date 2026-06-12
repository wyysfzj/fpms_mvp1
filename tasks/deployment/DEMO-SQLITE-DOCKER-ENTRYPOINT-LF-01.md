# DEMO-SQLITE-DOCKER-ENTRYPOINT-LF-01

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

Harden the SQLite Docker demo image build so the copied container entrypoint is normalized to LF line endings before it is executed.

This closes only:

1. Ensure `/usr/local/bin/fpms-demo-entrypoint` inside the demo image does not retain Windows CRLF line endings after `COPY`.
2. Preserve the existing demo entrypoint path, permissions, and runtime behavior.

## Explicit Non-Closure

This task does not modify product frontend behavior, backend API behavior, database schema/migrations, seed data, permissions, nginx routing, compose ports, host Git checkout policy, or repository-wide line-ending policy.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/deployment/DEMO-SQLITE-DOCKER-ENTRYPOINT-LF-01.md`
- `Dockerfile.demo`
- `artifacts/DEMO-SQLITE-DOCKER-ENTRYPOINT-LF-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh DEMO-SQLITE-DOCKER-ENTRYPOINT-LF-01 lint /bin/zsh -lc 'test -s Dockerfile.demo && python3 - <<'"'"'PY'"'"'
from pathlib import Path
dockerfile = Path("Dockerfile.demo").read_text()
assert "fpms-demo-entrypoint" in dockerfile
assert "sed -i" in dockerfile
assert "\\r$" in dockerfile
PY'
```

```bash
./scripts/evidence_run.sh DEMO-SQLITE-DOCKER-ENTRYPOINT-LF-01 test /bin/zsh -lc 'python3 - <<'"'"'PY'"'"'
from pathlib import Path
entrypoint = Path("deploy/docker/demo/entrypoint.sh").read_bytes()
assert entrypoint.startswith(b"#!/usr/bin/env bash\n")
dockerfile = Path("Dockerfile.demo").read_text()
assert "sed -i" in dockerfile and "/usr/local/bin/fpms-demo-entrypoint" in dockerfile
PY'
```

```bash
./scripts/task_validate.sh DEMO-SQLITE-DOCKER-ENTRYPOINT-LF-01
```

## Evidence Path

- `artifacts/DEMO-SQLITE-DOCKER-ENTRYPOINT-LF-01/results.jsonl`
- `artifacts/DEMO-SQLITE-DOCKER-ENTRYPOINT-LF-01/summary.md`
- `artifacts/DEMO-SQLITE-DOCKER-ENTRYPOINT-LF-01/git/diff.patch`

## Done Definition

- Demo image build normalizes the copied entrypoint line endings before `chmod`.
- Static verification proves the Dockerfile contains the entrypoint normalization.
- Task evidence and task gate pass.
