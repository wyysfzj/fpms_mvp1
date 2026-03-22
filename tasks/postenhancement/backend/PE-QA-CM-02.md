# PE-QA-CM-02 — Adjusted Batch 1A Case 域验证与关闭审计。

- Source: `docs/FPMS_Batch1_Scope_Adjustment_20260315.md`
- Type: `qa gate`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：对 adjusted `Batch 1A` 的剩余实现与 evidence normalization 做关闭审计。
- Scope checked:
  - `US-CM-03`
  - `FR-CM-03`
  - adjusted `Batch 1A` evidence package
- Allowlist:
  - `frontend/src/modules/cases/pages/CaseCreate.vue`
  - `frontend/src/modules/cases/pages/CaseEdit.vue`
  - `frontend/src/api/cases.ts`
  - `frontend/src/api/cases.types.ts`
  - `frontend/src/api/clients.ts`
  - `docs/FPMS_Batch1_Scope_Adjustment_20260315.md`
  - `docs/FPMS_Final_Enhancement_execution_summary_20260315.md`
- Audit focus:
  - allowlist compliance
  - adjusted `Batch 1A` scope only
  - no false claim on `FR-CM-05`
  - FE validation and evidence completeness
- Verification:
  - `npm run lint`
  - `npm run typecheck`
  - `./scripts/task_validate.sh PE-FE-CM-02` if evidence exists

## Execution Checklist

- [ ] Confirm adjusted Batch 1A only
- [ ] Run minimal FE verification
- [ ] Verify no scope contamination inside claimed task
- [ ] Produce PASS / FAIL / BLOCKED with evidence path
