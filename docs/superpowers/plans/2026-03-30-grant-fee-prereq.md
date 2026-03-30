# GF-PRE Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish `T_GrantFeeTask` carrier, SQLite-safe migration, grant-fee backend module skeleton, and `GrantFeeTask` permission namespace so later grant-fee workflow stories have a stable foundation.

**Architecture:** Execute this as a prerequisite-heavy story with serialized ownership: DB carrier first, then backend skeleton/permission wiring, then QA close. Keep workflow engine, worklist, and linkage strictly deferred.

**Tech Stack:** FastAPI, SQLAlchemy, Alembic, SQLite

---

## Story Shape Classification
- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: chained (DB -> BE skeleton)
- evidence_cost: medium

## chosen_runbook
- P0-prereq-heavy-story

## Batch Manifest

### GFPRE-DB-01
- task file path: `tasks/postenhancement/backend/GFPRE-DB-01.md`
- closure slice: add `T_GrantFeeTask` structured carrier and SQLite-safe migration with the frozen minimal field set
- explicit non-closure: no workflow endpoints, no worklist, no state-machine actions, no fee draft/bill/document linkage
- allowlist:
  - `backend/alembic/versions/gfpre_db_01_create_t_grant_fee_task.py`
  - `backend/app/modules/fees/models.py`
  - `backend/tests/test_grant_fee_prereq_schema.py`
- verification:
  - `python3 -m ruff check backend/alembic/versions/gfpre_db_01_create_t_grant_fee_task.py backend/app/modules/fees/models.py backend/tests/test_grant_fee_prereq_schema.py`
  - `cd backend && PYTHONPATH=. pytest -q tests/test_grant_fee_prereq_schema.py`
  - `cd backend && PYTHONPATH=. alembic upgrade head`
  - `./scripts/task_validate.sh GFPRE-DB-01`
- dependency notes: first wave; BE skeleton depends on stable carrier

### GFPRE-BE-01
- task file path: `tasks/postenhancement/backend/GFPRE-BE-01.md`
- closure slice: add grant-fee backend module skeleton and freeze `GrantFeeTask.Read/Write` permission namespace without implementing workflow actions
- explicit non-closure: no worklist, no state-machine actions, no fee draft/bill/document linkage, no frontend
- allowlist:
  - `backend/app/modules/grant_fees/api.py`
  - `backend/app/modules/grant_fees/schemas.py`
  - `backend/app/modules/grant_fees/service.py`
  - `backend/app/modules/grant_fees/__init__.py`
  - `backend/app/api/router.py`
  - `backend/app/modules/rbac/service.py`
  - `backend/tests/test_grant_fee_prereq_contract.py`
- verification:
  - `python3 -m ruff check backend/app/modules/grant_fees/api.py backend/app/modules/grant_fees/schemas.py backend/app/modules/grant_fees/service.py backend/app/modules/rbac/service.py backend/app/api/router.py backend/tests/test_grant_fee_prereq_contract.py`
  - `cd backend && PYTHONPATH=. pytest -q tests/test_grant_fee_prereq_contract.py`
  - `./scripts/task_validate.sh GFPRE-BE-01`
- dependency notes: serialize after `GFPRE-DB-01`; owns router and permission wiring

### GFPRE-QA-01
- task file path: `tasks/postenhancement/backend/GFPRE-QA-01.md`
- closure slice: gate audit, evidence audit, and story close summary for `GF-PRE`
- explicit non-closure: no product code changes
- allowlist:
  - `artifacts/GFPRE-DB-01/**`
  - `artifacts/GFPRE-BE-01/**`
  - `artifacts/GFPRE-QA-01/**`
- verification:
  - `./scripts/task_validate.sh GFPRE-DB-01`
  - `./scripts/task_validate.sh GFPRE-BE-01`
  - `./scripts/task_validate.sh GFPRE-QA-01`
- dependency notes: final wave after DB and BE pass

## Waves
- Wave 1: `GFPRE-DB-01`
- Wave 2: `GFPRE-BE-01`
- Wave 3: `GFPRE-QA-01`

## Serialized Shared-file Decisions
- `backend/app/modules/fees/models.py` is owned only by `GFPRE-DB-01`
- `backend/app/api/router.py` is owned only by `GFPRE-BE-01`
- `backend/app/modules/rbac/service.py` is owned only by `GFPRE-BE-01`
- `backend/app/modules/grant_fees/*` is owned only by `GFPRE-BE-01`
