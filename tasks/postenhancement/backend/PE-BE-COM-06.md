# PE-BE-COM-06 — 实现 WaitPay/ForceSettle 可结算判定更新（offset/reverse 后重算）。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
- Type: `service`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：实现 WaitPay/ForceSettle 可结算判定更新（offset/reverse 后重算）。
- Allowlist:
  - `backend/app/modules/commission/service.py`
  - `backend/app/modules/billing/service.py`
- 依赖：PE-BE-COM-05
- 验收：回款比例变化后提成状态可更新。
- 验证：`cd backend && pytest -q`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
