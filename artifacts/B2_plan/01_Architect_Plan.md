# Batch B2 Implementation Plan — Document Reply Chain + Auto Write-off

## Executive Summary

B2 adds reply chain tracking to the Document model (reply_to_id, need_reply, reply_date) and implements two key automation rules: (1) when an OUT document is registered as a reply to an IN document, any OPEN tasks linked to that IN document are automatically closed (auto write-off), and (2) when a document is created with a DocTemplate, the template's configuration cascades to the document and case (status_effect updates Case.status, need_reply propagates to Document.need_reply). All B1 DocTemplate SPEC fields are already present in the codebase; B2 activates their orchestration logic.

---

## Current State Audit

### documents/models.py (Document class, line 51-69)
- **Fields**: id, case_id, doc_template_id, direction, doc_date, title, ref_no, extra_data
- **Relationships**: case (→ Case), attachments (→ DocAttachment[])
- **Missing for B2**: reply_to_id, need_reply, reply_date — none exist

### documents/models.py (DocTemplate class, line 30-48)
- **B1 SPEC fields present**: status_effect, status_restore, deadline_template_code, fee_draft_type, fee_item_list, need_reply, reply_to_template_code, input_fields
- **Status**: Complete, no changes needed

### documents/schemas.py
- **DocumentCreateIn** (line 20-27): case_id, doc_template_id, direction, doc_date, title, ref_no, extra_data
- **DocumentUpdateIn** (line 30-37): All optional versions of above
- **DocumentOut** (line 40-55): All fields + created_at, updated_at, attachments
- **Missing for B2**: reply_to_id, need_reply, reply_date in all three schemas

### documents/service.py — create_document() (line 76-103)
- Validates case_id exists (404)
- Validates doc_template_id exists if provided (404)
- Creates Document object with basic fields
- Commits and returns
- **Missing for B2**: No template cascade logic, no reply chain logic
- **Note**: Template variable is scoped inside `if data.doc_template_id:` block — needs restructuring

### documents/api.py — create_document endpoint (line 176-241)
- Calls create_document_service()
- Then calls TaskGenerationService().generate_from_document()
- Manually constructs DocumentOut (not model_validate) — 4 endpoints do this
- **Missing for B2**: reply_to_id, need_reply, reply_date in all DocumentOut constructions

### tasks/models.py
- **Task** (line 25-48): has document_id FK → t_document.id, status (default OPEN), done_at
- **TaskLog** (line 51-60): task_id, action, from_status, to_status, remark

### tasks/enums.py — TaskAction
- Current values: CREATE, UPDATE, ASSIGN, CLOSE, REOPEN, CANCEL, AUTO_CREATE, AUTO_CREATE_FROM_DOCUMENT
- **Missing for B2**: AUTO_WRITEOFF, STATUS_CHANGE

### tasks/service.py
- `_create_task_log()` (line 47-65): Reusable helper — creates TaskLog with UUID
- `close_task()` (line 222-242): Validates OPEN→DONE, sets done_at, creates log
- **For B2**: We'll reuse `_create_task_log()` directly rather than calling `close_task()` (which commits independently)

### tasks/task_generation_service.py
- `generate_from_document()`: Only triggers for IN documents, matches DocTemplate.code → TaskTemplate.code
- Creates Task + TaskLog(action=AUTO_CREATE_FROM_DOCUMENT)
- **For B2**: No changes needed; auto-task generation continues to work for IN docs

### cases/models.py — Case (line 21-67)
- `status`: String(32), default 'NOT_FILED' — writable, no constraints
- **For B2**: Will be updated by template cascade (status_effect)

### tests/conftest.py — Seed Data
- Task templates: OA_REPLY (add_days=120), GRANT_FEE (add_days=60)
- Doc templates: OA_IN (need_reply=True, status_effect="OA1", deadline_template_code="OA_REPLY"), OA_OUT (reply_to_template_code="OA_IN"), ACCEPTANCE_NOTICE, GRANT_NOTICE, CLIENT_IN
- **For B2**: Seeds are sufficient for testing full OA lifecycle

---

## Task Decomposition

### T2.1: Migration — Add reply chain columns to t_document

**File**: `backend/alembic/versions/b2_document_reply_chain.py` (NEW)

```
revision = "b2_doc_reply_01"
down_revision = "b1_doc_tpl_01"
```

Add 3 columns using batch_alter_table (SQLite compatible):
- `reply_to_id`: String(36), nullable, ForeignKey("t_document.id")
- `need_reply`: Boolean, nullable, server_default=sa.text("0")
- `reply_date`: Date, nullable

Pattern: Follow b1_doc_template_spec_fields.py — inspect existing columns, skip if present.

### T2.2: Model — Add 3 fields + self-referential relationship

**File**: `backend/app/modules/documents/models.py`

Add after `extra_data` (line 64):
```python
# --- B2: Reply chain fields ---
reply_to_id: Mapped[str | None] = mapped_column(
    String(36), ForeignKey("t_document.id"), nullable=True
)
need_reply: Mapped[bool | None] = mapped_column(
    Boolean, nullable=True, server_default=text("0")
)
reply_date: Mapped[date | None] = mapped_column(Date, nullable=True)
```

Add self-referential relationships:
```python
replies: Mapped[list["Document"]] = relationship(
    "Document", back_populates="reply_to_doc", foreign_keys=[reply_to_id]
)
reply_to_doc: Mapped["Document | None"] = relationship(
    "Document", back_populates="replies", remote_side="Document.id", foreign_keys=[reply_to_id]
)
```

### T2.3: Schema — Add reply fields to Document schemas

**File**: `backend/app/modules/documents/schemas.py`

- **DocumentCreateIn**: Add `reply_to_id: str | None = None`
  - Note: need_reply and reply_date are NOT user-settable on create (set by service logic)
- **DocumentUpdateIn**: Add `reply_to_id: str | None = None`, `need_reply: bool | None = None`, `reply_date: date | None = None`
- **DocumentOut**: Add `reply_to_id: str | None = None`, `need_reply: bool | None = None`, `reply_date: date | None = None`

### T2.4: Service — Reply chain auto write-off

**File**: `backend/app/modules/documents/service.py`

Modify `create_document()`:

1. **Restructure template loading** — Move `template = None` before the if-block so it's accessible later:
```python
template = None
if data.doc_template_id:
    template = db.execute(
        select(DocTemplate).where(DocTemplate.id == data.doc_template_id)
    ).scalar_one_or_none()
    if not template:
        raise_business_error(...)
```

2. **Add reply_to_id to Document constructor**:
```python
document = Document(
    ...,
    reply_to_id=data.reply_to_id,
)
```

3. **Add reply chain logic** after `db.add(document)`, before `db.commit()`:
```python
# B2: Reply chain — auto write-off
if data.reply_to_id and data.direction == DocumentDirection.OUT:
    original_doc = db.execute(
        select(Document).where(Document.id == data.reply_to_id)
    ).scalar_one_or_none()
    if not original_doc:
        raise_business_error("REPLY_TO_DOC_NOT_FOUND",
                             "Reply-to document not found", status_code=404)

    # Find OPEN tasks linked to the original document
    open_tasks = db.execute(
        select(Task).where(
            Task.document_id == data.reply_to_id,
            Task.status == TaskStatus.OPEN.value,
        )
    ).scalars().all()

    for task in open_tasks:
        task.status = TaskStatus.DONE.value
        task.done_at = datetime.utcnow()
        _create_task_log(
            db,
            task_id=task.id,
            action=TaskAction.AUTO_WRITEOFF,
            from_status=TaskStatus.OPEN.value,
            to_status=TaskStatus.DONE.value,
            remark=f"Auto write-off: reply document {document.id}",
        )

    # Update original document's reply_date
    original_doc.reply_date = data.doc_date
```

**New imports**:
```python
from datetime import datetime
from app.modules.tasks.models import Task
from app.modules.tasks.enums import TaskAction, TaskStatus
from app.modules.tasks.service import _create_task_log
```

### T2.5: Service — DocTemplate cascade

**File**: `backend/app/modules/documents/service.py`

Add after Document creation, before reply chain logic:
```python
# B2: DocTemplate cascade
if template:
    if template.need_reply:
        document.need_reply = True
    if template.status_effect:
        case.status = template.status_effect
```

### T2.6: API + Enum updates

**File**: `backend/app/modules/tasks/enums.py` — Add:
```python
AUTO_WRITEOFF = "AUTO_WRITEOFF"
STATUS_CHANGE = "STATUS_CHANGE"
```

**File**: `backend/app/modules/documents/api.py` — Update DocumentOut construction in 4 endpoints:
- `get_documents` (list, line 158-172)
- `create_document` (line 230-241)
- `get_document` (line 315-337)
- `update_document` (line 375-386)

Each gets 3 new fields:
```python
reply_to_id=document.reply_to_id,
need_reply=document.need_reply,
reply_date=document.reply_date,
```

---

## API Contract

### POST /api/v1/documents (Create Document)

**Request body** (new field: reply_to_id):
```json
{
  "case_id": "uuid",
  "doc_template_id": "uuid|null",
  "direction": "IN|OUT",
  "doc_date": "2024-01-15",
  "title": "string",
  "ref_no": "string|null",
  "extra_data": "string|null",
  "reply_to_id": "uuid|null"
}
```

**Response** (new fields: reply_to_id, need_reply, reply_date):
```json
{
  "id": "uuid",
  "case_id": "uuid",
  "doc_template_id": "uuid|null",
  "direction": "IN|OUT",
  "doc_date": "2024-01-15",
  "title": "string",
  "ref_no": "string|null",
  "extra_data": "string|null",
  "reply_to_id": "uuid|null",
  "need_reply": "bool|null",
  "reply_date": "date|null",
  "created_at": "datetime",
  "updated_at": "datetime",
  "attachments": []
}
```

**New side effects**:
- `reply_to_id` + `direction=OUT` → auto-closes OPEN tasks on replied-to document
- `doc_template_id` with `status_effect` → updates `Case.status`
- `doc_template_id` with `need_reply=True` → sets `Document.need_reply=True`

### GET /api/v1/documents, GET /api/v1/documents/{id}, PUT /api/v1/documents/{id}
Same 3 new fields in response.

---

## Test Strategy

**File**: `backend/tests/test_b2_reply_chain.py` (NEW)

### Helpers
- `_create_case(client, headers)` → Create case via POST /api/v1/cases
- `_create_document(client, headers, **kwargs)` → Create document via POST /api/v1/documents
- `_get_tasks(client, headers, case_id)` → GET /api/v1/tasks?case_id=...

### Test Cases (12)

| # | Test Name | What It Verifies |
|---|-----------|-----------------|
| 1 | test_create_document_with_reply_fields | New fields present in response, defaults correct |
| 2 | test_reply_chain_auto_writeoff | Full auto write-off: IN → task OPEN → OUT reply → task DONE |
| 3 | test_reply_chain_no_writeoff_if_no_open_tasks | No error when replying to doc with no open tasks |
| 4 | test_reply_chain_only_closes_linked_tasks | Reply closes only tasks on that specific document |
| 5 | test_reply_to_nonexistent_document_404 | 404 when reply_to_id is invalid UUID |
| 6 | test_doc_template_cascade_status_effect | Case.status updated when template has status_effect |
| 7 | test_doc_template_cascade_need_reply | Document.need_reply=True from template |
| 8 | test_doc_template_cascade_no_effect_when_null | No cascade when template fields are null |
| 9 | test_document_update_reply_fields | PUT with reply fields works |
| 10 | test_document_list_includes_reply_fields | GET list includes new fields |
| 11 | test_auto_writeoff_task_log_created | TaskLog with AUTO_WRITEOFF action exists |
| 12 | test_full_oa_lifecycle | End-to-end: case → OA_IN → task → OA_OUT reply → task closed |

---

## Risk Analysis

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Self-referential FK on SQLite | Migration could fail | batch_alter_table handles this; tested in similar patterns |
| Circular import (documents ↔ tasks) | ImportError at startup | No circular: tasks imports Document, documents will import Task — one-directional |
| _create_task_log is "private" | Fragile coupling | It's a stable module-level helper; acceptable to import |
| Multiple OPEN tasks per document | Could close more than expected | Spec says close ALL OPEN tasks linked to that document — loop handles this |
| Template variable scoping | NoneType error | Restructure: `template = None` before if-block |
| Commit timing | Partial data on error | All mutations happen before single commit at end of create_document() |

---

## Dependency Check

| B1 Artifact | Status | Location |
|------------|--------|----------|
| DocTemplate model with SPEC fields | PRESENT | documents/models.py:30-48 |
| DocTemplate schemas | PRESENT | documents/schemas.py:61-111 |
| DocTemplate CRUD service | PRESENT | documents/service.py:258-349 |
| DocTemplate CRUD API | PRESENT | documents/api.py:46-108 |
| B1 migration | PRESENT | alembic/versions/b1_doc_template_spec_fields.py |
| Test seed: OA_IN, OA_OUT templates | PRESENT | tests/conftest.py:120-155 |
| Test seed: OA_REPLY task template | PRESENT | tests/conftest.py:110-117 |
| TaskGenerationService | PRESENT | tasks/task_generation_service.py |

**All B1 dependencies verified present. B2 implementation can proceed.**
