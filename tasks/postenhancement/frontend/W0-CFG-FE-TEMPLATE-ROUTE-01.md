# W0-CFG-FE-TEMPLATE-ROUTE-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: medium
- evidence_cost: medium

## chosen_runbook

P0-frontend-heavy-story

## Exact Closure Slice

Close only the frontend route/menu gap for the existing TemplateList page: expose `frontend/src/modules/system/pages/TemplateList.vue` at `/system/templates` with menu visibility tied to the existing backend `Template.Read` permission.

## Explicit Non-Closure Statement

This task does not change TemplateList layout or behavior, does not modify backend template APIs, does not add upload functionality, and does not implement Playwright or pytest handlers.

## Remaining Follow-Up Task IDs

- `tasks/automation/W0-CFG-PY-TEMPLATES-01.md`
- `tasks/automation/W0-CFG-PY-RBAC-SEED-UI-01.md`

## Allowed Files

- `tasks/postenhancement/frontend/W0-CFG-FE-TEMPLATE-ROUTE-01.md`
- `frontend/src/router/index.ts`
- `frontend/src/constants/menu.ts`
- `frontend/src/constants/perms.ts`
- `artifacts/W0-CFG-FE-TEMPLATE-ROUTE-01/**`

## Verification Commands

```bash
npm --prefix frontend run typecheck
npm --prefix frontend run lint
./scripts/task_validate.sh W0-CFG-FE-TEMPLATE-ROUTE-01
```

## Evidence Path

- `artifacts/W0-CFG-FE-TEMPLATE-ROUTE-01/results.jsonl`
- `artifacts/W0-CFG-FE-TEMPLATE-ROUTE-01/summary.md`
- `artifacts/W0-CFG-FE-TEMPLATE-ROUTE-01/git/diff.patch`
