# AD-FE-CASE-ROUTE-NO-DISPLAY-01 - case route visible case number cleanup

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Task Plan Classification

- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Make the case detail and case edit browser URL display a readable business case number instead of a raw internal UUID.

This closes only:

1. Add frontend routes for case detail and edit by business case number.
2. Keep legacy UUID routes as internal-compatible fallback routes.
3. When a legacy UUID detail/edit route is opened, load the case through the existing API and replace the visible URL with the case-number route after the case number is known.
4. Case detail/edit API calls continue to use the internal UUID once resolved.
5. The case list `查看` action uses the case-number detail route.

## Explicit Non-Closure

This task does not:

- modify backend code, database schema, permissions, response envelopes, or API route contracts.
- change document/task/fee/billing/annuity/commission pages that link to cases; those legacy links are only handled by the case detail fallback redirect.
- change client routes, bill routes, document routes, task routes, or any non-case UUID URL behavior.
- change case create/edit business fields, validation rules, status transitions, save payloads, or UI layout.
- remove UUIDs from API payloads, logs, dev tooling, or internal query parameters.

## Remaining Follow-Up Task IDs

- `AD-FE-CLIENT-ROUTE-DISPLAY-01`
- `AD-FE-CROSS-MODULE-CASE-LINK-BUSINESS-ROUTES-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-CASE-ROUTE-NO-DISPLAY-01.md`
- `frontend/src/router/index.ts`
- `frontend/src/api/cases.ts`
- `frontend/src/api/cases.types.ts`
- `frontend/src/modules/cases/pages/CaseList.vue`
- `frontend/src/modules/cases/pages/CaseDetail.vue`
- `frontend/src/modules/cases/pages/CaseEdit.vue`
- `artifacts/AD-FE-CASE-ROUTE-NO-DISPLAY-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-CASE-ROUTE-NO-DISPLAY-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/router/index.ts src/api/cases.ts src/api/cases.types.ts src/modules/cases/pages/CaseList.vue src/modules/cases/pages/CaseDetail.vue src/modules/cases/pages/CaseEdit.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-CASE-ROUTE-NO-DISPLAY-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-CASE-ROUTE-NO-DISPLAY-01 ux_check /bin/zsh -lc 'rg -n "case_detail_by_no|case_edit_by_no|getCaseByCaseNo|route.params.caseNo|router.replace" frontend/src/router/index.ts frontend/src/api/cases.ts frontend/src/modules/cases/pages/CaseList.vue frontend/src/modules/cases/pages/CaseDetail.vue frontend/src/modules/cases/pages/CaseEdit.vue && ! rg -n "router.push\\(`/cases/\\$\\{row\\.id\\}`\\)|router.push\\(`/cases/\\$\\{id\\}`\\)" frontend/src/modules/cases/pages/CaseList.vue frontend/src/modules/cases/pages/CaseDetail.vue frontend/src/modules/cases/pages/CaseEdit.vue'
./scripts/evidence_run.sh AD-FE-CASE-ROUTE-NO-DISPLAY-01 task_gate ./scripts/task_validate.sh AD-FE-CASE-ROUTE-NO-DISPLAY-01
```

## Evidence Path

- `artifacts/AD-FE-CASE-ROUTE-NO-DISPLAY-01/results.jsonl`
- `artifacts/AD-FE-CASE-ROUTE-NO-DISPLAY-01/summary.md`
- `artifacts/AD-FE-CASE-ROUTE-NO-DISPLAY-01/git/diff.patch`
- `artifacts/AD-FE-CASE-ROUTE-NO-DISPLAY-01/baseline_allowlist.diff`
- `artifacts/AD-FE-CASE-ROUTE-NO-DISPLAY-01/baseline_external_files.txt`
