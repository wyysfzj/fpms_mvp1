# Story V8-OA-REPLY-DATE-RECEIPT-PROJECTION-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Integration parent: `7d04e97`
- Outcome: project an OA source document's reply date only from its valid archived receipt,
  never from OA_OUT preparation.
- Catalog ID: `FPMS-V8-OA-REPLY-DATE-RECEIPT-PROJECTION-20260712-01` (ordinal `71`,
  profile `TC-ADAPTER`).
- Authority: frozen catalog row `71`, its exact task contract, current-verified row `70`,
  and the deadline/document-lineage rules in `docs/product/v8/domain-contract.md`.

## Dependency and exact paths

The sole canonical predecessor is
`FPMS-V8-OA-RECEIPT-LIFECYCLE-ADAPTER-20260712-01`, current-verified by
`V8-OA-RECEIPT-LIFECYCLE-ADAPTER-CURRENT-ADOPTION`.

- `backend/app/modules/documents/service.py`
- `backend/app/modules/official_workflows/service.py`
- `backend/tests/test_v8_oa_reply_date_receipt_projection.py`
- `docs/product/v8/cutover-dirty-path-disposition.json`
- `docs/product/v8/stories/V8-OA-REPLY-DATE-RECEIPT-PROJECTION-CURRENT-ADOPTION.md`

## Observable contract

Creating or preparing OA_OUT does not write the OA source document's `reply_date`, and
leaves the source OA task/case open. Archiving the one valid same-case owned receipt
projects `reply_date` from that receipt's canonical captured date within the same
transaction as the accepted row-70 lifecycle/archive effects. Exact replay keeps one
projection, one lifecycle event and one task close.

No current date, OA_OUT preparation time, deadline, task due date, attachment metadata or
fallback source may supply the projection.

## TDD and verification

After correcting only the dedicated fixture's newly required explicit fee-reduction
decision, the focused RED failed exactly because OA_OUT prematurely wrote `2026-03-01`
and receipt archive left the projection null. The minimum two-service change produced
focused GREEN `2/2`.

The task's frozen inherited set reported `10` passes and `24` requests rejected before
row-71 behavior because their legacy fixtures omit the independently required
`fee_reduction` input. Those files remain baseline-subtracted and read-only; receipt
archive regressions in the set pass. Scoped Ruff and exact-path diff check pass.

An independent High reviewer must inspect the exact eventual commit, independently rerun
the focused test under the serialized SQLite lane, and verify row-70 lifecycle, atomicity,
lineage and idempotency remain intact.

## Non-goals and rollback

No deadline calculation, OA lifecycle-rule change, direct legal-status write, receipt
selection change, fee-reduction fixture cleanup, API/schema/UI/migration change, adjacent
document refactor, old task/evidence mutation, ledger/review edit or milestone claim.
Rollback reverts only the five paths listed above.
