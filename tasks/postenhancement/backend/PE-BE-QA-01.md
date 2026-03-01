# PE-BE-QA-01 — 统一关键模块错误 envelope（避免裸 `HTTPException detail` 分叉）。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
- Type: `service`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：统一关键模块错误 envelope（避免裸 `HTTPException detail` 分叉）。
- Allowlist:
  - `backend/app/modules/cases/api.py`
  - `backend/app/modules/fees/api.py`
  - `backend/app/modules/billing/api.py`
- 依赖：全部功能批次完成后执行
- 验收：错误返回一致，前端解析统一。
- 验证：`cd backend && pytest -q`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
