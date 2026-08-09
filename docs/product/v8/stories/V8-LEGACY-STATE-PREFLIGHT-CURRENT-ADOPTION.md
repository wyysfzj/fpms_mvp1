# Story V8-LEGACY-STATE-PREFLIGHT-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Outcome: provide a deterministic, read-only preflight for legacy lifecycle state and
  document-evidence conflicts before any separately authorized import.
- Catalog ID: `FPMS-V8-LEGACY-STATE-PREFLIGHT-20260712-01` (ordinal `252`).
- Contract freeze: `1b16956e72a23515651d18361fe86ce6c9e1ea8a`.
- Product commits: `71b219f6c90ee968aa16fcc0be0a320b78d1216b` and
  `1d219f5ad465ee45ce904c6adadcadf84ed02411`.

## Observable contract

`audit_v8_legacy_state()` reads every case in stable ID order, selects only the latest
confirmed LIFECYCLE activity, validates stored lifecycle carriers without inference, and
delegates status classification to the accepted one-way
`project_legacy_case_status()` rule. Malformed carriers are retained as exact conflict
rows instead of aborting later rows.

Legacy `GRANTED` never becomes authority for `PATENT_IN_FORCE`. It remains an unresolved
conflict unless an already-managed, fully confirmed, conflict-free projection is exactly
unchanged as `GRANTED`.

The same preflight consumes row 254 only through
`import_legacy_document_evidence(..., dry_run=True)` and preserves its five attachment
classifications. It creates no reverse lifecycle mapping, event, import, evidence version,
status update, transaction boundary or second report family.

The report contains stable rows, derived counts and a canonical SHA-256 that excludes the
auditor identity. Equal stored facts produce equal bytes and digest for every valid actor.

## Verification and review

The real RED produced `18 failed` on the missing module. The focused GREEN initially
reached `17 passed, 1 failed`; the sole failure was a test-only AST false positive that
mistook `set.add()` for `Session.add()`. After restricting the assertion to transaction
methods, the exact focused suite passed `18` tests. Independent review then required one
missing confirmed FEE-activity exclusion case; correction commit `1d219f5` added only that
case and the independent rerun passed all `18` tests.

Scoped Ruff, format and exact-path diff checks passed. The final independent High review
approved the cumulative candidate with `P0/P1/P2 = 0/0/0`.

## Non-goals and rollback

No CLI, endpoint, UI, schema, migration, backfill, activity append, projection update,
evidence import or conflict persistence is included. Rollback removes only the two
task-owned source/test commits and this adoption record; accepted lifecycle projection and
row-254 import behavior remain unchanged.
