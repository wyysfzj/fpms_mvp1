# PE-BE-QA-02 — 统一分页上限策略（`page_size le=100`）。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
- Type: `service`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：统一分页上限策略（`page_size le=100`）。
- Allowlist:
  - `backend/app/modules/*/api.py`（仅 list endpoint 参数）
- 依赖：PE-BE-QA-01
- 验收：所有列表端点具备 page_size 上限。
- 验证：`cd backend && pytest -q`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
