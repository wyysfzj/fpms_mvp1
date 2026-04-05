# GF-NOTICE-VIS-FE-01

- chosen_runbook: `P0-frontend-heavy-story`
- exact closure slice: display internal notice carrier semantics and count on the grant-fee worklist
- explicit non-closure: no real document/task creation or linkage
- allowlist:
  - `frontend/src/api/grantFees.ts`
  - `frontend/src/api/grantFees.types.ts`
  - `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`
- verification:
  - `cd frontend && npm run lint -- src/api/grantFees.ts src/api/grantFees.types.ts src/modules/grantFees/pages/GrantFeeTaskList.vue`
  - `cd frontend && npm run typecheck`
- evidence path: `artifacts/GF-NOTICE-VIS-FE-01`
- remaining follow-up task ids:
  - `GF-NOTICE-VIS-QA-01`

