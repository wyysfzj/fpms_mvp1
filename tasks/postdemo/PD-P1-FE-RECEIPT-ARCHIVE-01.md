# PD-P1-FE-RECEIPT-ARCHIVE-01 — Receipt archive UI

## Exact Closure Slice

Implement receipt/archive UI for filing and OA packages: upload/reference receipt or merged PDF, record visible metadata, received file list, archive status, and controlled manual override.

## Explicit Non-Closure

No automatic receipt download. No OCR. No official confirmation automation. No backend code.

## Remaining Follow-Up Task IDs

- `PD-P1-QA-FULLSCOPE-E2E-01`

## Allowed Files

- `frontend/src/modules/officialWorkflows/components/ReceiptArchivePanel.vue`
- `frontend/src/modules/cases/pages/FilingPreparation.vue`
- `frontend/src/modules/documents/pages/OAReplyPackage.vue`
- `tasks/postdemo/PD-P1-FE-RECEIPT-ARCHIVE-01.md`
- `artifacts/PD-P1-FE-RECEIPT-ARCHIVE-01/**`

## Verification Commands

- `cd frontend && npm run lint`
- `cd frontend && npm run typecheck`
- `cd frontend && npm run build`
- Browser smoke: receipt archive panel enforces required metadata or override reason.
- `./scripts/task_validate.sh PD-P1-FE-RECEIPT-ARCHIVE-01`

## Evidence Path

- `artifacts/PD-P1-FE-RECEIPT-ARCHIVE-01/`

## Acceptance

- Filing and OA packages cannot appear closed in UI without archive evidence or explicit override.
- Override UI records reason and follow-up responsibility.
