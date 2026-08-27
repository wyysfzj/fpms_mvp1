# FPMS-DEMO-V6-UI-PARITY-FEE-LANE-DEDUPLICATION-20260827-08AI

Status: READY / CONTRACT FROZEN
Risk-Tier: HIGH
Closure-Tags: ["demo", "fees", "ui"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-FEE-LANE-DEDUPLICATION-20260827-08AI.md
Chosen runbook: `P0-single-lane-story`

## Design references

- Standing user authority granted with Task08AG for directly analogous minimal Demo-critical fixes.
- Accepted Task08AH HEAD `1c6c56105d26da99fd9c2f9416a40a10d8ee3b3d`.
- Latest strict Stage 08 diagnostic completed both draft locks, then showed one GOV obligation three
  times and two SERVICE obligations six times because the fee lane flat-mapped milestone snapshots.

## Exact Closure Slice

Project one fee-lane card per obligation ID across milestone snapshots, retaining the latest
occurrence so current statuses, related facts, and supersession facts remain visible. Pin this
projection in the focused frontend contract.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-FEE-LANE-DEDUPLICATION-20260827-08AI.md`
- `frontend/src/modules/cases/components/FeeObligationLane.vue`
- `frontend/tests/demo-v6-fee-ui-parity-contract.mjs`

## Explicit Non-Closure

- No backend, overlay payload, milestone order, fee fact, obligation state, sorting policy, generic
  deduplication framework, other overlay lane, runner, strict journey, runbook, candidate, or release change.
- No card redesign, status translation cleanup, pagination change, or broad suite.
- Do not absorb or modify active Task08 dirty files.

## Verification Commands

1. Focused RED then GREEN: `node frontend/tests/demo-v6-fee-ui-parity-contract.mjs`.
2. Scoped ESLint, exact dirty-baseline scope, and `git diff --check`.
3. Independent zero-finding HIGH review and atomic evidence gate.
4. Resume strict UI and verify GOV 1 / SERVICE 2 with unique cards.

## Evidence Path

`artifacts/FPMS-DEMO-V6-UI-PARITY-FEE-LANE-DEDUPLICATION-20260827-08AI/`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-UI-PARITY-STRICT-E2E-20260826-08`

## Prompt

Deduplicate fee-lane milestone projections by obligation ID while retaining the latest value.
