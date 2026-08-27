# FPMS-DEMO-V6-UI-PARITY-SERVICE-OBLIGATION-REQUEST-20260827-08AE

Status: READY / CONTRACT FROZEN
Risk-Tier: HIGH
Closure-Tags: ["demo", "fees", "ui"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-SERVICE-OBLIGATION-REQUEST-20260827-08AE.md
Chosen runbook: `P0-single-lane-story`

## Design references

- User approval: `` `批准 Task08AE 服务费义务请求移除遗留 item_code 最小投影边界` ``.
- Accepted Task08AD HEAD `45e65d117893cd5cd6b7a860f22133a1274a7b1a`.
- Latest strict Stage 08 diagnostic: the visible `生成服务费义务` action reached
  `POST /fees/demo-service-obligations`, which returned 422 because the frontend sent the retired
  `item_code` field while `DemoServiceObligationIn` accepts only `case_id` and `idempotency_key`.

## Exact Closure Slice

Remove the retired `item_code` argument and JSON field from the existing frontend
`createDemoServiceObligation` request and its two frontend call sites. Keep the prior validated
runtime-item read and response comparison unchanged, so the server-owned multi-line runtime bundle
remains authoritative.

## Scope decision — FIXED

- `shared_file_density`: low
- `prereq_dependency_density`: low
- `be_fe_coupling`: frontend request projection only
- `evidence_cost`: low
- `chosen_runbook`: `P0-single-lane-story`
- The backend request schema and runtime source already own the selected service-fee lines; this is
  removal of a stale caller projection, not a new fee decision.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-SERVICE-OBLIGATION-REQUEST-20260827-08AE.md`
- `frontend/src/modules/demo/demo.api.ts`
- `frontend/src/modules/demo/pages/DemoAbc.vue`
- `frontend/tests/demo-v6-fee-ui-parity-contract.mjs`

## Explicit Non-Closure

- No backend, schema, migration, bundle, service-price, amount, obligation, adjustment, response,
  permission, observer, runner, strict journey, runbook, candidate, or release change.
- No parser rewrite, generic request builder, compatibility fallback, endpoint versioning, or
  adjacent API cleanup.
- No broad frontend suite or broad Playwright run.
- Do not absorb or modify active Task08 dirty files.

## Verification Commands

1. Focused RED then GREEN: `node frontend/tests/demo-v6-fee-ui-parity-contract.mjs`.
2. Scoped ESLint for the implementation and focused contract test.
3. Exact baseline-subtracted scope and `git diff --check`.
4. Independent findings-only review with `Verdict: APPROVED`, `P0: 0`, `P1: 0`, `P2: 0`.
5. Atomic evidence validation after review.
6. Resume the strict UI diagnostic and confirm the service-obligation request no longer returns 422.

## Evidence Path

`artifacts/FPMS-DEMO-V6-UI-PARITY-SERVICE-OBLIGATION-REQUEST-20260827-08AE/`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-UI-PARITY-STRICT-E2E-20260826-08`

## Prompt

Remove only the retired request field and signature argument. Preserve server-owned runtime facts.
