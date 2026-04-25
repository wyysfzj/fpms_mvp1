# BE-B-DOCUMENT-REPLYTO-NOTFOUND-RULE-01

Task ID: `BE-B-DOCUMENT-REPLYTO-NOTFOUND-RULE-01`

Story Shape Classification:
- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

chosen_runbook: `P0-prereq-heavy-story`

## Exact Closure Slice

Ensure document creation returns stable business error semantics when an OUT document references a nonexistent `reply_to_id`.

This task closes only:
- Validate `reply_to_id` before inserting/flushing a new document.
- Return `REPLY_TO_DOC_NOT_FOUND` with HTTP 404 instead of leaking a database foreign-key failure as 500.
- Preserve existing reply-chain auto write-off behavior for valid reply documents.

## Explicit Non-Closure

Do not:
- implement B-wave pytest automation handlers
- change reply-to template compatibility rules
- implement status restore or deadline edit behavior
- modify frontend
- modify skeleton data
- change document update semantics unless separately planned

## Remaining Follow-Up Task IDs

- `PRODUCT-B-OA-WIZARD-CONTRACT-01`
- `BE-B-OA-WIZARD-READINESS-01`
- `BE-B-OA-REPLY-READINESS-01`

## Allowed Files

- `tasks/backend/business_logic/BE-B-DOCUMENT-REPLYTO-NOTFOUND-RULE-01.md`
- `backend/app/modules/documents/service.py`
- `backend/tests/test_b2_reply_chain.py`
- `artifacts/BE-B-DOCUMENT-REPLYTO-NOTFOUND-RULE-01/**`

`backend/tests/test_b2_reply_chain.py` is allowlisted only for existing focused verification; this task does not need to modify it if the existing assertion already covers the rule.

## Verification Commands

Run from `backend/`:

```bash
python3 -m ruff check --fix app/modules/documents/service.py tests/test_b2_reply_chain.py
python3 -m ruff format app/modules/documents/service.py tests/test_b2_reply_chain.py
python3 -m ruff check app/modules/documents/service.py tests/test_b2_reply_chain.py
pytest tests/test_b2_reply_chain.py::test_reply_to_nonexistent_document_404 -q
pytest tests/test_b2_reply_chain.py -q
./scripts/task_validate.sh BE-B-DOCUMENT-REPLYTO-NOTFOUND-RULE-01
```

## Evidence Path

- `artifacts/BE-B-DOCUMENT-REPLYTO-NOTFOUND-RULE-01/results.jsonl`
- `artifacts/BE-B-DOCUMENT-REPLYTO-NOTFOUND-RULE-01/summary.md`
- `artifacts/BE-B-DOCUMENT-REPLYTO-NOTFOUND-RULE-01/git/diff.patch`
