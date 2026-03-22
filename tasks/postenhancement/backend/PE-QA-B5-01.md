# PE-QA-B5-01 — Batch 5 final close audit for commission / consulting scope.

- Source: `tasks/postenhancement/BATCH5_COMMISSION_CONSULTING_MANIFEST_20260321.md`
- Type: `qa gate`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: determine whether Batch 5 can be closed after all executable Batch 5 implementation tasks complete.
- Scope checked:
  - all in-scope Batch 5 commission items
  - consulting/search blocked/deferred status
  - no spillover outside Batch 5
- Allowlist:
  - `backend/app/modules/commission/api.py`
  - `backend/app/modules/commission/service.py`
  - `backend/app/modules/consulting/api.py`
  - `backend/app/modules/consulting/service.py`
  - `backend/tests/test_commission_e2e.py`
  - `backend/tests/test_consulting_e2e.py`
  - `frontend/src/modules/commission/pages/CommissionList.vue`
  - `frontend/src/modules/commission/pages/CommissionSettlement.vue`
  - `frontend/src/modules/consulting/pages/ConsultingCaseCreate.vue`
  - `frontend/src/modules/consulting/pages/ConsultingProfitability.vue`
  - `frontend/src/api/commission.ts`
  - `frontend/src/api/commission.types.ts`
  - `frontend/src/api/consulting.ts`
  - `frontend/src/api/consulting.types.ts`
  - `docs/FPMS_Final_Enhancement_execution_summary_20260315.md`
- Verification:
  - `./scripts/task_validate.sh PE-BE-COM-01`
  - `./scripts/task_validate.sh PE-FE-COM-01`
  - `./scripts/task_validate.sh PE-BE-COM-02`
  - `./scripts/task_validate.sh PE-FE-COM-02`
  - `./scripts/task_validate.sh PE-BE-COM-03`
  - `./scripts/task_validate.sh PE-FE-COM-03`
  - `cd backend && pytest -q tests/test_commission_e2e.py tests/test_consulting_e2e.py`
  - `cd frontend && npm run lint`
  - `cd frontend && npm run typecheck`

## Exact Closure Slice

- This task closes exactly:
  - Batch 5 QA ledger and final close audit only.

## Explicit Non-Closure Statement

- This task does NOT close:
  - any remaining blocked consulting/search schema gap
  - any unexecuted follow-up task
  - any post-Batch-5 work

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

- `artifacts/PE-QA-B5-01/baseline_allowlist.diff`
- `artifacts/PE-QA-B5-01/baseline_external_files.txt`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Record baseline artifacts before auditing
- [ ] Verify all implementation tasks are already PASS
- [ ] Build item-to-slice ledger
- [ ] Run required verification
- [ ] Generate evidence artifacts
- [ ] Run task gate
- [ ] Stop after close audit
