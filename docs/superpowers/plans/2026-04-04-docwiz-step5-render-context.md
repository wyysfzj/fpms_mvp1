# DOCWIZ-STEP5-RENDER-CONTEXT-01 Plan

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `backend prerequisite implementation before Step 5 final submit integration`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Batch Manifest

| Task ID | Owner | Allowlist | Dependency Notes | Exact Closure Slice | Explicit Non-closure |
|---|---|---|---|---|---|
| `DOCWIZ-STEP5-RENDER-CONTEXT-01` | main thread | `backend/app/modules/documents/service.py`, `backend/tests/test_document_template_render_context.py`, `docs/superpowers/specs/2026-04-04-docwiz-step5-render-context-design.md`, `docs/superpowers/plans/2026-04-04-docwiz-step5-render-context.md`, `tasks/postenhancement/backend/DOCWIZ-STEP5-RENDER-CONTEXT-01.md` | Must stay below final submit integration | Implement document-template render context helper only | No renderer invocation, no persistence, no final submit integration |
| `DOCWIZ-QA-STEP5-RENDER-CONTEXT-01` | main thread | `artifacts/DOCWIZ-STEP5-RENDER-CONTEXT-01/**`, `artifacts/DOCWIZ-QA-STEP5-RENDER-CONTEXT-01/**`, `tasks/postenhancement/backend/DOCWIZ-QA-STEP5-RENDER-CONTEXT-01.md` | Runs after helper artifacts exist | Audit render-context evidence and close summary | No product-code change beyond QA artifacts |

## Verification

- `ruff check --fix backend/app/modules/documents/service.py backend/tests/test_document_template_render_context.py`
- `ruff format backend/app/modules/documents/service.py backend/tests/test_document_template_render_context.py`
- `ruff check backend/app/modules/documents/service.py backend/tests/test_document_template_render_context.py`
- `cd backend && pytest -q tests/test_document_template_render_context.py`
- `./scripts/task_validate.sh DOCWIZ-STEP5-RENDER-CONTEXT-01`
- `./scripts/task_validate.sh DOCWIZ-QA-STEP5-RENDER-CONTEXT-01`

## Done Definition

- documents render-context helper exists
- helper returns stable field set from `Document + Case + Client`
- targeted tests pass
- required artifacts exist and both task gates pass
