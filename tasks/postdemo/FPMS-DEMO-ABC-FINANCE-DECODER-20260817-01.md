# FPMS-DEMO-ABC-FINANCE-DECODER-20260817-01

Status: READY
Risk-Tier: HIGH
Risk-Class: PROTECTED
Closure-Tags: ["demo", "frontend", "finance", "contract"]
Task-Path: tasks/postdemo/FPMS-DEMO-ABC-FINANCE-DECODER-20260817-01.md

## Exact Closure Slice

Runtime-decode every response consumed by the local ABC demo. Required money remains an exact
two-decimal string; IDs, SHA-256 digests, dates, CNY currency and finite status vocabularies fail
closed with `FINANCE_CONTRACT_INVALID`. The page must never turn null, numbers, malformed strings or
unknown statuses into a visible financial fact.

## Explicit Non-Closure

No generic billing, annuity, commission, expense, collection or dashboard adapter cleanup. No API
schema redesign, visual redesign, production or release work.

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-ABC-EVIDENCE-REBUILD-20260817-01`

## Allowed Files

- `frontend/src/modules/demo/demo.contract.ts`
- `frontend/src/modules/demo/demo.api.ts`
- `frontend/tests/demo-abc-finance-decoder.mjs`
- `artifacts/FPMS-DEMO-ABC-FINANCE-DECODER-20260817-01/**`

## Verification Commands

1. RED shows malformed required money/ID/status can cross the current typed-only adapter.
2. GREEN behavior test transpiles the pure decoder and proves exact rejection/round-trip behavior.
3. Frontend lint/typecheck and exact scope checks pass.

## Evidence Path

- `artifacts/FPMS-DEMO-ABC-FINANCE-DECODER-20260817-01/`

## Rollback

Revert the atomic implementation commit.

## Done definition

All ABC demo API responses are runtime-validated before any page state update. Independent High
acceptance remains required.
