# Story V8-FEE-OBLIGATION-READ-DRAFT-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Base: `ea06bcd71a5017ba543f78f272605db56d19ee0b`
- Outcome: adopt the already accepted fee-obligation detail-read and prepare-draft
  contracts onto the current Lean integration tree without changing fee policy, source
  authority, caller-owned transaction semantics, or the current payment-evidence
  successor.
- Change mode: exact archive adoption from
  `6b2ef89da447353380b99853168d4d38aaf9210a`, followed by fresh current-tree
  verification and independent High review.
- Authority: the official-fee, service-receivable, lineage and SQLite rules in
  `docs/product/v8/domain-contract.md`; `docs/product/v8/source-decision-registry.md`;
  frozen catalog rows 110 and 113; and their exact task contracts.

## Catalog IDs

1. `FPMS-V8-FO-OBLIGATION-DETAIL-READ-20260712-01` (ordinal `110`)
2. `FPMS-V8-FO-PREPARE-DRAFT-20260712-01` (ordinal `113`)

## Durable TDD and dependency state

- Row 110 preserves its historical valid RED and terminal independent PASS. The current
  728-line partial test is completed to the accepted 1,184-line archive blob
  `06d1a9c5fc174843bb9cba6677ceedc2505edc57`; RED is not rerun.
- Row 113 preserves its historical RED, GREEN and terminal independent PASS. Its accepted
  test blob is `bdecb76171670bc2939c0a26742a49a118cef6c6`.
- The accepted archive service blob is
  `4d634bd51abe541c27d365598526189899f56bd9`. Compared with the current base, its
  product difference consists only of the missing row 110/113 seams and their imports,
  constants and helpers; the already current row 114 payment-evidence successor remains
  byte-equivalent. Current Ruff mechanically normalizes the adopted service and row 113
  test to blobs `7bc3699b592e3d934649f9b34aafeabd2842efc0` and
  `eb2ee7c97e40d027038e5d7dfaf01633a4f1c1cb`; the row 110 test remains exact and the
  post-format combined regression is rerun.
- Row 107 client instruction, the F3 obligation-draft-link carrier, and lifecycle activity
  append are current and reachable from the base.

## Exact product and test paths

- `backend/app/modules/fees/obligation_service.py`
  - adopt `get_fee_obligation` and its detail validation helpers;
  - adopt `prepare_draft` and its draft validation/replay helpers;
  - retain `record_payment_evidence` and every other serialized successor unchanged.
- `backend/tests/test_v8_fee_obligation_detail_read.py`
- `backend/tests/test_v8_fee_obligation_prepare_draft.py`

## Observable contracts

- Detail read executes zero/one/exactly-four SELECTs for invalid/missing/success paths,
  uses mapping rows under `no_autoflush`, returns persisted separated statuses without
  inference, and fails closed on corrupt, partial, cross-linked or ambiguous lineage.
- Draft preparation creates or reuses exact FeeDraft/FeeItem/link facts only for an
  actionable obligation and explicit policy; it appends or reuses exactly one
  `FEE_DRAFT_CREATED` fee activity with `center_changes={}` in the caller transaction.
- Replays are exact and idempotent. Missing or conflicting persisted authority fails
  closed; the service never activates an official rate, customer instruction or service
  receivable by inference.

## Verification and independent review

- Run the two decisive tests with the inherited detail-read regressions and the existing
  fee-obligation core tranche in the serialized SQLite lane.
- Run scoped Ruff and format-check on the exact service and two tests.
- Run exact story diff-check and inspect the commit range.
- An independent High reviewer must review the exact commit, rerun decisive checks and
  reattest the current `V8-FEE-OBLIGATION-CORE-CURRENT-VERIFICATION` successor.

## Non-goals and rollback

No endpoint/UI/schema/migration, fee or reduction policy, rate/source activation, payment
status inference, customer default, adjacent obligation row, old taskctl/evidence mutation,
ledger edit or milestone claim. Rollback reverts only this story commit.
