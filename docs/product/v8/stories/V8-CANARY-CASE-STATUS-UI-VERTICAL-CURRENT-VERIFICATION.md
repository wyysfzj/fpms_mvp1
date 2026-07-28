# Story V8-CANARY-CASE-STATUS-UI-VERTICAL-CURRENT-VERIFICATION

- Risk: `PROTECTED`
- Outcome: prove on the current lean tree that case creation initializes through the
  lifecycle seam, backend create/update reject direct legacy-status mutation, and the
  Chinese create/edit UI neither selects nor submits status.
- Change mode: current verification only; no backend or frontend product byte changes.
- Dependencies: lifecycle core evidence-kind canary `7bb54cef0d4f8d7c10c177be54b1adddc01e1d06`.
- Authority: lifecycle, API and Simplified-Chinese UI rules in
  `docs/product/v8/domain-contract.md`.

## Catalog IDs

- `FPMS-V8-LC-CASE-OPENED-20260712-01`
- `FPMS-V8-CASE-CREATE-STATUS-INPUT-GATE-20260712-01`
- `FPMS-V8-CASE-UPDATE-STATUS-INPUT-GATE-20260712-01`
- `FPMS-V8-CASE-CREATE-STATUS-UI-GATE-20260712-01`
- `FPMS-V8-CASE-EDIT-STATUS-UI-GATE-20260712-01`

## Exact paths

- `backend/app/modules/cases/lifecycle_rules.py`
- `backend/app/modules/cases/schemas.py`
- `backend/app/modules/cases/service.py`
- the three catalog primary backend tests;
- `frontend/src/api/cases.ts`
- `frontend/src/api/cases.types.ts`
- `frontend/src/modules/cases/pages/CaseCreate.vue`
- `frontend/src/modules/cases/pages/CaseEdit.vue`
- the two catalog primary Playwright tests.

## Verification

- Run the three backend tests serially and scoped Ruff.
- Start Vite from this exact worktree and run only the two mocked-API Playwright tests,
  serialized in Chromium.
- Run targeted ESLint on the exact TypeScript/Vue paths and exact diff-check.
- Independent High review and decisive rerun on the exact story commit.

## Non-goals and rollback

No fee-reduction adoption, new lifecycle event, schema/migration, API behavior change,
frontend refactor, full build, broad Playwright or Foundation claim. Rollback removes only
the story and coverage mapping; current product bytes remain unchanged.
