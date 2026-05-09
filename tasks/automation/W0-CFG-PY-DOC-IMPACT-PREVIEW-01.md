# W0-CFG-PY-DOC-IMPACT-PREVIEW-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: medium
- be_fe_coupling: medium
- evidence_cost: medium

## chosen_runbook

P0-prereq-heavy-story

## Exact Closure Slice

Implement only the pytest handler for `TC-W0-CFG-009` in `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py`.

The handler must create a minimal run-scoped case, create the OA reply task template and OA_IN document template preconditions, call `POST /documents/impact-preview`, and assert preview sections for status, deadline, task, fee, file-status, and confirmation requirements.

## Explicit Non-Closure Statement

This task does not create a real document, does not test reply chain closure with `reply_to_id`, does not create fee drafts, and does not change document backend or frontend behavior.

## Remaining Follow-Up Task IDs

- `tasks/automation/W0-CFG-PY-DOC-REPLY-FLOW-01.md`
- `tasks/automation/W0-CFG-QA-CLOSE-01.md`

## Allowed Files

- `tasks/automation/W0-CFG-PY-DOC-IMPACT-PREVIEW-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_w0_doc_impact_preview_handler.py`
- `artifacts/W0-CFG-PY-DOC-IMPACT-PREVIEW-01/**`

## Verification Commands

```bash
cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check --fix handlers/wave_w0.py tests/test_w0_doc_impact_preview_handler.py
cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff format handlers/wave_w0.py tests/test_w0_doc_impact_preview_handler.py
cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check handlers/wave_w0.py tests/test_w0_doc_impact_preview_handler.py
cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_w0_doc_impact_preview_handler.py -q
cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_wave_w0.py -q -k TC-W0-CFG-009
./scripts/task_validate.sh W0-CFG-PY-DOC-IMPACT-PREVIEW-01
```

## Evidence Path

- `artifacts/W0-CFG-PY-DOC-IMPACT-PREVIEW-01/results.jsonl`
- `artifacts/W0-CFG-PY-DOC-IMPACT-PREVIEW-01/summary.md`
- `artifacts/W0-CFG-PY-DOC-IMPACT-PREVIEW-01/git/diff.patch`
- `artifacts/W0-CFG-PY-DOC-IMPACT-PREVIEW-01/baseline_allowlist.diff`
- `artifacts/W0-CFG-PY-DOC-IMPACT-PREVIEW-01/baseline_external_files.txt`
