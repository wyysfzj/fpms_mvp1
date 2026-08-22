# Story V8-GENERIC-FEE-DRAFT-ACTIVITY-ADAPTER-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Integration parent: `c11ac99`
- Catalog row: `115`,
  `FPMS-V8-GENERIC-FEE-DRAFT-ACTIVITY-ADAPTER-20260712-01`.
- Outcome: the existing generic fee-draft entrypoint accepts an explicit obligation ID
  and delegates the actionable PAY path to the current-verified `prepare_draft` service,
  preserving its link and activity identity without adding a duplicate activity.
- Authority: the frozen row-115 task contract and current-verified row-105
  `FPMS-V8-FO-PREPARE-DRAFT-20260712-01` dependency.

## Exact behavior and paths

When no obligation ID is supplied, legacy unlinked draft creation remains unchanged.
When one is supplied, the adapter requires an exact actor, uses the stable
`generic-fee-draft:{obligation_id}` idempotency key, delegates the write to
`prepare_draft`, and accepts the result only when obligation, key, link, activity, case,
client, draft type and currency all match. Missing PAY authority and every mismatch fail
closed through the underlying or adapter error; the caller owns the transaction.

Story-owned paths:

- `backend/app/modules/fees/service.py`
- `backend/tests/test_v8_generic_fee_draft_activity_adapter.py`
- `docs/product/v8/cutover-dirty-path-disposition.json`
- this story card.

The focused public test is adopted byte-for-byte from the independently accepted archive
checkpoint with SHA-256
`33637994891262d10495ce9ac85424d34457d8d0d4c1a7e0d697af16a551eceb`.
The product change is limited to the two obligation imports, the optional parameter and
one private adapter.

## Verification, non-goals and rollback

Run the focused test as RED and GREEN under the serialized SQLite lane, then the exact
prepare-draft regression and scoped Ruff/diff checks. An independent High reviewer reviews
the exact commit and independently reruns the decisive focused test.

The public test produced the expected RED with `1 failed, 1 passed, 8 skipped`; the
decisive failure was the missing explicit `obligation_id` parameter. After the minimum
adapter port, the focused GREEN passed `10` tests and the combined adapter plus
prepare-draft regression passed `33` tests. Scoped Ruff and diff checks passed. The
disposition transfer leaves `474` unique paths with exact story counts and SHA-256
`bfab6799eba6c0f97f2d919bb8c4d3e97f7e1617fa93e36c4be8edc2d19e5788`.

No obligation-core rule change, second entrypoint, rate lookup or activation, amount or
reduction policy, payment, service receivable, API, UI, schema, migration, seed, unrelated
fee flow or adjacent refactor is included. Rollback removes only the adapter slice, focused
test, exact disposition transfer and this story card.
