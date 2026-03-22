# DEMO-FEE-DRAFT-DETAIL — Demo Atomic Tasks

**Type**: Doc change  
**Priority**: P0  
**Date**: 2026-03-08

## Goal
Freeze the atomic execution plan for two demo issues in fee draft detail flow:

1. opening fee draft items triggers:
   - `GET /api/v1/fees/drafts/{draft_id}/items`
   - response `405 Method Not Allowed`
2. relation chain and overview display mostly UUIDs for fee draft, case, and client, resulting in poor readability during demo

This file is planning-only. It does **not** implement product code.  
Per `AGENTS.md`, each later execution must implement **exactly one** task from this file.

## Confirmed Problem

### Problem A — fee draft item list returns `405`

- Frontend fee draft detail page mounts `FeeDraftItemsTable`
- `FeeDraftItemsTable` calls `getFeeDraftItems(draftId)`
- FE requests `GET /api/v1/fees/drafts/{draft_id}/items`
- Backend fee module currently exposes:
  - `POST /fees/drafts/{draft_id}/items`
  - `PUT /fees/drafts/{draft_id}/items/{item_id}`
  - `DELETE /fees/items/{item_id}`
- Backend does **not** expose `GET /fees/drafts/{draft_id}/items`
- Because the same path exists for `POST`, browser `GET` receives `405 Method Not Allowed`

### Problem B — relation chain readability is poor

- `RelationChainCard` prefers human-readable values:
  - `name`
  - `no`
  - `title`
  - `refNo`
  - `label`
- Fee draft detail page currently passes only raw IDs for client and case
- Fee draft API payload currently lacks display-friendly fields such as:
  - `case_no`
  - `client_name`
- As a result:
  - relation chain falls back to UUIDs
  - draft overview also shows UUIDs for case and client

## Contract Freeze

- Demo target backend endpoint must include `GET /api/v1/fees/drafts/{draft_id}/items`
- Existing fee item create/update/delete semantics remain unchanged
- Existing response envelope/module conventions must be preserved
- No database schema changes
- No backend router rewiring beyond the existing fees module
- User-facing fee draft detail should prioritize readable business identifiers over UUIDs
- All touched UI text must remain Simplified Chinese

## Six-Agent Team Execution

- Lead: main thread assigns one explicit task ID per execution
- Architect (`explorer`): freeze fee detail read contract and display-field strategy
- Backend Developer (`worker`): implement exactly one backend atomic task
- Frontend Developer (`worker`): implement exactly one frontend atomic task
- Tester (`worker`): run scoped gates and smoke the fee draft detail flow
- Reviewer (`explorer`): verify route semantics, permission wiring, readability, and no schema drift

## Atomic Task List

### 1) `tasks/demo/DEMO-BE-FEE-01.md`
**Title**: Add missing `GET /fees/drafts/{draft_id}/items` endpoint

**Owner**: Backend Developer  
**Scope**: backend stopgap and canonical fee-item read support

**Allowed files**
- `backend/app/modules/fees/api.py`
- `backend/app/modules/fees/service.py`

**Requirements**
- Add `GET /fees/drafts/{draft_id}/items`
- Return `list[FeeItemOut]`
- Verify draft exists before returning items
- Use permission parameter, preferred:
  - `_perm: None = Depends(require_perm("Fee.Read"))`
- Preserve module conventions and error semantics
- Do not broaden scope to display-name enrichment in this task

**Acceptance**
- Existing draft returns `200`
- Missing draft returns `404`
- Fee draft detail item tab no longer fails with `405`
- No files outside allowlist change


### 2) `tasks/demo/DEMO-FE-FEE-01.md`
**Title**: Improve fee draft relation chain and overview readability using existing case/client APIs

**Owner**: Frontend Developer  
**Scope**: fee draft detail page only

**Allowed files**
- `frontend/src/modules/fees/pages/FeeDraftDetail.vue`

**Requirements**
- Resolve case metadata by `draft.case_id`
- Resolve client metadata by `draft.client_id` when present
- Pass readable values into `RelationChainCard`
  - client: `name`
  - case: `case_no`
- Replace raw UUID display in the overview section where readable data is available
- Keep UUID only as internal route identity, not as primary visible label
- Do not change backend contracts in this task

**Acceptance**
- Relation chain prefers client name and case number over UUID
- Fee draft overview shows readable case/client labels when they can be resolved
- Existing detail page behavior remains intact


### 3) `tasks/demo/DEMO-BE-FEE-02.md`
**Title**: Extend fee draft API payload with display-friendly case/client fields

**Owner**: Backend Developer  
**Scope**: canonical fee draft display contract

**Allowed files**
- `backend/app/modules/fees/api.py`
- `backend/app/modules/fees/schemas.py`

**Requirements**
- Extend fee draft list/detail response schema with display fields such as:
  - `case_no`
  - `client_name`
- Populate those fields from existing case/client data without schema changes
- Preserve existing path semantics and response envelope conventions
- Do not refactor unrelated fee endpoints

**Acceptance**
- Fee draft list/detail responses include display-friendly identifiers
- FE can render readable values without extra lookups if it chooses
- No database schema changes


### 4) `tasks/demo/DEMO-FE-FEE-02.md`
**Title**: Align fee draft frontend types with enriched fee draft display contract

**Owner**: Frontend Developer  
**Scope**: fee API types only

**Allowed files**
- `frontend/src/api/fees.types.ts`
- `frontend/src/api/fees.ts`

**Requirements**
- Add optional display fields matching backend enriched fee draft contract
- Preserve existing fee draft read/write behavior
- Do not change unrelated fee-rate or bill APIs

**Acceptance**
- FE types support `case_no` / `client_name` or equivalent enriched fields
- Existing build and typecheck remain clean


### 5) `tasks/demo/DEMO-QA-FEE-01.md`
**Title**: Demo smoke and evidence for fee draft item tab and readable relation chain

**Owner**: Tester  
**Scope**: verification only

**Allowed files**
- `artifacts/DEMO-QA-FEE-01/**`
- optional runbook/evidence summary under `tasks/demo/` if explicitly required

**Requirements**
- Verify fee draft detail page can load item list without `405`
- Verify `GET /api/v1/fees/drafts/{draft_id}/items` returns controlled `200/404`
- Verify fee draft detail relation chain no longer primarily shows raw UUIDs when readable data exists
- Record evidence artifacts

**Acceptance**
- Existing draft item endpoint returns `200`
- Missing draft item endpoint returns `404`
- Fee draft detail page no longer shows a blocking item-list error
- Evidence exists under `artifacts/DEMO-QA-FEE-01/`

## Recommended Execution Order

1. `tasks/demo/DEMO-BE-FEE-01.md`
2. `tasks/demo/DEMO-FE-FEE-01.md`
3. `tasks/demo/DEMO-BE-FEE-02.md`
4. `tasks/demo/DEMO-FE-FEE-02.md`
5. `tasks/demo/DEMO-QA-FEE-01.md`

## Recommended First Implementation Task

Start with:

`tasks/demo/DEMO-BE-FEE-01.md`

This is the smallest atomic fix that removes the live-demo `405`.

## Shared Acceptance Checklist

- Fee draft item read endpoint exists and supports `GET /api/v1/fees/drafts/{id}/items`
- Existing draft item request returns `200`
- Missing draft returns `404`
- Relation chain and overview prioritize readable business labels over UUIDs where data exists
- No database schema or migration changes
- No unrelated refactors
- Touched UI text remains Simplified Chinese

## Verification Commands

Backend implementation tasks:

```bash
cd backend && ruff check --fix .
cd backend && ruff format .
cd backend && ruff check .
cd backend && pytest -q
```

Frontend implementation tasks:

```bash
cd frontend && npm run lint
cd frontend && npm run typecheck
cd frontend && npm run build
```

Runtime expectations:

- `GET /api/v1/fees/drafts/{id}/items` with valid token and existing draft returns `200`
- `GET /api/v1/fees/drafts/{id}/items` with missing draft returns `404`
- fee draft detail item tab no longer produces `405`
- relation chain should show readable case/client labels when available

## Evidence Expectations

- `artifacts/<TASK-ID>/results.jsonl`
- `artifacts/<TASK-ID>/summary.md`
- `artifacts/<TASK-ID>/git/diff.patch`

## STOP Contract

STOP and escalate before implementation if:

- the fix requires database schema changes
- the task requires edits outside its allowlist
- readability improvements require a larger cross-module contract change than one atomic task can safely contain
- fee item read semantics conflict with existing authoritative module conventions
