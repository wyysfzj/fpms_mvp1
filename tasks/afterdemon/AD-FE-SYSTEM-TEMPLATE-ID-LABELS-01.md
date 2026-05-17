# AD-FE-SYSTEM-TEMPLATE-ID-LABELS-01 — task template supervisor ID label cleanup

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Task Plan Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Normalize the task template page so default supervisor internal IDs are not shown as user-visible text.

This closes only:

1. `TaskTemplateList.vue` table label changes from `默认监督人ID` to `默认监督人`.
2. `TaskTemplateList.vue` table cells show `已指定` or `—` instead of rendering `default_supervisor_id`.
3. `TaskTemplateList.vue` create/edit form label and placeholder no longer mention user ID.
4. `TaskTemplateList.vue` validation error no longer mentions UUID; it uses a Chinese business/configuration message while preserving the existing validation rule.

## Explicit Non-Closure

This task does not:

- modify backend code, task template API wrappers/types, route params, permissions, response envelopes, or template persistence behavior.
- add user-name resolution, a supervisor selector, or any new API join.
- change deadline/reminder base options, reminder offset logic, template enable/disable behavior, filters, pagination, export, or print behavior.
- close raw-ID display issues outside `TaskTemplateList.vue`.

## Remaining Follow-Up Task IDs

- `PRODUCT-FE-AGENT-USER-SELECTOR-CONTRACT-01`
- `AD-FE-ANNUITY-GRANT-ID-DISPLAY-01`
- `AD-FE-COMMISSION-ID-DISPLAY-01`
- `AD-FE-CASE-FILTER-ID-LABELS-01`
- `AD-FE-CONSULTING-EXPENSE-ID-DISPLAY-01`
- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-SYSTEM-TEMPLATE-ID-LABELS-01.md`
- `frontend/src/modules/system/pages/TaskTemplateList.vue`
- `artifacts/AD-FE-SYSTEM-TEMPLATE-ID-LABELS-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-SYSTEM-TEMPLATE-ID-LABELS-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/system/pages/TaskTemplateList.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-SYSTEM-TEMPLATE-ID-LABELS-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-SYSTEM-TEMPLATE-ID-LABELS-01 ux_check /bin/zsh -lc '! rg -n "默认监督人ID|用户ID|UUID|\\{\\{ row\\.default_supervisor_id" frontend/src/modules/system/pages/TaskTemplateList.vue && rg -n "formatDefaultSupervisor|默认监督人|已指定|默认监督人配置格式不正确" frontend/src/modules/system/pages/TaskTemplateList.vue'
./scripts/evidence_run.sh AD-FE-SYSTEM-TEMPLATE-ID-LABELS-01 task_gate ./scripts/task_validate.sh AD-FE-SYSTEM-TEMPLATE-ID-LABELS-01
```

## Evidence Path

- `artifacts/AD-FE-SYSTEM-TEMPLATE-ID-LABELS-01/results.jsonl`
- `artifacts/AD-FE-SYSTEM-TEMPLATE-ID-LABELS-01/summary.md`
- `artifacts/AD-FE-SYSTEM-TEMPLATE-ID-LABELS-01/git/diff.patch`
- `artifacts/AD-FE-SYSTEM-TEMPLATE-ID-LABELS-01/baseline_allowlist.diff`
- `artifacts/AD-FE-SYSTEM-TEMPLATE-ID-LABELS-01/baseline_external_files.txt`
