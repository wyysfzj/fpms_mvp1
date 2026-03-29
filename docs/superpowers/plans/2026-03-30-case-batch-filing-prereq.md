# Case Batch Filing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 `US-CM-05 / FR-CM-07` 建立最小可用的案件递交批处理 workflow：批量筛选 `NOT_FILED` 案件，批量设置 `submitted_date` 和 `apply_exam_now`，并将状态更新为 `WAITING_RECEIPT`。

**Architecture:** 先补 `Case.submitted_date` 的模型承载，再补专用批量查询与批量动作后端 contract，最后落地一个独立的前端批件递交页面。第一版不进入 documents/tasks 联动，不扩展到通用列表/导出。

**Tech Stack:** FastAPI, SQLAlchemy, Alembic, Vue 3, Element Plus, SQLite

---

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `chained (DB -> BE -> FE)`
- `evidence_cost`: `high`

## chosen_runbook

- `P0-prereq-heavy-story`

## Batch Manifest

### Task 1: CASEBF-DB-01

**Files:**
- Create: `backend/alembic/versions/casebf_db_01_case_submitted_date.py`
- Modify: `backend/app/modules/cases/models.py`
- Test: `backend/tests/test_case_batch_filing_schema.py`
- Task file: `tasks/postenhancement/backend/CASEBF-DB-01.md`

- [ ] Step 1: 写 `submitted_date` 模型与 migration 的失败测试
- [ ] Step 2: 运行 `cd backend && pytest -q tests/test_case_batch_filing_schema.py`
- [ ] Step 3: 实现 `Case.submitted_date` 与 SQLite-safe migration
- [ ] Step 4: 运行：
  - `ruff check backend/alembic/versions/casebf_db_01_case_submitted_date.py backend/app/modules/cases/models.py backend/tests/test_case_batch_filing_schema.py`
  - `cd backend && pytest -q tests/test_case_batch_filing_schema.py`
  - `cd backend && alembic upgrade head`
- [ ] Step 5: 生成 evidence 并收口

**closure slice**
- 只为 `Case` 新增 `submitted_date` 结构化承载

**explicit non-closure**
- 不改批量查询
- 不改批量动作
- 不改前端
- 不改 documents/tasks

**allowlist**
- `backend/alembic/versions/casebf_db_01_case_submitted_date.py`
- `backend/app/modules/cases/models.py`
- `backend/tests/test_case_batch_filing_schema.py`

**verification**
- `ruff check backend/alembic/versions/casebf_db_01_case_submitted_date.py backend/app/modules/cases/models.py backend/tests/test_case_batch_filing_schema.py`
- `cd backend && pytest -q tests/test_case_batch_filing_schema.py`
- `cd backend && alembic upgrade head`
- `./scripts/task_validate.sh CASEBF-DB-01`

**evidence path**
- `artifacts/CASEBF-DB-01/**`

**dependency notes**
- 后续所有任务依赖本任务

### Task 2: CASEBF-BE-QUERY-01

**Files:**
- Modify: `backend/app/modules/cases/api.py`
- Modify: `backend/app/modules/cases/schemas.py`
- Modify: `backend/app/modules/cases/service.py`
- Test: `backend/tests/test_case_batch_filing_query.py`
- Task file: `tasks/postenhancement/backend/CASEBF-BE-QUERY-01.md`

- [ ] Step 1: 写专用批件递交查询的失败测试
- [ ] Step 2: 运行 `cd backend && pytest -q tests/test_case_batch_filing_query.py`
- [ ] Step 3: 实现最小筛选集查询与列表返回 contract
- [ ] Step 4: 运行：
  - `ruff check backend/app/modules/cases/api.py backend/app/modules/cases/schemas.py backend/app/modules/cases/service.py backend/tests/test_case_batch_filing_query.py`
  - `cd backend && pytest -q tests/test_case_batch_filing_query.py`
- [ ] Step 5: 生成 evidence 并收口

**closure slice**
- 只补批件递交页面所需的专用查询 contract

**explicit non-closure**
- 不执行状态迁移
- 不更新 `submitted_date`
- 不改前端

**allowlist**
- `backend/app/modules/cases/api.py`
- `backend/app/modules/cases/schemas.py`
- `backend/app/modules/cases/service.py`
- `backend/tests/test_case_batch_filing_query.py`

**verification**
- `ruff check backend/app/modules/cases/api.py backend/app/modules/cases/schemas.py backend/app/modules/cases/service.py backend/tests/test_case_batch_filing_query.py`
- `cd backend && pytest -q tests/test_case_batch_filing_query.py`
- `./scripts/task_validate.sh CASEBF-BE-QUERY-01`

**evidence path**
- `artifacts/CASEBF-BE-QUERY-01/**`

**dependency notes**
- 依赖 `CASEBF-DB-01`

### Task 3: CASEBF-BE-ACT-01

**Files:**
- Modify: `backend/app/modules/cases/api.py`
- Modify: `backend/app/modules/cases/schemas.py`
- Modify: `backend/app/modules/cases/service.py`
- Test: `backend/tests/test_case_batch_filing_action.py`
- Task file: `tasks/postenhancement/backend/CASEBF-BE-ACT-01.md`

- [ ] Step 1: 写批量执行递交动作的失败测试
- [ ] Step 2: 运行 `cd backend && pytest -q tests/test_case_batch_filing_action.py`
- [ ] Step 3: 实现批量动作、校验与状态迁移
- [ ] Step 4: 运行：
  - `ruff check backend/app/modules/cases/api.py backend/app/modules/cases/schemas.py backend/app/modules/cases/service.py backend/tests/test_case_batch_filing_action.py`
  - `cd backend && pytest -q tests/test_case_batch_filing_action.py`
- [ ] Step 5: 生成 evidence 并收口

**closure slice**
- 只关闭批件递交批量动作：
  - `submitted_date`
  - `apply_exam_now`
  - `NOT_FILED -> WAITING_RECEIPT`
  - `has_exam_request` 更新

**explicit non-closure**
- 不实现 `generate_list`
- 不联动 tasks/documents
- 不改前端

**allowlist**
- `backend/app/modules/cases/api.py`
- `backend/app/modules/cases/schemas.py`
- `backend/app/modules/cases/service.py`
- `backend/tests/test_case_batch_filing_action.py`

**verification**
- `ruff check backend/app/modules/cases/api.py backend/app/modules/cases/schemas.py backend/app/modules/cases/service.py backend/tests/test_case_batch_filing_action.py`
- `cd backend && pytest -q tests/test_case_batch_filing_action.py`
- `./scripts/task_validate.sh CASEBF-BE-ACT-01`

**evidence path**
- `artifacts/CASEBF-BE-ACT-01/**`

**dependency notes**
- 依赖 `CASEBF-DB-01`
- 与 `CASEBF-BE-QUERY-01` 共享文件，必须串行

### Task 4: CASEBF-FE-01

**Files:**
- Modify: `frontend/src/api/cases.ts`
- Modify: `frontend/src/api/cases.types.ts`
- Create: `frontend/src/modules/cases/pages/CaseBatchFiling.vue`
- Modify: `frontend/src/router/index.ts`
- Task file: `tasks/postenhancement/frontend/CASEBF-FE-01.md`

- [ ] Step 1: 写或准备最小前端静态校验路径
- [ ] Step 2: 先实现 cases API/types 批件递交 contract
- [ ] Step 3: 实现批件递交页面：
  - 筛选
  - 列表
  - 勾选
  - 参数区
  - 执行动作
- [ ] Step 4: 路由接入
- [ ] Step 5: 运行：
  - `cd frontend && npm run lint -- src/api/cases.ts src/api/cases.types.ts src/modules/cases/pages/CaseBatchFiling.vue src/router/index.ts`
  - `cd frontend && npm run typecheck`
- [ ] Step 6: 生成 evidence 并收口

**closure slice**
- 只关闭前端批件递交页面 workflow

**explicit non-closure**
- 不改 `CaseList.vue`
- 不做详情页 timeline
- 不做文档生成

**allowlist**
- `frontend/src/api/cases.ts`
- `frontend/src/api/cases.types.ts`
- `frontend/src/modules/cases/pages/CaseBatchFiling.vue`
- `frontend/src/router/index.ts`

**verification**
- `cd frontend && npm run lint -- src/api/cases.ts src/api/cases.types.ts src/modules/cases/pages/CaseBatchFiling.vue src/router/index.ts`
- `cd frontend && npm run typecheck`
- `./scripts/task_validate.sh CASEBF-FE-01`

**evidence path**
- `artifacts/CASEBF-FE-01/**`

**dependency notes**
- 依赖 `CASEBF-BE-QUERY-01`
- 依赖 `CASEBF-BE-ACT-01`

### Task 5: CASEBF-QA-01

**Files:**
- Create: `artifacts/CASEBF-QA-01/summary.md`
- Task file: `tasks/postenhancement/backend/CASEBF-QA-01.md`

- [ ] Step 1: 汇总各任务 evidence
- [ ] Step 2: 生成 item-to-slice ledger
- [ ] Step 3: 运行：
  - `./scripts/task_validate.sh CASEBF-DB-01`
  - `./scripts/task_validate.sh CASEBF-BE-QUERY-01`
  - `./scripts/task_validate.sh CASEBF-BE-ACT-01`
  - `./scripts/task_validate.sh CASEBF-FE-01`
  - `./scripts/task_validate.sh CASEBF-QA-01`
- [ ] Step 4: 完成故事级收口

**closure slice**
- 只做 evidence audit 与故事级 close 决策

**explicit non-closure**
- 不改任何产品代码

**allowlist**
- `artifacts/CASEBF-QA-01/**`

**verification**
- `./scripts/task_validate.sh CASEBF-DB-01`
- `./scripts/task_validate.sh CASEBF-BE-QUERY-01`
- `./scripts/task_validate.sh CASEBF-BE-ACT-01`
- `./scripts/task_validate.sh CASEBF-FE-01`
- `./scripts/task_validate.sh CASEBF-QA-01`

**evidence path**
- `artifacts/CASEBF-QA-01/**`

**dependency notes**
- 依赖所有前置实现任务

## Wave Order

- Wave 1: `CASEBF-DB-01`
- Wave 2: `CASEBF-BE-QUERY-01`
- Wave 3: `CASEBF-BE-ACT-01`
- Wave 4: `CASEBF-FE-01`
- Wave 5: `CASEBF-QA-01`

## Serialized Ownership

- `backend/app/modules/cases/models.py` 仅 `CASEBF-DB-01`
- `backend/app/modules/cases/api.py` / `schemas.py` / `service.py` 在 `CASEBF-BE-QUERY-01` 与 `CASEBF-BE-ACT-01` 间串行
- `frontend/src/api/cases.ts` / `cases.types.ts` / `router/index.ts` 在 FE wave 独占

## Final Notes

- 本计划明确把 `generate_list`、documents 联动、tasks 联动留在 `non-closure`
- 不存在“剩余流程收尾”类任务
- 每个任务只关闭一个明确 slice
