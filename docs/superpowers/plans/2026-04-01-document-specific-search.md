# P2 #19 Document-specific Search Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the spec-to-carrier mapping prerequisite for spec 9.3.2 document-specific search before reopening the backend/frontend query enhancement story.

**Architecture:** Execute this as a prereq-heavy story. First freeze the stable mapping from spec query terms to current `documents` repo carriers; only after that prerequisite passes may the backend query contract and frontend document list enhancement continue in a follow-up wave.

**Tech Stack:** FastAPI, SQLAlchemy, Vue 3, TypeScript, Element Plus, SQLite

---

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: medium
- be_fe_coupling: chained (PRE -> BE -> FE)
- evidence_cost: medium

## chosen_runbook

- P0-prereq-heavy-story

## Batch Manifest

### DOCSEARCH-PRE-01

- task file path: `tasks/postenhancement/backend/DOCSEARCH-PRE-01.md`
- closure slice: freeze and document the stable mapping between spec 9.3.2 search terms and current repo carriers as:
  - `DocType` -> no direct carrier, never equate to `direction`
  - `TemplateCode` -> `DocTemplate.code`
  - `DocName` -> `Document.title`
  - `NeedReply` -> `Document.need_reply`
  - `已Reply` -> `Document.reply_date is not null`
  - `Reply` -> display/query synonym for `已Reply`, not a new carrier
  update the frozen spec/plan/task wording so downstream implementation has an executable contract
- explicit non-closure: no product code changes, no backend endpoint changes, no frontend changes, no dispatch/reply/export/reporting, no schema changes unless a new follow-up prerequisite is explicitly created
- allowlist:
  - `docs/superpowers/specs/2026-04-01-document-specific-search-design.md`
  - `docs/superpowers/plans/2026-04-01-document-specific-search.md`
  - `tasks/postenhancement/backend/DOCSEARCH-PRE-01.md`
  - `tasks/postenhancement/backend/DOCSEARCH-BE-01.md`
  - `tasks/postenhancement/frontend/DOCSEARCH-FE-01.md`
  - `tasks/postenhancement/backend/DOCSEARCH-QA-01.md`
- verification:
  - `./scripts/task_validate.sh DOCSEARCH-PRE-01`
- dependency notes: must pass before reopening backend/frontend execution

### DOCSEARCH-QA-01

- task file path: `tasks/postenhancement/backend/DOCSEARCH-QA-01.md`
- closure slice: gate audit, evidence audit, and prerequisite close summary for `P2 #19` replanning batch
- explicit non-closure: no product code changes
- allowlist:
  - `artifacts/DOCSEARCH-PRE-01/**`
  - `artifacts/DOCSEARCH-QA-01/**`
- verification:
  - `./scripts/task_validate.sh DOCSEARCH-PRE-01`
  - `./scripts/task_validate.sh DOCSEARCH-QA-01`
- dependency notes: final wave after prerequisite task pass

## Deferred / Blocked Follow-up Tasks

### DOCSEARCH-BE-01

- task file path: `tasks/postenhancement/backend/DOCSEARCH-BE-01.md`
- status: blocked pending `DOCSEARCH-PRE-01`
- reason: current frozen filters/projection must not start until the stable `DocType` / `TemplateCode` / `DocName` / `NeedReply` / `已Reply` mapping is frozen

### DOCSEARCH-FE-01

- task file path: `tasks/postenhancement/frontend/DOCSEARCH-FE-01.md`
- status: deferred pending `DOCSEARCH-PRE-01` and rewritten backend contract
- reason: frontend filter wiring cannot close until backend mapping prerequisite freezes the executable contract and carrier semantics

## Waves

- Wave 1: `DOCSEARCH-PRE-01`
- Wave 2: `DOCSEARCH-QA-01`

## Serialized Shared-file Decisions

- `docs/superpowers/specs/2026-04-01-document-specific-search-design.md` is owned only by `DOCSEARCH-PRE-01`
- `docs/superpowers/plans/2026-04-01-document-specific-search.md` is owned only by `DOCSEARCH-PRE-01`
- `tasks/postenhancement/backend/DOCSEARCH-PRE-01.md` is owned only by `DOCSEARCH-PRE-01`
- `tasks/postenhancement/backend/DOCSEARCH-BE-01.md` is owned only by `DOCSEARCH-PRE-01`
- `tasks/postenhancement/frontend/DOCSEARCH-FE-01.md` is owned only by `DOCSEARCH-PRE-01`
- `tasks/postenhancement/backend/DOCSEARCH-QA-01.md` is owned only by `DOCSEARCH-PRE-01`
