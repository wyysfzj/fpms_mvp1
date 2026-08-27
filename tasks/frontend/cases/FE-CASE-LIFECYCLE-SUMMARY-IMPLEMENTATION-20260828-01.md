# FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01

Status: READY / CONTRACT FROZEN
Risk-Tier: HIGH
Closure-Tags: ["fee", "lifecycle", "lineage", "ui"]
Task-Path: tasks/frontend/cases/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01.md

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: none
- evidence_cost: medium
- chosen_runbook: P0-frontend-heavy-story

## Approved Inputs

- `docs/superpowers/specs/2026-08-28-case-lifecycle-three-track-summary-design.md`
- `docs/superpowers/plans/2026-08-28-case-lifecycle-three-track-summary.md`
- User selected inline execution approach 1 in the current Codex task dated 2026-08-28.

## Exact Closure Slice

Implement the approved customer-readable, current-first three-track summary on the case-detail
page. Add one stateless summary card, one shared Chinese display-mapping module, one explicit
collapsed-history disclosure, stable customer-visible warning deduplication, honest incomplete
pagination messaging, and the approved responsive three-column/one-column layout. Preserve the
existing detailed document, lifecycle, and fee lanes behind the disclosure and preserve their V6
business values.

## Explicit Non-Closure

No backend, API or API type, schema, store, lifecycle state machine, lifecycle transition, fee
calculation, monetary aggregation, customer balance, permission, seed/demo data, runbook, frozen
V6 worktree, or unrelated UI cleanup is changed. No later overlay page is fetched automatically,
no next action is inferred from status, and no customer decision gate or raw English status is
exposed.

## Remaining Follow-Up Task IDs

None.

## Allowed Files

- `frontend/src/modules/cases/components/CaseLifecycleOverlay.vue`
- `frontend/src/modules/cases/components/LifecycleSummaryCard.vue`
- `frontend/src/modules/cases/components/lifecycleOverlayDisplay.ts`
- `frontend/src/modules/cases/components/DocumentEvidenceLane.vue`
- `frontend/src/modules/cases/components/LifecycleCenterLane.vue`
- `frontend/src/modules/cases/components/FeeObligationLane.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-three-lane.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-overlay-cursor.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-gates-warnings.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-center-lane.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-document-lane.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-fee-lane.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-lifecycle-overlay-live.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity.live-backend.spec.ts`
- `tasks/frontend/cases/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01.md`
- `artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01 lint git diff --check -- frontend/src/modules/cases/components/CaseLifecycleOverlay.vue frontend/src/modules/cases/components/LifecycleSummaryCard.vue frontend/src/modules/cases/components/lifecycleOverlayDisplay.ts frontend/src/modules/cases/components/DocumentEvidenceLane.vue frontend/src/modules/cases/components/LifecycleCenterLane.vue frontend/src/modules/cases/components/FeeObligationLane.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-three-lane.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-overlay-cursor.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-gates-warnings.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-center-lane.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-document-lane.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-fee-lane.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-lifecycle-overlay-live.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity.live-backend.spec.ts tasks/frontend/cases/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01.md
./scripts/evidence_run.sh FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01 test shasum -a 256 frontend/src/modules/cases/components/CaseLifecycleOverlay.vue frontend/src/modules/cases/components/LifecycleSummaryCard.vue frontend/src/modules/cases/components/lifecycleOverlayDisplay.ts frontend/src/modules/cases/components/DocumentEvidenceLane.vue frontend/src/modules/cases/components/LifecycleCenterLane.vue frontend/src/modules/cases/components/FeeObligationLane.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-three-lane.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-overlay-cursor.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-gates-warnings.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-center-lane.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-document-lane.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-fee-lane.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-lifecycle-overlay-live.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity.live-backend.spec.ts tasks/frontend/cases/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01.md artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/verification.md artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/logs/typecheck.log artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/logs/eslint.log artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/logs/build.log artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/logs/v6-static-contract.log artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/playwright/mapping-baseline/index.html artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/playwright/mapping-after/index.html artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/playwright/focused-red/index.html artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/playwright/focused-green/index.html artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/playwright/compatibility/index.html artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/playwright/live-overlay/index.html artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/strict-v6-pass/run1/strict-pass-receipt.json artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/strict-v6-pass/run1/network-errors.json artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/strict-v6-pass/run1/console-errors.json artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/strict-v6-pass/run1/playwright.log
./scripts/evidence_run.sh FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01 scope python3 scripts/evidence_scope.py finalize FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01
```

## Evidence Path

- `artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/task.json`
- `artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/results.jsonl`
- `artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/summary.md`
- `artifacts/FE-CASE-LIFECYCLE-SUMMARY-IMPLEMENTATION-20260828-01/git/diff.patch`
