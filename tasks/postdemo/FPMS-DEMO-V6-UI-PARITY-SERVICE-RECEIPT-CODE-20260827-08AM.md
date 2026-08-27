# FPMS-DEMO-V6-UI-PARITY-SERVICE-RECEIPT-CODE-20260827-08AM

Status: ACTIVE
Risk-Tier: HIGH
Closure-Tags: ["fee", "api", "ui"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-SERVICE-RECEIPT-CODE-20260827-08AM.md
Chosen runbook: `P0-single-lane-story`

## Exact Closure Slice

Accept the backend's aggregate SERVICE case-receipt projection for the current multi-line bill:
`fee_code` may be absent; if present it must identify one of the bill's SERVICE item codes.

## Explicit Non-Closure

No backend, schema, receipt allocation, fee amount/status, endpoint, generic parser, page, Stage 11,
or unrelated finance change.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-SERVICE-RECEIPT-CODE-20260827-08AM.md`
- `frontend/src/modules/demo/demo.api.ts`
- `frontend/src/modules/demo/demo.contract.ts`
- `frontend/tests/demo-v6-fee-ui-parity-contract.mjs`
- `artifacts/FPMS-DEMO-V6-UI-PARITY-SERVICE-RECEIPT-CODE-20260827-08AM/**`

## Verification

Focused fee UI contract, scoped ESLint, frontend typecheck, diff check, independent HIGH review.

## Done Definition

Null aggregate code passes; a present member code passes; a present foreign code fails; all existing
SERVICE amount, type, balance, and settlement checks remain active.
