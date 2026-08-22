# Story V8-ANNUITY-LATE-FEE-RULE-CURRENT-VERIFICATION

- Risk: `PROTECTED`
- Outcome: prove on the current lean tree that the frozen annuity late-fee rule preserves
  its statutory calendar-month algorithm, official-notice precedence, exact error order
  and fee/provenance boundaries.
- Change mode: current verification only; no product or test byte changes unless the
  focused current-tree verification exposes an exact row-134 defect.
- Authority: the official-fee and provenance rules in `docs/product/v8/domain-contract.md`,
  the source-precedence and activation boundaries in
  `docs/product/v8/source-decision-registry.md`, frozen catalog row 134 and its exact task
  contract.
- Archive comparison anchor: `6b2ef89da447353380b99853168d4d38aaf9210a`.

## Catalog ID

- `FPMS-V8-ANNUITY-LATE-FEE-RULE-20260712-01` (ordinal 134)

## Dependency

- `FPMS-V8-FO-CONTRACTS-20260712-01` is current-verified by
  `V8-FEE-FOUNDATION-CONTRACTS-CURRENT-VERIFICATION` at
  `c2c45134fdf38602617fedf0f56ecadba0f3f8c6`.

## Exact current paths and archive identity

- `backend/app/modules/fees/late_fee.py`
  - current/archive SHA-256:
    `1319f9d83efc37a6b4d5d2d0d2a4b480803dcfcf6ddcaed3edd900ad9409f866`
- `backend/tests/test_v8_annuity_late_fee.py`
  - current/archive SHA-256:
    `611ea4cf0b7826f65779835a4af3e8c176504bc2affbaf0059d5a4d5932a0238`

The two current blobs are byte-identical to the archive anchor. Historical PASS remains
comparison evidence only; this story requires fresh current-tree verification.

## Frozen observable contract

- `calculate_annuity_late_fee(command, /)` is pure and uses the caller-supplied unreduced
  full annual fee and statutory due date.
- Calendar anniversary `M(n)` preserves the original day or clamps to the target month's
  final day. Inclusive statutory rates are exactly `0`, `0.05`, `0.10`, `0.15`, `0.20`
  and `0.25`; `M(6)` remains valid and any later payment fails closed.
- The full annual fee must be finite and positive. Statutory multiplication rounds only
  the final amount to cents with `ROUND_HALF_UP`.
- Valid reviewed-notice bands are sorted, inclusive, non-overlapping and contiguous. A
  matching band returns its stated rounded amount and source document without
  recalculation. Statutory fallback is permitted only in the leading zero-rate period;
  an uncovered non-zero date fails closed.
- Error precedence is exactly: invalid full annual fee, payment before due date, payment
  after the late window, invalid notice band, notice overlap, then notice gap.

The source registry's reviewed 32-page CNIPA annuity record is source metadata only. This
story neither activates a rate nor changes an amount. The superseded 31-page guide named
in historical task references remains read-only comparison history.

## Verification and review

- Run scoped Ruff check-only on the exact product and test paths.
- After controller grant of the serialized SQLite lane, run only:
  `/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/.venv/bin/pytest -q tests/test_v8_annuity_late_fee.py`
- Run exact story-only diff-check and inspect the commit range.
- An independent High reviewer must review the exact commit/range and independently rerun
  the decisive check; the implementer does not approve this `PROTECTED` story.

## Non-goals and rollback

No due-date derivation, obligation creation, rate lookup or source activation, annual-fee
amount change, reduction/payable-amount input, notice parsing or review, payment
sufficiency, restoration calculation, deadline inference, persistence, HTTP/UI,
schema/migration, adjacent annuity rule, ledger/disposition/review edit, old evidence
mutation or Foundation claim. Rollback removes only this story-card commit; current product
and test bytes remain unchanged.
