# DOCWIZ-FE-STEP2-01 Evidence Summary

Implemented the Step 2 wizard slice in the allowlisted frontend files only.

Verification:
- `cd frontend && npm run lint -- src/api/documents.ts src/api/documents.types.ts src/modules/documents/pages/DocumentWizard.vue` -> pass
- `cd frontend && npm run typecheck` -> pass
- `./scripts/task_validate.sh DOCWIZ-FE-STEP2-01` -> initially failed because `summary.md` was missing, then evidence files were added and the gate was rerun.

Scope notes:
- Step 1 parsing behavior was preserved.
- Step 2 now renders per-case editing fields for `title`, `doc_date`, `ref_no`, `need_reply`, `reply_to_id`, and `extra_data`.
- Batch submit is wired to `POST /api/v1/documents/wizard/batch-create` with Chinese success/error feedback.
- No backend files or non-allowlisted repo files were modified by this task.
