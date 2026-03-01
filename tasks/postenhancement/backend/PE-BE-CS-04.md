# PE-BE-CS-04 — 实现顾问/检索服务费草单生成策略（固定/工时/混合）。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
- Type: `service`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：实现顾问/检索服务费草单生成策略（固定/工时/混合）。
- Allowlist:
  - `backend/app/modules/consulting/service.py`
  - `backend/app/modules/fees/service.py`
- 依赖：PE-BE-CS-01
- 验收：草单明细金额可追溯计算。
- 验证：`cd backend && pytest -q`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
