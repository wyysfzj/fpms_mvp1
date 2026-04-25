# BE-B-OA-WIZARD-READINESS-01

Task ID: `BE-B-OA-WIZARD-READINESS-01`

Story Shape Classification:
- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

chosen_runbook: `P0-prereq-heavy-story`

## Exact Closure Slice

Verify the existing backend OA incoming document wizard path needed by `TC-B-001`, `TC-B-003`, and `TC-B-004`.

This task closes only:
- document wizard batch create
- template defaults and status effect readiness
- task preview/final task-row creation fields
- document row validation coverage
- attachment preview side-effect-free behavior

## Explicit Non-Closure

Do not:
- implement pytest automation handlers
- implement `OfficialDueDate` override for `TC-B-002`
- implement ReplyTo same-case/template rules
- implement OA fee/bill/payment/commission behavior
- modify frontend or skeleton data

## Remaining Follow-Up Task IDs

- `BE-B-OFFICIAL-DUE-DATE-TASK-GENERATION-01`
- `BE-B-OA-REPLY-READINESS-01`
- `BE-B-OA-FINANCE-READINESS-01`

## Allowed Files

- `tasks/backend/business_logic/BE-B-OA-WIZARD-READINESS-01.md`
- `backend/app/modules/documents/service.py`
- `backend/app/modules/documents/api.py`
- `backend/app/modules/documents/schemas.py`
- `artifacts/BE-B-OA-WIZARD-READINESS-01/**`

This readiness task is test/evidence-only because the current backend wizard tests pass after stale applicant fixtures were repaired by `BE-B-DOCUMENT-TEST-MAINT-01`.

## Verification Commands

Run from `backend/`:

```bash
python3 -m ruff check app/modules/documents/service.py app/modules/documents/api.py app/modules/documents/schemas.py
pytest tests/test_document_wizard_batch_create.py tests/test_document_wizard_task_preview.py tests/test_document_wizard_attachment_preview.py -q
./scripts/task_validate.sh BE-B-OA-WIZARD-READINESS-01
```

## Evidence Path

- `artifacts/BE-B-OA-WIZARD-READINESS-01/results.jsonl`
- `artifacts/BE-B-OA-WIZARD-READINESS-01/summary.md`
- `artifacts/BE-B-OA-WIZARD-READINESS-01/git/diff.patch`
