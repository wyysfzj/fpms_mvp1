# Batch FA1 — Case Detail Tab Completion — Task Plan

> **Team**: fa1-batch
> **Date**: 2026-02-26
> **Goal**: Replace the 4 stubbed tabs in CaseDetail.vue with actual data views using existing API endpoints filtered by `case_id`.

---

## Batch Summary

- **Batch**: FA1 (Case Detail Tab Completion)
- **Backend Dependency**: None — uses existing filtered list endpoints
- **File Allowlist** (strict — no other files may be modified):
  1. `frontend/src/modules/cases/pages/CaseDetail.vue` (modify)
  2. `frontend/src/modules/cases/components/CaseDocumentsTab.vue` (NEW)
  3. `frontend/src/modules/cases/components/CaseTasksTab.vue` (NEW)
  4. `frontend/src/modules/cases/components/CaseFeesTab.vue` (NEW)
  5. `frontend/src/modules/cases/components/CaseClaimsTab.vue` (NEW)

---

## Task Decomposition

### T1: Architect Review & Plan (architect-agent)
- Read Claude_FE_enhance.md FA1 section completely
- Read existing CaseDetail.vue to understand tab structure
- Read existing case components for patterns
- Read API clients (documents.ts, tasks.ts, fees.ts) for available functions
- Verify backend dependency: FA1 requires NONE
- Verify File Allowlist: exactly 5 files
- Verify API endpoints support case_id filtering
- Output: `01_Architect_Plan.md` with detailed implementation spec
- **WAIT for user approval before implementation starts**

### T2: Backend API Verification (backend-agent)
- Verify GET /documents?case_id= works
- Verify GET /tasks?case_id= works
- Verify GET /fees/drafts?case_id= works
- Verify case detail response includes applicants/inventors
- Document response schemas for frontend

### T3: Frontend Implementation (frontend-agent)
- Create 4 new tab components
- Modify CaseDetail.vue to import and use them
- Follow existing component patterns
- All text in Chinese
- Pass quality gate

### T4: Test Verification (test-agent)
- Verify quality gate passes
- Run backend tests (no regressions)
- Verify API endpoints return correct data with case_id filter
- Check types match between API and components

### T5: Review Report (reviewer-agent)
- Review all changes against acceptance criteria
- Verify File Allowlist compliance
- Write review report

---

## Dependency Graph

```
T1 (Architect Plan) → [USER APPROVAL] → T3 (Frontend Impl)
T2 (Backend API Verify) ─────────────→ T3 (Frontend Impl)
T3 (Frontend Impl) → T4 (Test) → T5 (Review)
```

---

## Acceptance Criteria (from Claude_FE_enhance.md)

- [ ] All 4 tabs show real data (not placeholder text)
- [ ] Docs tab shows documents linked to this case
- [ ] Tasks tab shows tasks linked to this case with status tags
- [ ] Fees tab shows fee drafts linked to this case
- [ ] Claims tab shows applicants and inventors
- [ ] "Create" buttons navigate to correct forms with case_id pre-filled
- [ ] Quality gate passes
