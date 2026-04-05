# CASERPT-TREND-01 Design

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `shared summary contract on existing page`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Problem Statement

`#13 所有统计报表` 在 `RPT-CASE` 维度上，只剩 `year/month trend reporting` 未闭合。`CASERPT-TREND-CARRIER-DB-01` 已补齐 terminal-event date carrier，因此现在可以在现有 `GET /cases` summary 和现有 `CaseList.vue` 上实现真实趋势统计。

## Scope

- 后端在 `GET /cases` summary 中新增年/月趋势汇总
- 前端在现有 `CaseList.vue` 显示按年趋势和按月趋势
- 趋势指标固定为：
  - `new_case_count`
  - `granted_count`
  - `terminated_count`
  - `invalidated_count`
  - `withdrawn_count`
  - `abandoned_count`

## Explicit Non-scope

- 不做图表
- 不做导出
- 不新建 `CaseReport.vue`
- 不做 `#13` close update

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
