# CASEDOCK-PROD-MANIFEST-01 — Production minimal UI follow-up manifest

## Exact Closure Slice

Create the planning-only production follow-up manifest and atomic frontend task files for implementing the Case Document Gate Minimal UI Mock in existing Vue pages.

## Explicit Non-Closure

No production Vue code changes. No backend/API/schema changes. No automation code changes. No execution of the listed follow-up implementation tasks.

## Remaining Follow-Up Task IDs

- `CASEDOCK-FE-CASECREATE-01`
- `CASEDOCK-FE-CASEDETAIL-01`
- `CASEDOCK-FE-DOCIMPACT-01`
- `CASEDOCK-FE-BATCHFILING-01`

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | Medium. Four independent existing Vue pages/components; no shared API client changes in this manifest. |
| prereq_dependency_density | Medium. Implementation depends on the completed static mock pages and existing case/document pages. |
| be_fe_coupling | Low for this batch. The follow-up tasks are UI-only minimal mock-aligned additions and explicitly avoid backend/API/schema changes. |
| evidence_cost | Medium. Each task requires focused Vue checks plus Playwright static/user-flow evidence where applicable. |

chosen_runbook: `P0-frontend-heavy-story`

## Batch Manifest

| Wave | Task file path | Owner role | Allowed files | Required verification | Dependency notes | Exact closure slice | Explicit non-closure | Remaining follow-up task ids | Done definition |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `tasks/postenhancement/frontend/CASEDOCK-FE-CASECREATE-01.md` | frontend worker | `frontend/src/modules/cases/pages/CaseCreate.vue`, `artifacts/CASEDOCK-FE-CASECREATE-01/**` | task-scoped Vue lint/build/typecheck evidence and screenshot/smoke evidence | Depends on `11_01_min_case_create_intake_gate.html` mock | Add static收案文件与材料核验 UI section to existing case create page | No save-payload/API/schema/backend changes | None | Existing create flow remains usable and section visually matches mock intent |
| 1 | `tasks/postenhancement/frontend/CASEDOCK-FE-CASEDETAIL-01.md` | frontend worker | `frontend/src/modules/cases/components/CaseDocumentsTab.vue`, `artifacts/CASEDOCK-FE-CASEDETAIL-01/**` | task-scoped Vue lint/build/typecheck evidence and screenshot/smoke evidence | Depends on `11_02_min_case_detail_file_event_tab.html` mock | Upgrade existing case documents tab with current材料摘要、建议动作、事件状态 UI | No new routes/API/schema/backend changes | None | Existing document list/create route still works and added section is visible |
| 2 | `tasks/postenhancement/frontend/CASEDOCK-FE-DOCIMPACT-01.md` | frontend worker | `frontend/src/modules/documents/pages/DocumentCreate.vue`, `artifacts/CASEDOCK-FE-DOCIMPACT-01/**` | task-scoped Vue lint/build/typecheck evidence and screenshot/smoke evidence | Depends on `11_03_min_document_create_impact_preview.html` mock | Add source-file and impact-preview UI to existing document create form | No create-payload/API/schema/backend changes | None | Existing document registration flow remains usable and impact preview is visible |
| 2 | `tasks/postenhancement/frontend/CASEDOCK-FE-BATCHFILING-01.md` | frontend worker | `frontend/src/modules/cases/pages/CaseBatchFiling.vue`, `artifacts/CASEDOCK-FE-BATCHFILING-01/**` | task-scoped Vue lint/build/typecheck evidence and screenshot/smoke evidence | Depends on `11_04_min_batch_filing_final_gate.html` mock | Add final-material gate columns and execution preview to existing batch filing page | No submit-payload/API/schema/backend changes | None | Existing submit flow remains usable and hard-block row is visually disabled |

## Serialized Shared-File Decisions

- No two listed tasks edit the same production file in the same wave.
- No shared frontend API client, router, store, constants, or backend file is in scope.
- If implementation discovers a required shared API/type/backend prerequisite, stop and create a new task; do not stretch any listed task.

## Allowed Files

- `tasks/postenhancement/frontend/CASEDOCK-PROD-MANIFEST-01.md`
- `tasks/postenhancement/frontend/CASEDOCK-FE-CASECREATE-01.md`
- `tasks/postenhancement/frontend/CASEDOCK-FE-CASEDETAIL-01.md`
- `tasks/postenhancement/frontend/CASEDOCK-FE-DOCIMPACT-01.md`
- `tasks/postenhancement/frontend/CASEDOCK-FE-BATCHFILING-01.md`
- `artifacts/CASEDOCK-PROD-MANIFEST-01/**`

## Verification Commands

- `/Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task <task-file>`
- `npm run lint` from `frontend`
- `npm run typecheck` from `frontend`
- `npm run build` from `frontend`
- Task-specific Playwright smoke or static screenshot evidence after each implementation task.
- `/Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate <TASK-ID>`

## Evidence Path

- `artifacts/CASEDOCK-PROD-MANIFEST-01/`
