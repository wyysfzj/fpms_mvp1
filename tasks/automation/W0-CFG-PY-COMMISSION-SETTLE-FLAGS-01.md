# W0-CFG-PY-COMMISSION-SETTLE-FLAGS-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: medium
- be_fe_coupling: low
- evidence_cost: medium

## chosen_runbook

P0-prereq-heavy-story

## Exact Closure Slice

Implement only the pytest handler for `TC-W0-CFG-007` in `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py`.

The handler must create and query the WaitPay and ForceSettle commission rules using:

- `DS-CFG-COM-NORMAL-WAITPAY`
- `DS-CFG-COM-NORMAL-FORCE`

It must assert the `wait_pay`, `force_settle`, and `enabled` flags are preserved by the real `/commission/rules` API.

## Explicit Non-Closure Statement

This task does not register payments, recompute commission settleability by receipt ratio, or test settlement creation.

## Remaining Follow-Up Task IDs

- `tasks/automation/W0-CFG-PY-COMMISSION-SETTLEABILITY-FLOW-01.md`
- `tasks/automation/W0-CFG-QA-CLOSE-01.md`

## Allowed Files

- `tasks/automation/W0-CFG-PY-COMMISSION-SETTLE-FLAGS-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_w0_commission_rule_handler.py`
- `artifacts/W0-CFG-PY-COMMISSION-SETTLE-FLAGS-01/**`

## Verification Commands

```bash
cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check --fix handlers/wave_w0.py tests/test_w0_commission_rule_handler.py
cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff format handlers/wave_w0.py tests/test_w0_commission_rule_handler.py
cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check handlers/wave_w0.py tests/test_w0_commission_rule_handler.py
cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_w0_commission_rule_handler.py -q
cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_wave_w0.py -q -k TC-W0-CFG-007
./scripts/task_validate.sh W0-CFG-PY-COMMISSION-SETTLE-FLAGS-01
```

## Evidence Path

- `artifacts/W0-CFG-PY-COMMISSION-SETTLE-FLAGS-01/results.jsonl`
- `artifacts/W0-CFG-PY-COMMISSION-SETTLE-FLAGS-01/summary.md`
- `artifacts/W0-CFG-PY-COMMISSION-SETTLE-FLAGS-01/git/diff.patch`
- `artifacts/W0-CFG-PY-COMMISSION-SETTLE-FLAGS-01/baseline_allowlist.diff`
- `artifacts/W0-CFG-PY-COMMISSION-SETTLE-FLAGS-01/baseline_external_files.txt`
