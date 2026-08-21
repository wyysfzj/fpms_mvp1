# FPMS-DEMO-INTEGRATED-A-EVIDENCE-REVIEW-20260821-04

Status: ACTIVE
Risk-Class: PROTECTED
Risk-Tier: HIGH
Closure-Tags: ["demo", "evidence", "idempotency", "frontend"]
Task-Path: tasks/postdemo/FPMS-DEMO-INTEGRATED-A-EVIDENCE-REVIEW-20260821-04.md
Role: Implementer
Dependencies: ["FPMS-DEMO-INTEGRATED-A-PROVENANCE-UI-20260821-03 APPROVED 0/0/0"]

## Exact Closure Slice

Make the evidence-review UI consume the authoritative POST result, preserve one immutable
`idempotency_key` and `reviewed_at` for the same visible review intent, and reconcile through the
document read only when the POST outcome is unknown because transport failed. A deterministic
HTTP response, including every 4xx, remains authoritative and is never replaced by a later GET.
Unknown-outcome reconciliation succeeds only when the exact evidence version, reviewer and
requested terminal decision match durable state.

## Explicit Non-Closure

No backend evidence contract change, upload workflow change, lifecycle command, customer data,
security, production, broad/product/release gate, or IA-01 implementation.

## Allowed Files

- `frontend/src/api/documents.ts`
- `frontend/src/api/contracts/v8_document_evidence_review.contract.ts`
- `frontend/src/modules/documents/components/AttachmentList.vue`
- `frontend/tests/document-evidence-review-contract.mjs`
- `tasks/postdemo/FPMS-DEMO-INTEGRATED-A-EVIDENCE-REVIEW-20260821-04.md`
- `artifacts/FPMS-DEMO-INTEGRATED-A-EVIDENCE-REVIEW-20260821-04/**`

## Verification Commands

- RED/GREEN `node frontend/tests/document-evidence-review-contract.mjs`.
- Run frontend typecheck and scoped ESLint.
- Bind the exact current candidate to independent High review.

## Evidence Path

- `artifacts/FPMS-DEMO-INTEGRATED-A-EVIDENCE-REVIEW-20260821-04/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-INTEGRATED-A-FIRST-OA-20260821-05`
- `FPMS-DEMO-INTEGRATED-A-SECOND-OA-20260821-06`
- `FPMS-DEMO-INTEGRATED-A-GRANT-20260821-07`
- `FPMS-DEMO-INTEGRATED-A-FINANCE-20260821-08`
- `FPMS-DEMO-INTEGRATED-A-RUNNER-20260821-09`
- `FPMS-DEMO-INTEGRATED-A-FINAL-20260821-10`

## Done Definition

Successful POST needs no follow-up GET; unknown transport can reconcile exact durable state;
deterministic 4xx is rethrown without GET; retry reuses the original timestamp and key; focused
checks pass and independent High review reports 0/0/0.
