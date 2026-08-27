# FPMS-DEMO-V6-UI-PARITY-OFFLINE-FONTS-20260827-08AB

Risk: MEDIUM
Closure-Tags: ui
Runbook: P0-single-lane-story
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-OFFLINE-FONTS-20260827-08AB.md

## Design references

- `frontend/index.html`
- `frontend/src/styles/variables.css`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity.live-backend.spec.ts`

## Exact Closure Slice

Remove the Google Fonts stylesheet from the runtime SPA entry point so the local customer demo
does not make any `fonts.googleapis.com` or `fonts.gstatic.com` request. Existing CSS system-font
fallbacks remain the only font behavior.

## Scope decision — FIXED

- `shared_file_density`: low
- `prereq_dependency_density`: low
- `be_fe_coupling`: frontend-only static entry point
- `evidence_cost`: low
- `chosen_runbook`: `P0-single-lane-story`
- Delete exactly the external font stylesheet link from `frontend/index.html`.
- Add one focused runtime-entry contract assertion for both Google Fonts domains.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-OFFLINE-FONTS-20260827-08AB.md`
- `frontend/index.html`
- `frontend/tests/demo-v6-lifecycle-ui-contract.mjs`

## Explicit Non-Closure

- No font download, vendoring, bundling, preload, cache, service worker, or CSP change.
- No CSS variable, font stack, layout, page, backend, API, or Playwright logic change.
- No filtering or suppression of console/network errors.
- No Stage 07 or later implementation.

## Verification Commands

1. Focused RED then GREEN: `node frontend/tests/demo-v6-lifecycle-ui-contract.mjs`.
2. Scoped ESLint for `frontend/tests/demo-v6-lifecycle-ui-contract.mjs`.
3. Exact scope and `git diff --check`.
4. Independent findings-only review with `Verdict: APPROVED`, `P0: 0`, `P1: 0`, `P2: 0`.
5. Atomic evidence validation after review.

## Evidence Path

`artifacts/FPMS-DEMO-V6-UI-PARITY-OFFLINE-FONTS-20260827-08AB/`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-UI-PARITY-STRICT-E2E-20260826-08`

## Prompt

Implement only the fixed closure above. Do not add optional behavior or absorb any follow-up.
