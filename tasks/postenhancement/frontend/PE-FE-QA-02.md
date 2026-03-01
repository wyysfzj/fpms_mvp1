# PE-FE-QA-02 — 新增页面响应式与 a11y 最低标准修复（键盘可达、语义标签、错误提示可读）。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_FRONTEND_TASKS.md`
- Type: `service`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：新增页面响应式与 a11y 最低标准修复（键盘可达、语义标签、错误提示可读）。
- Allowlist:
  - `frontend/src/modules/**/pages/*.vue`（仅新增页面）
  - `frontend/src/styles/*.css`（必要最小变更）
- 依赖：PE-FE-QA-01
- 验收：桌面/移动端均可用，基础可访问性通过人工检查。
- 验证：`npm run lint && npm run typecheck && npm run build`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Record manual verification if UI task
