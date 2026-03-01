# PE-FE-COM-04 — 结算批次页（创建批次、生成明细、查看报表）。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_FRONTEND_TASKS.md`
- Type: `endpoint page`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：结算批次页（创建批次、生成明细、查看报表）。
- Allowlist:
  - `frontend/src/modules/commission/pages/CommissionSettlement.vue` (new)
- 依赖：PE-FE-COM-01
- 验收：批次状态与统计结果可视化。
- 验证：`npm run lint && npm run typecheck`

---

## FE-B4 — Consulting/Search + Expense

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Record manual verification if UI task
