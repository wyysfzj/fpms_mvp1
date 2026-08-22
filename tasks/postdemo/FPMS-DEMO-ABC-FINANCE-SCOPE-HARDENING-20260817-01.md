# FPMS-DEMO-ABC-FINANCE-SCOPE-HARDENING-20260817-01

Status: READY
Risk-Tier: HIGH
Risk-Class: PROTECTED
Closure-Tags: ["api", "billing", "data", "demo", "migration", "payment", "sqlite"]
Task-Path: tasks/postdemo/FPMS-DEMO-ABC-FINANCE-SCOPE-HARDENING-20260817-01.md
Chosen-Runbook: protected-single-lane-story

## Authority and IDs

- Customer scope decision: `DEC-LOCAL-DEMO-ABC-20260815`.
- Controlling design: `docs/superpowers/specs/2026-08-15-fpms-local-demo-abc-design.md`.
- Independent findings: `P1-5`, `P1-7`, `P2-2`.
- Audit IDs: `FIN-BILL-001`, `FIN-OFFSET-001` (local/fresh SQLite closure only).
- V8 catalog IDs: `None` — this is a non-release local demo recovery story.
- Dependency: `FPMS-DEMO-ABC-TRUST-BOUNDARY-HARDENING-20260817-01` commit `fc3c381`.

## Exact Closure Slice

Remove the local ABC migration's global money CHECK constraints and preflight from generic billing
tables so valid existing prepayment semantics remain unchanged. Enforce the ABC happy-path money
projections in its owned command service with fixed two-decimal values; construct the exact canonical
`case_id|fee_code|fee_type|year_or_-|currency` receipt key with delimiter/whitespace rejection; and
make local ABC requests reject coercion, non-two-decimal money and whitespace identities while
returning 404 for missing resources, 400 for deterministic client/currency/balance/content errors,
and 409 only for lifecycle/idempotency/ownership conflicts.

## Explicit Non-Closure

No generic billing redesign, production PostgreSQL closure, historic database repair, partial or
cross-bill allocation, prepayment model change, reverse UI, dashboard, security or release.

## Expected Paths

- `backend/app/modules/billing/{models.py,schemas.py,service.py}`
- `backend/alembic/versions/demo_abc_command_reconcile_01.py`
- focused demo finance tests plus the existing unified-receipt prepayment regression.

## Allowed Files

- `backend/app/modules/billing/models.py`
- `backend/app/modules/billing/schemas.py`
- `backend/app/modules/billing/service.py`
- `backend/alembic/versions/demo_abc_command_reconcile_01.py`
- `backend/tests/test_demo_abc_unique_ar_bill.py`
- `backend/tests/test_demo_abc_payment_offset.py`
- `backend/tests/test_fee_unified_query_api.py`
- `tasks/postdemo/FPMS-DEMO-ABC-FINANCE-SCOPE-HARDENING-20260817-01.md`

## Verification Commands

1. RED proves the existing `received > receivable` prepayment fixture fails under the global CHECK,
   the colon receipt key is written and loose request values are accepted/coerced.
2. GREEN runs the two demo finance files plus the exact unified-receipt regression.
3. Scoped Ruff and diff checks pass.

## Rollback

Revert this atomic commit. The edited migration is unreleased and accepted only on fresh disposable
local-demo databases; no shared database is migrated by this task.

## Done definition

Generic prepayments work unchanged, the demo command writes the exact unambiguous receipt key,
strict API inputs/statuses are observable, focused tests pass, and independent High acceptance is
still required.
