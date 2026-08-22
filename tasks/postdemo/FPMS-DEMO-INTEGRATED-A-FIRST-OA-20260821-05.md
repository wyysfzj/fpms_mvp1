# FPMS-DEMO-INTEGRATED-A-FIRST-OA-20260821-05

Status: ACTIVE
Risk-Class: PROTECTED
Risk-Tier: HIGH
Closure-Tags: ["demo", "lifecycle", "filing", "oa", "lineage"]
Task-Path: tasks/postdemo/FPMS-DEMO-INTEGRATED-A-FIRST-OA-20260821-05.md
Role: Implementer
Dependencies: ["FPMS-DEMO-INTEGRATED-A-EVIDENCE-REVIEW-20260821-04 APPROVED 0/0/0"]

## Exact Closure Slice

Close IA-01 through IA-06 on one fresh local synthetic run: visible-UI client/contact/case
creation, exact initial lifecycle projection and zero downstream counts, the exact 60-row document
catalog, idempotent filing preparation, the reviewed filing-to-first-OA evidence ladder with the
same confirmed deadline triple on all five required surfaces, and one uniquely linked OA_OUT while
the target task remains OPEN. The controller may terminate at the first unimplemented IA-07 RED;
that downstream RED is not part of this task.

The integrated bundle's twelve immutable evidence descriptors must be passed from the already
validated manifest to the browser as a redacted runtime JSON value. It contains only role, absolute
local file path, SHA-256 and metadata; it does not create or review evidence and cannot broaden the
audited lifecycle API allowlist.

## Explicit Non-Closure

No receipt/archive or OA2 behavior, grant, finance, customer-authorized input, security,
production/PostgreSQL, broad/product/release gate, direct evidence API write, pre-created business
objects or lifecycle enrichment. The approved 60-row reference catalog is configuration, not a
seeded customer/case/lifecycle object.

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-a.live-backend.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-a-static-contract.mjs`
- `scripts/run_demo_integrated_a_rehearsal.py`
- `backend/scripts/run_local_demo_abc.py`
- `backend/tests/test_demo_integrated_first_oa.py`
- `backend/app/modules/cases/service.py`
- `backend/app/modules/official_workflows/service.py`
- `backend/app/modules/official_workflows/filing_evidence_resolver.py`
- `backend/app/modules/documents/lifecycle_evidence_adapters.py`
- `backend/app/modules/documents/service.py`
- `frontend/src/api/documents.ts`
- `frontend/src/modules/documents/components/AttachmentList.vue`
- `frontend/src/modules/documents/pages/DocumentWizard.vue`
- `tasks/postdemo/FPMS-DEMO-INTEGRATED-A-FIRST-OA-20260821-05.md`
- `artifacts/FPMS-DEMO-INTEGRATED-A-FIRST-OA-20260821-05/**`

## Verification Commands

- RED/GREEN focused pytest for the runtime descriptor bridge and IA-01…06 source contract.
- Run the integrated static contract.
- Run one fresh headless diagnostic and prove IA-01…06 completed before the expected IA-07 RED.
- Run Ruff on changed Python and Playwright list on the canonical spec.
- Bind the exact candidate to independent High review.

## Evidence Path

- `artifacts/FPMS-DEMO-INTEGRATED-A-FIRST-OA-20260821-05/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-INTEGRATED-A-SECOND-OA-20260821-06`
- `FPMS-DEMO-INTEGRATED-A-GRANT-20260821-07`
- `FPMS-DEMO-INTEGRATED-A-FINANCE-20260821-08`
- `FPMS-DEMO-INTEGRATED-A-RUNNER-20260821-09`
- `FPMS-DEMO-INTEGRATED-A-FINAL-20260821-10`

## Done Definition

One fresh real browser run produces observable IA-01…06 results and exact evidence bindings using
only visible evidence upload/review UI plus the approved lifecycle API helper; focused checks pass;
the next failure is explicitly IA-07 RED; independent High review reports 0/0/0.
