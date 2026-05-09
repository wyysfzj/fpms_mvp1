# W0-CFG-FE-SYSTEM-PARAMS-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: medium
- be_fe_coupling: medium
- evidence_cost: medium

## chosen_runbook

P0-prereq-heavy-story

## Exact Closure Slice

Close only the frontend API-client mapping gap for `TC-W0-CFG-001` and the system-params portion of `TC-W0-CFG-015`: the existing System Params page must receive `description`, `updated_at`, `created_at`, `value_type`, and `is_secret` from the real `/system/params` API instead of dropping metadata in the client mapper.

## Explicit Non-Closure Statement

This task does not modify backend endpoints, does not add routes, does not change the System Params page layout, does not implement fee/commission/template pages, does not add Playwright specs, and does not introduce new dependencies.

## Remaining Follow-Up Task IDs

- `tasks/automation/W0-CFG-PY-SYSTEM-PARAMS-01.md`
- `tasks/automation/W0-CFG-PW-CONFIG-PAGES-01.md`

## Allowed Files

- `tasks/postenhancement/frontend/W0-CFG-FE-SYSTEM-PARAMS-01.md`
- `frontend/src/api/system.ts`
- `frontend/src/api/system.types.ts`
- `artifacts/W0-CFG-FE-SYSTEM-PARAMS-01/**`

## Verification Commands

```bash
npm --prefix frontend run typecheck
npm --prefix frontend run lint
./scripts/task_validate.sh W0-CFG-FE-SYSTEM-PARAMS-01
```

## Evidence Path

- `artifacts/W0-CFG-FE-SYSTEM-PARAMS-01/results.jsonl`
- `artifacts/W0-CFG-FE-SYSTEM-PARAMS-01/summary.md`
- `artifacts/W0-CFG-FE-SYSTEM-PARAMS-01/git/diff.patch`
