# FPMS-DEMO-ABC-FINANCE-DECODER-HARDENING-20260817-02

Status: READY
Risk-Tier: HIGH
Risk-Class: PROTECTED
Closure-Tags: ["billing", "data", "demo", "frontend", "money", "ui"]
Task-Path: tasks/postdemo/FPMS-DEMO-ABC-FINANCE-DECODER-HARDENING-20260817-02.md
Chosen-Runbook: protected-single-lane-story

## Authority and IDs

- Customer decision: `DEC-LOCAL-DEMO-ABC-20260815`.
- Controlling design: `docs/superpowers/specs/2026-08-15-fpms-local-demo-abc-design.md` §6.4.
- Independent finding: `P1-6`.
- Dependency: commit `3da45be`; frontend demo contract owner is serialized here.

## Exact Closure Slice

Reject impossible calendar dates by exact component validation. Cross-bind every ABC finance
composite before it becomes visible: payment/line/bill identities, client/case/currency and initial
amount projections; offset/line/bill/receipt identities, currency, date, non-reversed state and final
settled/full-allocation projections; bill service-only totals and status/balance invariants.

## Explicit Non-Closure

No generic billing adapter rewrite, non-ABC currency, partial allocation, reverse, dashboard,
production or release.

## Allowed Files

- `frontend/src/modules/demo/demo.contract.ts`
- `frontend/tests/demo-abc-finance-decoder.mjs`
- `tasks/postdemo/FPMS-DEMO-ABC-FINANCE-DECODER-HARDENING-20260817-02.md`

## Verification Commands

1. RED executable decoder probes accept February overflow and wrong-object composites.
2. GREEN rejects each mutation with `FINANCE_CONTRACT_INVALID` and preserves exact valid payloads.
3. Node behavior contract, frontend typecheck and scoped lint/diff checks pass.

## Rollback

Revert the atomic commit.

## Done definition

Every ABC finance response is both shape-valid and internally the same business object/projection;
independent High acceptance remains required.
