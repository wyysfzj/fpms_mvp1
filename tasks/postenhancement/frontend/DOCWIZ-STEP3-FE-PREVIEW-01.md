# DOCWIZ-STEP3-FE-PREVIEW-01 — Step 3 任务候选预览前端承载

- Source: `docs/superpowers/plans/2026-04-03-docwiz-step3-preview-implementation.md`
- Type: `frontend page capability`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 在向导 Step 3 中显示任务候选预览、可调字段和无候选空状态。
- Exact closure slice:
  - 更新 `frontend/src/modules/documents/pages/DocumentWizard.vue`
  - 更新 `frontend/src/api/documents.ts`
  - 更新 `frontend/src/api/documents.types.ts`
- Explicit non-closure:
  - 不做最终提交 integration
  - 不做 Step 4/5
  - 不做 backend preview carrier 以外的后端改动
- Remaining follow-up task ids:
  - `DOCWIZ-QA-STEP3-IMPL-01`
- Allowlist:
  - `frontend/src/modules/documents/pages/DocumentWizard.vue`
  - `frontend/src/api/documents.ts`
  - `frontend/src/api/documents.types.ts`
  - `docs/superpowers/specs/2026-04-03-docwiz-step3-preview-implementation-design.md`
  - `docs/superpowers/plans/2026-04-03-docwiz-step3-preview-implementation.md`
  - `tasks/postenhancement/frontend/DOCWIZ-STEP3-FE-PREVIEW-01.md`
- Verification:
  - `cd frontend && npm run lint -- src/modules/documents/pages/DocumentWizard.vue src/api/documents.ts src/api/documents.types.ts`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh DOCWIZ-STEP3-FE-PREVIEW-01`

## Execution Checklist

- [ ] Add Step 3 preview state/types
- [ ] Fetch preview candidates from backend carrier
- [ ] Render preview table/cards and editable fields
- [ ] Render empty state for no applicable draft rows
- [ ] Keep Step 3 preview in-memory only
