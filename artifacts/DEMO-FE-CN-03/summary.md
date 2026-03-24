# DEMO-FE-CN-03 Summary

## Task
- `tasks/dmmo/DEMO-FE-CN-03.md` as defined by `tasks/dmmo/DEMO_CN_UI.md`

## Scope
- `frontend/src/modules/system/pages/DocTemplateList.vue`
- `frontend/src/modules/consulting/pages/ConsultingFeeDraftCreate.vue`
- `frontend/src/modules/consulting/pages/ConsultingCaseCreate.vue`

## Changes
- Removed mixed Chinese-English visible labels and placeholders from the document template page.
- Replaced raw English examples such as `PUBLISHED`, `SUB_EXAM`, `REG_FEE`, and `IN/OUT` from visible form copy.
- Added Chinese display rendering for document-template status effects and common fee draft types in list view.
- Normalized consulting fee-draft page labels such as `案件 ID`, `草单 ID`, and `费用项 ID` to Chinese wording.
- Replaced visible mode labels `FIXED/HOURLY/HYBRID` with Chinese labels while preserving submitted enum values.
- Added Chinese display helpers for consulting draft result fields such as draft type, mode, fee type, and currency.
- Normalized consulting case-create page labels such as `客户 ID` / `负责人 ID`, and changed created-case status display to shared Chinese case-status text.

## Verification
- `npm run lint` -> `0`
- `npm run typecheck` -> `0`
- `npm run build` -> `0`

## Runtime Expectation
- The touched system and consulting pages no longer expose obvious mixed Chinese-English UI text in the areas covered by this task.
- Technical enum values remain in code and payloads, but no longer dominate visible labels in the touched UI.
