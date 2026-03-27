# FR-FE-06: Annuity Task Generation + Model Extension — Summary

- **Task**: FR-FE-06 (P0 #3 — 年费管理 API/UI)
- **Role**: Implementation (subagent-driven)
- **Result**: `PASS`
- **Date**: 2026-03-25

## Exact Closure Slice

Multi-year annuity task generation API, 6 new model fields on T_AnnuityTask, first_annuity_year on T_Case, computed is_overdue, updated list response, frontend generate dialog + list column updates.

## Explicit Non-Closure

- Does NOT implement auto-trigger on case GRANTED status (deferred to P1)
- Does NOT implement notice letter generation (document generation excluded)
- Does NOT implement rolling generation strategy (manual endpoint only)

## Files Changed

### Backend
- `backend/alembic/versions/pe_fr_fe_06_annuity_task_ext.py` — NEW migration (6 cols on t_annuity_task + 1 col on t_case)
- `backend/app/modules/annuity/models.py` — 6 new mapped_column fields
- `backend/app/modules/cases/models.py` — first_annuity_year field
- `backend/app/modules/annuity/service.py` — generate_annuity_tasks_for_case, updated _rate_amount, draft_generated flag
- `backend/app/modules/annuity/api.py` — POST /annuity/tasks/generate endpoint, updated list response
- `backend/app/modules/cases/schemas.py` — optional status field in CaseCreate (for test support)
- `backend/app/modules/cases/service.py` — apply status from schema
- `backend/tests/test_annuity_generate.py` — 11 tests

### Frontend
- `frontend/src/api/annuity.types.ts` — 7 new fields on AnnuityTask + 2 new interfaces
- `frontend/src/api/annuity.ts` — generateAnnuityTasks function
- `frontend/src/modules/annuity/components/AnnuityGenerateDialog.vue` — NEW dialog
- `frontend/src/modules/annuity/pages/AnnuityTaskList.vue` — 6 new columns + generate button

## Validation

- `pytest tests/test_annuity_generate.py -v` → 11 passed
- `rm -f fpms_dev.db && alembic upgrade head && python scripts/seed_dev.py` → success (29 migrations)
- `npm run lint` → PASS
- `npm run typecheck` → PASS
- `npm run build` → PASS
