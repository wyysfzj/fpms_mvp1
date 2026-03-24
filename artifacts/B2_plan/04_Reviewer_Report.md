# B2 Reviewer Report

## Summary
B2 implementation is correct and complete. All reply chain fields, auto write-off logic, DocTemplate cascade, and test coverage align with the architect plan. Code is clean, well-structured, and all 105 tests pass.

## Quality Gate
- ruff: PASS
- pytest: 105/105 PASS
- migration: PASS (clean `alembic upgrade head`)
- seed: PASS

## File-by-File Review

### alembic/versions/b2_document_reply_chain.py (NEW)
- Status: PASS
- Findings: Correct revision chain (b2_doc_reply_01 → b1_doc_tpl_01). Uses `batch_alter_table` for SQLite compat. Idempotent column checks via `insp.get_columns()`. Self-referential FK created correctly. `downgrade()` is pass (forward-only). No issues.

### app/modules/documents/models.py
- Status: PASS
- Findings: Three new fields added correctly — `reply_to_id` (String(36) FK), `need_reply` (Boolean, server_default="0"), `reply_date` (Date). Self-referential relationships (`replies`, `reply_to_doc`) use proper `foreign_keys` and `remote_side` declarations. Clean placement after existing fields.

### app/modules/documents/schemas.py
- Status: PASS
- Findings: `DocumentCreateIn` gets `reply_to_id` only (need_reply/reply_date set by service logic — correct). `DocumentUpdateIn` gets all three fields. `DocumentOut` gets all three with `= None` defaults. Schema design matches spec.

### app/modules/documents/service.py
- Status: PASS
- Findings: `template = None` before if-block (solves scoping issue from plan). DocTemplate cascade correctly propagates `need_reply` and `status_effect`. Reply chain logic: validates reply_to_id exists (404), finds OPEN tasks linked to replied doc only, closes them with AUTO_WRITEOFF log, sets `reply_date` on original doc. All mutations happen before single `db.commit()`. Imports Task, TaskAction, TaskStatus, `_create_task_log` — no circular dependency.

### app/modules/documents/api.py
- Status: PASS
- Findings: All 4 document endpoints (list, create, get, update) include `reply_to_id`, `need_reply`, `reply_date` in DocumentOut construction. Verified lines 168-170 (list), 242-244 (create), 330-332 (get), 392-394 (update). No endpoints missed.

### app/modules/tasks/enums.py
- Status: PASS
- Findings: `AUTO_WRITEOFF` and `STATUS_CHANGE` added to TaskAction enum. Clean addition, no existing values changed.

### app/modules/tasks/task_generation_service.py
- Status: PASS
- Findings: No B2 changes needed or made. Continues to auto-create tasks for IN documents. Correctly uses `deadline_template_code` from DocTemplate to match TaskTemplate.

### app/modules/cases/api.py
- Status: PASS
- Findings: No B2-specific changes. Case.status is already writable and returned in all endpoints. Status cascade from DocTemplate → Case works via the service layer, not the cases API.

### tests/test_b2_reply_chain.py (NEW)
- Status: PASS
- Findings: 12 comprehensive tests covering all acceptance criteria. Good helper functions (_create_case, _create_document, _get_tasks_for_document, etc.) with unique case_no generation. Tests cover: field presence, full auto write-off lifecycle, no-op when no tasks, selective task closure (only linked doc), 404 on nonexistent reply_to_id, status_effect cascade, need_reply cascade, null cascade no-op, update reply fields, list includes reply fields, AUTO_WRITEOFF task log verification, and full OA lifecycle end-to-end.

## Acceptance Criteria
- [x] reply_to_id, need_reply, reply_date added to t_document
- [x] OUT reply auto-closes OPEN tasks on replied-to doc
- [x] TaskLog AUTO_WRITEOFF created
- [x] reply_date set on original doc
- [x] status_effect cascades to Case.status
- [x] need_reply propagates to Document
- [x] Quality gate passes (ruff, pytest 105/105, migration, seed)

## Iron Rules Compliance
- SQLite compat: PASS — batch_alter_table, server_default=text("0"), UUIDs as String(36), no PG-only functions
- Forward-only migration: PASS — downgrade() is pass
- No scope creep: PASS — only B2-specified changes, no unrelated modifications

## Issues

### Critical
None.

### Minor
1. **`datetime.utcnow()` deprecation** (service.py:141): Deprecated in Python 3.12+ in favor of `datetime.now(UTC)`. Acceptable for current Python 3.11 target, but worth noting for future migration.
2. **Defensive `getattr`** (service.py:110,114): Uses `getattr(template, "need_reply", None)` instead of direct attribute access. Harmless but unnecessary since `template` is typed as `DocTemplate`. Existing pattern in codebase, not a concern.

## Verdict
**APPROVE**
