# CASEFLD-DB-01 — 案卷缺失字段持久化前置任务

- Source: `docs/superpowers/plans/2026-03-29-case-missing-fields-prereq.md`
- Type: `migration + model`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 为 `Case` 增加 15 个缺失字段的结构化承载，保持 SQLite-safe schema/model 对齐。
- Exact closure slice:
  - 新增 SQLite-safe migration
  - 更新 `backend/app/modules/cases/models.py`
  - 新增最小 schema/model 覆盖测试
- Explicit non-closure:
  - 不实现 CRUD contract
  - 不实现前端 create/edit/detail
  - 不实现 list/search/import/export/downstream
- Remaining follow-up task ids:
  - `CASEFLD-BE-CRUD-01`
  - `CASEFLD-FE-FORM-01`
  - `CASEFLD-FE-DETAIL-01`
  - `CASEFLD-QA-01`
- Allowlist:
  - `backend/alembic/versions/casefld_db_01_case_missing_fields.py`
  - `backend/app/modules/cases/models.py`
  - `backend/tests/test_case_missing_fields_schema.py`
- Shared ownership files:
  - `backend/app/modules/cases/models.py`
- Verification:
  - `ruff check backend/alembic/versions/casefld_db_01_case_missing_fields.py backend/app/modules/cases/models.py backend/tests/test_case_missing_fields_schema.py`
  - `cd backend && pytest -q tests/test_case_missing_fields_schema.py`
  - `cd backend && alembic upgrade head`
  - `./scripts/task_validate.sh CASEFLD-DB-01`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Write failing schema/model coverage first
- [ ] Verify RED
- [ ] Implement minimal migration/model change
- [ ] Run listed verification commands
- [ ] Generate required artifacts including dirty baseline files
