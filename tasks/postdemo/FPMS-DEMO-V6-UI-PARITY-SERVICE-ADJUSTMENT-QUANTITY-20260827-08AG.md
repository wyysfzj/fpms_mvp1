# FPMS-DEMO-V6-UI-PARITY-SERVICE-ADJUSTMENT-QUANTITY-20260827-08AG

Status: READY / CONTRACT FROZEN
Risk-Tier: HIGH
Closure-Tags: ["demo", "fees", "ui"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-SERVICE-ADJUSTMENT-QUANTITY-20260827-08AG.md
Chosen runbook: `P0-single-lane-story`

## Design references

- User approval and standing authority: `` `批准 Task08AG 服务费调整使用来源事实数量最小投影边界` ``;
  subsequent directly analogous minimal Demo-critical fixes may proceed without another approval.
- Accepted Task08AF HEAD `f2ffa563f510f36ff14dbc1da42f47fadbfa2b46`.
- Latest strict Stage 08 diagnostic passed visible obligation creation, PAY instruction, and linked
  draft creation, then sent `expected_quantity: 0` because the frontend projected a nullable fee
  item quantity instead of the persisted service source-fact quantity `1`; the API returned 422.

## Exact Closure Slice

For source-linked SERVICE draft items only, use the existing persisted source-fact quantity for the
visible quantity, adjustment dialog current quantity, immutable expected quantity, and submitted
adjustment payload. Pin the projection with the focused frontend contract.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-SERVICE-ADJUSTMENT-QUANTITY-20260827-08AG.md`
- `frontend/src/modules/fees/components/FeeDraftItemsTable.vue`
- `frontend/tests/demo-v6-fee-ui-parity-contract.mjs`

## Explicit Non-Closure

- No backend, schema, migration, source fact, fee item, amount, obligation, adjustment policy,
  generic fee editing, GOV path, API, runner, strict journey, runbook, candidate, or release change.
- No generic mapping framework, persistence rewrite, adjacent display cleanup, or broad suite.
- Do not absorb or modify active Task08 dirty files.

## Verification Commands

1. Focused RED then GREEN: `node frontend/tests/demo-v6-fee-ui-parity-contract.mjs`.
2. Scoped ESLint for the component and focused contract.
3. Exact baseline-subtracted scope and `git diff --check`.
4. Independent findings-only review with zero P0/P1/P2 findings and OE/review-discipline PASS.
5. Atomic evidence validation.
6. Resume strict UI and confirm adjustment no longer returns 422.

## Evidence Path

`artifacts/FPMS-DEMO-V6-UI-PARITY-SERVICE-ADJUSTMENT-QUANTITY-20260827-08AG/`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-UI-PARITY-STRICT-E2E-20260826-08`

## Prompt

Project the persisted service source-fact quantity into the adjustment UI and request only.
