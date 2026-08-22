# FPMS-DEMO-ABC-RUNTIME-SERVICE-DRAFT-20260816-01

Status: READY
Risk-Class: PROTECTED
Closure-Tags: ["demo", "service-receivable", "fee-obligation", "fee-draft"]
Task-Path: tasks/postdemo/FPMS-DEMO-ABC-RUNTIME-SERVICE-DRAFT-20260816-01.md

## Story shape

- shared_file_density: medium
- prereq_dependency_density: high
- be_fe_coupling: API-first
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Design references

- `AGENTS.md`
- `docs/product/v8/domain-contract.md`
- `docs/superpowers/specs/2026-08-15-fpms-local-demo-abc-design.md` sections 6–7
- `tasks/postdemo/FPMS-DEMO-ABC-BUNDLE-PREFLIGHT-20260816-01.md`

## Exact Closure Slice

Expose the one validated runtime SERVICE item in demo mode and provide one authenticated,
idempotent command that records its immutable bundle lineage and creates one SERVICE obligation
for an existing case. Existing PAY-instruction and obligation-draft commands must then create one
positive SERVICE draft item, after which the existing lock command freezes the draft. Missing or
changed input and item/key drift return 409 with no partial obligation/draft/item write.

## Explicit Non-Closure

No production ServicePriceBook/FeeRate/Template/decision-gate row, official fee, automatic draft,
PayList, billing, frontend, lifecycle fixture or actual customer bundle. This task does not create
clients/cases and does not bypass authentication or permissions.

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-ABC-UNIQUE-AR-BILL-20260816-01`
- `FPMS-DEMO-ABC-PAYMENT-OFFSET-20260816-01`
- `FPMS-DEMO-ABC-FINANCE-UI-20260816-01`
- `FPMS-DEMO-ABC-LIVE-E2E-20260816-01`

## Allowed Files

- `backend/app/modules/fees/demo_service.py`
- `backend/app/modules/fees/demo_service_schemas.py`
- `backend/app/modules/fees/api.py`
- `backend/tests/test_demo_abc_runtime_service_draft.py`
- `artifacts/FPMS-DEMO-ABC-RUNTIME-SERVICE-DRAFT-20260816-01/**`

## Verification Commands

1. RED proves the demo runtime-service API is absent.
2. Target pytest proves read-only item display, exact source/obligation lineage, same-key replay,
   drift/no-input no-write, PAY prerequisite, one positive SERVICE item and lock.
3. Scoped Ruff passes.
4. Exact allowlist and `git diff --check` pass. No broad/release gate runs.

## Evidence Path

- `artifacts/FPMS-DEMO-ABC-RUNTIME-SERVICE-DRAFT-20260816-01/`

## Rollback

Revert the atomic story commit; no bundle or production input row exists to migrate or roll back.

## Done definition

Target checks pass and the exact commit is ready for independent High review. Billing remains
outside closure.
