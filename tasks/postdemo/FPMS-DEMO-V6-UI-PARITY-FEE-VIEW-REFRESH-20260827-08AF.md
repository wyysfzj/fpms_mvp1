# FPMS-DEMO-V6-UI-PARITY-FEE-VIEW-REFRESH-20260827-08AF

Status: READY / CONTRACT FROZEN
Risk-Tier: HIGH
Closure-Tags: ["demo", "fees", "ui"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-FEE-VIEW-REFRESH-20260827-08AF.md
Chosen runbook: `P0-single-lane-story`

## Design references

- User approval: `` `批准 Task08AF 服务费义务生成后费用视图 200 条最小刷新边界` ``.
- Accepted Task08AE HEAD `73d1bfa0766cd222e8f9fc156094df03d474fb21`.
- Latest strict Stage 08 diagnostic: visible service-obligation creation returned 201, but the
  refreshed fee view requested only the first 50 lifecycle activities. The new obligation was
  sourced after sequence 50 and therefore remained absent from the visible fee-obligation list.
- Existing case lifecycle first-page read uses a 200-item limit.

## Exact Closure Slice

Synchronize only the post-service-obligation fee-view refresh from 50 to the existing 200-item
case lifecycle first-page limit, and pin that request projection in the focused frontend contract.

## Scope decision — FIXED

- `shared_file_density`: low
- `prereq_dependency_density`: low
- `be_fe_coupling`: frontend read query only
- `evidence_cost`: low
- `chosen_runbook`: `P0-single-lane-story`
- This changes no fee fact or lifecycle write; it exposes the already persisted obligation in the
  current V6 demo case whose new source activity is beyond sequence 50.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-FEE-VIEW-REFRESH-20260827-08AF.md`
- `frontend/src/modules/cases/components/CaseFeesTab.vue`
- `frontend/tests/demo-v6-fee-ui-parity-contract.mjs`

## Explicit Non-Closure

- No backend, schema, migration, fee amount, obligation write, lifecycle write, generic pagination,
  standalone loader, parent overlay, runner, strict journey, runbook, candidate, or release change.
- No adjacent refresh, error-handling, locator, naming, formatting, or cleanup change.
- No broad frontend suite or broad Playwright run.
- Do not absorb or modify active Task08 dirty files.

## Verification Commands

1. Focused RED then GREEN: `node frontend/tests/demo-v6-fee-ui-parity-contract.mjs`.
2. Scoped ESLint for the implementation and focused contract test.
3. Exact baseline-subtracted scope and `git diff --check`.
4. Independent findings-only review with `Verdict: APPROVED`, `P0: 0`, `P1: 0`, `P2: 0`.
5. Atomic evidence validation after review.
6. Resume the strict UI diagnostic and confirm the created service obligation is visible.

## Evidence Path

`artifacts/FPMS-DEMO-V6-UI-PARITY-FEE-VIEW-REFRESH-20260827-08AF/`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-UI-PARITY-STRICT-E2E-20260826-08`

## Prompt

Synchronize only the post-create fee-view lifecycle query limit from 50 to 200.
