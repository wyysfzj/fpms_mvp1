# Story V8-DUAL-READ-RECONCILIATION-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Integration parent: `bc48dad`
- Catalog ID: `FPMS-V8-DUAL-READ-RECONCILIATION-20260712-01` (ordinal `257`).
- Outcome: one deterministic read-only cutover report across lifecycle,
  document-evidence, fee-reduction and fee-truth legacy/current representations.

The implementation delegates only to the four current-verified import/link seams with
`dry_run=True`. Exact existing facts are `RECONCILED`; every frozen invalid/conflict class
remains an explicit `CLASSIFIED_CONFLICT`; any remaining import/link action is
`REQUIRES_IMPORT` and prevents acceptance. Unknown result types, hashes, identities or
classifications fail closed with HTTP 409.

The report preserves the four child input/plan/output hashes, fixed lane ordering, stable
identities, exact counts and a canonical report SHA-256. It performs no import, repair,
flush, commit, rollback or direct product write.

The focused RED failed `5/5` because the compositor seam was absent. Focused and all four
importer/preflight affected regressions passed `81/81`; scoped Ruff, format and diff checks
passed. Independent High review approved the exact product commit with P0/P1/P2 all zero.

No endpoint/UI/schema, migration execution, conflict repair, source change, static write
gate or adjacent cleanup is included. Rollback reverts product commit `c5f689b` and this
ledger adoption only.
