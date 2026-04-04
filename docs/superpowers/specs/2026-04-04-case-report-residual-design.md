# RPT-CASE Residual Design

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `residual decomposition after implemented first-round slice`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Problem Statement

`RPT-CASE` 当前不能再被诚实地描述为“未实现”。现有仓库已经具备第一轮案件统计报表产品切片：`GET /cases` 提供 report-style summary，`CaseList.vue` 提供筛选、summary cards、状态/类型分布摘要和明细列表。但对照 `FPMS SPEC 2.0` `9.4.1`，当前 family 仍缺少多个 full-spec 维度与指标，因此下一步不应重做已完成的 first-round 实现，而应先冻结 residual map。

## Assumptions

- `CASERPT-BE-01` / `CASERPT-FE-01` / `CASERPT-QA-01` 的 first-round closure 继续有效
- residual 目标不是推翻 first-round closure，而是定义：
  - 还缺哪些 spec semantics
  - 哪个 residual slice 应优先进入实现
- 关闭标准仍固定为：
  - 只有真实产品行为存在，才允许新增 residual capability 计入 closure

## Scope

- 对 `RPT-CASE` 做 strict residual capability map
- 明确 first-round already closed slice
- 明确仍未覆盖的 spec-level dimensions / metrics
- 推荐一个最小 residual implementation slice

## Explicit Non-scope

- 不重做 `CASERPT-BE-01`
- 不重做 `CASERPT-FE-01`
- 不做任何案件统计产品实现补丁
- 不做图表 / 导出 / 地图 / BI shell

## Current Implemented Slice

### Existing product evidence

- `frontend/src/modules/cases/pages/CaseList.vue`
- `backend/app/modules/cases/api.py`
- `backend/app/modules/cases/service.py`
- `backend/app/modules/cases/schemas.py`
- `artifacts/CASERPT-BE-01/**`
- `artifacts/CASERPT-FE-01/**`
- `artifacts/CASERPT-QA-01/**`

### Already closed under first-round interpretation

- approved report filters:
  - `client_id`
  - `status`
  - `case_type`
  - `patent_category`
  - `country`
  - `agent_id`
  - `date_range`
- summary cards:
  - total case count
  - status distribution count
  - case-type distribution count
- detail list retained as report detail portion

## Residual Spec Gap vs `FPMS SPEC 2.0`

### Spec-required examples not yet closed

- 按客户统计案件数量与类型分布
- 按国别统计案件数量
- 按代理人统计案件数量和授权率
- 按年度/月度统计新案 / 授权 / 终止数量趋势

### Residual dimensions not yet represented as summary output

- `Client` grouped statistics
- `Country` grouped statistics
- `PrimaryAgent / SecondAgent` grouped statistics
- `Year / Month` grouped trend buckets

### Residual metrics not yet represented as summary output

- 授权数量
- 授权率
- 终止/无效数量
- 正在审中数量
- 按时间趋势分组后的新案/授权/终止统计

## Residual Decomposition Recommendation

### Residual bucket A — grouped dimension summaries

- by client counts / type distribution
- by country counts
- by agent counts

### Residual bucket B — authorization metrics

- granted count
- grant rate
- terminated / invalidated counts
- in-prosecution counts

### Residual bucket C — time trend reporting

- year/month buckets
- new / granted / terminated trend rows

## Recommended First Residual Slice

- `CASERPT-AGGREGATE-01`
- exact closure candidate:
  - extend `GET /cases` summary with grouped `country_counts` and `agent_counts`
  - add FE presentation for those grouped summaries on `CaseList.vue`

### Why this is recommended first

- It builds on the existing report summary contract instead of inventing a second page
- It is narrower than authorization-rate and trend analytics
- It stays inside the current `cases` module ownership
- It avoids charting and export prerequisites

## Residuals Explicitly Deferred

- grant-rate computation semantics
- year/month trend reporting
- charts
- maps
- complex export
- BI shell / unified report center

## SQLite / Phase Compatibility Assessment

- This residual mapping story is doc-only and compatible
- The recommended first residual slice appears achievable without schema change
- If grant-rate semantics later require extra derived carrier logic, that must be assessed as a follow-up story, not absorbed here

## Risks / Blockers

- Treating filter coverage as equivalent to grouped statistical coverage
- Reopening already-closed first-round case report work
- Folding trend analytics and grant-rate semantics into the same next slice

## Exact Closure Slice Candidates

### Preferred

- `CASERPT-RESIDUAL-01`
  - freeze residual case-report map and first residual implementation recommendation

### Explicit non-closure

- no product implementation
- no re-close of first-round `CASERPT-*`
- no charts/export/trend implementation

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
- The atomic task should be a doc-only residual mapping story before any new case-report implementation slice.
