# PE-BE-COM-09 Evidence Summary

## Task
- Task ID: `PE-BE-COM-09`
- Task file: `tasks/postenhancement/backend/PE-BE-COM-09.md`
- Scope (allowlist):
  - `backend/app/modules/commission/api.py`
  - `backend/app/modules/commission/service.py`

## Product Changes
1. Added endpoint `POST /commission/settlements/{id}/generate-lines` in commission API.
2. Enforced permission injection with:
   - `_perm: None = Depends(require_perm("CommissionSettlement.Action"))`
3. Added service `generate_commission_settlement_lines(...)` with:
   - settlement load + `404` not found handling
   - settlement precondition checks (`agent_id`, period coherence)
   - allowed-state gate for generation (`DRAFT`/`GENERATED`)
   - eligible commission selection by settleable/agent/status/period
   - deterministic line amount from unsettled stages only
   - idempotent upsert behavior by `(settlement_id, commission_id)`
   - deterministic `line_no` append for new lines
   - aggregate recompute from persisted lines (`line_count`, `total_amount`)
   - deterministic settlement status transition (`GENERATED` when lines exist)

## Verification
- `./scripts/evidence_run.sh PE-BE-COM-09 lint bash -lc 'cd backend && ruff check app/modules/commission/api.py app/modules/commission/service.py && ruff format --check app/modules/commission/api.py app/modules/commission/service.py'`
  - first run: `rc=1` (format check failure: `service.py`)
  - fix applied: `cd backend && ruff format app/modules/commission/service.py`
  - second run: `rc=0`
- `./scripts/evidence_run.sh PE-BE-COM-09 test bash -lc 'cd backend && pytest -q'`
  - `rc=0` (`141 passed, 3 warnings`)

## Status Semantics
- `200`: generation summary returned.
- `404`: settlement not found.
- `400`: invalid settlement scope/range context.
- `409`: settlement state conflict or duplicate-line integrity conflict.

## Evidence Files
- `artifacts/PE-BE-COM-09/results.jsonl`
- `artifacts/PE-BE-COM-09/summary.md`
- `artifacts/PE-BE-COM-09/git/diff.patch`
