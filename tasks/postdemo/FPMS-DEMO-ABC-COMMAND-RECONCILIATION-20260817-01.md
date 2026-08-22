# FPMS-DEMO-ABC-COMMAND-RECONCILIATION-20260817-01

Status: READY
Risk-Tier: HIGH
Risk-Class: PROTECTED
Closure-Tags: ["demo", "billing", "payment", "offset", "idempotency", "reconciliation"]
Task-Path: tasks/postdemo/FPMS-DEMO-ABC-COMMAND-RECONCILIATION-20260817-01.md

## Exact Closure Slice

For the local `LOCAL_ABC_E2E` command surface only: durably bind one bank receipt intent to one
demo AR bill; expose actor-owned GET-by-idempotency-key reconciliation for bill, payment and full
offset; make the frontend reconcile after an unknown POST outcome before retry; reconcile draft
locking through authoritative GET state; bind the exact CaseReceipt ID into the offset command;
include fee year in the canonical receipt identity; and add SQLite-enforced positive/non-negative
money projection checks for newly written ABC rows.

## Explicit Non-Closure

No generic billing redesign, partial or cross-bill allocation, reverse UI, production PostgreSQL
concurrency closure, historical duplicate repair, dashboard, multi-currency, security or release.

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-ABC-FINANCE-DECODER-20260817-01`
- `FPMS-DEMO-ABC-EVIDENCE-REBUILD-20260817-01`

## Allowed Files

- `backend/app/modules/billing/models.py`
- `backend/app/modules/billing/schemas.py`
- `backend/app/modules/billing/service.py`
- `backend/app/modules/billing/api.py`
- `backend/alembic/versions/demo_abc_command_reconcile_01.py`
- `backend/tests/test_demo_abc_unique_ar_bill.py`
- `backend/tests/test_demo_abc_payment_offset.py`
- `frontend/src/modules/demo/demo.api.ts`
- `frontend/src/modules/demo/pages/DemoAbc.vue`
- `frontend/tests/demo-abc-command-reconcile.mjs`
- `artifacts/FPMS-DEMO-ABC-COMMAND-RECONCILIATION-20260817-01/**`

## Verification Commands

1. RED covers second payment intent, exact receipt replay, command GET ownership and lost-response reconciliation.
2. GREEN focused backend tests prove exact replay/no-write and SQLite constraints.
3. Frontend contract test proves POST failure triggers GET reconciliation before the same intent can retry.
4. Ruff, frontend lint/typecheck for touched files and exact scope checks pass.

## Evidence Path

- `artifacts/FPMS-DEMO-ABC-COMMAND-RECONCILIATION-20260817-01/`

## Rollback

Revert the atomic implementation commit. The migration is forward-only and must not be applied to
a shared database during this local task.

## Done definition

An unknown response cannot create a second ABC command, a bill cannot own two demo payment intents,
and offset replay returns the exact receipt created by that command. Independent High acceptance
remains required.
