# W0-CFG-PY-FEE-CALC-MODES-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: medium
- be_fe_coupling: low
- evidence_cost: medium

## chosen_runbook

P0-prereq-heavy-story

## Exact Closure Slice

Implement only the pytest handler for `TC-W0-CFG-004` in `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py`.

The handler must create run-scoped fee rates for the supported/spec calc-mode coverage seeds and assert that `calc_mode`, `calc_params`, and standard fee-rate metadata are preserved by the real `/fees/rates` API:

- `DS-CFG-RATE-APPLY-BASE-GOV`
- `DS-CFG-RATE-APPLY-EXCESS-CLAIM`
- `DS-CFG-RATE-ANNUITY-GOV-Y1`
- `DS-CFG-RATE-BY-PAGES`
- `DS-CFG-RATE-COMPOSITE`

## Explicit Non-Closure Statement

This task does not implement or prove downstream fee amount calculation for BY_YEAR, BY_PAGES, or COMPOSITE. It records metadata persistence coverage only and leaves full business calculation verification to a later service-flow task.

## Remaining Follow-Up Task IDs

- `tasks/automation/W0-CFG-PY-FEE-CALC-SERVICE-FLOW-01.md`
- `tasks/automation/W0-CFG-QA-CLOSE-01.md`

## Allowed Files

- `tasks/automation/W0-CFG-PY-FEE-CALC-MODES-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_w0_fee_rate_handler.py`
- `artifacts/W0-CFG-PY-FEE-CALC-MODES-01/**`

## Verification Commands

```bash
cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check --fix handlers/wave_w0.py tests/test_w0_fee_rate_handler.py
cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff format handlers/wave_w0.py tests/test_w0_fee_rate_handler.py
cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check handlers/wave_w0.py tests/test_w0_fee_rate_handler.py
cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_w0_fee_rate_handler.py -q
cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_wave_w0.py -q -k TC-W0-CFG-004
./scripts/task_validate.sh W0-CFG-PY-FEE-CALC-MODES-01
```

## Evidence Path

- `artifacts/W0-CFG-PY-FEE-CALC-MODES-01/results.jsonl`
- `artifacts/W0-CFG-PY-FEE-CALC-MODES-01/summary.md`
- `artifacts/W0-CFG-PY-FEE-CALC-MODES-01/git/diff.patch`
- `artifacts/W0-CFG-PY-FEE-CALC-MODES-01/baseline_allowlist.diff`
- `artifacts/W0-CFG-PY-FEE-CALC-MODES-01/baseline_external_files.txt`
