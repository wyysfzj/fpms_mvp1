# PE-BE-CS-06 — 顾问/检索账单生成时接入提成规则匹配。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
- Type: `service`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：顾问/检索账单生成时接入提成规则匹配。
- Allowlist:
  - `backend/app/modules/consulting/service.py`
  - `backend/app/modules/commission/service.py`
  - `backend/app/modules/billing/service.py`
- 依赖：PE-BE-COM-05, PE-BE-CS-05
- 验收：顾问/检索项目可写提成记录并进入结算候选。
- 验证：`cd backend && pytest -q`

---

## BE-B6 — 一致性硬化与测试补齐

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
