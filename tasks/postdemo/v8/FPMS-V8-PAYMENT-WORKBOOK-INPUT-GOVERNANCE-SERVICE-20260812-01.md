# FPMS-V8-PAYMENT-WORKBOOK-INPUT-GOVERNANCE-SERVICE-20260812-01

Status: READY / NOT STARTED
Successor role: WB-I2
Risk: PROTECTED
Task Contract Profile: `TC-BE`

## Exact Closure Slice

Create one governance service that re-hashes already managed template/proof files, idempotently
registers DRAFT input, invokes row 214's read-only structure validation, and performs independent
review plus activate/retire transitions. Fail closed on missing files, hash/structure/scope/time
conflicts, invalid approval, actor overlap, or predecessor conflict. Macros are read/preserved,
never executed.

## Explicit Non-Closure

No multipart HTTP, router, UI, formal workbook generation, official acceptance, payment, ticket,
PayList change, client-supplied actor/time, or production activation claim.

## Dependencies

- WB-I1 and row 214 independently accepted before RED.
- Sequence: `WB-I1 -> row 214 -> WB-I2 -> WB-I3 -> rows 215-222 -> row 278`.
- `TEST_ONLY` registration is restricted to explicit isolated-test context and is always rejected
  for production activation.

## Allowed Files

- `backend/app/modules/annuity/official_payment_workbook_input_service.py`
- `backend/tests/test_v8_payment_workbook_input_service.py`
- This task card and its exact evidence path.
- Row 214's adapter is a read-only dependency.

## Targeted RED / GREEN

Write focused service RED for register/validate/review/activate/retire and every rollback boundary;
implement only the service; rerun focused GREEN, scoped Ruff, exact diff, and affected tests.
Missing reviewed real input stays `CONFIG_REQUIRED` and production requests are `409 / NO WRITE`.

## Serialized Ownership

Serialize the service path, its tests, row 214 adapter consumption, and SQLite-writing checks.
The service never commits; its caller owns the transaction.

## Evidence Path

- Exact Git commit/range plus task-scoped RED/GREEN, Ruff, affected-test, diff, scope, and
  independent-review results. Do not create a legacy artifact directory.

## Rollback Boundary

Revert only this task's exact commit and owned paths before dependent tasks start. Remove only
the owned service and focused test; do not reverse WB-I1, row 214, managed files, or stored input
facts. Leave accepted predecessors and production inputs untouched.

## Independent Close

Independent High review must bind the exact commit/task bytes and report zero findings.
Acceptance may prove `CAPABILITY_READY + CONFIG_REQUIRED` and never claims production activation.
