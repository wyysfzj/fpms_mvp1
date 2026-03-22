# DEMO-DOC-00 — Demo Fix Runbook: Case Detail -> Create Document

**Type**: Doc change  
**Priority**: P0  
**Date**: 2026-03-08

## Goal
Freeze the atomic execution plan for the demo fix where a user enters from Case Detail -> Official Documents -> Create Document and must:
- see `case_no` immediately
- see the case association as read-only
- submit internal `case.id` only
- never manually edit case association in this flow

This runbook is planning-only. It does **not** implement product code.

## Confirmed problem
- `POST /api/v1/documents` exists and is wired.
- Backend creation resolves `payload.case_id` against `Case.id`, not `case_no`.
- The current create page treats `case_id` as user-editable "案件编号", which lets users submit `case_no` text and hit `404 CASE_NOT_FOUND`.
- Demo expectation is different: entering from a case page should show user-visible `case_no`, while internal submission must keep `case.id`.

## Contract freeze
- User-visible value: `case_no`
- Internal submitted value: `case.id`
- Entry path covered by this demo fix: Case Detail -> Documents tab -> Create Document
- In this entry path, case association is read-only
- No backend contract change
- No schema or router change
- All visible UI text remains Simplified Chinese

## Six-Agent team execution
- Lead: main thread assigns one explicit task file path per execution
- Architect (`explorer`): confirm route/query contract and readonly UX
- Frontend Developer (`worker`): implement exactly one FE task file
- Tester (`worker`): run `npm run lint`, `npm run typecheck`, `npm run build`, then smoke the flow
- Reviewer (`explorer`): verify allowlist, Simplified Chinese UI text, and no editable case association

## Atomic task list

### 1) `tasks/demo/DEMO-FE-DOC-01.md`
**Title**: Pass case context from Case Detail documents tab into document creation route

**Owner**: Frontend Developer  
**Scope**: routing handoff only

**Allowed files**
- `frontend/src/modules/cases/components/CaseDocumentsTab.vue`

**Requirements**
- Change the create navigation to route by name instead of string concatenation
- Pass query params for:
  - `case_id`: internal ID
  - `case_no`: display-only case number
- Do not change document creation payload logic here

**Acceptance**
- Clicking "登记公文" from a case page navigates to `/documents/new` with both `case_id` and `case_no`
- No visible English UI text added

### 2) `tasks/demo/DEMO-FE-DOC-02.md`
**Title**: Bootstrap document create page with readonly case context

**Owner**: Frontend Developer  
**Scope**: create-page state + readonly display

**Allowed files**
- `frontend/src/modules/documents/pages/DocumentCreate.vue`

**Requirements**
- Read `case_id` and `case_no` from route query on page entry
- Store internal `case_id` in form state for submission
- Show user-visible `case_no` in a read-only field or read-only display block
- Remove editable case association for this entry flow
- If `case_id` is present, user must not be able to edit associated case
- Keep submission payload using internal `case.id`

**Acceptance**
- Opening from case page shows `case_no` immediately
- Submitted payload still sends `case_id=<uuid/text-id>` and never sends `case_no`
- User cannot edit or overwrite the case association in this flow

### 3) `tasks/demo/DEMO-FE-DOC-03.md`
**Title**: Canonicalize readonly case display and context-missing error handling on document create

**Owner**: Frontend Developer  
**Scope**: guardrails and UX hardening for the same page

**Allowed files**
- `frontend/src/modules/documents/pages/DocumentCreate.vue`

**Requirements**
- Use existing case API by `case_id` to refresh or confirm the displayed `case_no`
- If case context is missing or invalid, block save and show a clear Simplified Chinese message instructing the user to re-enter from the case page
- Keep error text in Simplified Chinese

**Acceptance**
- Query tampering cannot cause the page to submit an arbitrary visible case number
- Missing/invalid case context is user-visible before save
- No backend change required

## Recommended execution order
1. `tasks/demo/DEMO-FE-DOC-01.md`
2. `tasks/demo/DEMO-FE-DOC-02.md`
3. `tasks/demo/DEMO-FE-DOC-03.md`

## Recommended first implementation task
If the next execution is meant to "directly land" the demo fix, start with:

`tasks/demo/DEMO-FE-DOC-01.md`

Then continue with:

`tasks/demo/DEMO-FE-DOC-02.md`

`DEMO-FE-DOC-03.md` is optional hardening if the first two are sufficient for the live demo path.

## Shared acceptance checklist
- User enters from Case Detail -> Official Documents -> Create Document
- Create page shows the correct `case_no`
- Case association is read-only
- Create request sends internal `case.id`
- `POST /api/v1/documents` returns `201`
- No new backend API or schema change
- UI text added/changed in scope is Simplified Chinese
- Frontend gates pass:
  - `npm run lint`
  - `npm run typecheck`
  - `npm run build`

## Evidence expectations for each implementation task
- `artifacts/<TASK-ID>/results.jsonl`
- `artifacts/<TASK-ID>/summary.md`
- `artifacts/<TASK-ID>/git/diff.patch`

## STOP contract
STOP and escalate before implementation if:
- the requested behavior requires backend contract changes
- the fix requires edits outside the task allowlist
- a reviewer finds user-visible non-Chinese text in touched FE scope
