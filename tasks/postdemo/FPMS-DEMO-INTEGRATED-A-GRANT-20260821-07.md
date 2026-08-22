# FPMS-DEMO-INTEGRATED-A-GRANT-20260821-07

Status: ACTIVE
Risk-Class: PROTECTED
Risk-Tier: HIGH
Closure-Tags: ["demo", "grant", "lifecycle", "lineage", "evidence", "fee"]
Task-Path: tasks/postdemo/FPMS-DEMO-INTEGRATED-A-GRANT-20260821-07.md
Role: Implementer
Dependencies: ["FPMS-DEMO-INTEGRATED-A-SECOND-OA-20260821-06 APPROVED 0/0/0", "FPMS-DEMO-INTEGRATED-A-GRANT-NO-FEE-20260822-07A APPROVED 0/0/0"]

## Exact Closure Slice

Implement canonical checkpoints IA-10…12 on the same dynamic case. Create an executable original
grant-registration notice with the exact confirmed source/date tuple, upload and independently
review immutable `GRANT_NOTICE_ORIGINAL` evidence through visible UI, and bind that exact evidence
version/hash to the public grant lifecycle command. The result must create exactly one actionable
source-linked grant task and the exact grant-registration/application-pending/confirmed projection,
without creating any official fee item, obligation, draft or payable carrier.

Create the corrected notice only through the public replacement command. Upload and independently
review distinct immutable `GRANT_NOTICE_REPLACEMENT` evidence through visible UI, bind its exact
version/hash to the replacement lifecycle command, and prove original/replacement document,
evidence, task and activity lineage. The original task becomes superseded, exactly one replacement
task remains actionable, and the lifecycle projection remains unchanged.

Against the superseded task, exercise direct draft generation, batch customer instruction, notice
generation and status mutation. Each must return 409 with the exact before/after grant-task and fee
carrier snapshot unchanged. Record PAY once on the current task. A current-task draft attempt with
missing official-fee authority must return deterministic CONFIG_REQUIRED/409 with no fee item,
obligation, draft or payable write. Persist IA-01…12 checkpoint/evidence state before the canonical
spec reaches the exact IA-13 RED.

## Explicit Non-Closure

No IA-13…18 implementation, no SERVICE obligation/draft, bill, payment or offset mutation, no
customer or official fee authority activation, no inference of missing official amounts, no new
public API allowlist operation, no attachment/review API shortcut, no runtime bundle mutation, no
production/PostgreSQL/security/release closure and no broad/product/release gate.

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-a.live-backend.spec.ts`
- `backend/tests/test_demo_integrated_grant.py`
- `backend/app/modules/grant_fees/service.py` only on a focused product RED
- `backend/app/modules/grant_fees/api.py` only on a focused product RED
- `backend/app/modules/grant_fees/schemas.py` only on a focused product RED
- `backend/app/modules/documents/lifecycle_evidence_adapters.py` only on a focused product RED
- `frontend/src/api/grantFees.ts` only on a focused product RED
- `tasks/postdemo/FPMS-DEMO-INTEGRATED-A-GRANT-20260821-07.md`
- `artifacts/FPMS-DEMO-INTEGRATED-A-GRANT-20260821-07/**`

## Verification Commands

- Run the new Task-7 contract test RED/GREEN plus focused existing grant lifecycle, replacement,
  lineage/state and draft-authority tests.
- Run canonical static contract, typecheck/discovery and one fresh local rehearsal.
- The rehearsal must persist IA-01…12 and stop only at exact IA-13 RED.
- Prove exact scope, cleanup, candidate identity and independent High review.

## Evidence Path

- `artifacts/FPMS-DEMO-INTEGRATED-A-GRANT-20260821-07/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-INTEGRATED-A-FINANCE-20260821-08`
- `FPMS-DEMO-INTEGRATED-A-RUNNER-20260821-09`
- `FPMS-DEMO-INTEGRATED-A-FINAL-20260821-10`

## Done Definition

IA-10…12 pass against a fresh real local backend; evidence map has all twelve exact roles and the
checkpoint ledger has IA-01…12; original/replacement lineage and all five no-write gates are
observable; next failure is IA-13 RED; focused checks and cleanup pass; exact candidate receives
independent High `APPROVED` with `P0/P1/P2 = 0/0/0`.
