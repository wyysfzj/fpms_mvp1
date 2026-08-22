# Story V8-LEGACY-DOCUMENT-EVIDENCE-IMPORT-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Integration parent: `9b46c5c`
- Outcome: create unverified document-evidence versions only for unambiguous legacy
  attachments, leaving role/current conflicts unresolved.
- Catalog ID: `FPMS-V8-LEGACY-DOCUMENT-EVIDENCE-IMPORT-20260712-01`
  (ordinal `254`, profile `TC-MIGRATION`).
- Authority: frozen catalog row `254`, its exact task contract, the current-verified
  document-evidence core and attachment projection, and the lineage rules in
  `docs/product/v8/domain-contract.md`.

## Dependency and exact paths

- `backend/scripts/backfill_v8_document_evidence.py`
- `backend/tests/test_v8_legacy_document_evidence_import.py`

All catalog dependencies are current-verified. This lane shares no product/test path with
the active work-package manifest story; SQLite verification remains serialized.

## Observable contract

The importer creates an unverified evidence version only when the legacy attachment,
case/source identity and role/current facts are unambiguous. Existing or conflicting role
or current-version facts fail closed or remain unresolved exactly as the frozen task
defines. Writes remain caller-owned and deterministic.

## TDD and verification

The focused RED failed `5/5` because the public importer seam was absent. The archive
candidate supplied the minimum two-path implementation; focused GREEN passed `5/5`, and
scoped Ruff/diff checks passed. Independent High review approved the exact candidate with
P0/P1/P2 all zero without repeating the serialized SQLite test.

## Non-goals and rollback

No endpoint, UI, schema, migration, adjacent document rule, second dataset, customer
migration, old task/evidence mutation or unrelated cleanup. Rollback reverts only product
commit `207b10b` and this story mapping.
