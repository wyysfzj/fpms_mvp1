# Story V8-ANNUITY-DRAFT-OBLIGATION-ADAPTER-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Integration parent: `e868617`
- Catalog row: `122`,
  `FPMS-V8-ANNUITY-DRAFT-OBLIGATION-ADAPTER-20260712-01`.
- Outcome: current-adopt existing annuity draft generation so each selected yearly task
  delegates to `prepare_draft` for its exact obligation and preserves the returned draft,
  link and activity identities without a second draft activity.
- Authority: the frozen row-122 task contract, current-verified Task121 annuity instruction
  adapter through `1f7f6a1`, and the current deep `prepare_draft` contract.

## Exact behavior and paths

For each selected current or next-year target, the adapter requires the complete Task121
six-field carrier and validates its same-case obligation, recognition, document, evidence,
year, due-date and fee-line lineage before delegation. It uses the stable
`annuity-draft:{task_id}:{obligation_id}` key and accepts only a deep result whose obligation,
key, draft scope, currency and persisted returned links match the selected task. Missing or
contradictory selection and lineage facts fail closed before the deep write.

The success row projects the exact deep obligation, draft, link, activity and idempotency
identities. Exact replay therefore returns the original draft/link/activity with their
deep reuse flags. The adapter does not append an activity, synthesize a second FeeItem,
change the legacy `draft_generated` flag, commit or roll back the caller's transaction.

Story-owned paths:

- `backend/app/modules/annuity/service.py`
- `backend/tests/test_v8_annuity_draft_obligation_adapter.py`
- this story card.

## Test provenance and local verification

No historical focused row-122 test exists at checkpoint `6b2ef89`. The five-test current
acceptance matrix is derived from the frozen exact closure and reuses the accepted Task121
fixture only as its current prerequisite. It covers one exact selected-obligation
delegation and identity projection, one-activity exact replay, caller rollback, missing
selection and contradictory fee-line lineage.

Under the controller-serialized SQLite lane, the focused RED produced `5 failed`: the
entrypoint did not import or call `prepare_draft`, replay was rejected, direct commit
survived caller rollback, and missing/mismatched carrier facts still created legacy
drafts. The minimum adapter then produced `5 passed` with one inherited passlib `crypt`
deprecation warning. The combined Task121 and deep prepare-draft affected regression
tranche produced `68 passed` with the same warning. Scoped Ruff and exact diff checks
passed. Independent High review and integration acceptance remain controller-owned.

## Non-goals and rollback

No deep fee-obligation rule, second entrypoint, API/UI contract, schema/migration/seed,
ledger/review/evidence machinery, source/rate/reduction/amount policy, PayList, payment,
service receivable, unrelated annuity flow or adjacent refactor is included. Rollback
removes only this adapter slice, its focused test and this story card.
