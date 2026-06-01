# PD-P1-FE-FILING-PREP-01 — Filing preparation page

## Exact Closure Slice

Implement the P1 filing preparation page that reads backend package data and shows field completeness, file list, official-page checklist, XML zip placeholder/reference, merged PDF archive status, fee summary, review actions, and external-operation timestamps.

## Explicit Non-Closure

No official submit. No CPC XML generation. No auto-signature, QR scan, or RPA. No backend code.

## Remaining Follow-Up Task IDs

- `PD-P1-QA-FULLSCOPE-E2E-01`

## Allowed Files

- `frontend/src/modules/cases/pages/FilingPreparation.vue`
- `frontend/src/modules/cases/components/FilingPackageChecklist.vue`
- `frontend/src/modules/cases/components/FilingPackageManifest.vue`
- `tasks/postdemo/PD-P1-FE-FILING-PREP-01.md`
- `artifacts/PD-P1-FE-FILING-PREP-01/**`

## Verification Commands

- `cd frontend && npm run lint`
- `cd frontend && npm run typecheck`
- `cd frontend && npm run build`
- Browser smoke: filing preparation page renders API data and no auto-submit affordance exists.
- `./scripts/task_validate.sh PD-P1-FE-FILING-PREP-01`

## Evidence Path

- `artifacts/PD-P1-FE-FILING-PREP-01/`

## Acceptance

- Checklist mirrors FS sections for internal number, title, inventor, applicant, contact,代理机构, division, sequence listing, priority, early publication, substantive examination, abstract drawing, confidentiality review, additional files, associated business, and proof filing.
- Missing stable data links back to maintenance positions rather than a permanent submit-time补录 area.
