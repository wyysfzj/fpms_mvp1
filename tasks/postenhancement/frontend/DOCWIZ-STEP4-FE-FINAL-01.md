# DOCWIZ-STEP4-FE-FINAL-01 — Step 4 最终提交前端接线

- Source: `docs/superpowers/plans/2026-04-04-docwiz-step4-final-submit-integration.md`
- Type: `frontend page capability`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 将 Step 4 preview 中编辑过的费用行纳入最终 payload，并随最终批量提交一并发送。
- Exact closure slice:
  - 更新 `frontend/src/modules/documents/pages/DocumentWizard.vue`
  - 更新 `frontend/src/api/documents.ts`
  - 更新 `frontend/src/api/documents.types.ts`
- Explicit non-closure:
  - 不做 Step 5
  - 不做 billing 页面增强
  - 不做新的 preview 功能
- Remaining follow-up task ids:
  - `DOCWIZ-QA-STEP4-FINAL-01`
- Allowlist:
  - `frontend/src/modules/documents/pages/DocumentWizard.vue`
  - `frontend/src/api/documents.ts`
  - `frontend/src/api/documents.types.ts`
  - `docs/superpowers/specs/2026-04-04-docwiz-step4-final-submit-integration-design.md`
  - `docs/superpowers/plans/2026-04-04-docwiz-step4-final-submit-integration.md`
  - `tasks/postenhancement/frontend/DOCWIZ-STEP4-FE-FINAL-01.md`
- Verification:
  - `cd frontend && npm run lint -- src/modules/documents/pages/DocumentWizard.vue src/api/documents.ts src/api/documents.types.ts`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh DOCWIZ-STEP4-FE-FINAL-01`

## Execution Checklist

- [ ] Extend final payload type with Step 4 fee rows
- [ ] Serialize current Step 4 edited rows on submit
- [ ] Keep Step 4 preview state and final payload aligned
