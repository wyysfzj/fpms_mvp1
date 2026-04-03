# P1 #5 多代理人提成分成 Generation Hardening Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Freeze the commission generation / rewrite behavior under current split before any settlement-linkage or frontend work continues.

**Architecture:** Treat this wave as a backend behavior-hardening prerequisite. The active task freezes generation, fallback, rewritable-only update/delete, and locked-row boundaries, then keeps settlement and frontend work deferred. No settlement, API, or frontend implementation happens in this wave.

**Tech Stack:** Markdown specs/plans, existing commission service behavior, Superpowers workflow

---

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `backend behavior hardening before settlement follow-up`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Current Recommendation

1. `COMMSPLIT-BE-02`
2. `COMMSPLIT-QA-05`

## Frozen Decision Snapshot

- Split rows present:
  - generate/update one commission row per current allocation
- Split rows absent:
  - fallback to one `primary_agent_id` row
- Rewrite scope:
  - only rewritable rows may be updated or deleted
- Locked boundary:
  - terminal or settlement-linked rows remain untouched
- Deferred implementation stories:
  - `COMMSPLIT-BE-03`
  - `COMMSPLIT-FE-01`

## Decomposition Ledger

### `COMMSPLIT-BE-02`

- role: generation / rewrite behavior hardening story
- closure:
  - freeze split-driven generation behavior
  - freeze single-agent fallback behavior
  - freeze rewritable-only update / delete behavior
  - freeze locked-row boundary
- non-closure:
  - no settlement changes
  - no API
  - no FE

### `COMMSPLIT-QA-05`

- role: generation-hardening close audit
- closure:
  - audit the generation-hardening evidence
  - verify the frozen behavior and follow-up mapping
- non-closure:
  - no product code changes

### Deferred

- `COMMSPLIT-BE-03`
- `COMMSPLIT-FE-01`

## Shared-file Serialization Notes

- `docs/superpowers/specs/2026-04-03-commission-split-generation-hardening-design.md` must be owned only by `COMMSPLIT-BE-02`
- `docs/superpowers/plans/2026-04-03-commission-split-generation-hardening.md` must be owned only by `COMMSPLIT-BE-02`
- `tasks/postenhancement/backend/COMMSPLIT-BE-02.md` must be owned only by `COMMSPLIT-BE-02`
- `tasks/postenhancement/backend/COMMSPLIT-QA-05.md` stays QA-owned; `COMMSPLIT-BE-02` may touch it only to align audit wording with the frozen behavior result, not to expand QA scope

## Atomic Task Inventory

### `COMMSPLIT-BE-02`

- Task file path:
  - `tasks/postenhancement/backend/COMMSPLIT-BE-02.md`
- Owner role:
  - `worker`
- Exact closure slice:
  - freeze current split driven generation / rewrite behavior only
- Explicit non-closure:
  - no settlement, no API, no FE, no schema/model changes
- Required verification:
  - `./scripts/task_validate.sh COMMSPLIT-BE-02`
- Dependency notes:
  - first and only generation-hardening wave
- Remaining follow-up task ids:
  - `COMMSPLIT-BE-03`
  - `COMMSPLIT-FE-01`
  - `COMMSPLIT-QA-05`
- Allowlist:
  - `docs/superpowers/specs/2026-04-03-commission-split-generation-hardening-design.md`
  - `docs/superpowers/plans/2026-04-03-commission-split-generation-hardening.md`
  - `tasks/postenhancement/backend/COMMSPLIT-BE-02.md`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-05.md`
- File access rule:
  - `tasks/postenhancement/backend/COMMSPLIT-QA-05.md` is reference-only for scope; edits, if any, are limited to audit phrasing alignment and do not transfer QA ownership into this wave
- Done definition:
  - generation, fallback, rewritable-only update/delete, and locked-row semantics are explicit, and no settlement or frontend slice is silently absorbed

### `COMMSPLIT-QA-05`

- Task file path:
  - `tasks/postenhancement/backend/COMMSPLIT-QA-05.md`
- Owner role:
  - `monitor`
- Exact closure slice:
  - validate the generation-hardening evidence and close summary only
- Explicit non-closure:
  - no product code changes
- Required verification:
  - `./scripts/task_validate.sh COMMSPLIT-BE-02`
  - `./scripts/task_validate.sh COMMSPLIT-QA-05`
- Dependency notes:
  - final serialized wave after `COMMSPLIT-BE-02`
- Remaining follow-up task ids:
  - `None`
- Allowlist:
  - `artifacts/COMMSPLIT-QA-05/**`
  - `docs/superpowers/specs/2026-04-03-commission-split-generation-hardening-design.md`
  - `docs/superpowers/plans/2026-04-03-commission-split-generation-hardening.md`
  - `tasks/postenhancement/backend/COMMSPLIT-BE-02.md`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-05.md`
- File access rule:
  - `COMMSPLIT-QA-05` owns its own wording and evidence audit; `COMMSPLIT-BE-02` only keeps the shared hardening phrasing aligned
- Done definition:
  - generation-hardening evidence is mapped, close decision is recorded, and residual implementation stories are explicit

## Wave-based Batch Manifest

### Wave 1

- `COMMSPLIT-BE-02`

### Wave 2

- `COMMSPLIT-QA-05`

## No Execution Yet

- This plan intentionally stops at generation / rewrite behavior hardening.
- Do not start implementation until one exact slice is selected:
  - `COMMSPLIT-BE-02`
  - `COMMSPLIT-BE-03`
  - `COMMSPLIT-FE-01`
