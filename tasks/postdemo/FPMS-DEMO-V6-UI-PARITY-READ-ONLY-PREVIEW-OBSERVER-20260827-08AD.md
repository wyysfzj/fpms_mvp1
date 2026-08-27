# FPMS-DEMO-V6-UI-PARITY-READ-ONLY-PREVIEW-OBSERVER-20260827-08AD

Status: READY / CONTRACT FROZEN
Risk-Tier: HIGH
Closure-Tags: ["demo", "evidence", "ui"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-READ-ONLY-PREVIEW-OBSERVER-20260827-08AD.md
Chosen runbook: `P0-single-lane-story`

## Design references

- User approval: `` `批准 Task08AD 文书影响预览只读观察器最小分类边界` ``.
- Accepted Task08AC HEAD `c6e9e78be3b165535ad6e449c79f9a92b9b7dc06`.
- Strict UI Stage 08 diagnostic: the observer emitted `STOP:UNMATCHED_MUTATION` on
  `POST /api/v1/documents/impact-preview`; Stage 01–07 then continued outside the stopped
  observer, so the Stage 08 session-only service-obligation control was not rendered.

## Exact Closure Slice

The active Demo UI observer must classify only the existing
`POST /documents/impact-preview` Axios request as a read-only preview. It must neither append a
mutation event nor consume the last visible action nor trigger terminal STOP. The next real
business mutation must still consume that same visible action and retain all existing unmatched
mutation, transport-failure, console-failure, capability and terminal behavior.

## Scope decision — FIXED

- `shared_file_density`: low
- `prereq_dependency_density`: low
- `be_fe_coupling`: frontend observer only
- `evidence_cost`: low
- `chosen_runbook`: `P0-single-lane-story`
- The strict journey already classifies this exact endpoint as read-only for its passive network
  ledger. This task synchronizes the session observer with that frozen fact.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-READ-ONLY-PREVIEW-OBSERVER-20260827-08AD.md`
- `frontend/src/modules/demo/demoUiSession.ts`
- `frontend/tests/demo-v6-ui-session-contract.mjs`

## Explicit Non-Closure

- No backend, API response, document-preview behavior, business mutation, schema, migration,
  fee/lifecycle rule, security, permission, runner, strict journey, runbook, candidate, or release
  change.
- No generic safe-method registry, configurable endpoint list, observer rewrite, URL-normalization
  cleanup, or relaxation for any other POST endpoint.
- No broad frontend suite or broad Playwright run.
- Do not absorb or modify active Task08 dirty files.

## Verification Commands

1. Focused RED then GREEN:
   `node frontend/tests/demo-v6-ui-session-contract.mjs`.
2. Scoped ESLint for the two changed implementation/test files.
3. Exact baseline-subtracted scope and `git diff --check`.
4. Independent findings-only review with `Verdict: APPROVED`, `P0: 0`, `P1: 0`, `P2: 0`.
5. Atomic evidence validation after review.
6. Resume the strict UI diagnostic from Stage 01 and confirm it reaches the first Stage 08 result.

## Evidence Path

`artifacts/FPMS-DEMO-V6-UI-PARITY-READ-ONLY-PREVIEW-OBSERVER-20260827-08AD/`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-UI-PARITY-STRICT-E2E-20260826-08`

## Prompt

Implement only the exact read-only preview observer classification. Do not add a generic policy or
absorb any follow-up.
