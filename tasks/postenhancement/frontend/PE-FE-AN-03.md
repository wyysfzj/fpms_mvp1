# PE-FE-AN-03 — 客户指示编辑对话框（PAY/ABANDON/DEFER）。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_FRONTEND_TASKS.md`
- Type: `endpoint page`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：客户指示编辑对话框（PAY/ABANDON/DEFER）。
- Allowlist:
  - `frontend/src/modules/annuity/components/InstructionDialog.vue` (new)
  - `frontend/src/modules/annuity/pages/AnnuityTaskList.vue`
- 依赖：PE-FE-AN-02
- 验收：指示保存成功后列表刷新，错误提示正确。
- 验证：`npm run lint && npm run typecheck`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Record manual verification if UI task
