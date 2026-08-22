# Story V8-FILING-RECEIPT-LIFECYCLE-ADAPTER-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Integration parent: `e76a388`
- Outcome: an exact archived filing receipt revalidates its final-submission lineage and
  advances the filing lifecycle atomically with the receipt and attachment flags.
- Catalog ID: `FPMS-V8-FILING-RECEIPT-LIFECYCLE-ADAPTER-20260712-01` (ordinal `66`,
  profile `TC-ADAPTER`).
- Authority: frozen catalog row `66`, its Delta-4 latest-wins appendix, the current
  lifecycle/evidence contracts, and `docs/product/v8/domain-contract.md`.

## Dependency and exact paths

The filing-receipt lifecycle rule, D4-05 final-evidence resolver, filing external submission
adapter and inherited Tasks 14–16 are current baseline.

- `backend/app/modules/official_workflows/service.py`
- `backend/tests/test_v8_filing_receipt_lifecycle_adapter.py`
- `docs/product/v8/stories/V8-FILING-RECEIPT-LIFECYCLE-ADAPTER-CURRENT-ADOPTION.md`

The shared official-workflow service and SQLite verification remain serialized.

## Observable contract

Only an exact `FILING_PREP` receipt with `archive_status=ARCHIVED`, one persisted
same-case attachment, matching persisted bytes/hash and a naive `received_at` enters the
lifecycle path. The service re-resolves the exact reviewed final evidence and its durable
external-submission activity/link, then applies one `FILING_RECEIPT_ARCHIVED` event with
exactly the final-version and receipt evidence pair. The receipt evidence identity is the
receipt ID and its content hash is the validated attachment hash.

Exact replay reuses the receipt and lifecycle event. Changed receipt, actor, time,
attachment flags, evidence identity/hash/link or case projection fails closed. Receipt,
attachment flags, lifecycle activity/evidence and projection share the existing
adapter-owned transaction and commit once only after the complete operation succeeds.

## TDD and verification

The archive test was restored byte-for-byte. Focused RED failed `5/5` on the missing
idempotent receipt lifecycle, rollback and replay validation. The exact archive hunk made
focused GREEN pass `5/5`; the named inherited Tasks 14–16 regression set passes `11/11`.
Scoped Ruff check and format check pass. Exact-path diff validation is required again at
handoff, and an independent High reviewer must review the eventual exact commit/range.

## Non-goals and rollback

No lifecycle rule, resolver, external-submission adapter, OA receipt behavior, API,
schema, model, migration, seed, endpoint, UI, legacy task/evidence, ledger or adjacent
service change. Rollback reverts only the three paths listed above.
