# FPMS Additional Functional GAP Mitigation Implementation Plan

Status: APPROVED — revision 3 independently reviewed
Goal: `019f4a1a-6f55-77a2-b558-b6555201415c`
Program ID: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Design: `docs/superpowers/specs/2026-07-10-fpms-additional-gap-mitigation-design.md`

Independent review: `/root/plan_review` returned `APPROVE` on 2026-07-10 after the shared-file serialization, exact allowlist, final E2E ownership, and self-excluding final-gate contracts were corrected.

## Goal and planning gate

Close the seven additional functional gaps through 47 independently gated atomic tasks. No product task starts until this plan, the explicit batch manifest, all 47 task files, and the initial item-to-slice ledger exist and the Wave 0 planning gate passes.

## Story Shape Classification

- `shared_file_density`: high — the document, official-workflow, grant-fee, seed, shared-schema, and frontend API files recur across slices.
- `prereq_dependency_density`: high — transaction atomicity, semantic resolution, database uniqueness, receipt ownership, and structured deadline contracts gate later behavior.
- `be_fe_coupling`: high — work-package reachability and deadline/provenance clarity close only through backend plus Simplified Chinese product UI.
- `evidence_cost`: high — each task needs dirty-baseline, RED/GREEN, scoped checks, evidence, and a final no-enrichment real-path/release audit.
- `chosen_runbook`: `P0-prereq-heavy-story`.

## Execution protocol

For every task: check current Goal and `AGENTS.md`; capture `git status --short`; initialize `artifacts/<TASK-ID>/`; record `baseline_allowlist.diff` and `baseline_external_files.txt`; freeze exact allowlist; run the task's RED command and preserve failure evidence; implement only the closure; run GREEN, scoped lint/format, scope diff, evidence finalize, and `./scripts/task_validate.sh <TASK-ID>`. SQLite-writing tests are serialized. No commit, push, PR, reset, clean, checkout, or overwrite of user changes.

Command abbreviations used below:

- `PYTEST <file>` = `cd backend && .venv/bin/pytest -q <file>`
- `RUFF <files>` = `cd backend && .venv/bin/ruff check --fix <files> && .venv/bin/ruff format <files> && .venv/bin/ruff check <files>`
- `FE-CHECK` = `cd frontend && npm run lint && npm run typecheck`
- `PW <file>` = `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test <file> --workers=1`
- every task additionally runs `git diff --check -- <allowlist>` and its task gate.

## Shared-file serial order

- `documents/service.py`: 02 → 04 → 13 → 21 → 24 → 25 → 26 → 28 → 29 → 34 → 39.
- `documents/api.py`: 02 → 23 → 24 → 25 → 28 → 29 → 40.
- `documents/schemas.py`: 23 → 24 → 25 → 28 → 29 → 40.
- `official_workflows/service.py`: 06 → 10 → 14 → 15 → 17.
- `official_workflows/api.py` / `schemas.py`: 07 → 11.
- frontend `officialWorkflows.ts/.types.ts`: 08 → 12.
- `seed_dev.py`: 18 → 33 → 38.
- `official_notice_catalog.py`: 19 → 33 → 38.
- frontend `documents.ts/.types.ts`: 30 → 31 → 32.
- `grant_fees/service.py`: 36 → 39 → 41 → 42.
- `grant_fees/schemas.py`: 40 → 41 → 42.
- frontend `grantFees.ts/.types.ts` and `GrantFeeTaskList.vue`: 43 → 44.

No two tasks in the same list may run concurrently.

For every row below, the executable allowlist is the union of its exact source paths, its exact test path, its own task file, and `artifacts/<TASK-ID>/**`. No wildcard authorizes a shared source file not named in the row.

## Atomic task matrix

### Wave 1 — isolated deterministic blocker

| # | Task file | Exact closure | Exact source allowlist | Exact test | Dependency |
| ---: | --- | --- | --- | --- | --- |
| 01 | `tasks/additional_gaps/FPMS-ADDGAP-WIZARD-TEMPLATE-LIMIT-20260710-01.md` | DocumentWizard requests at most 100 enabled templates, eliminating deterministic 422. | `frontend/src/modules/documents/pages/DocumentWizard.vue` | `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-wizard-template-limit.spec.ts` | Wave 0 |

Task 01 RED/GREEN: `PW src/tests/addgap-wizard-template-limit.spec.ts`; then `FE-CHECK`. Permission/status remains existing `DocTemplate.Read`, GET 200/422 contract. Non-closure: no pagination/search redesign.

### Wave 2 — transaction, semantics, and work-package reachability

| # | Task file | Exact closure | Exact source allowlist | Exact test | Dependency |
| ---: | --- | --- | --- | --- | --- |
| 02 | `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-CREATE-ATOMICITY-20260710-01.md` | Required document/task/grant side effects commit or roll back as one transaction. | `backend/app/modules/documents/service.py`, `backend/app/modules/documents/api.py` | `backend/tests/test_addgap_document_create_atomicity.py` | Wave 0 |
| 03 | `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-SEMANTICS-RESOLVER-20260710-01.md` | One resolver returns `ResolvedDocumentSemantics` and rejects malformed/conflicting execution metadata. | `backend/app/modules/documents/semantics.py` | `backend/tests/test_addgap_document_semantics.py` | 02 |
| 04 | `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-SEMANTIC-STATE-EFFECT-20260710-01.md` | Document need-reply and case-state effects consume the resolver, not raw/template-name inference. | `backend/app/modules/documents/service.py` | `backend/tests/test_addgap_document_semantic_state_effect.py` | 03 |
| 05 | `tasks/additional_gaps/FPMS-ADDGAP-WORKPKG-RESOLVE-KEY-SCHEMA-20260710-01.md` | Phase 0-EXT adds/backfills unique `OfficialWorkPackage.resolve_key` after duplicate preflight. | `backend/alembic/versions/addgap_workpkg_resolve_key.py`, `backend/app/modules/official_workflows/models.py` | `backend/tests/test_addgap_workpkg_resolve_key_schema.py` | Wave 0; current Alembic head recheck |
| 06 | `tasks/additional_gaps/FPMS-ADDGAP-FILING-ENSURE-SERVICE-20260710-01.md` | Resolve/create one initialized filing package; existing first, new only for `NOT_FILED`, DB-race winner re-read. | `backend/app/modules/official_workflows/service.py` | `backend/tests/test_addgap_filing_ensure_service.py` | 05 |
| 07 | `tasks/additional_gaps/FPMS-ADDGAP-FILING-RESOLVE-API-20260710-01.md` | Add bodyless filing resolve POST returning existing package envelope. | `backend/app/modules/official_workflows/api.py`, `backend/app/modules/official_workflows/schemas.py` | `backend/tests/test_addgap_filing_resolve_api.py` | 06 |
| 08 | `tasks/additional_gaps/FPMS-ADDGAP-FILING-PAGE-RESOLVE-20260710-01.md` | FilingPreparation resolves `case_id` to `package_id` and replaces route. | `frontend/src/api/officialWorkflows.ts`, `frontend/src/api/officialWorkflows.types.ts`, `frontend/src/modules/cases/pages/FilingPreparation.vue` | `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-filing-page-resolve.spec.ts` | 07 |
| 09 | `tasks/additional_gaps/FPMS-ADDGAP-FILING-CASE-ENTRY-20260710-01.md` | CaseDetail exposes the Simplified Chinese filing-preparation action with current case ID. | `frontend/src/modules/cases/pages/CaseDetail.vue` | `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-filing-case-entry.spec.ts` | 08 |
| 10 | `tasks/additional_gaps/FPMS-ADDGAP-OA-ENSURE-SERVICE-20260710-01.md` | Resolve/create one OA package per executable IN source; creation state must match resolved OA1/OA2. | `backend/app/modules/official_workflows/service.py` | `backend/tests/test_addgap_oa_ensure_service.py` | 03, 05 |
| 11 | `tasks/additional_gaps/FPMS-ADDGAP-OA-RESOLVE-API-20260710-01.md` | Add bodyless OA resolve POST returning `OaReplyPackageOut`. | `backend/app/modules/official_workflows/api.py`, `backend/app/modules/official_workflows/schemas.py` | `backend/tests/test_addgap_oa_resolve_api.py` | 10 |
| 12 | `tasks/additional_gaps/FPMS-ADDGAP-OA-PAGE-RESOLVE-20260710-01.md` | OAReplyPackage resolves existing DocumentDetail `document_id` context to package ID. | `frontend/src/api/officialWorkflows.ts`, `frontend/src/api/officialWorkflows.types.ts`, `frontend/src/modules/documents/pages/OAReplyPackage.vue` | `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-oa-page-resolve.spec.ts` | 11; serialized after 08 |

Task 05 verification includes `cd backend && PYTHONPATH=. .venv/bin/alembic heads`, clean SQLite `upgrade head`, and `PYTEST tests/test_addgap_workpkg_resolve_key_schema.py`. It may not rewrite `frfe04_paylist_govpayment_struct.py`. Tasks 07/11 use `OfficialWorkflow.Update`, POST 200, existing envelopes; 404 for absent resource, 400 for direction, 409 for state/semantics/identity conflict. All backend tasks use `RUFF` on their exact source/test files and `PYTEST` on the exact test.

### Wave 3/4 — OA remains open, then evidence gates, then one archive event

| # | Task file | Exact closure | Exact source allowlist | Exact test | Dependency |
| ---: | --- | --- | --- | --- | --- |
| 13 | `tasks/additional_gaps/FPMS-ADDGAP-OA-OUT-KEEPS-TASK-OPEN-20260710-01.md` | OA_OUT records internal reply date but changes neither OA task nor case state; ordinary non-OA behavior stays scoped. | `backend/app/modules/documents/service.py` | `backend/tests/test_addgap_oa_out_keeps_task_open.py`, `backend/tests/test_b2_reply_chain.py`, `backend/tests/test_spec_alignment_e2e.py` | 03, 04 |
| 14 | `tasks/additional_gaps/FPMS-ADDGAP-RECEIPT-SAME-CASE-GATE-20260710-01.md` | Receipt attachment document case must equal package case before any write. | `backend/app/modules/official_workflows/service.py` | `backend/tests/test_addgap_receipt_same_case_gate.py` | 05 |
| 15 | `tasks/additional_gaps/FPMS-ADDGAP-OA-RECEIPT-SOURCE-GATE-20260710-01.md` | Same-case OA receipt must be on linked reply document or explicit package manifest. | `backend/app/modules/official_workflows/service.py` | `backend/tests/test_addgap_oa_receipt_source_gate.py` | 14 |
| 16 | `tasks/additional_gaps/FPMS-ADDGAP-RECEIPT-HISTORY-SCAN-20260710-01.md` | Read-only scan reports cross-case and invalid OA-source historical receipt links. | `backend/scripts/audit_receipt_ownership.py` | `backend/tests/test_addgap_receipt_history_scan.py` | 14, 15 |
| 17 | `tasks/additional_gaps/FPMS-ADDGAP-OA-RECEIPT-ARCHIVE-EVENT-20260710-01.md` | One `OFFICIAL_RECEIPT_ARCHIVED` transaction revalidates evidence, closes exactly one matching OA task, archives package, restores OA1/OA2 to SUB_EXAM, and writes evidence. | `backend/app/modules/official_workflows/service.py` | `backend/tests/test_addgap_oa_receipt_archive_event.py` | 13–16 |

Task 14 status: 404 absent package/attachment, 400 `OFFICIAL_WORK_PACKAGE_RECEIPT_CASE_MISMATCH`, 201 valid. Task 15 adds 400 `OA_RECEIPT_ATTACHMENT_SOURCE_INVALID`. Task 17 returns 409 for no valid receipt, invalid historical receipt, zero/multiple matching OA tasks, or wrong case state before any close; complete override remains 200/`OVERRIDE` and changes neither task nor case; repeated archived call is idempotent. Permission/envelope remain `OfficialWorkflow.Update` and current receipt/archive models. Non-closure: no receipt number-content matching or general state matrix.

### Wave 5 — catalog is visible but fail-closed

| # | Task file | Exact closure | Exact source allowlist | Exact test | Dependency |
| ---: | --- | --- | --- | --- | --- |
| 18 | `tasks/additional_gaps/FPMS-ADDGAP-OA-SUBSEQUENT-TASK-IDENTITY-20260710-01.md` | Seed `OA_REPLY_SUBSEQUENT` as task identity without calculable fallback. | `backend/scripts/seed_dev.py` | `backend/tests/test_addgap_oa_subsequent_task_identity.py` | 03 |
| 19 | `tasks/additional_gaps/FPMS-ADDGAP-NOTICE-CATALOG-CLASSIFICATION-20260710-01.md` | Mark all 60 official-notice rows reference-only/non-selectable with preserved source codes and no effects. | `backend/app/modules/documents/official_notice_catalog.py` | `backend/tests/test_addgap_notice_catalog_classification.py` | 03 |
| 20 | `tasks/additional_gaps/FPMS-ADDGAP-NOTICE-CATALOG-UI-CLARITY-20260710-01.md` | DocumentCreate shows all catalog rows with Chinese executable/reference labels and disables reference-only selection. | `frontend/src/modules/documents/pages/DocumentCreate.vue` | `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-notice-catalog-ui-clarity.spec.ts` | 19 |
| 21 | `tasks/additional_gaps/FPMS-ADDGAP-NOTICE-CATALOG-REFERENCE-GATE-20260710-01.md` | Backend create/wizard rejects use of a reference-only official catalog template with 409. | `backend/app/modules/documents/service.py` | `backend/tests/test_addgap_notice_catalog_reference_gate.py` | 03, 19 |

Task 20 deliberately fetches/displays reference rows as disabled, not hidden. Task 21 preserves plain non-catalog templates; it rejects only catalog metadata marked reference-only. No customer-unconfirmed semantics are activated.

### Wave 6 — structured official deadline

| # | Task file | Exact closure | Exact source allowlist | Exact test | Dependency |
| ---: | --- | --- | --- | --- | --- |
| 22 | `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-DEADLINE-CARRIER-20260710-01.md` | Canonical parser/merger preserves unknown JSON, legacy text, and projects read-only `LEGACY_UNVERIFIED`. | `backend/app/modules/documents/extra_data.py` | `backend/tests/test_addgap_document_deadline_carrier.py` | 03 |
| 23 | `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-DEADLINE-READ-PROJECTION-20260710-01.md` | Existing DocumentOut responses project structured due/source/read-status/description while retaining extra_data. | `backend/app/modules/documents/schemas.py`, `backend/app/modules/documents/api.py` | `backend/tests/test_addgap_document_deadline_read_projection.py` | 22 |
| 24 | `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-API-20260710-01.md` | POST document accepts write-status fields and persists canonical structured deadline. | `backend/app/modules/documents/schemas.py`, `backend/app/modules/documents/service.py`, `backend/app/modules/documents/api.py` | `backend/tests/test_addgap_document_deadline_create_api.py` | 02, 22, 23 |
| 25 | `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-DEADLINE-UPDATE-API-20260710-01.md` | PUT document accepts missing/legacy confirmation but rejects changing/clearing confirmed due through ordinary edit. | `backend/app/modules/documents/schemas.py`, `backend/app/modules/documents/service.py`, `backend/app/modules/documents/api.py` | `backend/tests/test_addgap_document_deadline_update_api.py` | 22–24 |
| 26 | `tasks/additional_gaps/FPMS-ADDGAP-LEGACY-DEADLINE-TASK-SYNC-20260710-01.md` | Confirming the same legacy/missing date recalculates exactly one matching OA task due/internal/reminders and logs evidence. | `backend/app/modules/documents/service.py`, `backend/app/modules/tasks/task_generation_service.py` | `backend/tests/test_addgap_legacy_deadline_task_sync.py` | 18, 25 |
| 27 | `tasks/additional_gaps/FPMS-ADDGAP-OA-DEADLINE-FAIL-CLOSED-20260710-01.md` | Executable OA task generation requires confirmed explicit due and never uses task-template date fallback. | `backend/app/modules/tasks/task_generation_service.py` | `backend/tests/test_addgap_oa_deadline_fail_closed.py` | 02–04, 18, 22 |
| 28 | `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-DEADLINE-IMPACT-PREVIEW-20260710-01.md` | Impact preview reports structured due lineage or a 409 missing-confirmation blocker. | `backend/app/modules/documents/service.py`, `backend/app/modules/documents/schemas.py`, `backend/app/modules/documents/api.py` | `backend/tests/test_addgap_document_deadline_impact_preview.py` | 22, 27 |
| 29 | `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-WIZARD-DEADLINE-BACKEND-20260710-01.md` | Wizard schemas/service accept and persist per-row structured due/source/write-status fields. | `backend/app/modules/documents/schemas.py`, `backend/app/modules/documents/service.py` | `backend/tests/test_addgap_document_wizard_deadline_backend.py` | 22, 24, 27 |
| 30 | `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-UI-20260710-01.md` | DocumentCreate exposes Simplified Chinese date/source/confirmation fields and impact warning. | `frontend/src/api/documents.ts`, `frontend/src/api/documents.types.ts`, `frontend/src/modules/documents/pages/DocumentCreate.vue` | `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-document-deadline-create-ui.spec.ts` | 24, 28 |
| 31 | `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-DEADLINE-WIZARD-UI-20260710-01.md` | DocumentWizard exposes/persists the structured fields per row. | `frontend/src/api/documents.ts`, `frontend/src/api/documents.types.ts`, `frontend/src/modules/documents/pages/DocumentWizard.vue` | `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-document-deadline-wizard-ui.spec.ts` | 29, 30 |
| 32 | `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-DEADLINE-EDIT-UI-20260710-01.md` | DocumentEdit displays lineage, confirms missing/legacy same date, and keeps confirmed date read-only. | `frontend/src/api/documents.ts`, `frontend/src/api/documents.types.ts`, `frontend/src/modules/documents/pages/DocumentEdit.vue` | `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-document-deadline-edit-ui.spec.ts` | 25, 26, 31 |

Tasks 23–29 use write enum `CONFIRMED|NEEDS_CONFIRMATION|null`, read enum adds service-only `LEGACY_UNVERIFIED`; shape errors 422, cross-field business errors 400, missing confirmation/config or override conflict 409. Permissions remain `Doc.Create` for create/preview/wizard and `Doc.Edit` for update; GET is bodyless. FE tasks run `PW` and `FE-CHECK` serially.

### Wave 6B — activate only confirmed OA/acceptance aliases

| # | Task file | Exact closure | Exact source allowlist | Exact test | Dependency |
| ---: | --- | --- | --- | --- | --- |
| 33 | `tasks/additional_gaps/FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01.md` | Activate only acceptance, exact first OA, and second/third/fourth/fifth OA catalog rows with frozen semantics. | `backend/app/modules/documents/official_notice_catalog.py`, `backend/scripts/seed_dev.py` | `backend/tests/test_addgap_notice_oa_acceptance_activation.py` | 18–29 |
| 34 | `tasks/additional_gaps/FPMS-ADDGAP-OA-ALIAS-REPLY-VALIDATION-20260710-01.md` | OA_OUT validation accepts executable OA semantic aliases, not only literal OA_IN. | `backend/app/modules/documents/service.py` | `backend/tests/test_addgap_oa_alias_reply_validation.py` | 33 |

Real Chinese OA creation with confirmed due must produce OA1/OA2 and the correct task identity. UM/design OA, rectification, reexamination, rejection, annuity, PCT, and grant remain reference-only here.

### Wave 7 — grant provenance, then grant catalog activation

| # | Task file | Exact closure | Exact source allowlist | Exact test | Dependency |
| ---: | --- | --- | --- | --- | --- |
| 35 | `tasks/additional_gaps/FPMS-ADDGAP-GRANT-LINEAGE-SCHEMA-20260710-01.md` | Phase 0-EXT adds grant source/deadline/supersede/request-key carriers and unique indexes after duplicate scan. | `backend/alembic/versions/addgap_grant_lineage.py`, `backend/app/modules/fees/models.py` | `backend/tests/test_addgap_grant_lineage_schema.py` | current Alembic head recheck; 22 |
| 36 | `tasks/additional_gaps/FPMS-ADDGAP-GRANT-SOURCE-DEADLINE-20260710-01.md` | First executable grant notice creates/reuses one source-keyed task with confirmed explicit due; removes +60. | `backend/app/modules/grant_fees/service.py` | `backend/tests/test_addgap_grant_source_deadline.py` | 03, 22, 35 |
| 37 | `tasks/additional_gaps/FPMS-ADDGAP-GRANT-AUTO-DRAFT-GATE-20260710-01.md` | Grant notice registration does not create generic zero-value FeeDraft before client instruction. | `backend/app/modules/documents/fee_linking_service.py` | `backend/tests/test_addgap_grant_auto_draft_gate.py` | 03, 36 |
| 38 | `tasks/additional_gaps/FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01.md` | Activate only `授权通知书-电子` with frozen grant semantics after lineage/due/draft gates exist. | `backend/app/modules/documents/official_notice_catalog.py`, `backend/scripts/seed_dev.py` | `backend/tests/test_addgap_notice_grant_activation.py` | 35–37 |
| 39 | `tasks/additional_gaps/FPMS-ADDGAP-GRANT-REPLACEMENT-SERVICE-20260710-01.md` | Atomic service creates/reuses replacement notice/task and supersedes old task using request key/reason. | `backend/app/modules/grant_fees/service.py`, `backend/app/modules/documents/service.py` | `backend/tests/test_addgap_grant_replacement_service.py` | 02, 22, 35–38 |
| 40 | `tasks/additional_gaps/FPMS-ADDGAP-GRANT-REPLACEMENT-API-20260710-01.md` | Add composite replacement-notice POST with existing/new composite response. | `backend/app/modules/grant_fees/schemas.py`, `backend/app/modules/grant_fees/api.py`, `backend/app/modules/documents/schemas.py`, `backend/app/modules/documents/api.py` | `backend/tests/test_addgap_grant_replacement_api.py` | 39 |
| 41 | `tasks/additional_gaps/FPMS-ADDGAP-GRANT-LIST-LINEAGE-PROJECTION-20260710-01.md` | Grant list response adds separate lineage fields without changing workflow status. | `backend/app/modules/grant_fees/service.py`, `backend/app/modules/grant_fees/schemas.py` | `backend/tests/test_addgap_grant_list_lineage_projection.py` | 35–40 |
| 42 | `tasks/additional_gaps/FPMS-ADDGAP-GRANT-STATE-LINEAGE-GATE-20260710-01.md` | Grant state response exposes lineage and removes state-changing actions for legacy/superseded tasks. | `backend/app/modules/grant_fees/service.py`, `backend/app/modules/grant_fees/schemas.py` | `backend/tests/test_addgap_grant_state_lineage_gate.py` | 41 |
| 43 | `tasks/additional_gaps/FPMS-ADDGAP-GRANT-LINEAGE-UI-20260710-01.md` | GrantFeeTaskList displays source/deadline/legacy/superseded lineage in Simplified Chinese. | `frontend/src/api/grantFees.ts`, `frontend/src/api/grantFees.types.ts`, `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue` | `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-grant-lineage-ui.spec.ts` | 41, 42 |
| 44 | `tasks/additional_gaps/FPMS-ADDGAP-GRANT-REPLACEMENT-UI-20260710-01.md` | GrantFeeTaskList provides explicit replacement-notice action with reason, request key, and confirmed due. | `frontend/src/api/grantFees.ts`, `frontend/src/api/grantFees.types.ts`, `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue` | `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-grant-replacement-ui.spec.ts` | 40, 43 |

Task 35 re-checks the single head, never edits the user migration, uses SQLite-safe types/`CURRENT_TIMESTAMP`, verifies clean upgrade. Task 36 missing/unverified due or different active source returns 409; same source reuses. Task 40 permissions are both function-parameter `GrantFeeTask.Write` and `Doc.Create`; POST success is 200 with `GrantFeeTaskReplacementNoticeOut`, 404 old task, 400 business shape, 409 semantics/lineage/idempotency conflict, 422 payload shape. `lineage_status` stays separate from workflow `state/status`.

### Wave 8 — program-scoped release and final close

| # | Task file | Exact closure | Exact source allowlist | Exact test | Dependency |
| ---: | --- | --- | --- | --- | --- |
| 45 | `tasks/additional_gaps/FPMS-ADDGAP-MANIFEST-RELEASE-GATE-20260710-01.md` | `release_gate.sh --manifest <file> [--exclude-task ID]` validates listed task IDs while no-arg behavior remains compatible. | `scripts/release_gate.sh` | `backend/tests/test_addgap_manifest_release_gate.py` | Wave 0; execute before Task 47 |
| 46 | `tasks/additional_gaps/FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01.md` | Add and pass one no-enrichment real-user E2E scenario covering all seven GAP outcomes. | `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-final-real-path.spec.ts` | `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-final-real-path.spec.ts` | 01–44 PASS |
| 47 | `tasks/additional_gaps/FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01.md` | Run task gates/full checks/program gate excluding self and produce final item-to-slice close audit. | `docs/reviews/fpms_additional_gap_mitigation_close_audit_20260710.md` | `backend/tests/test_addgap_final_close_ledger_contract.py` | 01–46 PASS |

Task 45 test creates isolated temporary artifact fixtures and proves manifest scope, one-task exclusion, and default compatibility. Task 46 owns creation of the final Playwright scenario and no product source. Task 47 may write only its exact close-ledger contract test, review document, task file, and evidence; it may not fix product code. It serially runs backend full pytest/Ruff, frontend lint/typecheck/build, Task 46, every prior task gate, and `./scripts/release_gate.sh --manifest tasks/batches/FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01.md --exclude-task FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01`. It then finalizes its evidence and passes its own task gate. Finally, the main/lead runs the same manifest-scoped gate without exclusion over all 47 tasks and records that batch-acceptance output under the program artifact. Any in-scope failure makes Task 47 or batch acceptance FAIL.

## GAP coverage map

| GAP | Required task numbers |
| --- | --- |
| `ADD-GAP-WIZARD-01` | 01 |
| `ADD-GAP-WORKPKG-01` | 03–12 |
| `ADD-GAP-OA-01` | 03–04, 10–18, 26–27, 33–34 |
| `ADD-GAP-RECEIPT-01` | 14–17 |
| `ADD-GAP-CATALOG-01` | 03–04, 18–21, 27–28, 33–34, 36–38 |
| `ADD-GAP-DEADLINE-01` | 02–04, 22–34 |
| `ADD-GAP-GRANT-01` | 02–04, 22–25, 35–44 |

Program-level acceptance tasks 45–47 apply uniformly to all seven GAPs and are therefore not misattributed to one row.

## Plan acceptance gate

Before Wave 1: independent plan reviewer returns APPROVE; the explicit manifest contains the 47 exact task paths, owner roles, dependencies, shared ownership, status/permission/envelope contracts, and verification; all 47 task files contain mandatory AGENTS fields; initial ledger exists; planning dirty baseline/evidence exists; `git diff --check` and the Wave 0 planning gate pass.
