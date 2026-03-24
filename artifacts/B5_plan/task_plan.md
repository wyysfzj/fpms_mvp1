# B5 — CaseReceipt Enrichment + Billing Polish — Task Plan

## Status: PLAN COMPLETE — Ready for Implementation

## Batch Scope
Add missing fields to T_CaseReceipt (5 columns) and implement offset reversal
service + endpoint.

## Team Composition
| Role | Agent Name | Status |
|------|-----------|--------|
| Architect | architect | ✅ Plan Complete |
| Backend Impl | backend-impl | Pending |
| Test Agent | test-agent | Pending |
| Reviewer | reviewer | Pending |

## Task Decomposition

### Backend Agent Tasks (sequential execution)

| ID | Task | File(s) | Dependencies |
|----|------|---------|-------------|
| B5-1 | Create Alembic migration: add 5 cols to t_case_receipt | `alembic/versions/b5_case_receipt_enrich.py` (NEW) | — |
| B5-2 | Update CaseReceipt model: add fee_code, year_no, is_arrears, invoice_no, is_commissionable | `app/modules/billing/models.py` | B5-1 |
| B5-3 | Add CaseReceiptResponse schema | `app/modules/billing/schemas.py` | B5-2 |
| B5-4 | Implement `reverse_offset()` + `_reverse_offset_from_receipts()` in service | `app/modules/billing/service.py` | B5-2 |
| B5-5 | Fix reverse_offset API endpoint → call service, change perm to Billing.Edit, fix status code | `app/modules/billing/api.py` | B5-4 |
| B5-6 | Update GET /cases/{case_id}/receipts response to include 5 new fields | `app/modules/billing/api.py` | B5-3 |
| B5-7 | Verify/add Billing.Edit permission in RBAC seed | `app/modules/rbac/service.py` | — |

### Test Agent Tasks (after all backend tasks)

| ID | Test | Description |
|----|------|-------------|
| B5-T2a | test_case_receipt_new_fields | Create receipt with new fields, verify API response |
| B5-T2b | test_case_receipt_backward_compat | Existing receipts return null for new fields |
| B5-T3 | test_offset_reversal_happy_path | Full flow: bill → payment → offset → reverse → verify balances |
| B5-T4 | test_offset_reversal_partial | Two offsets, reverse one, verify partial balance |
| B5-T5 | test_double_reversal_blocked | Reverse same offset twice → 400 |
| B5-T6 | test_offset_not_found | Reverse non-existent offset → 404 |
| B5-T7 | test_payment_line_balance_restored | Verify payment_line balances restored after reversal |
| B5-T8 | test_receipt_received_amt_reversed | Verify CaseReceipt.received_amt decreased after reversal |

## Dependency Graph
```
B5-1 (Migration) → B5-2 (Model) → B5-3 (Schema) → B5-6 (Receipt API)
                                 → B5-4 (Service)  → B5-5 (Reverse API)
B5-7 (RBAC) — parallel/independent

All B5-1..B5-7 → B5-T2..T8 (Tests)
```

## Quality Gates
1. `alembic upgrade head` on fresh DB
2. `python scripts/seed_dev.py` succeeds
3. `pytest --tb=short` — all pass
4. `ruff check --fix . && ruff format .` — clean
