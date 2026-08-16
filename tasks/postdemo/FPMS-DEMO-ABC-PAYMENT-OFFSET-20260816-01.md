# FPMS-DEMO-ABC-PAYMENT-OFFSET-20260816-01

Status: READY
Risk-Class: PROTECTED
Closure-Tags: ["demo", "customer-payment", "offset", "money", "idempotency", "migration"]
Task-Path: tasks/postdemo/FPMS-DEMO-ABC-PAYMENT-OFFSET-20260816-01.md

## Story shape

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: API-first
- evidence_cost: high
- chosen_runbook: P0-prereq-heavy-story

## Design references

- `AGENTS.md`
- `docs/product/v8/domain-contract.md`
- `docs/superpowers/specs/2026-08-15-fpms-local-demo-abc-design.md`
- `tasks/postdemo/FPMS-DEMO-ABC-UNIQUE-AR-BILL-20260816-01.md`

## Exact Closure Slice

For the one local-demo CNY AR bill, add an authenticated idempotent bank-receipt command and an
authenticated idempotent full-offset command. Persist payment method/reference and command hashes.
The receipt initially remains unapplied. The offset is the only applied-bill fact and atomically
sets bill balance/status, payment-line allocated/balance, one SERVICE case-receipt projection and
one active offset. Exact retries reuse the same facts; drift, duplicate reference, wrong client,
currency, amount, consumed balance or concurrent second commands return 4xx without partial writes.

## Explicit Non-Closure

No production/PostgreSQL concurrency certification, partial/multi-bill allocation, multi-currency,
refund, reverse UI, bank reconciliation, attachments, accounting export, dashboard, bad debt,
dunning, manual payment or generic legacy payment/offset endpoint repair. The demo uses admin and
the new demo-scoped commands only.

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-ABC-FINANCE-UI-20260816-01`
- `FPMS-DEMO-ABC-LIVE-E2E-20260816-01`

## Allowed Files

- `backend/alembic/versions/demo_abc_payment_offset_01.py`
- `backend/app/modules/billing/models.py`
- `backend/app/modules/billing/schemas.py`
- `backend/app/modules/billing/service.py`
- `backend/app/modules/billing/api.py`
- `backend/tests/test_demo_abc_payment_offset.py`
- `artifacts/FPMS-DEMO-ABC-PAYMENT-OFFSET-20260816-01/**`

## Verification Commands

1. RED proves the demo receipt/offset commands and durable carriers are absent.
2. Target pytest proves receipt-before-offset truth, exact full allocation, authoritative composite
   response, exact replay, drift/duplicate/wrong-scope rejection and exception rollback.
3. Fresh SQLite migration reaches the new head; duplicate command/reference carriers fail closed.
4. Scoped Ruff and exact allowlist/diff checks pass. No broad/release gate runs.

## Evidence Path

- `artifacts/FPMS-DEMO-ABC-PAYMENT-OFFSET-20260816-01/`

## Rollback

Revert the atomic story commit. Fresh demo databases are disposable; production data migration is
outside closure.

## Done definition

Target checks pass and the exact commit is ready for independent High review. Frontend and live
browser rehearsal remain outside closure.
