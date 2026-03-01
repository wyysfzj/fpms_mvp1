# PE-BE-CS-05 — `POST /consulting/fee-drafts`。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
- Type: `endpoint`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：`POST /consulting/fee-drafts`。
- Allowlist:
  - `backend/app/modules/consulting/api.py`
  - `backend/app/modules/consulting/service.py`
- 依赖：PE-BE-CS-04
- 验收：可生成 CONSULT_FEE/SEARCH_FEE 草单。
- 验证：`cd backend && pytest -q`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
