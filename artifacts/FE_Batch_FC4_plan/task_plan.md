# Batch FC4 — Billing Offset Reversal + Receipt Enrichment — Task Plan

> Created: 2026-02-27
> Status: Planning

## Objective
Add offset reversal UI (reverse button + status tag in BillDetail). Display enriched CaseReceipt fields (fee_code, year_no, is_arrears).

## Backend Dependency Check
- **Backend B5 Status**: COMPLETE
  - POST /api/v1/offsets/{offset_id}/reverse — exists and working
  - CaseReceiptResponse includes: fee_code, year_no, is_arrears, invoice_no, is_commissionable
  - Offset model has: is_reversed, reversed_at fields
  - OffsetResponse includes: is_reversed (but NOT reversed_at)

## Pre-existing Implementation (IMPORTANT)
Some FC4 items already exist:
- `billing.ts`: `reverseOffset()` function already implemented (line 309)
- `billing.ts`: `BackendOffset.is_reversed` already mapped (line 72)
- `billing.types.ts`: `OffsetListItem.is_reversed` already present (line 127)

## Still Missing
- `billing.types.ts`: No `reversed_at` on OffsetListItem; CaseReceipt types missing enriched fields
- `BillDetail.vue`: No offsets section/tab at all — needs new UI
- `CaseReceiptsSummary.vue`: No fee_code, year_no, is_arrears display

## File Allowlist (STRICT)
| File | Action |
|------|--------|
| `frontend/src/api/billing.ts` | MODIFY — already has reverseOffset, may need BackendOffset update |
| `frontend/src/api/billing.types.ts` | MODIFY — add reversed_at, enrich CaseReceipt types |
| `frontend/src/modules/billing/pages/BillDetail.vue` | MODIFY — add offsets section with reverse button |
| `frontend/src/modules/cases/components/CaseReceiptsSummary.vue` | MODIFY — display enriched receipt fields |

## Tasks
- T1: Architect Plan
- T2: Update billing.types.ts
- T3: Update billing.ts (if needed)
- T4: Update BillDetail.vue — add offsets section
- T5: Update CaseReceiptsSummary.vue — add enriched fields
- T6: Quality Gate
- T7: Review Report
