# BE-A-COMMISSION-WAITPAY-THRESHOLD-READINESS-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Verify TC-A-024 commission wait-pay threshold readiness:

1. `wait_pay=True` commissions remain not settleable at 0%, 50%, and 90% service receipt.
2. `wait_pay=True` commissions become settleable at 100% service receipt.
3. `force_settle=True` commissions are settleable without full receipt.
4. Results are visible through `GET /commission`.

## Explicit Non-Closure

Do not implement settlement execution, frontend, skeleton data, or pytest automation handlers.

## Remaining Follow-Up Task IDs

- A-AUTO-PY-A-COMMISSION-WAITPAY-P1-01

## Allowed Files

- tasks/backend/business_logic/BE-A-COMMISSION-WAITPAY-THRESHOLD-READINESS-01.md
- backend/app/modules/commission/service.py
- backend/app/modules/commission/api.py
- backend/tests/test_commission_waitpay_threshold.py
- artifacts/BE-A-COMMISSION-WAITPAY-THRESHOLD-READINESS-01/**

## Verification Commands

```bash
cd backend
python3 -m ruff check --fix app/modules/commission/service.py app/modules/commission/api.py tests/test_commission_waitpay_threshold.py
python3 -m ruff format app/modules/commission/service.py app/modules/commission/api.py tests/test_commission_waitpay_threshold.py
python3 -m ruff check app/modules/commission/service.py app/modules/commission/api.py tests/test_commission_waitpay_threshold.py
pytest tests/test_commission_waitpay_threshold.py -q
pytest tests/test_commission_rule_seed_readiness.py -q
```

## Evidence Path

- artifacts/BE-A-COMMISSION-WAITPAY-THRESHOLD-READINESS-01/results.jsonl
- artifacts/BE-A-COMMISSION-WAITPAY-THRESHOLD-READINESS-01/summary.md
- artifacts/BE-A-COMMISSION-WAITPAY-THRESHOLD-READINESS-01/git/diff.patch
