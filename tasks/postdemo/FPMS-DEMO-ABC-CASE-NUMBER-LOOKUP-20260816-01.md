# FPMS-DEMO-ABC-CASE-NUMBER-LOOKUP-20260816-01

Status: READY
Risk-Class: PROTECTED
Closure-Tags: ["demo", "frontend", "navigation", "case"]
Task-Path: tasks/postdemo/FPMS-DEMO-ABC-CASE-NUMBER-LOOKUP-20260816-01.md

## Exact Closure Slice

Make the sidebar-reachable ABC demo console load the just-created case by its visible exact case
number, using the existing `getCaseByCaseNo` read contract. Remove the requirement for an operator
to obtain or paste an internal UUID or visit the case detail route before entering the demo.

## Explicit Non-Closure

No case detail repair, receipt endpoint change, generic case search rewrite, fuzzy matching, route
guard work, production deployment, security or release gate.

## Allowed Files

- `frontend/src/modules/demo/pages/DemoAbc.vue`
- `frontend/tests/demo-abc-contract.mjs`
- `artifacts/FPMS-DEMO-ABC-CASE-NUMBER-LOOKUP-20260816-01/**`

## Verification Commands

1. RED proves the console still imports direct `getCase` and asks for a UUID.
2. GREEN proves the exact visible case number is passed to `getCaseByCaseNo`.
3. Focused source contract, typecheck and lint pass.
4. Live browser loads a fresh case by case number with no detail-route detour.

## Evidence Path

- `artifacts/FPMS-DEMO-ABC-CASE-NUMBER-LOOKUP-20260816-01/`

## Rollback

Revert the atomic product commit.

## Done definition

Target checks and live verification pass. Independent High acceptance is still required.
