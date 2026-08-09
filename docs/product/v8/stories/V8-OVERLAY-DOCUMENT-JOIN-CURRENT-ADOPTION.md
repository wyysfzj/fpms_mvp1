# Story V8-OVERLAY-DOCUMENT-JOIN-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Contract commit: `dace1c1`.
- Product/test commits: `0ea0d14`, `0cb1cd7`.
- Catalog ID: `FPMS-V8-OVERLAY-DOCUMENT-JOIN-20260712-01` (ordinal `261`).
- Outcome: enrich each overlay milestone only through its exact activity-evidence graph with
  document versions/derivations, work packages/manifests/receipts and document tasks.

Exact IDs are the sole association root. Selected and derived objects must exist and belong to
the same case; enum, identity or relation corruption fails closed. Results preserve deterministic
ordering and reuse the official package evaluator once per distinct package. Unrelated facts are
not attached, and the service performs only reads in the caller session.

The focused RED observed empty row-260 document tuples. GREEN plus center regression reached
`18 passed`. Independent review required explicit fail-closed coverage for every distinct
cross-case association and corrupt enum; the test-only correction added that matrix, and final
focused/regression verification reached `24 passed`. Scoped Ruff, format and diff checks passed;
the corrected range was independently approved with P0/P1/P2 all zero.

No fee/gate/pagination/API/UI/schema behavior or fuzzy association is included. Rollback reverts
the two commits and this adoption; row 260 remains the predecessor and later overlay rows own
their separate successor changes.
