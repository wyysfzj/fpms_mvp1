# B3 — Document→FeeDraft Linking — Architect Plan

## 1. Current State Analysis

### 1.1 DocTemplate Model (`backend/app/modules/documents/models.py:30-48`)
The `DocTemplate` model already has the two key fields:
- `fee_draft_type: Mapped[str | None] = mapped_column(String(32), nullable=True)` — line 42
- `fee_item_list: Mapped[str | None] = mapped_column(Text, nullable=True)` — line 43

These were added as part of Batch B1. No schema migration needed.

### 1.2 Document Model (`backend/app/modules/documents/models.py:51-84`)
- `case_id: Mapped[str]` — FK to `t_case.id` (line 54-56)
- `doc_template_id: Mapped[str | None]` — FK to `t_doc_template.id` (line 57-59)
- Has `case` relationship back to Case (line 75)

### 1.3 Case Model (`backend/app/modules/cases/models.py:21-68`)
- `client_id: Mapped[str | None]` — FK to `t_client.id` (line 34-36)
- **No `currency` field** — Case model has no currency. Default to "CNY".

### 1.4 FeeDraft Model (`backend/app/modules/fees/models.py:12-37`)
Key fields for auto-creation:
- `id`: String(36) UUID — generated in app code
- `case_id`: String(36) FK, required
- `client_id`: String(36) FK, nullable
- `draft_type`: String(32), defaults to "GENERIC"
- `currency`: String(8), defaults to "CNY"
- `status`: String(16), defaults to "OPEN"
- `total_gov`, `total_service`, `total_misc`, `amount`: Numeric(18,2), defaults to 0

### 1.5 FeeItem Model (`backend/app/modules/fees/models.py:40-61`)
Key fields for auto-creation from fee_item_list JSON:
- `id`: String(36) UUID
- `draft_id`: FK to fee_draft, required
- `case_id`: FK to case, optional
- `rate_id`: FK to fee_rate, optional (NULL for auto-created items — no rate lookup)
- `fee_code`: String(64), optional
- `fee_name`: String(256), optional
- `fee_type`: String(16), defaults to "SERVICE"
- `year_no`, `quantity`, `unit_price`, `amount`: numeric fields

### 1.6 Document Creation Flow (current)
**service.py `create_document()`** (lines 79-156):
1. Validate case exists
2. Load template (if doc_template_id provided)
3. Create Document ORM object
4. B2 cascades: need_reply propagation, status_effect on case
5. B2 reply chain: auto write-off tasks
6. `db.commit()` + `db.refresh(document)` → return document

**api.py `create_document` endpoint** (lines 185-247):
1. Call `create_document_service(db, payload)` → document committed
2. Call `TaskGenerationService().generate_from_document(db, document)` → tasks added
3. `db.commit()` → tasks committed
4. Set `X-Auto-Tasks-Created` header
5. Return `DocumentOut`

### 1.7 Existing Fee Service Pattern (`fees/service.py:61-86`)
The `create_fee_draft()` function shows the pattern for creating a FeeDraft:
- Validates case and client exist
- Creates `FeeDraft(id=uuid4(), case_id=..., client_id=..., draft_type=..., currency=..., status=OPEN, totals=0)`
- Commits and returns

### 1.8 Test Infrastructure (`tests/conftest.py`)
- Session-scoped SQLite test DB with Alembic migrations
- `seed_data` fixture seeds admin user, task templates, and doc templates
- **GRANT_NOTICE** template seeded with `fee_draft_type="GRANT_FEE"` (line 147-149) — perfect for testing
- **CLIENT_IN** template seeded with no fee_draft_type — perfect for negative testing
- Test patterns: function-scoped `client` fixture, `auth_headers` fixture, helpers for creating cases/docs

---

## 2. Task Decomposition

### Task B3-1: Create `fee_linking_service.py`
**Agent**: Backend
**File**: `backend/app/modules/documents/fee_linking_service.py` (NEW)
**Scope**: Single function `maybe_create_fee_draft()`

```python
"""B3: Auto-create FeeDraft when document registered with fee-enabled template."""
from __future__ import annotations

import json
import logging
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.orm import Session

from app.modules.cases.models import Case
from app.modules.documents.models import DocTemplate, Document
from app.modules.fees.models import FeeDraft, FeeItem

logger = logging.getLogger(__name__)


def maybe_create_fee_draft(
    db: Session,
    document: Document,
    template: DocTemplate,
) -> FeeDraft | None:
    """Auto-create a FeeDraft if template has fee_draft_type configured.

    Returns created FeeDraft, or None if no draft was needed.
    Does NOT commit — caller is responsible for db.commit().
    """
    fee_draft_type = getattr(template, "fee_draft_type", None)
    if not fee_draft_type:
        return None

    # Load case to get client_id
    case = db.get(Case, document.case_id)
    if not case:
        logger.warning(
            "B3: Case %s not found for document %s, skipping fee draft",
            document.case_id,
            document.id,
        )
        return None

    draft = FeeDraft(
        id=str(uuid4()),
        case_id=document.case_id,
        client_id=case.client_id,
        draft_type=fee_draft_type,
        currency="CNY",
        status="OPEN",
        total_gov=Decimal("0"),
        total_service=Decimal("0"),
        total_misc=Decimal("0"),
        amount=Decimal("0"),
    )
    db.add(draft)

    # Parse fee_item_list if present
    fee_item_list_raw = getattr(template, "fee_item_list", None)
    if fee_item_list_raw:
        _parse_and_create_fee_items(db, draft, document, fee_item_list_raw, template.code)

    return draft


def _parse_and_create_fee_items(
    db: Session,
    draft: FeeDraft,
    document: Document,
    raw_json: str,
    template_code: str,
) -> None:
    """Parse fee_item_list JSON and create FeeItem rows. Logs warning on malformed data."""
    try:
        items = json.loads(raw_json)
    except (json.JSONDecodeError, TypeError) as exc:
        logger.warning("B3: Malformed fee_item_list JSON in template %s: %s", template_code, exc)
        return

    if not isinstance(items, list):
        logger.warning("B3: fee_item_list in template %s is not a list", template_code)
        return

    for item_data in items:
        if not isinstance(item_data, dict):
            continue
        fee_item = FeeItem(
            id=str(uuid4()),
            draft_id=draft.id,
            case_id=document.case_id,
            fee_code=item_data.get("code") or item_data.get("fee_code"),
            fee_name=item_data.get("name") or item_data.get("fee_name"),
            fee_type=item_data.get("fee_type", "SERVICE"),
            quantity=Decimal(str(item_data["quantity"])) if item_data.get("quantity") is not None else None,
            unit_price=Decimal(str(item_data["unit_price"])) if item_data.get("unit_price") is not None else None,
            amount=Decimal(str(item_data.get("amount", 0))),
        )
        db.add(fee_item)
```

### Task B3-2: Wire into `create_document` API endpoint
**Agent**: Backend
**File**: `backend/app/modules/documents/api.py` — modify `create_document` function
**Scope**: ~15 lines added

Changes to `create_document` endpoint (lines 185-247):

1. Add imports at top of file:
```python
from sqlalchemy import select
from app.modules.documents.models import DocTemplate
from app.modules.documents.fee_linking_service import maybe_create_fee_draft
```

2. Insert between service call (line 223) and task generation (line 224-228):
```python
    document = create_document_service(db, payload)

    # B3: Auto-create fee draft if template has fee_draft_type
    auto_fee_draft_id = None
    if document.doc_template_id:
        template = db.execute(
            select(DocTemplate).where(DocTemplate.id == document.doc_template_id)
        ).scalar_one_or_none()
        if template:
            draft = maybe_create_fee_draft(db, document, template)
            if draft:
                auto_fee_draft_id = draft.id

    try:
        created_tasks = TaskGenerationService().generate_from_document(db, document)
    ...
```

3. Add header after existing task header (line 232):
```python
    response.headers["X-Auto-Tasks-Created"] = str(len(created_tasks))
    if auto_fee_draft_id:
        response.headers["X-Auto-Fee-Draft-Created"] = auto_fee_draft_id
```

### Task B3-3: Write tests
**Agent**: Test
**File**: `backend/tests/test_b3_fee_linking.py` (NEW)

Tests using patterns from `test_b2_reply_chain.py`:

| # | Test Name | Validates |
|---|-----------|-----------|
| 1 | `test_grant_notice_creates_fee_draft` | GRANT_NOTICE doc → X-Auto-Fee-Draft-Created header present, FeeDraft in DB |
| 2 | `test_fee_draft_fields_correct` | draft_type="GRANT_FEE", currency="CNY", status="OPEN", all totals=0 |
| 3 | `test_fee_draft_client_id_from_case` | Case with client → fee draft inherits client_id |
| 4 | `test_no_fee_draft_without_template` | Doc without template → no header |
| 5 | `test_no_fee_draft_for_client_in_template` | CLIENT_IN template (no fee_draft_type) → no header |
| 6 | `test_fee_item_list_creates_items` | Custom template with fee_item_list JSON → FeeItems created |
| 7 | `test_malformed_fee_item_list_no_crash` | Template with invalid JSON → draft created, no items, no crash |

Test helpers needed:
- `_create_case()` — from test_b2 pattern
- `_get_doc_template_by_code()` — from test_b2 pattern
- `_create_document()` — returns full response for header inspection
- Fee draft queries via `/api/v1/fee-drafts?case_id=X`

---

## 3. API Contract

### POST /api/v1/documents (modified behavior)

**Existing behavior**: Returns 201 with DocumentOut, sets `X-Auto-Tasks-Created` header.

**New behavior (additive)**:
- If the document's template has `fee_draft_type` set, a FeeDraft is auto-created
- Response header `X-Auto-Fee-Draft-Created: {draft_id}` is added when a draft was created
- If `fee_draft_type` is null/empty, no draft is created, no header

**Error behavior**: fee_item_list parsing failures are logged but do not affect the response. The draft is still created even if fee items fail to parse.

---

## 4. Dependency Graph

```
B3-1 (fee_linking_service.py) ←── must complete first
    ├── B3-2 (wire into api.py) ←── depends on B3-1
    │       └── B3-3 (tests) ←── depends on B3-1 + B3-2
```

Backend Agent: B3-1 → B3-2 (sequential)
Test Agent: B3-3 (after Backend Agent completes B3-1 + B3-2)

---

## 5. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Template re-query in API layer | Low | Negligible | SQLAlchemy identity map may cache; PK lookup is fast |
| fee_item_list JSON format mismatch | Medium | Low | Flexible key parsing (code/fee_code, name/fee_name), log warning on error |
| FeeItem creation without rate_id | Low | Low | FeeItem.rate_id is nullable — safe |
| Double commit pattern | Low | Low | Follows existing TaskGeneration pattern exactly |
| No currency on Case | None | None | Default to "CNY" per spec |

---

## 6. Constraints Adherence
- ✅ Import FeeDraft, FeeItem from app.modules.fees.models
- ✅ fee_item_list parsed with json.loads()
- ✅ Malformed fee_item_list → log warning, skip — no crash
- ✅ Do NOT modify fee module models or schemas
- ✅ No fee calculation engine, no rate lookup — just creates draft structure
- ✅ SQLite compatible (no PG-only features)
- ✅ UUIDs generated in app code with uuid4()
