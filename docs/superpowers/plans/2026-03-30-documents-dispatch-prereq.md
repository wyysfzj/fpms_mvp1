# Documents Dispatch Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 `FR-WD-08~10` 建立最小可用的 documents dispatch workflow：批量登记去文邮寄信息、生成并查看交接单、按地址优先级生成信封打印数据。

**Architecture:** 先补 `Document` 邮寄字段和 `T_DocDispatch / T_DocDispatchLine` 的结构化承载，再补三个后端 contract：邮寄登记、交接单、信封打印，最后落地两个前端入口页面。第一版不进入模板/附件联动、timeline、导出报表。

**Tech Stack:** FastAPI, SQLAlchemy, Alembic, Vue 3, Element Plus, SQLite

---

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `chained (DB -> BE -> FE)`
- `evidence_cost`: `high`

## chosen_runbook

- `P0-prereq-heavy-story`

## File Structure

- `backend/alembic/versions/docdsp_db_01_doc_dispatch_tables.py`
  - SQLite-safe migration for document mail fields and dispatch tables
- `backend/app/modules/documents/models.py`
  - ORM for `Document` mail fields and `DocDispatch` / `DocDispatchLine`
- `backend/app/modules/documents/api.py`
  - dispatch actions and queries
- `backend/app/modules/documents/schemas.py`
  - request/response models for mailing, dispatch detail, envelope preview
- `backend/app/modules/documents/service.py`
  - dispatch service rules and address resolution
- `backend/tests/test_doc_dispatch_schema.py`
  - schema/table prerequisite tests
- `backend/tests/test_doc_dispatch_mailing_action.py`
  - mailing batch update tests
- `backend/tests/test_doc_dispatch_handoff.py`
  - dispatch create/detail tests
- `backend/tests/test_doc_dispatch_envelope.py`
  - envelope preview tests
- `frontend/src/api/documents.ts`
  - dispatch endpoints client
- `frontend/src/api/documents.types.ts`
  - frontend types for dispatch workflow
- `frontend/src/modules/documents/pages/DocumentDispatch.vue`
  - mailing + handoff workflow page
- `frontend/src/modules/documents/pages/DocumentEnvelopePrint.vue`
  - single-document envelope preview page
- `frontend/src/router/index.ts`
  - route wiring

## Batch Manifest

### Task 1: DOCDSP-DB-01

**Files:**
- Create: `backend/alembic/versions/docdsp_db_01_doc_dispatch_tables.py`
- Modify: `backend/app/modules/documents/models.py`
- Test: `backend/tests/test_doc_dispatch_schema.py`
- Task file: `tasks/postenhancement/backend/DOCDSP-DB-01.md`

- [ ] Step 1: 写 `Document` 邮寄字段与 `DocDispatch`/`DocDispatchLine` 的失败测试
- [ ] Step 2: 运行 `cd backend && pytest -q tests/test_doc_dispatch_schema.py`
- [ ] Step 3: 实现 SQLite-safe migration 与 ORM
- [ ] Step 4: 运行：
  - `ruff check backend/alembic/versions/docdsp_db_01_doc_dispatch_tables.py backend/app/modules/documents/models.py backend/tests/test_doc_dispatch_schema.py`
  - `cd backend && pytest -q tests/test_doc_dispatch_schema.py`
  - `cd backend && alembic upgrade head`
- [ ] Step 5: 生成 evidence 并收口

**closure slice**
- 只补 `Document.outgoing_reg_no / forward_date` 与 `DocDispatch / DocDispatchLine` 结构化承载

**explicit non-closure**
- 不改 API
- 不改 service action
- 不改前端
- 不做 envelope 打印逻辑

**allowlist**
- `backend/alembic/versions/docdsp_db_01_doc_dispatch_tables.py`
- `backend/app/modules/documents/models.py`
- `backend/tests/test_doc_dispatch_schema.py`

**verification**
- `ruff check backend/alembic/versions/docdsp_db_01_doc_dispatch_tables.py backend/app/modules/documents/models.py backend/tests/test_doc_dispatch_schema.py`
- `cd backend && pytest -q tests/test_doc_dispatch_schema.py`
- `cd backend && alembic upgrade head`
- `./scripts/task_validate.sh DOCDSP-DB-01`

**evidence path**
- `artifacts/DOCDSP-DB-01/**`

**dependency notes**
- 所有后续任务依赖本任务

### Task 2: DOCDSP-BE-MAIL-01

**Files:**
- Modify: `backend/app/modules/documents/api.py`
- Modify: `backend/app/modules/documents/schemas.py`
- Modify: `backend/app/modules/documents/service.py`
- Test: `backend/tests/test_doc_dispatch_mailing_action.py`
- Task file: `tasks/postenhancement/backend/DOCDSP-BE-MAIL-01.md`

- [ ] Step 1: 写批量邮寄登记 action 的失败测试
- [ ] Step 2: 运行 `cd backend && pytest -q tests/test_doc_dispatch_mailing_action.py`
- [ ] Step 3: 实现批量更新 `outgoing_reg_no / forward_date` contract 与 service
- [ ] Step 4: 运行：
  - `ruff check backend/app/modules/documents/api.py backend/app/modules/documents/schemas.py backend/app/modules/documents/service.py backend/tests/test_doc_dispatch_mailing_action.py`
  - `cd backend && pytest -q tests/test_doc_dispatch_mailing_action.py`
- [ ] Step 5: 生成 evidence 并收口

**closure slice**
- 只关闭 `A. 邮寄信息登记` 批量 action

**explicit non-closure**
- 不生成交接单
- 不做 envelope 数据生成
- 不改前端

**allowlist**
- `backend/app/modules/documents/api.py`
- `backend/app/modules/documents/schemas.py`
- `backend/app/modules/documents/service.py`
- `backend/tests/test_doc_dispatch_mailing_action.py`

**verification**
- `ruff check backend/app/modules/documents/api.py backend/app/modules/documents/schemas.py backend/app/modules/documents/service.py backend/tests/test_doc_dispatch_mailing_action.py`
- `cd backend && pytest -q tests/test_doc_dispatch_mailing_action.py`
- `./scripts/task_validate.sh DOCDSP-BE-MAIL-01`

**evidence path**
- `artifacts/DOCDSP-BE-MAIL-01/**`

**dependency notes**
- 依赖 `DOCDSP-DB-01`

### Task 3: DOCDSP-BE-DISP-01

**Files:**
- Modify: `backend/app/modules/documents/api.py`
- Modify: `backend/app/modules/documents/schemas.py`
- Modify: `backend/app/modules/documents/service.py`
- Test: `backend/tests/test_doc_dispatch_handoff.py`
- Task file: `tasks/postenhancement/backend/DOCDSP-BE-DISP-01.md`

- [ ] Step 1: 写交接单生成/详情的失败测试
- [ ] Step 2: 运行 `cd backend && pytest -q tests/test_doc_dispatch_handoff.py`
- [ ] Step 3: 实现交接单生成 action 与详情 query
- [ ] Step 4: 运行：
  - `ruff check backend/app/modules/documents/api.py backend/app/modules/documents/schemas.py backend/app/modules/documents/service.py backend/tests/test_doc_dispatch_handoff.py`
  - `cd backend && pytest -q tests/test_doc_dispatch_handoff.py`
- [ ] Step 5: 生成 evidence 并收口

**closure slice**
- 只关闭 `B. 文件交接单` 的生成与详情查看 contract

**explicit non-closure**
- 不更新邮寄登记字段
- 不做 envelope 打印 query
- 不改前端

**allowlist**
- `backend/app/modules/documents/api.py`
- `backend/app/modules/documents/schemas.py`
- `backend/app/modules/documents/service.py`
- `backend/tests/test_doc_dispatch_handoff.py`

**verification**
- `ruff check backend/app/modules/documents/api.py backend/app/modules/documents/schemas.py backend/app/modules/documents/service.py backend/tests/test_doc_dispatch_handoff.py`
- `cd backend && pytest -q tests/test_doc_dispatch_handoff.py`
- `./scripts/task_validate.sh DOCDSP-BE-DISP-01`

**evidence path**
- `artifacts/DOCDSP-BE-DISP-01/**`

**dependency notes**
- 依赖 `DOCDSP-DB-01`
- 与 `DOCDSP-BE-MAIL-01` 共享文件，必须串行

### Task 4: DOCDSP-BE-ENV-01

**Files:**
- Modify: `backend/app/modules/documents/api.py`
- Modify: `backend/app/modules/documents/schemas.py`
- Modify: `backend/app/modules/documents/service.py`
- Test: `backend/tests/test_doc_dispatch_envelope.py`
- Task file: `tasks/postenhancement/backend/DOCDSP-BE-ENV-01.md`

- [ ] Step 1: 写信封打印数据 query 的失败测试
- [ ] Step 2: 运行 `cd backend && pytest -q tests/test_doc_dispatch_envelope.py`
- [ ] Step 3: 实现地址优先级解析与 envelope preview contract
- [ ] Step 4: 运行：
  - `ruff check backend/app/modules/documents/api.py backend/app/modules/documents/schemas.py backend/app/modules/documents/service.py backend/tests/test_doc_dispatch_envelope.py`
  - `cd backend && pytest -q tests/test_doc_dispatch_envelope.py`
- [ ] Step 5: 生成 evidence 并收口

**closure slice**
- 只关闭 `C. 信封打印` 的即时打印数据 query

**explicit non-closure**
- 不做交接单生成
- 不做打印日志持久化
- 不改前端

**allowlist**
- `backend/app/modules/documents/api.py`
- `backend/app/modules/documents/schemas.py`
- `backend/app/modules/documents/service.py`
- `backend/tests/test_doc_dispatch_envelope.py`

**verification**
- `ruff check backend/app/modules/documents/api.py backend/app/modules/documents/schemas.py backend/app/modules/documents/service.py backend/tests/test_doc_dispatch_envelope.py`
- `cd backend && pytest -q tests/test_doc_dispatch_envelope.py`
- `./scripts/task_validate.sh DOCDSP-BE-ENV-01`

**evidence path**
- `artifacts/DOCDSP-BE-ENV-01/**`

**dependency notes**
- 依赖 `DOCDSP-DB-01`
- 与 `DOCDSP-BE-MAIL-01`、`DOCDSP-BE-DISP-01` 共享文件，必须串行

### Task 5: DOCDSP-FE-MAIL-01

**Files:**
- Modify: `frontend/src/api/documents.ts`
- Modify: `frontend/src/api/documents.types.ts`
- Create: `frontend/src/modules/documents/pages/DocumentDispatch.vue`
- Modify: `frontend/src/router/index.ts`
- Task file: `tasks/postenhancement/frontend/DOCDSP-FE-MAIL-01.md`

- [ ] Step 1: 准备最小前端静态校验路径
- [ ] Step 2: 先实现 dispatch workflow 页的筛选、列表和邮寄登记 action 接线
- [ ] Step 3: 运行：
  - `cd frontend && npm run lint -- src/api/documents.ts src/api/documents.types.ts src/modules/documents/pages/DocumentDispatch.vue src/router/index.ts`
  - `cd frontend && npm run typecheck`
- [ ] Step 4: 生成 evidence 并收口

**closure slice**
- 只关闭 `A. 邮寄信息登记` 的前端 workflow：筛选、勾选、批量登记

**explicit non-closure**
- 不做交接单详情
- 不做信封打印预览
- 不改 `DocumentList.vue`

**allowlist**
- `frontend/src/api/documents.ts`
- `frontend/src/api/documents.types.ts`
- `frontend/src/modules/documents/pages/DocumentDispatch.vue`
- `frontend/src/router/index.ts`

**verification**
- `cd frontend && npm run lint -- src/api/documents.ts src/api/documents.types.ts src/modules/documents/pages/DocumentDispatch.vue src/router/index.ts`
- `cd frontend && npm run typecheck`
- `./scripts/task_validate.sh DOCDSP-FE-MAIL-01`

**evidence path**
- `artifacts/DOCDSP-FE-MAIL-01/**`

**dependency notes**
- 依赖 `DOCDSP-BE-MAIL-01`

### Task 6: DOCDSP-FE-DISP-01

**Files:**
- Modify: `frontend/src/api/documents.ts`
- Modify: `frontend/src/api/documents.types.ts`
- Modify: `frontend/src/modules/documents/pages/DocumentDispatch.vue`
- Task file: `tasks/postenhancement/frontend/DOCDSP-FE-DISP-01.md`

- [ ] Step 1: 扩展 dispatch workflow 页以支持交接单生成与详情查看
- [ ] Step 2: 运行：
  - `cd frontend && npm run lint -- src/api/documents.ts src/api/documents.types.ts src/modules/documents/pages/DocumentDispatch.vue`
  - `cd frontend && npm run typecheck`
- [ ] Step 3: 生成 evidence 并收口

**closure slice**
- 只关闭 `B. 文件交接单` 的前端生成与详情查看

**explicit non-closure**
- 不做信封打印预览
- 不改通用 document 列表
- 不做模板/附件联动

**allowlist**
- `frontend/src/api/documents.ts`
- `frontend/src/api/documents.types.ts`
- `frontend/src/modules/documents/pages/DocumentDispatch.vue`

**verification**
- `cd frontend && npm run lint -- src/api/documents.ts src/api/documents.types.ts src/modules/documents/pages/DocumentDispatch.vue`
- `cd frontend && npm run typecheck`
- `./scripts/task_validate.sh DOCDSP-FE-DISP-01`

**evidence path**
- `artifacts/DOCDSP-FE-DISP-01/**`

**dependency notes**
- 依赖 `DOCDSP-BE-DISP-01`
- 与 `DOCDSP-FE-MAIL-01` 共享文件，必须串行

### Task 7: DOCDSP-FE-ENV-01

**Files:**
- Modify: `frontend/src/api/documents.ts`
- Modify: `frontend/src/api/documents.types.ts`
- Create: `frontend/src/modules/documents/pages/DocumentEnvelopePrint.vue`
- Modify: `frontend/src/router/index.ts`
- Task file: `tasks/postenhancement/frontend/DOCDSP-FE-ENV-01.md`

- [ ] Step 1: 实现单文档信封打印预览页与 API 接线
- [ ] Step 2: 运行：
  - `cd frontend && npm run lint -- src/api/documents.ts src/api/documents.types.ts src/modules/documents/pages/DocumentEnvelopePrint.vue src/router/index.ts`
  - `cd frontend && npm run typecheck`
- [ ] Step 3: 生成 evidence 并收口

**closure slice**
- 只关闭 `C. 信封打印` 的前端预览/打印数据展示

**explicit non-closure**
- 不做交接单生成
- 不做打印日志
- 不改 `DocumentList.vue`

**allowlist**
- `frontend/src/api/documents.ts`
- `frontend/src/api/documents.types.ts`
- `frontend/src/modules/documents/pages/DocumentEnvelopePrint.vue`
- `frontend/src/router/index.ts`

**verification**
- `cd frontend && npm run lint -- src/api/documents.ts src/api/documents.types.ts src/modules/documents/pages/DocumentEnvelopePrint.vue src/router/index.ts`
- `cd frontend && npm run typecheck`
- `./scripts/task_validate.sh DOCDSP-FE-ENV-01`

**evidence path**
- `artifacts/DOCDSP-FE-ENV-01/**`

**dependency notes**
- 依赖 `DOCDSP-BE-ENV-01`
- 与前两个 FE 任务共享 api/router，必须串行

### Task 8: DOCDSP-QA-01

**Files:**
- Create: `artifacts/DOCDSP-QA-01/summary.md`
- Task file: `tasks/postenhancement/backend/DOCDSP-QA-01.md`

- [ ] Step 1: 汇总各任务 evidence
- [ ] Step 2: 生成 item-to-slice ledger
- [ ] Step 3: 运行：
  - `./scripts/task_validate.sh DOCDSP-DB-01`
  - `./scripts/task_validate.sh DOCDSP-BE-MAIL-01`
  - `./scripts/task_validate.sh DOCDSP-BE-DISP-01`
  - `./scripts/task_validate.sh DOCDSP-BE-ENV-01`
  - `./scripts/task_validate.sh DOCDSP-FE-MAIL-01`
  - `./scripts/task_validate.sh DOCDSP-FE-DISP-01`
  - `./scripts/task_validate.sh DOCDSP-FE-ENV-01`
  - `./scripts/task_validate.sh DOCDSP-QA-01`
- [ ] Step 4: 完成故事级收口

**closure slice**
- 只做 evidence audit 与故事级 close 决策

**explicit non-closure**
- 不改任何产品代码

**allowlist**
- `artifacts/DOCDSP-QA-01/**`

**verification**
- `./scripts/task_validate.sh DOCDSP-DB-01`
- `./scripts/task_validate.sh DOCDSP-BE-MAIL-01`
- `./scripts/task_validate.sh DOCDSP-BE-DISP-01`
- `./scripts/task_validate.sh DOCDSP-BE-ENV-01`
- `./scripts/task_validate.sh DOCDSP-FE-MAIL-01`
- `./scripts/task_validate.sh DOCDSP-FE-DISP-01`
- `./scripts/task_validate.sh DOCDSP-FE-ENV-01`
- `./scripts/task_validate.sh DOCDSP-QA-01`

**evidence path**
- `artifacts/DOCDSP-QA-01/**`

**dependency notes**
- 依赖所有前置实现任务

## Wave Order

- Wave 1: `DOCDSP-DB-01`
- Wave 2: `DOCDSP-BE-MAIL-01`
- Wave 3: `DOCDSP-BE-DISP-01`
- Wave 4: `DOCDSP-BE-ENV-01`
- Wave 5: `DOCDSP-FE-MAIL-01`
- Wave 6: `DOCDSP-FE-DISP-01`
- Wave 7: `DOCDSP-FE-ENV-01`
- Wave 8: `DOCDSP-QA-01`

## Serialized Ownership

- `backend/app/modules/documents/models.py` 仅 `DOCDSP-DB-01`
- `backend/app/modules/documents/api.py` / `schemas.py` / `service.py` 在三个 BE 任务间串行
- `frontend/src/api/documents.ts` / `documents.types.ts` / `router/index.ts` 在三个 FE 任务间串行
- `frontend/src/modules/documents/pages/DocumentDispatch.vue` 在 `DOCDSP-FE-MAIL-01` 与 `DOCDSP-FE-DISP-01` 间串行

## Final Notes

- 不允许把 `A/B/C` 三个动作合并为一个 atomic task
- 不允许把模板/附件联动、timeline、report 吸收到当前故事
