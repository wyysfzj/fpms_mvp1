# P1 #5 多代理人提成分成 Durable Carrier Decision Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Decide the durable carrier shape for multi-agent commission split and produce the schema prerequisite recommendation before any DB, BE, or FE implementation starts.

**Architecture:** Treat this story as a decision-only prerequisite wave. The active task compares candidate carriers, selects the recommended direction, and names the next DB/BE/FE follow-ups explicitly. No implementation happens in this wave.

**Tech Stack:** Markdown specs/plans, existing case/commission/settlement models, Superpowers workflow

---

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `shared commission program; schema decision before implementation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Current Recommendation

1. `COMMSPLIT-PRE-02`, recommended
2. `COMMSPLIT-QA-02`

## Frozen Decision Snapshot

- Carrier choice:
  - `CaseAgentSplit` 明细表
- Schema prerequisite:
  - `COMMSPLIT-DB-01` is mandatory before implementation waves start
- Deferred implementation stories:
  - `COMMSPLIT-DB-01`
  - `COMMSPLIT-BE-01`
  - `COMMSPLIT-BE-02`
  - `COMMSPLIT-FE-01`

## Decomposition Ledger

### `COMMSPLIT-PRE-02`

- role: durable carrier decision story
- closure:
  - compare the 3 carrier candidates
  - recommend the carrier choice
  - recommend whether a DB prerequisite is mandatory
  - name the follow-up DB/BE/FE stories explicitly
- non-closure:
  - no migration
  - no ORM model
  - no API
  - no calculation
  - no FE

### `COMMSPLIT-QA-02`

- role: decision-wave close audit
- closure:
  - audit the decision-wave evidence
  - verify the recommendation and follow-up naming
- non-closure:
  - no product code changes

### Deferred

- `COMMSPLIT-DB-01`
- `COMMSPLIT-BE-01`
- `COMMSPLIT-BE-02`
- `COMMSPLIT-FE-01`

## Shared-file Serialization Notes

- `docs/superpowers/specs/2026-04-03-commission-split-durable-carrier-design.md` must be owned only by `COMMSPLIT-PRE-02`
- `docs/superpowers/plans/2026-04-03-commission-split-durable-carrier-decision.md` must be owned only by `COMMSPLIT-PRE-02`
- `tasks/postenhancement/backend/COMMSPLIT-PRE-02.md` must be owned only by `COMMSPLIT-PRE-02`
- `tasks/postenhancement/backend/COMMSPLIT-QA-02.md` stays QA-owned; `COMMSPLIT-PRE-02` may touch it only to align audit wording with the frozen decision, not to expand QA scope

## Atomic Task Inventory

### `COMMSPLIT-PRE-02`

- Task file path:
  - `tasks/postenhancement/backend/COMMSPLIT-PRE-02.md`
- Owner role:
  - `worker`
- Exact closure slice:
  - freeze the durable carrier decision and schema prerequisite recommendation only
- Explicit non-closure:
  - no migration, no ORM model, no API, no calculation, no FE
- Required verification:
  - `./scripts/task_validate.sh COMMSPLIT-PRE-02`
- Dependency notes:
  - first and only decision wave
- Remaining follow-up task ids:
  - `COMMSPLIT-DB-01`
  - `COMMSPLIT-BE-01`
  - `COMMSPLIT-BE-02`
  - `COMMSPLIT-FE-01`
  - `COMMSPLIT-QA-02`
- Allowlist:
  - `docs/superpowers/specs/2026-04-03-commission-split-durable-carrier-design.md`
  - `docs/superpowers/plans/2026-04-03-commission-split-durable-carrier-decision.md`
  - `tasks/postenhancement/backend/COMMSPLIT-PRE-02.md`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-02.md`
- File access rule:
  - `tasks/postenhancement/backend/COMMSPLIT-QA-02.md` is reference-only for scope; edits, if any, are limited to audit phrasing alignment and do not transfer QA ownership into this wave
- Done definition:
  - carrier recommendation is explicit, DB prerequisite need is explicit, and no implementation slice is silently absorbed

### `COMMSPLIT-QA-02`

- Task file path:
  - `tasks/postenhancement/backend/COMMSPLIT-QA-02.md`
- Owner role:
  - `monitor`
- Exact closure slice:
  - validate the decision-wave evidence and close summary only
- Explicit non-closure:
  - no product code changes
- Required verification:
  - `./scripts/task_validate.sh COMMSPLIT-PRE-02`
  - `./scripts/task_validate.sh COMMSPLIT-QA-02`
- Dependency notes:
  - final serialized wave after `COMMSPLIT-PRE-02`
- Remaining follow-up task ids:
  - `None`
- Allowlist:
  - `artifacts/COMMSPLIT-QA-02/**`
  - `docs/superpowers/specs/2026-04-03-commission-split-durable-carrier-design.md`
  - `docs/superpowers/plans/2026-04-03-commission-split-durable-carrier-decision.md`
  - `tasks/postenhancement/backend/COMMSPLIT-PRE-02.md`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-02.md`
- File access rule:
  - `COMMSPLIT-QA-02` owns its own wording and evidence audit; PRE-02 only keeps the shared decision phrasing aligned
- Done definition:
  - decision-wave evidence is mapped, close decision is recorded, and residual implementation stories are explicit

## Wave-based Batch Manifest

### Wave 1

- `COMMSPLIT-PRE-02`

### Wave 2

- `COMMSPLIT-QA-02`

## No Execution Yet

- This plan intentionally stops at durable carrier decision.
- Do not start implementation until one exact slice is selected:
  - `COMMSPLIT-PRE-02`
  - `COMMSPLIT-DB-01`
  - `COMMSPLIT-BE-01`
  - `COMMSPLIT-BE-02`
  - `COMMSPLIT-FE-01`
