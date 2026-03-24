# Batch FC4 — Findings

## Backend Dependency (B5)
- CONFIRMED COMPLETE
- POST /offsets/{offset_id}/reverse endpoint exists (perm: Billing.Edit)
- CaseReceiptResponse includes: fee_code, year_no, is_arrears, invoice_no, is_commissionable
- OffsetResponse returns: is_reversed but NOT reversed_at

## Pre-existing Implementation
- `reverseOffset()` function already in billing.ts (line 309-312)
- `BackendOffset` already has `is_reversed: boolean` (line 72)
- `mapOffset()` already maps `is_reversed` (line 152)
- `OffsetListItem` already has `is_reversed: boolean` (billing.types.ts:127)

## Investigation A: No Backend Endpoint for Listing Offsets by Bill
- **Severity**: Medium — blocks full offsets tab functionality
- Backend has `POST /offsets` (create) and `POST /offsets/{id}/reverse` (reverse) only
- No `GET /offsets?bill_id=X` endpoint exists
- `GET /bills/{bill_id}` does NOT include offsets in response (only returns id, bill_no, client_id, currency, direction, status)
- Frontend `getOffsets()` is a confirmed stub returning empty array
- **Resolution**: Wire UI fully, show "暂无抵扣记录" empty state. Backend needs `GET /offsets?bill_id=X` (future ticket)

## Investigation B: CaseReceipt API Shape Mismatch
- **Severity**: High — current code shows undefined/0 for summary cards
- Backend returns: `{id, case_id, fee_type, currency, receivable_amt, received_amt, last_receipt_date, fee_code, year_no, is_arrears, invoice_no, is_commissionable}`
- Frontend expects: `{case_id, total_billed, total_paid, total_outstanding, bills[]}`
- `getCaseReceipts()` casts directly without mapper — broken
- **Resolution**: Add `BackendCaseReceipt` + `mapCaseReceipt()`. Map receivable_amt→total_billed, received_amt→total_paid, compute total_outstanding

## Finding C: `reversed_at` Not in Backend OffsetResponse Schema
- **Severity**: Low
- Backend Offset model has `reversed_at` (models.py:114), service sets it
- But `OffsetResponse` schema does NOT include it — API never returns this field
- Frontend `reversed_at` will always be `undefined`. No functional impact (UI uses `is_reversed` boolean)

## Finding D: `GET /bills/{bill_id}` Response is Minimal
- **Severity**: Info
- Only returns `{id, bill_no, client_id, currency, direction, status}` — no amount, balance, dates, items
- Frontend mapBillDetail fills defaults for missing fields

## Bugs Found
- CaseReceiptsSummary shows 0/undefined for all metrics due to shape mismatch (Finding B) — will be fixed by FC4
