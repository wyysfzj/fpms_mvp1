# FPMS-DEMO-ABC-LIVE-E2E-20260816-01

Status: READY
Risk-Class: PROTECTED
Closure-Tags: ["demo", "browser", "runtime-input", "billing", "evidence"]
Task-Path: tasks/postdemo/FPMS-DEMO-ABC-LIVE-E2E-20260816-01.md

## Exact Closure Slice

On one fresh local SQLite/storage run, use the visible UI to create fictional customer and case
records, enter the sidebar-reachable ABC demo console, and drive the real API through validated
DEMO_ONLY runtime input, SERVICE obligation, PAY instruction, one locked draft, one AR bill, one
bank receipt and one full offset. Preserve a final browser screenshot and a read-only database
postcondition report for the exact run.

## Explicit Non-Closure

The temporary technical-rehearsal bundle is not customer-approved runtime input. No OA/grant path,
production/PostgreSQL concurrency, remote hosting, security, generic finance UI, partial allocation,
refund, dashboard, broad Playwright, broad product gate, release approval or production claim.

## Allowed Files

- `artifacts/FPMS-DEMO-ABC-LIVE-E2E-20260816-01/**`

## Verification Commands

1. Fresh runner migrates and seeds only identities/RBAC.
2. Visible browser creates the fictional client and case and completes all ABC financial actions.
3. Final UI shows bill `SETTLED/0.00`, payment `FULLY_ALLOCATED/0.00`, and case receipt
   `1200.00/1200.00 CNY` with the exact manifest/template hashes.
4. Read-only SQLite checks prove exactly one source draft, bill, payment line, active offset and
   receipt, with the same amount and balanced projections.
5. Exact candidate identity and worktree cleanliness are recorded. No broad or release gate runs.

## Evidence Path

- `artifacts/FPMS-DEMO-ABC-LIVE-E2E-20260816-01/`

## Rollback

Stop the exact local processes and retain or remove only the exact temporary run root after evidence
capture. No repository business data is written.

## Done definition

The technical rehearsal and targeted postconditions are complete and bound to the exact candidate.
Acceptance remains BLOCKED until an independent High reviewer passes the task and a customer-
authorized runtime bundle replaces the temporary technical input.
