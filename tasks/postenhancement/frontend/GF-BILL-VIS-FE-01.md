# GF-BILL-VIS-FE-01

- chosen_runbook: `P0-frontend-heavy-story`
- exact closure slice: render grant-fee bill visibility on the worklist and link to existing bill detail when available
- explicit non-closure: no new action entry, no bill creation, no state-machine changes
- allowlist:
  - `frontend/src/api/grantFees.ts`
  - `frontend/src/api/grantFees.types.ts`
  - `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`
- verification:
  - `cd frontend && npm run lint -- src/api/grantFees.ts src/api/grantFees.types.ts src/modules/grantFees/pages/GrantFeeTaskList.vue`
  - `cd frontend && npm run typecheck`
- evidence path: `artifacts/GF-BILL-VIS-FE-01`
- remaining follow-up task ids:
  - `GF-BILL-VIS-QA-01`

