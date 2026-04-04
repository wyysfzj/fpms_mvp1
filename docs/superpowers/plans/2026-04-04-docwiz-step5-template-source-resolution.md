# DOCWIZ-STEP5-TEMPLATE-SOURCE-01 Plan

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `backend prerequisite implementation before Step 5 final submit integration`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Batch Manifest

| Task ID | Owner | Allowlist | Dependency Notes | Exact Closure Slice | Explicit Non-closure |
|---|---|---|---|---|---|
| `DOCWIZ-STEP5-TEMPLATE-SOURCE-01` | main thread | `backend/app/modules/documents/service.py`, `backend/tests/test_document_wizard_template_source_resolution.py`, `docs/superpowers/specs/2026-04-04-docwiz-step5-template-source-resolution-design.md`, `docs/superpowers/plans/2026-04-04-docwiz-step5-template-source-resolution.md`, `tasks/postenhancement/backend/DOCWIZ-STEP5-TEMPLATE-SOURCE-01.md` | Depends on `DOCWIZ-STEP5-PREREQ-01`; must not absorb final attachment write work | Implement deterministic `DocTemplate -> Template.file_path` resolution rule for Step 5 prerequisites | No attachment persistence, no final submit integration, no schema change |
| `DOCWIZ-QA-STEP5-TEMPLATE-SOURCE-01` | main thread | `artifacts/DOCWIZ-STEP5-TEMPLATE-SOURCE-01/**`, `artifacts/DOCWIZ-QA-STEP5-TEMPLATE-SOURCE-01/**`, `tasks/postenhancement/backend/DOCWIZ-QA-STEP5-TEMPLATE-SOURCE-01.md` | Runs after resolver task artifacts exist | Audit resolver evidence and close summary | No product-code change beyond QA artifacts |

## Verification

- `ruff check --fix backend/app/modules/documents/service.py backend/tests/test_document_wizard_template_source_resolution.py`
- `ruff format backend/app/modules/documents/service.py backend/tests/test_document_wizard_template_source_resolution.py`
- `ruff check backend/app/modules/documents/service.py backend/tests/test_document_wizard_template_source_resolution.py`
- `cd backend && pytest -q tests/test_document_wizard_template_source_resolution.py`
- `./scripts/task_validate.sh DOCWIZ-STEP5-TEMPLATE-SOURCE-01`
- `./scripts/task_validate.sh DOCWIZ-QA-STEP5-TEMPLATE-SOURCE-01`

## Done Definition

- deterministic resolver rule is implemented
- failure semantics are explicit and tested
- no schema/API changes were absorbed
- required artifacts exist and both task gates pass
