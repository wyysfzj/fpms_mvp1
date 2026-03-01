# PE-FE-COM-01 — 新增 commission API client（规则/记录/结算/报表）。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_FRONTEND_TASKS.md`
- Type: `service`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：新增 commission API client（规则/记录/结算/报表）。
- Allowlist:
  - `frontend/src/api/commission.ts` (new)
  - `frontend/src/api/commission.types.ts` (new)
- 依赖：PE-BE-COM-01~10
- 验收：所有 commission 端点有类型封装。
- 验证：`npm run lint && npm run typecheck`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Record manual verification if UI task
