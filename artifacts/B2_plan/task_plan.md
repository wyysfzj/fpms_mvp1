# B2 Task Plan — Document Reply Chain + Auto Write-off

## Task Dependency Graph

```
T2.1 (Migration) ─┐
T2.2 (Model)    ──┤
T2.3 (Schema)   ──┼──→ T2.4 (Service: Reply Chain) ──┐
                   │                                    ├──→ Tests
                   └──→ T2.5 (Service: Template Cascade)┘
T2.6 (API + Enum) ─────────────────────────────────────┘
```

All T2.1–T2.6 can be implemented in a single pass since they are tightly coupled. Tests depend on all of them.

## Sub-Tasks

### T2.1: Migration
- **File**: `backend/alembic/versions/b2_document_reply_chain.py` (NEW)
- **Action**: Create migration adding reply_to_id, need_reply, reply_date to t_document
- **Acceptance**: `alembic upgrade head` succeeds on fresh DB

### T2.2: Model Updates
- **File**: `backend/app/modules/documents/models.py`
- **Action**: Add 3 columns + self-referential relationship to Document class
- **Acceptance**: Model matches migration columns; no import errors

### T2.3: Schema Updates
- **File**: `backend/app/modules/documents/schemas.py`
- **Action**: Add fields to DocumentCreateIn, DocumentUpdateIn, DocumentOut
- **Acceptance**: Pydantic validation passes; new fields serialized correctly

### T2.4: Service — Reply Chain Auto Write-off
- **File**: `backend/app/modules/documents/service.py`
- **Action**: In create_document(), add reply chain logic: validate reply_to_id, find OPEN tasks, close them, set reply_date
- **Acceptance**: Auto write-off works when OUT doc replies to IN doc; TaskLog created

### T2.5: Service — DocTemplate Cascade
- **File**: `backend/app/modules/documents/service.py`
- **Action**: In create_document(), cascade template.status_effect → Case.status and template.need_reply → Document.need_reply
- **Acceptance**: Case.status updated when template has status_effect; Document.need_reply set

### T2.6: API + Enum Updates
- **Files**: `backend/app/modules/documents/api.py`, `backend/app/modules/tasks/enums.py`
- **Action**: Add AUTO_WRITEOFF, STATUS_CHANGE to TaskAction; add 3 new fields to DocumentOut in 4 endpoints
- **Acceptance**: API responses include new fields; enums available

### T2.7: Tests
- **File**: `backend/tests/test_b2_reply_chain.py` (NEW)
- **Action**: Write 12 test cases covering CRUD, auto write-off, template cascade, full lifecycle
- **Acceptance**: `pytest tests/test_b2_reply_chain.py -v` all pass

## Quality Gate
```bash
cd backend && ruff check --fix . && ruff format . && ruff check . && pytest -q
```

## Implementation Order
1. T2.6 (enums only) — Add TaskAction values first
2. T2.1 — Migration
3. T2.2 — Model
4. T2.3 — Schema
5. T2.4 + T2.5 — Service logic (both in same function)
6. T2.6 (API) — Update DocumentOut construction
7. T2.7 — Tests
