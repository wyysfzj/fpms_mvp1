# Wave 18 Final Independent Review Report

Date: 2026-02-28  
Role: Reviewer (Wave 18)  
Scope: `PE-BE-CL-01`

## Inputs Reviewed
- `artifacts/postenhancement/wave-18/task_plan.md`
- `artifacts/postenhancement/wave-18/contracts/contract_freeze.md`
- `artifacts/postenhancement/wave-18/test_report.md`
- `artifacts/postenhancement/wave-18/progress.md`
- `artifacts/postenhancement/wave-18/findings.md`
- `artifacts/PE-BE-CL-01/**`

## Findings (Ordered by Severity)
1. INFO - No unresolved blockers for `PE-BE-CL-01`.
   - Allowlist scope is respected.
   - Overdue filtering + grouping + head/line snapshot semantics are implemented.
   - Idempotent duplicate-protection behavior is implemented.
   - Error semantics include required `400/404/409` paths.
   - Task gate and pytest evidence pass on independent re-run.

## Allowlist Compliance
- PASS
- Task-scoped product edits are limited to:
  - `backend/app/modules/collections/service.py`
- Evidence check:
  - `artifacts/PE-BE-CL-01/git/diff.patch` contains one product-file diff entry for the allowlisted file only.

## Service Semantics Review
- PASS
- Overdue filtering:
  - `due_date <= to_date`
  - positive outstanding balance (`balance > 0`)
  - status include/exclude controls with default excluded non-collectable statuses.
- Grouping and snapshot generation:
  - grouped by `(client_id, currency)` per cutoff.
  - creates dunning head (`Dunning`) and snapshot lines (`DunningLine`).
  - head `total_amount` computed as sum of line snapshot outstanding amounts.
- Idempotency / duplicate protection:
  - deterministic snapshot signature marker per cutoff + eligible-bill snapshot.
  - repeated same-input generation reuses existing batch (no duplicate head/line creation).
  - optional strict conflict mode raises `409` for duplicate generation requests.

## Error Semantics
- PASS
- `400`: invalid cutoff/scope/filter state (`DUNNING_BATCH_STATE_INVALID`).
- `404`: scoped generation target has no overdue bills (`DUNNING_BATCH_NOT_FOUND`).
- `409`: duplicate generation under strict conflict mode (`DUNNING_BATCH_STATE_INVALID` with conflict semantics).

## Task Gate + Test Evidence
- `./scripts/task_validate.sh PE-BE-CL-01` -> PASS (independent re-run)
- `cd backend && pytest -q` -> PASS (`141 passed, 3 warnings`)
- Evidence bundle present:
  - `artifacts/PE-BE-CL-01/results.jsonl`
  - `artifacts/PE-BE-CL-01/summary.md`
  - `artifacts/PE-BE-CL-01/git/diff.patch`

## Verdict
- `PE-BE-CL-01`: ACCEPT
- Wave 18 reviewer sign-off: PASS
