# Story V8-PAYLIST-BOUNDARY-FE-ADAPTER-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Integration parent: `607261b`
- Outcome: expose the current PayList detail response as four separate frontend facts
  without deriving official state from the PayList header.
- Catalog ID: `FPMS-V8-PAYLIST-BOUNDARY-FE-ADAPTER-20260712-01` (ordinal `163`,
  profile `TC-FE-ADAPTER`).
- Authority: frozen catalog row `163`, its exact task contract,
  `docs/product/v8/domain-contract.md`, and the current-verified row `162` PayList
  export-artifact reader.
- Change mode: adopt the preserved pre-Lean row-163 candidate onto the current lean tree,
  then run a fresh current-tree contract RED/GREEN and scoped frontend verification.

## Dependency and exact paths

The sole canonical prerequisite is
`FPMS-V8-PAYLIST-EXPORT-ARTIFACT-READ-20260712-01`, current-verified by
`V8-PAYLIST-EXPORT-BOUNDARY-CURRENT-ADOPTION`.

- `frontend/src/api/govPayments.ts`
- `frontend/src/api/govPayments.types.ts`
- `frontend/src/api/contracts/v8_pay_list_boundary.contract.ts`
- `docs/product/v8/cutover-dirty-path-disposition.json`
- `docs/product/v8/stories/V8-PAYLIST-BOUNDARY-FE-ADAPTER-CURRENT-ADOPTION.md`

No old task, taskctl evidence, ledger, review, backend or other shared ownership file
enters this story.

## Observable contract

`PayListDetailResult` retains the existing header and `gov_payments` fields while exposing
four independent facts:

- `internal_artifacts` contains only persisted `INTERNAL_XLSX` artifacts;
- `official_workbook` preserves the optional server workbook metadata unchanged;
- `payment` is the normalized payment-row projection and is also retained under the
  existing `gov_payments` name for current consumers; and
- `official_evidence` contains only persisted `OFFICIAL_XLSM` artifacts, including their
  own generated/accepted status and acceptance-evidence fields.

The adapter uses only the server's `export_artifacts`, `official_workbook` and
`gov_payments` fields. It does not inspect or map `pay_list.status`, infer official
acceptance from a header or payment, synthesize missing arrays, or convert persisted
artifact/workbook facts. Existing payment amounts retain the adapter's established number
normalization.

## TDD and verification

The preserved pre-Lean candidate stopped at `READY_FOR_REVIEW`; its historical RED/GREEN
and candidate patch remain provenance, not current acceptance.

On the current tree, the dedicated contract probe first failed on the four missing public
types and the missing `internal_artifacts`, `official_workbook`, `payment` and
`official_evidence` properties. After the minimum type and adapter changes, those owned
errors disappeared and the exact strict isolated TypeScript command exited `0`:
`npx tsc --noEmit --strict --skipLibCheck --target ES2022 --module ESNext
--moduleResolution Bundler --lib ES2022,DOM --types node,vite/client
src/api/contracts/v8_pay_list_boundary.contract.ts`.

Exact-file ESLint and scoped diff-check pass. The required full frontend typecheck still
reports seven inherited integration-base errors in `billing.ts`, `http.ts`,
`officialWorkflows.ts` and `CaseFeesTab.vue`; it reports no row-163 or owned-path error.
The same seven errors exist without this story, so the row-specific strict contract probe
is the baseline-subtracted type gate. No full frontend build or SQLite command was run.

An independent High reviewer must review the exact eventual commit and rerun the decisive
checks. The implementer does not approve this `PROTECTED` story.

## Non-goals and rollback

The exact disposition transfer leaves all `474` paths unique and moves only the three
frontend paths from `V8-ADOPT-PAYLIST-PAYMENT` to this story. The exact disposition
SHA-256 is
`2aa582e916df1bfe7d81995693241750bc3211d3fb2d163884132760884ebdd1`.

No page behavior, backend, server-state inference, official-workbook generation or
acceptance, payment/evidence fabrication, lifecycle/legal state, fee/source rule,
schema/migration, SQLite, customer decision, adjacent catalog row, old evidence mutation,
ledger/review edit or milestone claim. Rollback reverts only the five paths
listed above.
