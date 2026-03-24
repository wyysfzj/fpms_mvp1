# A3 Batch — Task Plan

## Tasks

### Task 1: Migration — `a3_case_field_expansion.py` (NEW)
- Chain from `a2_client_addr_01` → revision `a3_case_fields_01`
- Use `batch_alter_table` to add 15 columns (idempotent)
- No FK constraints (SQLite limitation for agent IDs)

### Task 2: ORM Models — `cases/models.py` (MODIFY)
- Add 15 `mapped_column` entries to Case class after `filing_date`
- No new imports needed (Date, Boolean, Integer, String already imported)

### Task 3: Schemas — `cases/schemas.py` (MODIFY)
- CaseCreate: add 15 optional fields
- CaseUpdateFull: add 15 optional fields
- CaseUpdateLimited: add spec_pages, claim_count
- CaseDetail: add 15 fields with None defaults
- CaseListItem: add patent_no, primary_agent_id, app_no

### Task 4: Service — `cases/service.py` (MODIFY)
- create_case(): add new fields to Case constructor
- update_case_full(): add 15 field update blocks
- update_case_limited(): add spec_pages, claim_count blocks
- list_cases(): add patent_no, primary_agent_id, app_no to CaseListItem

### Task 5: API — `cases/api.py` (MODIFY)
- POST /cases: add fields to Case constructor + response dict
- PUT /cases/{id}: add .get() calls + response dict
- GET /cases/{id}: add fields to response dict
- GET /cases: add patent_no, primary_agent_id, app_no to list dict
- GET /cases/export: same as GET /cases
- POST /cases/{id}/limited-edit: add spec_pages, claim_count

### Task 6: Tests — `test_case_fields.py` (NEW)
- 12 tests covering all 4 groups, update, limited-edit, list, backward compat

### Task 7: Quality Gate + Review
- ruff, pytest, alembic, seed, review report

## Dependencies
```
1 (migration) ─┐
2 (models)   ──┼→ 3 (schemas) → 4 (service) → 5 (API) → 6 (tests) → 7 (review)
```
