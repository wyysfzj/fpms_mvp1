# FPMS-DEMO-INTEGRATED-A-SECOND-OA-20260821-06

Status: ACTIVE
Risk-Class: PROTECTED
Risk-Tier: HIGH
Closure-Tags: ["demo", "oa", "receipt", "lifecycle", "evidence"]
Task-Path: tasks/postdemo/FPMS-DEMO-INTEGRATED-A-SECOND-OA-20260821-06.md
Role: Implementer
Dependencies: ["FPMS-DEMO-INTEGRATED-A-UI-BOUNDARY-20260821-06A APPROVED 0/0/0"]

## Exact Closure Slice

Implement canonical checkpoints IA-07…09 on the same dynamic case. Upload all input evidence and
internal OA reply outputs through visible UI. Cross-case and same-case-wrong-source receipt
attempts must return a deterministic error with the main case's public document/task/package/
lifecycle snapshot unchanged. A correct OA1 receipt must archive only OA1 and close only its task.

Create OA2 from the distinct immutable `OA_NOTICE_2` and `OA_RECEIPT_2` inputs with sequence 2,
distinct source/package/task/OA_OUT/receipt identities, the full confirmed deadline triple on all
five surfaces, missing/changed/sequence-1-reuse no-write gates, and an archive event that closes
only OA2. OA1 history must remain byte-for-byte unchanged and both archive endpoints must restore
the exact prosecution/substantive-examination/application-pending/confirmed projection.

Persist IA-01…09 checkpoint/evidence state before the canonical spec reaches the exact IA-10 RED.

## Explicit Non-Closure

No IA-10…18 implementation, no grant, fee, bill, payment or offset mutation, no new public API
allowlist operation, no attachment/review API shortcut, no runtime bundle mutation, no product
backend owner edit unless a focused RED proves it necessary, no broad/product/release gate.

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-a.live-backend.spec.ts`
- `backend/tests/test_demo_integrated_second_oa.py`
- `backend/app/modules/official_workflows/service.py` only on a focused product RED
- `backend/app/modules/documents/lifecycle_evidence_adapters.py` only on a focused product RED
- `backend/app/modules/documents/api.py` only on a focused product RED
- `tasks/postdemo/FPMS-DEMO-INTEGRATED-A-SECOND-OA-20260821-06.md`
- `artifacts/FPMS-DEMO-INTEGRATED-A-SECOND-OA-20260821-06/**`

## Verification Commands

- Run the new Task-6 contract test RED/GREEN plus focused existing receipt/archive/sequence tests.
- Run canonical static contract, typecheck/discovery and one fresh local rehearsal.
- The rehearsal must persist IA-01…09 and stop only at exact IA-10 RED.
- Prove exact scope, cleanup, candidate identity and independent High review.

## Evidence Path

- `artifacts/FPMS-DEMO-INTEGRATED-A-SECOND-OA-20260821-06/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-INTEGRATED-A-GRANT-20260821-07`
- `FPMS-DEMO-INTEGRATED-A-FINANCE-20260821-08`
- `FPMS-DEMO-INTEGRATED-A-RUNNER-20260821-09`
- `FPMS-DEMO-INTEGRATED-A-FINAL-20260821-10`

## Done Definition

IA-07…09 pass against a fresh real local backend; evidence map has the exact first ten roles and
checkpoint ledger has IA-01…09; next failure is IA-10 RED; focused checks and cleanup pass; exact
candidate receives independent High `APPROVED` with `P0/P1/P2 = 0/0/0`.
