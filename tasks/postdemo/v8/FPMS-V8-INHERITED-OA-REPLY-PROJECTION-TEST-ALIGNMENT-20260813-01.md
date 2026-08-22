# FPMS V8 Inherited OA Reply Projection Test Alignment

Status: `READY`
Risk: `PROTECTED`
Runbook: `P0-single-lane-story`

## Observable outcome

Align three inherited OA reply-chain tests with the current reviewed receipt-owned projection:
preparing or creating OA_OUT keeps the source OA document `reply_date` unset and leaves its task
and case open. Only archival of one valid same-case owned official receipt may project the date.

## Authority

- `docs/product/v8/domain-contract.md`
- `docs/product/v8/stories/V8-OA-REPLY-DATE-RECEIPT-PROJECTION-CURRENT-ADOPTION.md`
- `backend/tests/test_v8_oa_reply_date_receipt_projection.py`

## Exact closure

- Replace only the inherited expectations that OA_OUT preparation writes `reply_date` or advances
  the case status.
- Assert that OA_OUT leaves `reply_date` null, keeps the source OA task open and leaves the case at
  its pre-receipt status.
- Keep ordinary non-OA reply auto-writeoff behavior unchanged.
- Keep receipt-owned positive projection coverage in the authoritative V8 successor unchanged.

## Non-closure

- No product, schema, migration, seed, API, document, lifecycle or receipt-selection change.
- No date fallback, direct status write, test skip/xfail or deletion of ordinary reply coverage.
- No changes to unrelated case-create, filing, seed overlay or Row281 files.
- No Row281 ledger adoption, Row282, Row283 or release close.

## Exact allowlist

- `tasks/postdemo/v8/FPMS-V8-INHERITED-OA-REPLY-PROJECTION-TEST-ALIGNMENT-20260813-01.md`
- `backend/tests/test_addgap_oa_out_keeps_task_open.py`
- `backend/tests/test_b2_reply_chain.py`
- `backend/tests/test_spec_alignment_e2e.py`

## Verification and acceptance

The recorded Row281 RED is six inherited nodes that still expect OA_OUT-created reply dates or a
direct OA status advance. Final verification runs the exact three files together with
`test_v8_oa_reply_date_receipt_projection.py`, scoped Ruff, exact diff and independent High review
with P0/P1/P2 `0/0/0`.

Rollback reverts only this task card and the obsolete expectations; it never changes product or
business data.
