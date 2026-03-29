# Billing Prepayment Management Reporting Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close `P1 #7` by turning the existing payments list path into a usable prepayment management report with filters, list fields, and summary totals.

**Architecture:** This is a frontend-heavy serialized story. The backend first extends `GET /payments` to support report filters and summary totals using existing payment/payment-line semantics. The frontend then upgrades the existing `PaymentList.vue` to consume that contract. Final QA audits item-to-slice coverage and evidence completeness.

**Tech Stack:** FastAPI, SQLAlchemy ORM, Vue 3, TypeScript, SQLite, Ruff, Pytest, ESLint, vue-tsc

---

## Story Shape

- shared_file_density: `medium`
- prereq_dependency_density: `low`
- be_fe_coupling: `chained (BE -> FE)`
- evidence_cost: `medium`

## Chosen Runbook

- chosen_runbook: `P0-frontend-heavy-story`

## Atomic Task Inventory

- `PREPAYRPT-BE-01`:
  - Task file path: `tasks/postenhancement/backend/PREPAYRPT-BE-01.md`
  - Owner role: `worker`
  - Exact closure slice:
    - Extend `GET /payments` with prepayment report filters and top-level summary fields while preserving the existing list envelope.
  - Explicit non-closure:
    - Does not modify frontend pages, create new pages, or add write actions.
  - Required verification:
    - `ruff check backend/app/modules/billing/api.py backend/app/modules/billing/schemas.py backend/app/modules/billing/service.py backend/tests/test_prepayment_reporting_api.py`
    - `cd backend && pytest -q tests/test_prepayment_reporting_api.py`
    - `./scripts/task_validate.sh PREPAYRPT-BE-01`
  - Dependency notes:
    - First execution wave. Frontend depends on this contract.
  - Remaining follow-up task ids:
    - `PREPAYRPT-FE-01`
    - `PREPAYRPT-QA-01`
  - Allowlist:
    - `backend/app/modules/billing/api.py`
    - `backend/app/modules/billing/schemas.py`
    - `backend/app/modules/billing/service.py`
    - `backend/tests/test_prepayment_reporting_api.py`

- `PREPAYRPT-FE-01`:
  - Task file path: `tasks/postenhancement/frontend/PREPAYRPT-FE-01.md`
  - Owner role: `worker`
  - Exact closure slice:
    - Upgrade the existing `PaymentList.vue` with prepayment filters, summary cards, and the approved minimal report columns using the new backend contract.
  - Explicit non-closure:
    - Does not create a dedicated report page, modify payment create flow, or change offset behavior.
  - Required verification:
    - `cd frontend && npm run lint -- src/api/billing.ts src/api/billing.types.ts src/modules/billing/pages/PaymentList.vue`
    - `cd frontend && npm run typecheck`
    - `./scripts/task_validate.sh PREPAYRPT-FE-01`
  - Dependency notes:
    - Must run after `PREPAYRPT-BE-01`.
  - Remaining follow-up task ids:
    - `PREPAYRPT-QA-01`
  - Allowlist:
    - `frontend/src/api/billing.ts`
    - `frontend/src/api/billing.types.ts`
    - `frontend/src/modules/billing/pages/PaymentList.vue`

- `PREPAYRPT-QA-01`:
  - Task file path: `tasks/postenhancement/backend/PREPAYRPT-QA-01.md`
  - Owner role: `monitor`
  - Exact closure slice:
    - Audit `P1 #7` implementation slices, evidence, and task gates; emit item-to-slice ledger and story-level close decision.
  - Explicit non-closure:
    - Does not modify product code or redefine the approved design.
  - Required verification:
    - `./scripts/task_validate.sh PREPAYRPT-BE-01`
    - `./scripts/task_validate.sh PREPAYRPT-FE-01`
    - `./scripts/task_validate.sh PREPAYRPT-QA-01`
  - Dependency notes:
    - Final close wave only.
  - Remaining follow-up task ids:
    - `None`
  - Allowlist:
    - `artifacts/PREPAYRPT-QA-01/**`
    - `docs/superpowers/specs/2026-03-29-billing-prepayment-reporting-design.md`
    - `docs/superpowers/plans/2026-03-29-billing-prepayment-reporting.md`
    - `tasks/postenhancement/backend/PREPAYRPT-BE-01.md`
    - `tasks/postenhancement/frontend/PREPAYRPT-FE-01.md`

## Wave Plan

- Wave 1:
  - Tasks:
    - `PREPAYRPT-BE-01`
  - Mode:
    - serialized
  - Shared ownership notes:
    - Owns `backend/app/modules/billing/api.py|schemas.py|service.py`.

- Wave 2:
  - Tasks:
    - `PREPAYRPT-FE-01`
  - Mode:
    - serialized
  - Shared ownership notes:
    - Owns `frontend/src/api/billing.ts|billing.types.ts|modules/billing/pages/PaymentList.vue`.

- Wave 3:
  - Tasks:
    - `PREPAYRPT-QA-01`
  - Mode:
    - serialized
  - Shared ownership notes:
    - Audit only; no product code edits.
