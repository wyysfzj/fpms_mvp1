# FR-FE-07 Case Receipt CRUD — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add manual CRUD endpoints and cross-case list for CaseReceipt (个案收款登记), with frontend list page and create/edit dialog.

**Architecture:** Extend existing billing module — add migration for 4 new columns, add Create/Update schemas + 3 new endpoints in billing/api.py, add service functions, add frontend list page + dialog component. TDD: tests written first for each backend task.

**Tech Stack:** FastAPI, SQLAlchemy 2.x, Pydantic 2.x, Alembic (SQLite compat), Vue 3 + Element Plus + TypeScript

**Spec:** `docs/superpowers/specs/2026-03-24-case-receipt-crud-design.md`

---

## File Structure

| File | Action | Responsibility |
|------|--------|---------------|
| `backend/alembic/versions/pe_fr_fe_07_case_receipt_ext.py` | CREATE | Migration: add fee_name, due_date, is_prepayment, remark to t_case_receipt |
| `backend/app/modules/billing/models.py` | EDIT | Add 4 mapped_column fields to CaseReceipt |
| `backend/app/modules/billing/schemas.py` | EDIT | Add CaseReceiptCreate, CaseReceiptUpdate, CaseReceiptListItem; update CaseReceiptResponse |
| `backend/app/modules/billing/service.py` | EDIT | Add create_case_receipt, update_case_receipt, list_case_receipts |
| `backend/app/modules/billing/api.py` | EDIT | Add POST /case-receipts, PUT /case-receipts/{id}, GET /case-receipts |
| `backend/app/modules/rbac/service.py` | EDIT | Add CaseReceipt.Create, CaseReceipt.Update to Admin role |
| `backend/tests/test_case_receipt_crud.py` | CREATE | 18 test functions |
| `frontend/src/api/billing.ts` | EDIT | Add createCaseReceipt, updateCaseReceipt, listCaseReceipts |
| `frontend/src/api/billing.types.ts` | EDIT | Add CaseReceiptCreate, CaseReceiptUpdate, CaseReceiptListItem, CaseReceiptListResponse |
| `frontend/src/modules/billing/pages/CaseReceiptList.vue` | CREATE | Cross-case list page with filters |
| `frontend/src/modules/billing/components/CaseReceiptDialog.vue` | CREATE | Create/edit dialog |
| `frontend/src/modules/cases/components/CaseReceiptsSummary.vue` | EDIT | Add "新增收款记录" button |
| `frontend/src/router/index.ts` | EDIT | Add /billing/case-receipts route |
| `frontend/src/constants/menu.ts` | EDIT | Add 个案收款登记 menu item |

---

## Task 1: Migration + Model (backend schema)

**Files:**
- Create: `backend/alembic/versions/pe_fr_fe_07_case_receipt_ext.py`
- Modify: `backend/app/modules/billing/models.py:74-98`

- [ ] **Step 1: Write migration file**

Create `backend/alembic/versions/pe_fr_fe_07_case_receipt_ext.py`:

```python
"""pe_fr_fe_07_case_receipt_ext

Revision ID: pe_fr_fe_07_01
Revises: pe_be_db_cm_02_case_ext_01
Create Date: 2026-03-24

Add 4 columns to t_case_receipt: fee_name, due_date, is_prepayment, remark.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "pe_fr_fe_07_01"
down_revision = "pe_be_db_cm_02_case_ext_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    if not insp.has_table("t_case_receipt"):
        return

    existing = {col["name"] for col in insp.get_columns("t_case_receipt")}

    columns = [
        ("fee_name", sa.String(128), None),
        ("due_date", sa.Date(), None),
        ("is_prepayment", sa.Boolean(), sa.text("0")),
        ("remark", sa.String(512), None),
    ]

    with op.batch_alter_table("t_case_receipt") as batch_op:
        for col_name, col_type, server_default in columns:
            if col_name not in existing:
                batch_op.add_column(
                    sa.Column(col_name, col_type, nullable=True, server_default=server_default)
                )


def downgrade() -> None:
    pass
```

- [ ] **Step 2: Update CaseReceipt model**

In `backend/app/modules/billing/models.py`, add after line 97 (`is_commissionable` field), before the blank line:

```python
    fee_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_prepayment: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, server_default=text("0")
    )
    remark: Mapped[str | None] = mapped_column(String(512), nullable=True)
```

- [ ] **Step 3: Test clean rebuild**

```bash
cd backend && source .venv/bin/activate
rm -f fpms_dev.db && alembic upgrade head && python scripts/seed_dev.py
```

Expected: All migrations succeed, seed completes with "✅ Development database seeded successfully!"

- [ ] **Step 4: Verify schema**

```bash
sqlite3 fpms_dev.db ".schema t_case_receipt"
```

Expected: Output includes `fee_name`, `due_date`, `is_prepayment`, `remark` columns.

- [ ] **Step 5: Commit**

```bash
git add backend/alembic/versions/pe_fr_fe_07_case_receipt_ext.py backend/app/modules/billing/models.py
git commit -m "feat(db): add case receipt extension columns (FR-FE-07)"
```

---

## Task 2: Permission seeding

**Files:**
- Modify: `backend/app/modules/rbac/service.py:29`

- [ ] **Step 1: Add permissions to ROLE_PERMISSIONS**

In `backend/app/modules/rbac/service.py`, in the `"Admin"` list, after line 29 (`"CaseReceipt.Read",`), add:

```python
        "CaseReceipt.Create",
        "CaseReceipt.Update",
```

- [ ] **Step 2: Test seed**

```bash
cd backend && source .venv/bin/activate
rm -f fpms_dev.db && alembic upgrade head && python scripts/seed_dev.py
```

Expected: Success.

- [ ] **Step 3: Commit**

```bash
git add backend/app/modules/rbac/service.py
git commit -m "feat(rbac): add CaseReceipt.Create/Update permissions (FR-FE-07)"
```

---

## Task 3: Schemas (CaseReceiptCreate, CaseReceiptUpdate, updated Response, ListItem)

**Files:**
- Modify: `backend/app/modules/billing/schemas.py:143-170`

- [ ] **Step 1: Update CaseReceiptResponse**

In `backend/app/modules/billing/schemas.py`, replace the existing `CaseReceiptResponse` class (lines 143-158) with:

```python
class CaseReceiptResponse(BaseModel):
    """Response schema for case receipts."""

    id: str
    case_id: str
    fee_type: str | None = None
    currency: str
    receivable_amt: Decimal
    received_amt: Decimal
    last_receipt_date: date | None = None
    fee_code: str | None = None
    fee_name: str | None = None
    year_no: int | None = None
    due_date: date | None = None
    is_arrears: bool | None = None
    is_prepayment: bool | None = None
    is_commissionable: bool | None = None
    invoice_no: str | None = None
    remark: str | None = None
    bills: list["CaseReceiptBillResponse"] = []
```

- [ ] **Step 2: Add CaseReceiptCreate schema**

Add after `CaseReceiptBillResponse` class (after line 170):

```python
class CaseReceiptCreate(BaseModel):
    """Schema for creating a case receipt manually."""

    case_id: str = Field(..., min_length=1)
    fee_type: str | None = Field(None, max_length=16)
    fee_code: str | None = Field(None, max_length=64)
    fee_name: str | None = Field(None, max_length=128)
    year_no: int | None = None
    currency: str = Field("CNY", max_length=8)
    receivable_amt: Decimal = Field(..., ge=0)
    received_amt: Decimal = Field(..., ge=0)
    last_receipt_date: date | None = None
    due_date: date | None = None
    is_arrears: bool | None = None
    is_prepayment: bool | None = None
    is_commissionable: bool | None = None
    invoice_no: str | None = Field(None, max_length=64)
    remark: str | None = Field(None, max_length=512)


class CaseReceiptUpdate(BaseModel):
    """Schema for updating a case receipt (partial)."""

    fee_type: str | None = Field(None, max_length=16)
    fee_code: str | None = Field(None, max_length=64)
    fee_name: str | None = Field(None, max_length=128)
    year_no: int | None = None
    currency: str | None = Field(None, max_length=8)
    receivable_amt: Decimal | None = Field(None, ge=0)
    received_amt: Decimal | None = Field(None, ge=0)
    last_receipt_date: date | None = None
    due_date: date | None = None
    is_arrears: bool | None = None
    is_prepayment: bool | None = None
    is_commissionable: bool | None = None
    invoice_no: str | None = Field(None, max_length=64)
    remark: str | None = Field(None, max_length=512)


class CaseReceiptListItem(BaseModel):
    """List item for cross-case receipt query."""

    id: str
    case_id: str
    case_no: str | None = None
    client_name: str | None = None
    fee_type: str | None = None
    currency: str
    receivable_amt: Decimal
    received_amt: Decimal
    last_receipt_date: date | None = None
    fee_code: str | None = None
    fee_name: str | None = None
    year_no: int | None = None
    due_date: date | None = None
    is_arrears: bool | None = None
    is_prepayment: bool | None = None
    is_commissionable: bool | None = None
    invoice_no: str | None = None
    remark: str | None = None
```

- [ ] **Step 3: Verify lint passes**

```bash
cd backend && source .venv/bin/activate && ruff check app/modules/billing/schemas.py && ruff format app/modules/billing/schemas.py
```

Expected: No errors.

- [ ] **Step 4: Commit**

```bash
git add backend/app/modules/billing/schemas.py
git commit -m "feat(billing): add CaseReceipt CRUD schemas (FR-FE-07)"
```

---

## Task 4: Service functions

**Files:**
- Modify: `backend/app/modules/billing/service.py`

- [ ] **Step 1: Write test file first (TDD RED)**

Create `backend/tests/test_case_receipt_crud.py`:

```python
"""Tests for CaseReceipt manual CRUD (FR-FE-07)."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def case_id(client: TestClient, auth_headers: dict) -> str:
    """Create a test case and return its ID."""
    resp = client.post(
        "/api/v1/cases",
        json={
            "case_no": f"CR-TEST-{uuid4().hex[:8]}",
            "case_type": "NORMAL",
            "patent_category": "INVENTION",
            "flow_dir": "IN",
            "title": "Test Case for Receipt",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    return resp.json()["id"]


# --- CREATE ---

def test_create_case_receipt_success(client: TestClient, auth_headers: dict, case_id: str):
    resp = client.post(
        "/api/v1/case-receipts",
        json={
            "case_id": case_id,
            "fee_type": "SERVICE",
            "fee_code": "SVC-001",
            "fee_name": "服务费",
            "currency": "CNY",
            "receivable_amt": "1000.00",
            "received_amt": "1000.00",
            "last_receipt_date": "2026-03-01",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["case_id"] == case_id
    assert data["fee_type"] == "SERVICE"
    assert data["fee_name"] == "服务费"
    assert Decimal(str(data["receivable_amt"])) == Decimal("1000.00")


def test_create_case_receipt_invalid_case(client: TestClient, auth_headers: dict):
    resp = client.post(
        "/api/v1/case-receipts",
        json={
            "case_id": "nonexistent-id",
            "receivable_amt": "100.00",
            "received_amt": "100.00",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 404


def test_create_case_receipt_negative_amt(client: TestClient, auth_headers: dict, case_id: str):
    resp = client.post(
        "/api/v1/case-receipts",
        json={
            "case_id": case_id,
            "receivable_amt": "-10.00",
            "received_amt": "100.00",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 422


def test_create_auto_arrears(client: TestClient, auth_headers: dict, case_id: str):
    resp = client.post(
        "/api/v1/case-receipts",
        json={
            "case_id": case_id,
            "receivable_amt": "1000.00",
            "received_amt": "500.00",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["is_arrears"] is True


def test_create_auto_prepayment(client: TestClient, auth_headers: dict, case_id: str):
    resp = client.post(
        "/api/v1/case-receipts",
        json={
            "case_id": case_id,
            "receivable_amt": "500.00",
            "received_amt": "1000.00",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["is_prepayment"] is True


def test_create_user_override_arrears(client: TestClient, auth_headers: dict, case_id: str):
    resp = client.post(
        "/api/v1/case-receipts",
        json={
            "case_id": case_id,
            "receivable_amt": "1000.00",
            "received_amt": "500.00",
            "is_arrears": False,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["is_arrears"] is False


def test_create_user_override_prepayment(client: TestClient, auth_headers: dict, case_id: str):
    resp = client.post(
        "/api/v1/case-receipts",
        json={
            "case_id": case_id,
            "receivable_amt": "500.00",
            "received_amt": "1000.00",
            "is_prepayment": False,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["is_prepayment"] is False


# --- UPDATE ---

def test_update_case_receipt_success(client: TestClient, auth_headers: dict, case_id: str):
    create_resp = client.post(
        "/api/v1/case-receipts",
        json={"case_id": case_id, "receivable_amt": "100.00", "received_amt": "100.00"},
        headers=auth_headers,
    )
    receipt_id = create_resp.json()["id"]

    resp = client.put(
        f"/api/v1/case-receipts/{receipt_id}",
        json={"remark": "已核实", "invoice_no": "INV-001"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["remark"] == "已核实"
    assert resp.json()["invoice_no"] == "INV-001"


def test_update_recompute_flags(client: TestClient, auth_headers: dict, case_id: str):
    create_resp = client.post(
        "/api/v1/case-receipts",
        json={"case_id": case_id, "receivable_amt": "100.00", "received_amt": "100.00"},
        headers=auth_headers,
    )
    receipt_id = create_resp.json()["id"]

    resp = client.put(
        f"/api/v1/case-receipts/{receipt_id}",
        json={"received_amt": "50.00"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["is_arrears"] is True


def test_update_not_found(client: TestClient, auth_headers: dict):
    resp = client.put(
        "/api/v1/case-receipts/nonexistent-id",
        json={"remark": "test"},
        headers=auth_headers,
    )
    assert resp.status_code == 404


# --- LIST ---

def test_list_case_receipts_no_filter(client: TestClient, auth_headers: dict, case_id: str):
    client.post(
        "/api/v1/case-receipts",
        json={"case_id": case_id, "receivable_amt": "100.00", "received_amt": "100.00"},
        headers=auth_headers,
    )
    resp = client.get("/api/v1/case-receipts", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert data["total"] >= 1


def test_list_filter_by_client(client: TestClient, auth_headers: dict):
    resp = client.get(
        "/api/v1/case-receipts",
        params={"client_id": "nonexistent"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


def test_list_filter_by_arrears(client: TestClient, auth_headers: dict, case_id: str):
    client.post(
        "/api/v1/case-receipts",
        json={
            "case_id": case_id,
            "receivable_amt": "1000.00",
            "received_amt": "500.00",
        },
        headers=auth_headers,
    )
    resp = client.get(
        "/api/v1/case-receipts",
        params={"is_arrears": "true"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    for item in resp.json()["items"]:
        assert item["is_arrears"] is True


def test_list_filter_by_date_range(client: TestClient, auth_headers: dict, case_id: str):
    client.post(
        "/api/v1/case-receipts",
        json={
            "case_id": case_id,
            "receivable_amt": "100.00",
            "received_amt": "100.00",
            "last_receipt_date": "2026-03-15",
        },
        headers=auth_headers,
    )
    resp = client.get(
        "/api/v1/case-receipts",
        params={"date_from": "2026-03-01", "date_to": "2026-03-31"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


def test_list_pagination(client: TestClient, auth_headers: dict):
    resp = client.get(
        "/api/v1/case-receipts",
        params={"page": 1, "page_size": 2},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["page"] == 1
    assert resp.json()["page_size"] == 2
    assert len(resp.json()["items"]) <= 2


# --- PERMISSIONS ---

def test_permissions_create(client: TestClient):
    resp = client.post("/api/v1/case-receipts", json={"case_id": "x", "receivable_amt": "1", "received_amt": "1"})
    assert resp.status_code == 401


def test_permissions_update(client: TestClient):
    resp = client.put("/api/v1/case-receipts/some-id", json={"remark": "x"})
    assert resp.status_code == 401


# --- INTEGRATION ---

def test_manual_receipt_no_conflict_with_auto(client: TestClient, auth_headers: dict, case_id: str):
    """Manual receipt creation does not affect existing auto-allocated receipts."""
    resp = client.post(
        "/api/v1/case-receipts",
        json={
            "case_id": case_id,
            "fee_type": "MISC",
            "receivable_amt": "200.00",
            "received_amt": "200.00",
            "remark": "手工录入",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201

    # Existing per-case endpoint still works
    get_resp = client.get(f"/api/v1/cases/{case_id}/receipts", headers=auth_headers)
    # May be 200 or 404 depending on whether auto-allocated receipt exists
    assert get_resp.status_code in (200, 404)
```

- [ ] **Step 2: Run tests — verify RED**

```bash
cd backend && source .venv/bin/activate && pytest tests/test_case_receipt_crud.py -v 2>&1 | tail -30
```

Expected: All 18 tests FAIL (endpoints don't exist yet).

- [ ] **Step 3: Write service functions**

Add to end of `backend/app/modules/billing/service.py`:

```python
from app.modules.billing.schemas import CaseReceiptCreate, CaseReceiptUpdate


def create_case_receipt(db: Session, payload: CaseReceiptCreate) -> CaseReceipt:
    """Create a manual case receipt."""
    from app.modules.cases.models import T_Case

    case = db.query(T_Case).filter(T_Case.id == payload.case_id).first()
    if not case:
        raise_business_error("CASE_NOT_FOUND", "案卷不存在", status_code=404)

    data = payload.model_dump()

    # V-CR-03: auto-set is_arrears if not explicitly provided
    if data.get("is_arrears") is None and data["received_amt"] < data["receivable_amt"]:
        data["is_arrears"] = True

    # V-CR-02: auto-set is_prepayment if not explicitly provided
    if data.get("is_prepayment") is None and data["received_amt"] > data["receivable_amt"]:
        data["is_prepayment"] = True

    receipt = CaseReceipt(**data)
    db.add(receipt)
    db.flush()
    return receipt


def update_case_receipt(db: Session, receipt_id: str, payload: CaseReceiptUpdate) -> CaseReceipt:
    """Update a case receipt (partial)."""
    receipt = db.query(CaseReceipt).filter(CaseReceipt.id == receipt_id).first()
    if not receipt:
        raise_business_error(
            "CASE_RECEIPT_NOT_FOUND", "收款记录不存在", status_code=404
        )

    changes = payload.model_dump(exclude_unset=True)
    for key, value in changes.items():
        setattr(receipt, key, value)

    # Recompute flags if amounts changed but flags not explicitly provided
    new_receivable = changes.get("receivable_amt", receipt.receivable_amt)
    new_received = changes.get("received_amt", receipt.received_amt)

    if ("receivable_amt" in changes or "received_amt" in changes):
        if "is_arrears" not in changes and new_received < new_receivable:
            receipt.is_arrears = True
        if "is_prepayment" not in changes and new_received > new_receivable:
            receipt.is_prepayment = True

    db.flush()
    return receipt


def list_case_receipts(
    db: Session,
    *,
    client_id: str | None = None,
    case_no: str | None = None,
    fee_type: str | None = None,
    is_arrears: bool | None = None,
    is_commissionable: bool | None = None,
    currency: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """List case receipts with cross-case filters."""
    from sqlalchemy import case as sa_case, func
    from app.modules.cases.models import T_Case
    from app.modules.masterdata.models import T_Client

    query = (
        db.query(
            CaseReceipt,
            T_Case.case_no.label("case_no"),
            T_Client.name.label("client_name"),
        )
        .join(T_Case, T_Case.id == CaseReceipt.case_id)
        .outerjoin(T_Client, T_Client.id == T_Case.client_id)
    )

    if client_id:
        query = query.filter(T_Case.client_id == client_id)
    if case_no:
        query = query.filter(T_Case.case_no.contains(case_no))
    if fee_type:
        query = query.filter(CaseReceipt.fee_type == fee_type)
    if is_arrears is not None:
        query = query.filter(CaseReceipt.is_arrears == is_arrears)
    if is_commissionable is not None:
        query = query.filter(CaseReceipt.is_commissionable == is_commissionable)
    if currency:
        query = query.filter(CaseReceipt.currency == currency)
    if date_from:
        query = query.filter(CaseReceipt.last_receipt_date >= date_from)
    if date_to:
        query = query.filter(CaseReceipt.last_receipt_date <= date_to)

    total = query.count()

    null_last = sa_case(
        (CaseReceipt.last_receipt_date.is_(None), 1), else_=0
    )
    rows = (
        query.order_by(null_last, CaseReceipt.last_receipt_date.desc(), CaseReceipt.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = []
    for receipt, c_no, c_name in rows:
        items.append({
            "id": receipt.id,
            "case_id": receipt.case_id,
            "case_no": c_no,
            "client_name": c_name,
            "fee_type": receipt.fee_type,
            "currency": receipt.currency,
            "receivable_amt": receipt.receivable_amt,
            "received_amt": receipt.received_amt,
            "last_receipt_date": receipt.last_receipt_date,
            "fee_code": receipt.fee_code,
            "fee_name": receipt.fee_name,
            "year_no": receipt.year_no,
            "due_date": receipt.due_date,
            "is_arrears": receipt.is_arrears,
            "is_prepayment": receipt.is_prepayment,
            "is_commissionable": receipt.is_commissionable,
            "invoice_no": receipt.invoice_no,
            "remark": receipt.remark,
        })

    return {"items": items, "page": page, "page_size": page_size, "total": total}
```

- [ ] **Step 4: Verify lint**

```bash
cd backend && ruff check app/modules/billing/service.py && ruff format app/modules/billing/service.py
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/modules/billing/service.py backend/tests/test_case_receipt_crud.py
git commit -m "feat(billing): add CaseReceipt service functions + tests (FR-FE-07)"
```

---

## Task 5: API Endpoints (POST, PUT, GET list)

**Files:**
- Modify: `backend/app/modules/billing/api.py`

- [ ] **Step 1: Add imports**

At top of `backend/app/modules/billing/api.py`, add to existing imports:

```python
from app.modules.billing.schemas import (
    CaseReceiptCreate,
    CaseReceiptUpdate,
    CaseReceiptListItem,
)
from app.modules.billing.service import (
    create_case_receipt,
    update_case_receipt,
    list_case_receipts,
)
```

- [ ] **Step 2: Add POST endpoint**

Add after the existing `get_case_receipt` function (after line 774):

```python
@router.post(
    "/case-receipts",
    response_model=CaseReceiptResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create case receipt",
)
def create_case_receipt_endpoint(
    payload: CaseReceiptCreate,
    _perm: None = Depends(require_perm("CaseReceipt.Create")),
    db: Session = Depends(get_db),
) -> CaseReceiptResponse:
    """
    Create a manual case receipt.

    **Auth**: Bearer JWT
    **Permission**: CaseReceipt.Create
    """
    receipt = create_case_receipt(db, payload)
    db.commit()
    return CaseReceiptResponse(
        id=receipt.id,
        case_id=receipt.case_id,
        fee_type=receipt.fee_type,
        currency=receipt.currency,
        receivable_amt=receipt.receivable_amt,
        received_amt=receipt.received_amt,
        last_receipt_date=receipt.last_receipt_date,
        fee_code=receipt.fee_code,
        fee_name=receipt.fee_name,
        year_no=receipt.year_no,
        due_date=receipt.due_date,
        is_arrears=receipt.is_arrears,
        is_prepayment=receipt.is_prepayment,
        is_commissionable=receipt.is_commissionable,
        invoice_no=receipt.invoice_no,
        remark=receipt.remark,
        bills=[],
    )
```

- [ ] **Step 3: Add PUT endpoint**

```python
@router.put(
    "/case-receipts/{receipt_id}",
    response_model=CaseReceiptResponse,
    summary="Update case receipt",
)
def update_case_receipt_endpoint(
    receipt_id: str,
    payload: CaseReceiptUpdate,
    _perm: None = Depends(require_perm("CaseReceipt.Update")),
    db: Session = Depends(get_db),
) -> CaseReceiptResponse:
    """
    Update a case receipt (partial).

    **Auth**: Bearer JWT
    **Permission**: CaseReceipt.Update
    """
    receipt = update_case_receipt(db, receipt_id, payload)
    db.commit()
    return CaseReceiptResponse(
        id=receipt.id,
        case_id=receipt.case_id,
        fee_type=receipt.fee_type,
        currency=receipt.currency,
        receivable_amt=receipt.receivable_amt,
        received_amt=receipt.received_amt,
        last_receipt_date=receipt.last_receipt_date,
        fee_code=receipt.fee_code,
        fee_name=receipt.fee_name,
        year_no=receipt.year_no,
        due_date=receipt.due_date,
        is_arrears=receipt.is_arrears,
        is_prepayment=receipt.is_prepayment,
        is_commissionable=receipt.is_commissionable,
        invoice_no=receipt.invoice_no,
        remark=receipt.remark,
        bills=[],
    )
```

- [ ] **Step 4: Add GET list endpoint**

```python
@router.get(
    "/case-receipts",
    summary="List case receipts",
)
def list_case_receipts_endpoint(
    client_id: str | None = None,
    case_no: str | None = None,
    fee_type: str | None = None,
    is_arrears: bool | None = None,
    is_commissionable: bool | None = None,
    currency: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    page: int = 1,
    page_size: int = 20,
    _perm: None = Depends(require_perm("CaseReceipt.Read")),
    db: Session = Depends(get_db),
) -> dict:
    """
    List case receipts with cross-case filters.

    **Auth**: Bearer JWT
    **Permission**: CaseReceipt.Read
    """
    return list_case_receipts(
        db,
        client_id=client_id,
        case_no=case_no,
        fee_type=fee_type,
        is_arrears=is_arrears,
        is_commissionable=is_commissionable,
        currency=currency,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
    )
```

- [ ] **Step 5: Run tests — verify GREEN**

```bash
cd backend && source .venv/bin/activate && pytest tests/test_case_receipt_crud.py -v
```

Expected: All 18 tests PASS.

- [ ] **Step 6: Run full test suite**

```bash
pytest -q
```

Expected: All tests PASS (existing + new).

- [ ] **Step 7: Lint**

```bash
ruff check --fix app/modules/billing/api.py && ruff format app/modules/billing/api.py
```

- [ ] **Step 8: Commit**

```bash
git add backend/app/modules/billing/api.py
git commit -m "feat(billing): add CaseReceipt CRUD endpoints (FR-FE-07)"
```

---

## Task 6: Frontend types + API client

**Files:**
- Modify: `frontend/src/api/billing.types.ts`
- Modify: `frontend/src/api/billing.ts`

- [ ] **Step 1: Add TypeScript types**

Add to `frontend/src/api/billing.types.ts`:

```typescript
export interface CaseReceiptCreate {
  case_id: string
  fee_type?: string | null
  fee_code?: string | null
  fee_name?: string | null
  year_no?: number | null
  currency?: string
  receivable_amt: number | string
  received_amt: number | string
  last_receipt_date?: string | null
  due_date?: string | null
  is_arrears?: boolean | null
  is_prepayment?: boolean | null
  is_commissionable?: boolean | null
  invoice_no?: string | null
  remark?: string | null
}

export interface CaseReceiptUpdate {
  fee_type?: string | null
  fee_code?: string | null
  fee_name?: string | null
  year_no?: number | null
  currency?: string | null
  receivable_amt?: number | string | null
  received_amt?: number | string | null
  last_receipt_date?: string | null
  due_date?: string | null
  is_arrears?: boolean | null
  is_prepayment?: boolean | null
  is_commissionable?: boolean | null
  invoice_no?: string | null
  remark?: string | null
}

export interface CaseReceiptListItem {
  id: string
  case_id: string
  case_no?: string | null
  client_name?: string | null
  fee_type?: string | null
  currency: string
  receivable_amt: number
  received_amt: number
  last_receipt_date?: string | null
  fee_code?: string | null
  fee_name?: string | null
  year_no?: number | null
  due_date?: string | null
  is_arrears?: boolean | null
  is_prepayment?: boolean | null
  is_commissionable?: boolean | null
  invoice_no?: string | null
  remark?: string | null
}

export interface CaseReceiptListResponse {
  items: CaseReceiptListItem[]
  page: number
  page_size: number
  total: number
}
```

- [ ] **Step 2: Add API functions**

Add to `frontend/src/api/billing.ts`:

```typescript
import type { CaseReceiptCreate, CaseReceiptUpdate, CaseReceiptListResponse } from './billing.types'

export async function createCaseReceipt(payload: CaseReceiptCreate) {
  const { data } = await api.post('/case-receipts', payload)
  return data
}

export async function updateCaseReceipt(id: string, payload: CaseReceiptUpdate) {
  const { data } = await api.put(`/case-receipts/${id}`, payload)
  return data
}

export async function listCaseReceipts(params: Record<string, unknown> = {}) {
  const { data } = await api.get<CaseReceiptListResponse>('/case-receipts', { params })
  return data
}
```

- [ ] **Step 3: Verify**

```bash
cd frontend && npm run lint && npm run typecheck
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/api/billing.types.ts frontend/src/api/billing.ts
git commit -m "feat(billing): add CaseReceipt CRUD API client (FR-FE-07)"
```

---

## Task 7: Frontend CaseReceiptDialog component

**Files:**
- Create: `frontend/src/modules/billing/components/CaseReceiptDialog.vue`

- [ ] **Step 1: Create dialog component**

Create `frontend/src/modules/billing/components/CaseReceiptDialog.vue` — a shared el-dialog for create/edit with all form fields in Chinese. Component accepts props: `visible`, `receiptId` (null for create), `prefillCaseId` (optional). Emits `saved` and `update:visible`.

*(Full Vue SFC code to be written by implementing agent — must follow existing dialog patterns in the codebase, use el-form with Chinese labels as specified in spec Section 5b/5e.)*

- [ ] **Step 2: Verify**

```bash
cd frontend && npm run lint && npm run typecheck
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/modules/billing/components/CaseReceiptDialog.vue
git commit -m "feat(billing): add CaseReceiptDialog component (FR-FE-07)"
```

---

## Task 8: Frontend CaseReceiptList page

**Files:**
- Create: `frontend/src/modules/billing/pages/CaseReceiptList.vue`
- Modify: `frontend/src/router/index.ts`
- Modify: `frontend/src/constants/menu.ts`

- [ ] **Step 1: Create list page**

Create `frontend/src/modules/billing/pages/CaseReceiptList.vue` — standard list page with filter bar, el-table, pagination, toolbar with "新增收款记录" button. Uses `listCaseReceipts` API function. Opens `CaseReceiptDialog` for create/edit.

*(Full Vue SFC code to be written by implementing agent — must follow BillList.vue pattern, all labels in Chinese.)*

- [ ] **Step 2: Add route**

In `frontend/src/router/index.ts`, add after the payments route (after line 71):

```typescript
{ path: 'billing/case-receipts', name: 'case_receipts', component: () => import('../modules/billing/pages/CaseReceiptList.vue') },
```

- [ ] **Step 3: Add menu item**

In `frontend/src/constants/menu.ts`, add after the payments menu item (after line 56):

```typescript
{ key: 'case_receipts', label: '个案收款登记', icon: '📋', route: '/billing/case-receipts', requiredPerms: [Perms.BILLING_READ] },
```

- [ ] **Step 4: Verify**

```bash
cd frontend && npm run lint && npm run typecheck && npm run build
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/modules/billing/pages/CaseReceiptList.vue frontend/src/router/index.ts frontend/src/constants/menu.ts
git commit -m "feat(billing): add CaseReceiptList page + route + menu (FR-FE-07)"
```

---

## Task 9: Case detail integration

**Files:**
- Modify: `frontend/src/modules/cases/components/CaseReceiptsSummary.vue`

- [ ] **Step 1: Add create button**

In `CaseReceiptsSummary.vue`, add a "新增收款记录" el-button in the card header. On click, open `CaseReceiptDialog` with `prefillCaseId` set to current case ID.

- [ ] **Step 2: Verify**

```bash
cd frontend && npm run lint && npm run typecheck && npm run build
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/modules/cases/components/CaseReceiptsSummary.vue
git commit -m "feat(cases): add create receipt button on case detail (FR-FE-07)"
```

---

## Task 10: Final verification

- [ ] **Step 1: Backend full test suite**

```bash
cd backend && source .venv/bin/activate && pytest -q
```

Expected: All tests PASS (183 existing + 18 new = 201).

- [ ] **Step 2: Clean DB rebuild**

```bash
rm -f fpms_dev.db && alembic upgrade head && python scripts/seed_dev.py
```

- [ ] **Step 3: Frontend quality gates**

```bash
cd frontend && npm run lint && npm run typecheck && npm run build
```

- [ ] **Step 4: Generate artifacts**

Create `artifacts/FR-FE-07/` with:
- `summary.md`
- `results.jsonl`
- `git/diff.patch`

```bash
mkdir -p artifacts/FR-FE-07/git
git diff HEAD~9..HEAD --stat > artifacts/FR-FE-07/git/diff.patch
```

- [ ] **Step 5: Final commit**

```bash
git add artifacts/FR-FE-07/
git commit -m "docs: add FR-FE-07 evidence artifacts"
```
