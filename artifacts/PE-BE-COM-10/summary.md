# PE-BE-COM-10 Evidence Summary

## Task
- Task ID: `PE-BE-COM-10`
- Task file: `tasks/postenhancement/backend/PE-BE-COM-10.md`
- Scope (allowlist):
  - `backend/app/modules/commission/api.py`
  - `backend/app/modules/commission/service.py`

## Implemented
1. Added endpoint `GET /commission/reports/settlement` in commission API.
2. Added permission injection exactly as required:
   - `_perm: None = Depends(require_perm("CommissionReport.Read"))`
3. Added service aggregation logic for settlement report with deterministic output:
   - filters: `agent_id`, `case_id`, `currency`, `settlement_status`, `line_status`
   - time filters: `date_from`, `date_to`, `time_field`
   - time field options: `line_created_at` (default), `settleable_date`, `settlement_period`
   - inclusive date range validation (`date_from <= date_to`; invalid => 400)
   - source rows from joined settlement line/header/commission tables
   - top-level output: `filters`, `totals`, `by_agent`, `by_case`, `by_time`, `details`
   - deterministic ordering for details and grouped outputs

## Verification
- `./scripts/evidence_run.sh PE-BE-COM-10 lint bash -lc 'cd backend && ruff check app/modules/commission/api.py app/modules/commission/service.py && ruff format --check app/modules/commission/api.py app/modules/commission/service.py'`
  - Result: `rc=0`
- `./scripts/evidence_run.sh PE-BE-COM-10 test bash -lc 'cd backend && pytest -q'`
  - Result: `rc=0` (`141 passed, 3 warnings`)

## Expected Status Semantics
- `200`: successful report generation (including empty dataset with zero totals and empty arrays)
- `400`: business validation failure (invalid date range or unsupported `time_field`)
- `401`/`403`: auth/permission enforcement from existing dependencies
- `422`: FastAPI query validation failures

## Evidence Files
- `artifacts/PE-BE-COM-10/results.jsonl`
- `artifacts/PE-BE-COM-10/summary.md`
- `artifacts/PE-BE-COM-10/git/diff.patch`
