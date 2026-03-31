# GF-DRAFT Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the first-round `GrantFeeTask -> FeeDraft` generation linkage with minimal FE trigger and strict non-closure boundaries.

**Architecture:** Execute this as a frontend-heavy story with serialized backend-then-frontend ownership. Backend closes generate-draft linkage and idempotency first, frontend turns the reserved button into a minimal trigger second, then QA close audits the story.

**Tech Stack:** FastAPI, SQLAlchemy, Vue 3, TypeScript, Element Plus, SQLite

---

## Story Shape Classification
- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: chained (BE -> FE)
- evidence_cost: medium

## chosen_runbook
- P0-frontend-heavy-story

## Batch Manifest

### GFDRAFT-BE-01
- task file path: `tasks/postenhancement/backend/GFDRAFT-BE-01.md`
- closure slice: implement grant-fee generate-draft backend action with precondition checks, idempotency, minimal FeeDraft/FeeItem creation, and draft_generated writeback
- explicit non-closure: no bill linkage, no document/reminder linkage, no detail/edit, no frontend
- allowlist:
  - `backend/app/modules/grant_fees/api.py`
  - `backend/app/modules/grant_fees/schemas.py`
  - `backend/app/modules/grant_fees/service.py`
  - `backend/tests/test_grant_fee_draft_linkage_api.py`
- verification:
  - `python3 -m ruff check backend/app/modules/grant_fees/api.py backend/app/modules/grant_fees/schemas.py backend/app/modules/grant_fees/service.py backend/tests/test_grant_fee_draft_linkage_api.py`
  - `cd backend && PYTHONPATH=. pytest -q tests/test_grant_fee_draft_linkage_api.py`
  - `./scripts/task_validate.sh GFDRAFT-BE-01`
- dependency notes: depends on committed `GF-PRE`, `GF-SM`, and `GF-WL`; owns grant-fee backend linkage files

### GFDRAFT-FE-01
- task file path: `tasks/postenhancement/frontend/GFDRAFT-FE-01.md`
- closure slice: implement minimal frontend trigger for grant-fee draft generation from the dedicated worklist page
- explicit non-closure: no complex batch selector, no result modal platform, no retry UI, no bill/document linkage
- allowlist:
  - `frontend/src/api/grantFees.ts`
  - `frontend/src/api/grantFees.types.ts`
  - `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`
  - `frontend/tests/grant-fee-draft-linkage.smoke.md`
- verification:
  - `cd frontend && npm run lint -- src/api/grantFees.ts src/api/grantFees.types.ts src/modules/grantFees/pages/GrantFeeTaskList.vue`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh GFDRAFT-FE-01`
- dependency notes: serialize after `GFDRAFT-BE-01`; owns grant-fee frontend trigger files

### GFDRAFT-QA-01
- task file path: `tasks/postenhancement/backend/GFDRAFT-QA-01.md`
- closure slice: gate audit, evidence audit, and story close summary for `GF-DRAFT`
- explicit non-closure: no product code changes
- allowlist:
  - `artifacts/GFDRAFT-BE-01/**`
  - `artifacts/GFDRAFT-FE-01/**`
  - `artifacts/GFDRAFT-QA-01/**`
- verification:
  - `./scripts/task_validate.sh GFDRAFT-BE-01`
  - `./scripts/task_validate.sh GFDRAFT-FE-01`
  - `./scripts/task_validate.sh GFDRAFT-QA-01`
- dependency notes: final wave after backend and frontend tasks pass

## Waves
- Wave 1: `GFDRAFT-BE-01`
- Wave 2: `GFDRAFT-FE-01`
- Wave 3: `GFDRAFT-QA-01`

## Serialized Shared-file Decisions
- `backend/app/modules/grant_fees/api.py` is owned only by `GFDRAFT-BE-01`
- `backend/app/modules/grant_fees/schemas.py` is owned only by `GFDRAFT-BE-01`
- `backend/app/modules/grant_fees/service.py` is owned only by `GFDRAFT-BE-01`
- `frontend/src/api/grantFees.ts|grantFees.types.ts` are owned only by `GFDRAFT-FE-01`
- `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue` is owned only by `GFDRAFT-FE-01`
