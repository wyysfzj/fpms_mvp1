# PE-BE-AN-04 — 实现“年费任务→费用草单”生成服务。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
- Type: `service`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：实现“年费任务→费用草单”生成服务。
- Allowlist:
  - `backend/app/modules/annuity/service.py`
- 依赖：PE-BE-AN-03
- 验收：支持 PayNextYear/草单幂等控制。
- 验证：`cd backend && pytest -q`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
