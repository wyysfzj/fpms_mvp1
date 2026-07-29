# Story V8-OFFICIAL-RATE-BOOK-CARRIER-CURRENT-VERIFICATION

- Risk: `PROTECTED`
- Outcome: prove on the current lean tree that the already-integrated official-rate-book
  carrier satisfies frozen catalog row `156`, including its exact schema, migration
  identity and fail-closed compatibility link.
- Change mode: current verification plus one test-only successor-compatibility correction;
  no migration, model, schema or product byte changes.
- Catalog ID: `FPMS-V8-OFFICIAL-RATE-BOOK-CARRIER-20260712-01` (ordinal `156`,
  profile `TC-SCHEMA`).
- Authority: the official-fee, source, migration and SQLite rules in
  `docs/product/v8/domain-contract.md`; the source-versus-activation boundary in
  `docs/product/v8/source-decision-registry.md`; frozen catalog row `156`; and its exact
  task contract.

## Archive comparison and dependency

- Archive comparison anchor:
  `6b2ef89da447353380b99853168d4d38aaf9210a`.
- The migration and fee model remain byte-identical to that archive checkpoint:
  - `backend/alembic/versions/v8_w4_official_rate_book.py`:
    `99a1c00d68eafe6aa35695f3cb9c89555e429acc`
  - `backend/app/modules/fees/models.py`:
    `6fc48246c5c6e56490235611da460355e7c11d58`
- The schema test began byte-identical to the archive checkpoint at blob
  `eab370c27b6b90aa554047f3728d91e662aa48db`. Its only current-tree delta is the focused
  compatibility hunk described below; the archive is comparison input, not current-tree
  acceptance.
- Canonical predecessor:
  `FPMS-V8-DECISION-GATE-CARRIER-20260712-01`.
- Current predecessor verification:
  `V8-DECISION-GATE-CARRIER-CURRENT-VERIFICATION` at
  `f0da54ef4e31f2f50330d5b11846479138677fb5`.
- Frozen row `156` migration identity remains
  `v8_w4_official_rate_book_01`, directly after
  `v8_post_w1_customer_decision_gate_01`.

## Exact paths and compatibility correction

- Migration:
  `backend/alembic/versions/v8_w4_official_rate_book.py`
- Model:
  `backend/app/modules/fees/models.py`
- Test:
  `backend/tests/test_v8_official_rate_book_schema.py`

The archive-era schema test asserted that row `156` was still the repository head. The
current migration graph has one legitimate linear successor chain:

`v8_w4_official_rate_book_01` →
`v8_w5_pay_list_export_artifact_01` →
`v8_d4_annuity_lineage_01` →
`v8_d4_legacy_fee_provenance_01` →
`v8_d4_evidence_kind_capacity_01`.

The minimum test-only correction names the exact current head, keeps the unique-head
assertion, and proves row `156` is reachable from that head. It does not alter the frozen
revision, down-revision, forward-only downgrade, table, constraint, index, legacy
preservation or SQLite schema assertions.

## Verification

- Focused RED from the archive-identical test:
  `7 passed, 1 failed, 1 warning`; the sole failure expected row `156` itself as head but
  observed the legitimate current head `v8_d4_evidence_kind_capacity_01`.
- GREEN, run serialized from this worktree's `backend` directory:
  `/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/.venv/bin/pytest -q tests/test_v8_official_rate_book_schema.py`
  with `8 passed, 1 warning`.
- Unique-head check:
  `PYTHONPATH=. /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/.venv/bin/alembic heads`
  with exact output `v8_d4_evidence_kind_capacity_01 (head)`.
- Isolated temporary SQLite `alembic upgrade head` and `alembic current` must succeed;
  exact current is `v8_d4_evidence_kind_capacity_01 (head)`.
- Run scoped Ruff check-only on the exact migration, model and schema-test paths.
- Run `git diff --check` and inspect the exact commit range and file list.
- An independent High reviewer must review the exact commit and independently rerun the
  decisive checks; the implementer does not approve this `PROTECTED` story.

## Non-goals and rollback

No source activation, source row, seed, official rate, amount, reduction rule, effective
legal date, category correction, provider behavior, backfill, endpoint, API, UI, adjacent
model edit, second carrier, coverage-ledger/disposition/review mutation, old
taskctl/evidence mutation or Foundation claim. Rollback reverts only this story and its
focused schema-test compatibility hunk; the already-integrated migration and model bytes
remain unchanged.
