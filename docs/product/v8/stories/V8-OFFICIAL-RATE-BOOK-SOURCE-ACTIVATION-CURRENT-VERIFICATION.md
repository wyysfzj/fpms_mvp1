# Story V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-CURRENT-VERIFICATION

- Risk: `PROTECTED`
- Outcome: prove on the current lean tree that the frozen official-rate-book activation
  seam preserves exact CNIPA source authority, immutable approval/activation provenance,
  replay, predecessor CAS, closed-interval, race and caller-transaction boundaries.
- Change mode: current verification only; no product, seed or test byte changes unless the
  focused current-tree tranche exposes an exact row-157 defect.
- Authority: the official-fee and provenance rules in `docs/product/v8/domain-contract.md`,
  the source-precedence and activation boundaries in
  `docs/product/v8/source-decision-registry.md`, frozen catalog row 157 and its exact task
  contract.
- Archive comparison anchor: `6b2ef89da447353380b99853168d4d38aaf9210a`.

## Catalog ID and dependency

- `FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01` (ordinal 157).
- Its carrier prerequisite
  `FPMS-V8-OFFICIAL-RATE-BOOK-CARRIER-20260712-01` (ordinal 156) is current-verified by
  `V8-OFFICIAL-RATE-BOOK-CARRIER-CURRENT-VERIFICATION` at
  `c8c56a5a993760064b88d4b3da1986d52f9bec13`.

## Exact paths and archive boundary

- `backend/app/modules/fees/official_rate_book.py`
  - `OfficialRateBookActivationDisposition`
  - `ActivateOfficialRateBookCommand`
  - `ActivateOfficialRateBookResult`
  - the source-validation, actor/state/replay, current-row CAS, interval and race helpers
  - `activate_official_rate_book`
- `backend/scripts/seed_dev.py`
- `backend/tests/test_v8_official_rate_book_activation.py`

The activation DTO block and activation core are byte-identical to the corresponding
archive blocks. The shared service has a different later serialized service set, including
the retained read-only estimate provider, so file-wide archive adoption is prohibited.

The seed and decisive-test blobs are archive-identical:

- seed SHA-256:
  `b9867318c9e24742a56bd3607ef7048f07153672446876e8d85b6c4de48ae928`
- decisive-test SHA-256:
  `3fe0b2276a1ac032e6cd46b8f17218197a92083130fc010d6b421fb81afc9afb`

Historical PASS and the archive remain comparison evidence only; fresh current-tree
verification is required.

## Frozen authority and activation contract

- Consume only one already-persisted candidate; never create or import a source.
- Trust only exact canonical CNIPA provenance: `CNIPA_RATE_SOURCE_V1`, exact two-level
  content/snapshot SHA-256 hashes, exact canonical JSON keys, valid source dates/timestamps
  and canonical HTTPS URLs hosted by `www.cnipa.gov.cn`.
- Customer files, Tianyue and other commercial or malformed sources fail closed. The
  service performs no network fetch and does not infer or activate rates or amounts.
- Both named actors must exist and be active. A pending candidate records the exact
  approval tuple; a valid pre-approved candidate preserves it. Same-actor approval and
  activation is allowed because no unapproved four-eyes rule is invented.
- Exact active replay with the immutable approval/activation tuple returns `REUSED` before
  current-row CAS. A differing tuple fails with the activation-payload conflict.
- The expected-current identity is an exact predecessor CAS. Inclusive intervals are
  compared against all active and retired history; same-day touching overlaps and an
  open-ended predecessor blocks a successor.
- Retire only the matched predecessor and activate the candidate in one nested
  transaction/savepoint. Preserve predecessor source, approval and first-activation
  facts. Never commit, caller-wide rollback or close the caller transaction.
- On unique-current `IntegrityError`, roll back only the savepoint and re-read. Reuse only
  when the exact candidate won with the identical immutable tuple; otherwise raise the
  current-identity conflict without partial retirement.

## Seed boundary

`seed_official_fee_rate_catalog()` remains idempotent and may seed customer-derived
`FeeRate` development rows only. It must not create, approve or activate an
`OfficialRateBook`, populate `FeeRate.official_rate_book_id`, convert customer source
status, enable a rate or change an amount/category.

The reviewed CNIPA source record in the registry supplies source metadata only. It does
not itself create a candidate, activate a runtime rate book, infer an effective interval
or authorize any fee amount.

## Exact decisive verification

Primary:

- `backend/tests/test_v8_official_rate_book_activation.py`

Contract-required read-only regressions:

- `backend/tests/test_v8_official_rate_book_schema.py`
- `backend/tests/test_official_fee_rate_catalog_seed.py`

After the controller grants the serialized SQLite lane, run once from this worktree's
`backend` directory:

`/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/.venv/bin/pytest -q tests/test_v8_official_rate_book_activation.py tests/test_v8_official_rate_book_schema.py tests/test_official_fee_rate_catalog_seed.py`

Run scoped Ruff check-only on the exact product, seed and primary-test paths, then exact
story-only diff-check. An independent High reviewer must review the exact commit/range and
independently rerun the decisive tranche; the implementer does not approve this
`PROTECTED` story.

## Non-goals and rollback

No candidate creation/import, unreviewed source activation, rate or amount inference,
source-metadata change, provider change, API/UI, schema/migration, adjacent service,
customer-source enablement/linkage, ledger/disposition/review edit, old evidence mutation
or Foundation claim. Rollback removes only this story-card commit; current product, seed
and test bytes remain unchanged.
