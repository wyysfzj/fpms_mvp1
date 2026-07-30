# Story V8-CASE-FEE-REDUCTION-VERTICAL-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Outcome: make case create and update require an explicit fee-reduction ratio and make
  the create UI submit only the canonical numeric choice, without inferring a reduction
  or expanding adjacent case behavior.
- Base: `89d2686db34e3ff419e3a93300da80e78aadc666`.
- Authority: `docs/product/v8/domain-contract.md`,
  `docs/product/v8/source-decision-registry.md`, frozen catalog rows `98`–`100`, their
  exact task contracts, and the current verified fee-reduction validator and approval
  service.

## Catalog IDs and order

1. `FPMS-V8-CASE-CREATE-FEE-REDUCTION-API-20260712-01` (ordinal `98`) depends on
   current-verified rows `93` and `94`.
2. `FPMS-V8-CASE-UPDATE-FEE-REDUCTION-API-20260712-01` (ordinal `99`) follows row `98`.
3. `FPMS-V8-CASE-CREATE-FEE-REDUCTION-UI-20260712-01` (ordinal `100`) follows row `98`.

The dependency commits `c2c45134fdf38602617fedf0f56ecadba0f3f8c6` and
`1a886c4e40b0ee6e83882c42e6eb4da561feccc7` are ancestors of the story base.

## Observable contract

- Case create rejects missing or ambiguous reduction input. Explicit `0` means no
  reduction. `0.7` or `0.85` requires a matching confirmed approval for the submitted
  applicant composition and otherwise returns `409`.
- Case update has the same fail-closed boundary, records actor/time for an explicit
  replacement, and never coerces unknown legacy data.
- The create page starts unset, requires an explicit Simplified-Chinese selection, sends
  only numeric `0`, `0.7`, or `0.85`, and explains that reduced ratios require a recorded
  approval. It never sends `NONE`, `PARTIAL`, or `FULL`.

## Exact paths

### Product

- `backend/app/modules/cases/schemas.py`
- `backend/app/modules/cases/service.py`
- `frontend/src/api/cases.ts`
- `frontend/src/api/cases.types.ts`
- `frontend/src/modules/cases/pages/CaseCreate.vue`

### Focused tests

- `backend/tests/test_v8_case_create_fee_reduction.py`
- `backend/tests/test_v8_case_update_fee_reduction.py`
- `backend/tests/test_v8_case_create_status_gate.py` (one-line successor fixture)
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-create-fee-reduction.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-create-status-gate.spec.ts`
  (successor fixture if required by the explicit-selection contract)

### Story

- `docs/product/v8/stories/V8-CASE-FEE-REDUCTION-VERTICAL-CURRENT-ADOPTION.md`

The three focused tests are adopted byte-for-byte from archive ref `6b2ef89`; their Git
blobs are respectively `f1baea57b66e29731ef04108f2d7bc3031800f50`,
`dfa57495070a414558d2a24c3642637e27ca11de`, and
`fe78a4a22dab209d968e9098e9aebc3f3a87ceab`.

## TDD and verification

Fresh story-branch verification:

- Row 98 RED stopped at collection because `_canonical_create_fee_reduction` was absent.
  The minimum schema/service implementation then produced `27 passed` plus 19 subtests.
  The adopted canonical validation/helper block is byte-identical to its archive slice
  at SHA-256 `a9b2b0e4aa9c9eebb6bff7f299c73aedc776cf0f560e4f49aef75e20b33a7645`.
- Row 99 RED produced `15 failed, 11 passed`; failures proved missing strict replacement,
  composition-change and confirmed-approval behavior. The minimum update seam then
  produced `26 passed`.
- Row 100 real-browser RED produced three expected failures because the canonical
  reduction control and explanation were absent. The minimum UI/API/type change then
  produced `3 passed`.
- The affected backend case-status tranche initially produced `1 failed, 97 passed`
  because its pre-existing create fixture omitted the newly required explicit choice.
  Adding only `"fee_reduction": "0"` to that fixture produced a final `98 passed` plus
  19 subtests across the two focused tests and three existing lifecycle/status tests.
- The affected existing CaseCreate status-gate Playwright test likewise proved its
  create request was blocked until its fixture explicitly selected `不减免（0）`. The
  final combined create-fee-reduction/status tranche produced `4 passed`; the unchanged
  CaseEdit status-gate spec produced `1 passed`.
- Scoped Ruff on the two case product files and three backend tests passed.
- Exact-file ESLint on `cases.ts`, `cases.types.ts`, and `CaseCreate.vue` passed.
- Exact-story `vue-tsc --noEmit` on those three frontend product files passed.
- The repository frontend typecheck still reports seven inherited errors only in
  `billing.ts`, `http.ts`, `officialWorkflows.ts`, and `CaseFeesTab.vue`; none is a
  changed path or caused by this story.
- `git diff --check` passed.

The initial bare `npx` Playwright invocation found a user-level binary and produced no
browser child or output; it was stopped after the liveness threshold. Effective RED/GREEN
used this worktree's project dependencies and a dedicated local Vite port. The first
sandboxed browser launch was denied by macOS Mach-port isolation before test execution;
the recorded product RED/GREEN results are from the subsequently authorized exact
single-spec commands.

Exact commit identity and independent review remain pending.

## Non-goals and rollback

No CaseEdit UI, row `97` or `101`, second endpoint, router rewiring, applicant-policy
inference, fee amount, source activation, customer decision, schema/migration/seed,
adjacent case cleanup, legacy-language cleanup, broad frontend build, broad Playwright,
ledger/disposition/review edit, or milestone claim.

Rollback reverts the single story commit and restores the current case create/update and
CaseCreate behavior without altering the verified validator or approval-service stories.
