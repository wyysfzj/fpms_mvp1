# PRODUCT-B-OA-WIZARD-CONTRACT-01

## 1. Scope

This contract freezes the MVP assertion surface for B-wave OA/补正 automation before backend readiness and handler landing.

Covered testcase scope:

- `TC-B-001` OA incoming document registration
- `TC-B-002` official due date deadline override
- `TC-B-003` document row validation
- `TC-B-004` OA reply task generation
- `TC-B-006` OA outgoing reply document
- `TC-B-007` ReplyTo constraints
- `TC-B-008` auto write-off and status restore
- `TC-B-009` OA fee draft
- `TC-B-010` OA official fee pay-list, deferred behind OA fee draft readiness
- `TC-B-011` OA bill and payment
- `TC-B-012` OA service fee commission
- `TC-B-013` NeedReply/Deadline main-screen edit, deferred to separate product task

## 2. Template Code Contract

Skeleton testcase wording remains the semantic source, but backend automation must resolve these aliases to the current backend seed codes:

| Skeleton term | Backend canonical code | Meaning |
| --- | --- | --- |
| `OA_NOTICE` | `OA_IN` | official incoming OA notice document template |
| `OA_REPLY` | `OA_OUT` | outgoing OA reply document template |
| `OA_REPLY_LIMIT` | `OA_REPLY` | OA reply deadline task template |

Automation may use alias resolution in test setup and assertions. Backend seed data does not need to be renamed for this wave.

## 3. OA Incoming MVP

`TC-B-001` MVP assertions:

- a legal case in `SUB_EXAM` can be arranged through the real backend API or backend readiness fixture
- wizard batch create accepts an incoming OA row with canonical template `OA_IN`
- document is created with:
  - `direction=IN`
  - `doc_template_id`
  - `doc_date`
  - `title`
  - `need_reply=true` when template/default says so
- status effect may move the case to `OA1` when configured
- response exposes document id and case id

Deferred branches:

- UI-only draft step state
- NotifyAgent display default
- non-persisted wizard field presentation

## 4. OfficialDueDate Contract

`TC-B-002` requires backend readiness before automation PASS:

- request surface: official due date may be supplied in document `extra_data` with stable key `OfficialDueDate`
- task `base_date` remains the document date
- task `due_date` uses `OfficialDueDate` when present and valid
- internal due date and reminders continue to derive from template offsets unless backend readiness documents a different stable rule

Stable errors:

- invalid official due date in `extra_data`: `DOCUMENT_OFFICIAL_DUE_DATE_INVALID`
- need-reply document without resolvable deadline template/date: `DOCUMENT_REPLY_DEADLINE_REQUIRED`

If backend cannot implement this without schema/model changes, `TC-B-002` stays blocked and the follow-up task must be replanned.

## 5. Document Row Validation Contract

`TC-B-003` MVP assertions:

- blank document title is rejected with `DOCUMENT_TITLE_REQUIRED` or existing schema validation if the endpoint validates before service
- missing/invalid document date is rejected with stable validation semantics
- overlong registration/reference fields are rejected by schema or service validation
- missing required template input fields are rejected only if the selected template defines `input_fields`
- unrelated applicant/case setup failures must not be used as TC-B-003 success

Warning-only UX is deferred unless a backend response field already exists.

## 6. OA Reply Task Contract

`TC-B-004` MVP assertions:

- incoming OA document with canonical template `OA_IN` and deadline template alias `OA_REPLY_LIMIT -> OA_REPLY` creates one open reply task
- task fields are stable:
  - `task_template_code=OA_REPLY`
  - `status=OPEN`
  - `base_date`
  - `due_date`
  - `internal_due_date`
  - reminders when template offsets are configured
  - worker/supervisor if configured by existing backend conventions
- task log records create action

Duplicate prevention:

- repeated generation for the same document/template should not create duplicate open reply tasks.

## 7. ReplyTo Contract

`TC-B-006`, `TC-B-007`, and `TC-B-008` MVP assertions:

- outgoing OA reply uses canonical template `OA_OUT`
- `reply_to_id` must reference an existing document
- `reply_to_id` must belong to the same case as the outgoing reply
- if the outgoing template has `reply_to_template_code`, the referenced document template must match it
- completed/no-reply documents are not valid reply targets when backend readiness exposes a stable rule
- valid reply creates the outgoing document and preserves `reply_to_id`
- valid reply auto write-off marks linked open tasks as done and writes task log
- status restore to `SUB_EXAM` is required only when `OA_OUT.status_restore=SUB_EXAM` is configured

Stable errors:

- nonexistent reply target: `REPLY_TO_DOC_NOT_FOUND`
- wrong-case reply target: `REPLY_TO_CASE_MISMATCH`
- wrong-template reply target: `REPLY_TO_TEMPLATE_MISMATCH`
- no open reply task when a task must be closed: `REPLY_TASK_NOT_FOUND`, if backend chooses blocking behavior

## 8. Attachment Contract

Attachment preview must be side-effect free.

Final attachment generation is in MVP only when an existing template source/rendering/storage path is configured. If no template source exists, automation should assert preview candidates and document metadata, not fake generated binary output.

## 9. OA Fee Contract

`TC-B-009` MVP assertions:

- canonical outgoing OA reply template may define `fee_draft_type=OA_FEE`
- fee rows may come from `fee_item_list`
- generated draft:
  - `draft_type=OA_FEE`
  - `status=OPEN`
  - `currency=CNY` unless case/client specifies otherwise through existing rules
  - service item is present when configured
  - optional government item is present when configured
  - totals equal the sum of generated items

Stable errors:

- malformed fee item list should not crash; backend readiness must either skip invalid rows with stable remark or return `DOCUMENT_FEE_ITEM_LIST_INVALID`
- missing required fee config: `OA_FEE_CONFIG_REQUIRED`

## 10. OA Billing, Payment, Commission Contract

`TC-B-010`, `TC-B-011`, and `TC-B-012` depend on an `OA_FEE` draft:

- pay-list behavior may reuse existing GOV pay-list semantics
- bill generation may reuse existing AR bill semantics
- payment offset may reuse existing bill/payment semantics
- commission base is OA service fee amount
- commission may create or update rows according to existing commission service convention, but automation must assert the convention documented by `BE-B-OA-FINANCE-READINESS-01`

Do not land automation for these cases before `BE-B-OA-FINANCE-READINESS-01` PASS.

## 11. Deferred Branches

The following are deferred and must not be hidden inside handler assertions:

- `TC-B-013` main-screen NeedReply/Deadline edit side effects
- frontend-only warning prompts
- UI draft-step persistence
- binary document rendering when no template source exists
- template/code renaming of backend seed data

Follow-up:

- `PRODUCT-B-NEED-REPLY-DEADLINE-EDIT-CONTRACT-01`

## 12. Automation Assertion Surface

Automation may assert only real backend behavior proven by backend readiness tasks:

- alias-resolved template codes
- document create/list/detail fields
- task create/list/log fields
- reply-to errors and write-off behavior
- fee draft/list/detail fields
- bill/payment/commission fields after backend readiness

Automation must not:

- treat skeleton skip/offline behavior as PASS
- use unrelated applicant/case errors as target failure
- assert deferred product decisions
- invent missing warning envelopes
