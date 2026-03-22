# PE-FE-CM-02 — Case 参与方补齐：申请人主数据选择、快速新建、回填与 FE 闭环证据。

- Source: `docs/FPMS_Batch1_Scope_Adjustment_20260315.md`
- Type: `page + api client`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：补齐 adjusted `Batch 1A` 中仍可实现的 `US-CM-03 / FR-CM-03` 前端部分，并收口 FE evidence。
- Covered items:
  - `US-CM-03`
  - `FR-CM-03`
- Allowlist:
  - `frontend/src/modules/cases/pages/CaseCreate.vue`
  - `frontend/src/modules/cases/pages/CaseEdit.vue`
  - `frontend/src/api/cases.ts`
  - `frontend/src/api/cases.types.ts`
  - `frontend/src/api/clients.ts`
- Shared ownership files:
  - `frontend/src/modules/cases/pages/CaseCreate.vue`
  - `frontend/src/modules/cases/pages/CaseEdit.vue`
  - `frontend/src/api/cases.ts`
  - `frontend/src/api/cases.types.ts`
  - `frontend/src/api/clients.ts`
- Out of scope:
  - `FR-CM-05` blocked attributes
  - foreign-agent dedicated masterdata implementation
  - schema / migration / backend model changes
  - Batch 2+ scope
- Acceptance:
  - case create/edit pages support applicant row maintenance on current case form
  - case create/edit pages support selecting existing client masterdata as applicant source
  - case create/edit pages support quick-create client -> applicant backfill
  - create/update payloads persist applicants through existing case API
  - evidence summary clearly states what remains blocked
- Verification:
  - `npm run lint`
  - `npm run typecheck`
  - manual flow notes for case create / edit applicant backfill

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Add minimal FE-first failing coverage note or validation-first step
- [ ] Implement minimal applicant management changes only
- [ ] Run listed verification commands
- [ ] Update evidence artifacts
