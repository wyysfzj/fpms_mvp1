# PE-FE-CL-01 — 新增 collections API client（催款、坏账、恢复）。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_FRONTEND_TASKS.md`
- Type: `service`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：新增 collections API client（催款、坏账、恢复）。
- Allowlist:
  - `frontend/src/api/collections.ts` (new)
  - `frontend/src/api/collections.types.ts` (new)
- 依赖：PE-BE-CL-02~05
- 验收：接口类型与错误映射完整。
- 验证：`npm run lint && npm run typecheck`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Record manual verification if UI task
