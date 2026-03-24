# B5 Findings

## Bugs Found

### F-01: CRITICAL — Existing reverse_offset Endpoint is Broken (api.py:409-453)
**Severity**: CRITICAL — Financial data corruption
**Location**: `backend/app/modules/billing/api.py` lines 409-453

The existing `POST /offsets/{offset_id}/reverse` endpoint:
1. Does NOT check if offset is already reversed → allows double reversal
2. Does NOT set `reversed_at` timestamp
3. Does NOT restore `bill.balance` → bill balance permanently reduced after reversal
4. Does NOT update `bill.status` after balance restoration
5. Does NOT restore `payment_line.allocated_amt` / `payment_line.balance_amt`
6. Does NOT reverse `CaseReceipt.received_amt` (undo receipt allocation)
7. Uses `Payment.Create` permission instead of `Billing.Edit`
8. Returns `201 CREATED` (semantically wrong for reversal)

**Impact**: Any offset reversal in the current system silently corrupts bill balances.
**Resolution**: B5-4 (service function) + B5-5 (endpoint fix)

### F-02: Minor — CaseReceipt Response Missing last_receipt_date
**Location**: `backend/app/modules/billing/api.py` lines 579-586
The `GET /cases/{case_id}/receipts` endpoint omits `last_receipt_date` from response.
**Resolution**: Fixed in B5-6

## Deviations from Plan

### D-01: Endpoint Already Exists
The spec says "Add POST /billing/offsets/{offset_id}/reverse endpoint" but the endpoint already
exists at `POST /offsets/{offset_id}/reverse` (no `/billing/` prefix — billing router has no
prefix in central router). We will enhance the existing endpoint rather than creating a duplicate.

### D-02: Permission Name Mismatch — Billing.Edit Does NOT Exist
Spec says `Billing.Edit` but this permission does NOT exist in RBAC seed.
Existing offset endpoints use `Payment.Create` (Admin role).
The Finance role has `Payment.Offset` which is semantically closer.

**Decision**: Add `Billing.Edit` to both Admin and Finance roles in RBAC seed (Task B5-7).
This ensures tests pass (admin user) and Finance role can reverse offsets in production.

Current relevant permissions:
- Admin: `Bill.Create`, `Bill.Print`, `Bill.Read`, `Payment.Create`, `Payment.Read`
- Finance: `Bill.Read`, `Bill.CreateFromDraft`, `Bill.CreateManual`, `Bill.Print`, `Payment.Create`, `Payment.Offset`

Neither role has `Billing.Edit`. Must add it to both.

## Discoveries

### Discovery 1: No Existing Billing Tests
There are no existing test files specifically covering billing endpoints (bills, payments,
offsets, receipts). The test_flows.py may have some coverage but there's no dedicated
test_billing.py. This means B5 tests will be the first dedicated billing test suite.

### Discovery 2: Receipt Allocation is Proportional
The `_allocate_offset_to_receipts()` function distributes offset amounts proportionally
across CaseReceipts based on BillItem amounts. The reversal function must use the exact
same proportional logic to ensure consistency. Last item gets the remainder to avoid
rounding issues.

### Discovery 3: CaseReceipt is Keyed by (case_id, fee_type)
When allocating to receipts, the service looks up by `(case_id, fee_type)` — not by
receipt ID. This is important for the reversal logic: we must match on the same compound key.
