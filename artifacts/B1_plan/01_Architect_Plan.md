# B1 Architect Plan: DocTemplate Enhancement + CRUD API

**Batch**: B1
**Date**: 2026-02-25
**Status**: Final

---

## 1. Gap Analysis

### What Exists Today

| Component | Current State |
|-----------|---------------|
| **Model** (`documents/models.py:30-37`) | `DocTemplate` has 4 fields: `code`, `name`, `direction`, `enabled`. Inherits `UUIDPrimaryKeyMixin` + `AuditMixin`. Table: `t_doc_template`. |
| **Migration** (`0002_documents.py`) | Created `t_doc_template` with `id`, `code`, `name`, `direction`, `enabled`. No audit columns in original DDL (AuditMixin adds them via ORM default). |
| **Schemas** (`documents/schemas.py`) | No DocTemplate schemas at all. Only `DocumentCreateIn/UpdateIn/Out` and `DocAttachmentOut`. |
| **Service** (`documents/service.py`) | No DocTemplate CRUD functions. `DocTemplate` is only queried for FK validation when creating/updating Documents. |
| **API** (`documents/api.py`) | No `/doc-templates` endpoints. Only `/documents` and `/documents/{id}/attachments` endpoints. |
| **Permissions** (`rbac/service.py`) | `Doc.Read`, `Doc.Create`, `Doc.Edit`, `Doc.Attach` exist. No `DocTemplate.*` permissions. |
| **Seed** (`seed_dev.py`) | No DocTemplate seed data. Only seeds roles, admin user, cases, task templates, system params. |
| **Tests** | No `test_doc_template.py` exists. |

### What Needs to Be Added

| Component | Change Required |
|-----------|----------------|
| **Migration** | Add 8 new columns to `t_doc_template` via `batch_alter_table` |
| **Model** | Add 8 new mapped columns to `DocTemplate` class |
| **Schemas** | Add `DocTemplateCreateIn`, `DocTemplateUpdateIn`, `DocTemplateOut`, `DocTemplateListOut` |
| **Service** | Add `list_doc_templates()`, `get_doc_template()`, `create_doc_template()`, `update_doc_template()` |
| **API** | Add 4 endpoints under `/doc-templates` prefix |
| **Permissions** | Register `DocTemplate.Read`, `DocTemplate.Create`, `DocTemplate.Edit` in `ROLE_PERMISSIONS["Admin"]` |
| **Seed** | Add `seed_doc_templates()` function with 5 template entries |
| **Tests** | Add `test_doc_template.py` with CRUD + edge-case tests |
| **Router** | No change needed -- `documents_router` is already included in `api_router` |

---

## 2. Task Decomposition

| # | Sub-Task | Files Modified | Depends On |
|---|----------|----------------|------------|
| T1 | Write Alembic migration to add 8 columns to `t_doc_template` | `backend/alembic/versions/b1_doc_template_spec_fields.py` (new) | -- |
| T2 | Add 8 new fields to `DocTemplate` model class | `backend/app/modules/documents/models.py` | T1 |
| T3 | Create DocTemplate Pydantic schemas | `backend/app/modules/documents/schemas.py` | T2 |
| T4 | Create DocTemplate CRUD service functions | `backend/app/modules/documents/service.py` | T2, T3 |
| T5 | Create 4 DocTemplate API endpoints | `backend/app/modules/documents/api.py` | T3, T4 |
| T6 | Register `DocTemplate.*` permissions in RBAC | `backend/app/modules/rbac/service.py` | -- |
| T7 | Add `seed_doc_templates()` to seed script | `backend/scripts/seed_dev.py` | T2 |
| T8 | Seed DocTemplate data in test `conftest.py` | `backend/tests/conftest.py` | T2 |
| T9 | Write `test_doc_template.py` test file | `backend/tests/test_doc_template.py` (new) | T5, T6, T8 |

**Implementation order**: T1 -> T2 -> T3 -> T4 -> T5 -> T6 -> T7 -> T8 -> T9

Since T6 is independent of T1-T5, it can be done in parallel. However, for a single implementation agent, the linear order above is simplest.

---

## 3. Migration Details

**File**: `backend/alembic/versions/b1_doc_template_spec_fields.py`

**Revision chain**: `down_revision = "a3_case_fields_01"` (the latest migration head)

**Pattern**: Follow `a1_task_template_fields.py` -- use `batch_alter_table`, check existing columns for idempotency.

```python
"""b1_doc_template_spec_fields

Revision ID: b1_doc_tpl_01
Revises: a3_case_fields_01
Create Date: 2026-02-25

Add SPEC configuration fields to t_doc_template for downstream automation.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "b1_doc_tpl_01"
down_revision = "a3_case_fields_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    if not insp.has_table("t_doc_template"):
        return

    existing = {col["name"] for col in insp.get_columns("t_doc_template")}

    new_columns = []
    if "status_effect" not in existing:
        new_columns.append(sa.Column("status_effect", sa.String(32), nullable=True))
    if "status_restore" not in existing:
        new_columns.append(sa.Column("status_restore", sa.String(32), nullable=True))
    if "deadline_template_code" not in existing:
        new_columns.append(sa.Column("deadline_template_code", sa.String(64), nullable=True))
    if "fee_draft_type" not in existing:
        new_columns.append(sa.Column("fee_draft_type", sa.String(32), nullable=True))
    if "fee_item_list" not in existing:
        new_columns.append(sa.Column("fee_item_list", sa.Text, nullable=True))
    if "need_reply" not in existing:
        new_columns.append(
            sa.Column("need_reply", sa.Boolean, nullable=True, server_default=sa.text("0"))
        )
    if "reply_to_template_code" not in existing:
        new_columns.append(sa.Column("reply_to_template_code", sa.String(64), nullable=True))
    if "input_fields" not in existing:
        new_columns.append(sa.Column("input_fields", sa.Text, nullable=True))

    if new_columns:
        with op.batch_alter_table("t_doc_template") as batch_op:
            for column in new_columns:
                batch_op.add_column(column)


def downgrade() -> None:
    pass
```

**SQLite compatibility notes**:
- All new columns are `nullable=True` (required for SQLite ALTER TABLE)
- `need_reply` uses `server_default=sa.text("0")` (SQLite boolean convention)
- No foreign keys added to these columns (they store reference codes, not FK UUIDs)
- `batch_alter_table` used for SQLite compatibility
- Idempotent column checks via `sa.inspect(bind).get_columns()`

---

## 4. Model Changes

**File**: `backend/app/modules/documents/models.py`

Add 8 fields to `DocTemplate` class (lines 30-37), after the existing `enabled` field:

```python
class DocTemplate(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_doc_template"

    # --- existing fields ---
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    direction: Mapped[str] = mapped_column(String(8), nullable=False, server_default=text("'IN'"))
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("1"))

    # --- B1: SPEC configuration fields ---
    status_effect: Mapped[str | None] = mapped_column(String(32), nullable=True)
    status_restore: Mapped[str | None] = mapped_column(String(32), nullable=True)
    deadline_template_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    fee_draft_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    fee_item_list: Mapped[str | None] = mapped_column(Text, nullable=True)
    need_reply: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, server_default=text("0")
    )
    reply_to_template_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    input_fields: Mapped[str | None] = mapped_column(Text, nullable=True)
```

**Notes**:
- `fee_item_list` and `input_fields` are `Text` storing JSON strings. No JSON column type (SQLite has no native JSON type with schema enforcement).
- `need_reply` defaults to `False` (0) via `server_default`.
- All new fields are nullable to maintain backward compatibility with existing rows.

---

## 5. Schema Definitions

**File**: `backend/app/modules/documents/schemas.py`

Add these schemas after the existing `DocumentListOut` class:

```python
from app.modules.documents.enums import DocumentDirection


class DocTemplateCreateIn(BaseModel):
    code: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., min_length=1, max_length=256)
    direction: DocumentDirection = DocumentDirection.IN
    enabled: bool = True
    status_effect: str | None = Field(default=None, max_length=32)
    status_restore: str | None = Field(default=None, max_length=32)
    deadline_template_code: str | None = Field(default=None, max_length=64)
    fee_draft_type: str | None = Field(default=None, max_length=32)
    fee_item_list: str | None = None  # JSON string
    need_reply: bool | None = False
    reply_to_template_code: str | None = Field(default=None, max_length=64)
    input_fields: str | None = None  # JSON string


class DocTemplateUpdateIn(BaseModel):
    name: str | None = Field(default=None, max_length=256)
    direction: DocumentDirection | None = None
    enabled: bool | None = None
    status_effect: str | None = Field(default=None, max_length=32)
    status_restore: str | None = Field(default=None, max_length=32)
    deadline_template_code: str | None = Field(default=None, max_length=64)
    fee_draft_type: str | None = Field(default=None, max_length=32)
    fee_item_list: str | None = None
    need_reply: bool | None = None
    reply_to_template_code: str | None = Field(default=None, max_length=64)
    input_fields: str | None = None


class DocTemplateOut(BaseModel):
    id: str
    code: str
    name: str
    direction: DocumentDirection
    enabled: bool
    status_effect: str | None = None
    status_restore: str | None = None
    deadline_template_code: str | None = None
    fee_draft_type: str | None = None
    fee_item_list: str | None = None
    need_reply: bool | None = None
    reply_to_template_code: str | None = None
    input_fields: str | None = None
    created_at: datetime
    updated_at: datetime


class DocTemplateListOut(PageResult[DocTemplateOut]):
    pass
```

**Design decisions**:
- `DocTemplateCreateIn.code` is required (unique business key). `DocTemplateUpdateIn` does NOT include `code` -- it is immutable once created.
- `need_reply` defaults to `False` on create (consistent with DB `server_default=text("0")`).
- `fee_item_list` and `input_fields` are plain `str | None` -- the JSON validation is application-level (not schema-enforced in Pydantic). This keeps the schema simple and avoids type coercion issues.
- `DocumentDirection` enum is reused for the `direction` field validation.

---

## 6. Service Functions

**File**: `backend/app/modules/documents/service.py`

Add 4 new functions. Follow the pattern from `templates/service.py` (list/get/create/update).

### `list_doc_templates()`

```python
def list_doc_templates(
    db: Session,
    *,
    direction: DocumentDirection | None = None,
    enabled: bool | None = None,
    q: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[DocTemplate], int]:
    """List doc templates with optional filters and pagination."""
    stmt = select(DocTemplate)

    if direction:
        stmt = stmt.where(DocTemplate.direction == direction)
    if enabled is not None:
        stmt = stmt.where(DocTemplate.enabled == enabled)
    if q:
        q_like = f"%{q.lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(DocTemplate.code).like(q_like),
                func.lower(DocTemplate.name).like(q_like),
            )
        )

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    offset = (page - 1) * page_size
    stmt = stmt.order_by(DocTemplate.code.asc()).offset(offset).limit(page_size)
    items = db.execute(stmt).scalars().all()
    return items, total
```

### `get_doc_template()`

```python
def get_doc_template(db: Session, template_id: str) -> DocTemplate:
    """Get a single doc template by ID. Raises 404 if not found."""
    template = db.execute(
        select(DocTemplate).where(DocTemplate.id == template_id)
    ).scalar_one_or_none()
    if not template:
        raise_business_error(
            "DOC_TEMPLATE_NOT_FOUND", "Doc template not found", status_code=404
        )
    return template
```

### `create_doc_template()`

```python
from app.modules.documents.schemas import DocTemplateCreateIn

def create_doc_template(db: Session, data: DocTemplateCreateIn) -> DocTemplate:
    """Create a new doc template. Raises 409 if code already exists."""
    existing = db.execute(
        select(DocTemplate).where(DocTemplate.code == data.code)
    ).scalar_one_or_none()
    if existing:
        raise_business_error(
            "DOC_TEMPLATE_CODE_EXISTS",
            f"Doc template code '{data.code}' already exists",
            status_code=409,
        )

    template = DocTemplate(
        id=str(uuid4()),
        code=data.code,
        name=data.name,
        direction=data.direction,
        enabled=data.enabled,
        status_effect=data.status_effect,
        status_restore=data.status_restore,
        deadline_template_code=data.deadline_template_code,
        fee_draft_type=data.fee_draft_type,
        fee_item_list=data.fee_item_list,
        need_reply=data.need_reply,
        reply_to_template_code=data.reply_to_template_code,
        input_fields=data.input_fields,
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template
```

### `update_doc_template()`

```python
from app.modules.documents.schemas import DocTemplateUpdateIn

def update_doc_template(
    db: Session, template_id: str, data: DocTemplateUpdateIn
) -> DocTemplate:
    """Update an existing doc template. Raises 404 if not found."""
    template = db.execute(
        select(DocTemplate).where(DocTemplate.id == template_id)
    ).scalar_one_or_none()
    if not template:
        raise_business_error(
            "DOC_TEMPLATE_NOT_FOUND", "Doc template not found", status_code=404
        )

    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(template, field, value)

    db.commit()
    db.refresh(template)
    return template
```

**Import additions needed** at top of `service.py`:
```python
from app.modules.documents.schemas import DocTemplateCreateIn, DocTemplateUpdateIn
```

---

## 7. API Contract

**File**: `backend/app/modules/documents/api.py`

All endpoints are added to the existing `router = APIRouter()` in `documents/api.py`. Since `documents_router` is already registered in `api_router` without a prefix (documents endpoints use `/documents` explicitly), the new endpoints will use `/doc-templates` path prefix.

### Endpoint 1: List DocTemplates

| Property | Value |
|----------|-------|
| **Method** | `GET` |
| **Path** | `/doc-templates` |
| **Permission** | `DocTemplate.Read` |
| **Query Params** | `q: str \| None`, `direction: DocumentDirection \| None`, `enabled: bool \| None`, `page: int = 1`, `page_size: int = 20` |
| **Response** | `200 DocTemplateListOut` |
| **Errors** | 401, 403, 422 |

### Endpoint 2: Create DocTemplate

| Property | Value |
|----------|-------|
| **Method** | `POST` |
| **Path** | `/doc-templates` |
| **Permission** | `DocTemplate.Create` |
| **Request Body** | `DocTemplateCreateIn` |
| **Response** | `201 DocTemplateOut` |
| **Errors** | 401, 403, 409 (duplicate code), 422 |

### Endpoint 3: Get DocTemplate by ID

| Property | Value |
|----------|-------|
| **Method** | `GET` |
| **Path** | `/doc-templates/{template_id}` |
| **Permission** | `DocTemplate.Read` |
| **Response** | `200 DocTemplateOut` |
| **Errors** | 401, 403, 404, 422 |

### Endpoint 4: Update DocTemplate

| Property | Value |
|----------|-------|
| **Method** | `PUT` |
| **Path** | `/doc-templates/{template_id}` |
| **Permission** | `DocTemplate.Edit` |
| **Request Body** | `DocTemplateUpdateIn` |
| **Response** | `200 DocTemplateOut` |
| **Errors** | 401, 403, 404, 422 |

**API implementation pattern** (following `templates/api.py` style):

```python
@router.get("/doc-templates", response_model=DocTemplateListOut, summary="List doc templates")
def list_doc_templates_endpoint(
    q: str | None = Query(default=None),
    direction: DocumentDirection | None = Query(default=None),
    enabled: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    _perm: None = Depends(require_perm("DocTemplate.Read")),
    db: Session = Depends(get_db),
) -> DocTemplateListOut:
    ...


@router.post(
    "/doc-templates",
    status_code=status.HTTP_201_CREATED,
    response_model=DocTemplateOut,
    summary="Create a doc template",
)
def create_doc_template_endpoint(
    payload: DocTemplateCreateIn,
    _perm: None = Depends(require_perm("DocTemplate.Create")),
    db: Session = Depends(get_db),
) -> DocTemplateOut:
    ...


@router.get(
    "/doc-templates/{template_id}",
    response_model=DocTemplateOut,
    summary="Get a doc template",
)
def get_doc_template_endpoint(
    template_id: str,
    _perm: None = Depends(require_perm("DocTemplate.Read")),
    db: Session = Depends(get_db),
) -> DocTemplateOut:
    ...


@router.put(
    "/doc-templates/{template_id}",
    response_model=DocTemplateOut,
    summary="Update a doc template",
)
def update_doc_template_endpoint(
    template_id: str,
    payload: DocTemplateUpdateIn,
    _perm: None = Depends(require_perm("DocTemplate.Edit")),
    db: Session = Depends(get_db),
) -> DocTemplateOut:
    ...
```

**Note on response construction**: The API layer should construct `DocTemplateOut` from the ORM model. Two approaches exist in the codebase:
1. Manual field mapping (used in `documents/api.py` for `DocumentOut`)
2. `Model.model_validate(obj)` with `from_attributes=True` (used in `templates/api.py`)

**Recommendation**: Use approach 2 (add `model_config = ConfigDict(from_attributes=True)` to `DocTemplateOut`). This is cleaner and less error-prone for a model with 14+ fields.

---

## 8. Seed Data

**File**: `backend/scripts/seed_dev.py`

Add a new function `seed_doc_templates()` and call it in `main()`.

```python
from app.modules.documents.models import DocTemplate  # add to imports

def seed_doc_templates(db: Session) -> None:
    """Seed default doc templates. Idempotent."""
    templates = [
        {
            "code": "OA_IN",
            "name": "审查意见通知书（收文）",
            "direction": "IN",
            "need_reply": True,
            "deadline_template_code": "OA_REPLY",
            "status_effect": "OA1",
            "status_restore": None,
            "fee_draft_type": None,
            "fee_item_list": None,
            "reply_to_template_code": None,
            "input_fields": None,
        },
        {
            "code": "OA_OUT",
            "name": "审查意见答复书（发文）",
            "direction": "OUT",
            "need_reply": False,
            "deadline_template_code": None,
            "status_effect": None,
            "status_restore": None,
            "fee_draft_type": None,
            "fee_item_list": None,
            "reply_to_template_code": "OA_IN",
            "input_fields": None,
        },
        {
            "code": "ACCEPTANCE_NOTICE",
            "name": "受理通知书",
            "direction": "IN",
            "need_reply": False,
            "deadline_template_code": None,
            "status_effect": "ACCEPTED",
            "status_restore": None,
            "fee_draft_type": None,
            "fee_item_list": None,
            "reply_to_template_code": None,
            "input_fields": None,
        },
        {
            "code": "GRANT_NOTICE",
            "name": "授权通知书",
            "direction": "IN",
            "need_reply": False,
            "deadline_template_code": None,
            "status_effect": "GRANT_PENDING",
            "status_restore": None,
            "fee_draft_type": "GRANT_FEE",
            "fee_item_list": None,
            "reply_to_template_code": None,
            "input_fields": None,
        },
        {
            "code": "CLIENT_IN",
            "name": "客户来函",
            "direction": "IN",
            "need_reply": False,
            "deadline_template_code": None,
            "status_effect": None,
            "status_restore": None,
            "fee_draft_type": None,
            "fee_item_list": None,
            "reply_to_template_code": None,
            "input_fields": None,
        },
    ]
    created = 0
    for t in templates:
        existing = db.query(DocTemplate).filter(DocTemplate.code == t["code"]).first()
        if not existing:
            db.add(DocTemplate(id=str(uuid4()), **t))
            created += 1
    db.commit()
    if created:
        print(f"Created {created} doc templates")
    else:
        print("Doc templates already exist, skipping")
```

**Call order in `main()`**: Add after `seed_task_templates(db)` and before `seed_system_params(db)`:
```python
print("Seeding doc templates...")
seed_doc_templates(db)
print("Doc templates seeded")
```

---

## 9. Permission Registration

**File**: `backend/app/modules/rbac/service.py`

Add 3 new permission codes to `ROLE_PERMISSIONS["Admin"]`:

```python
"DocTemplate.Create",
"DocTemplate.Edit",
"DocTemplate.Read",
```

Insert alphabetically after the existing `Doc.*` entries (after `"Doc.Read"`).

Also add `DocTemplate.Read` to the `"Formalities"` role (they need to see templates to register documents):
```python
"DocTemplate.Read",
```

---

## 10. Test Conftest Changes

**File**: `backend/tests/conftest.py`

Add a `_seed_doc_templates()` helper and call it within the `seed_data` fixture, similar to `_seed_task_templates()`.

```python
from app.modules.documents.models import DocTemplate  # add import

def _seed_doc_templates(db: Session) -> None:
    """Seed doc templates into the test DB. Idempotent."""
    templates = [
        {
            "code": "OA_IN",
            "name": "OA收文",
            "direction": "IN",
            "need_reply": True,
            "deadline_template_code": "OA_REPLY",
            "status_effect": "OA1",
        },
        {
            "code": "OA_OUT",
            "name": "OA答复",
            "direction": "OUT",
            "reply_to_template_code": "OA_IN",
        },
        {
            "code": "ACCEPTANCE_NOTICE",
            "name": "受理通知书",
            "direction": "IN",
            "status_effect": "ACCEPTED",
        },
        {
            "code": "GRANT_NOTICE",
            "name": "授权通知书",
            "direction": "IN",
            "status_effect": "GRANT_PENDING",
            "fee_draft_type": "GRANT_FEE",
        },
        {
            "code": "CLIENT_IN",
            "name": "客户来函",
            "direction": "IN",
            "need_reply": False,
        },
    ]
    for t in templates:
        existing = db.query(DocTemplate).filter(DocTemplate.code == t["code"]).first()
        if not existing:
            db.add(DocTemplate(id=str(uuid4()), **t))
```

Call `_seed_doc_templates(db)` inside the `seed_data` fixture, after `_seed_task_templates(db)`.

---

## 11. Test Strategy

**File**: `backend/tests/test_doc_template.py` (new)

### Test Cases

| # | Test Name | Behavior Verified |
|---|-----------|-------------------|
| 1 | `test_list_doc_templates_returns_seeded` | GET `/doc-templates` returns 200, contains seeded OA_IN, OA_OUT, etc. Verify `need_reply`, `status_effect` fields. |
| 2 | `test_list_doc_templates_filter_direction` | GET `/doc-templates?direction=IN` returns only IN templates; `direction=OUT` returns only OUT. |
| 3 | `test_list_doc_templates_filter_enabled` | GET `/doc-templates?enabled=true` filters correctly. |
| 4 | `test_list_doc_templates_search_q` | GET `/doc-templates?q=OA` returns templates with "OA" in code or name. |
| 5 | `test_create_doc_template` | POST `/doc-templates` creates a template with all SPEC fields; response has 201 and correct data. |
| 6 | `test_create_doc_template_minimal` | POST with only `code` + `name`; defaults applied (`direction=IN`, `enabled=True`, `need_reply=False`). |
| 7 | `test_create_doc_template_duplicate_code_rejected` | POST with existing code returns 409 with `DOC_TEMPLATE_CODE_EXISTS`. |
| 8 | `test_get_doc_template_by_id` | GET `/doc-templates/{id}` returns 200 with correct fields. |
| 9 | `test_get_doc_template_not_found` | GET `/doc-templates/{nonexistent_id}` returns 404. |
| 10 | `test_update_doc_template` | PUT `/doc-templates/{id}` updates specified fields, leaves others unchanged. |
| 11 | `test_update_doc_template_not_found` | PUT to nonexistent ID returns 404. |
| 12 | `test_update_doc_template_partial` | PUT with only `enabled=false` disables template; other fields remain. |
| 13 | `test_list_doc_templates_pagination` | Create >20 templates, verify `page`, `page_size`, `total` in response. |
| 14 | `test_doc_template_unauthorized` | Request without auth token returns 401. |

### Test Skeleton

```python
"""Tests for Batch B1: DocTemplate CRUD API."""
from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient


def test_list_doc_templates_returns_seeded(client: TestClient, auth_headers: dict) -> None:
    resp = client.get("/api/v1/doc-templates", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    codes = {t["code"] for t in data["items"]}
    assert "OA_IN" in codes
    assert "CLIENT_IN" in codes

    oa_in = next(t for t in data["items"] if t["code"] == "OA_IN")
    assert oa_in["need_reply"] is True
    assert oa_in["status_effect"] == "OA1"
    assert oa_in["deadline_template_code"] == "OA_REPLY"


def test_create_doc_template(client: TestClient, auth_headers: dict) -> None:
    code = f"B1-{uuid4().hex[:6]}"
    resp = client.post(
        "/api/v1/doc-templates",
        headers=auth_headers,
        json={
            "code": code,
            "name": "Test Template",
            "direction": "IN",
            "status_effect": "OA1",
            "need_reply": True,
            "deadline_template_code": "OA_REPLY",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["code"] == code
    assert body["status_effect"] == "OA1"
    assert body["need_reply"] is True


def test_create_doc_template_duplicate_code_rejected(
    client: TestClient, auth_headers: dict
) -> None:
    code = f"DUP-{uuid4().hex[:6]}"
    r1 = client.post(
        "/api/v1/doc-templates",
        headers=auth_headers,
        json={"code": code, "name": "First"},
    )
    assert r1.status_code == 201
    r2 = client.post(
        "/api/v1/doc-templates",
        headers=auth_headers,
        json={"code": code, "name": "Duplicate"},
    )
    assert r2.status_code == 409


# ... (remaining tests follow same pattern)
```

---

## 12. Risks / Edge Cases

### SQLite Compatibility
- **Boolean storage**: SQLite stores booleans as 0/1 integers. `server_default=text("0")` is correct for `need_reply`. The ORM `Boolean` type handles Python-to-SQLite conversion.
- **JSON in Text**: `fee_item_list` and `input_fields` store JSON as plain text. No `JSON` column type is used, ensuring SQLite compatibility. Application code that later reads these fields must use `json.loads()`.
- **ALTER TABLE limitations**: SQLite does not support adding columns with non-constant defaults. All new columns use either `nullable=True` with no default, or `server_default=text(...)` with a constant value. This is safe.

### Backward Compatibility
- **Existing DocTemplate rows**: If any `t_doc_template` rows were manually inserted before this migration, they will have `NULL` for all new columns. This is acceptable since all new fields are nullable.
- **Existing Document creation flow**: The `create_document` function in `service.py` only checks that the referenced `doc_template_id` exists via FK. It does not read any of the new SPEC fields. B2/B3 will add cascade logic. No changes needed for B1.
- **API route ordering**: The `/doc-templates` endpoints must be registered BEFORE `/documents/{document_id}` to avoid FastAPI treating `doc-templates` as a `document_id` path parameter. Since both use the same `router` instance, endpoints added at the top of the file (or before the `/{document_id}` routes) will be matched correctly. **This is critical** -- place the new `@router.get("/doc-templates", ...)` before `@router.get("/documents/{document_id}", ...)`.

### Migration Chain
- `down_revision = "a3_case_fields_01"` -- this is the latest migration. If other branches add migrations concurrently, a merge migration may be needed. For now, this is a single-branch linear chain.

### Permission Seeding
- The `seed_default_roles_perms()` function is idempotent (checks existing perm codes before inserting). Adding new entries to `ROLE_PERMISSIONS` will cause them to be inserted on next seed run.
- Existing DB deployments that re-run `seed_dev.py` will get the new permissions automatically.

### Route Path Conflict Prevention
- `/doc-templates` vs `/documents`: These paths do NOT conflict because they have different prefixes. FastAPI matches routes in registration order, and `/doc-templates` is a distinct literal path from `/documents`.
- `/doc-templates/{template_id}` vs `/documents/{document_id}`: No conflict -- different path prefixes.

### Data Validation
- `fee_item_list` JSON validation: Not enforced at schema level in B1. Consumers in B2/B3 should validate JSON structure. Storing as `str | None` is intentional to keep B1 scope minimal.
- `status_effect` / `status_restore` values should correspond to valid `Case.status` enum values, but this cross-validation is deferred to B2 (cascade execution logic).

---

## 13. Files Changed Summary

| File | Action | Description |
|------|--------|-------------|
| `backend/alembic/versions/b1_doc_template_spec_fields.py` | **CREATE** | Alembic migration adding 8 columns |
| `backend/app/modules/documents/models.py` | **EDIT** | Add 8 mapped columns to `DocTemplate` |
| `backend/app/modules/documents/schemas.py` | **EDIT** | Add `DocTemplateCreateIn`, `DocTemplateUpdateIn`, `DocTemplateOut`, `DocTemplateListOut` |
| `backend/app/modules/documents/service.py` | **EDIT** | Add `list_doc_templates`, `get_doc_template`, `create_doc_template`, `update_doc_template` |
| `backend/app/modules/documents/api.py` | **EDIT** | Add 4 endpoints: GET/POST `/doc-templates`, GET/PUT `/doc-templates/{id}` |
| `backend/app/modules/rbac/service.py` | **EDIT** | Add `DocTemplate.Read`, `DocTemplate.Create`, `DocTemplate.Edit` to Admin + Formalities roles |
| `backend/scripts/seed_dev.py` | **EDIT** | Add `seed_doc_templates()` with 5 template entries |
| `backend/tests/conftest.py` | **EDIT** | Add `_seed_doc_templates()` helper for test DB |
| `backend/tests/test_doc_template.py` | **CREATE** | New test file with ~14 test cases |

**No router.py changes needed** -- `documents_router` is already included.

---

## 14. Acceptance Criteria Checklist

- [ ] Migration runs cleanly on fresh DB: `rm -f fpms_dev.db && alembic upgrade head`
- [ ] `seed_dev.py` seeds 5 doc templates without errors
- [ ] `GET /api/v1/doc-templates` returns seeded templates with all SPEC fields
- [ ] `POST /api/v1/doc-templates` creates template with all fields; returns 201
- [ ] `POST /api/v1/doc-templates` with duplicate code returns 409
- [ ] `GET /api/v1/doc-templates/{id}` returns single template; 404 for missing
- [ ] `PUT /api/v1/doc-templates/{id}` updates partial fields; returns 200
- [ ] `PUT /api/v1/doc-templates/{id}` for missing ID returns 404
- [ ] Direction/enabled/q filters work on list endpoint
- [ ] Pagination works (page, page_size, total)
- [ ] Unauthenticated requests return 401
- [ ] Admin role has all 3 DocTemplate permissions
- [ ] Formalities role has DocTemplate.Read
- [ ] All existing tests still pass (`pytest --tb=short`)
- [ ] `ruff check --fix . && ruff format .` passes with no errors
- [ ] Existing Document CRUD endpoints continue to work unchanged
