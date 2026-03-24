# B5 — CaseReceipt Enrichment + Billing Polish — Architecture Plan

**Author**: Architect Agent
**Date**: 2026-02-26
**Status**: READY FOR REVIEW

---

## 1. Current State Analysis

### 1.1 T_CaseReceipt (models.py:74-88)
Current columns:
| Column | Type | Constraints |
|--------|------|-------------|
| id | String(36) PK | UUIDPrimaryKeyMixin |
| case_id | String(36) FK→t_case.id | NOT NULL, CASCADE |
| fee_type | String(16) | nullable |
| currency | String(8) | NOT NULL, default 'CNY' |
| receivable_amt | Numeric(18,2) | NOT NULL, default 0 |
| received_amt | Numeric(18,2) | NOT NULL, default 0 |
| last_receipt_date | Date | nullable |
| created_at, updated_at, created_by, updated_by | AuditMixin | — |

### 1.2 T_Offset (models.py:91-105)
Current columns:
| Column | Type | Notes |
|--------|------|-------|
| id | String(36) PK | — |
| payment_line_id | String(36) FK→t_payment_line.id | CASCADE |
| bill_id | String(36) FK→t_bill.id | CASCADE |
| offset_amt | Numeric(18,2) | NOT NULL, default 0 |
| offset_date | Date | nullable |
| **is_reversed** | Boolean | NOT NULL, default 0 |
| **reversed_at** | DateTime | nullable |

**Key**: `is_reversed` and `reversed_at` already exist in the model. No model changes needed for T_Offset.

### 1.3 T_Bill (models.py:23-49)
Key fields for offset reversal:
- `amount`: Numeric(18,2) — total bill amount
- `balance`: Numeric(18,2) — remaining unpaid balance
- `status`: String(24) — UNSETTLED / PARTIALLY_SETTLED / SETTLED

### 1.4 Existing Service Functions (service.py)
- `create_offset()` — Creates offset, reduces bill.balance, updates bill status, updates payment_line balances, allocates to CaseReceipts via `_allocate_offset_to_receipts()`
- `_apply_bill_status()` — Validates and applies bill status transitions (allows all transitions between the 3 states)
- `_allocate_offset_to_receipts()` — Distributes offset amount proportionally across CaseReceipts based on BillItem amounts

### 1.5 Existing API Endpoints (api.py)
- `GET /bills` — List bills (paginated, includes client_name)
- `POST /bills/from-drafts` — Create bill from fee drafts
- `POST /bills/manual` — Create manual bill
- `GET /bills/{bill_id}` — Get bill detail
- `GET /bills/{bill_id}/print` — Print bill as DOCX
- `GET /payments` — List payments
- `POST /payments` — Create payment
- `GET /payments/{payment_id}` — Get payment detail
- `POST /offsets` — Create offset
- **`POST /offsets/{offset_id}/reverse`** — ALREADY EXISTS but incomplete (see Finding F-01)
- `GET /cases/{case_id}/receipts` — Get case receipt

### 1.6 Existing Schemas (schemas.py)
- No dedicated CaseReceipt schemas exist. Receipt data is returned as raw dict in the API handler.
- `OffsetResponse` — has id, payment_line_id, bill_id, offset_amt, offset_date, is_reversed

### 1.7 Migration Chain
Latest migration: `b4_fee_rate_dims_01` (revises: `b2_doc_reply_01`).
New migration must chain from `b4_fee_rate_dims_01`.

---

## 2. Findings (Critical)

### F-01: EXISTING reverse_offset ENDPOINT IS INCOMPLETE (CRITICAL BUG)

**Location**: `api.py:409-453`

The existing `reverse_offset` endpoint at `POST /offsets/{offset_id}/reverse`:
1. Does NOT check if offset is already reversed → **allows double reversal**
2. Does NOT set `reversed_at` timestamp
3. Does NOT restore `bill.balance` → **bill balance permanently reduced**
4. Does NOT update `bill.status` after balance restoration
5. Does NOT restore `payment_line.allocated_amt` / `payment_line.balance_amt`
6. Does NOT reverse `CaseReceipt.received_amt` (undo receipt allocation)
7. Uses wrong permission: `Payment.Create` instead of spec's `Billing.Edit`
8. Returns `201 CREATED` which is semantically wrong for a reversal (should be `200 OK`)

**Impact**: Offset reversals currently corrupt financial data. The bill balance is never restored.

**Resolution**: Replace the inline handler logic with a proper `reverse_offset()` service function.

### F-02: CaseReceipt Response Missing last_receipt_date

The `GET /cases/{case_id}/receipts` endpoint (api.py:579-586) does not return `last_receipt_date` even though it's in the model. Minor issue, will be fixed when adding new fields.

### F-03: No CaseReceipt Schemas

There are no Pydantic schemas for CaseReceipt create/update/response. The API returns raw dicts. We should add at least a response schema.

---

## 3. Task Decomposition

### Task B5-1: Alembic Migration — Add 5 Columns to t_case_receipt
**Agent**: Backend
**File**: `alembic/versions/b5_case_receipt_enrich.py`
**Dependencies**: None

New migration `b5_case_receipt_01` chaining from `b4_fee_rate_dims_01`:

```python
"""b5_case_receipt_enrich

Revision ID: b5_case_receipt_01
Revises: b4_fee_rate_dims_01
Create Date: 2026-02-26

Add 5 enrichment columns to t_case_receipt.
"""
from __future__ import annotations
import sqlalchemy as sa
from alembic import op

revision = "b5_case_receipt_01"
down_revision = "b4_fee_rate_dims_01"
branch_labels = None
depends_on = None

def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    if not insp.has_table("t_case_receipt"):
        return

    existing = {col["name"] for col in insp.get_columns("t_case_receipt")}

    columns = [
        ("fee_code", sa.String(64), None),
        ("year_no", sa.Integer(), None),
        ("is_arrears", sa.Boolean(), sa.text("0")),
        ("invoice_no", sa.String(64), None),
        ("is_commissionable", sa.Boolean(), sa.text("0")),
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

### Task B5-2: Update CaseReceipt Model — Add 5 Columns
**Agent**: Backend
**File**: `app/modules/billing/models.py`
**Dependencies**: B5-1

Add after `last_receipt_date` (line 88):

```python
fee_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
year_no: Mapped[int | None] = mapped_column(Integer, nullable=True)
is_arrears: Mapped[bool | None] = mapped_column(Boolean, nullable=True, server_default=text("0"))
invoice_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
is_commissionable: Mapped[bool | None] = mapped_column(Boolean, nullable=True, server_default=text("0"))
```

Note: `Boolean` and `Integer` are already imported. No new imports needed.

### Task B5-3: Add CaseReceipt Schemas
**Agent**: Backend
**File**: `app/modules/billing/schemas.py`
**Dependencies**: B5-2

Add `CaseReceiptResponse` schema:

```python
class CaseReceiptResponse(BaseModel):
    """Response schema for case receipts."""
    id: str
    case_id: str
    fee_type: str | None
    currency: str
    receivable_amt: Decimal
    received_amt: Decimal
    last_receipt_date: date | None
    fee_code: str | None = None
    year_no: int | None = None
    is_arrears: bool | None = None
    invoice_no: str | None = None
    is_commissionable: bool | None = None
```

### Task B5-4: Implement reverse_offset() Service Function
**Agent**: Backend
**File**: `app/modules/billing/service.py`
**Dependencies**: B5-2

Add `reverse_offset(db, offset_id, actor_id)` function:

```python
def reverse_offset(db: Session, offset_id: str, actor_id: str | None = None) -> Offset:
    """Reverse an existing offset, restoring bill and payment line balances."""
    # 1. Load offset
    offset = db.query(Offset).filter(Offset.id == offset_id).first()
    if not offset:
        raise_business_error("OFFSET_NOT_FOUND", "Offset not found", status_code=404)

    # 2. Check already reversed
    if offset.is_reversed:
        raise_business_error(
            "OFFSET_ALREADY_REVERSED",
            "Offset has already been reversed",
            status_code=400,
        )

    # 3. Mark offset as reversed
    offset.is_reversed = True
    offset.reversed_at = datetime.now(timezone.utc)

    # 4. Restore bill balance
    bill = db.query(Bill).filter(Bill.id == offset.bill_id).first()
    if not bill:
        raise_business_error("BILL_NOT_FOUND", "Bill not found", status_code=404)

    bill.balance = bill.balance + offset.offset_amt

    # 5. Update bill status based on new balance
    if bill.balance == bill.amount:
        next_status = "UNSETTLED"
    elif bill.balance > Decimal("0"):
        next_status = "PARTIALLY_SETTLED"
    else:
        next_status = "SETTLED"
    _apply_bill_status(bill, next_status)

    # 6. Restore payment line balances
    payment_line = db.query(PaymentLine).filter(PaymentLine.id == offset.payment_line_id).first()
    if payment_line:
        payment_line.allocated_amt = payment_line.allocated_amt - offset.offset_amt
        payment_line.balance_amt = payment_line.balance_amt + offset.offset_amt

    # 7. Reverse CaseReceipt allocations (proportional, matching _allocate_offset_to_receipts)
    _reverse_offset_from_receipts(db, bill, offset.offset_amt)

    db.commit()
    db.refresh(offset)
    return offset
```

Also add helper `_reverse_offset_from_receipts()`:

```python
def _reverse_offset_from_receipts(
    db: Session, bill: Bill, offset_amt: Decimal
) -> None:
    """Reverse the proportional receipt allocation for an offset reversal."""
    items = (
        db.query(BillItem)
        .filter(BillItem.bill_id == bill.id, BillItem.case_id.isnot(None))
        .all()
    )
    if not items or offset_amt <= Decimal("0"):
        return

    total_amount = sum((item.amount for item in items), Decimal("0"))
    if total_amount <= Decimal("0"):
        return

    remaining = offset_amt
    for index, item in enumerate(items):
        if index == len(items) - 1:
            share = remaining
        else:
            share = (offset_amt * item.amount) / total_amount
            remaining -= share
        if share <= Decimal("0"):
            continue

        receipt = (
            db.query(CaseReceipt)
            .filter(CaseReceipt.case_id == item.case_id, CaseReceipt.fee_type == item.fee_type)
            .first()
        )
        if receipt:
            receipt.received_amt = max(receipt.received_amt - share, Decimal("0"))
```

**New imports needed** in service.py:
```python
from datetime import datetime, timezone  # add timezone
```
Note: `datetime` is already imported but `timezone` is not. Also `Decimal` is already imported.

### Task B5-5: Fix reverse_offset API Endpoint
**Agent**: Backend
**File**: `app/modules/billing/api.py`
**Dependencies**: B5-4

Replace the existing `reverse_offset` endpoint (lines 409-453) to call the service function:

```python
@router.post(
    "/offsets/{offset_id}/reverse",
    summary="Reverse an offset",
    response_model=OffsetResponse,
)
def reverse_offset(
    offset_id: str,
    _perm: None = Depends(require_perm("Billing.Edit")),
    db: Session = Depends(get_db),
) -> OffsetResponse:
    """Reverse an offset (mark as reversed, restore bill and payment balances)."""
    offset = reverse_offset_service(db, offset_id)
    return OffsetResponse(
        id=offset.id,
        payment_line_id=offset.payment_line_id,
        bill_id=offset.bill_id,
        offset_amt=offset.offset_amt,
        offset_date=offset.offset_date,
        is_reversed=offset.is_reversed,
    )
```

Changes:
1. Remove `status_code=201` (default 200 is correct for reversal)
2. Change permission from `Payment.Create` to `Billing.Edit`
3. Add `response_model=OffsetResponse`
4. Call `reverse_offset_service()` instead of inline logic
5. Import `reverse_offset as reverse_offset_service` from service

### Task B5-6: Update CaseReceipt API Response
**Agent**: Backend
**File**: `app/modules/billing/api.py`
**Dependencies**: B5-3

Update `GET /cases/{case_id}/receipts` endpoint (lines 550-586) to include new fields:

```python
return {
    "id": receipt.id,
    "case_id": receipt.case_id,
    "fee_type": receipt.fee_type,
    "currency": receipt.currency,
    "receivable_amt": receipt.receivable_amt,
    "received_amt": receipt.received_amt,
    "last_receipt_date": receipt.last_receipt_date,
    "fee_code": receipt.fee_code,
    "year_no": receipt.year_no,
    "is_arrears": receipt.is_arrears,
    "invoice_no": receipt.invoice_no,
    "is_commissionable": receipt.is_commissionable,
}
```

### Task B5-7: Add Billing.Edit Permission to RBAC Seed
**Agent**: Backend
**File**: `app/modules/rbac/service.py`
**Dependencies**: None (can run in parallel)

`Billing.Edit` does NOT exist in the current RBAC seed. Must add it to:
- **Admin** role (line 12-70): Add `"Billing.Edit"` to the permissions list
- **Finance** role (line 112-125): Add `"Billing.Edit"` to the permissions list

This ensures:
1. Tests pass (admin user has the permission)
2. Finance role can reverse offsets in production

After editing, re-run `python scripts/seed_dev.py` to seed the new permission.

---

## 4. Test Strategy

### Task B5-T1: Test Migration (implicit)
Validated by: `rm -f fpms_dev.db && alembic upgrade head && python scripts/seed_dev.py`

### Task B5-T2: Test CaseReceipt New Fields
**File**: `tests/test_b5_billing_polish.py`

- **T2a**: Create a CaseReceipt with new fields via DB, verify via GET /cases/{case_id}/receipts
- **T2b**: Backward compat — existing receipts without new fields still return correctly (null fields)

### Task B5-T3: Test Offset Reversal — Happy Path
- Create client → bill → payment → offset → verify bill.balance reduced
- Call `POST /offsets/{offset_id}/reverse`
- Assert: `is_reversed=True`, `offset_date` preserved
- Assert: bill.balance restored to original amount
- Assert: bill.status back to UNSETTLED

### Task B5-T4: Test Offset Reversal — Partial Reversal
- Create bill, create two offsets (partial payments)
- Reverse one offset
- Assert: bill.balance = amount - remaining_offset
- Assert: bill.status = PARTIALLY_SETTLED

### Task B5-T5: Test Double Reversal Blocked
- Reverse an offset
- Attempt to reverse same offset again
- Assert: 400 error with code OFFSET_ALREADY_REVERSED

### Task B5-T6: Test Offset Not Found
- Call reverse with non-existent ID
- Assert: 404

### Task B5-T7: Test Payment Line Balance Restoration
- After offset creation: verify payment_line.balance_amt reduced
- After reversal: verify payment_line.balance_amt restored

### Task B5-T8: Test CaseReceipt received_amt Reversal
- Create bill with BillItems → create offset → verify CaseReceipt.received_amt increased
- Reverse offset → verify CaseReceipt.received_amt decreased back

---

## 5. Dependency Graph

```
B5-1 (Migration)
  └─→ B5-2 (Model)
        ├─→ B5-3 (Schema)
        │     └─→ B5-6 (API receipt response)
        └─→ B5-4 (Service: reverse_offset)
              └─→ B5-5 (API: fix reverse endpoint)

B5-7 (RBAC seed) — independent, parallel

B5-T2..T8 (Tests) — depend on all B5-1..B5-6 complete
```

**Execution order for Backend Agent**:
1. B5-1 → B5-2 → B5-3 → B5-4 → B5-5 → B5-6 → B5-7 (sequential)

**Test Agent** starts after Backend Agent completes all tasks.

---

## 6. Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Double reversal corrupts balances | HIGH | Explicit `is_reversed` check at start of service function |
| Proportional receipt reversal rounding | MEDIUM | Use same algorithm as `_allocate_offset_to_receipts` with last-item remainder |
| `Billing.Edit` permission not seeded | LOW | Check RBAC seed; add if missing |
| Existing tests break | LOW | No existing billing-specific tests found; new fields are nullable |
| Migration fails on existing data | LOW | All new columns nullable; idempotent column check |

---

## 7. Files Changed Summary

| File | Change Type |
|------|------------|
| `alembic/versions/b5_case_receipt_enrich.py` | NEW — migration |
| `app/modules/billing/models.py` | EDIT — 5 columns on CaseReceipt |
| `app/modules/billing/schemas.py` | EDIT — add CaseReceiptResponse |
| `app/modules/billing/service.py` | EDIT — add reverse_offset(), _reverse_offset_from_receipts() |
| `app/modules/billing/api.py` | EDIT — fix reverse endpoint, update receipt response |
| `app/modules/rbac/service.py` | EDIT (conditional) — add Billing.Edit perm if missing |
| `tests/test_b5_billing_polish.py` | NEW — 8 test cases |

---

## 8. Acceptance Criteria

1. `alembic upgrade head` succeeds on fresh DB
2. `python scripts/seed_dev.py` succeeds
3. GET /cases/{case_id}/receipts returns all 5 new fields
4. POST /offsets/{offset_id}/reverse:
   - Returns 200 with OffsetResponse (is_reversed=True)
   - Restores bill.balance
   - Updates bill.status correctly
   - Restores payment_line balances
   - Blocks double reversal (400)
   - Returns 404 for non-existent offset
5. All existing tests pass (`pytest --tb=short`)
6. New tests pass
7. `ruff check --fix . && ruff format .` clean
