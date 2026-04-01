# P2 #18 Advanced Case Search Filters Implementation Plan (Replanned)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reclassify `P2 #18` into a prerequisite-heavy program after discovering that `applicant_id` cannot be honestly implemented against current carriers. Execute the prerequisite as serialized `DB -> BE payload -> QA`, then defer the actual query enhancement story until that prerequisite closes.

**Architecture:** Execute this as a prerequisite-heavy story. First add the carrier and SQLite-safe migration for `T_CaseApplicant.applicant_id`, then wire the new field through case full create/update payload and persistence path, then close with a prerequisite QA audit. Only after that should a follow-up `CASEFILTER-QRY` story reopen backend query contract and frontend case list filters.

**Tech Stack:** FastAPI, SQLAlchemy, Vue 3, TypeScript, Element Plus, SQLite

---

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: high
- be_fe_coupling: chained (DB -> BE -> FE)
- evidence_cost: medium

## chosen_runbook

- P0-prereq-heavy-story

## Batch Manifest

## Decomposition Ledger

- `CASEFILTER-PRE`
  - prerequisite slice
  - establishes stable query path for `applicant_id`
- `CASEFILTER-QRY`
  - follow-up query enhancement story
  - blocked on `CASEFILTER-PRE`

## Batch Manifest

### CASEFILTER-DB-01

- task file path: `tasks/postenhancement/backend/CASEFILTER-DB-01.md`
- closure slice: add nullable `T_CaseApplicant.applicant_id` carrier, SQLite-safe migration, and index/reference needed for a stable applicant masterdata query path
- explicit non-closure: no case create/update payload wiring yet, no `/cases` query enhancement, no frontend, no `patent_no`, no `fee_status`
- allowlist:
  - `backend/app/modules/cases/models.py`
  - `backend/alembic/versions/casefilter_pre_01_case_applicant_masterdata_link.py`
  - `backend/tests/test_case_applicant_masterdata_link_schema.py`
- verification:
  - `python3 -m ruff check backend/app/modules/cases/models.py backend/alembic/versions/casefilter_pre_01_case_applicant_masterdata_link.py backend/tests/test_case_applicant_masterdata_link_schema.py`
  - `cd backend && PYTHONPATH=. pytest -q tests/test_case_applicant_masterdata_link_schema.py`
  - `cd backend && DATABASE_URL=sqlite:////tmp/fpms_casefilter_pre_verify_$$.db alembic upgrade head`
  - `./scripts/task_validate.sh CASEFILTER-DB-01`
- dependency notes: first wave; payload wiring depends on stable carrier

### CASEFILTER-PRE-01

- task file path: `tasks/postenhancement/backend/CASEFILTER-PRE-01.md`
- closure slice: add `applicant_id` to case full create/update payload and persistence path once the new case-applicant carrier exists
- explicit non-closure: no `/cases` query enhancement, no frontend, no `patent_no`, no `fee_status`, no detail response changes, no limited update changes
- allowlist:
  - `backend/app/modules/cases/schemas.py`
  - `backend/app/modules/cases/service.py`
  - `backend/tests/test_case_applicant_masterdata_link_write_path.py`
- verification:
  - `python3 -m ruff check backend/app/modules/cases/schemas.py backend/app/modules/cases/service.py backend/tests/test_case_applicant_masterdata_link_write_path.py`
  - `cd backend && PYTHONPATH=. pytest -q tests/test_case_applicant_masterdata_link_write_path.py`
  - `./scripts/task_validate.sh CASEFILTER-PRE-01`
- dependency notes: serialize after `CASEFILTER-DB-01`; owns full create/update payload and write-path wiring

### CASEFILTER-QA-01

- task file path: `tasks/postenhancement/backend/CASEFILTER-QA-01.md`
- closure slice: gate audit, evidence audit, and prerequisite close summary for `CASEFILTER-PRE`
- explicit non-closure: no product code changes
- allowlist:
  - `artifacts/CASEFILTER-DB-01/**`
  - `artifacts/CASEFILTER-PRE-01/**`
  - `artifacts/CASEFILTER-QA-01/**`
- verification:
  - `./scripts/task_validate.sh CASEFILTER-DB-01`
  - `./scripts/task_validate.sh CASEFILTER-PRE-01`
  - `./scripts/task_validate.sh CASEFILTER-QA-01`
- dependency notes: final wave after DB and payload slices pass

## Waves

- Wave 1: `CASEFILTER-DB-01`
- Wave 2: `CASEFILTER-PRE-01`
- Wave 3: `CASEFILTER-QA-01`

## Serialized Shared-file Decisions

- `backend/app/modules/cases/models.py` is owned only by `CASEFILTER-DB-01`
- `backend/alembic/versions/casefilter_pre_01_case_applicant_masterdata_link.py` is owned only by `CASEFILTER-DB-01`
- `backend/app/modules/cases/schemas.py` is owned only by `CASEFILTER-PRE-01`
- `backend/app/modules/cases/service.py` is owned only by `CASEFILTER-PRE-01`
