# Story V8-OA-RECEIPT-LIFECYCLE-ADAPTER-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Integration parent: `e12a075`
- Outcome: make successful OA receipt archival append the accepted
  `OA_RECEIPT_ARCHIVED` lifecycle event atomically, with the lifecycle rule owning the
  legal-status projection.
- Catalog ID: `FPMS-V8-OA-RECEIPT-LIFECYCLE-ADAPTER-20260712-01` (ordinal `70`,
  profile `TC-ADAPTER`).
- Authority: frozen catalog row `70`, its exact task contract, the current-verified
  lifecycle contracts and `docs/product/v8/domain-contract.md`.

## Dependency and exact paths

The sole canonical predecessor is
`FPMS-V8-LC-OA-RECEIPT-ARCHIVED-20260712-01`, current-verified by the accepted
lifecycle core.

- `backend/app/modules/official_workflows/service.py`
- `backend/tests/test_v8_oa_receipt_lifecycle_adapter.py`
- `backend/tests/test_addgap_oa_receipt_archive_event.py`
- `docs/product/v8/cutover-dirty-path-disposition.json`
- `docs/product/v8/stories/V8-OA-RECEIPT-LIFECYCLE-ADAPTER-CURRENT-ADOPTION.md`

The third product/test path is a direct compatibility regression for this same endpoint:
only its valid OA1/OA2/replay fixtures establish the already-required confirmed OA
projection. Negative fixtures and expectations are unchanged. No unrelated inherited
fixture enters this story.

## Observable contract

After selecting and archiving the exact receipt evidence, the service deterministically
hashes that archived receipt and applies exactly one accepted `OA_RECEIPT_ARCHIVED` event
with one receipt evidence reference and a stable idempotency key. The lifecycle rule owns
the transition to `SUB_EXAM`; the adapter does not write legal status directly. It then
closes exactly the matched task and records the checklist evidence using the captured
pre-transition status.

Archive, lifecycle activity, case projection, matched task and checklist evidence share
the caller-owned transaction. A lifecycle failure leaves all of them unchanged. Exact
replay remains idempotent. No legacy/null projection bootstrap is added; such data remains
owned by the separately contracted legacy import.

## TDD and verification

The corrected focused RED failed twice on the exact missing behavior: no lifecycle
activity was created, and an injected lifecycle failure was never reached. The minimum
implementation made the focused test pass `2/2`.

The first inherited run exposed three directly affected legacy fixtures plus twenty-two
unrelated requests rejected earlier by the already-required `fee_reduction` input. The
direct fixture compatibility change then exposed a real ordering RED: the checklist read
the already-updated case status. Capturing that status immediately before lifecycle
application produced the final exact result:

`pytest -q tests/test_v8_oa_receipt_lifecycle_adapter.py
tests/test_addgap_oa_receipt_archive_event.py` — `12 passed`.

Scoped Ruff check, test-file format check and exact-path diff check pass. The twenty-two
unrelated inherited `422` fixture failures remain baseline-subtracted and read-only; no
claim is made that their separate closure is complete. An independent High reviewer must
review the exact eventual commit and rerun the decisive two-file test.

## Non-goals and rollback

No lifecycle rule change, direct case-status write, legacy projection bootstrap, receipt
selection change, fee-reduction compatibility, API/schema/UI/migration change, broad
fixture cleanup, old task/evidence mutation, ledger/review edit or milestone claim.
Rollback reverts only the five paths listed above.
