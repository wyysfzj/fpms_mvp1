# DEMO-CASE-EDIT-500 — Demo Atomic Tasks

**Type**: Doc change  
**Priority**: P0  
**Date**: 2026-03-08

## Goal
Freeze the atomic execution plan for the demo issue where updating case `ZY-IP-2026-D-003`` from the case edit page returns `500 Internal Server Error`.

This file is planning-only. It does **not** implement product code.
Per `AGENTS.md`, each later execution must implement **exactly one** task from this file.

## Confirmed Problem
- Frontend case edit currently submits raw form data to `PUT /api/v1/cases/{id}`.
- Payload includes empty-string date fields such as `pub_date: ""`, `grant_date: ""`, and `valid_until: ""`.
- Backend `PUT /cases/{id}` parses these fields with `date.fromisoformat(...)` and crashes on `""`, causing `500`.
- Frontend and backend update contracts are not aligned:
  - FE sends `title`
  - backend update logic only handles `title_cn` / `title_en`
  - FE sends `filing_date`, `app_date`, `notes`
  - backend `PUT /cases/{id}` does not consistently support those fields
- FE also submits `status: "ACCEPTED"` in the reported payload, but backend case status enum does not define `ACCEPTED`.

## Contract Freeze
- Demo target endpoint remains `PUT /api/v1/cases/{case_id}`.
- Empty optional dates must not trigger `500`.
- Invalid values should fail as controlled validation/business errors, not server errors.
- Backend should own canonical validation of update payload.
- Frontend should only submit fields actually supported by the backend contract.
- No database schema changes.
- No router rewiring.

## Six-Agent Team Execution
- Lead: main thread assigns one explicit task ID per execution
- Architect (`explorer`): freeze update contract and file allowlist
- Backend Developer (`worker`): implement exactly one backend task
- Frontend Developer (`worker`): implement exactly one frontend task
- Tester (`worker`): run scoped gates and smoke the edit flow
- Reviewer (`explorer`): verify status-code semantics, allowlist, no schema drift, and no hidden contract mismatch

## Atomic Task List

### 1) `tasks/demo/DEMO-BE-CASE-01.md`
**Title**: Stop `PUT /cases/{id}` from crashing on empty-string date fields

**Owner**: Backend Developer  
**Scope**: server-side stopgap only

**Allowed files**
- `backend/app/modules/cases/api.py`

**Requirements**
- Normalize empty-string date inputs to `None` before date parsing
- Ensure `pub_date`, `grant_date`, and `valid_until` no longer raise `ValueError` on `""`
- Preserve existing route path and permission semantics
- Do not broaden scope to full contract refactor in this task

**Acceptance**
- Empty-string optional dates no longer produce `500`
- Same request shape returns controlled `200`, `400`, or `422` instead of `500`
- No other module files change


### 2) `tasks/demo/DEMO-BE-CASE-02.md`
**Title**: Convert case full-update endpoint to typed schema + service-layer contract

**Owner**: Backend Developer  
**Scope**: canonical backend update contract

**Allowed files**
- `backend/app/modules/cases/api.py`
- `backend/app/modules/cases/schemas.py`
- `backend/app/modules/cases/service.py`

**Requirements**
- Replace raw `dict[str, Any]` update input with typed update schema
- Validate case status against backend enum
- Route update handling through service-layer logic where appropriate
- Return controlled `422` for schema validation failures
- Keep response and permission conventions intact

**Acceptance**
- `PUT /api/v1/cases/{id}` no longer relies on ad hoc payload parsing
- Invalid status/date values fail cleanly with validation semantics
- Supported update fields are explicitly defined in one canonical contract


### 3) `tasks/demo/DEMO-FE-CASE-01.md`
**Title**: Normalize case edit payload before `PUT /cases/{id}`

**Owner**: Frontend Developer  
**Scope**: API payload mapper only

**Allowed files**
- `frontend/src/api/cases.ts`
- `frontend/src/api/cases.types.ts`

**Requirements**
- Add an update-payload mapper instead of sending raw form state
- Convert empty-string optional dates to `null` or omit them
- Convert empty-string optional text/ID selectors to `null` or omit them
- Map `title` to the backend-supported field name
- Do not submit unsupported fields blindly

**Acceptance**
- FE no longer sends empty-string dates that can crash the backend
- FE update payload only contains backend-supported keys
- Existing case detail/read flows remain unchanged


### 4) `tasks/demo/DEMO-FE-CASE-02.md`
**Title**: Align case edit form with actual backend-supported update fields

**Owner**: Frontend Developer  
**Scope**: case edit page only

**Allowed files**
- `frontend/src/modules/cases/pages/CaseEdit.vue`

**Requirements**
- Remove, disable, or clearly handle fields not supported by the canonical backend update contract
- Ensure selectable status values match backend enum exactly
- Keep all touched UI text in Simplified Chinese
- Surface backend validation errors through existing FE error pattern

**Acceptance**
- Editing a case from the UI no longer submits obviously unsupported values
- Status options align with backend enum values
- User-visible form behavior matches actual saved fields


### 5) `tasks/demo/DEMO-QA-CASE-01.md`
**Title**: Demo smoke and evidence for case edit update flow

**Owner**: Tester  
**Scope**: verification only

**Allowed files**
- `artifacts/DEMO-QA-CASE-01/**`
- optional runbook/evidence summary under `tasks/demo/` if explicitly required

**Requirements**
- Verify successful edit of the demo case using supported field values
- Verify empty optional dates do not cause `500`
- Verify invalid values fail with controlled semantics
- Record evidence artifacts

**Acceptance**
- Valid update request returns `200`
- Empty optional dates no longer return `500`
- Evidence exists under `artifacts/DEMO-QA-CASE-01/`

## Recommended Execution Order
1. `tasks/demo/DEMO-BE-CASE-01.md`
2. `tasks/demo/DEMO-BE-CASE-02.md`
3. `tasks/demo/DEMO-FE-CASE-01.md`
4. `tasks/demo/DEMO-FE-CASE-02.md`
5. `tasks/demo/DEMO-QA-CASE-01.md`

## Recommended First Implementation Task
Start with:

`tasks/demo/DEMO-BE-CASE-01.md`

This is the smallest stopgap that removes the live-demo `500`.

## Shared Acceptance Checklist
- Editing a case no longer returns `500` for empty optional dates
- Valid case update returns `200`
- Invalid status/date values fail with controlled semantics, not server crash
- FE payload and backend update contract are aligned
- No schema or migration changes
- No router rewiring
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
- `PUT /api/v1/cases/{id}` with valid payload returns `200`
- empty optional dates do not produce `500`
- invalid payloads fail with `400` or `422`, not `500`

## Evidence Expectations
- `artifacts/<TASK-ID>/results.jsonl`
- `artifacts/<TASK-ID>/summary.md`
- `artifacts/<TASK-ID>/git/diff.patch`

## STOP Contract
STOP and escalate before implementation if:
- the fix requires database schema changes
- the task requires edits outside its allowlist
- typed backend schema design conflicts with existing authoritative docs
- FE and BE contracts cannot be aligned without changing more than one atomic scope
