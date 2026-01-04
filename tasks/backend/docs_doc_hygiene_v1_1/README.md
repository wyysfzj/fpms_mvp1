# FPMS — Documentation Fix Atomic Task Pack v1.1 (Path-aligned)

Purpose:
Align documentation with the implemented MVP1 execution order and Phase 3/3-EXT/3.5 deliverables.

Key adjustments vs v1:
- Replace non-existent `docs/execution_order_v2.md` with updates to `docs/README.md`
- Replace non-existent `docs/llm_adapter_matrix.md` with references in `docs/README.md`

Execution prerequisites:
- `tasks/backend/README.md` exists (confirmed)
- Phase 3.5 task pack has been merged (tasks/backend/business_logic)

Execution order (do NOT change):
1) DOC-FIX-01_update_docs_readme_execution_order_and_lint_safe_refs
2) DOC-FIX-02_update_tasks_backend_readme_include_phase3_5
3) DOC-FIX-03_update_permissions_matrix_phase3ext_phase3_5
4) DOC-FIX-04_update_backend_architecture_doc_render_and_auto_task

Each task edits exactly ONE file.
