# DOCWIZ-STEP3-FE-FINAL-01 — Step 3 最终提交前端接入

- Source: `docs/superpowers/plans/2026-04-03-docwiz-step3-final-submit-integration.md`
- Type: `frontend page capability`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 将 Step 3 preview 中编辑过的任务行纳入最终 payload，并随最终批量提交一并发送。
- Exact closure slice:
  - 更新 `frontend/src/modules/documents/pages/DocumentWizard.vue`
  - 更新 `frontend/src/api/documents.ts`
  - 更新 `frontend/src/api/documents.types.ts`
- Explicit non-closure:
  - 不做 Step 4/5
  - 不做新的 preview 功能
  - 不做 backend 改动
- Remaining follow-up task ids:
  - `DOCWIZ-QA-STEP3-FINAL-01`
- Allowlist:
  - `frontend/src/modules/documents/pages/DocumentWizard.vue`
  - `frontend/src/api/documents.ts`
  - `frontend/src/api/documents.types.ts`
  - `docs/superpowers/specs/2026-04-03-docwiz-step3-final-submit-integration-design.md`
  - `docs/superpowers/plans/2026-04-03-docwiz-step3-final-submit-integration.md`
  - `tasks/postenhancement/frontend/DOCWIZ-STEP3-FE-FINAL-01.md`
- Verification:
  - `cd frontend && npm run lint -- src/modules/documents/pages/DocumentWizard.vue src/api/documents.ts src/api/documents.types.ts`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh DOCWIZ-STEP3-FE-FINAL-01`

## Execution Checklist

- [ ] Extend final payload type with Step 3 task rows
- [ ] Serialize current Step 3 edited rows on submit
- [ ] Keep preview state and final payload aligned
