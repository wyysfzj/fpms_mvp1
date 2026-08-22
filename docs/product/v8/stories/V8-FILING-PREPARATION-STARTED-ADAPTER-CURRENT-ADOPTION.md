# Story V8-FILING-PREPARATION-STARTED-ADAPTER-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Integration parent: `4f550a2`
- Outcome: resolving or creating a filing-preparation package records the exact
  `FILING_PREPARATION_STARTED` lifecycle event once with immutable package evidence.
- Catalog ID: `FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01`
  (ordinal `59`, profile `TC-ADAPTER`).
- Authority: frozen catalog row `59`, its Delta-4 latest-wins task appendix, accepted
  D4-05 filing-submission evidence resolver, the filing-preparation lifecycle rule, and
  `docs/product/v8/domain-contract.md`.

## Dependency and exact paths

- `backend/app/modules/official_workflows/service.py`
- `backend/app/modules/official_workflows/api.py`
- `backend/tests/test_v8_filing_preparation_started_adapter.py`

The catalog and Delta-4 prerequisites are accepted. Official-workflow shared-file work is
serialized after the current row-62/70/71 stories. SQLite verification is serialized.

## Observable contract

The existing API propagates exact `current_user.id`. A fresh package binds that actor as
creator/updater and records one exact package snapshot, canonical hash, timestamps and
idempotency key in the caller-owned transaction. An existing package must retain a stable
nonblank historical creator. Exact replay reuses persisted evidence bytes and event;
changed provenance fails `409`. No internal commit or rollback is added.

## TDD and verification

The focused RED failed `10/10`. Initial GREEN passed `10/10`; independent review then found
that coherent drift of all three persisted event/evidence timestamps was not anchored to
immutable package creation time. A dedicated RED reproduced `200` instead of `409`; the
minimum guard made final focused GREEN pass `11/11`. Scoped Ruff/diff checks passed.
Independent High re-review approved P0/P1/P2 all zero and successor-attested the row-62,
row-70 and row-71 shared-service behavior.

## Non-goals and rollback

No D4-05 change, final-submission/external-submission/receipt behavior, lifecycle-rule
change, endpoint shape, schema, migration, UI, old task/evidence mutation or adjacent
refactor. Rollback reverts only product commit `3e5e1d5` and this story mapping.
