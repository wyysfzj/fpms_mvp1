# BE-B-OA-FINANCE-READINESS-01

Task ID: `BE-B-OA-FINANCE-READINESS-01`

Story Shape Classification:
- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

chosen_runbook: `P0-prereq-heavy-story`

## Exact Closure Slice

Verify or minimally fix OA fee draft, OA bill, payment offset, CaseReceipt, and commission readiness for `TC-B-009`, `TC-B-010`, `TC-B-011`, and `TC-B-012`.

## Explicit Non-Closure

Do not:
- implement pytest automation handlers
- modify frontend or skeleton data
- combine unresolved fee, billing, payment, and commission product decisions into one guessed backend implementation
- change schema or migrations

## Remaining Follow-Up Task IDs

- `BE-B-OA-FEE-DRAFT-READINESS-01`
- `BE-B-OA-BILL-PAYMENT-READINESS-01`
- `BE-B-OA-COMMISSION-READINESS-01`

## Allowed Files

- `tasks/backend/business_logic/BE-B-OA-FINANCE-READINESS-01.md`
- `backend/app/modules/documents/service.py`
- `backend/app/modules/fees/service.py`
- `backend/app/modules/billing/service.py`
- `backend/app/modules/commission/service.py`
- `backend/tests/test_b_oa_finance_readiness.py`
- `artifacts/BE-B-OA-FINANCE-READINESS-01/**`

## Verification Commands

Run from `backend/` if implementation proceeds:

```bash
python3 -m ruff check app/modules/documents/service.py app/modules/fees/service.py app/modules/billing/service.py app/modules/commission/service.py
pytest tests/test_b3_fee_linking.py -q
./scripts/task_validate.sh BE-B-OA-FINANCE-READINESS-01
```

## Evidence Path

- `artifacts/BE-B-OA-FINANCE-READINESS-01/results.jsonl`
- `artifacts/BE-B-OA-FINANCE-READINESS-01/summary.md`
- `artifacts/BE-B-OA-FINANCE-READINESS-01/git/diff.patch`

## Status

BLOCKED

## Blocker Reason

Readiness confirms the repository has generic document fee-linking and A-wave billing/payment/commission services, but B-wave OA finance closure would combine multiple dependent closures:

- OA fee draft generation from `OA_FEE`
- OA official fee pay-list and payment
- OA AR bill and customer payment offset
- OA service-fee commission generation

This task would need to modify multiple shared services in one atomic task. Split into the listed follow-up tasks before implementation.
