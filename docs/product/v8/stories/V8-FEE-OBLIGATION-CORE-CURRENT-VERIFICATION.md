# Story V8-FEE-OBLIGATION-CORE-CURRENT-VERIFICATION

- Risk: `PROTECTED`
- Outcome: prove on the current lean tree that the coherent fee-obligation service core
  satisfies the frozen recognition, read-only estimate and payment-evidence contracts.
- Change mode: current verification only; no fee product or test byte changes unless the
  focused current-tree tranche exposes an exact defect in catalog row 103, 104 or 114.
- Authority: the official-fee, service-receivable, source-provenance and SQLite rules in
  `docs/product/v8/domain-contract.md`; the no-default/no-source-activation rules in
  `docs/product/v8/source-decision-registry.md`; frozen catalog rows 103, 104 and 114; and
  their exact task contracts.
- Archive comparison anchor: `6b2ef89da447353380b99853168d4d38aaf9210a`.
  The shared service has a different serialized successor set on the lean tree, so
  file-wide archive adoption is prohibited; comparison is limited to the three owned
  public seams and their frozen tests.

## Catalog IDs

1. `FPMS-V8-FO-RECOGNIZE-OBLIGATION-20260712-01` (ordinal `103`)
2. `FPMS-V8-FO-PREVIEW-ESTIMATE-20260712-01` (ordinal `104`)
3. `FPMS-V8-FO-PAYMENT-EVIDENCE-20260712-01` (ordinal `114`)

## Dependencies

- Lifecycle activity append is current-verified by
  `V8-CANARY-LIFECYCLE-CORE-EVIDENCE-KIND-ADOPTION` at
  `7bb54cef0d4f8d7c10c177be54b1adddc01e1d06`.
- Fee-obligation contracts and the pure fee-reduction validator are current-verified by
  `V8-FEE-FOUNDATION-CONTRACTS-CURRENT-VERIFICATION` at
  `c2c45134fdf38602617fedf0f56ecadba0f3f8c6`.
- The F4 obligation-payment-evidence carrier is current-verified by
  `V8-CANARY-SCHEMA-SPINE-CURRENT-VERIFICATION` at
  `38e3e6bc61f20c4c18872dbabe8a19150e56f0ce`.

## Exact product path and owned seams

- `backend/app/modules/fees/obligation_service.py`
  - `recognize_obligation`: whole-command atomic recognition/replay/supersession with
    caller-owned transactions and no estimate or official-rate lookup.
  - `preview_estimate`: pure provider-backed read-only candidates using an explicit
    effective date and the frozen fee-reduction validator.
  - `record_payment_evidence`: same-case payment-evidence linkage that keeps payment and
    official-evidence states distinct.

The shared file may retain later serialized fee services. This story neither adopts the
archive wholesale nor removes, rewrites or claims any adjacent fee row.

## Exact decisive tests

Primary:

- `backend/tests/test_v8_fee_obligation_recognize.py`
- `backend/tests/test_v8_fee_estimate_read_only.py`
- `backend/tests/test_v8_fee_obligation_payment_evidence.py`

Only the narrow inherited regressions explicitly required by row 103:

- `backend/tests/test_v8_fee_obligation_contracts.py`
- `backend/tests/test_v8_w1_f1_fee_obligation.py`
- `backend/tests/test_v8_w1_f2_fee_obligation_line.py`
- `backend/tests/test_v8_lifecycle_activity_append.py`

Run the seven files once as one serialized decisive tranche after controller grant, from
this worktree's `backend` directory, using the original backend virtual environment.
Before grant, only scoped Ruff, blob comparison and diff inspection are allowed.

## Verification and review

- Run scoped Ruff check-only on the exact service and seven test paths.
- After the controller grants the SQLite lane, run:
  `/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/.venv/bin/pytest -q tests/test_v8_fee_obligation_recognize.py tests/test_v8_fee_estimate_read_only.py tests/test_v8_fee_obligation_payment_evidence.py tests/test_v8_fee_obligation_contracts.py tests/test_v8_w1_f1_fee_obligation.py tests/test_v8_w1_f2_fee_obligation_line.py tests/test_v8_lifecycle_activity_append.py`
- Run exact story-only diff-check and inspect the commit range.
- An independent High reviewer must review the exact commit and rerun the decisive checks;
  the implementer does not approve this `PROTECTED` story.

## Non-goals and rollback

No official-rate-book or source activation, customer decision, official amount or
deadline inference, fee-reduction policy change, HTTP/UI, schema/migration, adjacent fee
row, broad regression, ledger/disposition/review edit, old evidence mutation or Foundation
claim. Rollback reverts only this story-card commit; current product and test bytes remain
unchanged.
