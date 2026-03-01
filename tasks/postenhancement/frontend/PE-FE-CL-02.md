# PE-FE-CL-02 — 催款批次创建页（截止日+客户过滤）。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_FRONTEND_TASKS.md`
- Type: `endpoint page`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：催款批次创建页（截止日+客户过滤）。
- Allowlist:
  - `frontend/src/modules/collections/pages/DunningCreate.vue` (new)
- 依赖：PE-FE-CL-01
- 验收：成功创建后跳转详情或列表。
- 验证：`npm run lint && npm run typecheck`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Record manual verification if UI task
