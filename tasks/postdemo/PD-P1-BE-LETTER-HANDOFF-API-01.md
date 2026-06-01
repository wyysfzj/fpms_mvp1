# PD-P1-BE-LETTER-HANDOFF-API-01 — Format letter and Longxia handoff API

## Exact Closure Slice

Add backend API behavior for format-letter mapping and Longxia handoff preparation: choose mapping by official document, preview handoff data, create handoff record, and record handoff status.

## Explicit Non-Closure

No email sending. No Longxia API integration. No replacement of existing dispatch/mail systems. No frontend implementation.

## Remaining Follow-Up Task IDs

- `PD-P1-FE-LETTER-HANDOFF-01`
- `PD-P1-QA-FULLSCOPE-E2E-01`

## Allowed Files

- `backend/app/modules/official_workflows/api.py`
- `backend/app/modules/official_workflows/schemas.py`
- `backend/app/modules/official_workflows/service.py`
- `backend/app/modules/documents/service.py`
- `backend/tests/test_pd_p1_letter_handoff_api.py`
- `tasks/postdemo/PD-P1-BE-LETTER-HANDOFF-API-01.md`
- `artifacts/PD-P1-BE-LETTER-HANDOFF-API-01/**`

## Verification Commands

- `ruff check --fix backend/app/modules/official_workflows backend/app/modules/documents/service.py backend/tests/test_pd_p1_letter_handoff_api.py`
- `ruff format backend/app/modules/official_workflows backend/app/modules/documents/service.py backend/tests/test_pd_p1_letter_handoff_api.py`
- `ruff check backend/app/modules/official_workflows backend/app/modules/documents/service.py backend/tests/test_pd_p1_letter_handoff_api.py`
- `cd backend && pytest -q tests/test_pd_p1_letter_handoff_api.py`
- `./scripts/task_validate.sh PD-P1-BE-LETTER-HANDOFF-API-01`

## Evidence Path

- `artifacts/PD-P1-BE-LETTER-HANDOFF-API-01/`

## Acceptance

- Preview includes subject, body draft, generated Word path or pending-template status, attachment list, contact, and salutation.
- If no contact rule is confirmed, default salutation remains `尊敬的：您好`.
