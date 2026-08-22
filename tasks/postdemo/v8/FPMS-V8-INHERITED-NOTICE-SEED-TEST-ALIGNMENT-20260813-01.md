# FPMS V8 Inherited Notice Seed Test Alignment

Status: `READY`
Risk: `PROTECTED`
Runbook: `P0-single-lane-story`

## Observable outcome

Align the inherited OA/acceptance seed-dev snapshot with the two already reviewed later notice
activations: application-fee row `OFFICIAL_NOTICE_034` and fee-reduction-approval row
`OFFICIAL_NOTICE_031`.

## Exact closure

- Keep the original OA/acceptance seeder's exact target set unchanged.
- Extend only the seed-dev expected activation mapping with the exact reviewed metadata for rows
  031 and 034.
- Preserve all 60-row, idempotency, reference-only, deadline, completion, archive, status-effect,
  fee-draft and reply assertions.

## Non-closure

- No seed implementation, product, schema, migration, API, fee or lifecycle change.
- No activation of any additional catalog row and no arbitrary executable-code acceptance.
- No skip/xfail or assertion deletion.
- No changes to grant behavior, filing, OA receipt projection or Row281 files.
- No Row281 adoption, Row282, Row283 or release close.

## Exact allowlist

- `tasks/postdemo/v8/FPMS-V8-INHERITED-NOTICE-SEED-TEST-ALIGNMENT-20260813-01.md`
- `backend/tests/test_addgap_notice_oa_acceptance_activation.py`

## Verification and acceptance

The recorded Row281 RED is one exact seed-dev snapshot failure because reviewed rows 031 and 034
are executable but absent from the inherited expected mapping. Final verification runs this test
with `test_v8_application_fee_notice_activation.py` and
`test_v8_fee_reduction_approval_notice_activation.py`, scoped Ruff, exact diff and independent
High review with P0/P1/P2 `0/0/0`.

Rollback reverts only this task card and inherited expected mapping; it never changes product or
business data.
