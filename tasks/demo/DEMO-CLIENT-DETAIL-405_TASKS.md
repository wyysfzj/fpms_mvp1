# DEMO-CLIENT-DETAIL-405 — Demo Atomic Tasks

**Type**: Doc change  
**Priority**: P0  
**Date**: 2026-03-08

## Goal
Freeze the atomic execution plan for the demo issue where clicking either “查看” or “编辑” from the client list triggers:

- `GET /api/v1/clients/{client_id}`
- response `405 Method Not Allowed`

This file is planning-only. It does **not** implement product code.  
Per `AGENTS.md`, each later execution must implement **exactly one** task from this file.

## Confirmed Problem

- Frontend client edit flow calls `getClient(id)` which requests `GET /api/v1/clients/{id}`.
- Frontend client detail page also calls the same endpoint.
- Backend client module currently exposes:
  - `GET /clients`
  - `POST /clients`
  - `PUT /clients/{id}`
  - `PUT /clients/{id}/deactivate`
  - address/contact sub-resource endpoints
- Backend does **not** expose `GET /clients/{id}`.
- Because the same path exists for `PUT`, browser `GET` hits the route path and receives `405 Method Not Allowed`.

## Secondary Risk Already Identified

- Client list page currently sends both “查看” and “编辑” to `/clients/{id}/edit`.
- Frontend already contains a `ClientDetail.vue` page, but router does not register `/clients/{id}`.
- Client form/detail UI currently shows fields such as `联系人 / 电话 / 地址`, while the current main client API contract only persists canonical client fields such as:
  - `client_code`
  - `name_cn`
  - `name_en`
  - `email`
  - `client_type`
  - `default_currency`
  - `is_active`
- Contact/address data should be treated through sub-resources, not implied as already saved in the main client record.

## Contract Freeze

- Demo target backend endpoint must include `GET /api/v1/clients/{client_id}`.
- Existing `PUT /api/v1/clients/{client_id}` behavior remains unchanged.
- Existing response envelope/module conventions must be preserved.
- No database schema changes.
- No router rewiring on backend beyond the existing client module.
- Frontend “查看” and “编辑” must become distinct user actions.
- All touched user-facing UI text must remain Simplified Chinese.

## Six-Agent Team Execution

- Lead: main thread assigns one explicit task ID per execution
- Architect (`explorer`): freeze route/API contract and file allowlist
- Backend Developer (`worker`): implement exactly one backend atomic task
- Frontend Developer (`worker`): implement exactly one frontend atomic task
- Tester (`worker`): run scoped gates and smoke the client open/view/edit flow
- Reviewer (`explorer`): verify route semantics, permission wiring, scope control, and no hidden contract drift

## Atomic Task List

### 1) `tasks/demo/DEMO-BE-CLIENT-01.md`
**Title**: Add missing `GET /clients/{id}` endpoint

**Owner**: Backend Developer  
**Scope**: backend stopgap and canonical detail-read support

**Allowed files**
- `backend/app/modules/masterdata/clients/api.py`

**Requirements**
- Add `GET /clients/{client_id}`
- Use existing service-layer `get_client(...)`
- Return `ClientOut`
- Enforce permission via function parameter:
  - `_perm: None = Depends(require_perm("Client.Read"))`
- Preserve module conventions and error semantics
- Do not broaden scope to address/contact aggregation or extra payload changes in this task

**Acceptance**
- Existing client returns `200`
- Missing client returns `404`
- Current `405 Method Not Allowed` is eliminated for `GET /clients/{id}`
- No other module files change


### 2) `tasks/demo/DEMO-FE-CLIENT-01.md`
**Title**: Split client list “查看 / 编辑” actions and wire client detail route

**Owner**: Frontend Developer  
**Scope**: routing and navigation only

**Allowed files**
- `frontend/src/router/index.ts`
- `frontend/src/modules/clients/pages/ClientList.vue`

**Requirements**
- Register `/clients/:id` to the existing `ClientDetail.vue`
- Keep `/clients/:id/edit` for edit flow
- Change client list action mapping:
  - “查看” -> `/clients/{id}`
  - “编辑” -> `/clients/{id}/edit`
- Keep touched UI text in Simplified Chinese
- Do not change client form/detail field semantics in this task

**Acceptance**
- Clicking “查看” opens client detail page
- Clicking “编辑” opens client edit page
- Existing list behavior and pagination remain unchanged


### 3) `tasks/demo/DEMO-FE-CLIENT-02.md`
**Title**: Align client detail/edit presentation with current backend-supported main client contract

**Owner**: Frontend Developer  
**Scope**: client pages contract cleanup only

**Allowed files**
- `frontend/src/modules/clients/pages/ClientForm.vue`
- `frontend/src/modules/clients/pages/ClientDetail.vue`
- `frontend/src/api/clients.ts`
- `frontend/src/api/clients.types.ts`

**Requirements**
- Stop implying that `联系人 / 电话 / 地址` are saved as main client fields if the current backend main client contract does not persist them
- Preserve contacts/addresses through their existing sub-resource tabs/components
- Ensure the main client form and detail page present only actually supported persisted fields, or clearly separate unsupported fields from the main record
- Keep all touched UI text in Simplified Chinese
- Do not add backend schema changes in this task

**Acceptance**
- Main client view/edit no longer misleads users about what is persisted in the primary client record
- Contacts/addresses remain available through existing sub-resource UI
- FE main client contract matches current backend-supported fields


### 4) `tasks/demo/DEMO-QA-CLIENT-01.md`
**Title**: Demo smoke and evidence for client view/edit flow

**Owner**: Tester  
**Scope**: verification only

**Allowed files**
- `artifacts/DEMO-QA-CLIENT-01/**`
- optional runbook/evidence summary under `tasks/demo/` if explicitly required

**Requirements**
- Verify client list loads
- Verify clicking “查看” opens client detail successfully
- Verify clicking “编辑” opens client edit successfully
- Verify `GET /api/v1/clients/{id}` returns controlled `200/404` semantics
- Record evidence artifacts

**Acceptance**
- Valid client detail request returns `200`
- Missing client detail request returns `404`
- No `405` remains on the client detail path
- Evidence exists under `artifacts/DEMO-QA-CLIENT-01/`

## Recommended Execution Order

1. `tasks/demo/DEMO-BE-CLIENT-01.md`
2. `tasks/demo/DEMO-FE-CLIENT-01.md`
3. `tasks/demo/DEMO-FE-CLIENT-02.md`
4. `tasks/demo/DEMO-QA-CLIENT-01.md`

## Recommended First Implementation Task

Start with:

`tasks/demo/DEMO-BE-CLIENT-01.md`

This is the smallest atomic fix that removes the live-demo `405`.

## Shared Acceptance Checklist

- Client detail endpoint exists and supports `GET /api/v1/clients/{id}`
- Clicking “查看” and “编辑” no longer lead to the same route
- Client detail read returns `200` for existing records, `404` for missing records
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

- `GET /api/v1/clients/{id}` with valid token and existing client returns `200`
- `GET /api/v1/clients/{id}` with missing client returns `404`
- client list “查看” / “编辑” navigation no longer produces `405`

## Evidence Expectations

- `artifacts/<TASK-ID>/results.jsonl`
- `artifacts/<TASK-ID>/summary.md`
- `artifacts/<TASK-ID>/git/diff.patch`

## STOP Contract

STOP and escalate before implementation if:

- the fix requires database schema changes
- the task requires edits outside its allowlist
- frontend contract cleanup requires backend field additions rather than FE-only scope control
- router or permission behavior conflicts with existing authoritative module conventions
