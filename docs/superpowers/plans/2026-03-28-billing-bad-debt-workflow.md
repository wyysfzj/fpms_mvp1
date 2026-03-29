# Billing Bad-Debt Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the AR bad-debt workflow from bill detail actions through reporting, using durable bad-debt vouchers and recovery records.

**Architecture:** This is a prerequisite-heavy serialized story. Durable bad-debt persistence lands first, then bill-detail contracts and actions, then recovery handling, then frontend bill-detail UI, then report/list integration, and finally audit closure.

**Tech Stack:** FastAPI, SQLAlchemy ORM, Alembic, Vue 3, TypeScript, SQLite, Ruff, Pytest

---

## Story Shape

- shared_file_density: `high`
- prereq_dependency_density: `high`
- be_fe_coupling: `chained (BE -> FE -> report)`
- evidence_cost: `high`

## Chosen Runbook

- chosen_runbook: `P0-prereq-heavy-story`

## Atomic Task Inventory

- `BADDEBT-DB-01`:
  - Task file path: `tasks/postenhancement/backend/BADDEBT-DB-01.md`
  - Owner role: `worker`
  - Exact closure slice:
    - Add durable bad-debt master voucher persistence, recovery persistence, and AR bill bad-debt state carriers only.
  - Explicit non-closure:
    - Does not add bill APIs, bad-debt actions, bill detail UI, or report slices.
  - Required verification:
    - `ruff check backend/alembic/versions/baddebt_db_01_create_bad_debt_tables.py backend/app/modules/billing/models.py`
    - `cd backend && alembic upgrade head`
    - `./scripts/task_validate.sh BADDEBT-DB-01`
  - Dependency notes:
    - First serialized prerequisite wave.
  - Remaining follow-up task ids:
    - `BADDEBT-BE-BILL-01`
    - `BADDEBT-BE-ACT-01`
    - `BADDEBT-BE-REC-01`
    - `BADDEBT-FE-BILL-01`
    - `BADDEBT-BE-RPT-01`
    - `BADDEBT-FE-RPT-01`
    - `BADDEBT-QA-01`
  - Allowlist:
    - `backend/alembic/versions/baddebt_db_01_create_bad_debt_tables.py`
    - `backend/app/modules/billing/models.py`
  - Done definition:
    - Durable bad-debt tables and bill state carriers exist, remain SQLite-safe, and no API/service behavior is silently absorbed.

## Wave Plan

- Wave 1:
  - Tasks:
    - `BADDEBT-DB-01`
  - Mode:
    - serialized
  - Shared ownership notes:
    - Owns billing schema/model only.

## Execution Notes

- 2026-03-29 planning correction:
  - The repo does not contain `frontend/src/modules/billing/pages/BillingReport.vue`.
  - `BADDEBT-FE-RPT-01` must therefore land on the existing bill-list surface (`frontend/src/modules/billing/pages/BillList.vue`) plus shared billing frontend API typings.
  - This correction does not change story shape or chosen runbook; it only narrows the frontend report/list closure slice to an existing UI surface.
