# Story V8-FEE-REDUCTION-APPROVAL-API-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Outcome: adopt the frozen fee-reduction approval create and list HTTP contracts onto
  the current lean tree without replacing the current shared fees API or absorbing an
  adjacent successor.
- Change mode: exact per-hunk adoption from archive checkpoint `6b2ef89`, followed by
  current-tree TDD and scoped regression verification.
- Authority: the fee, source-provenance, evidence-lineage, customer-decision and SQLite
  rules in `docs/product/v8/domain-contract.md`; the no-default/no-source-activation rules
  in `docs/product/v8/source-decision-registry.md`; frozen catalog rows `95` and `96`;
  their exact task contracts; and the row-95 Delta-4 latest-wins appendix.
- Base: `3c0ee20730c9ce6727639e8bdd9a1611f759853c`.

## Catalog IDs and dependency order

1. `FPMS-V8-FEE-REDUCTION-APPROVAL-CREATE-API-20260712-01` (ordinal `95`,
   profile `TC-API`) depends on accepted row `94`,
   `FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01`.
2. `FPMS-V8-FEE-REDUCTION-APPROVAL-LIST-API-20260712-01` (ordinal `96`,
   profile `TC-API`) depends on row `95` and was implemented second.

The accepted row-94 service adoption commit `1a886c4` is an ancestor of the base. This
story delegates creation to that service and does not duplicate its validation, evidence,
identity, reuse or conflict decisions.

## Exact row-95 boundary

The exact route is
`POST /api/v1/fees/cases/{case_id}/reduction-approvals` with `Fee.Edit`. Its strict
request model preserves the frozen field order and rejects missing, extra, malformed,
timezone-aware or client-idempotency input.

The body `case_id` remains intentional. A path/body mismatch returns 400
`FEE_REDUCTION_APPROVAL_CASE_MISMATCH` with both identifiers before service invocation.
The adapter passes the exact naive client `confirmed_at` and the server-owned current
user as `confirmed_by`, calls `record_fee_reduction_approval` exactly once, and returns
the direct approval identifier.

`CREATED` maps to 201 and `REUSED` to 200. Either success commits once; any service or
commit error rolls back once. Existing 401, 403, 404, 409 and 422 semantics are preserved.

## Exact row-96 boundary

The bodyless
`GET /api/v1/fees/cases/{case_id}/reduction-approvals` route uses `Fee.Read` and returns a
bare list. A missing case returns 404 without listing or writing.

The query returns every confirmed approval whose source-evidence identity is current for
the requested case, ordered by confirmation time and approval identifier. It preserves
the stored approval ratio and scope facts without selecting, defaulting or inferring a
different reduction ratio.

Current evidence requires the exact persisted identity
`current_identity_key == f"{case_id}|{lineage_key}"`. The SQL uses SQLite-safe string
concatenation to project that equality as `is_current`. The case/confirmation query does
not filter malformed non-null identities before validation. The selected evidence case,
lineage and current-identity values plus projected boolean are post-validated; malformed
persisted identity data therefore remains visible and fails closed with 409
`FEE_REDUCTION_APPROVAL_SOURCE_IDENTITY_CORRUPT`.

The stored fee-scope snapshot must be the exact canonical JSON object containing the
frozen schema and a non-empty, sorted, unique list of canonical fee-code strings. Each
code is nonblank, trimmed, NUL-free, UTF-8 encodable and at most 64 characters. Duplicate
JSON keys, noncanonical bytes, invalid lowercase SHA-256 or a hash mismatch fail closed
with 409 `FEE_REDUCTION_APPROVAL_SCOPE_CORRUPT`.

## Current-tree adoption

The current base lacked the approval API schema and both routes/tests. Only the exact
archive schema/test bytes and route/helper hunks for rows 95 and 96 were adopted.

The existing official-fee preview successor in the shared API was preserved. The shared
file was not checked out from the archive, and the obligation instruction or any later
fee-obligation detail seam was not absorbed.

The initial focused tests were adopted from archive `6b2ef89`. The create test remains
byte-identical; the list test was then extended for the independently verified review
findings:

- create test blob: `64a2bb0e01357570d6b89bec5f3b3f2e54a6888e`;
- corrected list test blob: `46ff2113bc4f0766b6b54f734f39aeed761681a6`.

The first story commit `968ba9a` was rejected by independent review and is stale. This
story rebuilds the single commit from the same base with both review findings corrected;
no review, ledger or disposition file is modified by the implementer.

## Exact changed paths

### Product

- `backend/app/modules/fees/fee_reduction_approval_schemas.py`
- `backend/app/modules/fees/api.py`

### Focused tests

- `backend/tests/test_v8_fee_reduction_approval_create_api.py`
- `backend/tests/test_v8_fee_reduction_approval_list_api.py`

### Story

- `docs/product/v8/stories/V8-FEE-REDUCTION-APPROVAL-API-CURRENT-ADOPTION.md`

## TDD and verification

Under the controller-granted serialized SQLite/shared lane:

- row 95 RED: collection failed because
  `app.modules.fees.fee_reduction_approval_schemas` did not exist;
- row 95 GREEN: `22 passed, 3 warnings`;
- row 96 RED: `7 failed, 3 warnings`, proving the missing list schema/route and the
  resulting 405 behavior;
- row 96 GREEN: `7 passed, 3 warnings`;
- combined decisive focused rerun: `29 passed, 3 warnings`.

Independent review then identified two valid fail-closed gaps in the list projection.
The correction followed a second test-first increment:

- correction RED: `10 failed, 6 passed, 3 warnings`, proving the missing strict
  snapshot/hash checks, missing evidence projection and malformed non-null current
  identity returning 200;
- first correction GREEN: `15 passed, 1 failed, 3 warnings`; all product probes passed,
  and the only failure was the new test binding itself to SQLAlchemy's anonymous
  parameter number;
- second-correction row-96 GREEN after correcting only that brittle structural assertion:
  `16 passed, 3 warnings`;
- second-correction combined row-95/96 GREEN: `38 passed, 3 warnings`.

A subsequent independent real-SQLite review proved that placing the exact equality in
`WHERE` hid malformed non-null identities before post-validation. A third minimal
test-first correction moved that equality into the selected `is_current` expression and
removed the identity filter:

- third-correction RED: `2 failed, 1 passed, 14 deselected, 3 warnings`; the SQL
  structure still placed equality in `WHERE`, and the real SQLite endpoint returned
  200 instead of 409 for a confirmed corrupt row;
- final row-96 GREEN: `17 passed, 3 warnings`;
- final combined row-95/96 GREEN: `39 passed, 3 warnings`.

The real SQLite regression seeds a confirmed case, evidence version and approval with a
malformed non-null current identity, calls the public endpoint, and proves the stored row
reaches the deterministic 409 post-validation rather than disappearing as an empty list.

The isolated worktree does not contain its own `.venv`, so the first literal command
failed before pytest could start. The effective RED/GREEN commands used the existing
project virtual environment against this worktree.

One bounded shared-API regression command returned `67 passed, 6 failed, 3 warnings`.
All six failures are in the untouched `tests/test_official_fee_preview_api.py` fixture:
case creation rejects legacy input `status="NOT_FILED"` with 422 before the official-fee
preview route is reached. The failing test and current case schema are unchanged from the
base, with blobs `6ce73b9fb93cc6668b6e17f9a28e965c5f4c1671` and
`a4bc31de44de46c716d2cf36ec7398b5f4d2cd9f`. The other official-preview,
fee-estimate-preview and obligation-instruction API regressions in that command passed.
This unrelated inherited mismatch is reported, not absorbed or repaired here.

The known unrelated preview failures were not rerun during correction. Scoped Ruff
check-only and format-check passed after the correction. Run final diff-check and inspect
the exact rebuilt commit range/file list after this story is updated.

The warnings are existing passlib `crypt` and Pydantic field deprecations. Every
serialized lane grant was released immediately after its named test command. No
SQLite-writing test remains active.

An independent High reviewer must review the exact commit and independently rerun the
decisive focused checks under the serialized lane. The implementer does not approve this
`PROTECTED` story; acceptance remains pending independent review.

## Non-goals and rollback

No router rewiring, second endpoint beyond the two catalog rows, model/migration/seed,
source activation, customer-policy inference, fee amount/deadline inference, service-rule
duplication, frontend work, preview change, obligation-detail successor, task/evidence
mutation, ledger/disposition/review edit or release/Foundation claim.

Rollback reverts this one story commit, removing only the two approval API routes, their
strict schemas/tests and this story card.
