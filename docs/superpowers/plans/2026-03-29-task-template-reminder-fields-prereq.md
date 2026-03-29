# 时限模板关键字段补全 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 补齐任务模板关键字段并让新生成任务按模板时限/提醒规则生效，但先以前置 prerequisite 方式拆开模板字段、运行时承载、generation logic 和前端表单。

**Architecture:** 先解决模型与 contract 断层，再让 generation 逻辑消费新字段，最后补齐模板管理前端。该故事当前不能被视为纯前端或纯 API 小改，必须按 prerequisite-heavy 方式串行推进。

**Tech Stack:** FastAPI, SQLAlchemy 2.x, Pydantic 2.x, Vue 3, TypeScript, Element Plus, SQLite

---

> Story Shape Classification
> - `shared_file_density`: `high`
> - `prereq_dependency_density`: `high`
> - `be_fe_coupling`: `chained (BE -> FE)`
> - `evidence_cost`: `high`
>
> chosen_runbook: `P0-prereq-heavy-story`

## Scope Decision

当前计划是 **prerequisite plan**，不是直接执行计划。只有当 schema / model prerequisite 被允许时，才能真正进入实现。

当前正式判断：

- `不可直接实现，必须先新增 prerequisite task(s)`
- 若仍受无 schema 的 `Phase 3 / 3.1 / 3.5` 约束，则本故事执行状态应视为 `BLOCKED`

## File Map

### Backend shared ownership

- `backend/app/modules/tasks/models.py`
  - `TaskTemplate` / `Task` 运行时字段承载
- `backend/app/modules/tasks/schemas.py`
  - 模板 CRUD 与任务输出 contract
- `backend/app/modules/tasks/api.py`
  - 模板 CRUD endpoint request/response shape
- `backend/app/modules/tasks/task_generation_service.py`
  - 新生成任务的时限/提醒计算
- `backend/app/modules/tasks/enums.py`
  - 如需稳定枚举定义，放在这里
- `backend/tests/test_task_template.py`
  - 模板 CRUD 与字段 contract
- `backend/tests/test_task_generation.py`
  - generation logic 与 reminder 结果

### Frontend shared ownership

- `frontend/src/api/tasks.ts`
  - 模板 API client
- `frontend/src/api/tasks.types.ts`
  - 模板与任务的 TS contract
- `frontend/src/modules/system/pages/TaskTemplateList.vue`
  - 模板字段维护 UI

## Batch Manifest

### DLTPL-DB-01

**task file path**
- `tasks/postenhancement/backend/DLTPL-DB-01.md`

**closure slice**
- 为 `TaskTemplate` 与 `Task` 新增本故事要求的关键字段承载，并保持 SQLite-safe schema/model 对齐。

**explicit non-closure**
- 不实现 generation logic。
- 不实现前端表单。
- 不实现历史 task 回填或重算。

**allowlist**
- `backend/alembic/versions/<new>_task_template_reminder_fields.py`
- `backend/app/modules/tasks/models.py`
- `backend/app/modules/tasks/enums.py`

**verification**
- `ruff check backend/alembic/versions/<new>_task_template_reminder_fields.py backend/app/modules/tasks/models.py backend/app/modules/tasks/enums.py`
- `cd backend && alembic upgrade head`
- `./scripts/task_validate.sh DLTPL-DB-01`

**evidence path**
- `artifacts/DLTPL-DB-01/**`

**dependency notes**
- First prerequisite. Blocks all follow-up tasks.

### DLTPL-BE-TPL-01

**task file path**
- `tasks/postenhancement/backend/DLTPL-BE-TPL-01.md`

**closure slice**
- 补齐 `TaskTemplate` CRUD contract，使模板 API 能读取和保存 `deadline_base / remind_base / remind_1/2/3_offset_days / daily_remind / default_supervisor_id`。
- 同时修正模板 CRUD 的原子写入与基础 supervisor 校验，避免 API 层二次提交补丁。

**explicit non-closure**
- 不实现 generation logic 生效。
- 不实现前端页面。
- 不修改 reminder execution path。

**allowlist**
- `backend/app/modules/tasks/api.py`
- `backend/app/modules/tasks/schemas.py`
- `backend/app/modules/tasks/service.py`
- `backend/tests/test_task_template.py`

**verification**
- `ruff check backend/app/modules/tasks/api.py backend/app/modules/tasks/schemas.py backend/app/modules/tasks/service.py backend/tests/test_task_template.py`
- `cd backend && pytest -q tests/test_task_template.py -k 'template'`
- `./scripts/task_validate.sh DLTPL-BE-TPL-01`

**evidence path**
- `artifacts/DLTPL-BE-TPL-01/**`

**dependency notes**
- Depends on `DLTPL-DB-01`.

### DLTPL-BE-GEN-01

**task file path**
- `tasks/postenhancement/backend/DLTPL-BE-GEN-01.md`

**closure slice**
- `task_generation_service` 读取模板新字段，并让新生成任务的 deadline / remind1/2/3 / daily_remind 结果生效。

**explicit non-closure**
- 不回填已有 task。
- 不改模板前端表单。
- 不改提醒页面展示。

**allowlist**
- `backend/app/modules/tasks/task_generation_service.py`
- `backend/tests/test_task_generation.py`

**verification**
- `ruff check backend/app/modules/tasks/task_generation_service.py backend/tests/test_task_generation.py`
- `cd backend && pytest -q tests/test_task_generation.py`
- `./scripts/task_validate.sh DLTPL-BE-GEN-01`

**evidence path**
- `artifacts/DLTPL-BE-GEN-01/**`

**dependency notes**
- Depends on `DLTPL-DB-01`.
- Must run after `DLTPL-BE-TPL-01` if schema serialization changes affect contract helpers.

### DLTPL-FE-TPL-01

**task file path**
- `tasks/postenhancement/frontend/DLTPL-FE-TPL-01.md`

**closure slice**
- 在任务模板管理页补齐关键字段输入与展示，使用简体中文 UI，并对齐后端模板 contract。

**explicit non-closure**
- 不改任务列表、今日提醒页、任务详情页。
- 不实现 reminder execution 逻辑。
- 不新增 reminder 专用权限。

**allowlist**
- `frontend/src/api/tasks.ts`
- `frontend/src/api/tasks.types.ts`
- `frontend/src/modules/system/pages/TaskTemplateList.vue`

**verification**
- `cd frontend && npm run lint -- src/api/tasks.ts src/api/tasks.types.ts src/modules/system/pages/TaskTemplateList.vue`
- `cd frontend && npm run typecheck`
- `./scripts/task_validate.sh DLTPL-FE-TPL-01`

**evidence path**
- `artifacts/DLTPL-FE-TPL-01/**`

**dependency notes**
- Depends on `DLTPL-BE-TPL-01`.
- Serialized with any other task touching `tasks.ts` / `tasks.types.ts`.

### DLTPL-QA-01

**task file path**
- `tasks/postenhancement/backend/DLTPL-QA-01.md`

**closure slice**
- 故事级 item-to-slice ledger、evidence audit、task gate 收口。

**explicit non-closure**
- 不改产品代码。

**allowlist**
- `artifacts/DLTPL-QA-01/**`

**verification**
- `./scripts/task_validate.sh DLTPL-DB-01`
- `./scripts/task_validate.sh DLTPL-BE-TPL-01`
- `./scripts/task_validate.sh DLTPL-BE-GEN-01`
- `./scripts/task_validate.sh DLTPL-FE-TPL-01`
- `./scripts/task_validate.sh DLTPL-QA-01`

**evidence path**
- `artifacts/DLTPL-QA-01/**`

**dependency notes**
- Final close task only after all prior tasks are PASS.

## Wave Order

1. `DLTPL-DB-01`
2. `DLTPL-BE-TPL-01`
3. `DLTPL-BE-GEN-01`
4. `DLTPL-FE-TPL-01`
5. `DLTPL-QA-01`

## Serialized Ownership Decisions

- `backend/app/modules/tasks/models.py` is exclusive to `DLTPL-DB-01`.
- `backend/app/modules/tasks/schemas.py` and `backend/app/modules/tasks/api.py` are exclusive to `DLTPL-BE-TPL-01`.
- `backend/app/modules/tasks/service.py` is also serialized into `DLTPL-BE-TPL-01`; generation remains exclusive to `DLTPL-BE-GEN-01`.
- `backend/app/modules/tasks/task_generation_service.py` is exclusive to `DLTPL-BE-GEN-01`.
- `frontend/src/api/tasks.ts` and `frontend/src/api/tasks.types.ts` require serialized ownership with `DLTPL-FE-TPL-01`.
- `frontend/src/modules/system/pages/TaskTemplateList.vue` is exclusive to `DLTPL-FE-TPL-01`.

## Blocker Note

This plan is intentionally prerequisite-first. If schema changes are not approved, execution must stop here and the story remains `BLOCKED`. In that case, the only valid fallback is to re-scope the story to documentation or non-executable design work; template-only UI/API edits would not honestly close the approved closure slice.

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-03-29-task-template-reminder-fields-prereq.md`.

Two execution options after you approve this prerequisite plan:

1. `Subagent-Driven` - recommended for serialized prerequisite waves
2. `Inline Execution` - execute waves in this session with review checkpoints
