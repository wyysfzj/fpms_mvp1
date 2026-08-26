# FPMS-DEMO-V6-UI-PARITY-OBSERVER-20260826-03

Status: ACTIVE
Risk-Tier: HIGH
Closure-Tags: ["data", "lineage", "security", "ui"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-OBSERVER-20260826-03.md
Chosen runbook: `P0-frontend-heavy-story`

## Design References

- Approved design:
  `docs/superpowers/specs/2026-08-26-fpms-demo-v6-ui-parity-design.md`, exact commit
  `5d48d0aed4356e7a1bd2d958301afe6ffab12b4d`.
- Approved plan:
  `docs/superpowers/plans/2026-08-26-fpms-demo-v6-ui-parity-implementation.md`, exact commit
  `80bd46829eaf5f798dda9422550a583c7fa12fde`.
- Active lean overlay:
  `docs/superpowers/plans/2026-08-26-fpms-demo-v6-ui-parity-lean-execution-overlay.md`.
- Accepted Ordinal 02 HEAD: `1971f62e2f3a489158ae83aec62c0ef42c72f8f2`.

## Exact Closure Slice

Expose the validated Ordinal 02 synthetic UI-session boundary on every normal page and install one
local-demo-only passive observer around the existing Axios instance. Persist only the exact validated
session tuple, correlate visible user actions to browser mutations, and invoke the pre-registered
observer-only finalize binding from `/demo/inputs`.

## Fixed Scope Decision

- `shared_file_density=MEDIUM`
- `prereq_dependency_density=HIGH`
- `be_fe_coupling=FRONTEND_ONLY`
- `evidence_cost=MEDIUM`
- `chosen_runbook=P0-frontend-heavy-story`
- Scope expansion is denied; no normal business page or command API is added in this ordinal.

## Exact Behavior

1. Activate only after a fresh `SYNTHETIC_TEST_ONLY` preflight whose schema/contract, run,
   candidate commit/tree, authority SHA, and exact complete Ordinal 02 business-count key set all
   validate and every count is zero.
2. Persist that exact tuple in `sessionStorage`; reload accepts only the same tuple. Missing session,
   stale/changed tuple, wrong classification/schema/count keys, or nonzero count disables every
   V6-only control, clears active state, and records STOP.
3. Show on every normal page exactly:
   `合成演示数据｜仅用于技术展示，非客户、生产或官方事实`.
4. The passive observer captures the immediately preceding visible click/submit route, role,
   label/testid, and action id; the existing Axios mutation method/path, normalized payload digest,
   response status; and console/network failures. It never issues, retries, blocks, or changes a
   request.
5. Observer storage excludes auth headers, tokens, passwords, credentials, cookies, and raw personal
   fields. Payload evidence is normalized/digested only.
6. `/demo/inputs` adds `完成并导出本轮证据`; it invokes the Ordinal 02 headed-session binding, writes
   only observer ledgers/screenshots under the external artifact root, and performs no API request or
   business mutation.

## Explicit Non-Closure

- No backend, API, schema, migration, seed, business command, request retry/reconcile, route mock,
  direct HTTP/DB, normal-page workflow entry, strict journey, customer activation, release, or
  Ordinal 04 behavior.
- No generic analytics/telemetry framework, raw payload recorder, global error redesign, `/demo/abc`
  integration, adjacent UI cleanup, or new English user-facing text.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-OBSERVER-20260826-03.md`
- `frontend/src/api/http.ts`
- `frontend/src/App.vue`
- `frontend/src/modules/demo/demo.contract.ts`
- `frontend/src/modules/demo/pages/DemoInputs.vue`
- `frontend/src/modules/demo/demoUiSession.ts`
- `frontend/src/components/demo/DemoBoundaryBanner.vue`
- `frontend/tests/demo-v6-ui-session-contract.mjs`
- `artifacts/FPMS-DEMO-V6-UI-PARITY-OBSERVER-20260826-03/**`

## Verification Commands

```bash
node frontend/tests/demo-v6-ui-session-contract.mjs
(cd frontend && npm run typecheck)
(cd frontend && npx eslint src/api/http.ts src/App.vue src/modules/demo/demo.contract.ts \
  src/modules/demo/pages/DemoInputs.vue src/modules/demo/demoUiSession.ts \
  src/components/demo/DemoBoundaryBanner.vue)
git diff --check
```

GREEN must prove exact-count parsing, tuple persistence/drift STOP, banner visibility, visible-action
correlation, digest-only/redacted observation, unchanged Axios request semantics, and binding-only
finalization with zero API/business mutation. Independent review binds the exact task range.

Expected HTTP status codes: unchanged existing API semantics; observer is passive.

## Evidence Path

- `artifacts/FPMS-DEMO-V6-UI-PARITY-OBSERVER-20260826-03/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-UI-PARITY-LIFECYCLE-20260826-04`, blocked until this task is accepted.

## Done Definition

The exact synthetic session alone activates a visible boundary and passive observer; drift/missing
state stops cleanly; no secret/raw personal data or observer-originated request is recorded; focused
contract, typecheck, scoped ESLint, independent review, and evidence gate pass with zero findings.

## Rollback

Run `git revert --no-edit <accepted-task-range>`. Ordinal 02 setup-only session remains available.
