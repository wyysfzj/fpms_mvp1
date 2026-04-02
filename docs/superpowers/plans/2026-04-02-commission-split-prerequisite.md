# P1 #5 多代理人提成分成 Prerequisite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Freeze `P1 #5` into a prerequisite-first commission split program before any schema, calculation, or frontend implementation starts.

**Architecture:** Treat this item as a prerequisite-heavy structural gap. The first wave only closes design/plan/task freeze for allocation carrier, ratio semantics, and settlement linkage semantics. Implementation stories remain deferred until the prerequisite conclusion is approved.

**Tech Stack:** Markdown specs/plans, existing case/commission/settlement models, Superpowers workflow

---

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `shared commission program; prerequisite before implementation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Current Recommendation

1. `COMMSPLIT-PRE-01`, recommended
2. `COMMSPLIT-QA-01`

## Decomposition Ledger

### `COMMSPLIT-PRE-01`

- role: prerequisite design story
- closure:
  - freeze allocation carrier definition
  - freeze ratio semantics
  - freeze settlement linkage semantics
  - explicitly mark current case/commission/settlement fields as context-only, not true split carrier
  - rewrite the follow-up implementation stories to match the frozen prerequisite
- non-closure:
  - no schema/migration implementation
  - no calculation logic
  - no frontend UI
  - no settlement/report/export changes

### `COMMSPLIT-QA-01`

- role: prerequisite close audit
- closure:
  - audit the prerequisite outputs
  - verify evidence and close summary
- non-closure:
  - no product code changes

### Deferred

- `COMMSPLIT-PRE-02`
- `COMMSPLIT-BE-01`
- `COMMSPLIT-BE-02`
- `COMMSPLIT-FE-01`

## Shared-file Serialization Notes

- `docs/superpowers/specs/2026-04-02-commission-split-prerequisite-design.md` must be owned only by `COMMSPLIT-PRE-01`
- `docs/superpowers/plans/2026-04-02-commission-split-prerequisite.md` must be owned only by `COMMSPLIT-PRE-01`
- `tasks/postenhancement/backend/COMMSPLIT-PRE-01.md` must be owned only by `COMMSPLIT-PRE-01`
- `tasks/postenhancement/backend/COMMSPLIT-QA-01.md` is reserved for the downstream serialized QA wave; it is listed here only so the handoff path is explicit, not because it is co-owned in the prerequisite editing wave
- legacy `FRCOM03-*` task files are historical references and must not be silently treated as the active batch for this wave

## Atomic Task Inventory

### `COMMSPLIT-PRE-01`

- Task file path:
  - `tasks/postenhancement/backend/COMMSPLIT-PRE-01.md`
- Owner role:
  - `worker`
- Exact closure slice:
  - freeze multi-agent split prerequisite semantics and rewrite the active decomposition accordingly
- Explicit non-closure:
  - no schema, no API, no calculation, no FE
- Required verification:
  - `./scripts/task_validate.sh COMMSPLIT-PRE-01`
- Dependency notes:
  - first and only implementation-preparation wave
- Remaining follow-up task ids:
  - `COMMSPLIT-PRE-02`
  - `COMMSPLIT-BE-01`
  - `COMMSPLIT-BE-02`
  - `COMMSPLIT-FE-01`
  - `COMMSPLIT-QA-01`
- Allowlist:
  - `docs/superpowers/specs/2026-04-02-commission-split-prerequisite-design.md`
  - `docs/superpowers/plans/2026-04-02-commission-split-prerequisite.md`
  - `tasks/postenhancement/backend/COMMSPLIT-PRE-01.md`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-01.md`
- Done definition:
  - prerequisite semantics are frozen, follow-up stories are named, and no implementation slice is silently absorbed

### `COMMSPLIT-QA-01`

- Task file path:
  - `tasks/postenhancement/backend/COMMSPLIT-QA-01.md`
- Owner role:
  - `monitor`
- Exact closure slice:
  - validate prerequisite evidence and close summary only
- Explicit non-closure:
  - no product code changes
- Required verification:
  - `./scripts/task_validate.sh COMMSPLIT-PRE-01`
  - `./scripts/task_validate.sh COMMSPLIT-QA-01`
- Dependency notes:
  - final serialized wave after `COMMSPLIT-PRE-01`
- Remaining follow-up task ids:
  - `None`
- Allowlist:
  - `artifacts/COMMSPLIT-QA-01/**`
  - `docs/superpowers/specs/2026-04-02-commission-split-prerequisite-design.md`
  - `docs/superpowers/plans/2026-04-02-commission-split-prerequisite.md`
  - `tasks/postenhancement/backend/COMMSPLIT-PRE-01.md`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-01.md`
- Done definition:
  - prerequisite evidence is mapped, close decision is recorded, and residual follow-up stories are explicit

## Wave-based Batch Manifest

### Wave 1

- `COMMSPLIT-PRE-01`

### Wave 2

- `COMMSPLIT-QA-01`

## No Execution Yet

- This plan intentionally stops at prerequisite planning.
- Do not start implementation until one exact slice is selected:
  - `COMMSPLIT-PRE-01`
  - `COMMSPLIT-PRE-02`
  - `COMMSPLIT-BE-01`
  - `COMMSPLIT-BE-02`
  - `COMMSPLIT-FE-01`
