# PE-FE-AN-02 — 年费任务列表页（筛选、分页、状态展示）。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_FRONTEND_TASKS.md`
- Type: `endpoint page`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：年费任务列表页（筛选、分页、状态展示）。
- Allowlist:
  - `frontend/src/modules/annuity/pages/AnnuityTaskList.vue` (new)
  - `frontend/src/router/index.ts`
- 依赖：PE-FE-AN-01
- 验收：可查询并分页展示年费任务。
- 验证：`npm run lint && npm run typecheck`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Record manual verification if UI task
