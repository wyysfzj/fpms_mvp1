# A-AUTO-PY-A-PAYMENT-OFFSET-VALIDATION-P1-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Implement only TC-A-022 pytest automation:

1. Negative payment amount rejected.
2. Far-future payment date rejected.
3. Duplicate client/pay number rejected.
4. Invalid and over-limit offsets rejected.
5. Received amount greater than receivable amount is recognized as prepayment.

## Explicit Non-Closure

Do not implement TC-A-016, TC-A-018, TC-A-020, TC-A-024, backend code, frontend code, skeleton data changes, or broader payment workflows.

## Remaining Follow-Up Task IDs

- A-AUTO-PY-A-BILL-INVALID-COMBOS-P1-01
- A-AUTO-PY-A-COMMISSION-WAITPAY-P1-01

## Allowed Files

- tasks/automation/A-AUTO-PY-A-PAYMENT-OFFSET-VALIDATION-P1-01.md
- FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py
- FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_payment_offset_handler.py
- artifacts/A-AUTO-PY-A-PAYMENT-OFFSET-VALIDATION-P1-01/**

## Verification Commands

```bash
cd FPMS_Automation_Skeleton_Pack/pytest_python
python3 -m ruff check --fix handlers/wave_a.py tests/test_a_payment_offset_handler.py
python3 -m ruff format handlers/wave_a.py tests/test_a_payment_offset_handler.py
python3 -m ruff check handlers/wave_a.py tests/test_a_payment_offset_handler.py
pytest tests/test_a_payment_offset_handler.py -q
pytest tests/test_wave_a.py -k TC-A-022 -q
```

Real smoke must use a fresh run id and `FPMS_DB_DSN=`.

## Evidence Path

- artifacts/A-AUTO-PY-A-PAYMENT-OFFSET-VALIDATION-P1-01/results.jsonl
- artifacts/A-AUTO-PY-A-PAYMENT-OFFSET-VALIDATION-P1-01/summary.md
- artifacts/A-AUTO-PY-A-PAYMENT-OFFSET-VALIDATION-P1-01/git/diff.patch
