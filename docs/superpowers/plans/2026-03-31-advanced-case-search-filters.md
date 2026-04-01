# P2 #18 Advanced Case Search Filters Implementation Plan (Post-Prerequisite)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reopen `P2 #18` after prerequisite closure and finish the follow-up query enhancement story: extend `GET /cases` and the existing case list filters with `applicant_id`, `patent_no`, and `fee_status`.

**Architecture:** Execute this as a frontend-heavy chained story. First extend the backend case query contract and service filter logic, then wire the new filters into the existing frontend case list page and API types, then close with QA/evidence audit.

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

### CASEFILTER-BE-01

- task file path: `tasks/postenhancement/backend/CASEFILTER-BE-01.md`
- closure slice: extend `GET /cases` backend query contract and service logic with `applicant_id`, `patent_no`, and minimal derived `fee_status`
- explicit non-closure: no frontend changes, no new page, no export/reporting, no fee drill-down, no list projection change
- allowlist:
  - `backend/app/modules/cases/api.py`
  - `backend/app/modules/cases/service.py`
  - `backend/tests/test_case_advanced_filters_api.py`
- verification:
  - `python3 -m ruff check backend/app/modules/cases/api.py backend/app/modules/cases/service.py backend/tests/test_case_advanced_filters_api.py`
  - `cd backend && PYTHONPATH=. pytest -q tests/test_case_advanced_filters_api.py`
  - `./scripts/task_validate.sh CASEFILTER-BE-01`
- dependency notes: first wave; FE depends on stabilized backend contract

### CASEFILTER-FE-01

- task file path: `tasks/postenhancement/frontend/CASEFILTER-FE-01.md`
- closure slice: add `applicant_id`, `patent_no`, and `fee_status` filters to the existing case list UI and frontend API/types wiring
- explicit non-closure: no backend changes, no new page, no summary/export/reporting, no applicant selector deep linkage
- allowlist:
  - `frontend/src/api/cases.ts`
  - `frontend/src/api/cases.types.ts`
  - `frontend/src/modules/cases/pages/CaseList.vue`
- verification:
  - `cd frontend && npm run lint -- src/api/cases.ts src/api/cases.types.ts src/modules/cases/pages/CaseList.vue`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh CASEFILTER-FE-01`
- dependency notes: serialize after `CASEFILTER-BE-01`

### CASEFILTER-QA-01

- task file path: `tasks/postenhancement/backend/CASEFILTER-QA-01.md`
- closure slice: gate audit, evidence audit, and close summary for the reopened case-filter query enhancement story
- explicit non-closure: no product code changes
- allowlist:
  - `artifacts/CASEFILTER-BE-01/**`
  - `artifacts/CASEFILTER-FE-01/**`
  - `artifacts/CASEFILTER-QA-01/**`
- verification:
  - `./scripts/task_validate.sh CASEFILTER-BE-01`
  - `./scripts/task_validate.sh CASEFILTER-FE-01`
  - `./scripts/task_validate.sh CASEFILTER-QA-01`
- dependency notes: final wave after BE and FE slices pass

## Waves

- Wave 1: `CASEFILTER-BE-01`
- Wave 2: `CASEFILTER-FE-01`
- Wave 3: `CASEFILTER-QA-01`

## Serialized Shared-file Decisions

- `backend/app/modules/cases/api.py` is owned only by `CASEFILTER-BE-01`
- `backend/app/modules/cases/service.py` is owned only by `CASEFILTER-BE-01`
- `frontend/src/api/cases.ts` is owned only by `CASEFILTER-FE-01`
- `frontend/src/api/cases.types.ts` is owned only by `CASEFILTER-FE-01`
- `frontend/src/modules/cases/pages/CaseList.vue` is owned only by `CASEFILTER-FE-01`
