# CASEFLD-BE-CRUD-01 — 案卷缺失字段 CRUD 契约补齐

- Source: `docs/superpowers/plans/2026-03-29-case-missing-fields-prereq.md`
- Type: `api + schema + service`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 补齐 `CaseCreate / CaseUpdateFull / CaseDetail` contract 与 service 校验，使 15 字段在 create/update/detail 生效。
- Exact closure slice:
  - 更新 `backend/app/modules/cases/api.py`
  - 更新 `backend/app/modules/cases/schemas.py`
  - 更新 `backend/app/modules/cases/service.py`
  - 新增 CRUD 覆盖测试
- Explicit non-closure:
  - 不改前端页面
  - 不改列表/筛选/搜索/导入导出
  - 不做历史数据回填
- Remaining follow-up task ids:
  - `CASEFLD-FE-FORM-01`
  - `CASEFLD-FE-DETAIL-01`
  - `CASEFLD-QA-01`
- Allowlist:
  - `backend/app/modules/cases/api.py`
  - `backend/app/modules/cases/schemas.py`
  - `backend/app/modules/cases/service.py`
  - `backend/tests/test_case_missing_fields_crud.py`
- Shared ownership files:
  - `backend/app/modules/cases/api.py`
  - `backend/app/modules/cases/schemas.py`
  - `backend/app/modules/cases/service.py`
- Verification:
  - `ruff check backend/app/modules/cases/api.py backend/app/modules/cases/schemas.py backend/app/modules/cases/service.py backend/tests/test_case_missing_fields_crud.py`
  - `cd backend && pytest -q tests/test_case_missing_fields_crud.py`
  - `./scripts/task_validate.sh CASEFLD-BE-CRUD-01`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Write failing CRUD coverage first
- [ ] Verify RED
- [ ] Implement minimal contract/service change
- [ ] Run listed verification commands
- [ ] Generate required artifacts including dirty baseline files
