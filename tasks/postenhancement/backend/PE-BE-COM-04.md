# PE-BE-COM-04 — 实现账单生成触发提成记录服务。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
- Type: `service`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：实现账单生成触发提成记录服务。
- Allowlist:
  - `backend/app/modules/commission/service.py`
- 依赖：PE-BE-DB-07, PE-BE-COM-01
- 验收：根据规则生成/更新 `T_Commission`。
- 验证：`cd backend && pytest -q`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
