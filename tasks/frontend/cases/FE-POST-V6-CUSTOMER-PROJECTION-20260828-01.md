# FE-POST-V6-CUSTOMER-PROJECTION-20260828-01

Status: READY / CONTRACT FROZEN
Risk-Tier: HIGH
Closure-Tags: ["fee", "lifecycle", "lineage", "ui"]
Task-Path: tasks/frontend/cases/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01.md
Chosen runbook: `P0-frontend-heavy-story`

## Approved Inputs

- Approved design commit: `ed61376`.
- Approved plan commit: `27ad872`.
- Design:
  `docs/superpowers/specs/2026-08-28-post-v6-customer-projection-remediation-design.md`.
- Plan:
  `docs/superpowers/plans/2026-08-28-post-v6-customer-projection-remediation.md`.
- User execution choice: Inline Execution in the current main thread, without intermediate
  approval requests unless a frozen stop condition is reached.

## Exact Closure Slice

Implement only the three presentation slices frozen by the approved plan:

1. classify the existing initial-filing document gate as current, historical, or applicability
   unknown from the persisted case business and official stages, without changing the gate fact;
2. make expanded lifecycle history customer-readable by default while retaining exact raw
   identifiers and codes inside collapsed audit disclosures;
3. make real fee obligations customer-readable in both the history lane and case fee tab, reuse
   one latest-obligation projection, and preserve all fee-instruction requests and retry behavior.

## Allowed Files

- `tasks/frontend/cases/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01.md`
- `frontend/src/modules/cases/components/CaseDocumentsTab.vue`
- `frontend/src/modules/cases/components/CaseFeesTab.vue`
- `frontend/src/modules/cases/components/CaseLifecycleOverlay.vue`
- `frontend/src/modules/cases/components/DocumentEvidenceLane.vue`
- `frontend/src/modules/cases/components/LifecycleCenterLane.vue`
- `frontend/src/modules/cases/components/FeeObligationLane.vue`
- `frontend/src/modules/cases/components/lifecycleOverlayDisplay.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-document-gate-applicability.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-document-lane.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-center-lane.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-fee-lane.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-fees-instruction.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/casedock-real-api.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity.live-backend.spec.ts`
- `frontend/tests/demo-v6-fee-ui-parity-contract.mjs`
- `artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/**`

## Verification-Only Files

- `scripts/run_demo_integrated_a_rehearsal.py`

## Explicit Non-Closure

- No backend, API contract, schema, database, migration, seed, runbook, runtime-bundle, or demo
  business-value change.
- No new gate kind, authorization gate, lifecycle transition, fee calculation, balance,
  deadline/legal inference, payment mutation, document fact, lineage fact, retry, or request.
- No presentation DTO, store, composable, rules engine, generic i18n framework, page redesign,
  unrelated English cleanup, rename, reformat, or adjacent refactor.
- No modification, staging, deletion, or absorption of the user-owned untracked
  `docs/postdemo/demo-v6-colleague-clone-start-guide.md`.

## Required TDD Order

1. RED/GREEN: case document-gate applicability matrix, including case metadata failure.
2. RED/GREEN: expanded history document, center, and fee lanes.
3. RED/GREEN: case fee-tab projection while retaining exact PAY/HOLD/ABANDON behavior.
4. Final focused typecheck, scoped ESLint, build, static contract, and combined Playwright suite.
5. One strict V6 rehearsal from committed code, followed by independent HIGH review and atomic
   evidence close.

## Approved Strict V6 Recovery

- The first strict invocation exited with code 2 before product startup because the rehearsal
  CLI requires an absolute `--artifact` path while the approved plan showed a relative path.
- The user approved recovery on 2026-08-29. The committed recovery changes no product behavior,
  inputs, guide content, or evidence meaning; it only resolves the artifact path with
  `"$(pwd)/artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/strict-v6-attempt-1"`.
- The rejected invocation created no attempt/pass directory. The protected colleague guide was
  restored at SHA-256
  `24f9b8acab8ec2e93c50f95991b5f0301dfe4f7438a7f98b84259fa3628a144c`.
- After this recovery is committed, run the corrected strict rehearsal once. A product/runtime
  failure remains a stop condition; do not perform an uncommitted retry.
- That corrected invocation reached the launcher but found the existing V6 worktree services on
  ports 8000 and 5173. The isolated runner therefore could not start, and Playwright received 401
  after reaching the old backend with the new run's temporary credential. This is an environment
  collision, not a product assertion failure.
- The user approved stopping those two verified V6 worktree listeners on 2026-08-29. The failed
  evidence is preserved under `strict-v6-failed-port-conflict-1`; after confirming both ports are
  free and committing this recovery record, one clean strict invocation is authorized.
- The clean isolated run then proved the strict test still required audit hashes and fee
  identifiers to be visible by default, contrary to the approved collapsed-audit projection. The
  user approved a test-only contract synchronization on 2026-08-29: assert raw values hidden in
  the customer view, expand the matching `审计信息`, and then assert exact raw values. The failed
  evidence is preserved under `strict-v6-failed-stale-assertion-1`. No business input, mutation,
  product source, API, database, seed, or runner change is authorized by this amendment.

## Canonical Evidence Commands

```bash
./scripts/evidence_run.sh FE-POST-V6-CUSTOMER-PROJECTION-20260828-01 lint \
  git diff --check -- \
  frontend/src/modules/cases/components/CaseDocumentsTab.vue \
  frontend/src/modules/cases/components/CaseFeesTab.vue \
  frontend/src/modules/cases/components/CaseLifecycleOverlay.vue \
  frontend/src/modules/cases/components/DocumentEvidenceLane.vue \
  frontend/src/modules/cases/components/LifecycleCenterLane.vue \
  frontend/src/modules/cases/components/FeeObligationLane.vue \
  frontend/src/modules/cases/components/lifecycleOverlayDisplay.ts \
  FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-document-gate-applicability.spec.ts \
  FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-document-lane.spec.ts \
  FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-center-lane.spec.ts \
  FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-fee-lane.spec.ts \
  FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-fees-instruction.spec.ts \
  FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/casedock-real-api.spec.ts \
  FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity.live-backend.spec.ts \
  frontend/tests/demo-v6-fee-ui-parity-contract.mjs \
  tasks/frontend/cases/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01.md

./scripts/evidence_run.sh FE-POST-V6-CUSTOMER-PROJECTION-20260828-01 test \
  shasum -a 256 \
  frontend/src/modules/cases/components/CaseDocumentsTab.vue \
  frontend/src/modules/cases/components/CaseFeesTab.vue \
  frontend/src/modules/cases/components/CaseLifecycleOverlay.vue \
  frontend/src/modules/cases/components/DocumentEvidenceLane.vue \
  frontend/src/modules/cases/components/LifecycleCenterLane.vue \
  frontend/src/modules/cases/components/FeeObligationLane.vue \
  frontend/src/modules/cases/components/lifecycleOverlayDisplay.ts \
  FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-document-gate-applicability.spec.ts \
  FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-document-lane.spec.ts \
  FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-center-lane.spec.ts \
  FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-fee-lane.spec.ts \
  FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-fees-instruction.spec.ts \
  FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/casedock-real-api.spec.ts \
  FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity.live-backend.spec.ts \
  frontend/tests/demo-v6-fee-ui-parity-contract.mjs \
  tasks/frontend/cases/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01.md \
  artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/logs/typecheck.log \
  artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/logs/eslint.log \
  artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/logs/build.log \
  artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/logs/static-contract.log \
  artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/playwright/gate-green/index.html \
  artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/playwright/history-green/index.html \
  artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/playwright/fee-green/index.html \
  artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/playwright/focused-final/index.html \
  artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/strict-v6-pass/run1/strict-pass-receipt.json \
  artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/strict-v6-pass/run1/network-errors.json \
  artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/strict-v6-pass/run1/console-errors.json \
  artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/strict-v6-pass/run1/playwright.log

./scripts/evidence_run.sh FE-POST-V6-CUSTOMER-PROJECTION-20260828-01 scope \
  python3 scripts/evidence_scope.py finalize FE-POST-V6-CUSTOMER-PROJECTION-20260828-01
```

## Stop Conditions

Stop and replan if existing payloads cannot produce the approved projection; an approved Chinese
term is missing; exact audit facts require an API/backend/schema/seed change; V6 business inputs
must change; an unlisted source/test path must be edited; or strict V6 reveals an unrelated
business failure.

## Evidence Path

`artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/`
