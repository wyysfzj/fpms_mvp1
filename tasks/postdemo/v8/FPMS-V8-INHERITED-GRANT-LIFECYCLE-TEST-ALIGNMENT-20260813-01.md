# FPMS V8 Inherited Grant Lifecycle Test Alignment

Status: `READY`
Risk: `PROTECTED`
Runbook: `P0-prereq-heavy-story`

## Observable outcome

Align three inherited grant tests with the current reviewed grant contracts: seed-dev contains all
currently activated notice rows; grant notice creation/attachment and grant-fee DONE append their
own evidence activities but never directly establish legal grant status; DONE has a durable actor.

## Authority

- `docs/product/v8/domain-contract.md`
- `backend/tests/test_v8_grant_notice_lifecycle_adapter.py`
- `backend/tests/test_v8_grant_attachment_no_legal_effect.py`
- `backend/tests/test_v8_grant_fee_done_no_legal_effect.py`
- Current reviewed application-fee and fee-reduction notice activation tests.

## Exact closure

- Update only the seed-dev executable-code expectation to include the already reviewed current
  application-fee (`OFFICIAL_NOTICE_034`) and fee-reduction (`OFFICIAL_NOTICE_031`) activations.
- Preserve the grant-target seeder's exact single-row addition contract.
- Replace inherited expectations that grant notice creation/attachment directly writes
  `GRANT_PENDING`/`GRANTED` with the current lifecycle-neutral status contract.
- Give inherited grant-fee task fixtures one explicit stable audit actor.
- Replace inherited expectations that DONE directly grants a case with the current FEE activity
  and lifecycle-neutral case projection.

## Non-closure

- No product, schema, migration, seed implementation, API, fee or lifecycle-rule change.
- No inference of legal grant status from attachment, task completion or payment.
- No test skip/xfail, assertion deletion or change to ordinary state-machine permissions/errors.
- No OA receipt, filing, case-create input or Row281 file change.
- No Row281 adoption, Row282, Row283 or release close.

## Exact allowlist

- `tasks/postdemo/v8/FPMS-V8-INHERITED-GRANT-LIFECYCLE-TEST-ALIGNMENT-20260813-01.md`
- `backend/tests/test_addgap_notice_grant_activation.py`
- `backend/tests/test_grant_fee_notice_task_creation.py`
- `backend/tests/test_grant_fee_state_machine_api.py`

## Verification and acceptance

The post-case-input Row281 diagnostic is nine failures: two current notice/status expectations,
four grant-notice direct lifecycle expectations and three DONE fixtures without a durable actor.
Final verification runs the exact three inherited files with the three authoritative V8 successor
tests, scoped Ruff, exact diff and independent High review with P0/P1/P2 `0/0/0`.

Rollback reverts only this task card and inherited test inputs/expectations; it never changes
product behavior or business data.
