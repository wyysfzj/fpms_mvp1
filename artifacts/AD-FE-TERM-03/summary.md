# AD-FE-TERM-03 Summary

## Task
- `tasks/afterdemon/AD-FE-TERM-03.md` as defined by `tasks/afterdemon/AFTERDEMO-TERM-ALIGNMENT_PLAN.md`

## Scope
- `frontend/src/constants/labels.zh.ts`
- `frontend/src/modules/cases/components/CaseReceiptsSummary.vue`

## Changes
- Changed the case-detail tab label from `账单` to `账单与收款` through the shared Chinese label table.
- Added a clear `收款摘要` section heading above the aggregate cards so the summary area matches the page purpose.
- Renamed the bills section to `相关账单` to distinguish bill objects from the receipt summary above.
- Replaced vague `账务` empty-state wording with `账单与收款信息`, and updated the no-bills message to reflect that only related bills are missing while the summary remains available.

## Verification
- `npm run lint` -> `0`
- `npm run typecheck` -> `0`
- `npm run build` -> `0`

## Runtime Expectation
- The touched case-detail tab no longer mixes `账单` and `账务` as competing labels.
- Users should now see a clearer distinction between bill objects and receipt/settlement summary in the current simplified case-finance view.
