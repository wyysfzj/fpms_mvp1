# FPMS-DEMO-INTEGRATED-A-DRAFT-IDENTITY-20260822-08B

Status: ACTIVE
Risk-Class: NORMAL
Outcome: The fee-draft detail page shows the authoritative draft UUID anywhere labelled as the draft number.
Source: Task 8 fresh rehearsal at commit `8d6b7a58a4f1a52b90990bd9f839692b76c784cc`.
Dependency: `FPMS-DEMO-INTEGRATED-A-FINANCE-20260821-08` remediation candidate `8d6b7a5`.

## Observable Outcome

After opening `/fees/drafts/:id`, the header, overview and relation-chain label display the exact
`draft.id` returned by the authoritative detail API. The separate draft-type subtitle continues to
use the localized draft-type label. The route identity assertion in the Integrated A rehearsal can
therefore compare a customer-visible value with the authoritative response.

## Non-Goals

No fee, billing, payment, offset, lifecycle, API, route, session, styling, permission, security,
production or release behavior changes. No adjacent cleanup of the fee-draft page.

## Expected Paths

- `frontend/src/modules/fees/pages/FeeDraftDetail.vue`
- `frontend/tests/fee-draft-detail-identity-contract.mjs`
- `tasks/postdemo/FPMS-DEMO-INTEGRATED-A-DRAFT-IDENTITY-20260822-08B.md`

## Tests

- `node frontend/tests/fee-draft-detail-identity-contract.mjs`
- `cd frontend && npm run typecheck`
- `cd frontend && npx eslint src/modules/fees/pages/FeeDraftDetail.vue`
- one fresh Task 8 headless rehearsal, which must persist IA-01…17 and stop only at IA-18 RED

## Risk and Rollback

Risk is NORMAL UI identity presentation. Rollback is the single exact commit for this story; it
restores the prior incorrect type-as-number display without changing stored data.

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-INTEGRATED-A-FINANCE-20260821-08`
- `FPMS-DEMO-INTEGRATED-A-RUNNER-20260821-09`
- `FPMS-DEMO-INTEGRATED-A-FINAL-20260821-10`
