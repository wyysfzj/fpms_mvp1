# W0-CFG-PY-LETTERHEADS-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: medium
- be_fe_coupling: low
- evidence_cost: medium

## chosen_runbook

P0-prereq-heavy-story

## Exact Closure Slice

Implement only the pytest handler for `TC-W0-CFG-011` in `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py`.

The handler must create CN and EN default letterheads through `/letterheads`, create a second CN default letterhead, list CN letterheads, and assert only the replacement CN letterhead remains default for that locale.

## Explicit Non-Closure Statement

This task does not test bill print rendering context, does not change backend letterhead logic, does not change frontend letterhead UI, and does not implement any other W0-CFG handler.

## Remaining Follow-Up Task IDs

- `tasks/automation/W0-CFG-PY-DOC-IMPACT-PREVIEW-01.md`
- `tasks/automation/W0-CFG-PY-RBAC-CONFIG-ENDPOINTS-01.md`
- `tasks/automation/W0-CFG-QA-CLOSE-01.md`

## Allowed Files

- `tasks/automation/W0-CFG-PY-LETTERHEADS-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_w0_letterhead_handler.py`
- `artifacts/W0-CFG-PY-LETTERHEADS-01/**`

## Verification Commands

```bash
cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check --fix handlers/wave_w0.py tests/test_w0_letterhead_handler.py
cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff format handlers/wave_w0.py tests/test_w0_letterhead_handler.py
cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check handlers/wave_w0.py tests/test_w0_letterhead_handler.py
cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_w0_letterhead_handler.py -q
cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_wave_w0.py -q -k TC-W0-CFG-011
./scripts/task_validate.sh W0-CFG-PY-LETTERHEADS-01
```

## Evidence Path

- `artifacts/W0-CFG-PY-LETTERHEADS-01/results.jsonl`
- `artifacts/W0-CFG-PY-LETTERHEADS-01/summary.md`
- `artifacts/W0-CFG-PY-LETTERHEADS-01/git/diff.patch`
- `artifacts/W0-CFG-PY-LETTERHEADS-01/baseline_allowlist.diff`
- `artifacts/W0-CFG-PY-LETTERHEADS-01/baseline_external_files.txt`
