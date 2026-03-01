# PE-BE-AN-01 — 实现年费任务提取服务（按到期区间/状态筛选）。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
- Type: `service`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：实现年费任务提取服务（按到期区间/状态筛选）。
- Allowlist:
  - `backend/app/modules/annuity/service.py`
- 依赖：PE-BE-DB-04
- 验收：返回可分页任务列表，支持待处理筛选。
- 验证：`cd backend && pytest -q tests/test_b6_search_filters.py`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
