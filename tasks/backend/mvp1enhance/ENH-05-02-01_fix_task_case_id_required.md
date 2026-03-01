# ENH-05-02-01 — Tasks schema fix: require case_id (align with DB NOT NULL)

## Context / Why
POST /api/v1/tasks currently fails with 500 because DB enforces:
- t_task.case_id is NOT NULL

But TaskCreateIn allows case_id=None, causing IntegrityError on insert.

## Target (Atomic – FIXED)
Align API contract with DB constraint by making `case_id` required in `TaskCreateIn`.

## Allowed files (Strict allowlist)
- backend/app/modules/tasks/schemas.py ONLY

## Non-scope
- Do NOT change DB schema/migrations
- Do NOT change service.py or api.py in this task

## Required change (EXACT)
In `TaskCreateIn`:
- Change `case_id: str | None = None` to `case_id: str` (required)
- Keep other fields unchanged

## Acceptance checklist
- [ ] Only schemas.py changed
- [ ] Missing case_id yields HTTP 422 (schema validation)
- [ ] Ruff + py_compile pass

## Evidence
```bash
export FPMS_TOKEN="REPLACE_ME"
curl -i -H "Authorization: Bearer $FPMS_TOKEN" -H "Content-Type: application/json" \
  -d '{"title":"Test task","due_date":"2026-01-24"}' \
  "http://localhost:8000/api/v1/tasks"
```
Expected: 422

## Validation (MUST RUN)
```bash
./scripts/evidence_run.sh ENH-05-02-01 lint bash -lc "cd backend && ruff check app/modules/tasks/schemas.py"
./scripts/evidence_run.sh ENH-05-02-01 fmt  bash -lc "cd backend && ruff format app/modules/tasks/schemas.py"
./scripts/evidence_run.sh ENH-05-02-01 test bash -lc "cd backend && python3 -m py_compile app/modules/tasks/schemas.py"
./scripts/evidence_finalize.sh ENH-05-02-01
./scripts/task_validate.sh ENH-05-02-01
```

## STOP Contract
STOP if any change outside schemas.py is required.
