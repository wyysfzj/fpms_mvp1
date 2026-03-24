# Summary

## Commands
- `./scripts/evidence_run.sh AD-FE-TERM-04 lint /bin/zsh -lc 'cd frontend && npm run lint'`
- `./scripts/evidence_run.sh AD-FE-TERM-04 test /bin/zsh -lc 'cd frontend && npm run typecheck'`
- `./scripts/evidence_run.sh AD-FE-TERM-04 build /bin/zsh -lc 'cd frontend && npm run build'`
- `./scripts/evidence_finalize.sh AD-FE-TERM-04`
- `./scripts/task_validate.sh AD-FE-TERM-04`

## Results
- 新增 `frontend/src/constants/terminology.ts`，冻结四组高频术语的 `UI 短标签 / 领域解释词 / UI 禁用词`
- `frontend/src/constants/labels.zh.ts` 中与案件对象、往来文件、账单与收款相关的关键标签统一改为引用术语词典
- 新增 `UI_BANNED_TERM_MAP`、`isBannedUiTerm()`、`getPreferredUiTerm()`，为后续页面整改提供命名守卫
- 前端质量门通过：`lint`、`typecheck`、`build` 均为 `0`

## Notes
- 本任务只在术语词典和标签常量层收敛命名，没有批量改其它页面
- reviewer / tester 并行审查结论：当前主链路 UI 中 `案卷 / 公文记录 / 官方文件 / 账务` 已无高风险残留；`DocTemplateList.vue` 的“中间文件费草稿”属于后续任务
