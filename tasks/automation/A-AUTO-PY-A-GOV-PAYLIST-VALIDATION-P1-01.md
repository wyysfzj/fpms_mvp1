# A-AUTO-PY-A-GOV-PAYLIST-VALIDATION-P1-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Implement TC-A-018 automation for the narrowed Batch 3 official-payment validation surface: duplicate payment, invalid paid amount, and pay-list state conflict.

## Explicit Non-Closure

Do not assert deferred stale planned-pay-date warning or paid GovPayment edit/audit behavior. Do not modify backend/frontend/skeleton data.

## Remaining Follow-Up Task IDs

- PRODUCT-A-GOV-PAYMENT-PAID-EDIT-AUDIT-01

## Allowed Files

- tasks/automation/A-AUTO-PY-A-GOV-PAYLIST-VALIDATION-P1-01.md
- FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py
- FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_gov_paylist_handler.py
- artifacts/A-AUTO-PY-A-GOV-PAYLIST-VALIDATION-P1-01/**

## Verification Commands

```bash
cd FPMS_Automation_Skeleton_Pack/pytest_python
python3 -m ruff check --fix handlers/wave_a.py tests/test_a_gov_paylist_handler.py
python3 -m ruff format handlers/wave_a.py tests/test_a_gov_paylist_handler.py
python3 -m ruff check handlers/wave_a.py tests/test_a_gov_paylist_handler.py
pytest tests/test_a_gov_paylist_handler.py -q
pytest tests/test_wave_a.py -k TC-A-018 -q
```

## Evidence Path

- artifacts/A-AUTO-PY-A-GOV-PAYLIST-VALIDATION-P1-01/results.jsonl
- artifacts/A-AUTO-PY-A-GOV-PAYLIST-VALIDATION-P1-01/summary.md
- artifacts/A-AUTO-PY-A-GOV-PAYLIST-VALIDATION-P1-01/git/diff.patch
