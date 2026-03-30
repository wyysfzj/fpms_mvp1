# GF-SM Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the grant-fee task mainline state machine and action contract on top of the `GF-PRE` carrier without absorbing worklist or linkage slices.

**Architecture:** Execute this as a backend-only single-lane story. State-machine contract and service rules are implemented in one backend wave, followed by QA close. Keep worklist, fee draft generation, and all other linkage strictly deferred.

**Tech Stack:** FastAPI, SQLAlchemy, SQLite

---

## Story Shape Classification
- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: backend-only
- evidence_cost: medium

## chosen_runbook
- P0-single-lane-story

## Batch Manifest

### GFSM-BE-01
- task file path: `tasks/postenhancement/backend/GFSM-BE-01.md`
- closure slice: implement grant-fee mainline state machine contract and service rules, including legal transitions and invalid-transition validation
- explicit non-closure: no worklist, no fee draft linkage, no bill/document linkage, no frontend
- allowlist:
  - `backend/app/modules/grant_fees/api.py`
  - `backend/app/modules/grant_fees/schemas.py`
  - `backend/app/modules/grant_fees/service.py`
  - `backend/tests/test_grant_fee_state_machine_api.py`
- verification:
  - `python3 -m ruff check backend/app/modules/grant_fees/api.py backend/app/modules/grant_fees/schemas.py backend/app/modules/grant_fees/service.py backend/tests/test_grant_fee_state_machine_api.py`
  - `cd backend && PYTHONPATH=. pytest -q tests/test_grant_fee_state_machine_api.py`
  - `./scripts/task_validate.sh GFSM-BE-01`
- dependency notes: depends on committed `GF-PRE`; owns all grant-fee backend state-machine files

### GFSM-QA-01
- task file path: `tasks/postenhancement/backend/GFSM-QA-01.md`
- closure slice: gate audit, evidence audit, and story close summary for `GF-SM`
- explicit non-closure: no product code changes
- allowlist:
  - `artifacts/GFSM-BE-01/**`
  - `artifacts/GFSM-QA-01/**`
- verification:
  - `./scripts/task_validate.sh GFSM-BE-01`
  - `./scripts/task_validate.sh GFSM-QA-01`
- dependency notes: final wave after backend task passes

## Waves
- Wave 1: `GFSM-BE-01`
- Wave 2: `GFSM-QA-01`

## Serialized Shared-file Decisions
- `backend/app/modules/grant_fees/api.py` is owned only by `GFSM-BE-01`
- `backend/app/modules/grant_fees/schemas.py` is owned only by `GFSM-BE-01`
- `backend/app/modules/grant_fees/service.py` is owned only by `GFSM-BE-01`
