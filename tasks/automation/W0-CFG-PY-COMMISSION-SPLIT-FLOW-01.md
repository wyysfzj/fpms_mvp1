# W0-CFG-PY-COMMISSION-SPLIT-FLOW-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: low
- evidence_cost: high

## chosen_runbook

P0-prereq-heavy-story

## Exact Closure Slice

Implement only the pytest handler for `TC-W0-CFG-006` in `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py`.

The handler must create two Agent users, a run-scoped client, a run-scoped NORMAL/INV case with 70/30 agent splits, the normal service commission rule, a manual service-fee bill, then query `/commission` and assert commission records are split into 700/300 base fees with rule-derived stage amounts.

## Explicit Non-Closure Statement

This task does not verify WaitPay/ForceSettle receipt-ratio recomputation, settlement batching, or UI display of commission results.

## Remaining Follow-Up Task IDs

- `tasks/automation/W0-CFG-PY-COMMISSION-SETTLEABILITY-FLOW-01.md`
- `tasks/automation/W0-CFG-QA-CLOSE-01.md`

## Allowed Files

- `tasks/automation/W0-CFG-PY-COMMISSION-SPLIT-FLOW-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_w0_commission_rule_handler.py`
- `artifacts/W0-CFG-PY-COMMISSION-SPLIT-FLOW-01/**`

## Verification Commands

```bash
cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check --fix handlers/wave_w0.py tests/test_w0_commission_rule_handler.py
cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff format handlers/wave_w0.py tests/test_w0_commission_rule_handler.py
cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check handlers/wave_w0.py tests/test_w0_commission_rule_handler.py
cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_w0_commission_rule_handler.py -q
cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_wave_w0.py -q -k TC-W0-CFG-006
./scripts/task_validate.sh W0-CFG-PY-COMMISSION-SPLIT-FLOW-01
```

## Evidence Path

- `artifacts/W0-CFG-PY-COMMISSION-SPLIT-FLOW-01/results.jsonl`
- `artifacts/W0-CFG-PY-COMMISSION-SPLIT-FLOW-01/summary.md`
- `artifacts/W0-CFG-PY-COMMISSION-SPLIT-FLOW-01/git/diff.patch`
- `artifacts/W0-CFG-PY-COMMISSION-SPLIT-FLOW-01/baseline_allowlist.diff`
- `artifacts/W0-CFG-PY-COMMISSION-SPLIT-FLOW-01/baseline_external_files.txt`
