# FPMS-DEMO-ABC-FINAL-REHEARSAL-20260817-01

Status: READY
Risk-Tier: HIGH
Risk-Class: PROTECTED
Closure-Tags: ["demo", "browser", "runtime-input", "billing", "evidence"]
Task-Path: tasks/postdemo/FPMS-DEMO-ABC-FINAL-REHEARSAL-20260817-01.md

## Exact Closure Slice

On the current candidate, execute one focused visible-browser spec twice against two fresh, isolated
SQLite/storage RUN_IDs. Each run uses the temporary fictional technical bundle, creates customer and
case through the UI, and completes runtime input → service obligation → PAY → locked draft → unique
AR bill → bank receipt → full offset through visible UI actions and real APIs. Persist screenshots,
Playwright logs, exact run metadata, read-only database postconditions, candidate identity and process
cleanup evidence for both runs.

## Explicit Non-Closure

The technical fixture is not customer authority and cannot yield `DEMO_READY`. No OA/grant,
production/PostgreSQL, remote hosting, security, dashboard, generic finance, broad Playwright,
product/release gate or release claim.

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-ABC-CUSTOMER-INPUT-ACTIVATION-20260817-01`

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-abc.live-backend.spec.ts`
- `artifacts/FPMS-DEMO-ABC-FINAL-REHEARSAL-20260817-01/**`

## Verification Commands

1. Static gate forbids route mocks, direct DB/enrichment and skipped tests in the focused spec.
2. Each fresh run migrates, seeds only identities/RBAC, and passes one Chromium test with zero skips.
3. Each final UI shows SETTLED/0.00, FULLY_ALLOCATED/0.00 and equal CaseReceipt amounts.
4. Read-only SQLite checks prove one source draft, bill, payment line, active offset and receipt.
5. Exact candidate/tree, technical bundle digests, RUN_IDs and cleanup are persisted.

## Evidence Path

- `artifacts/FPMS-DEMO-ABC-FINAL-REHEARSAL-20260817-01/`

## Rollback

Revert the focused test commit, stop exact recorded PIDs, and remove only the two exact temporary run
roots after evidence capture.

## Done definition

Two current-candidate technical rehearsals are reproducibly green. Independent High acceptance and
actual customer input remain separate mandatory gates.
