# PD-ENH-P1-DEV-MANIFEST-20260531-01 — Post-demo P1 full-scope development manifest

Status: Ready for user approval before execution

## Exact Closure Slice

Coordinate the full P1 development scope from `docs/postdemo/postdemo_p1_functional_spec_20260531.md` by decomposing it into atomic implementation task files with wave order, dependencies, allowlists, required verification, and user confirmation gates.

## Explicit Non-Closure

No backend product code changes. No frontend product code changes. No database migration execution. No CPC/OA direct submit, RPA, email sending, automatic payment, or execution of any listed follow-up implementation task.

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | High. Multiple tasks touch shared module files, migrations, frontend API clients/types, router, and menu. |
| prereq_dependency_density | High. Data carriers and services must precede API and UI work. |
| be_fe_coupling | High. UI tasks depend on backend contracts and status semantics. |
| evidence_cost | High. Full scope requires backend, frontend, browser, and final ledger evidence. |

chosen_runbook: `P0-prereq-heavy-story`

## Global Non-Scope

- No direct CPC / 专利业务办理系统 submission.
- No automatic official-site login, signature, QR scan, click-submit, or RPA.
- No official receipt auto-download.
- No automatic official-fee payment.
- No replacement of Longxia email sending.
- No broad redesign or unrelated refactor.

## Execution Gate

After each wave, and after each task when executing inline, stop and ask the user whether to continue. Do not proceed silently.

## Batch Manifest

| Wave | Task File Path | Owner Role | Dependency Notes | Exact Closure Slice | Explicit Non-Closure |
|---|---|---|---|---|---|
| 1 | `tasks/postdemo/PD-P1-DB-CASE-OFFICIAL-FIELDS-01.md` | backend worker | First schema prerequisite. Serialize Alembic ownership. | Add applicant/inventor official field carriers. | No API/UI behavior. |
| 1 | `tasks/postdemo/PD-P1-DB-ATTACHMENT-MANIFEST-01.md` | backend worker | After case field carrier or serialized with migration ownership. | Add attachment official role/manifest carriers. | No upload UI or package API. |
| 1 | `tasks/postdemo/PD-P1-DB-WORK-PACKAGE-01.md` | backend worker | After migration head is stable. | Add work-package/checklist/receipt/override carriers. | No API/UI workflow. |
| 1 | `tasks/postdemo/PD-P1-DB-FEE-OFFICIAL-CARRIERS-01.md` | backend worker | Serialize fees/annuity carrier ownership. | Add fee checklist/template-compatibility carriers. | No auto-payment or official Excel export promise. |
| 1 | `tasks/postdemo/PD-P1-DB-LETTER-HANDOFF-CARRIERS-01.md` | backend worker | Serialize documents/templates carrier ownership. | Add format-letter mapping and handoff carriers. | No email sending. |
| 2 | `tasks/postdemo/PD-P1-BE-CASE-OFFICIAL-FIELDS-API-01.md` | backend worker | Depends on case official field DB task. | Expose official fields through existing case APIs. | No package workflow. |
| 2 | `tasks/postdemo/PD-P1-BE-ATTACHMENT-MANIFEST-SERVICE-01.md` | backend worker | Depends on attachment manifest DB task. | Add deterministic attachment manifest role service. | No route or UI. |
| 2 | `tasks/postdemo/PD-P1-BE-WORK-PACKAGE-SERVICE-01.md` | backend worker | Depends on work-package DB task. | Add package status/checklist/receipt service rules. | No route or UI. |
| 3 | `tasks/postdemo/PD-P1-BE-FILING-PACKAGE-API-01.md` | backend worker | Depends on case fields, attachment service, package service. | Add filing preparation API resource. | No CPC XML/direct submit. |
| 3 | `tasks/postdemo/PD-P1-BE-OA-PACKAGE-API-01.md` | backend worker | Depends on package service and document reply-chain base. | Add OA reply package API resource. | No official-site automation. |
| 3 | `tasks/postdemo/PD-P1-BE-RECEIPT-ARCHIVE-API-01.md` | backend worker | Depends on package service. | Add receipt metadata/archive/override API. | No receipt OCR or auto-download. |
| 3 | `tasks/postdemo/PD-P1-BE-FEE-LINKAGE-API-01.md` | backend worker | Depends on fee carriers. | Add fee linkage/checklist API. | No official payment execution. |
| 3 | `tasks/postdemo/PD-P1-BE-LETTER-HANDOFF-API-01.md` | backend worker | Depends on letter carriers. | Add format-letter mapping/handoff API. | No Longxia sending. |
| 4 | `tasks/postdemo/PD-P1-FE-API-CONTRACTS-01.md` | frontend worker | Depends on backend API tasks. | Add frontend API clients/types. | No Vue page behavior. |
| 4 | `tasks/postdemo/PD-P1-FE-NAV-ROUTES-01.md` | frontend worker | After target page paths are frozen. Serialize router/menu. | Add official workflow routes/menu entries. | No page implementation. |
| 5 | `tasks/postdemo/PD-P1-FE-CASE-OFFICIAL-FIELDS-01.md` | frontend worker | Depends on frontend API contracts and case backend API. | Add official fields/gates to case create/edit. | No filing package page. |
| 5 | `tasks/postdemo/PD-P1-FE-ATTACHMENT-GATES-01.md` | frontend worker | Depends on attachment manifest API contract. | Add attachment official role/gate UI. | No file conversion. |
| 5 | `tasks/postdemo/PD-P1-FE-FILING-PREP-01.md` | frontend worker | Depends on filing API, routes, attachment gates. | Add filing preparation page. | No direct official submission. |
| 5 | `tasks/postdemo/PD-P1-FE-OA-PACKAGE-01.md` | frontend worker | Depends on OA package API and routes. | Add OA reply package page. | No auto-fill official site. |
| 5 | `tasks/postdemo/PD-P1-FE-RECEIPT-ARCHIVE-01.md` | frontend worker | Depends on receipt API. | Add receipt archive UI. | No receipt auto-download/OCR. |
| 5 | `tasks/postdemo/PD-P1-FE-FEE-LINKAGE-01.md` | frontend worker | Depends on fee API. | Add fee linkage/checklist UI. | No payment execution. |
| 5 | `tasks/postdemo/PD-P1-FE-LETTER-HANDOFF-01.md` | frontend worker | Depends on letter API. | Add format-letter/Longxia handoff UI. | No email sending. |
| 6 | `tasks/postdemo/PD-P1-QA-FULLSCOPE-E2E-01.md` | monitor | Runs after all implementation task gates pass. | Final QA and item-to-slice ledger. | No feature implementation except harness-only fixes inside allowlist. |

## Serialized Shared-File Decisions

- Alembic migration tasks run one at a time.
- `backend/app/modules/cases/models.py`, `schemas.py`, and `api.py` are serialized across case official field tasks.
- `backend/app/modules/documents/models.py`, `schemas.py`, `service.py`, and `api.py` are serialized across attachment, OA, receipt, and letter work.
- `backend/app/modules/official_workflows/**` is serialized for service/API tasks unless the lead creates non-overlapping files and confirms no shared ownership conflict.
- `frontend/src/api/*.ts` and `frontend/src/api/*.types.ts` are owned by `PD-P1-FE-API-CONTRACTS-01` before Vue page tasks.
- `frontend/src/router/index.ts` and `frontend/src/constants/menu.ts` are owned by `PD-P1-FE-NAV-ROUTES-01`.
- SQLite-writing backend tests and final full-scope tests run serialized.

## Verification

Every implementation task must:

- run task-scoped lint/format checks on allowlist files;
- run targeted tests defined in its task file;
- write `artifacts/<TASK-ID>/results.jsonl`, `summary.md`, and `git/diff.patch`;
- run `./scripts/task_validate.sh <TASK-ID>`;
- report PASS/FAIL/BLOCKED with exact closure and non-closure.

## Stop Rule

This manifest authorizes planning only until the user explicitly approves execution. During execution, each next wave requires explicit user confirmation.
