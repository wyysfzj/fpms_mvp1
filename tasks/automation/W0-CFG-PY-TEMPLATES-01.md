# W0-CFG-PY-TEMPLATES-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: medium
- be_fe_coupling: medium
- evidence_cost: medium

## chosen_runbook

P0-prereq-heavy-story

## Exact Closure Slice

Implement only the pytest handler for `TC-W0-CFG-010` in `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py`.

The handler must create run-scoped template source records through the real `/templates` API using:

- `DS-CFG-TEMPLATE-DOC-OA-CN`
- `DS-CFG-TEMPLATE-BILL-CN`

It must verify list visibility by `group`, assert the returned template source identity and enabled state, and optionally assert `t_template` rows through the existing read-only DB helper.

## Explicit Non-Closure Statement

This task does not implement `TC-W0-CFG-008`, `TC-W0-CFG-009`, or `TC-W0-CFG-011`, does not change backend template APIs, does not change frontend TemplateList behavior, and does not add Playwright coverage.

## Remaining Follow-Up Task IDs

- `tasks/automation/W0-CFG-PY-TASK-DEADLINE-TEMPLATE-01.md`
- `tasks/automation/W0-CFG-PY-DOC-IMPACT-PREVIEW-01.md`
- `tasks/automation/W0-CFG-PY-LETTERHEADS-01.md`
- `tasks/automation/W0-CFG-PY-RBAC-SEED-UI-01.md`

## Allowed Files

- `tasks/automation/W0-CFG-PY-TEMPLATES-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_w0_template_source_handler.py`
- `artifacts/W0-CFG-PY-TEMPLATES-01/**`

## Verification Commands

```bash
cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check handlers/wave_w0.py tests/test_w0_template_source_handler.py
cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_w0_template_source_handler.py -q
cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_wave_w0.py -q -k TC-W0-CFG-010
./scripts/task_validate.sh W0-CFG-PY-TEMPLATES-01
```

## Evidence Path

- `artifacts/W0-CFG-PY-TEMPLATES-01/results.jsonl`
- `artifacts/W0-CFG-PY-TEMPLATES-01/summary.md`
- `artifacts/W0-CFG-PY-TEMPLATES-01/git/diff.patch`
- `artifacts/W0-CFG-PY-TEMPLATES-01/baseline_allowlist.diff`
- `artifacts/W0-CFG-PY-TEMPLATES-01/baseline_external_files.txt`
