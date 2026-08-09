# Story V8-OVERLAY-FEE-JOIN-CURRENT-CONTRACT

- Risk: `PROTECTED`
- Outcome: close catalog row `262` by attaching exact obligation, instruction, draft,
  PayList, payment and official-evidence facts to the fee activities that name them.
- Catalog ID: `FPMS-V8-OVERLAY-FEE-JOIN-20260712-01`.
- Dependency owner: the accepted row-261 document-join successor of the row-260 overlay.

## Activity-rooted association

Only an already-selected `FEE` milestone may root fee facts. Strictly decode its canonical JSON
payload and recognize the accepted activity schemas/types for obligation recognition, client
instruction, draft creation, PayList creation/internal export, payment recording and official
payment-evidence verification. Obtain obligation identity only from that payload's exact
`obligation_id` or `obligation_ids`; for a PayList-only activity, derive identities only through
its persisted `GovPayment -> FeeItem -> FeeObligationDraftItemLink -> FeeObligationLine` graph.

Unknown fee activities remain valid milestones with an empty `fee_obligations` tuple. A known
fee activity with malformed JSON/schema/identity, a named object that is missing or belongs to a
different case, an ambiguous relation, or payload/persistence disagreement fails 409
`LIFECYCLE_OVERLAY_FEE_CONFLICT`. Never associate by amount, fee name/code, date, year, title,
status, client, or case-wide fallback.

## Deep read and projection

Call the accepted `get_fee_obligation()` read seam once per distinct activity-selected
obligation and reuse its fail-closed validation. Require its case and source lineage to agree
with the activity graph. Project every obligation and line field into the accepted overlay DTO;
money is formatted exactly to two decimal places and reduction ratio to four, preserving
nullable official/source amounts and source date. Preserve all seven independent statuses
without inference or collapsing.

For the current milestone, `related_facts` contains only exact persisted objects named by that
activity:

- `DRAFT`: its `FeeDraft.id` and stored status;
- `PAY_LIST`: its decimal-string `PayList.id` and stored status;
- `PAYMENT`: its decimal-string `GovPayment.id` and stored status; or
- `OFFICIAL_EVIDENCE`: the named payment ID and the obligation's exact official-evidence status.

Each object must be linked to one of the projected obligation's exact lines through accepted
link tables. Order obligations by obligation ID, lines by the deep read seam, and related facts
by `(kind, object_id)`. Preserve the center/document facts, generated timestamp, decision gates,
warnings, conflicts and cursor fields unchanged. All reads use the caller session and perform no
add/delete/update, flush, commit or rollback.

## Verification, non-goals and rollback

The focused test proves each recognized activity family, exact monetary strings and independent
statuses, multi-obligation PayList ordering, directly named related facts, unknown-fee empty
behavior, malformed/cross-case/ambiguous linkage fail-closed behavior, no fuzzy association and
read-only execution. Run it with document and center regressions, scoped Ruff/format/diff, then
independent High review of the exact commit/range.

No new fee rule, rate/reduction calculation, draft/list/payment mutation, temporal rewriting,
decision gate, pagination, endpoint/UI, schema or neighboring cleanup. Rollback reverts only the
row-262 service/test change and its adoption; prior overlay owners remain intact.
