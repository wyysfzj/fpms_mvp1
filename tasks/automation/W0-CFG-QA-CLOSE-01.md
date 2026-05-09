# W0-CFG-QA-CLOSE-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: high
- evidence_cost: high

## chosen_runbook

P0-prereq-heavy-story

## Exact Closure Slice

Create the final QA close audit for the W0 configuration-parameter canonical automation batch. The audit must map `TC-W0-CFG-001` through `TC-W0-CFG-015` to concrete pytest or Playwright evidence, confirm task gates, and run final validation commands for backend/frontend/automation assets.

## Explicit Non-Closure Statement

This task does not add new product behavior, does not add new test cases, and does not modify automation handlers beyond audit/evidence files.

## Remaining Follow-Up Task IDs

None

## Allowed Files

- `tasks/automation/W0-CFG-QA-CLOSE-01.md`
- `artifacts/W0-CFG-QA-CLOSE-01/**`

## Verification Commands

```bash
python3 FPMS_Automation_Skeleton_Pack/scripts/validate_assets.py
cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_w0_*_handler.py -q
cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_wave_w0.py -q -k TC-W0-CFG
cd backend && python3 -m ruff check app/modules/system/api.py app/modules/system/schemas.py app/modules/system/service.py tests/test_system_params.py
cd backend && pytest tests/test_system_params.py -q
npm --prefix frontend run lint
npm --prefix frontend run typecheck
npm --prefix frontend run build
cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx tsc --noEmit
./scripts/task_validate.sh W0-CFG-QA-CLOSE-01
```

## Evidence Path

- `artifacts/W0-CFG-QA-CLOSE-01/results.jsonl`
- `artifacts/W0-CFG-QA-CLOSE-01/summary.md`
- `artifacts/W0-CFG-QA-CLOSE-01/git/diff.patch`
- `artifacts/W0-CFG-QA-CLOSE-01/completion_audit.md`
- `artifacts/W0-CFG-QA-CLOSE-01/baseline_allowlist.diff`
- `artifacts/W0-CFG-QA-CLOSE-01/baseline_external_files.txt`
