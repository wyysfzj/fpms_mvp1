# Story V8-GENERIC-FEE-DRAFT-OBLIGATION-FE-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Integration parent: `a9f500a`
- Outcome: type one optional obligation identity on generic fee-draft creation while
  preserving direct transport and the server-owned source, status and amount boundary.
- Catalog ID: `FPMS-V8-GENERIC-FEE-DRAFT-OBLIGATION-FE-ADAPTER-20260712-01`
  (ordinal `117`, profile `TC-FE-ADAPTER`).
- Authority: frozen catalog row `117`, its exact task contract,
  `docs/product/v8/domain-contract.md`, and the current-verified row `116` generic
  fee-draft obligation API adapter.

## Dependency and exact paths

The sole canonical prerequisite is
`FPMS-V8-GENERIC-FEE-DRAFT-OBLIGATION-API-ADAPTER-20260712-01`, current-verified by
`V8-GENERIC-FEE-DRAFT-OBLIGATION-API-CURRENT-ADOPTION`.

- `frontend/src/api/fees.ts`
- `frontend/src/api/fees.types.ts`
- `frontend/src/api/contracts/v8_fee_draft_obligation.contract.ts`
- `docs/product/v8/stories/V8-GENERIC-FEE-DRAFT-OBLIGATION-FE-CURRENT-ADOPTION.md`

No old task, taskctl, evidence, ledger, review, disposition, backend, UI or other shared
ownership file enters this story.

## Observable contract

`FeeDraftCreatePayload` exposes `obligation_id?: string | null`. Omitting the property or
passing `null` preserves legacy unlinked draft creation; passing a string transports that
exact identity through the existing `createFeeDraft` request. The create function retains
its exact `(data: FeeDraftCreatePayload) => Promise<FeeDraftDetail>` signature and posts
the caller payload unchanged.

The frontend does not add or derive an obligation source, status, amount, instruction,
fee rule or response projection. The dedicated compile-time probe asserts optional
nullability, the create signature, and rejection of caller-owned source-document and
amount fields.

## TDD and verification

The new contract probe first made the full frontend typecheck report three exact row-117
errors: two object-shape failures for `obligation_id` and one missing indexed property.
After the minimum one-property type change, all three owned errors disappeared. The exact
strict isolated contract compile exits `0`:

`npx tsc --noEmit --strict --skipLibCheck --target ES2022 --module ESNext
--moduleResolution Bundler --lib ES2022,DOM --types node,vite/client
src/api/contracts/v8_fee_draft_obligation.contract.ts`.

Exact-file ESLint and scoped diff-check pass. The required full frontend typecheck still
reports seven inherited integration-base errors in `billing.ts`, `http.ts`,
`officialWorkflows.ts` and `CaseFeesTab.vue`; it reports no row-117 or owned-path error.
No full frontend build, backend test or SQLite command was run.

An independent High reviewer must review the exact eventual commit and rerun the decisive
checks. The implementer does not approve this `PROTECTED` story.

## Non-goals and rollback

No page behavior, server-state inference, backend change, source or amount derivation,
fee/rate/reduction rule, payment or service receivable, lifecycle/legal state,
schema/migration, customer decision, adjacent catalog row, old evidence mutation,
ledger/review/disposition edit or milestone claim. Rollback removes only the optional
payload property, its contract probe and this story card.
