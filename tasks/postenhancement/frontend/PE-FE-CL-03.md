# PE-FE-CL-03 — 催款列表/详情页。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_FRONTEND_TASKS.md`
- Type: `endpoint page`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：催款列表/详情页。
- Allowlist:
  - `frontend/src/modules/collections/pages/DunningList.vue` (new)
  - `frontend/src/modules/collections/pages/DunningDetail.vue` (new)
- 依赖：PE-FE-CL-02
- 验收：支持轮次/状态筛选与行明细查看。
- 验证：`npm run lint && npm run typecheck`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Record manual verification if UI task
