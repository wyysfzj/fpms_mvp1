# FPMS-DEMO-V6-UI-PARITY-OBSERVER-REPAIR-20260826-03R

Status: ACTIVE
Risk-Tier: HIGH
Closure-Tags: ["data", "lineage", "security", "ui"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-OBSERVER-REPAIR-20260826-03R.md
Chosen runbook: `P0-frontend-heavy-story`

## Approval And Fixed References

- User approval: `批准 Ordinal 02R/03R 最小重划边界，修复后恢复 Ordinal 03 并继续后续计划`.
- Approved design: `docs/superpowers/specs/2026-08-26-fpms-demo-v6-ui-parity-design.md`,
  exact commit `5d48d0aed4356e7a1bd2d958301afe6ffab12b4d`.
- Approved plan: `docs/superpowers/plans/2026-08-26-fpms-demo-v6-ui-parity-implementation.md`,
  exact commit `80bd46829eaf5f798dda9422550a583c7fa12fde`.
- Active lean overlay:
  `docs/superpowers/plans/2026-08-26-fpms-demo-v6-ui-parity-lean-execution-overlay.md`.
- Accepted Ordinal 02R HEAD: `c4230a48e356764b956bbd51d34ce589969c88fa`.
- Rejected Ordinal 03 candidate: `54074a764ddd176f826711928453a6dc9ff4b236`.
- Controlling findings: the eight P1s in the independent review of
  `1971f62e2f3a489158ae83aec62c0ef42c72f8f2..54074a764ddd176f826711928453a6dc9ff4b236`;
  02R closed only their runner/host portion.

## Exact Closure Slice

Repair the existing Ordinal 03 frontend session/observer to consume the accepted 02R capability.
Close reload revalidation, fail-closed/auditable STOP, exact HTTP status, `/demo/abc` isolation,
canonical API typing, observer disposal, and evidence-complete browser finalization. Reuse the
existing implementation; do not create a second observer or session layer.

## Exact Behavior

1. Initial activation still requires the existing backend preflight, exact 77-key all-zero business
   projection, `SYNTHETIC_TEST_ONLY`, exact run/candidate/tree/authority/contract, and a valid 02R
   activation binding. Parse the actor from that authenticated binding and persist the full exact
   six-field host tuple plus binding in `sessionStorage`; never print or record the capability.
2. Normal-route reload restores only by POSTing the stored exact tuple to the same capability's
   `/revalidate` operation. It must not rerun the all-zero preflight after business mutations.
   Missing/drifted storage, wrong binding/actor/tuple, or failed revalidation transitions to STOP.
3. STOP disables every V6-only control but retains the redacted ledger and exact host tuple long
   enough to export the STOP evidence through the observer-only binding. Manual preflight failure,
   console error, window error, unhandled rejection, unmatched mutation, and network failure all
   transition to STOP; no observer operation issues/retries/changes a business request.
4. Preserve an Axios HTTP error's `response.status`; use `0` only for a transport failure. Reject the
   identical Axios error after observation.
5. `/demo/abc` and `/login` never show the boundary and are never observed. Entering `/demo/abc`
   during an active V6 session records/exports STOP and clears active controls; normal business
   routes remain covered.
6. Return and invoke an exact disposer for DOM/window listeners and console interception. Eject any
   installed Axios interceptors when disposed/reinstalled. Mount/unmount/reinstall cannot duplicate
   actions, failures, or interceptors and restores the original `console.error`.
7. Replace the obsolete ten-key `DemoPreflight` projection in `demo.api.ts` with the canonical
   contract type; remove the unsafe cast in `DemoInputs.vue`. Update the supported A contract test to
   validate runtime compatibility with the canonical parser, not stale source-string key literals.
8. Browser finalization uploads the redacted observer ledger and the eleven genuine stage PNG
   captures named by 02R, then POSTs the exact tuple to `/finalize`. It must not create repeated or
   synthetic placeholder images. A host rejection records STOP and preserves the run; only a 200
   finalization clears session state and reports success. The observer may capture visible browser
   state but may not click, fill, navigate, call a business API, or mutate business data.

## Explicit Non-Closure

- No backend/runner change, dependency addition, business API/state machine, schema/migration, seed,
  source/fee/lifecycle decision, generic telemetry, analytics, retry framework, or release.
- No normal-page business command, `/demo/abc` integration, Ordinal 04 behavior, UI redesign,
  adjacent translation/cleanup, or generated screenshot substitute.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-OBSERVER-REPAIR-20260826-03R.md`
- `frontend/src/api/http.ts`
- `frontend/src/App.vue`
- `frontend/src/modules/demo/demo.contract.ts`
- `frontend/src/modules/demo/demo.api.ts`
- `frontend/src/modules/demo/pages/DemoInputs.vue`
- `frontend/src/modules/demo/demoUiSession.ts`
- `frontend/src/components/demo/DemoBoundaryBanner.vue`
- `frontend/tests/demo-v6-ui-session-contract.mjs`
- `frontend/tests/demo-abc-contract.mjs`
- `artifacts/FPMS-DEMO-V6-UI-PARITY-OBSERVER-REPAIR-20260826-03R/**`

## Verification Commands

```bash
node frontend/tests/demo-v6-ui-session-contract.mjs
node frontend/tests/demo-abc-contract.mjs
(cd frontend && npm run typecheck)
(cd frontend && npx eslint src/api/http.ts src/App.vue src/modules/demo/demo.contract.ts \
  src/modules/demo/demo.api.ts src/modules/demo/pages/DemoInputs.vue \
  src/modules/demo/demoUiSession.ts src/components/demo/DemoBoundaryBanner.vue)
git diff --check
```

GREEN must dynamically prove initial all-zero activation, post-mutation reload revalidation through
the real 02R protocol, every STOP source and export, 409 versus transport status, `/demo/abc`
exclusion, dispose/remount behavior, exact API type/runtime compatibility, eleven non-placeholder PNG
uploads, ledger-before-finalize ordering, and no observer-originated business request. Independent
review binds the exact repaired Ordinal 03 range.

Expected loopback statuses are the accepted 02R semantics. Existing business API statuses and Axios
request/rejection identity are unchanged.

## Evidence Path

- `artifacts/FPMS-DEMO-V6-UI-PARITY-OBSERVER-REPAIR-20260826-03R/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-UI-PARITY-LIFECYCLE-20260826-04`, blocked until repaired Ordinal 03 is accepted.

## Done Definition

The exact fresh session activates once, survives normal reload through authenticated tuple-only
revalidation after mutations, stops and exports auditable evidence on every named failure, excludes
`/demo/abc`, disposes cleanly, reports exact HTTP status, uses canonical frontend types, and completes
the headed run only after the required genuine observer evidence. Focused tests, typecheck, scoped
ESLint, independent zero-finding review, and evidence gate pass.

## Rollback

Run `git revert --no-edit <accepted-03R-task-range>`. Accepted 02R remains available; Ordinal 04 stays
blocked until a repaired Ordinal 03 is independently accepted.
