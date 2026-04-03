# P1 #5 多代理人提成分成 Settlement Linkage Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Freeze the row-level settlement linkage semantics under current split before any settlement API, frontend, or payout work continues.

**Architecture:** Treat this wave as a backend settlement-semantics prerequisite. The active task freezes per-row `settleable` semantics, `Commission -> CommissionSettleLine` entry conditions, linked-row immutability, and settlement-as-consumer boundaries, then keeps API, frontend, and payout work deferred. No settlement API, frontend, or schema implementation happens in this wave.

**Tech Stack:** Markdown specs/plans, existing commission settlement behavior, Superpowers workflow

---

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `backend settlement semantics before frontend follow-up`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Current Recommendation

1. `COMMSPLIT-BE-03`
2. `COMMSPLIT-QA-06`

## Frozen Decision Snapshot

- `is_settleable` remains per commission row
- same `bill/case` may produce multiple independently settleable agent-level commission rows
- settlement line generation remains row-based by `commission_id`
- settlement-linked rows remain non-rewritable
- settlement consumes current commission rows only, not split definitions directly
- Deferred implementation stories:
  - `COMMSPLIT-FE-01`

## Decomposition Ledger

### `COMMSPLIT-BE-03`

- role: settlement linkage semantics story
- closure:
  - freeze row-level `settleable` semantics
  - freeze `Commission -> CommissionSettleLine` entry semantics
  - freeze linked-row immutability boundary
  - freeze settlement-as-consumer boundary
- non-closure:
  - no settlement API
  - no FE
  - no payout/export

### `COMMSPLIT-QA-06`

- role: settlement-linkage close audit
- closure:
  - audit the settlement-linkage evidence
  - verify the frozen settlement semantics and follow-up mapping
- non-closure:
  - no product code changes

### Deferred

- `COMMSPLIT-FE-01`

## Shared-file Serialization Notes

- `docs/superpowers/specs/2026-04-03-commission-split-settlement-linkage-design.md` must be owned only by `COMMSPLIT-BE-03`
- `docs/superpowers/plans/2026-04-03-commission-split-settlement-linkage.md` must be owned only by `COMMSPLIT-BE-03`
- `tasks/postenhancement/backend/COMMSPLIT-BE-03.md` must be owned only by `COMMSPLIT-BE-03`
- `tasks/postenhancement/backend/COMMSPLIT-QA-06.md` stays QA-owned; `COMMSPLIT-BE-03` may touch it only to align audit wording with the frozen settlement result, not to expand QA scope

## Atomic Task Inventory

### `COMMSPLIT-BE-03`

- Task file path:
  - `tasks/postenhancement/backend/COMMSPLIT-BE-03.md`
- Owner role:
  - `worker`
- Exact closure slice:
  - freeze row-level settlement linkage semantics only
- Explicit non-closure:
  - no settlement/API implementation, no FE, no payout/export, no schema/model changes
- Required verification:
  - `./scripts/task_validate.sh COMMSPLIT-BE-03`
- Dependency notes:
  - follows `COMMSPLIT-BE-02`
- Remaining follow-up task ids:
  - `COMMSPLIT-FE-01`
  - `COMMSPLIT-QA-06`
- Allowlist:
  - `docs/superpowers/specs/2026-04-03-commission-split-settlement-linkage-design.md`
  - `docs/superpowers/plans/2026-04-03-commission-split-settlement-linkage.md`
  - `tasks/postenhancement/backend/COMMSPLIT-BE-03.md`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-06.md`
- File access rule:
  - `tasks/postenhancement/backend/COMMSPLIT-QA-06.md` is reference-only for scope; edits, if any, are limited to audit phrasing alignment and do not transfer QA ownership into this wave
- Done definition:
  - settlement-linkage semantics are explicit, and no API, frontend, or payout slice is silently absorbed

### `COMMSPLIT-QA-06`

- Task file path:
  - `tasks/postenhancement/backend/COMMSPLIT-QA-06.md`
- Owner role:
  - `monitor`
- Exact closure slice:
  - validate the settlement-linkage evidence and close summary only
- Explicit non-closure:
  - no product code changes
- Required verification:
  - `./scripts/task_validate.sh COMMSPLIT-BE-03`
  - `./scripts/task_validate.sh COMMSPLIT-QA-06`
- Dependency notes:
  - final serialized wave after `COMMSPLIT-BE-03`
- Remaining follow-up task ids:
  - `None`
- Allowlist:
  - `artifacts/COMMSPLIT-QA-06/**`
  - `docs/superpowers/specs/2026-04-03-commission-split-settlement-linkage-design.md`
  - `docs/superpowers/plans/2026-04-03-commission-split-settlement-linkage.md`
  - `tasks/postenhancement/backend/COMMSPLIT-BE-03.md`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-06.md`
- File access rule:
  - `COMMSPLIT-QA-06` owns its own wording and evidence audit; `COMMSPLIT-BE-03` only keeps the shared settlement phrasing aligned
- Done definition:
  - settlement-linkage evidence is mapped, close decision is recorded, and residual implementation stories are explicit

## Wave-based Batch Manifest

### Wave 1

- `COMMSPLIT-BE-03`

### Wave 2

- `COMMSPLIT-QA-06`

## No Execution Yet

- This plan intentionally stops at settlement linkage semantics.
- Do not start implementation until one exact slice is selected:
  - `COMMSPLIT-BE-03`
  - `COMMSPLIT-FE-01`
