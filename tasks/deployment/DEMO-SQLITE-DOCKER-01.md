# DEMO-SQLITE-DOCKER-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: deployment-packaging-only
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Task Plan Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: deployment-packaging-only
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Add a Docker-based demo deployment path for the current project that teams can run on a laptop or deploy to a cloud container host while still using SQLite.

This closes only:

1. Add a project-root demo Dockerfile that builds the Vue frontend, runs the FastAPI backend, serves the SPA through nginx, and proxies API traffic to the backend inside one container.
2. Add a demo compose file that persists SQLite database and storage data under a Docker volume.
3. Add minimal runtime support files needed by the demo container entrypoint and nginx reverse proxy.
4. Add a detailed user guide covering local demo startup, cloud deployment settings, SQLite persistence, backup, reset, and troubleshooting.

## Explicit Non-Closure

This task does not modify product frontend behavior, backend API behavior, database schema/migrations, seed data contents, permissions, existing PostgreSQL production compose behavior, or runtime demo case data.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/deployment/DEMO-SQLITE-DOCKER-01.md`
- `.dockerignore`
- `Dockerfile.demo`
- `docker-compose.demo.yml`
- `deploy/docker/demo/entrypoint.sh`
- `deploy/docker/demo/nginx.conf`
- `docs/docker_demo_guide.md`
- `artifacts/DEMO-SQLITE-DOCKER-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh DEMO-SQLITE-DOCKER-01 lint /bin/zsh -lc 'if command -v docker >/dev/null 2>&1; then docker compose -f docker-compose.demo.yml config >/tmp/fpms-demo-compose-config.yml && test -s /tmp/fpms-demo-compose-config.yml; else echo "Docker CLI unavailable; running static compose checks"; test -s Dockerfile.demo && test -s docker-compose.demo.yml && test -s deploy/docker/demo/entrypoint.sh && test -s deploy/docker/demo/nginx.conf; fi; rg -n "sqlite:////data/fpms_demo.db|FPMS_RUN_SEED|/data|8080:80" Dockerfile.demo docker-compose.demo.yml deploy/docker/demo/entrypoint.sh docs/docker_demo_guide.md'
```

```bash
./scripts/evidence_run.sh DEMO-SQLITE-DOCKER-01 test /bin/zsh -lc 'if command -v docker >/dev/null 2>&1; then docker build -f Dockerfile.demo -t fpms-mvp1-demo:sqlite .; else echo "Docker CLI unavailable; verified Docker package by static file checks only"; rg -n "FROM node:20-alpine|FROM python:3.11-slim|nginx|alembic upgrade head|npm run build|VITE_API_BASE_URL=/api/v1" Dockerfile.demo deploy/docker/demo/entrypoint.sh deploy/docker/demo/nginx.conf; fi'
```

```bash
./scripts/task_validate.sh DEMO-SQLITE-DOCKER-01
```

## Evidence Path

- `artifacts/DEMO-SQLITE-DOCKER-01/results.jsonl`
- `artifacts/DEMO-SQLITE-DOCKER-01/summary.md`
- `artifacts/DEMO-SQLITE-DOCKER-01/git/diff.patch`
- `artifacts/DEMO-SQLITE-DOCKER-01/baseline_allowlist.diff`
- `artifacts/DEMO-SQLITE-DOCKER-01/baseline_external_files.txt`

## Done Definition

- Docker demo files are present and scoped to SQLite demo deployment.
- The guide explains laptop and cloud deployment, persistence, backup, reset, health checks, login, and troubleshooting.
- Docker compose config validation passes.
- Demo image build passes when Docker is available; if Docker is unavailable in the execution environment, static package checks must pass and the limitation must be reported.
- Task evidence and task gate pass.
