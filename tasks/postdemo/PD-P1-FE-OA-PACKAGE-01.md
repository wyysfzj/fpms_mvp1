# PD-P1-FE-OA-PACKAGE-01 — OA reply package page

## Exact Closure Slice

Implement the P1 OA reply package page that reads backend package data and shows source official notice, reply chain, due dates, statement files, PDF fidelity attachment, modified files, experiment-data flag, official-page checklist, and status actions.

## Explicit Non-Closure

No official-site automation. No rich-text converter. No automatic submit/signature. No backend code.

## Remaining Follow-Up Task IDs

- `PD-P1-QA-FULLSCOPE-E2E-01`

## Allowed Files

- `frontend/src/modules/documents/pages/OAReplyPackage.vue`
- `frontend/src/modules/documents/components/OAReplyChecklist.vue`
- `frontend/src/modules/documents/components/OAReplyManifest.vue`
- `frontend/src/modules/documents/pages/DocumentDetail.vue`
- `tasks/postdemo/PD-P1-FE-OA-PACKAGE-01.md`
- `artifacts/PD-P1-FE-OA-PACKAGE-01/**`

## Verification Commands

- `cd frontend && npm run lint`
- `cd frontend && npm run typecheck`
- `cd frontend && npm run build`
- Browser smoke: OA package renders checklist sections for cloud second download, query result, business handling, preview tabs, signature, confirmation, and receipt.
- `./scripts/task_validate.sh PD-P1-FE-OA-PACKAGE-01`

## Evidence Path

- `artifacts/PD-P1-FE-OA-PACKAGE-01/`

## Acceptance

- UI keeps OA package embedded in existing document/reply flow.
- `reply_date` is not shown as proof of official submission unless receipt/archive status supports it.
