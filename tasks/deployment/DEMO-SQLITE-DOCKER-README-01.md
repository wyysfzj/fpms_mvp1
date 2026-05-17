# DEMO-SQLITE-DOCKER-README-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: doc-only
- evidence_cost: low
- chosen_runbook: P0-single-lane-story

## Task Plan Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: doc-only
- evidence_cost: low
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Add a new README section that points users to the SQLite Docker demo deployment package and its detailed guide.

This closes only:

1. Add the project-root README section for the SQLite Docker demo.
2. List the deployment file paths: `Dockerfile.demo`, `docker-compose.demo.yml`, `.dockerignore`, `deploy/docker/demo/entrypoint.sh`, `deploy/docker/demo/nginx.conf`, and `docs/docker_demo_guide.md`.
3. Include the local quick-start command and guide path.

## Explicit Non-Closure

This task does not modify Dockerfiles, compose files, runtime scripts, nginx config, product frontend/backend behavior, database schema, seed data, permissions, or deployment logic.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/deployment/DEMO-SQLITE-DOCKER-README-01.md`
- `README.md`
- `artifacts/DEMO-SQLITE-DOCKER-README-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh DEMO-SQLITE-DOCKER-README-01 lint /bin/zsh -lc 'test -s README.md && rg -n "Docker demo \\(SQLite\\)|Dockerfile.demo|docker-compose.demo.yml|docs/docker_demo_guide.md|deploy/docker/demo/entrypoint.sh|deploy/docker/demo/nginx.conf|\\.dockerignore" README.md'
```

```bash
./scripts/evidence_run.sh DEMO-SQLITE-DOCKER-README-01 test /bin/zsh -lc 'rg -n "docker compose -f docker-compose.demo.yml up --build|http://localhost:8080|admin123|SQLite" README.md'
```

```bash
./scripts/task_validate.sh DEMO-SQLITE-DOCKER-README-01
```

## Evidence Path

- `artifacts/DEMO-SQLITE-DOCKER-README-01/results.jsonl`
- `artifacts/DEMO-SQLITE-DOCKER-README-01/summary.md`
- `artifacts/DEMO-SQLITE-DOCKER-README-01/git/diff.patch`
- `artifacts/DEMO-SQLITE-DOCKER-README-01/baseline_allowlist.diff`
- `artifacts/DEMO-SQLITE-DOCKER-README-01/baseline_external_files.txt`

## Done Definition

- README has a new SQLite Docker demo section.
- The new section includes all relevant deployment file paths and points to the detailed guide.
- Task evidence and task gate pass.
