# PE-FE-QA-01 — 统一新增模块路由、菜单、权限 gate（不影响旧菜单行为）。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_FRONTEND_TASKS.md`
- Type: `service`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：统一新增模块路由、菜单、权限 gate（不影响旧菜单行为）。
- Allowlist:
  - `frontend/src/router/index.ts`
  - `frontend/src/constants/menu.ts`
- 依赖：FE-B1~B4 完成
- 验收：新模块可访问，旧模块不回归。
- 验证：`npm run lint && npm run typecheck`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Record manual verification if UI task
