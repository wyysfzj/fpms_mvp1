# BE-B-OA-FEE-DRAFT-READINESS-01

Task ID: `BE-B-OA-FEE-DRAFT-READINESS-01`

Story Shape Classification:
- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

chosen_runbook: `P0-prereq-heavy-story`

## Exact Closure Slice

Verify and minimally fix OA fee draft generation from a document template configured with `fee_draft_type=OA_FEE` and `fee_item_list`.

This task closes only:
- generate an `OA_FEE` draft from a fee-enabled OA document template
- create configured SERVICE and GOV fee items
- calculate `total_service`, `total_gov`, `total_misc`, and `amount`
- preserve existing generic document fee-linking behavior

## Explicit Non-Closure

Do not:
- implement OA pay-list
- implement OA bill/payment
- implement OA commission
- implement pytest automation handlers
- modify frontend or skeleton data
- add schema or migration

## Remaining Follow-Up Task IDs

- `BE-B-OA-BILL-PAYMENT-READINESS-01`
- `BE-B-OA-COMMISSION-READINESS-01`
- `B-AUTO-PY-B-OA-FEE-P1-01`

## Allowed Files

- `tasks/backend/business_logic/BE-B-OA-FEE-DRAFT-READINESS-01.md`
- `backend/app/modules/documents/fee_linking_service.py`
- `backend/tests/test_b3_fee_linking.py`
- `artifacts/BE-B-OA-FEE-DRAFT-READINESS-01/**`

## Verification Commands

Run from `backend/`:

```bash
python3 -m ruff check --fix app/modules/documents/fee_linking_service.py tests/test_b3_fee_linking.py
python3 -m ruff format app/modules/documents/fee_linking_service.py tests/test_b3_fee_linking.py
python3 -m ruff check app/modules/documents/fee_linking_service.py tests/test_b3_fee_linking.py
pytest tests/test_b3_fee_linking.py -q
./scripts/task_validate.sh BE-B-OA-FEE-DRAFT-READINESS-01
```

## Evidence Path

- `artifacts/BE-B-OA-FEE-DRAFT-READINESS-01/results.jsonl`
- `artifacts/BE-B-OA-FEE-DRAFT-READINESS-01/summary.md`
- `artifacts/BE-B-OA-FEE-DRAFT-READINESS-01/git/diff.patch`
