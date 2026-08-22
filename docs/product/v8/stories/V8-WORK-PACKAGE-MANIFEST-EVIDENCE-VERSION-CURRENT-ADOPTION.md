# Story V8-WORK-PACKAGE-MANIFEST-EVIDENCE-VERSION-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Integration parent: `9b46c5c`
- Outcome: persist and return the exact evidence-version identity for an evidence-backed
  work-package manifest while retaining legacy attachment-only compatibility.
- Catalog ID: `FPMS-V8-WORK-PACKAGE-MANIFEST-EVIDENCE-VERSION-20260712-01`
  (ordinal `62`, profile `TC-ADAPTER`).
- Authority: frozen catalog row `62`, its “writes/reads evidence-version identity” closure,
  the current-verified evidence-link carrier and attachment adapters, and the document
  lineage rules in `docs/product/v8/domain-contract.md`.

## Dependency and exact paths

- `backend/app/modules/official_workflows/schemas.py`
- `backend/app/modules/official_workflows/service.py`
- `backend/tests/test_v8_work_package_manifest_evidence_version.py`

The output-schema path is the minimum current-tree correction required to make the frozen
read half observable; it adds no new authority or adjacent API semantics.

## Observable contract

For a manifest attachment with exactly one evidence version, refresh persists its
`evidence_version_id` and returns the same identity in `filing_file_roles`. A legacy
attachment with no evidence version retains its attachment/content-hash behavior and
returns a null identity. More than one version for the attachment fails closed with the
existing manifest evidence conflict and no ambiguous selection.

## TDD and verification

The archive-exact focused RED proved the missing persisted identity. The independent
review of the first GREEN found that the output schema omitted the read projection. The
minimum correction added the exact nullable output field and assertions. The focused
serialized test passed `1/1`; scoped Ruff/diff checks passed. Independent High re-review
approved the exact corrected candidate with P0/P1/P2 all zero and re-attested the row-70
lifecycle and row-71 reply-date successor behavior.

## Non-goals and rollback

No evidence creation, version selection policy, lifecycle behavior, receipt/reply-date
behavior, endpoint shape beyond this nullable field, migration, UI, task-file mutation,
old evidence machinery or adjacent refactor. Rollback reverts only product commit
`749eb1d` and this story mapping.
