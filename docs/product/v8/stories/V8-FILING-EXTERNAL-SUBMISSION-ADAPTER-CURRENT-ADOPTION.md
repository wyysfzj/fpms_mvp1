# Story V8-FILING-EXTERNAL-SUBMISSION-ADAPTER-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Integration parent: `1cb8be0`
- Outcome: the existing filing external-operation endpoint records exact final submission
  evidence and the accepted filing lifecycle event in one transaction.
- Catalog ID: `FPMS-V8-FILING-EXTERNAL-SUBMISSION-ADAPTER-20260712-01`
  (ordinal `65`, profile `TC-ADAPTER`).
- Authority: frozen catalog row `65`, its Delta-4 latest-wins appendix, current-verified
  D4-05 resolver/finalizer/lifecycle seams, and `docs/product/v8/domain-contract.md`.

## Dependency and exact paths

- `backend/app/modules/official_workflows/service.py`
- `backend/app/modules/official_workflows/api.py`
- `backend/tests/test_v8_filing_external_submission_adapter.py`
- `docs/product/v8/stories/V8-FILING-EXTERNAL-SUBMISSION-ADAPTER-CURRENT-ADOPTION.md`

All catalog prerequisites are current-verified. The shared official-workflow files and
SQLite verification remain serialized.

## Observable contract

Only normalized `EXTERNAL_SUBMISSION_RECORDED` enters this path. The API supplies the
authenticated server-owned actor. The service resolves the exact filing evidence,
finalizes it once with the frozen submission time and key, re-resolves the immutable
activity snapshot/hash, then applies one `FILING_EXTERNAL_SUBMISSION_RECORDED` event with
the exact final-version and manual-submission evidence pair. Exact replay reuses both
activities; conflicting actor, time, identity, payload, hash, key or partial state fails
closed. The checklist, document finalization and lifecycle projection commit once only
after the whole chain succeeds. No direct case-status write or duplicate evidence-role
validation is introduced.

Every other checklist operation retains its existing path and semantics.

## TDD and verification

The focused RED failed `3/3` because the service lacked the D4-05 seam and server actor.
The minimum adapter produced focused GREEN `4/4`, including exact replay and document-only
partial-state rejection. The exact affected regression set passes `172/172`; scoped Ruff
and exact-path diff checks are required again immediately before handoff. Independent High
review of the eventual exact commit remains required.

## Non-goals and rollback

No resolver, finalizer, lifecycle rule, role allowlist, receipt/batch adapter, schema,
router shape, migration, seed, UI, old task/evidence, ledger or adjacent checklist change.
Rollback reverts only the four paths listed above.
