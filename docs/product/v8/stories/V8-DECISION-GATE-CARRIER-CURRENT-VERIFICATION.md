# Story V8-DECISION-GATE-CARRIER-CURRENT-VERIFICATION

- Risk: `PROTECTED`
- Outcome: prove on the current lean tree that the already-integrated customer-decision
  gate carrier satisfies the exact frozen schema and migration closure.
- Change mode: current verification only; no migration, model, schema, test or product byte
  changes.
- Catalog ID: `FPMS-V8-DECISION-GATE-CARRIER-20260712-01` (ordinal `165`,
  profile `TC-SCHEMA`).
- Authority: the schema, migration, SQLite and fail-closed customer-decision rules in
  `docs/product/v8/domain-contract.md`; the pending gate snapshot and activation rule in
  `docs/product/v8/source-decision-registry.md`; and frozen catalog row `165`.
- Archive comparison anchor: the three exact product/test paths below must remain
  byte-identical to archive checkpoint `6b2ef89da447353380b99853168d4d38aaf9210a`;
  that checkpoint is comparison input, not current-tree acceptance.

## Dependency

- Canonical predecessor:
  `FPMS-V8-W1-F5-FEE-REDUCTION-APPROVAL-CARRIER-20260712-01`.
- Current predecessor verification:
  `V8-CANARY-SCHEMA-SPINE-CURRENT-VERIFICATION` at
  `38e3e6bc61f20c4c18872dbabe8a19150e56f0ce`, mapped by
  `ff840e7bfc1a43fc159551219792199653e8e881`.
- Migration dependency: `v8_w1_f5_fee_reduction_01`; this story retains the frozen
  `GLOBAL_ALEMBIC_HEAD` order immediately after W1-F5.

## Exact paths

- Migration:
  `backend/alembic/versions/v8_post_w1_customer_decision_gate.py`
- Model:
  `backend/app/modules/system/models.py`
- Test:
  `backend/tests/test_v8_customer_decision_gate_schema.py`

## Verification

- Run only the exact SQLite-writing test, serialized from this worktree's `backend`
  directory:
  `/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/.venv/bin/pytest -q tests/test_v8_customer_decision_gate_schema.py`
- Run scoped Ruff check-only on the exact migration, model and test paths.
- Run `git diff --check` and inspect the exact story-only commit range and diff.
- An independent High reviewer must review the exact commit and rerun the decisive checks;
  the implementer does not approve this `PROTECTED` story.

## Non-goals and rollback

No migration/model/test rewrite, backfill, service, endpoint, seed, UI, second
table/carrier, source activation, customer-decision default, coverage-ledger/review
mutation, old taskctl/evidence mutation or Foundation claim. Rollback reverts only this
story-card commit; the already-integrated product/test bytes remain unchanged.
