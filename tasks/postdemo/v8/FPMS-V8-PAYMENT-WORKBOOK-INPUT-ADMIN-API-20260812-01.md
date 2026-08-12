# FPMS-V8-PAYMENT-WORKBOOK-INPUT-ADMIN-API-20260812-01

Status: READY / NOT STARTED
Successor role: WB-I3
Risk: PROTECTED
Task Contract Profile: `TC-API`

## Exact Closure Slice

Add protected same-resource multipart register, review, activate, and retire actions to the
annuity router through WB-I2. Register stores the real `.xlsm` and upload proof through existing
managed storage and cleans only new request files on failure. Preserve 201 new/200 replay,
200 state transitions, 409 conflicts, and 401/403/422 authentication, permission, and validation
semantics. Use exactly `Fee.Edit`; actor and server time come only from server context.

## Explicit Non-Closure

No admin UI, generic upload change, service-price activation, workbook generation, PayList,
payment or ticket state change, permission expansion, default input, or production activation
without an approved active real input.

## Dependencies

- WB-I2 independently accepted after WB-I1 and row 214.
- Sequence: `WB-I1 -> row 214 -> WB-I2 -> WB-I3 -> rows 215-222 -> row 278`.
- Missing real input remains `CONFIG_REQUIRED`; production action is `409 / NO WRITE`.

## Allowed Files

- `backend/app/modules/annuity/api.py`
- `backend/app/modules/annuity/official_payment_workbook_input_schemas.py`
- `backend/tests/test_v8_payment_workbook_input_api.py`
- This task card and its exact evidence path.
- `backend/app/core/storage.py` is read-only.

## Targeted RED / GREEN

Write focused endpoint RED for status, permission, replay, cleanup, and fail-closed semantics;
implement only the API/schema closure; rerun focused GREEN, scoped Ruff, exact diff, and affected
router tests. Prove production refuses `TEST_ONLY` and performs no business write.

## Serialized Ownership

Serialize `annuity/api.py`, the new schemas, shared router tests, managed-storage side effects, and
SQLite-writing verification.

## Evidence Path

- Exact Git commit/range plus task-scoped RED/GREEN, Ruff, router-test, diff, scope, and
  independent-review results. Do not create a legacy artifact directory.

## Rollback Boundary

Revert only this task's exact commit and owned paths before dependent tasks start. Remove only
the owned router/schema changes and focused API test; do not reverse WB-I2 or mutate managed
files, configuration versions, or input facts. Leave accepted predecessors and production inputs untouched.

## Independent Close

Independent High review must bind exact commit/task bytes with zero findings. API acceptance may
establish `CAPABILITY_READY`; it never claims production activation while `CONFIG_REQUIRED`.
