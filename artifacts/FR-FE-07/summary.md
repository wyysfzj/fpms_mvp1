# FR-FE-07: Case Receipt CRUD — Summary

- **Task**: FR-FE-07 (P0 #2 — 个案收款登记)
- **Role**: Implementation (subagent-driven)
- **Result**: `PASS`
- **Date**: 2026-03-24

## Exact Closure Slice

Manual CRUD for CaseReceipt: POST create, PUT update, GET cross-case list with filters. Frontend list page + create/edit dialog + case detail integration.

## Explicit Non-Closure

- Does NOT modify existing auto-allocation flow (`_allocate_offset_to_receipts` / `_reverse_offset_from_receipts`)
- Does NOT add delete endpoint
- Does NOT implement FR-FE-09 (full fee status query) — only the CaseReceipt portion

## Files Changed

### Backend
- `backend/alembic/versions/pe_fr_fe_07_case_receipt_ext.py` — NEW migration (4 columns)
- `backend/app/modules/billing/models.py` — 4 new mapped_column fields
- `backend/app/modules/billing/schemas.py` — CaseReceiptCreate, CaseReceiptUpdate, CaseReceiptListItem, updated Response
- `backend/app/modules/billing/service.py` — create_case_receipt, update_case_receipt, list_case_receipts
- `backend/app/modules/billing/api.py` — POST/PUT/GET endpoints
- `backend/app/modules/rbac/service.py` — CaseReceipt.Create, CaseReceipt.Update permissions
- `backend/tests/test_case_receipt_crud.py` — 18 tests

### Frontend
- `frontend/src/api/billing.types.ts` — 4 new TypeScript interfaces
- `frontend/src/api/billing.ts` — 3 new API functions
- `frontend/src/modules/billing/components/CaseReceiptDialog.vue` — NEW dialog
- `frontend/src/modules/billing/pages/CaseReceiptList.vue` — NEW list page
- `frontend/src/modules/cases/components/CaseReceiptsSummary.vue` — added create button
- `frontend/src/router/index.ts` — added route
- `frontend/src/constants/menu.ts` — added menu item

## Validation

- `pytest tests/test_case_receipt_crud.py -v` → 18 passed
- `pytest -q` → 219 passed (3 pre-existing annuity failures unrelated)
- `rm -f fpms_dev.db && alembic upgrade head && python scripts/seed_dev.py` → success
- `npm run lint` → PASS
- `npm run typecheck` → PASS
- `npm run build` → PASS
