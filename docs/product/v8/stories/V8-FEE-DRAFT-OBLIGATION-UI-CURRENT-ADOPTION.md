# Story V8-FEE-DRAFT-OBLIGATION-UI-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Integration parent: `f14d269`
- Outcome: let the generic fee-draft create page consume one explicit obligation identity,
  show its server-owned source and instruction facts, and permit the linked manual draft
  only when the exact server instruction is `PAY`.
- Catalog ID: `FPMS-V8-FEE-DRAFT-OBLIGATION-UI-ADAPTER-20260712-01`
  (ordinal `118`, profile `TC-UI`).
- Authority: frozen catalog row `118`, its exact task contract,
  `docs/product/v8/domain-contract.md`, `docs/product/v8/source-decision-registry.md`, and
  the current-verified row `112` obligation-detail and row `117` generic-draft frontend
  adapters.

## Dependencies and exact paths

Both canonical predecessors are current-verified:

- `FPMS-V8-FO-OBLIGATION-DETAIL-FE-ADAPTER-20260712-01` through
  `V8-FEE-OBLIGATION-HTTP-FE-VERTICAL-CURRENT-ADOPTION`.
- `FPMS-V8-GENERIC-FEE-DRAFT-OBLIGATION-FE-ADAPTER-20260712-01` through
  `V8-GENERIC-FEE-DRAFT-OBLIGATION-FE-CURRENT-ADOPTION`.

The exact story paths are:

- `frontend/src/modules/fees/pages/FeeDraftCreate.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-fee-draft-obligation.spec.ts`
- `docs/product/v8/stories/V8-FEE-DRAFT-OBLIGATION-UI-CURRENT-ADOPTION.md`

No old task, taskctl, evidence, canonical-scope, artifact, ledger, review, disposition,
backend or shared ownership file enters this story.

## Observable contract

`/fees/drafts/new?obligation_id=...` accepts only the explicit, singular, non-empty query
identity and requests `getFeeObligation` for that exact value. The page displays the direct
server obligation ID, source activity, source document, source status and client
instruction. It enables linked generic-draft creation only when the returned obligation ID
matches the query and `client_instruction_status` is exactly `PAY`; the create payload then
transports that same `obligation_id`.

Missing detail, an invalid or mismatched query identity, a non-`PAY` instruction, or mixing
the obligation link with application-fee generation fails closed. An absent
`obligation_id` performs no obligation read and preserves the existing unlinked generic
draft payload. The page derives no obligation, amount, source, instruction, fee rule or
business state.

## TDD and verification

The dedicated Playwright probe first produced the expected behavior RED: the two linked
obligation scenarios failed because no obligation detail was requested or rendered, while
the unlinked compatibility scenario passed. After the minimum page change, the initial
probe passed `3/3`. Independent review then required explicit coverage of the remaining
fail-closed branches. The expanded exact probe passed `7/7`, proving exact `PAY` transport,
non-`PAY` blocking, duplicate identity rejection, detail-load failure, returned-ID mismatch,
application-fee mixing rejection and no-identity/no-inference compatibility. The only
correction was a test locator narrowed to the exact heading; product bytes were unchanged.

Run the exact focused Playwright probe with one worker, exact-page ESLint and scoped
whitespace/diff checks. The full frontend typecheck retains seven known integration-base
errors outside this story and is not a repair surface for row 118. An independent High
reviewer must review the eventual exact commit and independently rerun the decisive checks;
the implementer does not approve this `PROTECTED` story.

## Non-goals and rollback

No backend, second page capability, frontend business-state calculation, amount/source/rate
or reduction rule, payment or service receivable, automatic draft, lifecycle/legal state,
schema/migration, SQLite command, adjacent catalog row, inherited typecheck repair, old
evidence mutation, ledger/review/disposition edit or milestone claim. Rollback reverts only
the three paths listed above.
