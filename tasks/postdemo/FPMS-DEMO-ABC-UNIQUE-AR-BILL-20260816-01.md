# FPMS-DEMO-ABC-UNIQUE-AR-BILL-20260816-01

Status: READY
Risk-Class: PROTECTED
Closure-Tags: ["demo", "billing", "money", "idempotency", "migration"]
Task-Path: tasks/postdemo/FPMS-DEMO-ABC-UNIQUE-AR-BILL-20260816-01.md

## Story shape

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: API-first
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Design references

- `AGENTS.md`
- `docs/product/v8/domain-contract.md`
- `docs/superpowers/specs/2026-08-15-fpms-local-demo-abc-design.md`
- `tasks/postdemo/FPMS-DEMO-ABC-RUNTIME-SERVICE-DRAFT-20260816-01.md`

## Exact Closure Slice

Add a demo-scoped authenticated command that consumes exactly one positive, CNY, SERVICE-only,
LOCKED fee draft into exactly one AR bill. Persist a billing-owned unique draft-source carrier and
canonical command hash. Same-key/same-command replay returns the same full bill; key drift or a
second key for an already consumed draft returns 409 without writes. The bill date is explicit,
amounts derive only from the frozen draft, and billed drafts cannot be unlocked.

## Explicit Non-Closure

No generic production bill repair, historical duplicate cleanup, PostgreSQL certification, manual
bill, AP, tax, invoice delivery, bad debt, dunning, payment, offset, dashboard or frontend. The
legacy `/bills/from-drafts` endpoint remains outside this local-demo command and must not be used in
the demo journey.

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-ABC-PAYMENT-OFFSET-20260816-01`
- `FPMS-DEMO-ABC-FINANCE-UI-20260816-01`
- `FPMS-DEMO-ABC-LIVE-E2E-20260816-01`

## Allowed Files

- `backend/alembic/versions/demo_abc_bill_source_01.py`
- `backend/app/modules/billing/models.py`
- `backend/app/modules/billing/schemas.py`
- `backend/app/modules/billing/service.py`
- `backend/app/modules/billing/api.py`
- `backend/app/modules/fees/service.py`
- `backend/tests/test_demo_abc_unique_ar_bill.py`
- `artifacts/FPMS-DEMO-ABC-UNIQUE-AR-BILL-20260816-01/**`

## Verification Commands

1. RED proves OPEN drafts and replay/duplicate protection are absent.
2. Target pytest proves LOCKED-only creation, exact full amount, source ownership, exact replay,
   drift/second-key rejection, unlock rejection and rollback/no-write behavior.
3. Fresh SQLite migration reaches the new head and direct duplicate carriers fail at the DB layer.
4. Scoped Ruff and exact allowlist/diff checks pass. No broad/release gate runs.

## Evidence Path

- `artifacts/FPMS-DEMO-ABC-UNIQUE-AR-BILL-20260816-01/`

## Rollback

Revert the atomic story commit. Fresh demo databases are disposable; production migration and
historical data remediation are outside this task.

## Done definition

Target checks pass and the exact commit is ready for independent High review. Customer payment and
offset remain outside closure.
