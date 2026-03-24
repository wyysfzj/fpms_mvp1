# FC2 Batch — Review Report

**Reviewer**: Team Lead (fallback — reviewer agent stalled)
**Date**: 2026-02-27
**Verdict**: **PASS** (15/15 AC met)

---

## Acceptance Criteria Checklist

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| AC1 | `Document` type includes `reply_to_id`, `need_reply`, `reply_date` | PASS | `documents.types.ts:18-20` — all 3 fields present |
| AC2 | `DocumentCreatePayload` includes `reply_to_id` | PASS | `documents.types.ts:38` — `reply_to_id?: string \| null` |
| AC3 | `DocumentUpdatePayload` includes `reply_to_id`, `need_reply`, `reply_date` | PASS | `documents.types.ts:49-51` — all 3 fields present |
| AC4 | `BackendDocument` includes reply chain fields + `case_no` | PASS | `documents.ts:35-38` — `reply_to_id`, `need_reply`, `reply_date`, `case_no` |
| AC5 | `mapDocument()` forwards all reply chain fields + `case_no` | PASS | `documents.ts:63-66` — all 4 fields forwarded with correct null handling |
| AC6 | `toCreatePayload()` includes `reply_to_id` | PASS | `documents.ts:80` — `reply_to_id: data.reply_to_id \|\| null` |
| AC7 | `toUpdatePayload()` includes `reply_to_id`, `need_reply`, `reply_date` | PASS | `documents.ts:94-96` — all 3 with undefined-guard pattern |
| AC8 | DocumentCreate has doc_template_id el-select | PASS | `DocumentCreate.vue:66-80` — filterable, clearable, fetches from getDocTemplates |
| AC9 | DocumentCreate has reply_to_id el-select | PASS | `DocumentCreate.vue:88-102` — disabled when no case_id, loads via watch |
| AC10 | Template select auto-updates direction | PASS | `DocumentCreate.vue:183-193` — `onTemplateChange()` sets `form.direction = tmpl.direction` |
| AC11 | DocumentCreate shows need_reply indicator when template selected | PASS | `DocumentCreate.vue:81-83` — warning tag "需要回复" shown when `selectedTemplate?.need_reply` |
| AC12 | DocumentDetail shows reply chain link when `reply_to_id` set | PASS | `DocumentDetail.vue:102-109` — router-link "查看原文档 →" to `/documents/{reply_to_id}` |
| AC13 | DocumentDetail shows need_reply / reply_date status | PASS | `DocumentDetail.vue:94-101` — 待回复 (warning), 已于 {date} 回复 (success), 否 |
| AC14 | DocumentList shows 回复状态 column with tags | PASS | `DocumentList.vue:80-90` — 待回复 (warning), 已回复 (success), dash |
| AC15 | Quality Gate passes (lint + typecheck + build) | PASS | All 3 passed after duplicate `case_no` fix |

---

## Files Modified (5)

| File | Lines | Change Summary |
|------|-------|---------------|
| `src/api/documents.types.ts` | 118 | Added reply chain fields to Document, CreatePayload, UpdatePayload |
| `src/api/documents.ts` | 210 | Added 4 fields to BackendDocument, forwarded in mapDocument/toCreate/toUpdate |
| `src/modules/documents/pages/DocumentCreate.vue` | 310 | Template selector + reply_to selector + onTemplateChange + watch(case_id) |
| `src/modules/documents/pages/DocumentDetail.vue` | 245 | Need_reply status tags + reply_to_id router-link in side panel |
| `src/modules/documents/pages/DocumentList.vue` | 193 | 回复状态 column with conditional el-tag |

---

## Scope Deviations

| # | Deviation | Justification | Impact |
|---|-----------|---------------|--------|
| SD1 | Added `documents.ts` as file #5 (not in original allowlist) | `BackendDocument` and `mapDocument()` silently drop all reply chain fields — FC2 impossible without this fix | **BLOCKER resolved** — same pattern as FB3 cases.ts |

---

## Bugs Found & Fixed

| # | Bug | Fix |
|---|-----|-----|
| B1 | Duplicate `case_no` in `Document` interface (line 10 and 21) | Removed duplicate at line 21, kept original at line 10 |
| B2 | Pre-existing: `case_no` returned by backend but dropped by `mapDocument()` | Fixed as part of T0 — added to BackendDocument and mapDocument |

---

## Code Quality Notes

- All imports use relative paths (no `@/` alias) — consistent
- Chinese labels inline (consistent with existing DocumentCreate pattern, labels.zh.ts not in allowlist)
- Template selector uses `filteredTemplates` computed property for direction filtering
- Reply_to selector correctly disables when no case_id and shows hint text
- DocumentDetail reply chain display uses simple router-link approach (no extra API call for title)
- toUpdatePayload uses undefined-guard pattern consistent with existing fields

---

## Conclusion

FC2 batch **PASSED** all acceptance criteria. The scope deviation for `documents.ts` was necessary and correctly executed. One implementation bug (duplicate case_no) was caught at Quality Gate and fixed before final verification.
