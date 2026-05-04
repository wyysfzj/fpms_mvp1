# CASEDOCK-FE-CASEDETAIL-01 — Case detail document material tab UI

## Exact Closure Slice

Upgrade the existing case documents tab to show current-node material requirements, matched files, gate conclusion, suggested actions, and document event status while preserving the existing document list and “登记往来文件” action.

## Explicit Non-Closure

No backend/API/schema changes. No new route, router entry, store, or shared API client change. No changes to case detail overview tab. No document create impact preview changes. No batch filing changes.

## Remaining Follow-Up Task IDs

None

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | Low. Single existing Vue component only. |
| prereq_dependency_density | Low. Depends only on completed static mock page and existing document tab. |
| be_fe_coupling | Low. UI-only static summary around existing fetched documents. |
| evidence_cost | Medium. Requires frontend checks and visual smoke. |

chosen_runbook: `P0-frontend-heavy-story`

## Allowed Files

- `frontend/src/modules/cases/components/CaseDocumentsTab.vue`
- `artifacts/CASEDOCK-FE-CASEDETAIL-01/**`

## Verification Commands

- `cd frontend && npm run lint`
- `cd frontend && npm run typecheck`
- `cd frontend && npm run build`
- Playwright or browser smoke showing a case detail documents tab loads and the “当前节点文件材料” section is visible.
- `/Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate CASEDOCK-FE-CASEDETAIL-01`

## Evidence Path

- `artifacts/CASEDOCK-FE-CASEDETAIL-01/`
