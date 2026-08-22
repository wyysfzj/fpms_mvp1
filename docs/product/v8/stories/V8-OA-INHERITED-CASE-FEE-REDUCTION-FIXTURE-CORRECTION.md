# Story V8-OA-INHERITED-CASE-FEE-REDUCTION-FIXTURE-CORRECTION

- Risk: `MECHANICAL`
- Integration parent: `24aadc66215e068874102156768cd8527917ec1c`
- Outcome: make the inherited OA regression fixtures satisfy the current strict case-create
  contract by selecting the neutral explicit fee-reduction ratio, without changing the OA,
  lifecycle, billing or fee-reduction behavior exercised by those tests.
- Authority: `docs/product/v8/domain-contract.md`, the independently accepted
  `V8-CASE-FEE-REDUCTION-VERTICAL-CURRENT-ADOPTION` story, and the row-67 inherited
  regression result.

## Exact paths and dependency

The current case-create successor requires every request to provide an explicit canonical
fee-reduction ratio. The row-67 inherited regression tranche reached that validation
boundary before its intended OA assertions: 24 failures were strict missing-field `422`
responses. These five case-create sites are test setup only.

- `backend/tests/test_addgap_oa_out_keeps_task_open.py`
- `backend/tests/test_b2_reply_chain.py`
- `backend/tests/test_document_ui_deadline_generation.py`
- `backend/tests/test_spec_alignment_e2e.py`
- `docs/product/v8/stories/V8-OA-INHERITED-CASE-FEE-REDUCTION-FIXTURE-CORRECTION.md`

## Observable contract

Each inherited case-create helper or payload supplies exactly `"fee_reduction": "0"`.
Explicit `0` preserves the existing test assumption of no reduction and satisfies the
current fail-closed create contract without inventing approval, applicant-composition or
fee facts. No product code, endpoint semantics, expected status, session setup or asserted
OA behavior changes.

## Verification

Verification is limited to scoped Ruff on the four Python files and exact diff checks.
The SQLite-writing inherited regression tranche remains serialized and runs only after an
explicit controller grant.

## Non-goals and rollback

No row-67 product implementation, B2 direct-status/session rewrite, fee-reduction product
behavior, lifecycle/legal status, deadline, billing/payment, document/evidence lineage,
API/schema/model/migration/seed, UI, ledger, review receipt, release claim or unrelated
fixture cleanup enters this story. Rollback removes the five neutral fixture fields and
this story file only.
