# P1 #5 多代理人提成分成 FE Edit Consistency Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement case-side create/edit split exposure consistency before any detail viewing or settlement exposure work continues.

**Architecture:** Treat this wave as a frontend single-lane implementation slice. The active task reuses the existing split editor, aligns create/edit validation semantics, and wires create payload submission, while keeping detail viewing, settlement exposure, and router work deferred.

**Tech Stack:** Vue 3, Element Plus, existing cases API/types, Superpowers workflow

---

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `frontend implementation on top of frozen backend semantics`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Current Recommendation

1. `COMMSPLIT-FE-EDIT-01`
2. `COMMSPLIT-QA-08`

## Frozen Decision Snapshot

- `CaseCreate.vue` gains a `代理人分摊` entry consistent with `CaseEdit.vue`
- `CaseAgentSplitEditor.vue` is reused
- create/edit split validation semantics stay aligned
- `second_agent_id` remains context-only for multi-agent entry

## Decomposition Ledger

### `COMMSPLIT-FE-EDIT-01`

- role: create/edit split consistency implementation
- closure:
  - add split entry section to create page
  - reuse split editor
  - align split validation semantics
  - submit `agent_splits` from create page
- non-closure:
  - no detail viewing
  - no settlement exposure
  - no router/menu changes

### `COMMSPLIT-QA-08`

- role: FE edit-consistency close audit
- closure:
  - audit the FE implementation evidence
  - verify the create/edit consistency result and residual gaps
- non-closure:
  - no product code changes

### Deferred

- `COMMSPLIT-FE-VIEW-01`
- settlement read-only exposure
- router/menu changes
- report/payout/export UI

## Shared-file Serialization Notes

- `frontend/src/api/cases.ts` and `frontend/src/api/cases.types.ts` are shared FE ownership files, but this slice should avoid changing them unless execution proves it is strictly necessary.
- `frontend/src/modules/cases/components/CaseAgentSplitEditor.vue` is shared with case edit and must stay serialized inside this single wave.

## Atomic Task Inventory

### `COMMSPLIT-FE-EDIT-01`

- Task file path:
  - `tasks/postenhancement/frontend/COMMSPLIT-FE-EDIT-01.md`
- Owner role:
  - `worker`
- Exact closure slice:
  - implement create/edit split exposure consistency only
- Explicit non-closure:
  - no detail viewing, no settlement exposure, no router/menu changes, no backend changes
- Required verification:
  - `cd frontend && npm run lint -- src/modules/cases/pages/CaseCreate.vue src/modules/cases/components/CaseAgentSplitEditor.vue`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh COMMSPLIT-FE-EDIT-01`
- Dependency notes:
  - follows `COMMSPLIT-FE-01`
- Remaining follow-up task ids:
  - `COMMSPLIT-FE-VIEW-01`
  - `COMMSPLIT-QA-08`
- Allowlist:
  - `frontend/src/modules/cases/pages/CaseCreate.vue`
  - `frontend/src/modules/cases/components/CaseAgentSplitEditor.vue`
  - `tasks/postenhancement/frontend/COMMSPLIT-FE-EDIT-01.md`
  - `tasks/postenhancement/frontend/COMMSPLIT-QA-08.md`
- File access rule:
  - `tasks/postenhancement/frontend/COMMSPLIT-QA-08.md` is reference-only for scope; edits, if any, are limited to audit wording alignment and do not transfer QA ownership into this wave
- Done definition:
  - create page exposes split editing with aligned validation and submit wiring, with no detail/settlement slice absorbed

### `COMMSPLIT-QA-08`

- Task file path:
  - `tasks/postenhancement/frontend/COMMSPLIT-QA-08.md`
- Owner role:
  - `monitor`
- Exact closure slice:
  - validate the FE edit-consistency evidence and close summary only
- Explicit non-closure:
  - no product code changes
- Required verification:
  - `./scripts/task_validate.sh COMMSPLIT-FE-EDIT-01`
  - `./scripts/task_validate.sh COMMSPLIT-QA-08`
- Dependency notes:
  - final serialized wave after `COMMSPLIT-FE-EDIT-01`
- Remaining follow-up task ids:
  - `None`
- Allowlist:
  - `artifacts/COMMSPLIT-QA-08/**`
  - `docs/superpowers/specs/2026-04-03-commission-split-fe-edit-consistency-design.md`
  - `docs/superpowers/plans/2026-04-03-commission-split-fe-edit-consistency.md`
  - `tasks/postenhancement/frontend/COMMSPLIT-FE-EDIT-01.md`
  - `tasks/postenhancement/frontend/COMMSPLIT-QA-08.md`
- File access rule:
  - `COMMSPLIT-QA-08` owns its own wording and evidence audit
- Done definition:
  - FE edit-consistency evidence is mapped, close decision is recorded, and residual implementation stories are explicit

## Wave-based Batch Manifest

### Wave 1

- `COMMSPLIT-FE-EDIT-01`

### Wave 2

- `COMMSPLIT-QA-08`

## No Execution Yet

- This plan intentionally stops at create/edit split consistency.
- Do not start implementation until one exact slice is selected:
  - `COMMSPLIT-FE-EDIT-01`
  - `COMMSPLIT-FE-VIEW-01`
