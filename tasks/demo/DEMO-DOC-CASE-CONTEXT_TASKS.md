# DEMO-DOC-CASE-CONTEXT — Demo Atomic Tasks

**Date**: 2026-03-08  
**Priority**: P0  
**Source**: Demo bug triage for case-driven document creation flow

## Purpose
Freeze the atomic task breakdown for the demo fix where:
- user enters document creation from a case page
- page must display `case_no` as read-only
- internal submit must continue using `case.id`
- user must not edit case association in this flow

This file is a planning/freeze document only.
Per `AGENTS.md`, later execution must implement **exactly one** task ID from this file per run.

## Contract Freeze

### User-visible contract
- From case detail "登记公文", document create page must show the current case number.
- The visible case field must be read-only.
- User must not type or edit case linkage in this flow.
- All touched UI text must be Simplified Chinese.

### Internal contract
- `POST /api/v1/documents` must still submit `case_id = case.id`.
- `case_no` is display-only and must not be used as the API identity field.
- No backend API/schema/router changes are allowed for this demo fix.

## Team Protocol
- Lead: choose exactly one task ID below for each execution.
- Architect (`explorer`): confirm UI/data contract and allowed scope before implementation.
- Frontend Developer (`worker`): implement only the allowlisted FE files for the chosen task.
- Tester (`worker`): run FE gates and targeted smoke verification.
- Reviewer (`explorer`): verify scope, Chinese UI text, internal `case.id` usage, and no backend drift.

## Atomic Tasks

### DEMO-FE-DOC-01 — Pass case context into document create route
**Goal**
When user clicks "登记公文" from the case documents tab, route query must carry both internal `case_id` and display `case_no`.

**Scope (Atomic – FIXED)**
Modify exactly one source file.

**Allowed files**
- `frontend/src/modules/cases/components/CaseDocumentsTab.vue`

**Requirements**
- Keep existing entry point from case detail page.
- Pass `case_id` for internal use.
- Pass `case_no` for read-only display on the target page.
- Do not change backend calls.

**Acceptance**
- Clicking "登记公文" navigates to `/documents/new` with query containing both `case_id` and `case_no`.
- Existing case documents list behavior remains unchanged.


### DEMO-FE-DOC-02 — Hydrate and lock case context on document create page
**Goal**
Document create page must consume route case context, display `case_no` read-only, and keep `case_id` internal for submit.

**Scope (Atomic – FIXED)**
Frontend page behavior only.

**Allowed files**
- `frontend/src/modules/documents/pages/DocumentCreate.vue`

**Requirements**
- Read `case_id` and `case_no` from route query on page load.
- Store `case_id` internally in the form model for submit.
- Show a read-only case display field using `case_no`.
- Remove the editable case input for the case-driven flow.
- If route query is incomplete, attempt to resolve display data by `getCase(case_id)` using existing API helper.
- Do not send `case_no` in the create-document payload.

**Acceptance**
- User sees case number in Simplified Chinese UI as a read-only field.
- Save submits `case_id = case.id` and not `case_no`.
- Existing template selection and document submit behavior still work.
- Successful create returns HTTP `201`.


### DEMO-FE-DOC-03 — Chinese error handling for missing or invalid case context
**Goal**
The document create page must fail clearly when case context is missing or invalid, instead of relying on user manual entry.

**Scope (Atomic – FIXED)**
Frontend error-state hardening only.

**Allowed files**
- `frontend/src/modules/documents/pages/DocumentCreate.vue`

**Requirements**
- Add Chinese error messaging when `case_id` is missing.
- Add Chinese error messaging when `case_id` cannot resolve to a valid case.
- Prevent submit when required case context is unavailable.
- Keep errors within the existing page/banner pattern.

**Acceptance**
- Missing case context shows a clear Chinese message.
- Invalid case context shows a clear Chinese message.
- User cannot submit the form until valid case context exists.

## Forbidden Changes
- No backend changes.
- No database schema or migration edits.
- No router rewiring.
- No unrelated refactors.
- Do not broaden API contract to accept `case_no` as `case_id`.

## Verification Commands
For any one task execution selected from this file:

```bash
npm run lint
npm run typecheck
npm run build
```

Targeted runtime expectation:
- `POST /api/v1/documents` with valid token and valid `case_id` returns `201 Created`
- missing or invalid case context is blocked in FE with clear Chinese messaging

## Evidence Required
- `artifacts/<TASK-ID>/results.jsonl`
- `artifacts/<TASK-ID>/summary.md`
- `artifacts/<TASK-ID>/git/diff.patch`

## Completion Rule
- Reviewer cannot pass unless gates pass, evidence exists, scope stays within the chosen task allowlist, and exactly one task ID from this file was executed.
