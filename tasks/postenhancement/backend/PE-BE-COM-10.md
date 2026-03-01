# PE-BE-COM-10 — `GET /commission/reports/settlement`。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
- Type: `endpoint`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：`GET /commission/reports/settlement`。
- Allowlist:
  - `backend/app/modules/commission/api.py`
  - `backend/app/modules/commission/service.py`
- 依赖：PE-BE-COM-09
- 验收：按代理人/案件/时间聚合统计。
- 验证：`cd backend && pytest -q`

---

## BE-B5 — Consulting/Search + Expense

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
