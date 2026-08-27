# FPMS-DEMO-V6-UI-PARITY-FEE-STATUS-LABELS-20260827-08AO

Status: ACTIVE
Risk-Tier: HIGH
Closure-Tags: ["fee", "ui"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-FEE-STATUS-LABELS-20260827-08AO.md
Chosen runbook: `P0-single-lane-story`

## Exact Closure Slice

Render the already-authoritative fee-obligation values exercised by the V6 dual-track summary with explicit Simplified Chinese labels, so the customer-visible summary contains no `未识别状态` fallback.

## Explicit Non-Closure

No backend enum, lifecycle, fee amount/status, persistence, API, unrelated UI text, or generic translation architecture change.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-FEE-STATUS-LABELS-20260827-08AO.md`
- `frontend/src/modules/cases/components/FeeObligationLane.vue`
- `frontend/tests/demo-v6-fee-ui-parity-contract.mjs`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity.live-backend.spec.ts`
- `artifacts/FPMS-DEMO-V6-UI-PARITY-FEE-STATUS-LABELS-20260827-08AO/**`

## Verification

Focused fee UI contract, scoped ESLint, frontend typecheck, strict V6 dynamic journey, diff check, independent HIGH review.

## Done Definition

The V6 Stage11 fee cards show authoritative Chinese labels for the current obligation/status/fact values, keep official evidence `PENDING` as `待处理`, and contain no `未识别状态`.
