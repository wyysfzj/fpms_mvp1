# PE-BE-AN-05 — `POST /annuity/tasks/generate-drafts`。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
- Type: `endpoint`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：`POST /annuity/tasks/generate-drafts`。
- Allowlist:
  - `backend/app/modules/annuity/api.py`
- 依赖：PE-BE-AN-04
- 验收：批量生成结果返回成功/失败明细。
- 验证：`cd backend && pytest -q`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
