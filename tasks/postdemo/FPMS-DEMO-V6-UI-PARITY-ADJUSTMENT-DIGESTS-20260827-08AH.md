# FPMS-DEMO-V6-UI-PARITY-ADJUSTMENT-DIGESTS-20260827-08AH

Status: READY / CONTRACT FROZEN
Risk-Tier: HIGH
Closure-Tags: ["demo", "fees", "ui"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-ADJUSTMENT-DIGESTS-20260827-08AH.md
Chosen runbook: `P0-single-lane-story`

## Design references

- Standing user authority granted with Task08AG for directly analogous minimal Demo-critical fixes.
- Accepted Task08AG HEAD `87f9fb2aba661fc55c671dc40fb9affc0fe9f62e`.
- Latest strict Stage 08 diagnostic confirmed adjustment 201 and updated source facts, but the
  source-facts table displayed only the reason while its existing API fields
  `adjustment_before_digest` and `adjustment_after_digest` remained invisible.

## Exact Closure Slice

In the existing service adjustment-record cell, display the existing before and after snapshot
digests with Simplified-Chinese labels and an explicit `sha256:` prefix. Pin both projections in the
focused frontend contract.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-ADJUSTMENT-DIGESTS-20260827-08AH.md`
- `frontend/src/modules/fees/pages/FeeDraftDetail.vue`
- `frontend/tests/demo-v6-fee-ui-parity-contract.mjs`

## Explicit Non-Closure

- No backend, API type, schema, migration, digest calculation, fee fact, adjustment, layout
  redesign, generic table abstraction, runner, strict journey, runbook, candidate, or release change.
- No adjacent source-fact fields, styling, truncation, copy action, or broad suite.
- Do not absorb or modify active Task08 dirty files.

## Verification Commands

1. Focused RED then GREEN: `node frontend/tests/demo-v6-fee-ui-parity-contract.mjs`.
2. Scoped ESLint for the page and focused contract.
3. Exact baseline-subtracted scope and `git diff --check`.
4. Independent zero-finding HIGH review and atomic evidence gate.
5. Resume strict UI and verify distinct before/after digests on screen.

## Evidence Path

`artifacts/FPMS-DEMO-V6-UI-PARITY-ADJUSTMENT-DIGESTS-20260827-08AH/`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-UI-PARITY-STRICT-E2E-20260826-08`

## Prompt

Expose only the existing adjustment before/after digests in the service source-fact row.
