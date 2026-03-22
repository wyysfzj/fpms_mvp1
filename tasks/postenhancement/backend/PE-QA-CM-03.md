# PE-QA-CM-03 — Deferred Batch 1 Case close audit for foreign agent and extended case fields.

- Source: `tasks/postenhancement/BATCH1B_CASES_DEFERRED_MANIFEST_20260315.md`
- Type: `qa gate`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: audit closure of deferred Batch 1 scope after backend and frontend completion.
- Scope checked:
  - `FR-CM-03`
  - `FR-CM-05`
- Allowlist:
  - `backend/app/modules/cases/models.py`
  - `backend/app/modules/cases/api.py`
  - `backend/app/modules/cases/schemas.py`
  - `backend/app/modules/cases/service.py`
  - `backend/app/modules/cases/enums.py`
  - `backend/tests/test_case_fields.py`
  - `frontend/src/modules/cases/pages/CaseCreate.vue`
  - `frontend/src/modules/cases/pages/CaseEdit.vue`
  - `frontend/src/modules/cases/pages/CaseDetail.vue`
  - `frontend/src/api/cases.ts`
  - `frontend/src/api/cases.types.ts`
  - `frontend/src/api/clients.ts`
  - `docs/FPMS_Final_Enhancement_execution_summary_20260315.md`
- Audit focus:
  - allowlist compliance
  - deferred Batch 1 scope only
  - no false claim on Batch 2
  - evidence completeness
- Verification:
  - `pytest -q backend/tests/test_case_fields.py`
  - `npm run lint`
  - `npm run typecheck`
  - `./scripts/task_validate.sh PE-BE-DB-CM-02`
  - `./scripts/task_validate.sh PE-BE-CM-02`
  - `./scripts/task_validate.sh PE-FE-CM-03`

## Execution Checklist

- [ ] Confirm deferred Batch 1 only
- [ ] Run minimal BE/FE verification
- [ ] Verify no scope contamination inside claimed tasks
- [ ] Produce PASS / FAIL / BLOCKED with evidence path
