# FPMS-DEMO-INTEGRATED-A-UI-BOUNDARY-20260821-06A

Status: ACTIVE
Risk-Class: PROTECTED
Risk-Tier: HIGH
Closure-Tags: ["demo", "browser", "ui", "evidence"]
Task-Path: tasks/postdemo/FPMS-DEMO-INTEGRATED-A-UI-BOUNDARY-20260821-06A.md
Role: Implementer
Dependencies: ["FPMS-DEMO-INTEGRATED-A-OA-REPLY-OUTPUT-20260821-05A APPROVED 0/0/0"]

## Exact Closure Slice

Remove the accidental Task-5 call-count freeze from the canonical browser static guard while
preserving its fail-closed transport boundary. Additional passive `waitForResponse` observations
are permitted, and browser navigation remains restricted to configured `baseUrl` template paths.
Evidence writes remain restricted to pretty-printed JSON under `evidenceDir` with the exact final
ledger name or the approved Task 5…10 checkpoint-ledger names.

The guard must continue to reject direct attachment/review API calls, direct network primitives,
request interception, code injection, non-`baseUrl` navigation, arbitrary filesystem writes and
all non-audited lifecycle API calls.

## Explicit Non-Closure

No IA-07…18 business action, no canonical journey implementation, no product frontend/backend
change, no API allowlist operation change, no runtime bundle change, no schema/migration, no
customer/official truth, no broad/product/release gate.

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-a-static-contract.mjs`
- `frontend/tests/demo-integrated-ui-boundary.mjs`
- `tasks/postdemo/FPMS-DEMO-INTEGRATED-A-UI-BOUNDARY-20260821-06A.md`
- `artifacts/FPMS-DEMO-INTEGRATED-A-UI-BOUNDARY-20260821-06A/**`

## Verification Commands

- Run the new UI-boundary contract RED/GREEN.
- Run the canonical integrated static contract and Playwright list discovery.
- Prove direct network, non-base navigation and arbitrary write paths still fail closed.
- Bind the exact candidate commit/tree to independent High review.

## Evidence Path

- `artifacts/FPMS-DEMO-INTEGRATED-A-UI-BOUNDARY-20260821-06A/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-INTEGRATED-A-SECOND-OA-20260821-06`
- `FPMS-DEMO-INTEGRATED-A-GRANT-20260821-07`
- `FPMS-DEMO-INTEGRATED-A-FINANCE-20260821-08`
- `FPMS-DEMO-INTEGRATED-A-RUNNER-20260821-09`
- `FPMS-DEMO-INTEGRATED-A-FINAL-20260821-10`

## Done Definition

Focused tests pass; the guard accepts the approved additional UI observation and checkpoint-ledger
shape without permitting a new transport or arbitrary write surface; independent High review is
`APPROVED` with `P0/P1/P2 = 0/0/0`.
