# MDPRE-FE-01

## Summary

- Added stable settings/masterdata landing routes for `/settings/masterdata`, `/settings/masterdata/applicants`, and `/settings/masterdata/countries`.
- Added placeholder pages for 主数据入口、申请人、国家 with Simplified Chinese copy only.
- Tightened placeholder copy to match prerequisite governance boundaries: future focus is 列表、编辑与启停用, not delete/import-export.
- Kept scope intentionally thin: no object-level CRUD UI, no selector/case linkage, no import/export.

## Verification

- `cd frontend && npm run lint -- src/router/index.ts src/modules/settings/pages/MasterDataHome.vue src/modules/settings/pages/ApplicantList.vue src/modules/settings/pages/CountryList.vue` -> pass
- `cd frontend && npm run typecheck` -> pass
- `./scripts/task_validate.sh MDPRE-FE-01` -> pass

## Evidence

- `artifacts/MDPRE-FE-01/results.jsonl`
- `artifacts/MDPRE-FE-01/commands.jsonl`
- `artifacts/MDPRE-FE-01/git/diff.patch`
- `artifacts/MDPRE-FE-01/baseline_allowlist.diff`
- `artifacts/MDPRE-FE-01/baseline_external_files.txt`
