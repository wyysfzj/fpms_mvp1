# P1 #5 多代理人提成分成 Existing Carrier Reclassification Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Re-assess the existing `CaseAgentSplit` carrier and decide whether `COMMSPLIT-DB-01` should remain a DB prerequisite or be reclassified before any implementation resumes.

**Architecture:** Treat this wave as a correction-first prerequisite checkpoint. The active task evaluates existing carrier facts across case and commission modules, rewrites the follow-up mapping, and explicitly defers all implementation slices. No schema, service, API, or frontend implementation happens in this wave.

**Tech Stack:** Markdown specs/plans, existing case/commission models and services, Superpowers workflow

---

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `shared commission program; carrier status assessment before implementation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Current Recommendation

1. `COMMSPLIT-DB-01`, repurposed as the assessment checkpoint
2. `COMMSPLIT-QA-03`

## Frozen Decision Snapshot

- Existing carrier status:
  - `CaseAgentSplit` is a real persisted and consumed structure, but only as a partial carrier
- Task-tree correction:
  - `COMMSPLIT-DB-01` is narrowed and renamed to an existing-carrier reclassification checkpoint before any DB implementation starts
- DB prerequisite meaning:
  - the old mandatory DB-prerequisite reading is removed
- Deferred implementation stories:
  - `COMMSPLIT-BE-01`
  - `COMMSPLIT-BE-02`
  - `COMMSPLIT-BE-03`
  - `COMMSPLIT-FE-01`

## Decomposition Ledger

### `COMMSPLIT-DB-01`

- role: existing carrier status assessment and reclassification checkpoint
- closure:
  - assess whether `CaseAgentSplit` already constitutes the durable carrier
  - freeze the carrier classification result as partial-carrier, not auxiliary-only
  - decide whether the old DB-prerequisite interpretation should be kept, narrowed, renamed, or removed
  - rewrite the follow-up mapping explicitly
- non-closure:
  - no migration
  - no ORM model
  - no API
  - no calculation
  - no FE

### `COMMSPLIT-QA-03`

- role: reclassification-wave close audit
- closure:
  - audit the assessment-wave evidence
  - verify the frozen carrier classification result and follow-up mapping
- non-closure:
  - no product code changes

### Deferred

- `COMMSPLIT-BE-01`
- `COMMSPLIT-BE-02`
- `COMMSPLIT-BE-03`
- `COMMSPLIT-FE-01`

## Shared-file Serialization Notes

- `docs/superpowers/specs/2026-04-03-commission-split-existing-carrier-reclassification-design.md` must be owned only by `COMMSPLIT-DB-01`
- `docs/superpowers/plans/2026-04-03-commission-split-existing-carrier-reclassification.md` must be owned only by `COMMSPLIT-DB-01`
- `tasks/postenhancement/backend/COMMSPLIT-DB-01.md` must be owned only by `COMMSPLIT-DB-01`
- `tasks/postenhancement/backend/COMMSPLIT-QA-03.md` stays QA-owned; `COMMSPLIT-DB-01` may touch it only to align audit wording with the frozen reclassification result, not to expand QA scope

## Atomic Task Inventory

### `COMMSPLIT-DB-01`

- Task file path:
  - `tasks/postenhancement/backend/COMMSPLIT-DB-01.md`
- Owner role:
  - `worker`
- Exact closure slice:
  - assess the existing `CaseAgentSplit` carrier status and freeze the reclassification result only
- Explicit non-closure:
  - no migration, no ORM model, no API, no calculation, no FE
- Required verification:
  - `./scripts/task_validate.sh COMMSPLIT-DB-01`
- Dependency notes:
  - first and only assessment wave
- Remaining follow-up task ids:
  - `COMMSPLIT-BE-01`
  - `COMMSPLIT-BE-02`
  - `COMMSPLIT-BE-03`
  - `COMMSPLIT-FE-01`
  - `COMMSPLIT-QA-03`
- Allowlist:
  - `docs/superpowers/specs/2026-04-03-commission-split-existing-carrier-reclassification-design.md`
  - `docs/superpowers/plans/2026-04-03-commission-split-existing-carrier-reclassification.md`
  - `tasks/postenhancement/backend/COMMSPLIT-DB-01.md`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-03.md`
- File access rule:
  - `tasks/postenhancement/backend/COMMSPLIT-QA-03.md` is reference-only for scope; edits, if any, are limited to audit phrasing alignment and do not transfer QA ownership into this wave
- Done definition:
  - existing-carrier status is explicit, the old DB-prerequisite assumption is either narrowed or superseded, and no implementation slice is silently absorbed

### `COMMSPLIT-QA-03`

- Task file path:
  - `tasks/postenhancement/backend/COMMSPLIT-QA-03.md`
- Owner role:
  - `monitor`
- Exact closure slice:
  - validate the reclassification-wave evidence and close summary only
- Explicit non-closure:
  - no product code changes
- Required verification:
  - `./scripts/task_validate.sh COMMSPLIT-DB-01`
  - `./scripts/task_validate.sh COMMSPLIT-QA-03`
- Dependency notes:
  - final serialized wave after `COMMSPLIT-DB-01`
- Remaining follow-up task ids:
  - `None`
- Allowlist:
  - `artifacts/COMMSPLIT-QA-03/**`
  - `docs/superpowers/specs/2026-04-03-commission-split-existing-carrier-reclassification-design.md`
  - `docs/superpowers/plans/2026-04-03-commission-split-existing-carrier-reclassification.md`
  - `tasks/postenhancement/backend/COMMSPLIT-DB-01.md`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-03.md`
- File access rule:
  - `COMMSPLIT-QA-03` owns its own wording and evidence audit; `COMMSPLIT-DB-01` only keeps the shared reclassification phrasing aligned
- Done definition:
  - reclassification evidence is mapped, close decision is recorded, and residual implementation stories are explicit

## Wave-based Batch Manifest

### Wave 1

- `COMMSPLIT-DB-01`

### Wave 2

- `COMMSPLIT-QA-03`

## No Execution Yet

- This plan intentionally stops at carrier-status assessment and task-tree correction.
- Do not start implementation until one exact slice is selected:
  - `COMMSPLIT-DB-01`
  - `COMMSPLIT-BE-01`
  - `COMMSPLIT-BE-02`
  - `COMMSPLIT-BE-03`
  - `COMMSPLIT-FE-01`
