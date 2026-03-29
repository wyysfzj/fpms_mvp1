# Documents Step1-2 Wizard Prerequisite Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolve the blocked Step 2 field contract before resuming the document wizard frontend work.

**Architecture:** Treat the missing Step 2 field contract as a prerequisite planning story. First freeze which fields remain in scope and where they live, then either shrink the wizard story or create a schema-bearing prerequisite story before resuming frontend implementation.

**Tech Stack:** FastAPI, SQLAlchemy, Vue 3

---

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `BE-first`
- `evidence_cost`: `medium`
- `chosen_runbook`: `P0-prereq-heavy-story`

## Immediate Outcome

- Suspend:
  - `DOCWIZ-FE-SHELL-01`
  - `DOCWIZ-FE-STEP1-01`
  - `DOCWIZ-FE-STEP2-01`
- Keep:
  - `DOCWIZ-BE-01` as `PASS`

## Required Decision Path

### Option A: Narrow the story

- Freeze Step 2 to only the fields already supported by the current documents contract:
  - `title`
  - `doc_date`
  - `ref_no`
  - `extra_data`
  - `reply_to_id`
  - `need_reply`
- Then rewrite the wizard spec/plan/task files and resume FE work.

### Option B: Add a prerequisite story

- Create a new prerequisite story for documents field support covering the approved Step 2 field set.
- That prerequisite story must decide:
  - whether fields become structured columns
  - whether some fields move into `extra_data`
  - whether any field is cut from current MVP closure
- Only after that story is complete can the wizard FE tasks resume.

## Next Atomic Planning Tasks

1. `DOCWIZ-PREREQ-PLAN-01`
- Closure slice: freeze the authoritative Step 2 field set and storage contract.
- Non-closure: no product code changes.

2. `DOCWIZ-PREREQ-DB-01` or `DOCWIZ-PREREQ-CONTRACT-01`
- Chosen only after `DOCWIZ-PREREQ-PLAN-01`.
- If schema is required, this becomes a schema-bearing prerequisite story.
- If not, it becomes a contract-reduction task and the wizard story is replanned.

## Acceptance

- The implementer for the wizard no longer has to guess where `NeedNotifyAgent / InternalDocNo / Summary / Remark / simple input fields` belong.
- A replacement wizard plan exists that is decision-complete.
