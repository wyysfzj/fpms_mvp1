# Batch FA0 — FE Baseline Smoke Test — Task Plan

> **Team**: fa0-batch
> **Date**: 2026-02-26
> **Goal**: Verify all existing frontend pages load and render without console errors. **NO CODE CHANGES.**

---

## Batch Summary

- **Batch**: FA0 (FE Baseline Smoke Test)
- **Backend Dependency**: None (uses existing endpoints only)
- **Duration**: ~30 min
- **Constraint**: NO source file modifications unless blocking quality gate

---

## Task Decomposition

### T1: Architect Review & Plan (architect-agent)
- Read Claude_FE_enhance.md Batch FA0 section completely
- Verify backend dependency matrix: FA0 requires NONE → ✓
- List all 9 modules and pages to verify
- Review File Allowlist: FA0 has NO file allowlist (no changes permitted)
- Output: `01_Architect_Plan.md` in artifacts

### T2: Backend Health Verification (backend-agent)
- Verify backend server is running at http://localhost:8000
- Hit /healthz endpoint
- Test /api/v1/ endpoint accessibility
- Verify admin/admin123 login works via API
- Record API availability status

### T3: Frontend Quality Gate (frontend-agent)
- Run `npm run lint` — record pass/fail
- Run `npm run typecheck` — record pass/fail
- Run `npm run build` — record pass/fail
- Start dev server, verify http://localhost:5173 responds
- Record all findings

### T4: Smoke Test Checklist (test-agent)
- Execute the 10-point manual smoke checklist from Claude_FE_enhance.md
- Verify each module page loads without JS errors
- Check CRUD operations for Cases and Tasks
- Check DevTools console for uncaught errors
- Record pass/fail for each checkpoint

### T5: Review & Report (reviewer-agent)
- Collect findings from all agents
- Verify all 4 Success Criteria are assessed
- Write `04_Reviewer_Report.md` with acceptance criteria checklist
- Final pass/fail verdict

---

## Dependency Graph

```
T1 (Architect Plan)
 ├─→ T2 (Backend Health) [parallel]
 ├─→ T3 (FE Quality Gate) [parallel]
 └─→ T4 (Smoke Test) [after T2 + T3 confirm environments up]
      └─→ T5 (Review Report) [after all tasks complete]
```

---

## Success Criteria (from Claude_FE_enhance.md)

- [ ] All 9 modules' pages load without JS errors
- [ ] Login→Dashboard flow works
- [ ] CRUD operations work for at least Cases and Tasks
- [ ] DevTools console shows no uncaught errors
