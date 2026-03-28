# FRCOM03-FE-CASE-01 Evidence Summary

- Review-item fix applied: readonly workflow statuses in `CaseEdit.vue` are now disabled in the UI and stripped from the save payload.
- Review-item fix applied: backend `400` split failures are routed into the `agent_split` section, including row-level errors when the backend returns per-row locations.
- Verification passed: targeted lint, `cd frontend && npm run typecheck`, and `./scripts/task_validate.sh FRCOM03-FE-CASE-01`.
- Scope stayed inside the allowlist: `frontend/src/api/cases.ts`, `frontend/src/api/cases.types.ts`, `frontend/src/modules/cases/pages/CaseEdit.vue`, `frontend/src/modules/cases/components/CaseAgentSplitEditor.vue`.
- Exact closure slice completed: `CaseEdit` now honors readonly workflow-status constraints and surfaces agent split business-validation failures in the `agent_split` section.
- Explicit non-closure respected: no `CaseDetail`, commission, router, store, or backend edits.
