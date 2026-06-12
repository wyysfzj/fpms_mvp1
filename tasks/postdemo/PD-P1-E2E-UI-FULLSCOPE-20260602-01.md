# PD-P1-E2E-UI-FULLSCOPE-20260602-01 — P1 full-scope E2E UI regression suite

## Exact Closure Slice

Create and verify a Playwright E2E UI regression suite that covers the P1 Functional Spec full scope from the generated test design: official fields, filing-preparation gate/checklist, OA reply package/file roles, receipt archive hard gate and metadata, fee linkage/pay-list boundaries, letter handoff, navigation/status display, and explicit P1 non-scope boundaries.

This is one stable workflow QA slice because it verifies the completed P1 application as a single staff-facing official-workflow regression suite; it does not implement or modify separate product features.

## Explicit Non-Closure

No backend product code, frontend product code, database schema/migration, business rule, permission, CPC/OA direct submit, official-site RPA, auto-signature, auto-payment, receipt auto-download/OCR, Longxia API/mail sending, or customer-facing document template implementation.

## Remaining Follow-Up Task IDs

None unless diagnose identifies a product defect or untestable requirement; any such issue must be split into a new focused task.

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | Medium. Allows only Playwright test files/helpers, planning artifacts, and task evidence. |
| prereq_dependency_density | Medium. Depends on a running frontend dev/preview server, completed P1 implementation, and deterministic API-contract fixtures. It does not depend on local backend DB seeding because the current Python runtime is not a stable E2E prerequisite. |
| be_fe_coupling | Medium for verification. The suite drives real frontend pages with mocked API contracts that mirror completed P1 backend responses; persisted backend rules remain covered by existing P1 API evidence and are referenced in the coverage ledger. |
| evidence_cost | High. Requires E2E execution, frontend lint/type/build checks, task gate, evidence validation, and coverage ledger. |

chosen_runbook: `P0-frontend-heavy-story`

## Allowed Files

- `tasks/postdemo/PD-P1-E2E-TEST-MANIFEST-20260602-01.md`
- `tasks/postdemo/PD-P1-E2E-UI-FULLSCOPE-20260602-01.md`
- `artifacts/PD-P1-E2E-TEST-DESIGN-20260602-01/**`
- `artifacts/PD-P1-E2E-UI-FULLSCOPE-20260602-01/**`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/package.json`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/pd-p1.full-scope.spec.ts`

## Verification Commands

- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/PD-P1-E2E-UI-FULLSCOPE-20260602-01.md`
- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npm run test:pd-p1`
- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && node ./node_modules/.bin/playwright test src/tests/pd-p1.full-scope.spec.ts --list`
- `cd frontend && npm run typecheck`
- `cd frontend && npm run build`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate PD-P1-E2E-UI-FULLSCOPE-20260602-01`
- `./scripts/task_validate.sh PD-P1-E2E-UI-FULLSCOPE-20260602-01`

## Evidence Path

- `artifacts/PD-P1-E2E-UI-FULLSCOPE-20260602-01/`

## Done Definition

- `artifacts/PD-P1-E2E-TEST-DESIGN-20260602-01/test_design.md` contains P1 full-scope test cases with FS mapping, fixture, UI path, steps, assertions, negative/boundary expectations, automation status, evidence expectations, and residual risks.
- Playwright suite verifies the full P1 staff-facing workflow using real UI pages and API-contract fixtures for stable full-scope UI regression.
- Fixture setup is test-only, lives in the Playwright spec, and does not modify product code.
- E2E assertions cover official-field maintenance entry, filing-preparation field/file gates, official-page checklist actions, OA reply package and file roles, receipt hard gate and metadata, fee linkage/pay-list boundary, letter handoff, and P1 forbidden automation claims.
- `artifacts/PD-P1-E2E-UI-FULLSCOPE-20260602-01/full_scope_coverage_ledger.md` maps each P1 acceptance area to automated E2E evidence, existing API evidence, manual/P2/P3 exclusions, and residual risk.
- Required evidence files exist, verification commands pass, and task gates pass.
