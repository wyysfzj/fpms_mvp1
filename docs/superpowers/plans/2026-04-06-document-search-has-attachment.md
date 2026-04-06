# Document Search Has Attachment Plan

Date: 2026-04-06

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: medium
- evidence_cost: medium

## chosen_runbook

- P0-frontend-heavy-story

## Batch Manifest

### Wave 1

Task:
- `DOCSEARCH-ATTACH-BE-01`

Role:
- backend worker

Closure slice:
- add `has_attachment` backend filter support to `GET /documents`

Allowlist:
- `backend/app/modules/documents/api.py`
- `backend/app/modules/documents/service.py`
- `backend/tests/test_document_specific_search_api.py`

Non-closure:
- no frontend changes
- no export
- no list column changes
- no detail changes
- no attachment generation changes

Verification:
- `python3 -m ruff check backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/tests/test_document_specific_search_api.py`
- `cd backend && pytest -q tests/test_document_specific_search_api.py`

### Wave 2

Task:
- `DOCSEARCH-ATTACH-FE-01`

Role:
- frontend worker

Closure slice:
- add a real attachment-state selector and wire it to the existing document search request

Allowlist:
- `frontend/src/api/documents.ts`
- `frontend/src/api/documents.types.ts`
- `frontend/src/modules/documents/pages/DocumentList.vue`

Non-closure:
- no backend changes
- no export
- no result-column changes
- no detail changes

Verification:
- `cd frontend && npm run lint -- src/api/documents.ts src/api/documents.types.ts src/modules/documents/pages/DocumentList.vue`
- `cd frontend && npm run typecheck`

### Wave 3

Task:
- `DOCSEARCH-ATTACH-QA-01`

Role:
- QA / close-audit worker

Closure slice:
- verify BE/FE evidence, scope compliance, and task gates

Allowlist:
- `tasks/postenhancement/backend/DOCSEARCH-ATTACH-QA-01.md`
- `artifacts/DOCSEARCH-ATTACH-BE-01/**`
- `artifacts/DOCSEARCH-ATTACH-FE-01/**`
- `artifacts/DOCSEARCH-ATTACH-QA-01/**`

Non-closure:
- no product-code changes
- no other documents residuals

Verification:
- `./scripts/task_validate.sh DOCSEARCH-ATTACH-BE-01`
- `./scripts/task_validate.sh DOCSEARCH-ATTACH-FE-01`
- `./scripts/task_validate.sh DOCSEARCH-ATTACH-QA-01`

## Serialized Shared-File Decisions

- backend documents shared files are exclusive to Wave 1
- frontend documents shared files are exclusive to Wave 2
- QA wave does not modify product files
