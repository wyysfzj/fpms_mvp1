# P2 #17 Task Deadline Special Search Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the first-round special task search for `APPLY_FEE_LIMIT` and `EXAM_REQUEST_LIMIT` with a dedicated backend search contract and a dedicated frontend search page, without absorbing reminder/export/reporting or batch actions.

**Architecture:** Execute this as a frontend-heavy story with serialized backend-then-frontend ownership. Backend freezes task-code scope, projection, overdue semantics, filters, and pagination first; frontend then closes dedicated page, route, menu, and shared tasks api/types; QA finally audits evidence and close scope.

**Tech Stack:** FastAPI, SQLAlchemy, Vue 3, TypeScript, Element Plus, SQLite

---

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: chained (BE -> FE)
- evidence_cost: medium

## chosen_runbook

- P0-frontend-heavy-story

## Batch Manifest

### TASKSEARCH-BE-01

- task file path: `tasks/postenhancement/backend/TASKSEARCH-BE-01.md`
- closure slice: implement `APPLY_FEE_LIMIT` + `EXAM_REQUEST_LIMIT` special search backend contract with frozen projection fields, minimal filters, simple overdue semantics, and pagination
- closure slice: implement `APPLY_FEE_LIMIT` + `EXAM_REQUEST_LIMIT` special search backend contract with frozen projection fields, minimal filters, simple overdue semantics, pagination, and `due_date_range` realized as `due_date_from` / `due_date_to` query params
- explicit non-closure: no frontend, no reminder linkage, no summary/export/reporting, no schema changes
- allowlist:
  - `backend/app/modules/tasks/api.py`
  - `backend/app/modules/tasks/schemas.py`
  - `backend/app/modules/tasks/service.py`
  - `backend/tests/test_task_special_search_api.py`
- verification:
  - `python3 -m ruff check backend/app/modules/tasks/api.py backend/app/modules/tasks/schemas.py backend/app/modules/tasks/service.py backend/tests/test_task_special_search_api.py`
  - `cd backend && PYTHONPATH=. pytest -q tests/test_task_special_search_api.py`
  - `./scripts/task_validate.sh TASKSEARCH-BE-01`
- dependency notes: no schema prerequisite; owns tasks backend special-search files
- dependency notes: no schema prerequisite; `remark` stays a nullable placeholder because current Task carrier does not persist it

### TASKSEARCH-FE-01

- task file path: `tasks/postenhancement/frontend/TASKSEARCH-FE-01.md`
- closure slice: implement dedicated special-search page, route, menu entry, and shared tasks api/types for the frozen special-search list contract
- explicit non-closure: no summary/export/print, no reminder view, no dashboard/reporting, no rewrite of generic task list or today reminders pages
- allowlist:
  - `frontend/src/api/tasks.ts`
  - `frontend/src/api/tasks.types.ts`
  - `frontend/src/modules/tasks/pages/TaskSpecialSearch.vue`
  - `frontend/src/router/index.ts`
  - `frontend/src/constants/menu.ts`
- verification:
  - `cd frontend && npm run lint -- src/api/tasks.ts src/api/tasks.types.ts src/modules/tasks/pages/TaskSpecialSearch.vue src/router/index.ts src/constants/menu.ts`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh TASKSEARCH-FE-01`
- dependency notes: serialize after `TASKSEARCH-BE-01`; owns router, menu, and shared tasks FE api/types

### TASKSEARCH-QA-01

- task file path: `tasks/postenhancement/backend/TASKSEARCH-QA-01.md`
- closure slice: gate audit, evidence audit, and story close summary for `P2 #17` first-round special deadline search
- explicit non-closure: no product code changes
- allowlist:
  - `artifacts/TASKSEARCH-BE-01/**`
  - `artifacts/TASKSEARCH-FE-01/**`
  - `artifacts/TASKSEARCH-QA-01/**`
- verification:
  - `./scripts/task_validate.sh TASKSEARCH-BE-01`
  - `./scripts/task_validate.sh TASKSEARCH-FE-01`
  - `./scripts/task_validate.sh TASKSEARCH-QA-01`
- dependency notes: final wave after backend and frontend tasks pass

## Waves

- Wave 1: `TASKSEARCH-BE-01`
- Wave 2: `TASKSEARCH-FE-01`
- Wave 3: `TASKSEARCH-QA-01`

## Serialized Shared-file Decisions

- `backend/app/modules/tasks/api.py` is owned only by `TASKSEARCH-BE-01`
- `backend/app/modules/tasks/schemas.py` is owned only by `TASKSEARCH-BE-01`
- `backend/app/modules/tasks/service.py` is owned only by `TASKSEARCH-BE-01`
- `frontend/src/api/tasks.ts` is owned only by `TASKSEARCH-FE-01`
- `frontend/src/api/tasks.types.ts` is owned only by `TASKSEARCH-FE-01`
- `frontend/src/router/index.ts` is owned only by `TASKSEARCH-FE-01`
- `frontend/src/constants/menu.ts` is owned only by `TASKSEARCH-FE-01`
