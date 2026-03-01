# PE-FE-AN-01 — 新增 annuity API client（任务列表、指示更新、生成草单）。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_FRONTEND_TASKS.md`
- Type: `service`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：新增 annuity API client（任务列表、指示更新、生成草单）。
- Allowlist:
  - `frontend/src/api/annuity.ts` (new)
  - `frontend/src/api/annuity.types.ts` (new)
- 依赖：PE-BE-AN-02~05
- 验收：API 请求/响应类型完整，错误处理一致。
- 验证：`npm run lint && npm run typecheck`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Record manual verification if UI task
