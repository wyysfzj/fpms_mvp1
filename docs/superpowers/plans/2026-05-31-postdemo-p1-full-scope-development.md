# Post-Demo P1 Full-Scope Development Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the full P1 enhancement scope from `docs/postdemo/postdemo_p1_functional_spec_20260531.md` without falling back to long-term submit-time re-entry workarounds.

**Architecture:** Add a small official-work-package layer that reuses existing FPMS case, document, task, fee, template, attachment, and dispatch models. Stable official fields are maintained in existing case/applicant/inventor and agent-related surfaces; filing and OA package screens primarily verify completeness, manage checklist/manifest state, and archive receipts.

**Tech Stack:** FastAPI, SQLAlchemy, Alembic, SQLite-compatible migrations, pytest, Vue 3, TypeScript, Element Plus, existing FPMS API clients, atomic evidence gates.

---

## Source Spec

- Functional Spec: `docs/postdemo/postdemo_p1_functional_spec_20260531.md`
- Analysis: `docs/postdemo/postdemo_enhancement_analysis_20260530.md`
- Batch Manifest: `tasks/postdemo/PD-ENH-P1-DEV-MANIFEST-20260531-01.md`

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | High. Shared surfaces include `cases`, `documents`, `fees`, `annuity`, `templates`, frontend API clients/types, router/menu, and Alembic heads. |
| prereq_dependency_density | High. Official fields, attachment manifest roles, work-package carriers, state semantics, and permissions must land before UI and final QA. |
| be_fe_coupling | High. Frontend cannot be truthful until backend contracts expose official fields, package checklists, file roles, receipt metadata, fee linkage, and letter handoff. |
| evidence_cost | High. Every backend task needs scoped Ruff and targeted pytest; every frontend task needs lint/type/build plus browser evidence; final QA needs an item-to-slice ledger. |

chosen_runbook: `P0-prereq-heavy-story`

## Execution Rule

After each task or wave, the lead must stop and ask the user whether to execute the next task/wave. Do not continue silently.

## File Structure

Planned backend additions:

- `backend/app/modules/official_workflows/` owns P1 work-package APIs, service logic, status transitions, checklists, manifest rows, receipt metadata, and override audit.
- `backend/app/modules/cases/**` remains source of truth for case, applicant, and inventor official fields.
- `backend/app/modules/documents/**` remains source of truth for documents and attachments; P1 adds official attachment roles/manifest metadata instead of a detached upload store.
- `backend/app/modules/fees/**` and `backend/app/modules/annuity/**` remain fee/pay-list bases; P1 adds official-payment-template compatibility metadata and checklist state.
- `backend/app/modules/templates/**`, `documents` dispatch, and `clients` contacts remain bases for format letter and Longxia handoff.

Planned frontend additions:

- Existing case create/edit/detail pages expose official fields and new-case gates.
- New official workflow pages/components show filing preparation, OA reply package, receipt archive, fee linkage, and letter handoff.
- Shared frontend API clients/types are updated once, then page tasks consume them.
- User-facing UI text remains Simplified Chinese.

## Batch Tasks

| Wave | Task ID | Task File | Owner | Purpose |
|---|---|---|---|---|
| 1 | `PD-P1-DB-CASE-OFFICIAL-FIELDS-01` | `tasks/postdemo/PD-P1-DB-CASE-OFFICIAL-FIELDS-01.md` | backend worker | Add SQLite-safe official applicant/inventor field carriers. |
| 1 | `PD-P1-DB-ATTACHMENT-MANIFEST-01` | `tasks/postdemo/PD-P1-DB-ATTACHMENT-MANIFEST-01.md` | backend worker | Add official attachment role, hash, upload-position carriers. |
| 1 | `PD-P1-DB-WORK-PACKAGE-01` | `tasks/postdemo/PD-P1-DB-WORK-PACKAGE-01.md` | backend worker | Add official work-package, checklist, receipt, override carrier tables. |
| 1 | `PD-P1-DB-FEE-OFFICIAL-CARRIERS-01` | `tasks/postdemo/PD-P1-DB-FEE-OFFICIAL-CARRIERS-01.md` | backend worker | Add official fee compatibility/checklist carriers without changing payment behavior. |
| 1 | `PD-P1-DB-LETTER-HANDOFF-CARRIERS-01` | `tasks/postdemo/PD-P1-DB-LETTER-HANDOFF-CARRIERS-01.md` | backend worker | Add letter mapping/handoff carriers for format函 and Longxia handoff. |
| 2 | `PD-P1-BE-CASE-OFFICIAL-FIELDS-API-01` | `tasks/postdemo/PD-P1-BE-CASE-OFFICIAL-FIELDS-API-01.md` | backend worker | Expose official fields through existing case APIs. |
| 2 | `PD-P1-BE-ATTACHMENT-MANIFEST-SERVICE-01` | `tasks/postdemo/PD-P1-BE-ATTACHMENT-MANIFEST-SERVICE-01.md` | backend worker | Add attachment role/manifest service rules. |
| 2 | `PD-P1-BE-WORK-PACKAGE-SERVICE-01` | `tasks/postdemo/PD-P1-BE-WORK-PACKAGE-SERVICE-01.md` | backend worker | Add package status, checklist, receipt, and override service rules. |
| 3 | `PD-P1-BE-FILING-PACKAGE-API-01` | `tasks/postdemo/PD-P1-BE-FILING-PACKAGE-API-01.md` | backend worker | Add filing-preparation package API. |
| 3 | `PD-P1-BE-OA-PACKAGE-API-01` | `tasks/postdemo/PD-P1-BE-OA-PACKAGE-API-01.md` | backend worker | Add OA reply package API. |
| 3 | `PD-P1-BE-RECEIPT-ARCHIVE-API-01` | `tasks/postdemo/PD-P1-BE-RECEIPT-ARCHIVE-API-01.md` | backend worker | Add receipt metadata/archive/override API. |
| 3 | `PD-P1-BE-FEE-LINKAGE-API-01` | `tasks/postdemo/PD-P1-BE-FEE-LINKAGE-API-01.md` | backend worker | Add fee checklist and official-template compatibility API. |
| 3 | `PD-P1-BE-LETTER-HANDOFF-API-01` | `tasks/postdemo/PD-P1-BE-LETTER-HANDOFF-API-01.md` | backend worker | Add format-letter mapping and Longxia handoff API. |
| 4 | `PD-P1-FE-API-CONTRACTS-01` | `tasks/postdemo/PD-P1-FE-API-CONTRACTS-01.md` | frontend worker | Add frontend API clients/types for P1 backend contracts. |
| 4 | `PD-P1-FE-NAV-ROUTES-01` | `tasks/postdemo/PD-P1-FE-NAV-ROUTES-01.md` | frontend worker | Add serialized route/menu entries. |
| 5 | `PD-P1-FE-CASE-OFFICIAL-FIELDS-01` | `tasks/postdemo/PD-P1-FE-CASE-OFFICIAL-FIELDS-01.md` | frontend worker | Add official fields and new-case gate UI to case create/edit. |
| 5 | `PD-P1-FE-ATTACHMENT-GATES-01` | `tasks/postdemo/PD-P1-FE-ATTACHMENT-GATES-01.md` | frontend worker | Add attachment role/gate UI. |
| 5 | `PD-P1-FE-FILING-PREP-01` | `tasks/postdemo/PD-P1-FE-FILING-PREP-01.md` | frontend worker | Add filing preparation page. |
| 5 | `PD-P1-FE-OA-PACKAGE-01` | `tasks/postdemo/PD-P1-FE-OA-PACKAGE-01.md` | frontend worker | Add OA reply package page. |
| 5 | `PD-P1-FE-RECEIPT-ARCHIVE-01` | `tasks/postdemo/PD-P1-FE-RECEIPT-ARCHIVE-01.md` | frontend worker | Add receipt archive component/UI. |
| 5 | `PD-P1-FE-FEE-LINKAGE-01` | `tasks/postdemo/PD-P1-FE-FEE-LINKAGE-01.md` | frontend worker | Add fee linkage/checklist UI. |
| 5 | `PD-P1-FE-LETTER-HANDOFF-01` | `tasks/postdemo/PD-P1-FE-LETTER-HANDOFF-01.md` | frontend worker | Add format-letter/Longxia handoff UI. |
| 6 | `PD-P1-QA-FULLSCOPE-E2E-01` | `tasks/postdemo/PD-P1-QA-FULLSCOPE-E2E-01.md` | monitor | Run final full-scope QA and item-to-slice close ledger. |

## TDD Loop Required For Each Implementation Task

- [ ] Read the task file and freeze the exact closure/non-closure.
- [ ] Initialize `artifacts/<TASK-ID>/**` with `atomic-evidence-gates`.
- [ ] Write or update the smallest failing test through public APIs or UI behavior.
- [ ] Run the targeted test and confirm the expected failure.
- [ ] Implement only the minimum code needed for that closure slice.
- [ ] Run task-scoped lint/format/check commands.
- [ ] Run targeted tests and any browser smoke required by the task.
- [ ] Finalize evidence and run `./scripts/task_validate.sh <TASK-ID>`.
- [ ] Stop and ask the user whether to continue to the next task or wave.

## Done Definition

- All task gates for the 23 generated follow-up task files pass.
- Final QA ledger maps every P1 FS acceptance criterion to implemented task IDs and evidence.
- Stable business fields are maintained in existing FPMS UI/API/model surfaces, not relegated to long-term submit-time补录.
- P1 does not claim direct CPC/OA submit, auto-signature, RPA, auto-payment, or Longxia replacement.
- No residual in-scope gap remains inside the approved P1 interpretation.
