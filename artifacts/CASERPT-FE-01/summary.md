# CASERPT-FE-01

- 状态: PASS
- 闭环: 在 CaseList.vue 上完成第一轮案件统计报表前端闭环，补齐 country/agent/date 范围筛选、summary cards、状态/类型分布摘要，并保留现有明细列表作为报表明细。
- 非闭环: 未新增 CaseReport.vue，未实现图表、地图、复杂导出、多维透视分析或预测型分析。
- 说明: repo 当前 `npm run typecheck` 存在其他模块历史错误；本任务使用 scoped type evidence，确认 `cases.ts` / `cases.types.ts` / `CaseList.vue` 本身无新增类型错误。
- 验证:
  - `cd frontend && npm run lint -- src/api/cases.ts src/api/cases.types.ts src/modules/cases/pages/CaseList.vue` -> 0
  - `cd frontend && npm run typecheck > /tmp/caserpt_fe_typecheck.out 2>&1; if grep -E 'src/api/cases.ts|src/api/cases.types.ts|src/modules/cases/pages/CaseList.vue' /tmp/caserpt_fe_typecheck.out >/dev/null; then exit 1; fi` -> 0
