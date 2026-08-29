# FE-CLIENT-DETAIL-BREADCRUMB-20260829-01

Status: READY / CONTRACT FROZEN
Risk-Tier: MEDIUM
Closure-Tags: ["ui"]
Task-Path: tasks/frontend/FE-CLIENT-DETAIL-BREADCRUMB-20260829-01.md
Chosen runbook: `P0-single-lane-story`

## Exact Closure Slice

On a successfully loaded customer detail route, project the loaded customer name into the
existing top-header page context so the breadcrumb has exactly three ordered segments:
`客户管理 / 客户详情 / <客户名称>`. Clear the page context when leaving the detail page.

## Explicit Non-Closure

- No URL, router, API, backend, database, customer identity, contact, seed, or permission change.
- No global `TopHeader.vue` fallback change.
- No unrelated breadcrumb, customer page, or historical UUID/English cleanup.
- No second product fix if the requested full strict journey reveals a different failure.

## Allowed Files

- `tasks/frontend/FE-CLIENT-DETAIL-BREADCRUMB-20260829-01.md`
- `frontend/src/modules/clients/pages/ClientDetail.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-client-detail-breadcrumb.spec.ts`
- `artifacts/FE-CLIENT-DETAIL-BREADCRUMB-20260829-01/**`

## Observable Acceptance

1. After `/clients/:id` loads, the breadcrumb is exactly `客户管理 / 客户详情 / <客户名称>`.
2. The breadcrumb does not render the route UUID or an extra segment.
3. Leaving the page clears its context; a second customer detail shows only the second name.
4. Focused browser regression, typecheck, scoped lint, related UI contract, scope, independent
   zero-finding review, task gate, and atomic evidence gate pass.

## Verification Commands

```bash
cd FPMS_Automation_Skeleton_Pack/playwright_ts
FPMS_BASE_URL=http://127.0.0.1:5188 npx playwright test \
  src/tests/v8-client-detail-breadcrumb.spec.ts --workers=1
```

```bash
cd frontend
npm run typecheck
npx eslint src/modules/clients/pages/ClientDetail.vue --max-warnings 0
node tests/demo-v6-ui-session-contract.mjs
```

```bash
git diff --check
```

## Requested Post-Task Integration Verification

After the atomic UI task is committed from a clean tree, run one fresh strict V6 Stage
00–11 journey and require a commit/tree-bound PASS receipt with empty network and console
error arrays. This verification does not broaden the implementation closure.

## Stop Conditions

Stop without broadening scope if the behavior requires changing routing, APIs, backend data,
customer identity, contacts, or the global header fallback, or if the strict run reaches a
different product failure.

## Remaining Follow-Up Task IDs

None.

## Evidence Path

`artifacts/FE-CLIENT-DETAIL-BREADCRUMB-20260829-01/`
