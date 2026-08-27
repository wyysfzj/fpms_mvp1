# FPMS-DEMO-V6-UI-PARITY-SERVICE-RECEIPT-NULL-CODE-20260827-08AN

Status: ACTIVE
Risk-Tier: HIGH
Closure-Tags: ["fee", "api"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-SERVICE-RECEIPT-NULL-CODE-20260827-08AN.md
Chosen runbook: `P0-single-lane-story`

## Exact Closure Slice

Preserve the aggregate SERVICE case receipt's absent fee-code fact as JSON `null` in the Demo full-offset response instead of inventing an empty-string code.

## Explicit Non-Closure

No receipt allocation, fee amount/status, persistence, generic endpoint, frontend, page, Stage 11, or unrelated finance change.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-SERVICE-RECEIPT-NULL-CODE-20260827-08AN.md`
- `backend/app/modules/billing/api.py`
- `backend/app/modules/billing/schemas.py`
- `backend/tests/test_demo_abc_payment_offset.py`
- `artifacts/FPMS-DEMO-V6-UI-PARITY-SERVICE-RECEIPT-NULL-CODE-20260827-08AN/**`

## Verification

Focused two-receipt/two-offset backend test, scoped Ruff, diff check, independent HIGH review.

## Done Definition

The response emits `fee_code: null` when the persisted aggregate receipt has no fee code; all existing two-receipt/two-offset settlement assertions remain green.
