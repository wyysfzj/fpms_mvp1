# BATCH-DEMO-E2E-REAL-UI-FULL-RETRY-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: high
- be_fe_coupling: high
- evidence_cost: high
- chosen_runbook: P0-frontend-heavy-story

## Exact Closure Slice

Rerun a true observable browser-use full-case-lifecycle UI E2E after blocker fixes pass. Continue case `RUI202605100035` if feasible; if prior data cannot satisfy newly fixed prerequisites, document the reason and create a new UI-only case through visible UI.

## Explicit Non-Closure

- Do not perform business mutations through API.
- Do not use headless Playwright as primary proof.
- Do not modify product code in this QA retry task.
- Do not claim PASS if any lifecycle step remains unsupported, hidden, broken, or unreachable.
- Do not store passwords, tokens, Authorization headers, or PII in artifacts.

## Allowed Files

- `tasks/batches/BATCH-DEMO-E2E-REAL-UI-FULL-RETRY-01.md`
- `artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-RETRY-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh BATCH-DEMO-E2E-REAL-UI-FULL-RETRY-01 test /bin/zsh -lc 'test -f artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-RETRY-01/ui_full_lifecycle_retry_report.md && test "$(find artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-RETRY-01/screenshots -type f -name "*.png" | wc -l | tr -d " ")" -ge 12'
```

```bash
./scripts/evidence_run.sh BATCH-DEMO-E2E-REAL-UI-FULL-RETRY-01 lint /bin/zsh -lc 'test -f tasks/batches/BATCH-DEMO-E2E-REAL-UI-FULL-RETRY-01.md && test -f artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-RETRY-01/ui_full_lifecycle_retry_report.md'
```

```bash
./scripts/evidence_run.sh BATCH-DEMO-E2E-REAL-UI-FULL-RETRY-01 secret_scan /bin/zsh -lc '! rg -n "admin123|Authorization: Bearer|access_token|eyJ[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+" artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-RETRY-01'
```

```bash
./scripts/evidence_run.sh BATCH-DEMO-E2E-REAL-UI-FULL-RETRY-01 task_gate ./scripts/task_validate.sh BATCH-DEMO-E2E-REAL-UI-FULL-RETRY-01
```

## Evidence Path

- `artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-RETRY-01/results.jsonl`
- `artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-RETRY-01/summary.md`
- `artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-RETRY-01/git/diff.patch`
- `artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-RETRY-01/ui_full_lifecycle_retry_report.md`
- `artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-RETRY-01/browser_transcript.md`
- `artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-RETRY-01/screenshots/**`

## Remaining Follow-Up Task IDs

- `BATCH-DEMO-E2E-REAL-UI-FULL-RETRY-01-FOLLOW-UP-REMAINING-BLOCKER` if any required lifecycle step remains BLOCKED.

