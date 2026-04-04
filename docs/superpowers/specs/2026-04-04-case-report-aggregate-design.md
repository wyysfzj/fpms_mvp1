# CASERPT-AGGREGATE-01 Design

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `chained (BE -> FE)`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Problem Statement

`RPT-CASE` 的 first-round 案件统计报表已经存在，但相对 `FPMS SPEC 2.0 9.4.1` 仍缺少 grouped dimensions。`CASERPT-AGGREGATE-01` 只关闭其中一个最小 residual slice：在现有 `GET /cases` summary 上新增 `country_counts` 和 `agent_counts`，并在 `CaseList.vue` 中展示这两组聚合摘要。

## Assumptions

- 当前页面继续使用：
  - `frontend/src/modules/cases/pages/CaseList.vue`
- 当前接口继续使用：
  - `GET /cases`
- 本轮 grouped summary 语义固定为：
  - `country_counts`
    - 取 `to_country` 优先，其次 `from_country`
    - 为空时记为 `未填写`
  - `agent_counts`
    - 合并 `primary_agent_id` 与 `second_agent_id`
    - 同一案件中若两个字段相同，只计一次
    - 为空时不计入 agent bucket
- 当前只做案件数量统计，不做：
  - 授权率
  - 趋势
  - 图表

## Scope

- Backend:
  - 扩展 `CaseReportSummaryResponse`
  - 为 `GET /cases` 生成 `country_counts` 与 `agent_counts`
- Frontend:
  - 扩展 cases API types
  - 在 `CaseList.vue` 渲染国别统计与代理人统计卡片

## Explicit Non-scope

- grant rate
- year/month trends
- client grouped summary
- charts / export / maps
- new page or reports shell

## Atomic Closure Slices

- `CASERPT-AGG-BE-01`
  - extend case report summary contract with `country_counts` and `agent_counts`
- `CASERPT-AGG-FE-01`
  - render grouped country/agent summary cards on `CaseList.vue`
- `CASERPT-AGG-QA-01`
  - evidence audit and close summary

## Shared-file Decisions

- Serialized backend ownership:
  - `backend/app/modules/cases/api.py`
  - `backend/app/modules/cases/service.py`
  - `backend/app/modules/cases/schemas.py`
  - `backend/tests/test_case_report.py`
- Serialized frontend ownership:
  - `frontend/src/api/cases.ts`
  - `frontend/src/api/cases.types.ts`
  - `frontend/src/modules/cases/pages/CaseList.vue`

## SQLite / Phase Compatibility

- No schema or migration change
- Module-local API/service enhancement only
- SQLite compatible

## Risks

- Counting the same case twice in `agent_counts`
- Country semantics drifting from existing filter semantics
- Accidentally absorbing grant-rate or trend semantics into this slice

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
