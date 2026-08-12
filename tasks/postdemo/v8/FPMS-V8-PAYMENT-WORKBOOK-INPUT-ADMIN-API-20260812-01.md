# FPMS-V8-PAYMENT-WORKBOOK-INPUT-ADMIN-API-20260812-01

Status: IMPLEMENTED / AWAITING INDEPENDENT REVIEW
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

## Frozen HTTP Contract

- `POST /payment-workbook-inputs` is multipart with required `template_file`,
  `upload_proof_file`, `template_version`, `effective_from`, `source_classification`, and
  `idempotency_key`; `effective_to` is optional. The API hashes both request streams and WB-I2
  independently re-hashes managed files; hashes are not client fields. New registration returns
  201; exact replay returns 200.
- `POST /payment-workbook-inputs/{version_id}/review` accepts only `decision` and `reason`.
- `POST /payment-workbook-inputs/{version_id}/activate` accepts only `idempotency_key`.
- `POST /payment-workbook-inputs/{version_id}/retire` accepts only `reason` and
  `idempotency_key`. These three transitions return 200.
- All four routes require `Fee.Edit`. Actor comes from authenticated server context;
  validation/review time comes from WB-I2 and activation/retirement time plus
  `runtime_profile` come from server configuration. No request schema exposes actor, time, managed
  path, current identity override, or runtime profile.
- Managed destinations are deterministic from a SHA-256 of the idempotency key and use generated
  `template.xlsm` and `upload-proof.bin` names; client filenames never become paths. Directory
  creation is exclusive. An exact retry reuses both existing files only when both request hashes
  agree; partial or differing files conflict. On failure, the API removes only files and directory
  created by that request, never a replay's pre-existing files.
- Responses expose version, source/version hashes, workflow/activation/effective/lineage/current
  state and server actors/times, but never managed storage paths or derived official acceptance,
  payment, ticket, PayList, or legal facts. The caller commits on success and rolls back on every
  exception; WB-I2 remains commit/rollback-free.

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
