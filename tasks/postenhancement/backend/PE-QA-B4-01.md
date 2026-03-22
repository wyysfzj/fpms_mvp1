# PE-QA-B4-01 — Batch 4 final close audit for billing / collections scope.

- Source: `tasks/postenhancement/BATCH4_BILLING_COLLECTIONS_MANIFEST_20260318.md`
- Type: `qa gate`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: determine whether Batch 4 can be closed after all Batch 4 implementation tasks complete.
- Scope checked:
  - all in-scope Batch 4 Cluster C5 items
  - no spillover into Batch 5 commission / consulting logic
- Allowlist:
  - `backend/app/modules/billing/api.py`
  - `backend/app/modules/billing/service.py`
  - `backend/app/modules/billing/schemas.py`
  - `backend/app/modules/collections/api.py`
  - `backend/app/modules/collections/service.py`
  - `backend/tests/test_b5_billing_polish.py`
  - `backend/tests/test_collections_e2e.py`
  - `frontend/src/modules/billing/pages/BillCreate.vue`
  - `frontend/src/modules/billing/pages/PaymentCreate.vue`
  - `frontend/src/modules/billing/pages/PaymentList.vue`
  - `frontend/src/modules/collections/pages/DunningList.vue`
  - `frontend/src/modules/collections/pages/DunningDetail.vue`
  - `frontend/src/modules/collections/pages/DunningCreate.vue`
  - `frontend/src/api/billing.ts`
  - `frontend/src/api/billing.types.ts`
  - `frontend/src/api/collections.ts`
  - `frontend/src/api/collections.types.ts`
  - `docs/FPMS_Final_Enhancement_execution_summary_20260315.md`
- Verification:
  - `./scripts/task_validate.sh PE-BE-BL-01`
  - `./scripts/task_validate.sh PE-FE-BL-01`
  - `./scripts/task_validate.sh PE-BE-BL-02`
  - `./scripts/task_validate.sh PE-FE-BL-02`
  - `./scripts/task_validate.sh PE-BE-BL-03`
  - `./scripts/task_validate.sh PE-FE-BL-03`
  - `cd backend && pytest -q tests/test_b5_billing_polish.py tests/test_collections_e2e.py`
  - `cd frontend && npm run lint`
  - `cd frontend && npm run typecheck`

## Exact Closure Slice

- This task closes exactly:
  - Batch 4 QA ledger and final close audit only.

## Explicit Non-Closure Statement

- This task does NOT close:
  - any remaining implementation gap
  - any Batch 5 commission / consulting behavior

## Remaining Follow-up Task IDs

- `None`

## Done Definition

- [ ] item-to-slice ledger exists
- [ ] every in-scope item has a close decision
- [ ] no unresolved residual gap remains for a `complete` claim
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Dirty Baseline Artifacts

- `artifacts/PE-QA-B4-01/baseline_allowlist.diff`
- `artifacts/PE-QA-B4-01/baseline_external_files.txt`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Record baseline artifacts before auditing
- [ ] Verify all implementation tasks are already PASS
- [ ] Build item-to-slice ledger
- [ ] Run required verification
- [ ] Generate evidence artifacts
- [ ] Run task gate
- [ ] Stop after close audit
