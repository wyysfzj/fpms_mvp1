# FPMS-DEMO-ABC-FRONTEND-RECONCILE-IDENTITY-HARDENING-20260817-03

Status: READY
Risk-Tier: HIGH
Risk-Class: PROTECTED
Closure-Tags: ["billing", "data", "demo", "frontend", "idempotency", "ui"]
Task-Path: tasks/postdemo/FPMS-DEMO-ABC-FRONTEND-RECONCILE-IDENTITY-HARDENING-20260817-03.md
Chosen-Runbook: protected-single-lane-story

## Authority and IDs

- Customer decision: `DEC-LOCAL-DEMO-ABC-20260815`.
- Controlling design: `docs/superpowers/specs/2026-08-15-fpms-local-demo-abc-design.md`.
- Independent findings: second High review `P1-1`, `P1-2`, `P1-5`.
- Dependency: commit `c331864`; frontend demo API and contract owner is serialized here.

## Exact Closure Slice

Treat a fulfilled finance-command POST 202 as pending and poll only its exact durable GET carrier;
never issue a second mutation. Reconcile draft locking only after an unknown transport result and
preserve every response-bearing 4xx. Require the billed SERVICE line fee code and bind it exactly to
the resulting case receipt fee code before displaying a successful offset.

## Explicit Non-Closure

No generic billing adapter rewrite, partial allocation, reverse, dashboard, production, security,
PostgreSQL, customer input activation, or release.

## Allowed Files

- `frontend/src/modules/demo/command-reconcile.ts`
- `frontend/src/modules/demo/demo.api.ts`
- `frontend/src/modules/demo/demo.contract.ts`
- `frontend/tests/demo-abc-command-reconcile.mjs`
- `frontend/tests/demo-abc-finance-decoder.mjs`
- this task card

## Verification Commands

1. RED executable probes show direct POST 202 is not polled, deterministic lock 409 is masked, and
   a same-case wrong receipt fee code is accepted.
2. GREEN executable probes cover 202 -> 202 -> 200 without a second mutation, unknown lock transport
   reconciliation, deterministic 409 with zero GET, and wrong-fee rejection.
3. Both Node behavior contracts, frontend typecheck, scoped lint and diff checks pass.

## Rollback

Revert the atomic commit.

## Done definition

The ABC UI cannot convert a known command error into success, can recover a genuinely pending or
transport-unknown command without duplicate writes, and only displays fee-consistent offset results.
Independent High acceptance remains required.
