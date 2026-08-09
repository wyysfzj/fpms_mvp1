# Story V8-LEGACY-LIFECYCLE-IMPORT-NONINFERENTIAL-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Integration parent: `61cd23c`
- Outcome: import the existence of each exact known legacy case/status without reverse
  inference, preserving `Case.status` while recording `UNKNOWN/LEGACY_UNVERIFIED` lifecycle
  truth.
- Catalog ID: `FPMS-V8-LEGACY-LIFECYCLE-IMPORT-20260712-01`
  (ordinal `253`, profile `TC-SERVICE`).
- Authority: the frozen non-inferential successor contract, catalog row `253`, the
  current lifecycle append seam and `docs/product/v8/domain-contract.md`.

## Exact paths and behavior

- `backend/scripts/backfill_v8_lifecycle.py`
- `backend/tests/test_v8_legacy_lifecycle_import.py`

Only an exact known legacy status with four null lifecycle projection columns, consistent
revision and no lifecycle history is imported. The importer appends one `LEGACY_IMPORT /
LIFECYCLE / LEGACY_UNVERIFIED` event through `append_case_activity`, leaves business and
official stages null, sets legal status to `UNKNOWN`, and preserves the legacy status
string. No legacy value, including `GRANTED`, becomes a confirmed legal fact.

Dry-run is write-free. Apply requires the exact current plan hash and a caller-owned
transaction. Exact replay is unchanged. Partial projections, history/revision conflicts,
reserved-key or evidence drift, malformed stored imports and unknown carrier values remain
visible as `CONFLICT` or `INVALID` and are not written.

## TDD and verification

The initial RED failed all `27` cases because the public seam was absent. Focused and
affected regression GREEN reached `101 passed`; scoped Ruff, format and diff checks passed.
Independent High review found and drove three exact fail-closed corrections: evidence-link
drift, history/revision classification and nullable activity time. The corrected range was
approved with P0/P1/P2 all zero.

## Non-goals and rollback

No reverse mapping, confirmed status, endpoint, UI, schema, source mutation, historical
rewrite, bulk commit, customer policy or adjacent cleanup is included. Rollback reverts
only product commits `e85f7a3`, `1c00de6`, `c8396aa` and this ledger adoption; already-run
database migration history remains forward-only.
