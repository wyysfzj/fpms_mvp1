# 案卷缺失字段补全 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为 `Case` 补齐 15 个缺失字段，并使其在 `create / update / detail` 三个面向生效，同时严格排除 list/search/import/export/downstream。

**Architecture:** 先解决模型承载，再补齐 CRUD contract 与 service 校验，之后分离前端 form 与 detail 两个消费面，最后用 QA ledger 收口。

**Tech Stack:** FastAPI, SQLAlchemy 2.x, Pydantic 2.x, Vue 3, TypeScript, Element Plus, SQLite

---

> Story Shape Classification
> - `shared_file_density`: `high`
> - `prereq_dependency_density`: `high`
> - `be_fe_coupling`: `chained (DB -> BE -> FE)`
> - `evidence_cost`: `high`
>
> chosen_runbook: `P0-prereq-heavy-story`

## Scope Decision

当前计划是 schema/model prerequisite 执行计划，正式判断：

- `不可直接实现，必须先新增 prerequisite task(s)`

## Batch Manifest

### CASEFLD-DB-01

**task file path**
- `tasks/postenhancement/backend/CASEFLD-DB-01.md`

**closure slice**
- 为 `Case` 增加 15 个缺失字段的结构化承载，并保持 SQLite-safe migration/model 对齐。

**explicit non-closure**
- 不改 CRUD contract。
- 不改前端。
- 不改 list/search/import/export/downstream。

**allowlist**
- `backend/alembic/versions/casefld_db_01_case_missing_fields.py`
- `backend/app/modules/cases/models.py`
- `backend/tests/test_case_missing_fields_schema.py`

**verification**
- `ruff check backend/alembic/versions/casefld_db_01_case_missing_fields.py backend/app/modules/cases/models.py backend/tests/test_case_missing_fields_schema.py`
- `cd backend && pytest -q tests/test_case_missing_fields_schema.py`
- `cd backend && alembic upgrade head`
- `./scripts/task_validate.sh CASEFLD-DB-01`

**evidence path**
- `artifacts/CASEFLD-DB-01/**`

**dependency notes**
- First prerequisite. Blocks all follow-up tasks.

### CASEFLD-BE-CRUD-01

**task file path**
- `tasks/postenhancement/backend/CASEFLD-BE-CRUD-01.md`

**closure slice**
- 补齐 `CaseCreate / CaseUpdateFull / CaseDetail` contract 与 service 校验，使 15 字段在 create/update/detail 生效。

**explicit non-closure**
- 不改前端页面。
- 不改列表、搜索、导入导出、downstream。

**allowlist**
- `backend/app/modules/cases/api.py`
- `backend/app/modules/cases/schemas.py`
- `backend/app/modules/cases/service.py`
- `backend/tests/test_case_missing_fields_crud.py`

**verification**
- `ruff check backend/app/modules/cases/api.py backend/app/modules/cases/schemas.py backend/app/modules/cases/service.py backend/tests/test_case_missing_fields_crud.py`
- `cd backend && pytest -q tests/test_case_missing_fields_crud.py`
- `./scripts/task_validate.sh CASEFLD-BE-CRUD-01`

**evidence path**
- `artifacts/CASEFLD-BE-CRUD-01/**`

**dependency notes**
- Depends on `CASEFLD-DB-01`.

### CASEFLD-FE-FORM-01

**task file path**
- `tasks/postenhancement/frontend/CASEFLD-FE-FORM-01.md`

**closure slice**
- 在 `CaseCreate.vue` 与 `CaseEdit.vue` 补齐 15 字段的录入/编辑 UI，并对齐 cases API/types contract。

**explicit non-closure**
- 不改详情页。
- 不改列表页。
- 不做搜索筛选。

**allowlist**
- `frontend/src/api/cases.ts`
- `frontend/src/api/cases.types.ts`
- `frontend/src/modules/cases/pages/CaseCreate.vue`
- `frontend/src/modules/cases/pages/CaseEdit.vue`

**verification**
- `cd frontend && npm run lint -- src/api/cases.ts src/api/cases.types.ts src/modules/cases/pages/CaseCreate.vue src/modules/cases/pages/CaseEdit.vue`
- `cd frontend && npm run typecheck`
- `./scripts/task_validate.sh CASEFLD-FE-FORM-01`

**evidence path**
- `artifacts/CASEFLD-FE-FORM-01/**`

**dependency notes**
- Depends on `CASEFLD-BE-CRUD-01`.

### CASEFLD-FE-DETAIL-01

**task file path**
- `tasks/postenhancement/frontend/CASEFLD-FE-DETAIL-01.md`

**closure slice**
- 在 `CaseDetail.vue` 展示这 15 个字段。

**explicit non-closure**
- 不改 create/edit。
- 不改列表页。
- 不加筛选/搜索。

**allowlist**
- `frontend/src/api/cases.ts`
- `frontend/src/api/cases.types.ts`
- `frontend/src/modules/cases/pages/CaseDetail.vue`

**verification**
- `cd frontend && npm run lint -- src/api/cases.ts src/api/cases.types.ts src/modules/cases/pages/CaseDetail.vue`
- `cd frontend && npm run typecheck`
- `./scripts/task_validate.sh CASEFLD-FE-DETAIL-01`

**evidence path**
- `artifacts/CASEFLD-FE-DETAIL-01/**`

**dependency notes**
- Depends on `CASEFLD-BE-CRUD-01`.
- Serialized with `CASEFLD-FE-FORM-01` on `cases.ts` / `cases.types.ts`.

### CASEFLD-QA-01

**task file path**
- `tasks/postenhancement/backend/CASEFLD-QA-01.md`

**closure slice**
- item-to-slice ledger、evidence audit、故事级收口。

**explicit non-closure**
- 不改产品代码。

**allowlist**
- `artifacts/CASEFLD-QA-01/**`

**verification**
- `./scripts/task_validate.sh CASEFLD-DB-01`
- `./scripts/task_validate.sh CASEFLD-BE-CRUD-01`
- `./scripts/task_validate.sh CASEFLD-FE-FORM-01`
- `./scripts/task_validate.sh CASEFLD-FE-DETAIL-01`
- `./scripts/task_validate.sh CASEFLD-QA-01`

**evidence path**
- `artifacts/CASEFLD-QA-01/**`

**dependency notes**
- Final close task only after all prior tasks are PASS.

## Wave Order

1. `CASEFLD-DB-01`
2. `CASEFLD-BE-CRUD-01`
3. `CASEFLD-FE-FORM-01`
4. `CASEFLD-FE-DETAIL-01`
5. `CASEFLD-QA-01`

## Serialized Ownership Decisions

- `backend/app/modules/cases/models.py` is exclusive to `CASEFLD-DB-01`.
- `backend/app/modules/cases/api.py`, `schemas.py`, `service.py` are exclusive to `CASEFLD-BE-CRUD-01`.
- `frontend/src/api/cases.ts` and `frontend/src/api/cases.types.ts` require serialized ownership between `CASEFLD-FE-FORM-01` and `CASEFLD-FE-DETAIL-01`.
- `CaseCreate.vue` / `CaseEdit.vue` are exclusive to `CASEFLD-FE-FORM-01`.
- `CaseDetail.vue` is exclusive to `CASEFLD-FE-DETAIL-01`.
