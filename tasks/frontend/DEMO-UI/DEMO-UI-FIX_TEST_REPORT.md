# DEMO-UI FIX-01/02/03 Test Report

## Test Run Metadata
- **Date**: 2026-02-10
- **Branch**: master
- **Base Commit**: 661970e (chore: baseline snapshot before ENH-00-11 cleanup)
- **Frontend**: Vue 3 + TypeScript + Element Plus + Vite 5.4.21
- **Backend**: Not required for gate verification; required for manual smoke (T01-T14)
- **Tester**: Claude Code (automated gates) + manual browser inspection needed for T01-T14

---

## Gate Results (T15) — PASS

### ESLint
```
> eslint . --max-warnings 0
(clean — no warnings, no errors)
```
**Result**: PASS

### TypeScript
```
> vue-tsc --noEmit
(clean — no type errors)
```
**Result**: PASS

### Vite Build
```
> vite build
✓ 1645 modules transformed.
✓ built in 2.93s
```
**Result**: PASS

Key chunk sizes (affected pages):
| Chunk | Size | gzip |
|-------|------|------|
| CaseList | 3.23 kB | 1.38 kB |
| TaskList | 6.23 kB | 2.23 kB |
| BillList | 3.44 kB | 1.52 kB |
| FeeDraftList | 3.83 kB | 1.61 kB |
| DocumentList | 3.51 kB | 1.46 kB |
| CaseDetail | 11.84 kB | 3.92 kB |
| DocumentDetail | 7.24 kB | 2.69 kB |
| FeeDraftDetail | 12.93 kB | 4.20 kB |
| BillDetail | 8.48 kB | 2.89 kB |

---

## Static Code Verification

### FIX-01: CSS Selector & Hardcoded Colors
| Check | Status | Evidence |
|-------|--------|----------|
| `demo-themes.css` selector uses `.sidebar-nav` (not `.sidebar`) | PASS | Line 59: `body.style-b .sidebar-nav .nav-item.router-link-active` |
| `layout.css` hover uses `var(--sidebar-hover-bg, #F8FAFC)` | PASS | Line 62 |
| `layout.css` active uses `var(--sidebar-active-bg, #EFF6FF)` | PASS | Line 68 |
| `layout.css` active color uses `var(--sidebar-active-text, var(--color-primary))` | PASS | Line 69 |
| `demo-themes.css` defines `--sidebar-hover-bg: #F1F5F9` in style-b block | PASS | Line 15 |

### FIX-02: Detail Pages Chinese Labels
| Check | Status | Evidence |
|-------|--------|----------|
| CaseDetail imports `ZH` from `labels.zh.ts` | PASS | `import { ZH } from '../../../constants/labels.zh'` |
| CaseDetail uses `ZH.caseDetail.*` for all labels | PASS | 0 remaining English hardcoded labels |
| DocumentDetail uses `ZH.docDetail.*` | PASS | 0 remaining English hardcoded labels |
| FeeDraftDetail uses `ZH.feeDetail.*` | PASS | Confirm dialogs also localized |
| BillDetail uses `ZH.billDetail.*` | PASS | Table column labels, summary row, print messages localized |

### FIX-03: List Pages Chinese Labels
| Check | Status | Evidence |
|-------|--------|----------|
| All 5 list pages import `ZH` | PASS | grep confirms `ZH.*.title` in all 5 files |
| No remaining English hardcoded labels in scope pages | PASS | grep for 25 English labels returns 0 matches in target pages |
| Exception: `LimitedEditDialog.vue` has 1 English occurrence | KNOWN | Not in scope (dialog component, not a page) |

### `labels.zh.ts` Extension
| Section | Keys Added | Status |
|---------|------------|--------|
| `common` | refresh, view, total, goBack, noContent | PASS |
| `detail` | back, quickActions, overview | PASS |
| `caseDetail` | 22 keys (editCase → tasksPlaceholder) | PASS |
| `docDetail` | 8 keys (editDoc → noContent) | PASS |
| `feeDetail` | 18 keys (refresh → unlockSuccess) | PASS |
| `billDetail` | 19 keys (printBill → templateNotConfigured) | PASS |
| `caseList` | 12 keys (title → emptyMsg) | PASS |
| `taskList` | 14 keys (title → actionSuccess) | PASS |
| `billList` | 8 keys (title → emptyMsg) | PASS |
| `feeList` | 9 keys (title → emptyMsg) | PASS |
| `docList` | 10 keys (title → emptyMsg) | PASS |

---

## Manual Test Cases (Browser Verification Required)

> These tests require `VITE_DEMO_UI=1` and a running backend with seeded data. To be executed by a human tester.

| ID | Category | Test | Expected | Status |
|----|----------|------|----------|--------|
| T01 | FIX-01 | Sidebar active item background = `#EFF6FF` | `--sidebar-active-bg` resolves | PENDING (manual) |
| T02 | FIX-01 | Sidebar hover background = `#F1F5F9` | `--sidebar-hover-bg` resolves | PENDING (manual) |
| T03 | FIX-02 | CaseDetail all labels Chinese | 返回, 编辑案件, 概览, 案件信息... | PENDING (manual) |
| T04 | FIX-02 | DocumentDetail all labels Chinese | 返回, 编辑文档, 文档内容... | PENDING (manual) |
| T05 | FIX-02 | FeeDraftDetail all labels Chinese | 返回, 刷新, 锁定/解锁, 明细/概览... | PENDING (manual) |
| T06 | FIX-02 | BillDetail all labels Chinese | 返回, 打印账单, 明细/概览... | PENDING (manual) |
| T07 | FIX-03 | CaseList Chinese: 案件列表, 新建案件 | Column headers all Chinese | PENDING (manual) |
| T08 | FIX-03 | TaskList Chinese: 任务列表, 新建任务 | Column headers all Chinese | PENDING (manual) |
| T09 | FIX-03 | BillList Chinese: 账单列表, 新建账单 | Column headers all Chinese | PENDING (manual) |
| T10 | FIX-03 | FeeDraftList Chinese: 费用草稿, 新建草稿 | Column headers all Chinese | PENDING (manual) |
| T11 | FIX-03 | DocumentList Chinese: 文档列表, 新建文档 | Column headers all Chinese | PENDING (manual) |
| T12 | FIX-03 | TaskList close dialog Chinese | 关闭任务 / 关闭 / 取消 | PENDING (manual) |
| T13 | FIX-02 | FeeDraftDetail lock dialog Chinese | 锁定草稿 / 锁定 / 取消 | PENDING (manual) |
| T14 | FIX-02 | Detail not-found Chinese | 未找到案件/文档/草稿/账单 | PENDING (manual) |
| T15 | Gates | lint + typecheck + build | All pass, 0 warnings | **PASS** |

---

## Summary

| Category | Total | PASS | PENDING | FAIL |
|----------|-------|------|---------|------|
| Automated (Gates) | 1 | 1 | 0 | 0 |
| Static Verification | 12 | 12 | 0 | 0 |
| Manual (Browser) | 14 | 0 | 14 | 0 |
| **Total** | **27** | **13** | **14** | **0** |

### Conclusion
- **Automated gates**: PASS (lint, typecheck, build all clean)
- **Static code review**: PASS (CSS selectors correct, all labels wired to `ZH.*`, no remaining English hardcoded labels in target pages)
- **Manual browser verification**: PENDING — requires human tester with `VITE_DEMO_UI=1` and running backend

### Files Modified in FIX-01/02/03
1. `frontend/src/styles/demo-themes.css` — selector fix + `--sidebar-hover-bg`
2. `frontend/src/styles/layout.css` — hardcoded colors → CSS vars
3. `frontend/src/constants/labels.zh.ts` — extended with 120+ Chinese labels
4. `frontend/src/modules/cases/pages/CaseDetail.vue` — ZH labels
5. `frontend/src/modules/documents/pages/DocumentDetail.vue` — ZH labels
6. `frontend/src/modules/fees/pages/FeeDraftDetail.vue` — ZH labels + dialog messages
7. `frontend/src/modules/billing/pages/BillDetail.vue` — ZH labels + summary + print messages
8. `frontend/src/modules/cases/pages/CaseList.vue` — ZH labels
9. `frontend/src/modules/tasks/pages/TaskList.vue` — ZH labels + dialog messages
10. `frontend/src/modules/billing/pages/BillList.vue` — ZH labels
11. `frontend/src/modules/fees/pages/FeeDraftList.vue` — ZH labels
12. `frontend/src/modules/documents/pages/DocumentList.vue` — ZH labels

### Test Documentation Enhanced
13. `docs/frontend_smoke_flows.md` — added DEMO-UI note + Section 9 (label mapping + 5 DEMO-UI smoke flows)
14. `docs/FPMS_Frontend_Manual_Test_User_Guide.md` — added Section 0.0 DEMO-UI mode note + Section 5.8 DEMO-UI verification

### Known Out-of-Scope Items
- `LimitedEditDialog.vue` retains 1 English string ("Save") — not in FIX scope (dialog component)
- Create/Edit form pages (CaseCreate, CaseEdit, DocumentCreate, etc.) not localized — not in FIX scope
- Client pages not localized — not in FIX scope
- System/Template pages not localized — not in FIX scope

### Manual Testing Instructions
To execute T01-T14:
1. Ensure backend is running: `cd backend && uvicorn app.main:app --reload --port 8000`
2. Ensure DB is seeded: `cd backend && python scripts/seed_dev.py`
3. Set `VITE_DEMO_UI=1` in `frontend/.env`
4. Start frontend: `cd frontend && npm run dev`
5. Open `http://localhost:5173` in browser
6. Login with `admin / admin123`
7. Follow test steps for T01-T14 as documented above
8. Update this report with results and screenshots
