# CASEDOCK-FE-BATCHFILING-01 — Batch filing final material gate UI

## Exact Closure Slice

Add static, mock-aligned final-material gate UI to the existing case batch filing page: material count, missing item, gate conclusion, hard-block visual state, post-completion audit card, and execution preview.

## Explicit Non-Closure

No backend/API/schema changes. No changes to batch filing submit request payload or selected case ID semantics. No automatic document generation. No case create/detail/document create UI changes.

## Remaining Follow-Up Task IDs

None

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | Low. Single existing Vue page only. |
| prereq_dependency_density | Low. Depends only on completed static mock page. |
| be_fe_coupling | Low. UI-only static gate display around existing candidates. |
| evidence_cost | Medium. Requires frontend checks and visual smoke. |

chosen_runbook: `P0-frontend-heavy-story`

## Allowed Files

- `frontend/src/modules/cases/pages/CaseBatchFiling.vue`
- `artifacts/CASEDOCK-FE-BATCHFILING-01/**`

## Verification Commands

- `cd frontend && npm run lint`
- `cd frontend && npm run typecheck`
- `cd frontend && npm run build`
- Playwright or browser smoke showing `/cases/batch-filing` or the existing batch filing route loads and the “最终材料门禁” UI is visible.
- `/Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate CASEDOCK-FE-BATCHFILING-01`

## Evidence Path

- `artifacts/CASEDOCK-FE-BATCHFILING-01/`
