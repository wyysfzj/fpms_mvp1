# CASEDOCK-FS-MANIFEST-01 — Fullstack real API completion manifest

## Exact Closure Slice

Create the planning-only audit and explicit fullstack batch manifest for converting the Case Document Gate Minimal UI Mock from static UI-only Vue sections to real backend API data and backend gate enforcement.

## Explicit Non-Closure

No product backend code changes. No product frontend code changes. No database schema or migration changes. No automation harness code changes. No execution of the listed follow-up implementation tasks. No changes to the already completed UI-only Vue files.

## Remaining Follow-Up Task IDs

- `CASEDOCK-BE-GATE-RULES-01`
- `CASEDOCK-BE-INTAKE-GATE-API-01`
- `CASEDOCK-BE-CASE-GATE-API-01`
- `CASEDOCK-BE-DOC-IMPACT-API-01`
- `CASEDOCK-BE-BATCH-GATE-QUERY-01`
- `CASEDOCK-BE-BATCH-GATE-SUBMIT-01`
- `CASEDOCK-FE-GATE-API-CONTRACT-01`
- `CASEDOCK-FE-CASECREATE-API-01`
- `CASEDOCK-FE-CASEDETAIL-API-01`
- `CASEDOCK-FE-DOCIMPACT-API-01`
- `CASEDOCK-FE-BATCHFILING-API-01`
- `CASEDOCK-QA-REALAPI-E2E-01`

None of these follow-up rows may be absorbed into this planning task.

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | High. Backend shared files include `backend/app/modules/cases/api.py`, `backend/app/modules/cases/schemas.py`, `backend/app/modules/cases/service.py`, `backend/app/modules/documents/api.py`, `backend/app/modules/documents/schemas.py`, and `backend/app/modules/documents/service.py`. Frontend shared files include `frontend/src/api/cases.ts`, `frontend/src/api/cases.types.ts`, `frontend/src/api/documents.ts`, and `frontend/src/api/documents.types.ts`. |
| prereq_dependency_density | High. Frontend integration depends on backend contracts and API behavior. Batch submit enforcement depends on reusable material gate rules. Final real API evidence depends on backend, frontend, and automation readiness. |
| be_fe_coupling | High. Four existing Vue surfaces must consume backend results whose response shape is determined by the backend tasks. |
| evidence_cost | High. Each backend task needs scoped Ruff and targeted pytest. Each frontend task needs lint, typecheck, build, and browser evidence. Final QA needs FPMS Automation Skeleton Pack real API coverage. |

chosen_runbook: `P0-prereq-heavy-story`

## Current State Audit

| Area | Current state | Missing fullstack capability |
|---|---|---|
| Case create intake gate | `frontend/src/modules/cases/pages/CaseCreate.vue` shows a static "收案文件与材料核验" block created by `CASEDOCK-FE-CASECREATE-01`. | No backend intake gate endpoint. Requirement rows, missing items, gate conclusion, material roles, and suggested actions are static in the page. |
| Case detail document gate | `frontend/src/modules/cases/components/CaseDocumentsTab.vue` shows static current-node summary and event status created by `CASEDOCK-FE-CASEDETAIL-01`. | No case-level document gate endpoint. Current node material verification, matched documents, file event state, conclusion, and actions are not computed from `Document` rows. |
| Document create impact preview | `frontend/src/modules/documents/pages/DocumentCreate.vue` shows static impact preview created by `CASEDOCK-FE-DOCIMPACT-01`. | No single impact preview endpoint returning status, deadline, task, fee, file-status, confirmation, and risk impact for the pending document create form. Existing wizard preview endpoints are partial inputs only. |
| Batch filing final gate | `frontend/src/modules/cases/pages/CaseBatchFiling.vue` shows static final material gate columns and execution preview created by `CASEDOCK-FE-BATCHFILING-01`. | `GET /cases/batch-filing/candidates` returns candidates only. It does not return final material counts, missing items, hard-block status, afterfill audit requirement, or execution preview. |
| Batch filing submit enforcement | `POST /cases/batch-filing/submit` validates selection, status, and dates, then updates cases and creates side effects. | Submit does not run material gate rules and does not reject hard-block cases before the transaction mutates cases, creates documents, or creates tasks. |
| Evidence status | UI-only frontend tasks have evidence under `artifacts/CASEDOCK-FE-*` and completion audit under `artifacts/CASEDOCK-PROD-MANIFEST-01/completion_audit.md`. | No backend/API/real-data task evidence exists for this fullstack target. No final real API FPMS Automation Skeleton Pack evidence exists for this target. |

## Fullstack Design Boundary

- Reuse existing `Case`, `Document`, `DocTemplate`, `Task`, and `FeeDraft` data where possible.
- Do not add database columns or migrations in the listed tasks. If a task proves existing models cannot represent a required fact, that task must stop as `BLOCKED` and create a separate schema task instead of changing schema inside the same task.
- Material gate rules must be deterministic and SQLite-safe. Use application-side matching against existing document fields such as `doc_type`, `direction`, `title`, `doc_template_id`, `reply_to_id`, `extra_data`, attachment presence, and related case fields.
- Backend endpoints must inject permissions as function parameters with `Depends(require_perm(...))`, preserve existing response conventions, and return no request body for GET endpoints.
- Frontend tasks must preserve the current minimal UI layout and convert static values to API state with existing project loading, error, and empty-state patterns.
- New user-visible frontend text must be Simplified Chinese.

## Batch Manifest

| Wave | Task file path | Owner role | Allowed files | Required verification | Dependency notes | Exact closure slice | Explicit non-closure | Remaining follow-up task ids | Done definition |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `tasks/postenhancement/backend/CASEDOCK-BE-GATE-RULES-01.md` | backend worker | `backend/app/modules/cases/document_gate_service.py`, `backend/tests/test_case_document_gate_service.py`, `artifacts/CASEDOCK-BE-GATE-RULES-01/**` | `ruff check --fix` on allowlist Python files; `ruff format` on allowlist Python files; `ruff check` on allowlist Python files; targeted pytest for service rules; `./scripts/task_validate.sh CASEDOCK-BE-GATE-RULES-01` | First backend prerequisite. No endpoint wiring. | Add one deterministic service module for material requirement derivation, document matching, gate conclusion, hard-block classification, afterfill audit flag, and execution preview values from existing models and DTO inputs. | No FastAPI route, no Pydantic API schema, no frontend code, no schema or migration. | `CASEDOCK-BE-INTAKE-GATE-API-01`, `CASEDOCK-BE-CASE-GATE-API-01`, `CASEDOCK-BE-BATCH-GATE-QUERY-01`, `CASEDOCK-BE-BATCH-GATE-SUBMIT-01` | Service unit tests prove matched, missing, pass, warning, and hard-block outcomes without database schema changes. |
| 2 | `tasks/postenhancement/backend/CASEDOCK-BE-INTAKE-GATE-API-01.md` | backend worker | `backend/app/modules/cases/api.py`, `backend/app/modules/cases/schemas.py`, `backend/tests/test_case_intake_document_gate_api.py`, `artifacts/CASEDOCK-BE-INTAKE-GATE-API-01/**` | task-scoped Ruff; targeted pytest for intake gate API; `./scripts/task_validate.sh CASEDOCK-BE-INTAKE-GATE-API-01` | Depends on `CASEDOCK-BE-GATE-RULES-01`. Serialized ownership of `cases/api.py` and `cases/schemas.py`. | Add one GET endpoint for case intake document gate preview that returns material requirements, matched source documents, missing items, material roles, gate conclusion, and suggested actions from query inputs and existing document ids. | No case creation behavior change, no upload implementation, no batch filing behavior, no frontend code, no schema or migration. | `CASEDOCK-FE-GATE-API-CONTRACT-01`, `CASEDOCK-FE-CASECREATE-API-01` | Authenticated API test proves permission-protected 200 response and missing-material conclusion for an intake preview. |
| 2 | `tasks/postenhancement/backend/CASEDOCK-BE-DOC-IMPACT-API-01.md` | backend worker | `backend/app/modules/documents/api.py`, `backend/app/modules/documents/schemas.py`, `backend/app/modules/documents/service.py`, `backend/tests/test_document_impact_preview_api.py`, `artifacts/CASEDOCK-BE-DOC-IMPACT-API-01/**` | task-scoped Ruff; targeted pytest for impact preview API; `./scripts/task_validate.sh CASEDOCK-BE-DOC-IMPACT-API-01` | Can run after backend contract review. Serialized ownership of document shared files. | Add one POST endpoint for document create impact preview that returns status impact, deadline and task impact, fee impact, file status impact, confirmation requirements, and risk tips from the pending document create inputs. | No document creation mutation, no existing wizard endpoint behavior change, no frontend code, no schema or migration. | `CASEDOCK-FE-GATE-API-CONTRACT-01`, `CASEDOCK-FE-DOCIMPACT-API-01` | Targeted API test proves preview is read-only and returns non-empty impact groups for a seeded case/template. |
| 3 | `tasks/postenhancement/backend/CASEDOCK-BE-CASE-GATE-API-01.md` | backend worker | `backend/app/modules/cases/api.py`, `backend/app/modules/cases/schemas.py`, `backend/tests/test_case_document_gate_api.py`, `artifacts/CASEDOCK-BE-CASE-GATE-API-01/**` | task-scoped Ruff; targeted pytest for case document gate API; `./scripts/task_validate.sh CASEDOCK-BE-CASE-GATE-API-01` | Depends on `CASEDOCK-BE-GATE-RULES-01`. Must serialize with other `cases/api.py` and `cases/schemas.py` tasks. | Add one GET endpoint for case detail document gate that returns current-node material verification, matched documents, missing items, document event status, gate conclusion, and suggested actions for one case id. | No batch filing submit behavior, no document create preview, no frontend code, no schema or migration. | `CASEDOCK-FE-GATE-API-CONTRACT-01`, `CASEDOCK-FE-CASEDETAIL-API-01` | Targeted API test proves case documents change the returned matched and missing status. |
| 3 | `tasks/postenhancement/backend/CASEDOCK-BE-BATCH-GATE-QUERY-01.md` | backend worker | `backend/app/modules/cases/service.py`, `backend/app/modules/cases/schemas.py`, `backend/tests/test_case_batch_filing_document_gate_query.py`, `artifacts/CASEDOCK-BE-BATCH-GATE-QUERY-01/**` | task-scoped Ruff; targeted pytest for batch filing candidate gate fields; `./scripts/task_validate.sh CASEDOCK-BE-BATCH-GATE-QUERY-01` | Depends on `CASEDOCK-BE-GATE-RULES-01`. Must serialize with other `cases/schemas.py` tasks. | Extend the existing batch filing candidates query behavior so each candidate includes final material count, missing items, gate conclusion, hard-block status, afterfill audit requirement, and execution preview data. | No submit mutation changes, no route path change, no frontend code, no schema or migration. | `CASEDOCK-BE-BATCH-GATE-SUBMIT-01`, `CASEDOCK-FE-GATE-API-CONTRACT-01`, `CASEDOCK-FE-BATCHFILING-API-01` | Existing candidate query tests still pass and new targeted test proves one pass row and one hard-block row are distinguishable from backend data. |
| 4 | `tasks/postenhancement/backend/CASEDOCK-BE-BATCH-GATE-SUBMIT-01.md` | backend worker | `backend/app/modules/cases/service.py`, `backend/tests/test_case_batch_filing_document_gate_submit.py`, `artifacts/CASEDOCK-BE-BATCH-GATE-SUBMIT-01/**` | task-scoped Ruff; targeted pytest proving hard-block rejection; `./scripts/task_validate.sh CASEDOCK-BE-BATCH-GATE-SUBMIT-01` | Depends on `CASEDOCK-BE-GATE-RULES-01` and `CASEDOCK-BE-BATCH-GATE-QUERY-01`. Serialized ownership of `cases/service.py`. | Update the existing batch filing submit service so selected hard-block cases are rejected before any case status, document, or task mutation occurs. | No candidate query response changes, no frontend code, no schema or migration. | `CASEDOCK-QA-REALAPI-E2E-01` | Targeted pytest proves hard-block submit returns a business error and leaves selected case status and side effects unchanged. |
| 5 | `tasks/postenhancement/frontend/CASEDOCK-FE-GATE-API-CONTRACT-01.md` | frontend worker | `frontend/src/api/cases.ts`, `frontend/src/api/cases.types.ts`, `frontend/src/api/documents.ts`, `frontend/src/api/documents.types.ts`, `artifacts/CASEDOCK-FE-GATE-API-CONTRACT-01/**` | `npm --prefix frontend run lint`; `npm --prefix frontend run typecheck`; `npm --prefix frontend run build`; `./scripts/task_validate.sh CASEDOCK-FE-GATE-API-CONTRACT-01` | Depends on all backend API contract tasks. Serialized frontend shared API ownership. | Add frontend API client functions and types for intake gate, case document gate, document impact preview, and batch filing gate fields. | No Vue page behavior changes, no backend code, no route/store changes. | `CASEDOCK-FE-CASECREATE-API-01`, `CASEDOCK-FE-CASEDETAIL-API-01`, `CASEDOCK-FE-DOCIMPACT-API-01`, `CASEDOCK-FE-BATCHFILING-API-01` | Typecheck proves consumers can import the new contract without runtime implementation in page files. |
| 6 | `tasks/postenhancement/frontend/CASEDOCK-FE-CASECREATE-API-01.md` | frontend worker | `frontend/src/modules/cases/pages/CaseCreate.vue`, `artifacts/CASEDOCK-FE-CASECREATE-API-01/**` | `npm --prefix frontend run lint`; `npm --prefix frontend run typecheck`; `npm --prefix frontend run build`; browser smoke for `/cases/new`; `./scripts/task_validate.sh CASEDOCK-FE-CASECREATE-API-01` | Depends on `CASEDOCK-FE-GATE-API-CONTRACT-01` and `CASEDOCK-BE-INTAKE-GATE-API-01`. | Replace static intake material gate values in the existing Case Create minimal UI section with real intake gate API data, including loading, error, and empty states. | No create payload change, no upload implementation, no layout redesign, no backend code. | `CASEDOCK-QA-REALAPI-E2E-01` | Browser/API evidence proves the section renders API-provided material requirements and no hardcoded gate conclusion remains. |
| 6 | `tasks/postenhancement/frontend/CASEDOCK-FE-CASEDETAIL-API-01.md` | frontend worker | `frontend/src/modules/cases/components/CaseDocumentsTab.vue`, `artifacts/CASEDOCK-FE-CASEDETAIL-API-01/**` | `npm --prefix frontend run lint`; `npm --prefix frontend run typecheck`; `npm --prefix frontend run build`; browser smoke for a case detail documents tab; `./scripts/task_validate.sh CASEDOCK-FE-CASEDETAIL-API-01` | Depends on `CASEDOCK-FE-GATE-API-CONTRACT-01` and `CASEDOCK-BE-CASE-GATE-API-01`. | Replace static case detail document gate and file event status values with real case document gate API data. | No document list endpoint change, no upload implementation, no layout redesign, no backend code. | `CASEDOCK-QA-REALAPI-E2E-01` | Browser/API evidence proves matched and missing material rows come from API data for the selected case. |
| 6 | `tasks/postenhancement/frontend/CASEDOCK-FE-DOCIMPACT-API-01.md` | frontend worker | `frontend/src/modules/documents/pages/DocumentCreate.vue`, `artifacts/CASEDOCK-FE-DOCIMPACT-API-01/**` | `npm --prefix frontend run lint`; `npm --prefix frontend run typecheck`; `npm --prefix frontend run build`; browser smoke for document create; `./scripts/task_validate.sh CASEDOCK-FE-DOCIMPACT-API-01` | Depends on `CASEDOCK-FE-GATE-API-CONTRACT-01` and `CASEDOCK-BE-DOC-IMPACT-API-01`. | Replace static document impact preview values with real impact preview API data driven by case, document type, template, and reply source fields. | No document create submit mutation change, no layout redesign, no backend code. | `CASEDOCK-QA-REALAPI-E2E-01` | Browser/API evidence proves impact groups refresh from API input changes and no static impact summary remains. |
| 6 | `tasks/postenhancement/frontend/CASEDOCK-FE-BATCHFILING-API-01.md` | frontend worker | `frontend/src/modules/cases/pages/CaseBatchFiling.vue`, `artifacts/CASEDOCK-FE-BATCHFILING-API-01/**` | `npm --prefix frontend run lint`; `npm --prefix frontend run typecheck`; `npm --prefix frontend run build`; browser smoke for batch filing; `./scripts/task_validate.sh CASEDOCK-FE-BATCHFILING-API-01` | Depends on `CASEDOCK-FE-GATE-API-CONTRACT-01`, `CASEDOCK-BE-BATCH-GATE-QUERY-01`, and `CASEDOCK-BE-BATCH-GATE-SUBMIT-01`. | Replace static batch filing final gate columns and execution preview with real API data, and keep hard-block UI aligned with backend submit rejection. | No route/menu change, no layout redesign, no backend code. | `CASEDOCK-QA-REALAPI-E2E-01` | Browser/API evidence proves a hard-block backend row is disabled or blocked in UI and submit rejection is surfaced in Simplified Chinese. |
| 7 | `tasks/postenhancement/qa/CASEDOCK-QA-REALAPI-E2E-01.md` | monitor worker | `FPMS_Automation_Skeleton_Pack/pytest_python/**`, `FPMS_Automation_Skeleton_Pack/playwright_ts/**`, `artifacts/CASEDOCK-QA-REALAPI-E2E-01/**`, `artifacts/CASEDOCK-FULLSTACK-CLOSE-AUDIT-01/**` | FPMS Automation Skeleton Pack real API smoke covering the four Case Document Gate surfaces; `npm --prefix frontend run lint`; `npm --prefix frontend run typecheck`; `npm --prefix frontend run build`; backend targeted pytest list from backend tasks; `./scripts/task_validate.sh CASEDOCK-QA-REALAPI-E2E-01` | Runs after backend and frontend tasks pass. If skeleton pack lacks a required real API capability, make only the smallest harness enhancement inside this task's allowlist and record evidence. | Add or update final real API integration evidence so the four UI surfaces and backend hard-block submit are verified against real API behavior, then write a close audit mapping prompt requirements to files, APIs, tests, and evidence. | No product feature changes except a harness-only fix that is required to run real API evidence. No static network interception as completion evidence. No new dependencies. | None | Final audit proves every prompt requirement is mapped to evidence, records "Prettier not applicable" when the project still has no Prettier config/script/dependency, and identifies no residual in-scope gap. |

## Execution Waves

- Wave 1 freezes reusable backend gate rules before endpoint work.
- Waves 2 through 4 serialize backend shared file ownership where required.
- Wave 5 serializes frontend API client and type ownership.
- Wave 6 can run page integration tasks only when they do not edit the same Vue file.
- Wave 7 is the final real API QA and close audit.

## Serialized Shared-File Decisions

- `backend/app/modules/cases/api.py` is serialized across intake gate and case detail gate endpoint tasks.
- `backend/app/modules/cases/schemas.py` is serialized across cases endpoint and batch query tasks.
- `backend/app/modules/cases/service.py` is serialized across batch query and batch submit tasks.
- `backend/app/modules/documents/api.py`, `backend/app/modules/documents/schemas.py`, and `backend/app/modules/documents/service.py` are owned only by the document impact preview task in this manifest.
- `frontend/src/api/cases.ts`, `frontend/src/api/cases.types.ts`, `frontend/src/api/documents.ts`, and `frontend/src/api/documents.types.ts` are owned by one frontend API contract task before Vue page tasks begin.
- Each Vue page task owns exactly one existing Vue file.
- SQLite-writing backend tests and final skeleton tests must run serialized.

## Allowed Files

- `tasks/postenhancement/backend/CASEDOCK-FS-MANIFEST-01.md`
- `artifacts/CASEDOCK-FS-MANIFEST-01/**`

## Verification Commands

- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postenhancement/backend/CASEDOCK-FS-MANIFEST-01.md`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate CASEDOCK-FS-MANIFEST-01`
- `./scripts/task_validate.sh CASEDOCK-FS-MANIFEST-01`

## Evidence Path

- `artifacts/CASEDOCK-FS-MANIFEST-01/`
