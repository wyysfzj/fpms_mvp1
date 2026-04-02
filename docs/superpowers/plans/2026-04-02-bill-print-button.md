# P2 #20 Bill Print Button Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the missing first-round bill print entry on `BillList` by reusing the existing billing print backend contract and the existing FE `printBill` API, without expanding into preview/export/email/history.

**Architecture:** Execute this as a single-lane frontend story. Reuse the existing `/bills/{bill_id}/print` backend route and existing `printBill` client helper. Close the user-visible gap in `BillList.vue`, then run a QA/evidence close task.

**Tech Stack:** FastAPI, Vue 3, TypeScript, Element Plus, SQLite

---

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: frontend-only on existing backend contract
- evidence_cost: medium

## chosen_runbook

- P0-single-lane-story

## Batch Manifest

### BILLPRINT-FE-01

- task file path: `tasks/postenhancement/frontend/BILLPRINT-FE-01.md`
- closure slice: add the first-round bill print entry to `BillList.vue` by reusing the existing `printBill` FE API and existing detail-page print/download interaction semantics
- explicit non-closure: no backend changes, no preview page, no batch print, no PDF export, no email, no print history, no template changes
- allowlist:
  - `frontend/src/modules/billing/pages/BillList.vue`
- verification:
  - `cd frontend && npm run lint -- src/modules/billing/pages/BillList.vue`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh BILLPRINT-FE-01`
- dependency notes: no prerequisite; reuse existing `printBill` and existing backend print route without editing them

### BILLPRINT-QA-01

- task file path: `tasks/postenhancement/backend/BILLPRINT-QA-01.md`
- closure slice: gate audit, evidence audit, and close summary for the first-round `P2 #20` bill print button story
- explicit non-closure: no product code changes
- allowlist:
  - `artifacts/BILLPRINT-FE-01/**`
  - `artifacts/BILLPRINT-QA-01/**`
- verification:
  - `./scripts/task_validate.sh BILLPRINT-FE-01`
  - `./scripts/task_validate.sh BILLPRINT-QA-01`
- dependency notes: final wave after frontend task passes

## Waves

- Wave 1: `BILLPRINT-FE-01`
- Wave 2: `BILLPRINT-QA-01`

## Serialized Shared-file Decisions

- `frontend/src/modules/billing/pages/BillList.vue` is owned only by `BILLPRINT-FE-01`
