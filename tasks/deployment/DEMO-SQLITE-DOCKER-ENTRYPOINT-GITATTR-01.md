# DEMO-SQLITE-DOCKER-ENTRYPOINT-GITATTR-01

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

Pin the SQLite Docker demo entrypoint source file to LF line endings in Git so Windows checkouts do not rewrite its shebang to CRLF.

This closes only:

1. Add a Git attribute for `deploy/docker/demo/entrypoint.sh` with `text eol=lf`.
2. Verify Git reports the entrypoint with `eol: lf`.

## Explicit Non-Closure

This task does not modify product frontend behavior, backend API behavior, database schema/migrations, seed data, permissions, nginx routing, compose ports, Docker runtime behavior, or repository-wide line-ending policy for unrelated files.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/deployment/DEMO-SQLITE-DOCKER-ENTRYPOINT-GITATTR-01.md`
- `.gitattributes`
- `artifacts/DEMO-SQLITE-DOCKER-ENTRYPOINT-GITATTR-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh DEMO-SQLITE-DOCKER-ENTRYPOINT-GITATTR-01 lint /bin/zsh -lc 'test -s .gitattributes && rg -n "^deploy/docker/demo/entrypoint\\.sh text eol=lf$" .gitattributes'
```

```bash
./scripts/evidence_run.sh DEMO-SQLITE-DOCKER-ENTRYPOINT-GITATTR-01 test /bin/zsh -lc 'git check-attr text eol -- deploy/docker/demo/entrypoint.sh | rg "text: set" && git check-attr text eol -- deploy/docker/demo/entrypoint.sh | rg "eol: lf"'
```

```bash
./scripts/task_validate.sh DEMO-SQLITE-DOCKER-ENTRYPOINT-GITATTR-01
```

## Evidence Path

- `artifacts/DEMO-SQLITE-DOCKER-ENTRYPOINT-GITATTR-01/results.jsonl`
- `artifacts/DEMO-SQLITE-DOCKER-ENTRYPOINT-GITATTR-01/summary.md`
- `artifacts/DEMO-SQLITE-DOCKER-ENTRYPOINT-GITATTR-01/git/diff.patch`

## Done Definition

- `.gitattributes` pins the Docker demo entrypoint to LF.
- Git attribute verification reports `text: set` and `eol: lf`.
- Task evidence and task gate pass.
