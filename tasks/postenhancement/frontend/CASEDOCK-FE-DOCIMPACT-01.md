# CASEDOCK-FE-DOCIMPACT-01 — Document create impact preview UI

## Exact Closure Slice

Add a static, mock-aligned source-file and impact-preview section to the existing document create page so users can see source file status, status impact, deadline/task impact, fee impact, and confirmation warning before registering a document.

## Explicit Non-Closure

No backend/API/schema changes. No changes to document create request payload or save behavior. No attachment upload implementation. No document detail/list changes. No case create or batch filing changes.

## Remaining Follow-Up Task IDs

None

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | Low. Single existing Vue page only. |
| prereq_dependency_density | Low. Depends only on completed static mock page. |
| be_fe_coupling | Low. UI-only static preview. |
| evidence_cost | Medium. Requires frontend checks and visual smoke. |

chosen_runbook: `P0-frontend-heavy-story`

## Allowed Files

- `frontend/src/modules/documents/pages/DocumentCreate.vue`
- `artifacts/CASEDOCK-FE-DOCIMPACT-01/**`

## Verification Commands

- `cd frontend && npm run lint`
- `cd frontend && npm run typecheck`
- `cd frontend && npm run build`
- Playwright or browser smoke showing `/documents/new` loads and the “影响预览” section is visible.
- `/Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate CASEDOCK-FE-DOCIMPACT-01`

## Evidence Path

- `artifacts/CASEDOCK-FE-DOCIMPACT-01/`
