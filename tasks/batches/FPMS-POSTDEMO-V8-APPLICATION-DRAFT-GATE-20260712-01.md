# FPMS Post-demo V8 Application-draft Gate Lane

Status: ACTIVATION CANDIDATE / PRODUCT NOT STARTED
Controller task: `FPMS-V8-APPLICATION-DRAFT-MANIFEST-ACTIVATION-20260712-01`
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`

## Lane contract

- Manifest phase: `lane`
- Task count: `2`
- Gate identity: `DG-FEE-APPLICATION-DRAFT:GLOBAL`
- Gate status: `APPROVED_POLICY`
- Decision version: `customer-decision:2026-08-10:v8-full-batch-scheme-a:v1`
- Decision source SHA-256: `e6cfd648f1d366e27bde3f74310f00033a6db60ce55d850d2e668764745faace`
- Decision source commit: `e5a41c8d07f11d1b0dec68891ef7bef53312f883`
- Decision adoption commit: `72877386974cd57c720b7c622e6b00ca49c03d7d`
- Draft trigger: `reviewed-real-application-fee-notice`
- Draft result: `one-internal-pending-review-draft`
- Payment boundary: `client-instruction-required`
- SELF_PENDING: `FPMS-V8-APPLICATION-DRAFT-MANIFEST-ACTIVATION-20260712-01`
- Activation review: `independent-high-zero-finding-required`
- Product start: `after-activation-pass-only`
- SQLite verification: `globally-serialized`

The accepted customer policy authorizes one internal pending-review application-fee draft only
after the real application-fee notice has been reviewed. It does not authorize payment:
actual payment still requires explicit client instruction.

## Verified current prerequisites

| Frozen dependency | Current verified successor | Status |
| --- | --- | --- |
| `FPMS-V8-CATALOG-MANIFEST-COVERAGE-GATE-20260712-01` | `C3-LEAN-LEDGER-INTEGRATION-REF-CORRECTION` | `CURRENT_VERIFIED` |
| `FPMS-V8-FO-PREPARE-DRAFT-20260712-01` | `V8-FEE-OBLIGATION-READ-DRAFT-CURRENT-ADOPTION` | `CURRENT_VERIFIED` |
| `FPMS-V8-APPLICATION-FEE-NOTICE-OBLIGATION-20260712-01` | `V8-APPLICATION-FEE-NOTICE-OBLIGATION-CURRENT-ADOPTION` | `CURRENT_VERIFIED` |

All named successor commits and both customer-decision commits must remain reachable from the
candidate integration tree. A missing, revoked, stale, conflicting or scope-mismatched gate
blocks only this lane and never creates a draft or payment fact.

## Exact ordered task files

- Task file: `tasks/postdemo/v8/FPMS-V8-APPLICATION-DRAFT-MANIFEST-ACTIVATION-20260712-01.md`
- Task file: `tasks/postdemo/v8/FPMS-V8-APPLICATION-INTERNAL-DRAFT-PAYMENT-SEPARATION-20260810-01.md`

## Execution order

1. The controller task alone creates and verifies this manifest with itself as the only
   `SELF_PENDING` row. Its implementer cannot approve it.
2. An independent High reviewer must approve the exact activation candidate with zero P0/P1/P2
   findings before the product row starts.
3. The application internal-draft / payment-separation successor row then executes alone under
   its own task contract, allowlist, targeted RED/GREEN evidence and independent review. Its
   shared `fee_linking_service.py`, `obligation_contracts.py`, `obligation_service.py` and
   `annuity/service.py`, and `cases/lifecycle_overlay_service.py` ownership remains serialized.

## Explicit non-closure

This lane contains no other catalog row or customer gate. It performs no product, schema,
migration, catalog, coverage-ledger, payment, service-receivable or source-activation change.
It does not weaken any test assertion and does not authorize a second draft or actual payment.
