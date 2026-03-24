# AD-FE-TERM-02 Summary

## Task
- `tasks/afterdemon/AD-FE-TERM-02.md` as defined by `tasks/afterdemon/AFTERDEMO-TERM-ALIGNMENT_PLAN.md`

## Scope
- `frontend/src/constants/labels.zh.ts`
- `frontend/src/modules/cases/components/CaseDocumentsTab.vue`
- `frontend/src/modules/documents/pages/DocumentCreate.vue`
- `frontend/src/modules/documents/pages/DocumentList.vue`

## Changes
- Changed the case-detail tab label from `官方文件` to `往来文件` through the shared Chinese label table.
- Updated the case-detail panel copy from `公文记录` / `登记公文` to `往来文件记录` / `登记往来文件`.
- Updated document create flow copy to align case-detail entry messaging with `往来文件` terminology, including page title, form section title, case-context error messages, and success toast.
- Updated the list page title and empty-state CTA from generic `文档` wording to `往来文件` wording for this user-facing workflow.
- Updated shared route/detail labels in the Chinese string table so shell-level titles and breadcrumbs do not fall back to `文档` wording in the same workflow.

## Verification
- `npm run lint` -> `0`
- `npm run typecheck` -> `0`
- `npm run build` -> `0`

## Runtime Expectation
- The case-detail workflow no longer mixes `官方文件` / `公文记录` / `文档` as competing user-facing labels in the touched scope.
- Users should now see a consistent Simplified Chinese term chain centered on `往来文件`.
