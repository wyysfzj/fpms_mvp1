# FPMS-V8-PAYMENT-WORKBOOK-INPUT-VERSION-CARRIER-20260812-01

Status: READY / NOT STARTED
Successor role: WB-I1
Risk: PROTECTED
Task Contract Profile: `TC-DB`

## Exact Closure Slice

Add the `GLOBAL` payment-workbook input-version carrier with immutable
`PRODUCTION|TEST_ONLY` source classification, template/source/proof/validation hashes, effective
interval, review and activation tuples, supersession, idempotency, current identity, real actors,
and server time. Constraints permit active only from `PRODUCTION + APPROVED + VALIDATED` and keep
reviewer distinct from uploader.

## Explicit Non-Closure

No endpoint, upload, `.xlsm` validation, review/activation workflow, workbook generation, PayList
change, real input, seed, default, or production activation.

## Dependencies

- Current decoupling adoption task independently accepted.
- row175 terminal PASS is required after Task 1 adoption; WB-I1 depends on row175, so there is no
  cycle. WB-I1 is an external successor prerequisite, not a row175 manifest member.
- Sequence:
  `FPMS-V8-PAYMENT-WORKBOOK-MANIFEST-ACTIVATION-20260712-01 (row175) -> WB-I1 -> row214 -> WB-I2 -> WB-I3 -> rows215-222 -> row278`.
- Missing real input is `CONFIG_REQUIRED` and does not block this capability task.

## Allowed Files

- `backend/alembic/versions/v8_payment_workbook_input_version.py`
- `backend/app/modules/annuity/models.py`
- `backend/app/models/__init__.py`
- `backend/tests/test_v8_payment_workbook_input_version.py`
- This task card and its exact evidence path.

## Targeted RED / GREEN

Write and run the carrier contract test RED before implementation; add only the migration/model
closure; rerun focused GREEN, scoped Ruff, migration checks, and exact diff checks. Prove a
`TEST_ONLY` row cannot become active and invalid production state is `409 / NO WRITE`.

## Serialized Ownership

Serialize the migration, Alembic head, `annuity/models.py`, model export, and all SQLite-writing
tests. No concurrent owner may edit them.

## Evidence Path

- Exact Git commit/range plus task-scoped RED/GREEN, Ruff, migration, diff, scope, and
  independent-review results. Do not create a legacy artifact directory.

## Rollback Boundary

Revert only this task's exact commit and owned paths before dependent tasks start. If its
migration has reached an environment, preserve forward-only migration and data compatibility
through a separately reviewed corrective migration; perform no destructive downgrade or data deletion.
Leave accepted predecessors and production inputs untouched.

## Independent Close

Independent High review must bind the exact commit and current task bytes with zero P0/P1/P2
findings. Acceptance may establish `CAPABILITY_READY`; `CONFIG_REQUIRED` remains valid and this
task never claims production activation.
