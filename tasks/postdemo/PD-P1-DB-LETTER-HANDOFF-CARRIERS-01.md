# PD-P1-DB-LETTER-HANDOFF-CARRIERS-01 — Format letter and handoff carriers

## Exact Closure Slice

Add carriers for official-document-to-format-letter mapping, generated letter handoff records, salutation source, contact selection, Longxia handoff status, and handoff attachment list.

## Explicit Non-Closure

No email sending. No replacement of Longxia. No Word template rendering behavior change unless a minimal schema reference requires it. No frontend changes.

## Remaining Follow-Up Task IDs

- `PD-P1-BE-LETTER-HANDOFF-API-01`
- `PD-P1-FE-LETTER-HANDOFF-01`

## Allowed Files

- `backend/app/modules/documents/models.py`
- `backend/app/modules/documents/schemas.py`
- `backend/app/modules/templates/models.py`
- `backend/app/modules/templates/schemas.py`
- `backend/alembic/versions/pd_p1_db_05_letter_handoff_carriers.py`
- `backend/tests/test_pd_p1_letter_handoff_carriers.py`
- `tasks/postdemo/PD-P1-DB-LETTER-HANDOFF-CARRIERS-01.md`
- `artifacts/PD-P1-DB-LETTER-HANDOFF-CARRIERS-01/**`

## Verification Commands

- `ruff check --fix backend/app/modules/documents/models.py backend/app/modules/documents/schemas.py backend/app/modules/templates/models.py backend/app/modules/templates/schemas.py backend/alembic/versions/pd_p1_db_05_letter_handoff_carriers.py backend/tests/test_pd_p1_letter_handoff_carriers.py`
- `ruff format backend/app/modules/documents/models.py backend/app/modules/documents/schemas.py backend/app/modules/templates/models.py backend/app/modules/templates/schemas.py backend/alembic/versions/pd_p1_db_05_letter_handoff_carriers.py backend/tests/test_pd_p1_letter_handoff_carriers.py`
- `ruff check backend/app/modules/documents/models.py backend/app/modules/documents/schemas.py backend/app/modules/templates/models.py backend/app/modules/templates/schemas.py backend/alembic/versions/pd_p1_db_05_letter_handoff_carriers.py backend/tests/test_pd_p1_letter_handoff_carriers.py`
- `cd backend && pytest -q tests/test_pd_p1_letter_handoff_carriers.py`
- `./scripts/task_validate.sh PD-P1-DB-LETTER-HANDOFF-CARRIERS-01`

## Evidence Path

- `artifacts/PD-P1-DB-LETTER-HANDOFF-CARRIERS-01/**`

## Acceptance

- Mapping can connect an official document/template code to one format letter template.
- Handoff record can store generated Word path, subject/body draft, contact/salutation, attachments, and handoff status.
