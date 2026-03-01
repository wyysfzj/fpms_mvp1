# PE-BE-COM-01 — `POST /commission/rules`。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
- Type: `endpoint`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：`POST /commission/rules`。
- Allowlist:
  - `backend/app/modules/commission/api.py`
  - `backend/app/modules/commission/service.py`
- 依赖：PE-BE-DB-06
- 验收：规则唯一性与参数合法性校验完成。
- 验证：`cd backend && pytest -q`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
