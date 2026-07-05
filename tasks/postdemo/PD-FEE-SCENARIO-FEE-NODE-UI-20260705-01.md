# PD-FEE-SCENARIO-FEE-NODE-UI-20260705-01

Story Shape Classification
- shared_file_density: medium
- prereq_dependency_density: medium
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-frontend-heavy-story

## Exact Closure Slice
- Enhance the case fees tab to show a Simplified-Chinese official-fee node panel for the domestic filing/acceptance fee preview, including candidate status, calculation basis, source event/idempotency key, and existing fee-draft status.

## Explicit Non-Closure
- No backend changes, database migration, PayList/GovPayment generation, official payment Excel, CPC/OA direct submission, RPA, automatic signing, or automatic payment.
- No UI for PCT, restoration, extension, invalidation, compensation-period, open-license, or other P2/P3 official-fee triggers.
- No full E2E demo automation; that remains in `PD-FEE-SCENARIO-E2E-VERIFY-20260705-01`.

## Remaining Follow-Up Task IDs
- `PD-FEE-SCENARIO-E2E-VERIFY-20260705-01`
- Future trigger-specific UI tasks after customer confirms P2/P3 events.

## Allowed Files
- tasks/postdemo/PD-FEE-SCENARIO-FEE-NODE-UI-20260705-01.md
- frontend/src/api/fees.ts
- frontend/src/api/fees.types.ts
- frontend/src/modules/cases/components/CaseFeesTab.vue
- artifacts/PD-FEE-SCENARIO-FEE-NODE-UI-20260705-01/**

## Verification Commands
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/PD-FEE-SCENARIO-FEE-NODE-UI-20260705-01.md`
- `cd frontend && npm run typecheck`
- `cd frontend && npm run build`
- `./scripts/task_validate.sh PD-FEE-SCENARIO-FEE-NODE-UI-20260705-01`

## Evidence Path
- artifacts/PD-FEE-SCENARIO-FEE-NODE-UI-20260705-01/**

## Done Definition
- Case fees tab displays an official-fee node panel in Simplified Chinese.
- The panel loads `FILING_ACCEPTED` official fee candidates via the existing backend preview API.
- The panel shows candidate amount, candidate item calculation basis, source/idempotency key, and whether an existing fee draft has already been generated.
- Missing/unsupported preview states are shown as clear Chinese pending/blocker messages without implying official submission or payment.
