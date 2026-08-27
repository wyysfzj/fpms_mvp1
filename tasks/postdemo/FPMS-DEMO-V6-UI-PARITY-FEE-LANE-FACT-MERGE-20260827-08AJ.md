# FPMS-DEMO-V6-UI-PARITY-FEE-LANE-FACT-MERGE-20260827-08AJ

Status: READY / CONTRACT FROZEN
Risk-Tier: HIGH
Closure-Tags: ["demo", "fees", "ui"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-FEE-LANE-FACT-MERGE-20260827-08AJ.md
Chosen runbook: `P0-single-lane-story`

## Design references

- Standing user authority granted with Task08AG for directly analogous minimal Demo-critical fixes.
- Accepted Task08AI HEAD `1b127f8cdf683edb45353b70bcfcb8ae584e88a3`.
- Latest strict Stage 08 diagnostic verified unique GOV/SERVICE cards, but the latest replacement
  obligation occurrence omitted the draft relation carried by an earlier milestone occurrence.

## Exact Closure Slice

While deduplicating obligation cards, retain the latest obligation projection and merge its related
facts across occurrences by `(kind, objectId)`, with later occurrences replacing the status of the
same fact. Pin preservation and latest-status replacement in the focused frontend contract.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-FEE-LANE-FACT-MERGE-20260827-08AJ.md`
- `frontend/src/modules/cases/components/FeeObligationLane.vue`
- `frontend/tests/demo-v6-fee-ui-parity-contract.mjs`

## Explicit Non-Closure

- No backend, overlay payload, obligation state, relation write, other obligation fields, other
  lanes, generic merge framework, runner, strict journey, runbook, candidate, or release change.
- No sorting or card redesign; no broad suite.
- Do not absorb or modify active Task08 dirty files.

## Verification Commands

1. Focused RED then GREEN: `node frontend/tests/demo-v6-fee-ui-parity-contract.mjs`.
2. Scoped ESLint, exact dirty-baseline scope, and `git diff --check`.
3. Independent zero-finding HIGH review and atomic evidence gate.
4. Resume strict UI and verify the draft link transferred to the replacement obligation card.

## Evidence Path

`artifacts/FPMS-DEMO-V6-UI-PARITY-FEE-LANE-FACT-MERGE-20260827-08AJ/`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-UI-PARITY-STRICT-E2E-20260826-08`

## Prompt

Merge only related facts while retaining the latest deduplicated obligation projection.
