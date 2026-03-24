# PE-BE-CS-01 Evidence Summary

## Task
- Task ID: `PE-BE-CS-01`
- Task file: `tasks/postenhancement/backend/PE-BE-CS-01.md`
- Scope (allowlist):
  - `backend/app/modules/consulting/api.py`
  - `backend/app/modules/consulting/service.py`
  - `backend/app/modules/cases/service.py`

## Implemented
1. Added dedicated endpoint `POST /consulting/cases` in `consulting/api.py`.
2. Enforced permission injection exactly:
   - `_perm: None = Depends(require_perm("ConsultingCase.Create"))`
3. Added consulting service delegation in `consulting/service.py`.
4. Added dedicated create helper in `cases/service.py` for consulting/search with deterministic validation:
   - required fields with trim validation:
     - `case_no`, `case_type`, `client_id`, `title_cn`, `primary_agent_id`, `recv_date`
   - `case_type` restricted to `CONSULTING`/`SEARCH`
   - duplicate `case_no` returns `409`
5. Response payload for create returns contracted fields:
   - `id, case_no, case_type, status, client_id, title_cn, primary_agent_id, recv_date, created_at`
6. Existing `/cases` endpoint behavior unchanged (no edits to `cases/api.py`).

## Verification
- `./scripts/evidence_run.sh PE-BE-CS-01 lint bash -lc 'cd backend && ruff check app/modules/consulting/api.py app/modules/consulting/service.py app/modules/cases/service.py && ruff format --check app/modules/consulting/api.py app/modules/consulting/service.py app/modules/cases/service.py'`
  - `rc=0`
- `./scripts/evidence_run.sh PE-BE-CS-01 test bash -lc 'cd backend && pytest -q'`
  - `rc=0` (`141 passed, 3 warnings`)

## Status Semantics
- `201`: consulting/search case created.
- `400`: invalid `case_type` or missing/blank required fields.
- `409`: duplicate `case_no`.
- `401/403/422`: existing auth/permission/request validation behavior.

## Evidence Files
- `artifacts/PE-BE-CS-01/results.jsonl`
- `artifacts/PE-BE-CS-01/summary.md`
- `artifacts/PE-BE-CS-01/git/diff.patch`
