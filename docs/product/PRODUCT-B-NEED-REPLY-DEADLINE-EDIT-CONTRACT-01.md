# PRODUCT-B-NEED-REPLY-DEADLINE-EDIT-CONTRACT-01

## 1. Scope

This contract freezes the `TC-B-013` MVP product/backend assertion surface for editing `NeedReply` and reply-task deadlines from the document main screen.

## 2. Product Decision

`TC-B-013` is not an automation-only task. The MVP backend contract is:

- document update may edit `need_reply`
- document update may edit document metadata
- reply task update/cancel side effects are not implicit unless the request explicitly declares the intended task action

## 3. Required Backend Rule Task

Follow-up `BE-B-NEED-REPLY-DEADLINE-EDIT-RULE-01` must implement one focused service rule:

- Request surface must provide an explicit action, e.g. `reply_task_action=UPDATE|CANCEL|NONE`
- If `need_reply=false` and an open reply task exists:
  - `CANCEL` marks the task `CANCELLED`
  - task log action is `DOCUMENT_REPLY_TASK_CANCELLED`
- If deadline fields are edited and an open reply task exists:
  - `UPDATE` updates `due_date`, `internal_due_date`, and reminders
  - task log action is `DOCUMENT_REPLY_TASK_UPDATE_REQUIRED` or a stable update action chosen by the task
- Without explicit action, backend should reject ambiguous side effects with `DOCUMENT_REPLY_TASK_ACTION_REQUIRED`

## 4. Deferred Branches

The following are deferred:

- frontend modal wording
- UI-only warning prompts
- bulk document edit behavior
- changing historical DONE tasks
- reopening cancelled tasks

## 5. Automation Assertion Surface

Automation for `TC-B-013` may assert only after `BE-B-NEED-REPLY-DEADLINE-EDIT-RULE-01` PASS:

- edit `NeedReply=false` with explicit cancel action
- open task becomes cancelled
- task log exists
- deadline edit with explicit update action updates the open task
- ambiguous edit returns stable error

Do not fake `TC-B-013` PASS with generic `PUT /documents/{id}` metadata updates.
