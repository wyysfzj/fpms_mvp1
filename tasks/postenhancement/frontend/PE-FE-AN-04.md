# PE-FE-AN-04 — 草单批量生成操作（选中任务→调用生成接口）。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_FRONTEND_TASKS.md`
- Type: `endpoint page`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：草单批量生成操作（选中任务→调用生成接口）。
- Allowlist:
  - `frontend/src/modules/annuity/pages/AnnuityTaskList.vue`
- 依赖：PE-FE-AN-03
- 验收：结果回执显示成功/失败明细。
- 验证：`npm run lint && npm run typecheck`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Record manual verification if UI task
