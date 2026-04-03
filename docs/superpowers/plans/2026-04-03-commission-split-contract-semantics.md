# P1 #5 多代理人提成分成 Contract Semantics Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Freeze the `CaseAgentSplit -> commission generation` contract semantics before any calculation-hardening or settlement-linkage work continues.

**Architecture:** Treat this wave as a contract-freeze prerequisite. The active task captures the generation source-of-truth, fallback semantics, and generation preconditions, then narrows the downstream backend mapping. No calculation, settlement, API, or frontend implementation happens in this wave.

**Tech Stack:** Markdown specs/plans, existing case/commission services, Superpowers workflow

---

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `backend semantic-hardening before calculation and settlement follow-ups`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Current Recommendation

1. `COMMSPLIT-BE-01`
2. `COMMSPLIT-QA-04`

## Frozen Decision Snapshot

- Split source-of-truth:
  - `CaseAgentSplit` is the active generation source when split rows exist
  - split rows override `second_agent_id` for generation semantics
- Fallback:
  - no split rows -> `primary_agent_id` only
- Upstream invariant:
  - `share_ratio = 100` total is required before generation
- Deferred implementation stories:
  - `COMMSPLIT-BE-02`
  - `COMMSPLIT-BE-03`
  - `COMMSPLIT-FE-01`

## Decomposition Ledger

### `COMMSPLIT-BE-01`

- role: contract semantics decision story
- closure:
  - freeze split source-of-truth semantics
  - freeze whether split rows override `second_agent_id` for generation
  - freeze fallback semantics
  - freeze generation preconditions
  - narrow backend follow-up mapping
- non-closure:
  - no calculation changes
  - no settlement changes
  - no API
  - no FE

### `COMMSPLIT-QA-04`

- role: contract-freeze close audit
- closure:
  - audit the contract-freeze evidence
  - verify the frozen contract semantics and follow-up mapping
- non-closure:
  - no product code changes

### Deferred

- `COMMSPLIT-BE-02`
- `COMMSPLIT-BE-03`
- `COMMSPLIT-FE-01`

## Shared-file Serialization Notes

- `docs/superpowers/specs/2026-04-03-commission-split-contract-semantics-design.md` must be owned only by `COMMSPLIT-BE-01`
- `docs/superpowers/plans/2026-04-03-commission-split-contract-semantics.md` must be owned only by `COMMSPLIT-BE-01`
- `tasks/postenhancement/backend/COMMSPLIT-BE-01.md` must be owned only by `COMMSPLIT-BE-01`
- `tasks/postenhancement/backend/COMMSPLIT-QA-04.md` stays QA-owned; `COMMSPLIT-BE-01` may touch it only to align audit wording with the frozen contract result, not to expand QA scope

## Atomic Task Inventory

### `COMMSPLIT-BE-01`

- Task file path:
  - `tasks/postenhancement/backend/COMMSPLIT-BE-01.md`
- Owner role:
  - `worker`
- Exact closure slice:
  - freeze the `CaseAgentSplit -> commission generation` contract semantics only
- Explicit non-closure:
  - no calculation, no settlement, no API, no FE, no schema/model changes
- Required verification:
  - `./scripts/task_validate.sh COMMSPLIT-BE-01`
- Dependency notes:
  - first and only contract-freeze wave
- Remaining follow-up task ids:
  - `COMMSPLIT-BE-02`
  - `COMMSPLIT-BE-03`
  - `COMMSPLIT-FE-01`
  - `COMMSPLIT-QA-04`
- Allowlist:
  - `docs/superpowers/specs/2026-04-03-commission-split-contract-semantics-design.md`
  - `docs/superpowers/plans/2026-04-03-commission-split-contract-semantics.md`
  - `tasks/postenhancement/backend/COMMSPLIT-BE-01.md`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-04.md`
- File access rule:
  - `tasks/postenhancement/backend/COMMSPLIT-QA-04.md` is reference-only for scope; edits, if any, are limited to audit phrasing alignment and do not transfer QA ownership into this wave
- Done definition:
  - source-of-truth semantics, fallback semantics, generation preconditions, and the `second_agent_id` override rule are explicit, and no implementation slice is silently absorbed

### `COMMSPLIT-QA-04`

- Task file path:
  - `tasks/postenhancement/backend/COMMSPLIT-QA-04.md`
- Owner role:
  - `monitor`
- Exact closure slice:
  - validate the contract-freeze evidence and close summary only
- Explicit non-closure:
  - no product code changes
- Required verification:
  - `./scripts/task_validate.sh COMMSPLIT-BE-01`
  - `./scripts/task_validate.sh COMMSPLIT-QA-04`
- Dependency notes:
  - final serialized wave after `COMMSPLIT-BE-01`
- Remaining follow-up task ids:
  - `None`
- Allowlist:
  - `artifacts/COMMSPLIT-QA-04/**`
  - `docs/superpowers/specs/2026-04-03-commission-split-contract-semantics-design.md`
  - `docs/superpowers/plans/2026-04-03-commission-split-contract-semantics.md`
  - `tasks/postenhancement/backend/COMMSPLIT-BE-01.md`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-04.md`
- File access rule:
  - `COMMSPLIT-QA-04` owns its own wording and evidence audit; `COMMSPLIT-BE-01` only keeps the shared contract phrasing aligned
- Done definition:
  - contract-freeze evidence is mapped, close decision is recorded, and residual implementation stories are explicit

## Wave-based Batch Manifest

### Wave 1

- `COMMSPLIT-BE-01`

### Wave 2

- `COMMSPLIT-QA-04`

## No Execution Yet

- This plan intentionally stops at contract semantics freeze.
- Do not start implementation until one exact slice is selected:
  - `COMMSPLIT-BE-01`
  - `COMMSPLIT-BE-02`
  - `COMMSPLIT-BE-03`
  - `COMMSPLIT-FE-01`
