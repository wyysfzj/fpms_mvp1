# A2 Batch — Client Multi-Address & Contact — Task Plan

## Overview
Bring `t_client_address` and `t_client_contact` tables in line with Claude_enhance.md spec:
UUID PKs, AuditMixin, spec field names, full CRUD service + API + tests.

## Tasks

### Task 1: Migration — `a2_client_address_contact.py` (NEW)
- Chain from `a1_task_template_01`
- Drop old tables, recreate with UUID PK + AuditMixin + spec fields
- Agent: backend-impl

### Task 2: ORM Models — `clients/models.py` (MODIFY)
- Add `ClientAddress` and `ClientContact` classes with UUIDPrimaryKeyMixin + AuditMixin
- Agent: backend-impl

### Task 3: Update `app/models/__init__.py`
- Change imports from `app.models.client_address` → `app.modules.masterdata.clients.models`
- Remove old model files
- Agent: backend-impl

### Task 4: Schemas — `clients/schemas.py` (MODIFY)
- Rewrite `ClientAddressOut`, `ClientContactOut` with UUID PK + spec fields
- Add `CreateIn` / `UpdateIn` for both
- Agent: backend-impl

### Task 5: Service — `clients/service.py` (MODIFY)
- Add 8 CRUD functions for addresses and contacts
- Agent: backend-impl

### Task 6: API Endpoints — `clients/api.py` (MODIFY)
- Add 8 sub-resource endpoints (4 address + 4 contact)
- Agent: backend-impl

### Task 7: Tests — `test_client_address.py` (NEW)
- 12 tests covering CRUD + cross-client 404
- Agent: test-agent

### Task 8: Quality Gate + Review
- ruff check/format, pytest, alembic upgrade + seed
- Agent: review-agent

## Dependency Graph
```
Task 1 (migration) ──┐
Task 2 (models)   ───┤
Task 3 (init.py)  ───┼─→ Task 4 (schemas) → Task 5 (service) → Task 6 (API) → Task 7 (tests) → Task 8 (review)
```

## Team Assignment
| Role | Agent Name | Tasks |
|------|-----------|-------|
| Lead | team-lead | Coordinate, plan, assign |
| Backend Impl | backend-impl | Tasks 1-6 |
| Test Agent | test-agent | Task 7 |
| Review Agent | review-agent | Task 8 |
