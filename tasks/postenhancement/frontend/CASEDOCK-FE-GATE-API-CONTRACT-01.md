# CASEDOCK-FE-GATE-API-CONTRACT-01 — Case document gate frontend API contract

## Exact Closure Slice

Add frontend API client functions and TypeScript types for the Case Document Gate real API contract:

- intake material gate preview
- case detail document gate
- document create impact preview
- batch filing final material gate fields returned by existing candidate query

## Explicit Non-Closure

No Vue page or component behavior changes. No backend code. No router/store/menu changes. No visual layout changes. No new dependencies. No static mock data removal from page files in this task.

## Remaining Follow-Up Task IDs

- `CASEDOCK-FE-CASECREATE-API-01`
- `CASEDOCK-FE-CASEDETAIL-API-01`
- `CASEDOCK-FE-DOCIMPACT-API-01`
- `CASEDOCK-FE-BATCHFILING-API-01`
- `CASEDOCK-QA-REALAPI-E2E-01`

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | High. This task owns shared frontend API files `frontend/src/api/cases.ts`, `frontend/src/api/cases.types.ts`, `frontend/src/api/documents.ts`, and `frontend/src/api/documents.types.ts`. |
| prereq_dependency_density | High. Depends on completed backend contract tasks for case intake gate, case detail gate, document impact preview, and batch filing final gate fields. |
| be_fe_coupling | High. These types and client functions must match backend response shapes used by four later Vue page tasks. |
| evidence_cost | Medium. Requires frontend lint, typecheck, build, and task evidence gate. |

chosen_runbook: `P0-prereq-heavy-story`

## Allowed Files

- `tasks/postenhancement/frontend/CASEDOCK-FE-GATE-API-CONTRACT-01.md`
- `frontend/src/api/cases.ts`
- `frontend/src/api/cases.types.ts`
- `frontend/src/api/documents.ts`
- `frontend/src/api/documents.types.ts`
- `artifacts/CASEDOCK-FE-GATE-API-CONTRACT-01/**`

## Verification Commands

- `npm --prefix frontend run lint`
- `npm --prefix frontend run typecheck`
- `npm --prefix frontend run build`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postenhancement/frontend/CASEDOCK-FE-GATE-API-CONTRACT-01.md`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate CASEDOCK-FE-GATE-API-CONTRACT-01`
- `./scripts/task_validate.sh CASEDOCK-FE-GATE-API-CONTRACT-01`

## Evidence Path

- `artifacts/CASEDOCK-FE-GATE-API-CONTRACT-01/`

## Done Definition

- Frontend types expose the four gate/impact contract shapes without adding page behavior.
- Frontend API functions call the real backend endpoints for intake gate, case detail document gate, and document impact preview.
- Batch filing candidate type and mapper include backend `final_material_gate` data.
- Frontend lint, typecheck, build, and task gate pass with evidence.
