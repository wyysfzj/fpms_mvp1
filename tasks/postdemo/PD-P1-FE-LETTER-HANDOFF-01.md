# PD-P1-FE-LETTER-HANDOFF-01 — Format letter and Longxia handoff UI

## Exact Closure Slice

Implement format-letter and Longxia handoff UI: show mapping, preview subject/body/Word path/attachments/contact/salutation, create handoff record, and update handoff status.

## Explicit Non-Closure

No email sending. No Longxia API integration. No backend code. No unrelated dispatch redesign.

## Remaining Follow-Up Task IDs

- `PD-P1-QA-FULLSCOPE-E2E-01`

## Allowed Files

- `frontend/src/modules/documents/pages/DocumentDetail.vue`
- `frontend/src/modules/documents/pages/DocumentDispatch.vue`
- `frontend/src/modules/officialWorkflows/components/LetterHandoffPanel.vue`
- `tasks/postdemo/PD-P1-FE-LETTER-HANDOFF-01.md`
- `artifacts/PD-P1-FE-LETTER-HANDOFF-01/**`

## Verification Commands

- `cd frontend && npm run lint`
- `cd frontend && npm run typecheck`
- `cd frontend && npm run build`
- Browser smoke: handoff panel renders default `尊敬的：您好` when no contact rule is confirmed.
- `./scripts/task_validate.sh PD-P1-FE-LETTER-HANDOFF-01`

## Evidence Path

- `artifacts/PD-P1-FE-LETTER-HANDOFF-01/`

## Acceptance

- UI prepares data for Longxia handoff without sending email.
- Contact/salutation source is visible and auditable.
