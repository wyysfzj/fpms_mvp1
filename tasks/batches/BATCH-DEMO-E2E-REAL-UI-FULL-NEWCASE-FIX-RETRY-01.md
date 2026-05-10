# BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-FIX-RETRY-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: high
- be_fe_coupling: high
- evidence_cost: high
- chosen_runbook: P0-frontend-heavy-story

## Exact Closure Slice

Run an observable browser-use retry for new case `RUI20260510033534` covering the formerly blocked checkpoints: bill detail visibility for the generated bill and commission settlement target-case generation/report visibility.

## Explicit Non-Closure

- Do not create a new case unless `RUI20260510033534` cannot be found through the UI.
- Do not mutate business state through API.
- Do not modify product code or Skeleton Pack assets in this QA task.
- Do not claim full lifecycle PASS unless the retry visibly completes the previously blocked checkpoints and no new in-scope blocker appears.

## Allowed Files

- `tasks/batches/BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-FIX-RETRY-01.md`
- `artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-FIX-RETRY-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-FIX-RETRY-01 test /bin/zsh -lc 'test -f artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-FIX-RETRY-01/ui_blocker_retry_report.md && test "$(find artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-FIX-RETRY-01/screenshots -type f -name "*.png" | wc -l | tr -d " ")" -ge 4'
```

```bash
./scripts/evidence_run.sh BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-FIX-RETRY-01 lint /bin/zsh -lc 'test -f tasks/batches/BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-FIX-RETRY-01.md && test -f artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-FIX-RETRY-01/ui_blocker_retry_report.md'
```

```bash
./scripts/evidence_run.sh BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-FIX-RETRY-01 task_gate ./scripts/task_validate.sh BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-FIX-RETRY-01
```

## Evidence Path

- `artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-FIX-RETRY-01/results.jsonl`
- `artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-FIX-RETRY-01/summary.md`
- `artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-FIX-RETRY-01/git/diff.patch`
- `artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-FIX-RETRY-01/ui_blocker_retry_report.md`
- `artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-FIX-RETRY-01/screenshots/**`

## Remaining Follow-Up Task IDs

- `BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-FIX-RETRY-01-FOLLOW-UP` if the browser retry finds a new unsupported UI lifecycle step.
