# Story V8-CASE-BATCH-FILING-EVENT-ADAPTER-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Integration parent: `bfcd7fa`
- Outcome: batch filing finalizes exact submission evidence and records the external-
  submission lifecycle event instead of directly assigning `WAITING_RECEIPT`.
- Catalog ID: `FPMS-V8-CASE-BATCH-FILING-EVENT-ADAPTER-20260712-01`
  (ordinal `60`, profile `TC-ADAPTER`).
- Authority: frozen catalog row `60`, its Delta-4 latest-wins task appendix, accepted D4-02
  case-create evidence and D4-05 filing evidence resolver, and
  `docs/product/v8/domain-contract.md`.

## Dependency and exact paths

- `backend/app/modules/cases/service.py`
- `backend/tests/test_v8_batch_filing_lifecycle_adapter.py`

All frozen prerequisites are accepted. This lane shares no product/test path with the
fee-reduction notice story; SQLite and any Playwright verification remain serialized.

## Observable contract

Selected cases remain in stable de-duplicated request order. Each resolves exact final
filing evidence, finalizes the document activity, re-resolves the persisted identity and
applies one `FILING_EXTERNAL_SUBMISSION_RECORDED` lifecycle event with the frozen evidence
pair, canonical activity snapshot/hash, actor, times and keys. Exact replay is idempotent.
Any invalid case or document/lifecycle contradiction rolls back the entire batch; no direct
status write or partial commit remains.

## TDD and verification

The focused RED failed `6/6` on direct status, missing document/lifecycle evidence and
partial transaction behavior. The minimum current-service adapter produced focused GREEN
`6/6`; scoped Ruff/diff checks passed. Independent High review approved the exact candidate
with P0/P1/P2 all zero and successor-attested the shared case status and fee-reduction
verticals.

## Non-goals and rollback

No second case entrypoint, resolver/finalizer/lifecycle-rule/evidence-role change, schema,
API shape, UI, old task/evidence mutation or adjacent cleanup. Rollback reverts only
product commit `3b0c4e2` and this story mapping.
