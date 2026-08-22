# FPMS-DEMO-ABC-COMMAND-RESULT-HARDENING-20260817-01

Status: READY
Risk-Tier: HIGH
Risk-Class: PROTECTED
Closure-Tags: ["api", "billing", "data", "demo", "idempotency", "payment", "reconciliation", "ui"]
Task-Path: tasks/postdemo/FPMS-DEMO-ABC-COMMAND-RESULT-HARDENING-20260817-01.md
Chosen-Runbook: protected-single-lane-story

## Authority and IDs

- Customer decision: `DEC-LOCAL-DEMO-ABC-20260815`.
- Controlling design: `docs/superpowers/specs/2026-08-15-fpms-local-demo-abc-design.md` §6.4/§9.
- Independent findings: `P1-3`, `P1-4`.
- Audit IDs: `FIN-BILL-001`, `FIN-OFFSET-001` (local/fresh SQLite command outcome only).
- V8 catalog IDs: `None`; non-release local demo recovery.
- Dependencies: commits `fc3c381` and `ef0d84c`; shared billing owner is serialized here.

## Exact Closure Slice

Add one demo-owned durable command carrier for BILL/PAYMENT/OFFSET with actor, operation, exact
canonical request snapshot/hash, `IN_PROGRESS|COMPLETED` state and immutable completed response JSON.
Reserve before the business command, freeze the authoritative composite before returning, heal a
commit-then-drop gap from the existing operation-owned source record, and expose the frozen
reconciliation routes/statuses: completed 200, durable pending 202, absent 404. Make exact replay
return the stored result. Frontend reconciliation runs only for an Axios transport error without a
response; deterministic 4xx including idempotency drift is rethrown unchanged, while 202 remains
pending and never becomes a second intent.

## Explicit Non-Closure

No production distributed command bus, background timeout/reaper, PostgreSQL closure, reverse
command, generic billing rewrite, security, dashboard or release.

## Expected Paths

- billing model/migration/API/service and focused demo finance tests;
- demo frontend API and executable Node behavior contract.

## Allowed Files

- `backend/app/modules/billing/models.py`
- `backend/app/modules/billing/service.py`
- `backend/app/modules/billing/api.py`
- `backend/app/modules/billing/schemas.py`
- `backend/alembic/versions/demo_abc_command_reconcile_01.py`
- `backend/tests/test_demo_abc_unique_ar_bill.py`
- `backend/tests/test_demo_abc_payment_offset.py`
- `frontend/src/modules/demo/demo.api.ts`
- `frontend/src/modules/demo/command-reconcile.ts`
- `frontend/tests/demo-abc-command-reconcile.mjs`
- `tasks/postdemo/FPMS-DEMO-ABC-COMMAND-RESULT-HARDENING-20260817-01.md`

## Verification Commands

1. RED proves reconciliation currently rehydrates mutable payment state, has no 202 carrier, uses
   non-frozen routes and masks deterministic 409.
2. GREEN proves reservation, 202, immutable stored result, exact replay, drift preservation and
   commit-then-drop healing.
3. Scoped backend pytest/Ruff and frontend executable contract/typecheck pass.

## Rollback

Revert the atomic commit. The migration is used only on fresh disposable local-demo databases.

## Done definition

Unknown outcome is durably distinguishable from absent/completed, completed reconciliation is
immutable, deterministic 4xx cannot be converted to old success, focused gates pass, and independent
High acceptance remains required.
