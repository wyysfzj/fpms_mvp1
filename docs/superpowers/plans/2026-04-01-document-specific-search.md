# P2 #19 Document-specific Search Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the first-round executable spec 9.3.2 document-specific search on top of the existing documents list/query, using the frozen mapping from `DOCSEARCH-PRE-01`.

**Architecture:** Execute this as a frontend-heavy story with serialized backend-then-frontend ownership. Backend first closes the executable contract for `template_code / doc_name / case_no / need_reply / replied / date / direction`; frontend then wires the same contract into the existing document list page and shared documents api/types; QA finally audits evidence and close scope.

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

### DOCSEARCH-BE-01

- task file path: `tasks/postenhancement/backend/DOCSEARCH-BE-01.md`
- closure slice: implement the first-round document-specific search backend contract with the frozen executable mapping for `TemplateCode` -> `DocTemplate.code`, `DocName` -> `Document.title`, `NeedReply` -> `Document.need_reply`, `已Reply/Reply` -> `Document.reply_date is not null`, plus `case_no`, `date`, and `direction`
- explicit non-closure: no frontend, no `DocType` independent carrier/filter, no dispatch/reply linkage, no summary/export/reporting, no OCR/full-text, no schema changes
- allowlist:
  - `backend/app/modules/documents/api.py`
  - `backend/app/modules/documents/schemas.py`
  - `backend/app/modules/documents/service.py`
  - `backend/tests/test_document_specific_search_api.py`
- verification:
  - `python3 -m ruff check backend/app/modules/documents/api.py backend/app/modules/documents/schemas.py backend/app/modules/documents/service.py backend/tests/test_document_specific_search_api.py`
  - `cd backend && PYTHONPATH=. pytest -q tests/test_document_specific_search_api.py`
  - `./scripts/task_validate.sh DOCSEARCH-BE-01`
- dependency notes: prerequisite mapping already closed in `DOCSEARCH-PRE-01`; owns documents backend query files

### DOCSEARCH-FE-01

- task file path: `tasks/postenhancement/frontend/DOCSEARCH-FE-01.md`
- closure slice: implement the frozen document-specific filters and projection wiring in `DocumentList.vue` plus shared documents FE api/types for `template_code / doc_name / case_no / need_reply / replied / date / direction`
- explicit non-closure: no new page/system, no `DocType` UI closure, no dispatch/reply view, no summary/export/print, no reporting/dashboard, no OCR/full-text UI
- allowlist:
  - `frontend/src/api/documents.ts`
  - `frontend/src/api/documents.types.ts`
  - `frontend/src/modules/documents/pages/DocumentList.vue`
- verification:
  - `cd frontend && npm run lint -- src/api/documents.ts src/api/documents.types.ts src/modules/documents/pages/DocumentList.vue`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh DOCSEARCH-FE-01`
- dependency notes: serialize after `DOCSEARCH-BE-01`; owns shared documents FE api/types and the existing document list page

### DOCSEARCH-QA-01

- task file path: `tasks/postenhancement/backend/DOCSEARCH-QA-01.md`
- closure slice: gate audit, evidence audit, and story close summary for `P2 #19` first-round executable document-specific search story
- explicit non-closure: no product code changes
- allowlist:
  - `artifacts/DOCSEARCH-BE-01/**`
  - `artifacts/DOCSEARCH-FE-01/**`
  - `artifacts/DOCSEARCH-QA-01/**`
- verification:
  - `./scripts/task_validate.sh DOCSEARCH-BE-01`
  - `./scripts/task_validate.sh DOCSEARCH-FE-01`
  - `./scripts/task_validate.sh DOCSEARCH-QA-01`
- dependency notes: final wave after backend and frontend tasks pass

## Waves

- Wave 1: `DOCSEARCH-BE-01`
- Wave 2: `DOCSEARCH-FE-01`
- Wave 3: `DOCSEARCH-QA-01`

## Serialized Shared-file Decisions

- `backend/app/modules/documents/api.py` is owned only by `DOCSEARCH-BE-01`
- `backend/app/modules/documents/schemas.py` is owned only by `DOCSEARCH-BE-01`
- `backend/app/modules/documents/service.py` is owned only by `DOCSEARCH-BE-01`
- `frontend/src/api/documents.ts` is owned only by `DOCSEARCH-FE-01`
- `frontend/src/api/documents.types.ts` is owned only by `DOCSEARCH-FE-01`
- `frontend/src/modules/documents/pages/DocumentList.vue` is owned only by `DOCSEARCH-FE-01`
