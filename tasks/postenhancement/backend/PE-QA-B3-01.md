# PE-QA-B3-01 — Batch 3 final close audit for fees / annuity / receipt scope.

- Source: `tasks/postenhancement/BATCH3_FEES_ANNUITY_MANIFEST_20260317.md`
- Type: `qa gate`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: determine whether Batch 3 can be closed after all Batch 3 implementation tasks complete.
- Scope checked:
  - all in-scope Batch 3 Cluster C4 items
  - no spillover into Batch 4 billing / collections / commission logic
- Allowlist:
  - `backend/app/modules/fees/api.py`
  - `backend/app/modules/fees/service.py`
  - `backend/app/modules/fees/schemas.py`
  - `backend/app/modules/annuity/api.py`
  - `backend/app/modules/annuity/service.py`
  - `backend/app/modules/tasks/task_generation_service.py`
  - `backend/app/modules/billing/api.py`
  - `backend/app/modules/billing/schemas.py`
  - `backend/tests/test_annuity_e2e.py`
  - `frontend/src/modules/fees/pages/FeeRates.vue`
  - `frontend/src/modules/fees/components/FeeRateForm.vue`
  - `frontend/src/modules/fees/pages/FeeDraftList.vue`
  - `frontend/src/modules/fees/pages/FeeDraftDetail.vue`
  - `frontend/src/modules/annuity/pages/AnnuityTaskList.vue`
  - `frontend/src/modules/annuity/pages/PayList.vue`
  - `frontend/src/modules/annuity/pages/GovPaymentCreate.vue`
  - `frontend/src/modules/annuity/components/InstructionDialog.vue`
  - `frontend/src/modules/cases/components/CaseReceiptsSummary.vue`
  - `frontend/src/api/fees.ts`
  - `frontend/src/api/fees.types.ts`
  - `frontend/src/api/annuity.ts`
  - `frontend/src/api/annuity.types.ts`
  - `frontend/src/api/billing.ts`
  - `frontend/src/api/billing.types.ts`
  - `docs/FPMS_Final_Enhancement_execution_summary_20260315.md`
- Verification:
  - `./scripts/task_validate.sh PE-BE-FE-03`
  - `./scripts/task_validate.sh PE-FE-FE-03`
  - `./scripts/task_validate.sh PE-BE-AN-08`
  - `./scripts/task_validate.sh PE-FE-AN-06`
  - `./scripts/task_validate.sh PE-BE-FE-04`
  - `./scripts/task_validate.sh PE-FE-FE-04`
  - `cd backend && pytest -q tests/test_annuity_e2e.py`
  - `cd frontend && npm run lint`
  - `cd frontend && npm run typecheck`
