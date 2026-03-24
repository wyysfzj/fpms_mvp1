# PE-BE-COM-08 Evidence Summary

## Task
- ID: `PE-BE-COM-08`
- Runbook: `tasks/postenhancement/backend/PE-BE-COM-08.md`

## Scope Compliance
- Product-code changes restricted to allowlist:
  - `backend/app/modules/commission/api.py`
  - `backend/app/modules/commission/service.py`

## Implemented
- Added endpoint: `POST /commission/settlements`.
- Permission injection implemented exactly:
  - `_perm: None = Depends(require_perm("CommissionSettlement.Create"))`
- Added create service: `create_commission_settlement(...)` with input fields:
  - `agent_id`, `period_from`, `period_to`, `currency`, `remark`
- Validation & normalization:
  - `agent_id` required, trimmed, non-empty
  - `currency` required, trimmed, non-empty, normalized to uppercase
  - `remark` trimmed, empty -> `None`
  - period validation: when both provided, `period_from <= period_to`
- Uniqueness conflict enforcement:
  - active conflict scope: same `agent_id + currency + period_from + period_to`
  - active statuses include at least `DRAFT` and `CREATED`
  - conflict returns `409` with code `COMMISSION_SETTLEMENT_CONFLICT`
- Settlement initialization behavior:
  - `status = DRAFT`
  - `line_count = 0`
  - `total_amount = 0`
  - `settlement_no` generated after flush using persisted id
- Endpoint returns `201 Created` with created settlement payload fields.
- Existing commission endpoints kept unchanged.

## Verification
- Wrapper lint:
  - `./scripts/evidence_run.sh PE-BE-COM-08 lint bash -lc 'cd backend && ruff check app/modules/commission/api.py app/modules/commission/service.py && ruff format --check app/modules/commission/api.py app/modules/commission/service.py'`
  - Result: PASS (`rc=0`)
- Wrapper test:
  - `./scripts/evidence_run.sh PE-BE-COM-08 test bash -lc 'cd backend && pytest -q'`
  - Result: PASS (`141 passed, 3 warnings in 30.30s`)

## Evidence Files
- `artifacts/PE-BE-COM-08/results.jsonl`
- `artifacts/PE-BE-COM-08/summary.md`
- `artifacts/PE-BE-COM-08/git/diff.patch`
