# P2 #15 Grant Fee Workflow Decomposition Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Freeze `P2 #15` into a prerequisite-first workflow program so `T_GrantFeeTask` and the grant-fee chain can be implemented safely as separate stories.

**Architecture:** Treat the review item as a prerequisite-heavy workflow program. Create `T_GrantFeeTask` carrier first, then layer state machine, worklist, and fee-draft linkage as separate stories with serialized shared-file ownership.

**Tech Stack:** FastAPI, SQLAlchemy, Alembic, Vue 3, Element Plus, SQLite

---

## Story Shape Classification
- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: shared multi-lane workflow
- evidence_cost: medium

## chosen_runbook
- P0-prereq-heavy-story

## Decomposition Ledger

### GF-PRE
- role: prerequisite story
- closure: `T_GrantFeeTask` carrier, schema/migration, module skeleton, permission namespace freeze
- non-closure: no worklist, no state-machine actions, no draft linkage, no bill/doc/reminder linkage

### GF-SM
- role: workflow engine story
- closure: minimal state machine + trigger + state transition service/action contract
- non-closure: no worklist UI, no bill/doc/reminder linkage

### GF-WL
- role: workflow page story
- closure: grant-fee worklist/workbench list UI and list contract
- non-closure: no detail/edit, no bill/doc/reminder linkage

### GF-DRAFT
- role: workflow linkage story
- closure: generate `GRANT_FEE` fee drafts from eligible grant-fee tasks with idempotent protection
- non-closure: no bill linkage, no document/reminder linkage

### Deferred
- `GF-DETAIL`
- `GF-BILL`
- `GF-DOC`
- `GF-RPT`
- `GF-SEARCH`
- `GF-IO`

## Current Recommendation

1. `GF-PRE`, recommended
2. `GF-SM`
3. `GF-WL`
4. `GF-DRAFT`

## Shared-file Serialization Notes

- `backend/app/api/router.py` must be serialized if new module routers are introduced
- `backend/app/modules/fees/models.py` or equivalent carrier file must be owned by prerequisite/model wave only
- shared backend schemas and permission registry must be serialized
- `frontend/src/router/index.ts` and shared `frontend/src/api/*.ts` files must be serialized across workflow stories

## No Execution Yet

- This plan intentionally stops at decomposition.
- Do not start implementation until one exact slice is selected:
  - `GF-PRE`
  - `GF-SM`
  - `GF-WL`
  - `GF-DRAFT`
