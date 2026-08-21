# FPMS-DEMO-INTEGRATED-A-FINANCE-20260821-08

Status: ACTIVE
Risk-Class: PROTECTED
Risk-Tier: HIGH
Closure-Tags: ["demo", "finance", "fee", "billing", "payment", "offset", "evidence"]
Task-Path: tasks/postdemo/FPMS-DEMO-INTEGRATED-A-FINANCE-20260821-08.md
Role: Implementer
Dependencies: ["FPMS-DEMO-INTEGRATED-A-GRANT-20260821-07 APPROVED 0/0/0"]

## Exact Closure Slice

Implement canonical checkpoints IA-13…17 on the exact dynamic IA-02 case. Reuse only the
IA-00 runtime-input snapshot that was successfully validated in the same browser session and whose
manifest digest still equals the current read-only bundle. Do not rerun the fresh-database preflight
after lifecycle writes and do not treat an unvalidated or digest-mismatched session snapshot as
READY.

Through the visible Demo ABC UI, select the exact integrated runtime SERVICE item, create/reuse one
linked obligation, record PAY once, prepare exactly one draft and lock it. The visible provenance
must equal IA-00, service amount must equal the bundle, and official fee remains `未配置`, excluded
from every total with zero official-fee carriers.

Create and replay one AR bill command that consumes the locked draft/item, then create and replay
one equal CNY bank-receipt command and create one active full offset. Observe one bill/payment/
payment-line/offset identity; bill becomes `SETTLED/0.00`, payment becomes
`FULLY_ALLOCATED/0.00`, and the canonical CaseReceipt received amount equals the SERVICE amount.
After navigation/reload, read each case/draft/bill/payment/offset surface again and prove displayed
route identities, lifecycle tuple, states, amounts and currency equal authoritative responses. UI
session state may retain only the successfully validated bundle snapshot and dynamic identifiers;
financial truth after reload must be reconciled from backend reads, never trusted from stale cached
projections.

## Explicit Non-Closure

No IA-18/final acceptance or two-run controller, no official-fee activation or synthetic zero, no
customer bundle activation, no production/PostgreSQL/security/release closure, no AP, partial or
cross-bill allocation, refund, bad debt, dunning, invoice, commission, multi-currency dashboard or
broad/product/release gate. Do not alter lifecycle or grant authority semantics closed by Tasks 1–7.

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-a.live-backend.spec.ts`
- `frontend/src/modules/demo/pages/DemoAbc.vue`
- `frontend/src/modules/demo/demo.api.ts`
- `frontend/tests/demo-abc-contract.mjs`
- `backend/app/modules/fees/demo_service.py`
- `backend/app/modules/fees/demo_service_schemas.py`
- `backend/tests/test_demo_abc_runtime_service_draft.py`
- `backend/tests/test_demo_abc_unique_ar_bill.py`
- `backend/tests/test_demo_abc_payment_offset.py`
- `tasks/postdemo/FPMS-DEMO-INTEGRATED-A-FINANCE-20260821-08.md`
- `artifacts/FPMS-DEMO-INTEGRATED-A-FINANCE-20260821-08/**`

## Verification Commands

- Run Task-8 test-only changes against exact Task-7 baseline and retain failures at IA-13…17.
- Run the three focused backend finance specs, frontend ABC contract, typecheck, scoped ESLint,
  canonical static contract/discovery and one fresh headless integrated rehearsal.
- The rehearsal must persist IA-01…17 and stop only at exact IA-18 RED.
- Prove exact scope, cleanup, candidate identity and independent High review.

## Evidence Path

- `artifacts/FPMS-DEMO-INTEGRATED-A-FINANCE-20260821-08/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-INTEGRATED-A-RUNNER-20260821-09`
- `FPMS-DEMO-INTEGRATED-A-FINAL-20260821-10`

## Done Definition

IA-13…17 pass on one fresh real local run against the same IA-02 case; provenance and official-fee
boundary remain exact; obligation/draft/bill/payment/line/offset/CaseReceipt identities and counts
are authoritative and idempotent; reload proves route/state/amount/currency consistency; next
failure is IA-18 RED; focused checks and cleanup pass; exact candidate receives independent High
`APPROVED` with `P0/P1/P2 = 0/0/0`.
