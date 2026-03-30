# GF-WL Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the grant-fee task worklist/list/query and dedicated workbench page on top of `GF-PRE` and `GF-SM`, without absorbing draft or document linkage.

**Architecture:** Execute this as a frontend-heavy story with serialized backend-then-frontend ownership. Backend closes list/query contract first, frontend closes route/page/api client second, then QA close audits the story.

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

### GFWL-BE-01
- task file path: `tasks/postenhancement/backend/GFWL-BE-01.md`
- closure slice: implement grant-fee task list/query backend contract with the frozen field set, filters, pagination, and read-only status projection
- explicit non-closure: no draft generation, no state action changes, no bill/document linkage, no frontend
- allowlist:
  - `backend/app/modules/grant_fees/api.py`
  - `backend/app/modules/grant_fees/schemas.py`
  - `backend/app/modules/grant_fees/service.py`
  - `backend/tests/test_grant_fee_worklist_api.py`
- verification:
  - `python3 -m ruff check backend/app/modules/grant_fees/api.py backend/app/modules/grant_fees/schemas.py backend/app/modules/grant_fees/service.py backend/tests/test_grant_fee_worklist_api.py`
  - `cd backend && PYTHONPATH=. pytest -q tests/test_grant_fee_worklist_api.py`
  - `./scripts/task_validate.sh GFWL-BE-01`
- dependency notes: depends on committed `GF-PRE` and `GF-SM`; owns grant-fee backend list/query files

### GFWL-FE-01
- task file path: `tasks/postenhancement/frontend/GFWL-FE-01.md`
- closure slice: implement grant-fee dedicated worklist page, route, and frontend api/types for read-only list/query and action-entry shell
- explicit non-closure: no frontend action execution, no draft generation, no detail/edit, no bill/document linkage
- allowlist:
  - `frontend/src/api/grantFees.ts`
  - `frontend/src/api/grantFees.types.ts`
  - `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`
  - `frontend/src/router/index.ts`
  - `frontend/src/constants/menu.ts`
  - `frontend/tests/grant-fee-worklist.smoke.md`
- verification:
  - `cd frontend && npm run lint -- src/api/grantFees.ts src/api/grantFees.types.ts src/modules/grantFees/pages/GrantFeeTaskList.vue src/router/index.ts src/constants/menu.ts`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh GFWL-FE-01`
- dependency notes: serialize after `GFWL-BE-01`; owns route and frontend api/types

### GFWL-QA-01
- task file path: `tasks/postenhancement/backend/GFWL-QA-01.md`
- closure slice: gate audit, evidence audit, and story close summary for `GF-WL`
- explicit non-closure: no product code changes
- allowlist:
  - `artifacts/GFWL-BE-01/**`
  - `artifacts/GFWL-FE-01/**`
  - `artifacts/GFWL-QA-01/**`
- verification:
  - `./scripts/task_validate.sh GFWL-BE-01`
  - `./scripts/task_validate.sh GFWL-FE-01`
  - `./scripts/task_validate.sh GFWL-QA-01`
- dependency notes: final wave after backend and frontend tasks pass

## Waves
- Wave 1: `GFWL-BE-01`
- Wave 2: `GFWL-FE-01`
- Wave 3: `GFWL-QA-01`

## Serialized Shared-file Decisions
- `backend/app/modules/grant_fees/api.py` is owned only by `GFWL-BE-01`
- `backend/app/modules/grant_fees/schemas.py` is owned only by `GFWL-BE-01`
- `backend/app/modules/grant_fees/service.py` is owned only by `GFWL-BE-01`
- `frontend/src/router/index.ts` is owned only by `GFWL-FE-01`
- `frontend/src/constants/menu.ts` is owned only by `GFWL-FE-01`
- `frontend/src/api/grantFees.ts|grantFees.types.ts` are owned only by `GFWL-FE-01`
