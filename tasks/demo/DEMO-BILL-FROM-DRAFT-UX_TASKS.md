# DEMO-BILL-FROM-DRAFT-UX — Demo Atomic Tasks

**Type**: Doc change  
**Priority**: P0  
**Date**: 2026-03-08

## Goal

Freeze the atomic execution plan for three demo issues in the fee draft to bill flow:

1. bill creation from fee draft is misleading:
   - UI asks for a readable draft number
   - backend actually requires `draft_ids` as UUIDs
   - using UUID may still fail with `BILL_ITEM_REQUIRED` when the draft has no fee items
2. fee draft list still shows UUIDs as primary visible labels
3. bill detail / relation chain still cannot show fee draft linkage in a readable way

This file is planning-only. It does **not** implement product code.  
Per `AGENTS.md`, each later execution must implement **exactly one** task from this file.

## Confirmed Problems

### Problem A — bill creation from fee drafts uses the wrong visible identifier

- Frontend bill creation page says:
  - "输入已锁定费用草稿的编号"
- But the form actually submits:
  - `draft_ids: string[]`
- Backend `POST /api/v1/bills/from-drafts` resolves `draft_ids` strictly against `FeeDraft.id`
- Therefore:
  - entering display text like `GRANT_FEE-0F3334A4` fails with not found
  - only UUID works
- This is a contract/UX mismatch, not a router issue

### Problem B — `BILL_ITEM_REQUIRED` is currently discovered too late

- Backend bill generation validates all selected drafts have fee items
- If a locked draft has zero fee items, backend returns:
  - `400 BILL_ITEM_REQUIRED`
- Current frontend does not pre-screen or explain this
- Demo operator only learns after submit

### Problem C — fee draft list still exposes UUIDs

- Backend fee draft list already provides:
  - `case_no`
  - `client_name`
- Frontend fee draft list still renders:
  - `row.id`
  - `row.case_id`
  - `row.client_id`
- Result: demo table remains UUID-heavy although readable data already exists

### Problem D — bill detail cannot show readable fee draft linkage

- `BillDetail.vue` relation chain currently passes:
  - client
  - case
  - bill
- It does **not** pass `feeDraft`
- Backend `GET /api/v1/bills/{id}` does not expose:
  - source draft ids
  - source draft display labels
  - enriched case/client fields and items in a complete detail contract
- Result:
  - bill ↔ fee draft linkage is invisible or falls back to UUID-heavy display

## Contract Freeze

- Bill creation from drafts must keep backend input contract based on internal `draft.id`
- User-visible bill creation UI must not require typing UUID
- Demo-visible labels should prioritize:
  - fee draft display number
  - case number
  - client name
- Existing database schema remains unchanged
- No migration changes
- No router rewiring outside existing modules
- All touched UI text must remain Simplified Chinese

## Six-Agent Team Execution

- Lead: main thread assigns one explicit task ID per execution
- Architect (`explorer`): freeze bill creation selector contract and bill detail display contract
- Backend Developer (`worker`): implement exactly one backend atomic task
- Frontend Developer (`worker`): implement exactly one frontend atomic task
- Tester (`worker`): run scoped gates and record evidence
- Reviewer (`explorer`): validate status codes, readability, and no scope drift

## Atomic Task List

### 1) `tasks/demo/DEMO-FE-BILL-01.md`
**Title**: Replace free-text draft UUID entry with readable locked-draft selector in bill creation

**Owner**: Frontend Developer  
**Scope**: bill create page only

**Allowed files**
- `frontend/src/modules/billing/pages/BillCreate.vue`

**Requirements**
- Remove the current free-text / allow-create behavior for `draft_ids`
- Load fee drafts from existing fee draft list API
- Only allow choosing drafts with:
  - `status = LOCKED`
  - positive amount
- Show readable option labels using:
  - fee draft display number
  - case number
  - client name
  - amount
- Keep submitted value as internal `draft.id`
- Add clear Chinese helper text explaining:
  - only locked drafts with billable items can be used
- Do not change backend contract in this task

**Acceptance**
- User can create a bill without typing UUID manually
- Readable display labels are shown in selector
- UUID remains internal only
- Drafts with no billable amount are not offered


### 2) `tasks/demo/DEMO-FE-FEE-03.md`
**Title**: Make fee draft list use readable business labels instead of UUIDs

**Owner**: Frontend Developer  
**Scope**: fee draft list page only

**Allowed files**
- `frontend/src/modules/fees/pages/FeeDraftList.vue`

**Requirements**
- Replace visible UUID-heavy columns with readable labels:
  - draft display number
  - case number
  - client name
- Keep UUID only for route identity and internal actions
- Preserve existing navigation behavior

**Acceptance**
- Fee draft list no longer primarily shows UUIDs
- Case/client columns display readable labels whenever backend data exists
- Row click behavior remains intact


### 3) `tasks/demo/DEMO-BE-BILL-01.md`
**Title**: Enrich bill detail read contract with readable client/case/source-draft fields

**Owner**: Backend Developer  
**Scope**: bill detail endpoint only

**Allowed files**
- `backend/app/modules/billing/api.py`
- `backend/app/modules/billing/schemas.py`

**Requirements**
- Extend `GET /api/v1/bills/{bill_id}` response to include at least:
  - `client_name`
  - `case_id`
  - `case_no`
  - `items`
  - source draft linkage fields such as:
    - `source_draft_ids`
    - `source_draft_labels`
    - or `primary_draft_id` / `primary_draft_label`
- Populate those fields from existing `BillItem`, `FeeDraft`, `Case`, `Client`
- Preserve existing status code semantics:
  - `200` existing bill
  - `404` missing bill
- No schema changes

**Acceptance**
- Bill detail response is sufficient for frontend to show readable client/case/draft linkage
- Existing bill detail request remains `200`
- Missing bill remains `404`


### 4) `tasks/demo/DEMO-FE-BILL-02.md`
**Title**: Align billing frontend types with enriched bill detail contract

**Owner**: Frontend Developer  
**Scope**: billing API types only

**Allowed files**
- `frontend/src/api/billing.types.ts`
- `frontend/src/api/billing.ts`

**Requirements**
- Add optional fields matching enriched bill detail contract
- Preserve existing bill list/detail read behavior
- Keep manual bill and payment APIs untouched unless required by type alignment

**Acceptance**
- Frontend bill types support readable case/client/source-draft display fields
- Existing typecheck/build remain clean


### 5) `tasks/demo/DEMO-FE-BILL-03.md`
**Title**: Show readable fee draft linkage in bill detail relation chain and overview

**Owner**: Frontend Developer  
**Scope**: bill detail page only

**Allowed files**
- `frontend/src/modules/billing/pages/BillDetail.vue`

**Requirements**
- Use enriched bill detail fields to show:
  - client name
  - case number
  - fee draft display label
- Pass `feeDraft` into `RelationChainCard`
- In overview, stop falling back to UUID as primary visible label when readable data exists
- If multiple source drafts exist, show a stable readable summary

**Acceptance**
- Bill detail relation chain includes fee draft linkage
- Bill overview prioritizes readable business labels
- UUID is no longer the primary visible value in this flow


### 6) `tasks/demo/DEMO-QA-BILL-01.md`
**Title**: Demo smoke and evidence for bill creation from fee drafts and readable linkage

**Owner**: Tester  
**Scope**: verification only

**Allowed files**
- `artifacts/DEMO-QA-BILL-01/**`

**Requirements**
- Verify readable locked-draft selection is available in bill create flow
- Verify bill creation from a valid locked draft with items returns `201`
- Verify selecting drafts without billable items is blocked at UI level or clearly explained
- Verify fee draft list no longer primarily shows UUIDs
- Verify bill detail relation chain shows readable fee draft linkage
- Record evidence artifacts

**Acceptance**
- Valid bill-from-draft flow completes successfully
- No blocking UUID-only interaction remains in the demo path
- Evidence exists under `artifacts/DEMO-QA-BILL-01/`

## Recommended Execution Order

1. `tasks/demo/DEMO-FE-BILL-01.md`
2. `tasks/demo/DEMO-FE-FEE-03.md`
3. `tasks/demo/DEMO-BE-BILL-01.md`
4. `tasks/demo/DEMO-FE-BILL-02.md`
5. `tasks/demo/DEMO-FE-BILL-03.md`
6. `tasks/demo/DEMO-QA-BILL-01.md`

## Recommended First Implementation Task

Start with:

`tasks/demo/DEMO-FE-BILL-01.md`

This is the smallest demo-facing fix that removes the most confusing live interaction:
requiring the operator to type a UUID while the UI claims to accept a business draft number.

## Shared Acceptance Checklist

- Bill creation from drafts no longer requires manual UUID typing
- Locked, billable drafts are selectable by readable label
- Fee draft list prioritizes readable labels over UUIDs
- Bill detail relation chain can show fee draft linkage in a readable way
- No database schema or migration changes
- No unrelated refactors
- Touched UI text remains Simplified Chinese

## Verification Commands

Frontend implementation tasks:

```bash
cd frontend && npm run lint
cd frontend && npm run typecheck
cd frontend && npm run build
```

Backend implementation tasks:

```bash
cd backend && ruff check --fix .
cd backend && ruff format .
cd backend && ruff check .
cd backend && pytest -q
```

Runtime expectations:

- `POST /api/v1/bills/from-drafts` with valid locked draft UUID and non-empty items returns `201`
- invalid draft id returns `404`
- empty-item draft should not be a confusing demo path; frontend should pre-screen or clearly explain
- fee draft list should show readable draft/case/client labels
- bill detail relation chain should show readable fee draft linkage

## Evidence Expectations

- `artifacts/<TASK-ID>/results.jsonl`
- `artifacts/<TASK-ID>/summary.md`
- `artifacts/<TASK-ID>/git/diff.patch`

## STOP Contract

STOP and escalate before implementation if:

- the fix requires database schema changes
- the task requires edits outside its allowlist
- bill detail linkage requires a wider billing domain refactor than one atomic task can safely contain
- readable draft selection cannot be implemented without changing authoritative backend input semantics
