# DEMO_CN_UI — Demo Atomic Tasks

**Type**: Doc change  
**Priority**: P0  
**Date**: 2026-03-08

## Goal
Freeze the atomic execution plan for the demo issue where frontend UI still contains English or mixed Chinese-English text, violating the repository rule that all user-facing UI text must be Simplified Chinese.

This file is planning-only. It does **not** implement product code.  
Per `AGENTS.md`, each later execution must implement **exactly one** task from this file.

## Confirmed Problem

### Problem A — case legal status can fall back to English codes

- Frontend case status display is centralized in `frontend/src/constants/displayText.ts`
- `getCaseStatusText()` falls back to raw status code when no Chinese label exists
- Confirmed missing or risky values include:
  - `GRANT_PENDING`
  - `PENDING`
  - `WITHDRAWN`
  - `ABANDONED`
  - `EXPIRED`
- This can surface English status text in:
  - case detail
  - case list
  - workflow stepper
  - any other UI using the shared status display helper

### Problem B — case edit legal-status options are not fully aligned with canonical display mapping

- Case edit page exposes status options that are broader than the current shared Chinese display map
- Some status values shown in UI are not covered by the shared label helper
- This creates inconsistency between:
  - selectable labels
  - list/detail rendering
  - workflow rendering

### Problem C — other pages still expose mixed Chinese-English UI text

- Confirmed examples include:
  - `ID` shown directly in visible labels and table headers
  - English enum examples such as `PUBLISHED`, `SUB_EXAM`
  - mixed placeholders and helper text using technical English codes
- Confirmed high-risk pages include:
  - `frontend/src/modules/system/pages/DocTemplateList.vue`
  - `frontend/src/modules/consulting/pages/ConsultingFeeDraftCreate.vue`
  - `frontend/src/modules/consulting/pages/ConsultingCaseCreate.vue`
  - `frontend/src/modules/commission/pages/CommissionSettlement.vue`
  - `frontend/src/modules/annuity/pages/GovPaymentCreate.vue`
  - `frontend/src/modules/annuity/pages/AnnuityTaskList.vue`

## Contract Freeze

- All user-facing UI text touched by these tasks must be Simplified Chinese
- Technical enum values may remain in code and payloads, but must not be shown raw to users unless the task explicitly requires it
- No database schema changes
- No backend router rewiring
- Prefer centralized display-text mapping over repeated local label maps
- Keep existing functional behavior unchanged unless the task explicitly addresses a contract mismatch

## Six-Agent Team Execution

- Lead: main thread assigns one explicit task ID per execution
- Architect (`explorer`): freeze UI text scope and shared mapping strategy
- Frontend Developer (`worker`): implement exactly one frontend atomic task
- Tester (`worker`): run scoped checks and capture evidence
- Reviewer (`explorer`): verify no visible English remains within the task scope and confirm Simplified Chinese compliance

## Atomic Task List

### 1) `tasks/dmmo/DEMO-FE-CN-01.md`
**Title**: Complete shared Chinese mapping for case legal statuses

**Owner**: Frontend Developer  
**Scope**: shared case status display only

**Allowed files**
- `frontend/src/constants/displayText.ts`
- `frontend/src/constants/workflow.ts`

**Requirements**
- Add Chinese labels for every case status currently surfaced by frontend flows
- Ensure `GRANT_PENDING` no longer renders as English in UI
- Ensure legacy statuses such as `PENDING`, `WITHDRAWN`, `ABANDONED`, and `EXPIRED` also render in Chinese
- Keep workflow fallback behavior controlled and user-safe
- Do not broaden scope into unrelated page copy cleanup in this task

**Acceptance**
- Case detail renders Chinese legal status for all known case statuses
- Case list and workflow stepper no longer show raw English case status codes
- No files outside allowlist change


### 2) `tasks/dmmo/DEMO-FE-CN-02.md`
**Title**: Align case edit status selector with canonical Chinese case-status display

**Owner**: Frontend Developer  
**Scope**: case edit page only

**Allowed files**
- `frontend/src/modules/cases/pages/CaseEdit.vue`

**Requirements**
- Ensure visible status options are Simplified Chinese
- Align selectable status set with the canonical frontend-supported status display strategy
- Remove or clearly handle options that would otherwise create inconsistent English fallback behavior
- Preserve existing save flow unless a status option is clearly invalid for current frontend contract

**Acceptance**
- Case edit legal-status selector is fully Simplified Chinese
- Visible case status choices no longer contradict shared status rendering
- No unrelated page files change


### 3) `tasks/dmmo/DEMO-FE-CN-03.md`
**Title**: Remove mixed English UI text from system and consulting demo pages

**Owner**: Frontend Developer  
**Scope**: targeted mixed-language cleanup

**Allowed files**
- `frontend/src/modules/system/pages/DocTemplateList.vue`
- `frontend/src/modules/consulting/pages/ConsultingFeeDraftCreate.vue`
- `frontend/src/modules/consulting/pages/ConsultingCaseCreate.vue`

**Requirements**
- Replace user-visible English placeholders, labels, and helper text with Simplified Chinese
- Preserve technical values in submitted payloads where required by backend contracts
- Avoid changing API semantics or backend-facing enum codes
- Keep UI wording clear for demo use

**Acceptance**
- The listed pages no longer expose mixed Chinese-English visible text in their touched areas
- Technical codes remain internal where necessary
- No files outside allowlist change


### 4) `tasks/dmmo/DEMO-FE-CN-04.md`
**Title**: Normalize visible `ID`-style labels to Simplified Chinese on demo pages

**Owner**: Frontend Developer  
**Scope**: targeted label normalization only

**Allowed files**
- `frontend/src/modules/commission/pages/CommissionSettlement.vue`
- `frontend/src/modules/annuity/pages/GovPaymentCreate.vue`
- `frontend/src/modules/annuity/pages/AnnuityTaskList.vue`
- `frontend/src/modules/commission/pages/CommissionList.vue`

**Requirements**
- Replace visible `ID` labels, headers, and placeholders with Simplified Chinese wording such as:
  - `编号`
  - `标识`
  - `案件编号`
  - `客户编号`
- Preserve route params, payload field names, and backend API contracts
- Do not bundle unrelated status-translation refactors into this task

**Acceptance**
- The listed pages no longer show raw `ID` as user-facing UI text in touched scope
- Existing filtering and table behavior remains unchanged
- No files outside allowlist change


### 5) `tasks/dmmo/DEMO-QA-CN-01.md`
**Title**: Demo UI Simplified Chinese audit and evidence

**Owner**: Tester  
**Scope**: verification only

**Allowed files**
- `artifacts/DEMO-QA-CN-01/**`
- optional evidence summary under `tasks/dmmo/` if explicitly required

**Requirements**
- Verify case legal status no longer shows raw English codes in touched flows
- Verify touched pages no longer expose mixed Chinese-English visible UI text
- Run frontend quality gates
- Record evidence artifacts

**Acceptance**
- Touched pages render Simplified Chinese visible UI text
- Frontend checks pass for the implemented task scope
- Evidence exists under `artifacts/DEMO-QA-CN-01/`

## Recommended Execution Order

1. `tasks/dmmo/DEMO-FE-CN-01.md`
2. `tasks/dmmo/DEMO-FE-CN-02.md`
3. `tasks/dmmo/DEMO-FE-CN-03.md`
4. `tasks/dmmo/DEMO-FE-CN-04.md`
5. `tasks/dmmo/DEMO-QA-CN-01.md`

## Recommended First Implementation Task

Start with:

`tasks/dmmo/DEMO-FE-CN-01.md`

This is the smallest atomic fix that removes the currently observed `GRANT_PENDING` English leak from legal-status UI.

## Shared Acceptance Checklist

- Known case legal statuses render in Simplified Chinese
- Touched pages do not expose raw English status codes or mixed Chinese-English helper text
- User-visible labels follow the Simplified Chinese UI rule
- No database schema or migration changes
- No backend router rewiring
- No unrelated refactors outside the atomic task allowlist

## Verification Commands

Frontend implementation tasks:

```bash
cd frontend && npm run lint
cd frontend && npm run typecheck
cd frontend && npm run build
```

Runtime expectations:
- case legal status displays Chinese text instead of `GRANT_PENDING`
- touched pages do not show visible raw English enum examples unless explicitly exempted
- existing page behavior remains functional

## Evidence Expectations

- `artifacts/<TASK-ID>/results.jsonl`
- `artifacts/<TASK-ID>/summary.md`
- `artifacts/<TASK-ID>/git/diff.patch`

## STOP Contract
STOP and escalate before implementation if:
- the requested cleanup requires edits outside the assigned task allowlist
- a visible English term is actually a backend-controlled business code that product explicitly requires to remain visible
- frontend-only cleanup would create backend contract ambiguity or invalid saved values
