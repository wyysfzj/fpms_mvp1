# Story V8-FEE-REDUCTION-APPROVAL-NOTICE-ACTIVATION-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Integration parent: `6c34db4`
- Product/test commit: `caf0da6`
- Outcome: only `OFFICIAL_NOTICE_031 / 费用减缓审批通知书 / 200021` joins the
  existing executable official-notice rows as `FEE_REDUCTION_APPROVAL_NOTICE`; a reviewed
  confirmed notice records or reuses exactly one scoped approval.
- Catalog ID: `FPMS-V8-FEE-REDUCTION-APPROVAL-NOTICE-ACTIVATION-20260712-01`
  (ordinal `129`, profile `TC-SERVICE`).
- Authority: frozen catalog row `129`, its exact task contract, the current-verified row
  `127` adapter and row `128` application-fee activation, `docs/product/v8/domain-contract.md`,
  and `docs/product/v8/source-decision-registry.md`.

## Dependency and exact paths

- `backend/app/modules/documents/official_notice_catalog.py`
- `backend/scripts/seed_dev.py`
- `backend/tests/test_v8_fee_reduction_approval_notice_activation.py`

Rows 127 and 128 are current-verified. The shared catalog, development seed and
SQLite-writing verification lanes remain serialized. The C3 integration contract
supersedes the old task, canonical-scope and evidence-artifact machinery; this story does
not mutate those historical paths.

## Observable contract

The target extends the eight existing executable official-notice rows and no others. Its
metadata contains only the executable behavior and canonical template code required by the
row-127 adapter. It carries no deadline policy, completion event, archive restoration,
status effect, deadline template, reply relationship or fee-draft trigger. Every other IN
catalog row remains reference-only.

The development seed selects the cumulative row-129 activation set, converges both new and
existing catalog rows and is idempotent. A focused real-SQLite test supplies exact final,
independently approved, current source evidence plus reviewed applicant, fee scope and
`0.85` ratio facts. Processing the same notice twice creates once and reuses once, leaving
the case status and task, document, obligation, draft and activity counts unchanged.

## TDD and verification

The targeted RED failed `2/2`: development seed omitted row 31 and the row-129 seeder was
missing. The minimum cumulative activation map, seeder and development-seed selection then
made the focused test pass `2/2`. The attributable row127/128/129 and non-stale predecessor
regressions passed `17/17`; scoped Ruff and format checks passed.

The historical all-inherited command reported `17 passed, 17 failed`. Three failures are
legal successor invalidations: predecessor seed-dev assertions intentionally freeze the
executable set before row 129. Fourteen failures are pre-existing fixture drift: legacy case
creation omits the now-required `fee_reduction` field and receives `422` before exercising
notice behavior. This story does not rewrite those read-only predecessor tests. Independent
High review must bind the exact candidate patch and explicitly successor-attest the
overlapping current row127/128 stories. After establishing the approved local Vite and
Chromium test boundary, the inherited UI-clarity Playwright spec also passed `1/1`.
The independent controller review then approved the exact `caf0da6` product/test commit
with P0/P1/P2 `0/0/0`; its decisive row127/128/129 tranche passed `10/10`.

## Non-goals and rollback

No endpoint, UI, schema, migration, deadline, reply, obligation, draft, lifecycle change,
customer default, second catalog row, adapter/service rule or adjacent cleanup is added.
Rollback removes the row-31 cumulative activation/seeder selection, its focused test and
this story card, restoring row 128 as the latest executable catalog state.
