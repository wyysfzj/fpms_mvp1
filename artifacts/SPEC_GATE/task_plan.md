# SPEC ALIGNMENT GATE — Task Plan

## Objective
Write `backend/tests/test_spec_alignment_e2e.py` with 2 E2E chain tests proving cross-module integration.

## Tasks

### T1: Impl — Write test_spec_alignment_e2e.py
- **Owner**: impl-agent
- **File**: `backend/tests/test_spec_alignment_e2e.py`
- **Test 1**: `test_e2e_oa_workflow` — OA lifecycle chain
- **Test 2**: `test_e2e_billing_workflow` — Financial chain
- **Acceptance**: ruff clean, both tests pass, full suite 141+ pass

### T2: Quality Gate — ruff + pytest
- **Owner**: impl-agent (after T1)
- **Commands**: `ruff check --fix . && ruff format . && pytest -q`

### T3: Clean Rebuild — alembic + seed + healthz
- **Owner**: lead
- **Commands**: `rm -f fpms_dev.db && alembic upgrade head && python scripts/seed_dev.py`

### T4: Review — verify spec coverage
- **Owner**: review-agent
- **Deliverable**: `artifacts/SPEC_GATE/review_report.md`

## API Endpoint Reference

| Action | Endpoint | Notes |
|--------|----------|-------|
| Create client | POST /api/v1/clients | 201 |
| Create case | POST /api/v1/cases | 201, status=NOT_FILED |
| List doc templates | GET /api/v1/doc-templates?q=CODE | find by code |
| Create document | POST /api/v1/documents | 201, check X-Auto-* headers |
| Get case | GET /api/v1/cases/{id} | verify status cascade |
| List tasks | GET /api/v1/tasks?case_id={id} | tasks with status |
| Get task logs | GET /api/v1/tasks/{id}/logs | action field |
| Get document | GET /api/v1/documents/{id} | reply_date |
| Search cases | GET /api/v1/cases?client_id=X&status=Y | advanced search |
| Get fee draft | GET /api/v1/fees/drafts/{id} | draft_type (no amount) |
| List fee drafts | GET /api/v1/fees/drafts?case_id={id} | has amount |
| Create fee rate | POST /api/v1/fees/rates | 201 |
| Add fee item | POST /api/v1/fees/drafts/{id}/items | 201 |
| Create bill | POST /api/v1/bills/from-drafts | 201, status only (no amount/balance) |
| List bills | GET /api/v1/bills | has amount, balance, status |
| Create payment | POST /api/v1/payments | 201 |
| Get payment | GET /api/v1/payments/{id} | has payment_lines |
| Create offset | POST /api/v1/offsets | 201 |
| Reverse offset | POST /api/v1/offsets/{id}/reverse | 200 |
| Case receipts | GET /api/v1/cases/{id}/receipts | received_amt |

## Key Gotchas
- Bill detail (GET /bills/{id}) does NOT return amount/balance — use list endpoint
- Fee draft detail does NOT return amount — use list endpoint
- BillResponse from POST /bills/from-drafts only has id/bill_no/client_id/currency/direction/status
- Auto-draft starts at amount=0; must add fee items before bill generation
- GRANT_NOTICE has no deadline_template_code → X-Auto-Tasks-Created: 0
