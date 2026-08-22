# FPMS-DEMO-ABC-FINANCE-UI-20260816-01

Status: READY
Risk-Class: PROTECTED
Closure-Tags: ["demo", "frontend", "runtime-input", "billing", "money"]
Task-Path: tasks/postdemo/FPMS-DEMO-ABC-FINANCE-UI-20260816-01.md

## Exact Closure Slice

Add one Simplified-Chinese, sidebar-reachable local-demo page that loads an existing case and the
validated runtime bundle summary, then visibly drives the real APIs through SERVICE obligation,
PAY instruction, one draft, lock, unique AR bill, customer bank receipt and full offset. Display
bundle/template/rate provenance and authoritative bill/payment/offset states. Each visible intent
reuses one idempotency key across retries; unavailable/invalid money is never displayed as zero.

## Explicit Non-Closure

No generic billing page rewrite, dashboard, production upload/activation, customer/case form
replacement, OA UI rewrite, route-wide auth cleanup, remote hosting, security, responsive design or
visual redesign. Client and case are created through the existing visible pages before entering the
demo console.

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-ABC-LIVE-E2E-20260816-01`

## Allowed Files

- `backend/app/modules/fees/demo_service.py`
- `backend/app/modules/fees/demo_service_schemas.py`
- `backend/tests/test_demo_abc_runtime_service_draft.py`
- `frontend/src/modules/demo/demo.api.ts`
- `frontend/src/modules/demo/pages/DemoAbc.vue`
- `frontend/src/router/index.ts`
- `frontend/src/constants/menu.ts`
- `frontend/tests/demo-abc-contract.mjs`
- `artifacts/FPMS-DEMO-ABC-FINANCE-UI-20260816-01/**`

## Verification Commands

1. RED proves the route/API/page contract is absent.
2. Backend focused test proves bundle summary includes immutable template and rate provenance.
3. Frontend contract test, typecheck, lint and build pass; source gate rejects mocks and legacy
   generic billing mutations in the page.
4. Exact allowlist/diff checks pass. No broad Playwright or release gate runs.

## Evidence Path

- `artifacts/FPMS-DEMO-ABC-FINANCE-UI-20260816-01/`

## Rollback

Revert the atomic story commit. No runtime bundle or business rows are stored by the frontend.

## Done definition

Target checks pass and the exact commit is ready for independent High review. Fresh live browser
rehearsal remains outside closure.
