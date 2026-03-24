# A4 Batch — Task Plan

## Objective
Close remaining gaps in SystemParam CRUD API: add `get_system_param` service function, seed default params, write tests.

## Task Decomposition

### Task 1: Add `get_system_param` service function
- **File**: `backend/app/modules/system/service.py`
- **Agent**: backend-impl
- **Change**: Add `get_system_param(db, key)` that returns `SystemParam | None`

### Task 2: Seed default system params
- **File**: `backend/scripts/seed_dev.py`
- **Agent**: backend-impl
- **Change**: Add `seed_system_params(db)` function seeding 4 default params, call from `main()`
- **Depends on**: Task 1

### Task 3: Write tests
- **File**: `backend/tests/test_system_params.py` (new)
- **Agent**: test-impl
- **Tests**: list, unauthorized, upsert create/update, secret masking, forbidden
- **Depends on**: Tasks 1 + 2

### Task 4: Review
- **Agent**: reviewer
- **Action**: Read all changed files, verify acceptance criteria, write review_report.md
- **Depends on**: Task 3

## Dependency Graph
```
Task 1 (service) ──┐
                   ├──> Task 3 (tests) ──> Task 4 (review)
Task 2 (seed)   ──┘
```

## Acceptance Criteria
1. `get_system_param(db, key)` exists and works
2. `seed_dev.py` seeds 4 default params idempotently
3. All 6 tests pass in `test_system_params.py`
4. `pytest -q` full suite passes
5. `ruff check .` clean
6. Fresh DB rebuild works: `rm -f fpms_dev.db && alembic upgrade head && python scripts/seed_dev.py`
