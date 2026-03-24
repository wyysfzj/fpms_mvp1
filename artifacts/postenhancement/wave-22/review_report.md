# Wave 22 Final Independent Review Report

Date: 2026-02-28  
Role: Reviewer (Wave 22)  
Scope: `PE-BE-CL-05`

## Inputs Reviewed
- `artifacts/postenhancement/wave-22/task_plan.md`
- `artifacts/postenhancement/wave-22/contracts/contract_freeze.md`
- `artifacts/postenhancement/wave-22/test_report.md`
- `artifacts/postenhancement/wave-22/progress.md`
- `artifacts/postenhancement/wave-22/findings.md`
- `artifacts/PE-BE-CL-05/**`

## Findings (Ordered by Severity)
1. INFO - No unresolved blockers for `PE-BE-CL-05`.
   - Allowlist scope is respected.
   - Restore endpoint/service semantics and deterministic restore status mapping are implemented.
   - Permission injection pattern is compliant (`BadDebt.Action`).
   - Status semantics align with `200/400/404/409`.
   - Task gate and pytest evidence pass on independent re-run.

## Allowlist Compliance
- PASS
- Task-scoped product edits are limited to:
  - `backend/app/modules/collections/api.py`
  - `backend/app/modules/collections/service.py`
- Evidence check:
  - `artifacts/PE-BE-CL-05/git/diff.patch` contains only allowlisted product-file diffs.

## Restore Endpoint + Service Semantics
- PASS
- Endpoint exists:
  - `POST /bills/{bill_id}/bad-debt/restore`
- API delegation:
  - endpoint delegates to `restore_bill_from_bad_debt(...)`
- Restore eligibility:
  - bill must currently be `BAD_DEBT` (otherwise conflict)
- Deterministic target status mapping implemented:
  - `balance == amount` -> `UNSETTLED`
  - `0 < balance < amount` -> `PARTIALLY_SETTLED`
  - `balance <= 0` -> `SETTLED`
- Financial integrity preserved:
  - restore updates lifecycle status, does not mutate `amount`/`balance` values.

## Permission Injection
- PASS
- Parameter-injected permission enforcement:
  - `_perm: None = Depends(require_perm("BadDebt.Action"))`
- No decorator-level `dependencies=[Depends(require_perm(...))]` usage detected.

## Status Semantics
- PASS
- `200` on successful restore with updated bill payload.
- `404` for missing bill (`BILL_NOT_FOUND`).
- `409` when bill is not in `BAD_DEBT` (`BAD_DEBT_RESTORE_INVALID`).
- `400` for invalid financial restore preconditions (`BAD_DEBT_NOT_ALLOWED`).

## Task Gate + Test Evidence
- `./scripts/task_validate.sh PE-BE-CL-05` -> PASS (independent re-run)
- `cd backend && pytest -q` -> PASS (`141 passed, 3 warnings`)
- Evidence bundle present:
  - `artifacts/PE-BE-CL-05/results.jsonl`
  - `artifacts/PE-BE-CL-05/summary.md`
  - `artifacts/PE-BE-CL-05/git/diff.patch`

## Verdict
- `PE-BE-CL-05`: ACCEPT
- Wave 22 reviewer sign-off: PASS
