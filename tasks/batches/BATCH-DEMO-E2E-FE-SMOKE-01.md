# BATCH-DEMO-E2E-FE-SMOKE-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Role

Lead / demo smoke coordinator.

## Exact Closure Slice

Run one FE automation smoke for the prepared demo package in `docs/demo/FPMS_DEMO_E2E_HAPPY_PATH.md`.

This task closes only:

1. Create an evidence-only FE smoke task.
2. Run a Playwright browser smoke against the local frontend and backend.
3. Validate the demo pages and a UI-first, API-assisted happy-path record flow.
4. Capture screenshots and sanitized reports under task artifacts.

## Explicit Non-Closure

Do not:

- modify backend, frontend, pytest handler, Playwright skeleton source, or skeleton YAML/JSON/schema assets
- implement new product behavior
- claim `TC-B-005` as complete
- replace pytest backend smoke evidence
- store passwords, tokens, or authorization headers in artifacts

## Allowed Files

- `tasks/batches/BATCH-DEMO-E2E-FE-SMOKE-01.md`
- `artifacts/BATCH-DEMO-E2E-FE-SMOKE-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh BATCH-DEMO-E2E-FE-SMOKE-01 lint /bin/zsh -lc 'test -f tasks/batches/BATCH-DEMO-E2E-FE-SMOKE-01.md && test -f artifacts/BATCH-DEMO-E2E-FE-SMOKE-01/demo_fe_smoke.cjs'
```

```bash
./scripts/evidence_run.sh BATCH-DEMO-E2E-FE-SMOKE-01 test /bin/zsh -lc 'FPMS_BASE_URL=http://127.0.0.1:5173 FPMS_API_URL=http://127.0.0.1:8000/api/v1 FPMS_USERNAME=admin FPMS_PASSWORD="$FPMS_LOCAL_PASSWORD" FPMS_RUN_ID=DEMO-FE-SMOKE-001 node artifacts/BATCH-DEMO-E2E-FE-SMOKE-01/demo_fe_smoke.cjs'
```

```bash
./scripts/evidence_run.sh BATCH-DEMO-E2E-FE-SMOKE-01 task_gate ./scripts/task_validate.sh BATCH-DEMO-E2E-FE-SMOKE-01
```

## Evidence Path

- `artifacts/BATCH-DEMO-E2E-FE-SMOKE-01/results.jsonl`
- `artifacts/BATCH-DEMO-E2E-FE-SMOKE-01/summary.md`
- `artifacts/BATCH-DEMO-E2E-FE-SMOKE-01/git/diff.patch`
- `artifacts/BATCH-DEMO-E2E-FE-SMOKE-01/screenshots/**`
- `artifacts/BATCH-DEMO-E2E-FE-SMOKE-01/fe_smoke_report.md`

## Remaining Follow-Up Task IDs

None for this demo smoke.

`TC-B-005` remains deferred by B-wave close audit and outside this closure.
