# PE-FE-QA-01 Evidence Summary (Rework)

## Executed Task
- Task ID: `PE-FE-QA-01`
- Task File: `tasks/postenhancement/frontend/PE-FE-QA-01.md`

## Scope Compliance
- Product files modified:
  - `frontend/src/router/index.ts`
  - `frontend/src/constants/menu.ts`
- No other product source files changed in this rework.

## Reviewer Blockers Fixed
- 路由合同修复：提成记录主路径使用冻结合同 `'/commission'`。
- 兼容保留：`'/commission/records'` 通过路由别名保持向后兼容。
- 菜单权限门控修复：移除字面量权限映射 `EXTRA_PERMS`，`requiredPerms` 全部改为 `Perms.*` 常量。
- 菜单文案保持简体中文，旧菜单项结构与既有入口未回归。

## Verification Results
- `cd frontend && npm run lint` -> pass (rc=0)
- `cd frontend && npm run typecheck` -> pass (rc=0)
- `./scripts/task_validate.sh PE-FE-QA-01` -> pass (rc=0)
