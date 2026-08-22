# Contract — V8 Dual-read Reconciliation

- Risk: `PROTECTED`
- Catalog ID: `FPMS-V8-DUAL-READ-RECONCILIATION-20260712-01` (ordinal `257`).
- Outcome: produce one deterministic, read-only cutover report across lifecycle,
  document-evidence, fee-reduction and fee-truth legacy/current representations.
- Authority: frozen catalog row `257`, V8 design §11.4, and the four current-verified
  import stories on which row `257` depends.

## Public seam and delegated truth

`backend/scripts/audit_v8_dual_read.py` exposes frozen keyword-only synchronous
`audit_v8_dual_read(transaction, actor_id, lifecycle_recorded_at,
fee_reduction_manifest, fee_truth_rows)` and frozen result DTOs.

The audit delegates only to the four accepted import seams in `dry_run=True` mode. It does
not duplicate their domain rules:

1. lifecycle import supplies case projection/history classifications;
2. document-evidence import supplies attachment/version classifications;
3. fee-reduction import supplies legacy reduction/provenance classifications;
4. fee-truth link supplies draft/payment-to-obligation classifications.

The caller supplies the exact migration actor/time, approved reduction manifest and exact
fee-truth rows used by the corresponding import runs. Missing, malformed or stale input
fails through the owning importer; the audit never guesses it.

## Reconciliation classification

Each child row becomes one ordered report row containing lane, stable identity, source
classification and one disposition:

- `RECONCILED`: exact existing import/link classification (`UNCHANGED` or `unchanged`);
- `CLASSIFIED_CONFLICT`: one of the owning importer's frozen invalid/conflict classes;
- `REQUIRES_IMPORT`: the owning importer still plans a write (`IMPORT`,
  `explicit-zero`, `reused-70`, `reused-85` or `LINKED`).

Any other source classification raises `V8_DUAL_READ_UNCLASSIFIED_RESULT` with HTTP 409.
The report is `accepted=True` only when there are no `REQUIRES_IMPORT` rows. Classified
conflicts stay explicit and accepted for manual resolution; they are never converted to
matched truth. The report exposes exact counts, the four child input/plan/output hashes,
ordered rows and a canonical report SHA-256.

## Safety and verification

The audit validates the SQLAlchemy transaction and public input types, executes under
`no_autoflush`, and performs no add/delete/flush/commit/rollback or direct product write.
Verification covers an all-reconciled report, classified conflicts, pending-import
rejection, deterministic ordering/hash, unclassified-result fail-closed behavior and a
database snapshot proving zero writes.

Scope is exactly:

- `backend/scripts/audit_v8_dual_read.py`;
- `backend/tests/test_v8_dual_read_reconciliation.py`;
- this contract and later adoption/review records.

No import execution, conflict repair, endpoint/UI/schema, customer policy, source edit,
legacy write shutdown, direct-status static gate or adjacent cleanup is included.
