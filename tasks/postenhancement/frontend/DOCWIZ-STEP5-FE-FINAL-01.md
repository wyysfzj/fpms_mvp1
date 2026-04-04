# DOCWIZ-STEP5-FE-FINAL-01 — Step 5 最终提交前端接线

- Source: `docs/superpowers/plans/2026-04-04-docwiz-step5-final-submit-integration.md`
- Type: `frontend page capability`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 将 Step 5 preview 中编辑过的附件行纳入最终 payload，并随最终批量提交一并发送。
- Exact closure slice:
  - 更新 `frontend/src/modules/documents/pages/DocumentWizard.vue`
  - 更新 `frontend/src/api/documents.ts`
  - 更新 `frontend/src/api/documents.types.ts`
- Explicit non-closure:
  - 不做 Step 5 preview 扩展
  - 不做 dispatch / envelope
  - 不做单文档附件页增强
- Remaining follow-up task ids:
  - `DOCWIZ-QA-STEP5-FINAL-01`
- Allowlist:
  - `frontend/src/modules/documents/pages/DocumentWizard.vue`
  - `frontend/src/api/documents.ts`
  - `frontend/src/api/documents.types.ts`
  - `docs/superpowers/specs/2026-04-04-docwiz-step5-final-submit-integration-design.md`
  - `docs/superpowers/plans/2026-04-04-docwiz-step5-final-submit-integration.md`
  - `tasks/postenhancement/frontend/DOCWIZ-STEP5-FE-FINAL-01.md`
- Verification:
  - `cd frontend && npm run lint -- src/modules/documents/pages/DocumentWizard.vue src/api/documents.ts src/api/documents.types.ts`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh DOCWIZ-STEP5-FE-FINAL-01`

## Execution Checklist

- [ ] Extend final payload type with Step 5 attachment rows
- [ ] Serialize current Step 5 edited rows on submit
- [ ] Keep Step 5 preview state and final payload aligned
