# A4 Batch — Task Plan

## Summary
Close remaining gaps in Batch A4 (SystemParam CRUD API). Most work is already done; 3 tasks remain.

## Gap Analysis
- service.py: missing `get_param(db, key)` function
- seed_dev.py: missing default system param seeds
- tests: no test coverage for system param endpoints

## Tasks

### TASK-1: Add get_param service function [backend-impl]
- File: `backend/app/modules/system/service.py`
- Add `get_system_param(db, key)` returning `SystemParam | None`
- Blocked by: nothing

### TASK-2: Seed default system params [backend-impl]
- File: `backend/scripts/seed_dev.py`
- Add `seed_system_params(db)` — 4 default params, idempotent
- Call from `main()`
- Blocked by: nothing

### TASK-3: Write system param tests [test-impl]
- File: `backend/tests/test_system_params.py` (new)
- 5-6 test cases covering list, upsert, masking, auth
- Blocked by: TASK-2 (needs seeds for test assertions)

### TASK-4: Review all changes [reviewer]
- Read all modified files, check acceptance criteria
- Write `artifacts/A4_plan/review_report.md`
- Blocked by: TASK-1, TASK-2, TASK-3

## Dependency Graph
```
TASK-1 ──────────────────┐
TASK-2 ── → TASK-3 ──── → TASK-4 (review)
```

## Acceptance Criteria
1. `get_system_param(db, key)` exists and works
2. `seed_dev.py` seeds 4 default params idempotently
3. All tests pass: `pytest tests/test_system_params.py -v`
4. Full suite passes: `pytest -q`
5. Lint clean: `ruff check .`
6. Fresh DB works: `rm fpms_dev.db && alembic upgrade head && python scripts/seed_dev.py`
