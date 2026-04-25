# BATCH-B-BLOCKER-DRAIN-01

Batch ID: `BATCH-B-BLOCKER-DRAIN-01`

Story Shape Classification:
- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: high

chosen_runbook: `P0-prereq-heavy-story`

## Goal

Drain blockers discovered by `BATCH-B-READINESS-GATE-01` before B-wave automation landing.

## Critical Rules

- One atomic task equals one exact task file path.
- Do not implement pytest automation handlers in blocker drain.
- Do not modify `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_b.py`.
- Shared backend files and SQLite write tests must be serialized.
- Product ambiguity must be closed by PRODUCT tasks before backend guessing.

## Execution Order

### Wave 1: Test Maintenance

Task ID: `BE-B-DOCUMENT-TEST-MAINT-01`

Task file: `tasks/backend/test_maintenance/BE-B-DOCUMENT-TEST-MAINT-01.md`

Type: test maintenance

Exact closure slice:
- Update stale B/document backend tests so helper-created cases include valid applicants.
- Preserve existing document wizard, reply-chain, fee-linking, task-generation, and attachment business assertions.
- Do not weaken applicant rules.

Allowed files:
- `tasks/backend/test_maintenance/BE-B-DOCUMENT-TEST-MAINT-01.md`
- `backend/tests/test_b2_reply_chain.py`
- `backend/tests/test_b3_fee_linking.py`
- `backend/tests/test_document_wizard_batch_create.py`
- `backend/tests/test_document_wizard_task_preview.py`
- `backend/tests/test_document_wizard_fee_preview.py`
- `backend/tests/test_document_wizard_attachment_preview.py`
- `artifacts/BE-B-DOCUMENT-TEST-MAINT-01/**`

Verification from `backend/`:
- `python3 -m ruff check --fix tests/test_b2_reply_chain.py tests/test_b3_fee_linking.py tests/test_document_wizard_batch_create.py tests/test_document_wizard_task_preview.py tests/test_document_wizard_fee_preview.py tests/test_document_wizard_attachment_preview.py`
- `python3 -m ruff format tests/test_b2_reply_chain.py tests/test_b3_fee_linking.py tests/test_document_wizard_batch_create.py tests/test_document_wizard_task_preview.py tests/test_document_wizard_fee_preview.py tests/test_document_wizard_attachment_preview.py`
- `python3 -m ruff check tests/test_b2_reply_chain.py tests/test_b3_fee_linking.py tests/test_document_wizard_batch_create.py tests/test_document_wizard_task_preview.py tests/test_document_wizard_fee_preview.py tests/test_document_wizard_attachment_preview.py`
- `pytest tests/test_b2_reply_chain.py tests/test_b3_fee_linking.py tests/test_document_wizard_batch_create.py tests/test_document_wizard_task_preview.py tests/test_document_wizard_fee_preview.py tests/test_document_wizard_attachment_preview.py -q`
- `./scripts/task_validate.sh BE-B-DOCUMENT-TEST-MAINT-01`

Status: `EXECUTED_PASS`

### Wave 2: Product Contract Freeze

Task ID: `BE-B-DOCUMENT-REPLYTO-NOTFOUND-RULE-01`

Task file: `tasks/backend/business_logic/BE-B-DOCUMENT-REPLYTO-NOTFOUND-RULE-01.md`

Type: backend behavior blocker discovered during Wave 1 verification

Status: `EXECUTED_PASS`

Exact closure slice:
- Validate document `reply_to_id` before insert/flush.
- Return stable `REPLY_TO_DOC_NOT_FOUND` with HTTP 404 when an OUT reply references a nonexistent document.
- Preserve valid reply-chain auto write-off behavior.

Allowed files:
- `tasks/backend/business_logic/BE-B-DOCUMENT-REPLYTO-NOTFOUND-RULE-01.md`
- `backend/app/modules/documents/service.py`
- `backend/tests/test_b2_reply_chain.py`
- `artifacts/BE-B-DOCUMENT-REPLYTO-NOTFOUND-RULE-01/**`

Verification from `backend/`:
- `python3 -m ruff check app/modules/documents/service.py tests/test_b2_reply_chain.py`
- `pytest tests/test_b2_reply_chain.py::test_reply_to_nonexistent_document_404 -q`
- `pytest tests/test_b2_reply_chain.py -q`
- `./scripts/task_validate.sh BE-B-DOCUMENT-REPLYTO-NOTFOUND-RULE-01`

Task ID: `PRODUCT-B-OA-WIZARD-CONTRACT-01`

Task file: `tasks/product/PRODUCT-B-OA-WIZARD-CONTRACT-01.md`

Type: product contract

Exact closure slice:
- Freeze B-wave MVP assertion surface for OA document wizard, template names, task template names, official due date override, reply-to constraints, attachment generation, OA fee draft, OA bill/payment, and OA commission.
- Resolve skeleton/backend naming mismatch:
  - skeleton uses `OA_NOTICE`, `OA_REPLY`, `OA_REPLY_LIMIT`
  - backend currently seeds `OA_IN`, `OA_OUT`, `OA_REPLY`
- Define deferred branches and stable error codes.

Allowed files:
- `tasks/product/PRODUCT-B-OA-WIZARD-CONTRACT-01.md`
- `docs/product/PRODUCT-B-OA-WIZARD-CONTRACT-01.md`
- `artifacts/PRODUCT-B-OA-WIZARD-CONTRACT-01/**`

Verification:
- `test -f tasks/product/PRODUCT-B-OA-WIZARD-CONTRACT-01.md`
- `test -f docs/product/PRODUCT-B-OA-WIZARD-CONTRACT-01.md`
- `rg -n "OA_NOTICE|OA_IN|OA_REPLY_LIMIT|OA_REPLY|ReplyTo|OfficialDueDate|OA_FEE|deferred" docs/product/PRODUCT-B-OA-WIZARD-CONTRACT-01.md`
- `./scripts/task_validate.sh PRODUCT-B-OA-WIZARD-CONTRACT-01`

Status: `EXECUTED_PASS`

### Wave 3: Backend Readiness / Rule Tasks

Only start after Wave 1 PASS and relevant product contract PASS.

Task ID: `BE-B-OA-WIZARD-READINESS-01`

Task file: `tasks/backend/business_logic/BE-B-OA-WIZARD-READINESS-01.md`

Type: backend readiness/rule

Exact closure slice:
- Verify or minimally fix the OA incoming document wizard path needed by `TC-B-001`, `TC-B-003`, and `TC-B-004`:
  - document batch create
  - template defaults
  - required document row validation
  - task preview/create fields
  - status effect
  - task log create

Allowed files:
- `tasks/backend/business_logic/BE-B-OA-WIZARD-READINESS-01.md`
- `backend/app/modules/documents/service.py`
- `backend/app/modules/documents/api.py`
- `backend/app/modules/documents/schemas.py`
- `backend/tests/test_b_oa_wizard_readiness.py`
- `artifacts/BE-B-OA-WIZARD-READINESS-01/**`

Status: `EXECUTED_PASS`

Task ID: `BE-B-OA-REPLY-READINESS-01`

Task file: `tasks/backend/business_logic/BE-B-OA-REPLY-READINESS-01.md`

Type: backend readiness/rule

Exact closure slice:
- Verify or minimally fix OA reply path needed by `TC-B-006`, `TC-B-007`, and `TC-B-008`:
  - same-case ReplyTo enforcement
  - reply-to-template enforcement
  - reply document creation
  - task auto write-off
  - status restore

Allowed files:
- `tasks/backend/business_logic/BE-B-OA-REPLY-READINESS-01.md`
- `backend/app/modules/documents/service.py`
- `backend/app/modules/documents/api.py`
- `backend/app/modules/documents/schemas.py`
- `backend/tests/test_b_oa_reply_readiness.py`
- `artifacts/BE-B-OA-REPLY-READINESS-01/**`

Status: `EXECUTED_PASS`

Task ID: `BE-B-OA-FINANCE-READINESS-01`

Task file: `tasks/backend/business_logic/BE-B-OA-FINANCE-READINESS-01.md`

Type: backend readiness/rule

Exact closure slice:
- Verify or minimally fix OA fee draft, OA bill, payment offset, CaseReceipt, and commission readiness for `TC-B-009`, `TC-B-010`, `TC-B-011`, and `TC-B-012`.

Allowed files:
- `tasks/backend/business_logic/BE-B-OA-FINANCE-READINESS-01.md`
- `backend/app/modules/documents/service.py`
- `backend/app/modules/fees/service.py`
- `backend/app/modules/billing/service.py`
- `backend/app/modules/commission/service.py`
- `backend/tests/test_b_oa_finance_readiness.py`
- `artifacts/BE-B-OA-FINANCE-READINESS-01/**`

Status: `EXECUTED_BLOCKED`

Blocker:
- OA finance combines OA fee draft, pay-list/payment, AR bill/payment offset, and commission. Split into:
  - `BE-B-OA-FEE-DRAFT-READINESS-01`
  - `BE-B-OA-BILL-PAYMENT-READINESS-01`
  - `BE-B-OA-COMMISSION-READINESS-01`

Task ID: `BE-B-NEED-REPLY-DEADLINE-EDIT-CONTRACT-OR-RULE-01`

Task file: `tasks/backend/business_logic/BE-B-NEED-REPLY-DEADLINE-EDIT-CONTRACT-OR-RULE-01.md`

Type: product/backend blocker

Status: `PRODUCT_DECISION_REQUIRED`

Reason:
- `TC-B-013` expects main-screen edits to `NeedReply` and `Deadline` with update/cancel task side effects.
- Current backend exposes generic `PUT /documents/{id}` fields, but the product interaction and stable side-effect/error semantics are not frozen.

## Automation Landing Dependencies

Do not start B automation landing until:

- `BE-B-DOCUMENT-TEST-MAINT-01` PASS
- `PRODUCT-B-OA-WIZARD-CONTRACT-01` PASS
- relevant backend readiness task PASS for each testcase

## Suggested Automation Tasks After Drain

- `B-AUTO-PY-B-OA-INCOMING-P0-01` for `TC-B-001`
- `B-AUTO-PY-B-DOC-VALIDATION-P0-01` for `TC-B-003`
- `B-AUTO-PY-B-OA-TASK-GENERATION-P0-01` for `TC-B-004`
- `B-AUTO-PY-B-OA-REPLY-P0-01` for `TC-B-006`
- `B-AUTO-PY-B-REPLYTO-RULE-P0-01` for `TC-B-007`
- `B-AUTO-PY-B-AUTO-WRITEOFF-P0-01` for `TC-B-008`
- `B-AUTO-PY-B-OA-BILL-PAYMENT-P0-01` for `TC-B-011`
