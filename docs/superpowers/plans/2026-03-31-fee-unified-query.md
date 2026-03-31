# P2 #16 Fee Unified Query Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the first-round `payment + receipt` unified query with a `UNION-like` backend contract and a dedicated billing query page, without absorbing summary/export/reporting or reconciliation semantics.

**Architecture:** Execute this as a frontend-heavy story with serialized backend-then-frontend ownership. Backend freezes unified projection, filters, pagination, and permission semantics first; frontend then closes dedicated page, route, menu, and shared billing api/types; QA finally audits evidence and close scope.

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

### FEEQRY-BE-01

- task file path: `tasks/postenhancement/backend/FEEQRY-BE-01.md`
- closure slice: implement payment + receipt unified query backend contract with frozen projection fields, filters, pagination, and UNION-like service semantics
- explicit non-closure: no frontend, no summary/export/reporting, no reconciliation semantics, no schema changes
- allowlist:
  - `backend/app/modules/billing/api.py`
  - `backend/app/modules/billing/schemas.py`
  - `backend/app/modules/billing/service.py`
  - `backend/tests/test_fee_unified_query_api.py`
- verification:
  - `python3 -m ruff check backend/app/modules/billing/api.py backend/app/modules/billing/schemas.py backend/app/modules/billing/service.py backend/tests/test_fee_unified_query_api.py`
  - `cd backend && PYTHONPATH=. pytest -q tests/test_fee_unified_query_api.py`
  - `./scripts/task_validate.sh FEEQRY-BE-01`
- dependency notes: no schema prerequisite; owns billing backend unified query files

### FEEQRY-FE-01

- task file path: `tasks/postenhancement/frontend/FEEQRY-FE-01.md`
- closure slice: implement dedicated billing unified query page, route, menu entry, and shared billing api/types for the frozen unified list contract
- explicit non-closure: no summary cards, no export/print, no reconciliation view, no reuse-driven rewrite of existing payment/receipt pages
- allowlist:
  - `frontend/src/api/billing.ts`
  - `frontend/src/api/billing.types.ts`
  - `frontend/src/modules/billing/pages/FeeUnifiedQuery.vue`
  - `frontend/src/router/index.ts`
  - `frontend/src/constants/menu.ts`
- verification:
  - `cd frontend && npm run lint -- src/api/billing.ts src/api/billing.types.ts src/modules/billing/pages/FeeUnifiedQuery.vue src/router/index.ts src/constants/menu.ts`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh FEEQRY-FE-01`
- dependency notes: serialize after `FEEQRY-BE-01`; owns router, menu, and shared billing FE api/types

### FEEQRY-QA-01

- task file path: `tasks/postenhancement/backend/FEEQRY-QA-01.md`
- closure slice: gate audit, evidence audit, and story close summary for `P2 #16` first-round unified query
- explicit non-closure: no product code changes
- allowlist:
  - `artifacts/FEEQRY-BE-01/**`
  - `artifacts/FEEQRY-FE-01/**`
  - `artifacts/FEEQRY-QA-01/**`
- verification:
  - `./scripts/task_validate.sh FEEQRY-BE-01`
  - `./scripts/task_validate.sh FEEQRY-FE-01`
  - `./scripts/task_validate.sh FEEQRY-QA-01`
- dependency notes: final wave after backend and frontend tasks pass

## Waves

- Wave 1: `FEEQRY-BE-01`
- Wave 2: `FEEQRY-FE-01`
- Wave 3: `FEEQRY-QA-01`

## Serialized Shared-file Decisions

- `backend/app/modules/billing/api.py` is owned only by `FEEQRY-BE-01`
- `backend/app/modules/billing/schemas.py` is owned only by `FEEQRY-BE-01`
- `backend/app/modules/billing/service.py` is owned only by `FEEQRY-BE-01`
- `frontend/src/api/billing.ts` is owned only by `FEEQRY-FE-01`
- `frontend/src/api/billing.types.ts` is owned only by `FEEQRY-FE-01`
- `frontend/src/router/index.ts` is owned only by `FEEQRY-FE-01`
- `frontend/src/constants/menu.ts` is owned only by `FEEQRY-FE-01`
