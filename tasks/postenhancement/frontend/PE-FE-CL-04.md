# PE-FE-CL-04 — 在账单详情页接入坏账标记/恢复动作。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_FRONTEND_TASKS.md`
- Type: `endpoint page`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：在账单详情页接入坏账标记/恢复动作。
- Allowlist:
  - `frontend/src/modules/billing/pages/BillDetail.vue`
- 依赖：PE-FE-CL-01
- 验收：按钮权限可控，状态变化可视化。
- 验证：`npm run lint && npm run typecheck`

---

## FE-B3 — Commission

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Record manual verification if UI task
