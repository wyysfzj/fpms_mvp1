# PE-FE-COM-03 — 提成记录查询页（agent/case/status/date 过滤）。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_FRONTEND_TASKS.md`
- Type: `endpoint page`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：提成记录查询页（agent/case/status/date 过滤）。
- Allowlist:
  - `frontend/src/modules/commission/pages/CommissionList.vue` (new)
- 依赖：PE-FE-COM-01
- 验收：列表分页与筛选可用。
- 验证：`npm run lint && npm run typecheck`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Record manual verification if UI task
