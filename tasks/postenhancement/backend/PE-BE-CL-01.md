# PE-BE-CL-01 — 实现逾期账单筛选与催款批次生成服务。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
- Type: `service`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：实现逾期账单筛选与催款批次生成服务。
- Allowlist:
  - `backend/app/modules/collections/service.py`
- 依赖：PE-BE-DB-05
- 验收：按客户+截止日聚合，生成头/行快照。
- 验证：`cd backend && pytest -q`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
