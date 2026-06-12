# PD-P1-E2E-LIVE-BACKEND-20260602-01 — P1 full-scope E2E on live backend

## Exact Closure Slice

Switch the P1 full-scope UI E2E primary command from API contract fixtures to a live backend-backed workflow. The task creates a deterministic test-only backend fixture, drives real Vue pages through real backend API calls, and runs the full local loop: Alembic head, dev seed, P1 live fixture seed, backend server, frontend server, Playwright, typecheck/build, evidence gate, and task gate.

## Explicit Non-Closure

No backend product behavior changes, no frontend product behavior changes, no database migration/schema edits, no CPC/OA direct submit, no official-site RPA, no auto-signature, no auto-payment, no receipt auto-download/OCR, and no Longxia email/API implementation.

## Remaining Follow-Up Task IDs

None unless live-backend E2E exposes a product defect; any such defect must be split into a focused follow-up task.

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | Medium. Touches Playwright package scripts and test-only support/spec files. |
| prereq_dependency_density | High. Requires migrated SQLite DB, seeded dev auth, deterministic P1 fixture, live backend, and live frontend. |
| be_fe_coupling | High for verification. The test intentionally crosses frontend pages and backend APIs, but edits remain test-only. |
| evidence_cost | High. Requires E2E execution plus frontend typecheck/build, backend migration/seed checks, evidence validate, and task gate. |

chosen_runbook: `P0-frontend-heavy-story`

## Allowed Files

- `tasks/postdemo/PD-P1-E2E-LIVE-BACKEND-20260602-01.md`
- `artifacts/PD-P1-E2E-LIVE-BACKEND-20260602-01/**`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/package.json`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/pd-p1.live-backend.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/pdP1LiveSeed.py`

## Verification Commands

- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/PD-P1-E2E-LIVE-BACKEND-20260602-01.md`
- `cd backend && .venv/bin/alembic upgrade head`
- `cd backend && PYTHONPATH=. .venv/bin/python scripts/seed_dev.py`
- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && ../../backend/.venv/bin/python src/support/pdP1LiveSeed.py`
- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npm run test:pd-p1`
- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && node ./node_modules/.bin/playwright test src/tests/pd-p1.live-backend.spec.ts --list`
- `cd frontend && npm run typecheck`
- `cd frontend && npm run build`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate PD-P1-E2E-LIVE-BACKEND-20260602-01`
- `./scripts/task_validate.sh PD-P1-E2E-LIVE-BACKEND-20260602-01`

## Evidence Path

- `artifacts/PD-P1-E2E-LIVE-BACKEND-20260602-01/`

## Done Definition

- `test:pd-p1` runs the live-backend P1 full-scope E2E spec.
- The live fixture seed is idempotent and deterministic for the P1 E2E IDs.
- Playwright logs into the live backend and drives real UI pages without route-level API mocks.
- E2E assertions cover official fields, filing-preparation gates/checklist, OA reply file roles, receipt archive hard gate/metadata, fee linkage/pay-list boundary, letter handoff, and P1 non-scope boundary claims.
- Required evidence files exist and gates pass.
