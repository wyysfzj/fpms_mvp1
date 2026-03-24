# Batch FA0 — FE Baseline Smoke Test — Architect Plan

> **Agent**: architect-agent
> **Team**: fa0-batch
> **Date**: 2026-02-26
> **Source**: `Claude_FE_enhance.md` lines 139-193

---

## 1. Batch FA0 Summary

### What It Does
- Verifies **all existing frontend pages** load and render without console errors
- Runs the frontend quality gate (`npm run lint && npm run typecheck && npm run build`)
- Executes a **10-point manual smoke checklist** covering all 9 modules
- Records all findings for baseline documentation before code changes begin

### What It Does NOT Do
- **NO code changes** — zero source file modifications permitted
- **NO backend changes** — FA0 is purely a frontend verification pass
- **NO bug fixing** — issues discovered are logged as findings, not fixed
- **NO new features** — this is observation/verification only

---

## 2. Backend Dependency Verification

Per the **Backend Dependency Matrix** (Claude_FE_enhance.md §0.4):

| FE Batch | Requires Backend Batch | Key APIs Consumed |
|----------|----------------------|-------------------|
| **FA0** | **None (existing)** | All existing endpoints |

**Confirmed**: FA0 requires **ZERO backend changes**. It consumes only existing endpoints that should already be functional from the MVP1 baseline.

The backend must be running at `http://localhost:8000` with seed data loaded (admin/admin123).

---

## 3. File Allowlist

Per the batch definition in Claude_FE_enhance.md:

> **Duration**: ~30 min. NO code changes.

**Confirmed**: FA0 has **NO file allowlist** because **zero code changes are permitted**. The only outputs are:
- Artifacts files (`artifacts/FE_Batch_FA0_plan/` directory)
- Findings documentation

If any blocking issues are found (e.g., lint/typecheck/build failures), they are **documented as findings**, not fixed inline.

---

## 4. Complete Page Inventory

### 4.1 Standalone Routes (outside MainLayout)

| Route Path | Name | Component | Module |
|-----------|------|-----------|--------|
| `/login` | login | `Login.vue` | auth |
| `/forbidden` | forbidden | `PermissionDenied.vue` | views |
| `/:pathMatch(.*)*` | not_found | `NotFound.vue` | views |

### 4.2 Authenticated Routes (inside MainLayout, require auth)

| Route Path | Name | Component | Module | Permission |
|-----------|------|-----------|--------|------------|
| `/dashboard` | dashboard | `Dashboard.vue` | dashboard | (none) |
| `/cases` | cases | `CaseList.vue` | cases | CASES_READ |
| `/cases/new` | case_new | `CaseCreate.vue` | cases | CASES_WRITE |
| `/cases/:id` | case_detail | `CaseDetail.vue` | cases | CASES_READ |
| `/cases/:id/edit` | case_edit | `CaseEdit.vue` | cases | CASES_WRITE |
| `/documents` | documents | `DocumentList.vue` | documents | DOCUMENTS_READ |
| `/documents/new` | document_new | `DocumentCreate.vue` | documents | DOCUMENTS_WRITE |
| `/documents/:id` | document_detail | `DocumentDetail.vue` | documents | DOCUMENTS_READ |
| `/documents/:id/edit` | document_edit | `DocumentEdit.vue` | documents | DOCUMENTS_WRITE |
| `/tasks` | tasks | `TaskList.vue` | tasks | TASKS_READ |
| `/tasks/new` | task_new | `TaskCreate.vue` | tasks | TASKS_WRITE |
| `/tasks/today` | tasks_today | `TodayReminders.vue` | tasks | TASKS_READ |
| `/fees/drafts` | fee_drafts | `FeeDraftList.vue` | fees | FEES_READ |
| `/fees/drafts/new` | fee_draft_new | `FeeDraftCreate.vue` | fees | FEES_WRITE |
| `/fees/drafts/:id` | fee_draft_detail | `FeeDraftDetail.vue` | fees | FEES_READ |
| `/fees/rates` | fee_rates | `FeeRates.vue` | fees | FEES_READ |
| `/billing/bills` | bills | `BillList.vue` | billing | BILLING_READ |
| `/billing/bills/new` | bill_new | `BillCreate.vue` | billing | BILLING_WRITE |
| `/billing/bills/:id` | bill_detail | `BillDetail.vue` | billing | BILLING_READ |
| `/billing/payments` | payments | `PaymentList.vue` | billing | BILLING_READ |
| `/billing/payments/new` | payment_new | `PaymentCreate.vue` | billing | BILLING_WRITE |
| `/clients` | clients | `ClientList.vue` | clients | CLIENTS_READ |
| `/clients/new` | client_new | `ClientForm.vue` | clients | CLIENTS_WRITE |
| `/clients/:id/edit` | client_edit | `ClientForm.vue` | clients | CLIENTS_WRITE |
| `/settings/clients` | settings_clients | `ClientList.vue` | clients (legacy route) | SETTINGS_READ |
| `/system/templates` | system_templates | `TemplateList.vue` | system | SETTINGS_READ |
| `/system/params` | system_params | `SystemParams.vue` | system | SETTINGS_WRITE |
| `/system/letterheads` | system_letterheads | `LetterheadList.vue` | system | SETTINGS_WRITE |
| `/focus-demo` | focus_demo | `FocusDemo.vue` | views (demo) | (none) |

**Total**: 3 standalone routes + 28 authenticated routes = **31 routes total**

### 4.3 Component Inventory (non-page)

| Component | Module | Used In |
|-----------|--------|---------|
| `MainLayout.vue` | layout | All authenticated routes |
| `KpiCard.vue` | dashboard | Dashboard |
| `TodoTable.vue` | dashboard | Dashboard |
| `ActionCenter.vue` | dashboard | Dashboard |
| `FinanceRow.vue` | dashboard | Dashboard |
| `FinancePanel.vue` | dashboard | Dashboard |
| `NewCaseDrawer.vue` | dashboard | Dashboard |
| `PipeCard.vue` | dashboard | Dashboard |
| `WorkflowCaseTable.vue` | dashboard | Dashboard |
| `WorkflowOverview.vue` | dashboard | Dashboard |
| `CaseStepper.vue` | cases | CaseDetail |
| `CaseDeadlineCard.vue` | cases | CaseDetail |
| `CaseRelatedTasks.vue` | cases | CaseDetail |
| `LimitedEditDialog.vue` | cases | CaseDetail |
| `CaseReceiptsSummary.vue` | cases | CaseDetail |
| `AttachmentList.vue` | documents | DocumentDetail |
| `FeeDraftItemsTable.vue` | fees | FeeDraftDetail |
| `FeeRateForm.vue` | fees | FeeRates |

---

## 5. Smoke Test Checklist (10-Point)

From Claude_FE_enhance.md §FA0 Verification Script:

| # | Check | Navigation Path | Expected Behavior |
|---|-------|----------------|-------------------|
| 1 | Root redirect | Open `http://localhost:5173` | Redirects to `/login` (unauthenticated) |
| 2 | Login → Dashboard | Login with `admin/admin123` | Dashboard loads with KPI cards, no JS errors |
| 3 | Cases module | Navigate: Cases → list → Create | CaseList renders table; CaseCreate shows form |
| 4 | Documents module | Navigate: Documents → list → Create | DocumentList renders table; DocumentCreate shows form |
| 5 | Tasks module | Navigate: Tasks → list → Create → Today | TaskList renders; TaskCreate form works; TodayReminders loads |
| 6 | Fees module | Navigate: Fees → Drafts list → Rates list | FeeDraftList renders; FeeRates renders |
| 7 | Billing module | Navigate: Billing → Bills list → Payments list | BillList renders; PaymentList renders |
| 8 | Clients module | Navigate: Clients → list → New | ClientList renders; ClientForm shows create form |
| 9 | System module | Navigate: System → Params → Templates → Letterheads | SystemParams renders; TemplateList renders; LetterheadList renders |
| 10 | Console check | Open browser DevTools console | **No red errors** (warnings acceptable) |

### Smoke Test Prerequisites
- Backend running: `cd backend && uvicorn app.main:app --reload --port 8000`
- DB migrated and seeded: `alembic upgrade head && python scripts/seed_dev.py`
- Frontend dev server: `cd frontend && npm run dev`
- Browser with DevTools open

---

## 6. Quality Gate Commands

```bash
# From frontend/ directory
cd frontend

# 1. ESLint — must pass clean (or only warnings)
npm run lint

# 2. TypeScript type check — must pass
npm run typecheck

# 3. Vite production build — must succeed
npm run build
```

**Pass criteria**: All 3 commands exit with code 0.

**If any command fails**: Document the exact error in `findings.md`. Do NOT fix any source code. Determine if the failure is a pre-existing issue or a new regression.

---

## 7. Success Criteria

From Claude_FE_enhance.md §FA0 Success Criteria:

| # | Criterion | Verification Method |
|---|-----------|-------------------|
| 1 | All 9 modules' pages load without JS errors | Navigate to each module's pages, check DevTools console |
| 2 | Login → Dashboard flow works | Complete login flow with admin/admin123 |
| 3 | CRUD operations work for at least Cases and Tasks | Create a test case, verify it appears in list; create a test task, verify it appears in list |
| 4 | DevTools console shows no uncaught errors | Monitor console throughout all navigation |

---

## 8. Risk Assessment

### Known Issues / Potential Blockers

| Risk | Severity | Mitigation |
|------|----------|------------|
| Backend not running or not seeded | **HIGH** | Must confirm backend health (`curl http://localhost:8000/healthz`) before starting FE smoke test |
| Dashboard KPI fragility | **MEDIUM** | Dashboard uses client-side aggregation across 5 endpoints (per audit). May show errors if any endpoint returns unexpected data. Document but don't fix. |
| Missing API data fields | **LOW** | Known gaps: Tasks missing `case_no`/`client_name`, Cases missing `client_name`, Bills minimal schema. Pages may render but show empty columns. Document but don't fix. |
| CaseDetail stubbed tabs | **LOW** | 4 tabs are known stubs (Claims, OfficialDocs, Fees, Tasks). Expected to show placeholder content. This is a known gap addressed in FA1. |
| TypeScript strictness | **MEDIUM** | `tsconfig.json` settings may cause typecheck warnings/errors on existing code. Document any findings. |
| Element Plus locale | **LOW** | Chinese locale import (`element-plus/es/locale/lang/zh-cn`) may cause build issues depending on version. |
| Duplicate client route | **LOW** | `/clients` and `/settings/clients` both point to `ClientList.vue`. Both should work identically. |
| Focus Demo page | **LOW** | `/focus-demo` is a demo route — may or may not render correctly. Not part of core modules. |

### Pages NOT Covered by 10-Point Checklist
The checklist focuses on list + create flows. These pages are **not explicitly tested** but should be verified if time allows:
- `/cases/:id` (CaseDetail) — detail view with stubbed tabs
- `/cases/:id/edit` (CaseEdit) — requires existing case
- `/documents/:id` (DocumentDetail) — requires existing document
- `/documents/:id/edit` (DocumentEdit) — requires existing document
- `/fees/drafts/:id` (FeeDraftDetail) — requires existing fee draft
- `/billing/bills/:id` (BillDetail) — requires existing bill
- `/billing/bills/new` (BillCreate) — create form
- `/billing/payments/new` (PaymentCreate) — create form
- `/clients/:id/edit` (ClientForm edit mode) — requires existing client
- `/forbidden` (PermissionDenied) — static page
- `/focus-demo` (FocusDemo) — demo page
- `/nonexistent` (NotFound) — 404 catch-all

---

## 9. Execution Summary

| Item | Value |
|------|-------|
| Batch | FA0 — FE Baseline Smoke Test |
| Duration | ~30 min |
| Code changes | **ZERO** |
| Backend dependency | **NONE** |
| File allowlist | **NONE** (no files may be modified) |
| Quality gate | `npm run lint && npm run typecheck && npm run build` |
| Smoke test | 10-point checklist covering 9 modules |
| Success criteria | 4 criteria from spec |
| Artifacts produced | `01_Architect_Plan.md`, `findings.md`, `progress.md`, `review_report.md` |
