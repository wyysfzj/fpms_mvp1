# FC4 Review Report — Billing Offset Reversal + Receipt Enrichment

> Reviewer Agent | Date: 2026-02-27

## Overall Verdict
**PASS**

All 5 acceptance criteria are satisfied. Code quality is high. Only the 4 allowlisted files were created/modified. All Chinese labels present. CSS uses design-token variables throughout. No blocking issues found.

---

## Acceptance Criteria Checklist

| # | Criterion | Status | Notes |
|---|-----------|--------|-------|
| 1 | `billing.types.ts`: `OffsetListItem` has `reversed_at?: string`; `CaseReceiptsSummary` has enriched fields (fee_type, fee_code, year_no, is_arrears, invoice_no, is_commissionable) | PASS | `reversed_at` at line 128; enriched fields at lines 148-153. All typed as optional. |
| 2 | `billing.ts`: `BackendOffset.reversed_at`; `mapOffset()` maps it; `BackendCaseReceipt` interface; `mapCaseReceipt()` bridges shapes; `getCaseReceipts()` uses mapper; `getOffsets()` accepts `bill_id` | PASS | `BackendOffset.reversed_at` line 73. `mapOffset` line 154. `BackendCaseReceipt` lines 318-331. `mapCaseReceipt` lines 333-350 (receivable_amt→total_billed, received_amt→total_paid, diff→total_outstanding). `getCaseReceipts` lines 355-358. `getOffsets` param at line 287. |
| 3 | `BillDetail.vue`: "抵扣记录" tab; offsets table; `el-popconfirm` with "确定撤销此抵扣？"; "已撤销" danger tag; "有效" success tag; "暂无抵扣记录" empty state; `handleReverseOffset()` calls `reverseOffset()` and refreshes | PASS | Tab at line 183. Table lines 195-234. Popconfirm lines 220-230. Tags lines 214-215. Empty state lines 191-193. Handler lines 381-389 with `Promise.all([fetchBill(), fetchOffsets()])`. |
| 4 | `CaseReceiptsSummary.vue`: enriched info grid (fee_code, fee_type, year_no, invoice_no); "欠费" danger tag; "可提成" 是/否; `computed` import; `hasEnrichedFields` computed | PASS | Info grid lines 33-61. "欠费" tag line 54. 可提成 是/否 line 59. `computed` in import line 120. `hasEnrichedFields` lines 138-148. |
| 5 | Quality gates pass (lint + typecheck + build) | PASS | Confirmed by Frontend Agent in progress.md: lint PASS, typecheck PASS, build PASS (3.31s). |

---

## Code Quality Checks

| Check | Status | Notes |
|-------|--------|-------|
| No `@/` import aliases (relative imports only) | PASS | All imports use `../../../` relative paths. BillDetail.vue lines 256-263, CaseReceiptsSummary.vue lines 122-126. |
| No inline hex colors (CSS variables only) | PASS | All colors via `var(--text-sub)`, `var(--text-main)`, `var(--color-primary)`, `var(--color-success)`, `var(--color-warning)`, `var(--bg-card)`, `var(--border-light)`. Zero hex values in `<style>` blocks. |
| Only 4 allowlisted files modified | PASS | billing.types.ts, billing.ts, BillDetail.vue, CaseReceiptsSummary.vue — all new untracked files (`??` in git status). No other frontend files touched. |
| All UI labels in 简体中文 | PASS | BillDetail: 抵扣记录, 抵扣日期, 抵扣金额, 状态, 操作, 已撤销, 有效, 撤销, 确定撤销此抵扣？, 确定, 取消, 暂无抵扣记录, 抵扣已撤销. CaseReceiptsSummary: 累计开票, 累计回款, 未结清, 费用代码, 费用类型, 年度, 发票号, 欠费状态, 欠费, 正常, 可提成, 是/否, 账单, 该案件暂无账单, 暂无账务信息. |
| Element Plus components only | PASS | Used: el-table, el-table-column, el-tag, el-popconfirm, el-button, el-skeleton, el-tabs, el-tab-pane. No third-party or custom components beyond project standard. |
| `reverseOffset()` wired to real endpoint | PASS | billing.ts line 312: `http.post<BackendOffset>(`/offsets/${id}/reverse`)` → maps to backend `POST /api/v1/offsets/{offset_id}/reverse` (confirmed in api.py line 413). |
| Empty state for stub `getOffsets()` | PASS | getOffsets (billing.ts:286-298) returns `{ items: [], ... }`. BillDetail renders "暂无抵扣记录。" when `offsets.length === 0` (line 192). |
| `mapCaseReceipt()` field mapping correct | PASS | `receivable_amt → total_billed` (line 334), `received_amt → total_paid` (line 335), `totalBilled - totalPaid → total_outstanding` (line 340). Matches backend `CaseReceiptResponse` schema (schemas.py:100-114). |
| `el-popconfirm` Chinese button text | PASS | `confirm-button-text="确定"` and `cancel-button-text="取消"` (BillDetail.vue lines 223-224). |
| CSS uses design-token variables | PASS | `--text-sub`, `--text-main`, `--font-mono`, `--bg-card`, `--border-light`, `--color-success`, `--color-warning`, `--color-primary` — all confirmed in project CSS variable system. |
| No pre-existing code removed or broken | PASS | All 4 files are new creations (untracked in git). No modifications to existing tracked files. |

---

## Issues Found

**None** — no blocking issues.

---

## Observations (Non-Blocking)

1. **`reversed_at` will be undefined from API**: The backend `OffsetResponse` schema (schemas.py:89-97) does NOT include `reversed_at`, even though the ORM model has it (models.py:114). The frontend type and mapper are ready and forward-compatible, but the value will always be `undefined` until a backend schema update. Documented in architect plan as Risk 2.

2. **Offsets tab shows empty state only**: `getOffsets()` is a stub returning empty results because there is no `GET /offsets?bill_id=X` backend endpoint. The UI is fully wired — when backend adds the endpoint, only the stub body needs updating. Documented in architect plan as Risk 1.

3. **Inline Chinese labels vs labels.zh.ts**: New labels in BillDetail.vue (offsets section) and CaseReceiptsSummary.vue are hardcoded inline rather than added to `labels.zh.ts`. This matches the existing pattern in CaseReceiptsSummary.vue (which already uses inline Chinese for summary cards) and is acceptable since `labels.zh.ts` was not in the file allowlist. Existing BillDetail labels continue to use `ZH.billDetail.*` constants for pre-existing sections.

---

## Recommendations

1. **Backend follow-up**: Add `reversed_at` to `OffsetResponse` schema and create a `GET /offsets?bill_id=X` list endpoint to make the offsets tab functional.

2. **Future i18n**: Consider migrating inline Chinese labels to `labels.zh.ts` in a future batch for consistency with the label constant pattern used elsewhere in BillDetail.vue.
