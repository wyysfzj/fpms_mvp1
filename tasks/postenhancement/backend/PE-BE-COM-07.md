# PE-BE-COM-07 — `GET /commission`（提成记录查询）。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
- Type: `endpoint`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：`GET /commission`（提成记录查询）。
- Allowlist:
  - `backend/app/modules/commission/api.py`
- 依赖：PE-BE-COM-06
- 验收：支持 agent/case/status/date 过滤。
- 验证：`cd backend && pytest -q`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
