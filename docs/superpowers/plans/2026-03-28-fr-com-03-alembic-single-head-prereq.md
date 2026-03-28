# FR-COM-03 Alembic Single-Head Prerequisite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore the repository Alembic graph to a single head so the blocked `FRCOM03-BE-COM-01` pytest command can run against the existing test fixture.

**Architecture:** This is a single-lane prerequisite repair. Add one empty Alembic merge revision that points at the two current heads, verify the repo returns to a single head, and then hand control back to the blocked commission task for re-verification.

**Tech Stack:** Alembic, SQLAlchemy, SQLite, Pytest

---

## Story Shape

- shared_file_density: `low`
- prereq_dependency_density: `medium`
- be_fe_coupling: `backend-only`
- evidence_cost: `low`

## Chosen Runbook

- chosen_runbook: `P0-single-lane-story`

## File Structure

- `backend/alembic/versions/<new>_merge_frcom03_and_pe_fr_fe_06_heads.py`
  - Owns the Alembic graph repair only.
- `tasks/postenhancement/backend/FRCOM03-DB-MERGE-01.md`
  - Atomic task definition for the prerequisite repair.

## Atomic Task Inventory

- `FRCOM03-DB-MERGE-01`:
  - Task file path: `tasks/postenhancement/backend/FRCOM03-DB-MERGE-01.md`
  - Owner role: `worker`
  - Exact closure slice:
    - Add one Alembic merge revision that collapses the current two heads into a single head.
  - Explicit non-closure:
    - Does not modify commission code, tests, fixture setup, or any prior migration contents.
  - Required verification:
    - `ruff check backend/alembic/versions/*.py`
    - `cd backend && alembic heads`
    - `cd backend && alembic upgrade head`
    - `./scripts/task_validate.sh FRCOM03-DB-MERGE-01`
  - Dependency notes:
    - Serialized prerequisite lane; must finish before retrying `FRCOM03-BE-COM-01`.
  - Remaining follow-up task ids:
    - `FRCOM03-BE-COM-01`
  - Allowlist:
    - `backend/alembic/versions/*.py`
  - Done definition:
    - The repo has exactly one Alembic head and the standard upgrade path succeeds.

## Wave Plan

- Wave 1:
  - Tasks:
    - `FRCOM03-DB-MERGE-01`
  - Mode:
    - serialized
  - Shared ownership notes:
    - Owns Alembic version graph only.

### Task 1: Write `FRCOM03-DB-MERGE-01` Task File

**Files:**
- Create: `tasks/postenhancement/backend/FRCOM03-DB-MERGE-01.md`

- [ ] **Step 1: Write the atomic task definition**
- [ ] **Step 2: Lock the closure slice to merge-revision repair only**
- [ ] **Step 3: Save the task file**

### Task 2: Execute the Alembic Graph Repair

**Files:**
- Create: `backend/alembic/versions/<new>_merge_frcom03_and_pe_fr_fe_06_heads.py`

- [ ] **Step 1: Record baseline and current heads**
- [ ] **Step 2: Add the empty merge revision with the two current heads as parents**
- [ ] **Step 3: Run `cd backend && alembic heads` and confirm one head remains**
- [ ] **Step 4: Run `cd backend && alembic upgrade head` against the repo fixture path**
- [ ] **Step 5: Generate evidence and task gate output**
