# BE-B-NEED-REPLY-DEADLINE-EDIT-RULE-01

Task ID: `BE-B-NEED-REPLY-DEADLINE-EDIT-RULE-01`

Story Shape Classification:
- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

chosen_runbook: `P0-prereq-heavy-story`

## Exact Closure Slice

Implement the backend service rule for `TC-B-013` main-screen `NeedReply` and reply-task deadline edits according to `PRODUCT-B-NEED-REPLY-DEADLINE-EDIT-CONTRACT-01`.

This task closes only:

1. Generic document metadata updates do not silently mutate reply tasks.
2. Editing `need_reply` or reply-task deadline fields requires explicit `reply_task_action`.
3. `reply_task_action=CANCEL` cancels the open reply task when `need_reply=false`.
4. `reply_task_action=UPDATE` updates the open reply task deadline fields.
5. Stable business errors are returned when explicit action is missing or no open reply task exists.

## Explicit Non-Closure

Do not implement pytest automation handlers.
Do not modify document wizard create/preview behavior.
Do not modify frontend or skeleton data.
Do not add new task status/action enum values unless the task is stopped and replanned.

## Remaining Follow-Up Task IDs

- `B-AUTO-PY-B-NEED-REPLY-DEADLINE-EDIT-P1-01`

## Allowed Files

- `tasks/backend/business_logic/BE-B-NEED-REPLY-DEADLINE-EDIT-RULE-01.md`
- `backend/app/modules/documents/schemas.py`
- `backend/app/modules/documents/service.py`
- `backend/tests/test_b_need_reply_deadline_edit_rule.py`
- `artifacts/BE-B-NEED-REPLY-DEADLINE-EDIT-RULE-01/**`

## Verification Commands

Run from `backend/`:

```bash
python3 -m ruff check --fix app/modules/documents/schemas.py app/modules/documents/service.py tests/test_b_need_reply_deadline_edit_rule.py
python3 -m ruff format app/modules/documents/schemas.py app/modules/documents/service.py tests/test_b_need_reply_deadline_edit_rule.py
python3 -m ruff check app/modules/documents/schemas.py app/modules/documents/service.py tests/test_b_need_reply_deadline_edit_rule.py
pytest tests/test_b_need_reply_deadline_edit_rule.py -q
pytest tests/test_b2_reply_chain.py -q
```

Task gate:

```bash
./scripts/task_validate.sh BE-B-NEED-REPLY-DEADLINE-EDIT-RULE-01
```

## Evidence Path

- `artifacts/BE-B-NEED-REPLY-DEADLINE-EDIT-RULE-01/results.jsonl`
- `artifacts/BE-B-NEED-REPLY-DEADLINE-EDIT-RULE-01/summary.md`
- `artifacts/BE-B-NEED-REPLY-DEADLINE-EDIT-RULE-01/git/diff.patch`
