# P1 #5 多代理人提成分成 Frontend Exposure Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Freeze the frontend ownership and exposure boundary for multi-agent split before any component implementation, router wiring, or reporting UI work continues.

**Architecture:** Treat this wave as a frontend exposure prerequisite. The active task freezes case-side viewing/editing ownership, the FE boundary between `CaseAgentSplit` and `second_agent_id`, and the rule that settlement pages do not own split editing, then keeps all implementation work deferred.

**Tech Stack:** Markdown specs/plans, existing cases frontend pages and API types, Superpowers workflow

---

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `frontend exposure decision after backend semantics freeze`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Current Recommendation

1. `COMMSPLIT-FE-01`
2. `COMMSPLIT-QA-07`

## Frozen Decision Snapshot

- split editing ownership stays on case-side pages
- split viewing ownership also prioritizes case-side pages
- `CaseAgentSplit` is the FE split source object
- `second_agent_id` remains context-only for FE split semantics
- settlement pages do not own split editing

## Decomposition Ledger

### `COMMSPLIT-FE-01`

- role: frontend exposure decision story
- closure:
  - freeze case-side editing ownership
  - freeze case-side viewing ownership priority
  - freeze `CaseAgentSplit` vs `second_agent_id` FE boundary
  - freeze no-split-editing-on-settlement-pages rule
- non-closure:
  - no Vue implementation
  - no router/types patch
  - no report/payout/export UI

### `COMMSPLIT-QA-07`

- role: frontend-exposure close audit
- closure:
  - audit the frontend-exposure evidence
  - verify the frozen FE ownership semantics and follow-up mapping
- non-closure:
  - no product code changes

### Deferred

- case edit/create exposure consistency implementation
- case detail viewing implementation
- downstream read-only commission/settlement exposure if still needed

## Shared-file Serialization Notes

- `docs/superpowers/specs/2026-04-03-commission-split-frontend-exposure-design.md` must be owned only by `COMMSPLIT-FE-01`
- `docs/superpowers/plans/2026-04-03-commission-split-frontend-exposure.md` must be owned only by `COMMSPLIT-FE-01`
- `tasks/postenhancement/backend/COMMSPLIT-FE-01.md` must be owned only by `COMMSPLIT-FE-01`
- `tasks/postenhancement/backend/COMMSPLIT-QA-07.md` stays QA-owned; `COMMSPLIT-FE-01` may touch it only to align audit wording with the frozen FE result, not to expand QA scope

## Atomic Task Inventory

### `COMMSPLIT-FE-01`

- Task file path:
  - `tasks/postenhancement/backend/COMMSPLIT-FE-01.md`
- Owner role:
  - `worker`
- Exact closure slice:
  - freeze frontend viewing/editing exposure ownership only
- Explicit non-closure:
  - no Vue/page/component implementation, no shared API/types wiring, no router/menu changes, no reporting or settlement UI enhancement
- Required verification:
  - `./scripts/task_validate.sh COMMSPLIT-FE-01`
- Dependency notes:
  - follows `COMMSPLIT-BE-03`
- Remaining follow-up task ids:
  - `COMMSPLIT-QA-07`
- Allowlist:
  - `docs/superpowers/specs/2026-04-03-commission-split-frontend-exposure-design.md`
  - `docs/superpowers/plans/2026-04-03-commission-split-frontend-exposure.md`
  - `tasks/postenhancement/backend/COMMSPLIT-FE-01.md`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-07.md`
- File access rule:
  - `tasks/postenhancement/backend/COMMSPLIT-QA-07.md` is reference-only for scope; edits, if any, are limited to audit phrasing alignment and do not transfer QA ownership into this wave
- Done definition:
  - FE ownership semantics are explicit, and no implementation slice is silently absorbed

### `COMMSPLIT-QA-07`

- Task file path:
  - `tasks/postenhancement/backend/COMMSPLIT-QA-07.md`
- Owner role:
  - `monitor`
- Exact closure slice:
  - validate the frontend-exposure evidence and close summary only
- Explicit non-closure:
  - no product code changes
- Required verification:
  - `./scripts/task_validate.sh COMMSPLIT-FE-01`
  - `./scripts/task_validate.sh COMMSPLIT-QA-07`
- Dependency notes:
  - final serialized wave after `COMMSPLIT-FE-01`
- Remaining follow-up task ids:
  - `None`
- Allowlist:
  - `artifacts/COMMSPLIT-QA-07/**`
  - `docs/superpowers/specs/2026-04-03-commission-split-frontend-exposure-design.md`
  - `docs/superpowers/plans/2026-04-03-commission-split-frontend-exposure.md`
  - `tasks/postenhancement/backend/COMMSPLIT-FE-01.md`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-07.md`
- File access rule:
  - `COMMSPLIT-QA-07` owns its own wording and evidence audit; `COMMSPLIT-FE-01` only keeps the shared FE phrasing aligned
- Done definition:
  - frontend-exposure evidence is mapped, close decision is recorded, and residual implementation stories are explicit

## Wave-based Batch Manifest

### Wave 1

- `COMMSPLIT-FE-01`

### Wave 2

- `COMMSPLIT-QA-07`

## No Execution Yet

- This plan intentionally stops at frontend exposure semantics.
- Do not start implementation until one exact slice is selected:
  - `COMMSPLIT-FE-01`
