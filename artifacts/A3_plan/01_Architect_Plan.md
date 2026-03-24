# A3 Batch — Case Field Expansion (NORMAL Type) — Architect Plan

## 1. Context & Goal

FPMS SPEC 2.0 requires ~50 fields on T_Case. Currently only 11 fields exist. A3 adds the 15 most important fields for NORMAL case type, split into 4 risk-stratified groups. No PCT, no frontend changes.

**Migration chain**: `a2_client_addr_01` → `a3_case_fields_01`

## 2. Critical Findings

### Finding 1: API-Service Code Path Divergence
The `api.py` does NOT use `service.py` functions for most operations:
- `POST /cases` — inline ORM construction (line 171-237), NOT `service.create_case()`
- `PUT /cases/{case_id}` — inline dict-based update (line 431-458), NOT `service.update_case_full()`
- `GET /cases/{case_id}` — inline dict response (line 536-575), NOT using CaseDetail schema
- `POST /cases/{case_id}/limited-edit` — inline dict payload (line 282-292)

**Decision**: Update both the `api.py` inline code AND the `service.py` typed functions. This ensures both code paths work correctly. Do NOT refactor api.py to call service.py (out of scope, too risky).

### Finding 2: PUT endpoint uses untyped dict
`PUT /cases/{case_id}` accepts `payload: dict[str, Any]`. New fields need `.get()` calls with current value as default.

### Finding 3: POST response is minimal
`POST /cases` only returns `{id, case_no, case_type, patent_category, flow_dir, client_id}`. The 15 new fields should be returned in POST response too.

### Finding 4: No existing case field tests
No `test_case_fields.py` exists. Existing `test_v3_workflow.py` covers status enums and basic CRUD.

## 3. Files Modified (6 files)

| # | File | Action | Risk |
|---|------|--------|------|
| 1 | `backend/alembic/versions/a3_case_field_expansion.py` | NEW | Low |
| 2 | `backend/app/modules/cases/models.py` | MODIFY | Low |
| 3 | `backend/app/modules/cases/schemas.py` | MODIFY | Low |
| 4 | `backend/app/modules/cases/service.py` | MODIFY | Medium |
| 5 | `backend/app/modules/cases/api.py` | MODIFY | Medium |
| 6 | `backend/tests/test_case_fields.py` | NEW | Low |

## 4. Detailed Changes

### 4.1 Migration (`a3_case_field_expansion.py`)

Chain from: `a2_client_addr_01`
Revision ID: `a3_case_fields_01`

Use `batch_alter_table` (required for SQLite ALTER TABLE):

```python
with op.batch_alter_table("t_case") as batch_op:
    # Group 1 — Publication/Grant
    batch_op.add_column(sa.Column("pub_date", sa.Date, nullable=True))
    batch_op.add_column(sa.Column("pub_no", sa.String(64), nullable=True))
    batch_op.add_column(sa.Column("grant_date", sa.Date, nullable=True))
    batch_op.add_column(sa.Column("grant_no", sa.String(64), nullable=True))
    batch_op.add_column(sa.Column("patent_no", sa.String(64), nullable=True))
    batch_op.add_column(sa.Column("valid_until", sa.Date, nullable=True))
    # Group 2 — Spec details
    batch_op.add_column(sa.Column("spec_pages", sa.Integer, nullable=True))
    batch_op.add_column(sa.Column("claim_count", sa.Integer, nullable=True))
    batch_op.add_column(sa.Column("has_exam_request", sa.Boolean, nullable=True, server_default=sa.text("0")))
    # Group 3 — Agent assignment (no FK in migration — SQLite limitation)
    batch_op.add_column(sa.Column("primary_agent_id", sa.String(36), nullable=True))
    batch_op.add_column(sa.Column("second_agent_id", sa.String(36), nullable=True))
    batch_op.add_column(sa.Column("draftor_id", sa.String(36), nullable=True))
    # Group 4 — Control flags
    batch_op.add_column(sa.Column("is_fee_monitor", sa.Boolean, nullable=True, server_default=sa.text("0")))
    batch_op.add_column(sa.Column("fee_reduction", sa.String(16), nullable=True))
    batch_op.add_column(sa.Column("applicant_kind", sa.String(16), nullable=True))
```

Idempotent: Check existing columns first.

### 4.2 Models (`cases/models.py`)

Add 15 `mapped_column` entries to `Case` class after `filing_date` (line 44):

```python
# Group 1 — Publication/Grant
pub_date: Mapped[date | None] = mapped_column(Date, nullable=True)
pub_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
grant_date: Mapped[date | None] = mapped_column(Date, nullable=True)
grant_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
patent_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
valid_until: Mapped[date | None] = mapped_column(Date, nullable=True)

# Group 2 — Specification
spec_pages: Mapped[int | None] = mapped_column(Integer, nullable=True)
claim_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
has_exam_request: Mapped[bool | None] = mapped_column(Boolean, nullable=True, server_default=text("0"))

# Group 3 — Agent assignment (app-level FK, not DB-level for SQLite compat)
primary_agent_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
second_agent_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
draftor_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

# Group 4 — Control flags
is_fee_monitor: Mapped[bool | None] = mapped_column(Boolean, nullable=True, server_default=text("0"))
fee_reduction: Mapped[str | None] = mapped_column(String(16), nullable=True)
applicant_kind: Mapped[str | None] = mapped_column(String(16), nullable=True)
```

### 4.3 Schemas (`cases/schemas.py`)

**CaseCreate** (line 32) — add all 15 fields as optional:
```python
# Group 1
pub_date: date | None = None
pub_no: str | None = None
grant_date: date | None = None
grant_no: str | None = None
patent_no: str | None = None
valid_until: date | None = None
# Group 2
spec_pages: int | None = None
claim_count: int | None = None
has_exam_request: bool | None = None
# Group 3
primary_agent_id: str | None = None
second_agent_id: str | None = None
draftor_id: str | None = None
# Group 4
is_fee_monitor: bool | None = None
fee_reduction: str | None = None
applicant_kind: str | None = None
```

**CaseUpdateFull** (line 50) — add same 15 fields as optional

**CaseUpdateLimited** (line 60) — add `spec_pages: int | None = None` and `claim_count: int | None = None`

**CaseDetail** (line 68) — add all 15 fields with None defaults

**CaseListItem** (line 89) — add `app_no`, `patent_no`, `primary_agent_id` (most useful for list view)

### 4.4 Service (`cases/service.py`)

**`create_case()`** (line 109) — Add new fields to Case constructor. Use generic approach:
```python
# After existing explicit fields, add new A3 fields
pub_date=data.pub_date,
pub_no=data.pub_no,
...
```

**`update_case_full()`** (line 181) — Add 15 new `if data.field is not None` blocks following existing pattern.

**`update_case_limited()`** (line 250) — Add `spec_pages` and `claim_count` update blocks.

**`list_cases()`** (line 61) — Add `patent_no`, `primary_agent_id`, `app_no` to CaseListItem construction.

### 4.5 API (`cases/api.py`)

**`POST /cases`** (line 125):
- Add new fields to Case constructor (line 171-181)
- Add new fields to response dict (line 242-249)

**`PUT /cases/{case_id}`** (line 400):
- Add 15 `.get()` calls for new fields (line 444-448)
- Add new fields to response dict (line 452-459)

**`GET /cases/{case_id}`** (line 462):
- Add 15 new fields to response dict (line 536-575)

**`GET /cases`** (line 20):
- Add `patent_no`, `primary_agent_id`, `app_no` to list item dict (line 105-120)

**`GET /cases/export`** (line 295):
- Same additions as GET /cases list

**`POST /cases/{case_id}/limited-edit`** (line 252):
- Add `spec_pages` and `claim_count` to allowed fields

### 4.6 Tests (`test_case_fields.py`)

12 tests:
1. `test_create_with_group1_fields` — pub_date, pub_no, grant_date, grant_no, patent_no, valid_until
2. `test_create_with_group2_fields` — spec_pages, claim_count, has_exam_request
3. `test_create_with_group3_fields` — primary_agent_id, second_agent_id, draftor_id
4. `test_create_with_group4_fields` — is_fee_monitor, fee_reduction, applicant_kind
5. `test_create_all_15_fields` — All fields together, verify in GET detail
6. `test_update_full_new_fields` — PUT updates all 15 fields
7. `test_limited_edit_spec_fields` — limited-edit allows spec_pages, claim_count
8. `test_limited_edit_rejects_other_new_fields` — limited-edit does NOT allow pub_date etc.
9. `test_list_includes_new_fields` — GET /cases list includes patent_no, primary_agent_id
10. `test_backward_compat_no_new_fields` — Create case without any new field → still works
11. `test_date_fields_format` — Date fields round-trip correctly (ISO format)
12. `test_boolean_defaults` — has_exam_request and is_fee_monitor default to false

## 5. Task Dependency Graph

```
Task 1 (migration) ──┐
Task 2 (models)   ───┼─→ Task 3 (schemas) ──→ Task 4 (service) ──→ Task 5 (API) ──→ Task 6 (tests) ──→ Task 7 (quality gate)
```

Tasks 1-2 are independent (migration + models).
Tasks 3-5 are sequential (schemas → service → API).
Task 6 (tests) requires all above.
Task 7 (quality gate + review) is final.

## 6. Risk Analysis

| Risk | Mitigation |
|------|-----------|
| SQLite batch_alter_table FK | Skip FK constraints in migration, use String(36) only |
| Hand-built dicts in api.py miss fields | Systematic approach: add all 15 to every dict construction |
| PUT payload is untyped dict | Use `.get()` with current value as default |
| Backward compatibility | All 15 columns nullable, no existing field changes |
| Agent ID validation | App-level only (no DB FK), accept any String(36) |

## 7. API Contract Changes

### POST /cases — Request adds 15 optional fields
```json
{
  "case_no": "...",
  // existing fields...
  "pub_date": "2024-01-15",      // NEW, optional
  "pub_no": "CN123456A",          // NEW, optional
  "grant_date": "2024-06-01",     // NEW, optional
  "grant_no": "CN123456B",        // NEW, optional
  "patent_no": "ZL202012345.6",   // NEW, optional
  "valid_until": "2044-01-15",    // NEW, optional
  "spec_pages": 42,               // NEW, optional
  "claim_count": 10,              // NEW, optional
  "has_exam_request": true,        // NEW, optional
  "primary_agent_id": "uuid...",   // NEW, optional
  "second_agent_id": "uuid...",    // NEW, optional
  "draftor_id": "uuid...",         // NEW, optional
  "is_fee_monitor": false,         // NEW, optional
  "fee_reduction": "PARTIAL",      // NEW, optional
  "applicant_kind": "ENTITY"       // NEW, optional
}
```

### GET /cases/{id} — Response adds all 15 fields
### GET /cases — List items add: patent_no, primary_agent_id, app_no
### PUT /cases/{id} — Request/response adds all 15 fields

## 8. Quality Gate

```bash
cd backend && source .venv/bin/activate
ruff check --fix . && ruff format .
ruff check .
pytest -q
rm -f fpms_dev.db && alembic upgrade head && python scripts/seed_dev.py
```

## 9. Team Assignment

| Task | Agent | Notes |
|------|-------|-------|
| Tasks 1-5 | Backend Agent | Sequential impl |
| Task 6 | Test Agent | After backend done |
| Task 7 | Reviewer Agent | After tests pass |
