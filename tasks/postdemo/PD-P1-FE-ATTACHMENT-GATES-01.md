# PD-P1-FE-ATTACHMENT-GATES-01 — Attachment official role and gate UI

## Exact Closure Slice

Expose official attachment role, role alias, upload-position, hash/status, and gate classification in existing document/attachment UI surfaces.

## Explicit Non-Closure

No backend code. No file conversion. No OCR. No page-wide redesign.

## Remaining Follow-Up Task IDs

- `PD-P1-FE-FILING-PREP-01`
- `PD-P1-FE-OA-PACKAGE-01`
- `PD-P1-FE-RECEIPT-ARCHIVE-01`

## Allowed Files

- `frontend/src/modules/documents/components/AttachmentList.vue`
- `frontend/src/modules/documents/pages/DocumentDetail.vue`
- `frontend/src/modules/cases/components/CaseDocumentsTab.vue`
- `tasks/postdemo/PD-P1-FE-ATTACHMENT-GATES-01.md`
- `artifacts/PD-P1-FE-ATTACHMENT-GATES-01/**`

## Verification Commands

- `cd frontend && npm run lint`
- `cd frontend && npm run typecheck`
- `cd frontend && npm run build`
- Browser smoke: attachment role and gate labels render in Simplified Chinese.
- `./scripts/task_validate.sh PD-P1-FE-ATTACHMENT-GATES-01`

## Evidence Path

- `artifacts/PD-P1-FE-ATTACHMENT-GATES-01/`

## Acceptance

- Users can see whether a file is technical disclosure, commission instruction, filing document, OA attachment, XML zip, merged PDF, or receipt.
- Historical aliases are displayed as aliases, not as stable official roles.
