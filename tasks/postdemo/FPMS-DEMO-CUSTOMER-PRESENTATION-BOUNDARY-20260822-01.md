# FPMS-DEMO-CUSTOMER-PRESENTATION-BOUNDARY-20260822-01

Status: PENDING_REVIEW
Risk-Class: PROTECTED
Source: Customer feedback and approval in the active Codex task on 2026-08-22.
Dependency: Customer Demo V5 candidate `0a824dbbbf4da85bc07c79e31ea3f77f45dce6f1`.

## Observable Outcome

During the customer-facing V5 journey, both navigation modes omit the internal ABC control page.
The presenter can open a separate unlinked read-only input page to verify the runtime bundle and
the ten zero business counts before the journey. The case lifecycle center displays Simplified
Chinese state labels and does not expose raw state/event codes, source event IDs, customer-decision
gate cards, or customer-decision diagnostic warnings. Non-gate lifecycle warnings remain visible.

## Non-Goals

No backend decision-gate, lifecycle, fee, template, billing, payment, offset, permission, security,
schema, migration, seed, runner, runtime-bundle, or API behavior changes. The existing `/demo/abc`
control route remains available by direct URL for the presenter and canonical rehearsal. No new
route authorization model is introduced. The one non-reproducible browser `Network Error` is
observed separately and is not assigned a speculative retry or business-code fix.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-CUSTOMER-PRESENTATION-BOUNDARY-20260822-01.md`
- `docs/superpowers/plans/2026-08-22-customer-demo-presentation-boundary.md`
- `docs/postdemo/demo-lifecycle-customer-v5-runbook.md`
- `frontend/src/constants/labels.zh.ts`
- `frontend/src/constants/menu.ts`
- `frontend/src/router/index.ts`
- `frontend/src/modules/demo/pages/DemoInputs.vue`
- `frontend/src/modules/cases/components/CaseLifecycleOverlay.vue`
- `frontend/src/modules/cases/components/LifecycleCenterLane.vue`
- `frontend/tests/demo-abc-contract.mjs`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-center-lane.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-gates-warnings.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-overlay-cursor.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-lifecycle-overlay-live.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-a.live-backend.spec.ts`
- `artifacts/FPMS-DEMO-CUSTOMER-PRESENTATION-BOUNDARY-20260822-01/**`

## Verification Commands

- RED then GREEN: `node frontend/tests/demo-abc-contract.mjs`
- RED then GREEN: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-overlay-center-lane.spec.ts src/tests/v8-case-detail-gates-warnings.spec.ts src/tests/v8-case-detail-overlay-cursor.spec.ts --workers=1`
- GREEN: `cd frontend && npm run typecheck`
- GREEN: scoped ESLint for the changed Vue/TypeScript files only.
- Focused live browser verification on the existing fresh V5 run: both menus omit the ABC control,
  `/demo/inputs` is read-only and shows readiness/provenance/counts, and the live case page displays
  Chinese lifecycle labels without decision-gate diagnostics.
- Compatibility assertions in the existing lifecycle-overlay and Integrated A live specs are updated
  from the removed internal/raw presentation to the same customer-safe projection; their runners and
  business contracts are unchanged.
- Independent High review of the exact candidate commit with `P0/P1/P2 = 0/0/0`.

## Evidence Path

- `artifacts/FPMS-DEMO-CUSTOMER-PRESENTATION-BOUNDARY-20260822-01/**`

## Implementation Evidence

- Baseline: `0a824dbbbf4da85bc07c79e31ea3f77f45dce6f1`.
- RED: `node frontend/tests/demo-abc-contract.mjs` returned `1` because the approved
  `DemoInputs.vue` did not yet exist; the focused Playwright contract also reported the expected
  old-presentation failures before product edits.
- GREEN: the Node contract returned `0`; the three focused Playwright files returned `4 passed`;
  frontend typecheck, scoped ESLint, Playwright discovery for both live compatibility specs, and
  `git diff --check` returned `0`.
- Live screen: both navigation modes omitted ABC; the case displayed the four initial lifecycle
  facts in Chinese with no raw codes or customer-decision diagnostics; `/demo/inputs` exposed one
  read-only preflight action and correctly stopped on the already non-empty demo database; the
  payment/offset empty state showed without `Network Error` in the final observation.
- The earlier first-load transport cancellation remains `NOT_REPRODUCED` as a stable code defect;
  no speculative retry or business behavior was added.

## Risk and Rollback

The story is PROTECTED because it changes customer-visible lifecycle presentation while preserving
all stored and API lifecycle facts. Rollback is the single exact story commit. It restores the old
presentation without changing database state or backend decisions.

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-INTEGRATED-A-DEPLOY-PREFLIGHT-20260822-11`
