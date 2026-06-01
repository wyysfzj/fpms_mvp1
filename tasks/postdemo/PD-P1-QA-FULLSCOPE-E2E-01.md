# PD-P1-QA-FULLSCOPE-E2E-01 — P1 full-scope QA and close ledger

## Exact Closure Slice

Run final full-scope verification and produce an item-to-slice close ledger mapping every P1 Functional Spec acceptance criterion to implementation task IDs, tests, screenshots/browser evidence, and residual gap status.

## Explicit Non-Closure

No product feature implementation except minimal harness-only fixes inside the allowlist if required to run evidence. No scope expansion beyond P1 FS.

## Remaining Follow-Up Task IDs

None.

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/pytest_python/**`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/**`
- `artifacts/PD-P1-QA-FULLSCOPE-E2E-01/**`
- `artifacts/PD-P1-FULLSCOPE-CLOSE-AUDIT-20260531/**`
- `tasks/postdemo/PD-P1-QA-FULLSCOPE-E2E-01.md`

## Verification Commands

- `./scripts/task_validate.sh PD-P1-DB-CASE-OFFICIAL-FIELDS-01`
- `./scripts/task_validate.sh PD-P1-DB-ATTACHMENT-MANIFEST-01`
- `./scripts/task_validate.sh PD-P1-DB-WORK-PACKAGE-01`
- `./scripts/task_validate.sh PD-P1-DB-FEE-OFFICIAL-CARRIERS-01`
- `./scripts/task_validate.sh PD-P1-DB-LETTER-HANDOFF-CARRIERS-01`
- `./scripts/task_validate.sh PD-P1-BE-CASE-OFFICIAL-FIELDS-API-01`
- `./scripts/task_validate.sh PD-P1-BE-ATTACHMENT-MANIFEST-SERVICE-01`
- `./scripts/task_validate.sh PD-P1-BE-WORK-PACKAGE-SERVICE-01`
- `./scripts/task_validate.sh PD-P1-BE-FILING-PACKAGE-API-01`
- `./scripts/task_validate.sh PD-P1-BE-OA-PACKAGE-API-01`
- `./scripts/task_validate.sh PD-P1-BE-RECEIPT-ARCHIVE-API-01`
- `./scripts/task_validate.sh PD-P1-BE-FEE-LINKAGE-API-01`
- `./scripts/task_validate.sh PD-P1-BE-LETTER-HANDOFF-API-01`
- `./scripts/task_validate.sh PD-P1-FE-API-CONTRACTS-01`
- `./scripts/task_validate.sh PD-P1-FE-NAV-ROUTES-01`
- `./scripts/task_validate.sh PD-P1-FE-CASE-OFFICIAL-FIELDS-01`
- `./scripts/task_validate.sh PD-P1-FE-ATTACHMENT-GATES-01`
- `./scripts/task_validate.sh PD-P1-FE-FILING-PREP-01`
- `./scripts/task_validate.sh PD-P1-FE-OA-PACKAGE-01`
- `./scripts/task_validate.sh PD-P1-FE-RECEIPT-ARCHIVE-01`
- `./scripts/task_validate.sh PD-P1-FE-FEE-LINKAGE-01`
- `./scripts/task_validate.sh PD-P1-FE-LETTER-HANDOFF-01`
- `./scripts/task_validate.sh PD-P1-BE-BATCH-FILING-FEE-LIMIT-GATE-01`
- `cd backend && pytest -q` only if approved for final batch close.
- `cd frontend && npm run lint && npm run typecheck && npm run build`
- `./scripts/task_validate.sh PD-P1-QA-FULLSCOPE-E2E-01`

## Evidence Path

- `artifacts/PD-P1-QA-FULLSCOPE-E2E-01/`

## Acceptance

- Close ledger proves all P1 FS acceptance criteria are covered or explicitly marked out-of-scope/P2/P3.
- No direct submit, RPA, auto-signature, auto-payment, or Longxia replacement is introduced.
- Every implemented task has required evidence artifacts and task gate PASS.
