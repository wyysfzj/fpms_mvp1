# Story V8-PAYLIST-EXPORT-CARRIER-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Outcome: prove on the current lean tree that the already-integrated PayList
  export-artifact carrier satisfies frozen catalog row `159` while preserving every
  legitimate migration successor.
- Change mode: current adoption plus one focused test-only successor-compatibility
  correction; no migration, model or product byte changes.
- Catalog ID: `FPMS-V8-PAYLIST-EXPORT-ARTIFACT-CARRIER-20260712-01` (ordinal `159`,
  profile `TC-SCHEMA`).
- Authority: the official-fee, payment-boundary, schema, migration and SQLite rules in
  `docs/product/v8/domain-contract.md`; frozen catalog row `159`; and its exact task
  contract.
- Archive comparison anchor:
  `6b2ef89da447353380b99853168d4d38aaf9210a`.
- Base: `3766eedd584782d58a0e3056c678694d1f83c9ec`.

## Dependency and frozen carrier

The canonical predecessor
`FPMS-V8-OFFICIAL-RATE-BOOK-CARRIER-20260712-01` is current-verified by
`V8-OFFICIAL-RATE-BOOK-CARRIER-CURRENT-VERIFICATION` at
`c8c56a5a993760064b88d4b3da1986d52f9bec13`, which is an ancestor of this story base.

The row-159 migration remains byte-identical to the archive checkpoint at Git blob
`257c8b6f4e34f40152c51a78d90bbf3df752e859`. Its frozen identity remains:

- revision `v8_w5_pay_list_export_artifact_01`;
- down-revision `v8_w4_official_rate_book_01`;
- no branch labels or dependencies; and
- forward-only downgrade behavior.

The `PayListExportArtifact` ORM class remains byte-identical to the archive class. It
retains only the exact 14 columns, two foreign keys, six checks, PayList-scoped
idempotency unique, generation-time lookup index and application-generated UUID.

The carrier keeps internal workbook generation separate from official-site acceptance
and contains no payment, ticket, uploaded, current/superseded or retry-outcome state. It
does not read or activate `DG-PAYMENT-WORKBOOK`.

## Current migration graph and test correction

The archive-era focused test assumed that row `159` remained the repository head. The
current tree has one legitimate linear successor chain:

`v8_w4_official_rate_book_01` →
`v8_w5_pay_list_export_artifact_01` →
`v8_d4_annuity_lineage_01` →
`v8_d4_legacy_fee_provenance_01` →
`v8_d4_evidence_kind_capacity_01`.

The minimum test-only correction names
`v8_d4_evidence_kind_capacity_01` as the exact unique current head and proves W5 remains
reachable from it. It does not change or reinterpret the W5 revision, down-revision,
table, columns, constraints, indexes, defaults, foreign-key actions, UUID behavior or
forward-only boundary.

## Exact paths

- Migration, verified unchanged:
  `backend/alembic/versions/v8_w5_pay_list_export_artifact.py`
- ORM model, verified unchanged:
  `backend/app/modules/annuity/models.py`
- Focused schema test:
  `backend/tests/test_v8_pay_list_export_artifact_schema.py`
- Story:
  `docs/product/v8/stories/V8-PAYLIST-EXPORT-CARRIER-CURRENT-ADOPTION.md`

## RED, GREEN and migration verification

Under the controller-granted exclusive `GLOBAL_ALEMBIC_HEAD` and SQLite lane:

- untouched focused RED: `3 passed, 1 failed, 1 warning`; the sole failure expected W5
  itself as head but observed the legitimate current head;
- focused GREEN after the test-only correction: `4 passed, 1 warning`;
- `alembic heads`: exact output
  `v8_d4_evidence_kind_capacity_01 (head)`; and
- an isolated clean SQLite `upgrade head` succeeded, followed by `alembic current` with
  exact output `v8_d4_evidence_kind_capacity_01 (head)`.

The warning is the existing third-party passlib `crypt` deprecation. The exclusive lane
was released after these commands.

Run scoped Ruff check-only on the exact migration, model and focused-test paths, run
exact-range diff-check, and inspect the commit file list. An independent High reviewer
must review the exact commit and independently rerun the decisive checks under the
exclusive migration lane. The implementer does not approve this `PROTECTED` story; it
remains pending independent review.

## Non-goals and rollback

No migration or model change, head rewrite, down-revision edit, merge revision, branch,
second carrier/table, backfill, workbook generation, service behavior, acceptance
transition, gate read, payment/ticket state, API/endpoint, seed, UI, source activation,
ledger/disposition/review edit, old task/evidence mutation or Foundation claim.

Rollback reverts only this story card and the focused test compatibility hunk; the
already-integrated migration and model bytes remain unchanged.
