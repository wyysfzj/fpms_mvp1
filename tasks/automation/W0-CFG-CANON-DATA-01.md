# W0-CFG-CANON-DATA-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: medium
- be_fe_coupling: low
- evidence_cost: medium

## chosen_runbook

P0-prereq-heavy-story

## Exact Closure Slice

Promote the 15 supplemental parameter-configuration test cases from `FPMS_Automation_Skeleton_Pack/data/testcases/supplemental/config_parameters.yaml` into the canonical W0 automation assets.

This task only updates structured Pack assets and asset-count verifiers:

- Append the promoted cases to canonical `by_wave/w0.*`.
- Append the promoted cases to canonical `all_testcases.*`.
- Update W0 counts and total suite counts from 155 to 170.
- Update P0/P1 priority indexes, P0 smoke, and full regression manifests.
- Update asset integrity checks that intentionally assert the canonical case count.

## Explicit Non-Closure Statement

This task does not implement pytest handlers, Playwright handlers, backend code, frontend code, migrations, seed scripts, API behavior, UI behavior, or real business configuration. It does not remove the supplemental source files. It does not mark any promoted case as automated; promoted cases remain `status: supplemental_ready` until dedicated handler tasks implement them.

## Remaining Follow-Up Task IDs

- `W0-CFG-PY-SYSTEM-PARAMS-01`
- `W0-CFG-PY-FEE-RATES-01`
- `W0-CFG-PY-COMMISSION-01`
- `W0-CFG-PY-TEMPLATES-01`
- `W0-CFG-PY-RBAC-SEED-UI-01`
- `W0-CFG-PW-CONFIG-PAGES-01`
- `W0-CFG-BE-GAP-CLOSE-01`
- `W0-CFG-FE-GAP-CLOSE-01`
- `W0-CFG-MIGRATION-DECISION-01`
- `W0-CFG-QA-CLOSE-01`

## Allowed Files

- `tasks/automation/W0-CFG-CANON-DATA-01.md`
- `FPMS_Automation_Skeleton_Pack/data/testcases/by_wave/w0.yaml`
- `FPMS_Automation_Skeleton_Pack/data/testcases/by_wave/w0.json`
- `FPMS_Automation_Skeleton_Pack/data/testcases/all_testcases.yaml`
- `FPMS_Automation_Skeleton_Pack/data/testcases/all_testcases.json`
- `FPMS_Automation_Skeleton_Pack/data/manifests/wave_manifest.yaml`
- `FPMS_Automation_Skeleton_Pack/data/manifests/wave_manifest.json`
- `FPMS_Automation_Skeleton_Pack/data/manifests/priority_index.yaml`
- `FPMS_Automation_Skeleton_Pack/data/manifests/priority_index.json`
- `FPMS_Automation_Skeleton_Pack/data/manifests/smoke_p0.yaml`
- `FPMS_Automation_Skeleton_Pack/data/manifests/smoke_p0.json`
- `FPMS_Automation_Skeleton_Pack/data/manifests/full_regression.yaml`
- `FPMS_Automation_Skeleton_Pack/data/manifests/full_regression.json`
- `FPMS_Automation_Skeleton_Pack/scripts/validate_assets.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_asset_integrity.py`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/asset-integrity.spec.ts`
- `FPMS_Automation_Skeleton_Pack/README.md`
- `artifacts/W0-CFG-CANON-DATA-01/**`

## Verification Commands

```bash
cd FPMS_Automation_Skeleton_Pack && python3 scripts/validate_assets.py
cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_asset_integrity.py tests/test_seed_data.py -q
cd FPMS_Automation_Skeleton_Pack/playwright_ts && npm test -- --grep "asset integrity"
./scripts/task_validate.sh W0-CFG-CANON-DATA-01
```

## Evidence Path

- `artifacts/W0-CFG-CANON-DATA-01/results.jsonl`
- `artifacts/W0-CFG-CANON-DATA-01/summary.md`
- `artifacts/W0-CFG-CANON-DATA-01/git/diff.patch`
