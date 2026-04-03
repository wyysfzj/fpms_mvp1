# DOCWIZ-STEP4-FE-PREVIEW-01 — Step 4 费用预览前端接线

- Source: `docs/superpowers/plans/2026-04-04-docwiz-step4-preview-implementation.md`
- Type: `frontend page capability`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 在向导 Step 4 中展示费用候选预览，并承载 contract 允许的前端可调字段，保持所有修改仅存在于内存态。
- Exact closure slice:
  - 更新 `frontend/src/modules/documents/pages/DocumentWizard.vue`
  - 更新 `frontend/src/api/documents.ts`
  - 更新 `frontend/src/api/documents.types.ts`
- Explicit non-closure:
  - 不做最终 fee submit integration
  - 不做 Step 5
  - 不做 billing 页面增强
- Remaining follow-up task ids:
  - `DOCWIZ-QA-STEP4-IMPL-01`
- Allowlist:
  - `frontend/src/modules/documents/pages/DocumentWizard.vue`
  - `frontend/src/api/documents.ts`
  - `frontend/src/api/documents.types.ts`
  - `docs/superpowers/specs/2026-04-04-docwiz-step4-preview-implementation-design.md`
  - `docs/superpowers/plans/2026-04-04-docwiz-step4-preview-implementation.md`
  - `tasks/postenhancement/frontend/DOCWIZ-STEP4-FE-PREVIEW-01.md`
- Verification:
  - `cd frontend && npm run lint -- src/modules/documents/pages/DocumentWizard.vue src/api/documents.ts src/api/documents.types.ts`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh DOCWIZ-STEP4-FE-PREVIEW-01`

## Execution Checklist

- [ ] Render Step 4 fee preview rows
- [ ] Support in-memory edits for allowed fee fields
- [ ] Show no-candidate empty state
