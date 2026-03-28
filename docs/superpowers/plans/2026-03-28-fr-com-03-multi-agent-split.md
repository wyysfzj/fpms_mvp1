# FR-COM-03 Multi-Agent Split Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add case-level current effective multi-agent split configuration and use it to generate or recompute separate per-agent commission records while preserving the existing settlement/report flow.

**Architecture:** This story is prerequisite-heavy and must be executed in serialized waves. The design adds normalized case split persistence first, then extends case contracts, then teaches commission generation/recompute to consume the split configuration, and finally exposes case-page maintenance UI and QA evidence.

**Tech Stack:** FastAPI, SQLAlchemy ORM, Alembic, Vue 3, TypeScript, SQLite, Ruff, Pytest

---

## Story Shape

- shared_file_density: `high`
- prereq_dependency_density: `high`
- be_fe_coupling: `chained (BE -> FE)`
- evidence_cost: `high`

## Chosen Runbook

- chosen_runbook: `P0-prereq-heavy-story`

## Runbook Rationale

- Why this runbook fits the story shape:
  - The story depends on new durable persistence before service and frontend work can be implemented safely.
  - Multiple shared ownership files exist across `cases`, `commission`, shared schemas, and case frontend pages.
  - Frontend work cannot proceed honestly until backend contracts and persistence are frozen.
- Why the other runbooks were not chosen:
  - `P0-single-lane-story`: rejected because this is not a single-lane isolated slice.
  - `P0-multi-lane-parallel-story`: rejected because prerequisites and shared files force serialization for the early waves.
  - `P0-frontend-heavy-story`: rejected because the true blocker is persistence and backend contract design, not UI complexity.

## Preflight Dependency Audit

- Permission / RBAC prerequisites:
  - Reuse existing case edit authorization patterns for case-page split maintenance.
  - Restrict selectable split members to internal users with agent-related roles/permissions.
- State machine reachability:
  - Existing commission generation and settlement states remain reachable if the split service only rewrites unfrozen commission rows.
- Shared ownership file conflicts:
  - `backend/app/modules/cases/models.py`
  - `backend/app/modules/cases/schemas.py`
  - `backend/app/modules/cases/api.py`
  - `backend/app/modules/cases/service.py` if required by repo pattern
  - `backend/app/modules/commission/service.py`
  - `backend/app/modules/commission/models.py`
  - `backend/tests/test_commission_e2e.py`
  - `frontend/src/modules/cases/pages/*`
  - `frontend/src/modules/cases/components/*`
  - `frontend/src/api/cases.ts`
  - `frontend/src/api/cases.types.ts`
- Shared test file conflicts:
  - `backend/tests/test_commission_e2e.py`
  - case frontend test files if they already exist
- Router / shared schema / export helper / permission registry / shared API client checks:
  - Backend router changes should be avoided unless a new endpoint is required.
  - Shared schema updates must be serialized.
  - Shared frontend case API types must be serialized.

## Execution Mode

- Mode: `serialized subagent`
- Why this execution mode is safe for the current story shape:
  - Early prerequisite waves must land before dependent waves can start.
  - Shared ownership files make concurrent implementation unsafe.
  - Separate workers can still be used per atomic task, but wave order must remain serialized.

## Baseline Promotion Protocol

- Establish the baseline before editing and record whether the worktree is clean or dirty.
- If dirty, capture task-scoped baseline artifacts before each task edits its allowlist.
- Reviewer validation compares the task delta against the recorded baseline, not an assumed clean commit range.
- Accepted work becomes the next task wave baseline only after verification and task-gate success.

## Replan Triggers

- A new shared prerequisite is discovered in settlement/report flows.
- The split persistence contract requires additional shared model ownership not covered by the current wave.
- The case-page UI needs a new shared frontend selector/store not captured in the allowlist.
- Commission recompute semantics depend on a second unplanned closure slice.
- Reviewer determines a task is trying to close both persistence and business behavior in one slice.

## File Structure

- `backend/alembic/versions/<new>_create_t_case_agent_split.py`
- `backend/alembic/versions/frcom03_db_01_create_t_case_agent_split.py`
  - Creates durable case split persistence with SQLite-safe definitions.
- `backend/app/modules/cases/models.py`
  - Owns ORM mapping for case split details.
- `backend/app/modules/cases/schemas.py`
  - Exposes case split read/write contracts.
- `backend/app/modules/cases/api.py`
  - Saves and returns case split configuration with case payloads or dedicated case-level endpoints.
- `backend/app/modules/commission/service.py`
  - Consumes case split configuration during generation and unfrozen recompute.
- `backend/tests/test_commission_e2e.py`
  - Verifies multi-agent split generation, recompute boundary, and settlement freeze boundary.
- `backend/tests/test_case_agent_split_api.py`
  - Verifies case split contract validation and persistence rules.
- `frontend/src/api/cases.ts`
  - Adds case split request/response typing helpers.
- `frontend/src/api/cases.types.ts`
  - Adds case split types.
- `frontend/src/modules/cases/pages/CaseEdit.vue`
  - Hosts the Chinese UI split maintenance block.
- `frontend/src/modules/cases/components/CaseAgentSplitEditor.vue`
  - Encapsulates split row editing and ratio validation.

## Atomic Task Inventory

- `FRCOM03-DB-01`:
  - Task file path: `tasks/postenhancement/backend/FRCOM03-DB-01.md`
  - Owner role: `worker`
  - Exact closure slice:
    - Add SQLite-safe durable case split persistence and ORM mapping only.
  - Explicit non-closure:
    - Does not add case API contract, commission generation logic, or frontend UI.
  - Required verification:
    - `ruff check backend/app/modules/cases/models.py`
    - `cd backend && pytest -q tests/test_commission_e2e.py -k 'not multi_agent_split'`
    - task-scoped migration verification command to be finalized in task file
  - Dependency notes:
    - First prerequisite wave.
  - Remaining follow-up task ids:
    - `FRCOM03-BE-CASE-01`
    - `FRCOM03-BE-COM-01`
    - `FRCOM03-FE-CASE-01`
    - `FRCOM03-QA-01`
  - Allowlist:
    - `backend/alembic/versions/frcom03_db_01_create_t_case_agent_split.py`
    - `backend/app/modules/cases/models.py`
  - Done definition:
    - Durable split table exists, ORM mapping is loaded, SQLite-safe constraints are in place, and no business logic is silently absorbed.

- `FRCOM03-BE-CASE-01`:
  - Task file path: `tasks/postenhancement/backend/FRCOM03-BE-CASE-01.md`
  - Owner role: `worker`
  - Exact closure slice:
    - Add case contract read/write support for current effective split configuration only.
  - Explicit non-closure:
    - Does not generate split commissions or add case-page UI.
  - Required verification:
    - `ruff check backend/app/modules/cases/api.py backend/app/modules/cases/schemas.py backend/tests/test_case_agent_split_api.py`
    - `cd backend && pytest -q tests/test_case_agent_split_api.py`
  - Dependency notes:
    - Depends on `FRCOM03-DB-01`.
  - Remaining follow-up task ids:
    - `FRCOM03-BE-COM-01`
    - `FRCOM03-FE-CASE-01`
    - `FRCOM03-QA-01`
  - Allowlist:
    - `backend/app/modules/cases/api.py`
    - `backend/app/modules/cases/schemas.py`
    - `backend/tests/test_case_agent_split_api.py`
  - Done definition:
    - Case split config can be validated, saved, and read back with ratio sum and eligible-agent enforcement.

- `FRCOM03-BE-COM-01`:
  - Task file path: `tasks/postenhancement/backend/FRCOM03-BE-COM-01.md`
  - Owner role: `worker`
  - Exact closure slice:
    - Commission generation and unfrozen recompute use current case split config to produce one commission row per agent.
  - Explicit non-closure:
    - Does not redesign settlement/report endpoints or add split-history behavior.
  - Required verification:
    - `ruff check backend/app/modules/commission/service.py backend/tests/test_commission_e2e.py`
    - `cd backend && pytest -q tests/test_commission_e2e.py -k 'multi_agent_split or recompute'`
  - Dependency notes:
    - Depends on `FRCOM03-DB-01` and `FRCOM03-BE-CASE-01`.
  - Remaining follow-up task ids:
    - `FRCOM03-FE-CASE-01`
    - `FRCOM03-QA-01`
  - Allowlist:
    - `backend/app/modules/commission/service.py`
    - `backend/tests/test_commission_e2e.py`
  - Done definition:
    - Split config drives generation and unfrozen recompute, single-agent fallback remains intact, and frozen records are untouched.

- `FRCOM03-FE-CASE-01`:
  - Task file path: `tasks/postenhancement/frontend/FRCOM03-FE-CASE-01.md`
  - Owner role: `worker`
  - Exact closure slice:
    - Add case-page Chinese UI for maintaining current effective split members, roles, and ratios against the approved backend contract.
  - Explicit non-closure:
    - Does not add split-history UX, settlement UI changes, or standalone configuration center behavior.
  - Required verification:
    - `cd frontend && npm run lint -- src/api/cases.ts src/api/cases.types.ts src/modules/cases/pages/CaseEdit.vue src/modules/cases/components/CaseAgentSplitEditor.vue`
    - `cd frontend && npm run typecheck`
  - Dependency notes:
    - Depends on `FRCOM03-BE-CASE-01`.
  - Remaining follow-up task ids:
    - `FRCOM03-QA-01`
  - Allowlist:
    - `frontend/src/api/cases.ts`
    - `frontend/src/api/cases.types.ts`
    - `frontend/src/modules/cases/pages/CaseEdit.vue`
    - `frontend/src/modules/cases/components/CaseAgentSplitEditor.vue`
  - Done definition:
    - User can edit split members on the case page, validation is Chinese and ratio-safe, and the UI stays inside the case-page scope.

- `FRCOM03-QA-01`:
  - Task file path: `tasks/postenhancement/backend/FRCOM03-QA-01.md`
  - Owner role: `monitor`
  - Exact closure slice:
    - Validate the FR-COM-03 item-to-slice ledger and evidence set after all implementation slices complete.
  - Explicit non-closure:
    - Does not implement any new backend or frontend behavior.
  - Required verification:
    - `./scripts/task_validate.sh FRCOM03-DB-01`
    - `./scripts/task_validate.sh FRCOM03-BE-CASE-01`
    - `./scripts/task_validate.sh FRCOM03-BE-COM-01`
    - `./scripts/task_validate.sh FRCOM03-FE-CASE-01`
    - targeted regression checks finalized in task file
  - Dependency notes:
    - Final serialized wave.
  - Remaining follow-up task ids:
    - `None`
  - Allowlist:
    - `artifacts/FRCOM03-QA-01/**`
    - optional audit doc if the manifest requires one
  - Done definition:
    - Every implementation task is independently evidenced, validated, and mapped to the approved closure slice ledger.

## Wave Plan

- Wave 1:
  - Tasks:
    - `FRCOM03-DB-01`
  - Mode:
    - serialized
  - Shared ownership notes:
    - Owns schema and case ORM only. No commission logic or frontend edits in this wave.

- Wave 2:
  - Tasks:
    - `FRCOM03-BE-CASE-01`
  - Mode:
    - serialized
  - Shared ownership notes:
    - Owns case API/schema contract only. Must not absorb commission-service logic.

- Wave 3:
  - Tasks:
    - `FRCOM03-BE-COM-01`
  - Mode:
    - serialized
  - Shared ownership notes:
    - Owns commission-service logic and test evidence only. Must not reopen case contract shape.

- Wave 4:
  - Tasks:
    - `FRCOM03-FE-CASE-01`
  - Mode:
    - serialized
  - Shared ownership notes:
    - Consumes frozen case contract. Must not add settlement/report UI scope.

- Wave 5:
  - Tasks:
    - `FRCOM03-QA-01`
  - Mode:
    - serialized
  - Shared ownership notes:
    - Evidence and audit only.

## Task 1: Write `FRCOM03-DB-01` Task File

**Files:**
- Create: `tasks/postenhancement/backend/FRCOM03-DB-01.md`

- [ ] **Step 1: Write the task definition using the repo atomic template**
- [ ] **Step 2: Ensure it closes only the durable split persistence slice**
- [ ] **Step 3: Cross-check its allowlist against shared ownership rules**
- [ ] **Step 4: Save the task file**
- [ ] **Step 5: Commit the single task-file planning change**

## Task 2: Write `FRCOM03-BE-CASE-01` Task File

**Files:**
- Create: `tasks/postenhancement/backend/FRCOM03-BE-CASE-01.md`

- [ ] **Step 1: Write the task definition using the repo atomic template**
- [ ] **Step 2: Ensure it closes only the case contract slice**
- [ ] **Step 3: Cross-check its allowlist against shared ownership rules**
- [ ] **Step 4: Save the task file**
- [ ] **Step 5: Commit the single task-file planning change**

## Task 3: Write `FRCOM03-BE-COM-01` Task File

**Files:**
- Create: `tasks/postenhancement/backend/FRCOM03-BE-COM-01.md`

- [ ] **Step 1: Write the task definition using the repo atomic template**
- [ ] **Step 2: Ensure it closes only the commission split generation/recompute slice**
- [ ] **Step 3: Cross-check its allowlist against shared ownership rules**
- [ ] **Step 4: Save the task file**
- [ ] **Step 5: Commit the single task-file planning change**

## Task 4: Write `FRCOM03-FE-CASE-01` Task File

**Files:**
- Create: `tasks/postenhancement/frontend/FRCOM03-FE-CASE-01.md`

- [ ] **Step 1: Write the task definition using the repo atomic template**
- [ ] **Step 2: Ensure it closes only the case-page split editor slice**
- [ ] **Step 3: Cross-check its allowlist against shared ownership rules**
- [ ] **Step 4: Save the task file**
- [ ] **Step 5: Commit the single task-file planning change**

## Task 5: Write `FRCOM03-QA-01` Task File

**Files:**
- Create: `tasks/postenhancement/backend/FRCOM03-QA-01.md`

- [ ] **Step 1: Write the task definition using the repo atomic template**
- [ ] **Step 2: Ensure it closes only the audit/evidence slice**
- [ ] **Step 3: Cross-check its allowlist against shared ownership rules**
- [ ] **Step 4: Save the task file**
- [ ] **Step 5: Commit the single task-file planning change**

## Task 6: Execute DB / Model Prerequisite First

**Files:**
- Create: `backend/alembic/versions/frcom03_db_01_create_t_case_agent_split.py`
- Modify: `backend/app/modules/cases/models.py`
- Test: backend migration/test evidence files

- [ ] **Step 1: Write the failing migration/model proof**
- [ ] **Step 2: Run targeted migration proof to verify failure**
- [ ] **Step 3: Implement SQLite-safe schema and ORM mapping**
- [ ] **Step 4: Run task-scoped lint and migration proof**
- [ ] **Step 5: Generate artifacts and commit**

## Task 7: Execute Case Contract Prerequisite

**Files:**
- Modify: `backend/app/modules/cases/api.py`
- Modify: `backend/app/modules/cases/schemas.py`
- Test: `backend/tests/test_case_agent_split_api.py`

- [ ] **Step 1: Write failing case-contract tests for split validation**
- [ ] **Step 2: Run targeted tests to verify failure**
- [ ] **Step 3: Implement minimal read/write contract and validation**
- [ ] **Step 4: Run targeted lint and tests**
- [ ] **Step 5: Generate artifacts and commit**

## Task 8: Execute Commission Split Behavior

**Files:**
- Modify: `backend/app/modules/commission/service.py`
- Modify: `backend/tests/test_commission_e2e.py`

- [ ] **Step 1: Add failing tests for multi-agent generation and unfrozen recompute**
- [ ] **Step 2: Run targeted tests to verify failure**
- [ ] **Step 3: Implement minimal split generation and recompute behavior**
- [ ] **Step 4: Run targeted lint and tests**
- [ ] **Step 5: Generate artifacts and commit**

## Task 9: Execute Case-Page Split UI

**Files:**
- Modify: `frontend/src/api/cases.ts`
- Modify: `frontend/src/api/cases.types.ts`
- Modify: `frontend/src/modules/cases/pages/CaseEdit.vue`
- Create or Modify: `frontend/src/modules/cases/components/CaseAgentSplitEditor.vue`

- [ ] **Step 1: Add failing UI proof or targeted frontend test for split editing**
- [ ] **Step 2: Run targeted frontend verification to verify failure**
- [ ] **Step 3: Implement the minimal Chinese UI split editor**
- [ ] **Step 4: Run targeted lint/type verification**
- [ ] **Step 5: Generate artifacts and commit**

## Task 10: Execute Final QA Close Audit

**Files:**
- Create: `artifacts/FRCOM03-QA-01/summary.md`
- Create: `artifacts/FRCOM03-QA-01/results.jsonl`
- Create: `artifacts/FRCOM03-QA-01/git/diff.patch`

- [ ] **Step 1: Run task gates for each implementation slice**
- [ ] **Step 2: Build the item-to-slice ledger for FR-COM-03**
- [ ] **Step 3: Confirm evidence completeness**
- [ ] **Step 4: Record residual gaps or mark none**
- [ ] **Step 5: Commit audit artifacts if required by workflow**
