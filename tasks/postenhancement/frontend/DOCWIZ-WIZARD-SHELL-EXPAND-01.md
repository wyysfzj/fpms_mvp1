# DOCWIZ-WIZARD-SHELL-EXPAND-01 — 向导 5 步壳层扩展

- Source: `docs/superpowers/plans/2026-04-03-docwiz-wizard-shell-expand.md`
- Type: `frontend page capability`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 将当前 2-step 的中间文件向导扩成真正可承载 5-step flow 的前端壳层，并为 Step 3/4/5 提供占位区与正确流转。
- Exact closure slice:
  - 更新 `frontend/src/modules/documents/pages/DocumentWizard.vue`
  - 更新 `docs/superpowers/specs/2026-04-03-docwiz-wizard-shell-expand-design.md`
  - 更新 `docs/superpowers/plans/2026-04-03-docwiz-wizard-shell-expand.md`
- Explicit non-closure:
  - 不做 Step 3/4/5 业务逻辑
  - 不做 backend patch
  - 不做 API/types 变更
- Remaining follow-up task ids:
  - `DOCWIZ-QA-WIZARD-SHELL-01`
- Allowlist:
  - `frontend/src/modules/documents/pages/DocumentWizard.vue`
  - `docs/superpowers/specs/2026-04-03-docwiz-wizard-shell-expand-design.md`
  - `docs/superpowers/plans/2026-04-03-docwiz-wizard-shell-expand.md`
  - `tasks/postenhancement/frontend/DOCWIZ-WIZARD-SHELL-EXPAND-01.md`
  - `tasks/postenhancement/frontend/DOCWIZ-QA-WIZARD-SHELL-01.md`
- Verification:
  - `cd frontend && npm run lint -- src/modules/documents/pages/DocumentWizard.vue`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh DOCWIZ-WIZARD-SHELL-EXPAND-01`

## Execution Checklist

- [ ] Expand step shell from 2 to 5
- [ ] Correct title/subtitle and step labels
- [ ] Add Step 3/4/5 placeholder panels
- [ ] Preserve Step 1/2 behavior
- [ ] Keep step-specific logic deferred
