# PE-BE-CS-01 — `POST /consulting/cases`（或扩展 `/cases` 的 consulting/search 验证分支）。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
- Type: `endpoint`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：`POST /consulting/cases`（或扩展 `/cases` 的 consulting/search 验证分支）。
- Allowlist:
  - `backend/app/modules/consulting/api.py`
  - `backend/app/modules/consulting/service.py`
  - `backend/app/modules/cases/service.py`
- 依赖：PE-BE-00-01
- 验收：可创建 CONSULTING/SEARCH 案件并校验专属字段。
- 验证：`cd backend && pytest -q`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
