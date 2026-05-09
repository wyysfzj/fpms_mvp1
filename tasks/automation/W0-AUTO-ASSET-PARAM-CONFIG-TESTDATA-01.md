# W0-AUTO-ASSET-PARAM-CONFIG-TESTDATA-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: medium
- be_fe_coupling: medium
- evidence_cost: low

## chosen_runbook

P0-single-lane-story

## Exact Closure Slice

Create supplemental FPMS Automation Skeleton Pack test-case and seed-data assets for the application configuration parameter surface identified from `docs/FPMS SPEC 2.0.md`, SPEC 2 second-review/post ledgers, and the current implementation audit.

The assets must cover system parameters, fee rates, commission rules, task templates, document templates, template file sources, letterheads, master data, RBAC, current seed gaps, and frontend configuration visibility.

## Explicit Non-Closure Statement

This task does not implement pytest handlers, Playwright specs, backend code, frontend code, migrations, seed loaders, canonical `all_testcases.*`, canonical `by_wave/*`, canonical coverage files, or canonical wave manifests. It does not change the existing 155-case Pack baseline. It only adds supplemental structured QA assets that future atomic automation tasks may consume.

## Remaining Follow-Up Task IDs

- `W0-AUTO-PY-CFG-SYSTEM-PARAMS-01`
- `W0-AUTO-PY-CFG-FEE-RATES-01`
- `W0-AUTO-PY-CFG-COMMISSION-RULES-01`
- `W0-AUTO-PY-CFG-TEMPLATES-01`
- `W0-AUTO-PY-CFG-RBAC-SEED-AUDIT-01`

## Allowed Files

- `tasks/automation/W0-AUTO-ASSET-PARAM-CONFIG-TESTDATA-01.md`
- `FPMS_Automation_Skeleton_Pack/data/testcases/supplemental/config_parameters.yaml`
- `FPMS_Automation_Skeleton_Pack/data/testcases/supplemental/config_parameters.json`
- `FPMS_Automation_Skeleton_Pack/data/seeds/config_parameters_detailed.yaml`
- `FPMS_Automation_Skeleton_Pack/data/manifests/config_parameters_supplemental.yaml`
- `FPMS_Automation_Skeleton_Pack/data/manifests/config_parameters_supplemental.json`
- `artifacts/W0-AUTO-ASSET-PARAM-CONFIG-TESTDATA-01/**`

## Verification Commands

```bash
python3 -c '<supplemental asset structure validation>'
cd FPMS_Automation_Skeleton_Pack && python3 scripts/validate_assets.py
./scripts/task_validate.sh W0-AUTO-ASSET-PARAM-CONFIG-TESTDATA-01
```

## Evidence Path

- `artifacts/W0-AUTO-ASSET-PARAM-CONFIG-TESTDATA-01/results.jsonl`
- `artifacts/W0-AUTO-ASSET-PARAM-CONFIG-TESTDATA-01/summary.md`
- `artifacts/W0-AUTO-ASSET-PARAM-CONFIG-TESTDATA-01/git/diff.patch`
