# PE-BE-CL-03 — `GET /dunning`（查询与分页）。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
- Type: `endpoint`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：`GET /dunning`（查询与分页）。
- Allowlist:
  - `backend/app/modules/collections/api.py`
- 依赖：PE-BE-CL-02
- 验收：支持轮次/状态/客户过滤。
- 验证：`cd backend && pytest -q`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
