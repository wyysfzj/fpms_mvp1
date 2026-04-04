# CASERPT-TREND-PREREQ-01 Design

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `prerequisite freeze before implementation`
- `evidence_cost`: `low`

## chosen_runbook

- `P0-single-lane-story`

## Problem Statement

`RPT-CASE` 剩余的 `year/month trend` 统计目前不能诚实地直接进入实现。当前 `Case` carrier 只有 `filing_date` 和 `grant_date`，但缺少终止/无效/撤回/放弃等 terminal event 的独立日期字段。SPEC 2.0 要求的“按年度/月度统计新案/授权/终止数量趋势”如果直接用 `updated_at` 或当前 `status` 近似，会形成错误的报表语义。

## Scope

- 冻结 `RPT-CASE trend` 当前不能直接实现的 prerequisite 结论
- 明确缺失的事件日期 carrier
- 明确 trend story 现在应标记为 blocked by prerequisite
- 给出后续 prerequisite candidate

## Explicit Non-scope

- 不实现 trend report
- 不修改 schema / migration
- 不修改 `cases` 产品代码
- 不实现 grant-rate semantics

## Current Carrier Assessment

- Available:
  - `filing_date`
  - `grant_date`
  - current `status`
- Missing for honest trend reporting:
  - `terminated_date`
  - `invalidated_date`
  - `withdrawn_date`
  - `abandoned_date`
  - or an approved event ledger that can derive those dates deterministically

## Why This Is A Prerequisite

- “新案趋势”可以基于 `filing_date`
- “授权趋势”可以基于 `grant_date`
- “终止趋势”没有可靠事件日期
- 如果没有统一的 terminal-event date semantics，就无法诚实地输出：
  - 年度/月度终止数量趋势
  - 也无法稳定扩展到无效/撤回/放弃趋势

## Recommended Follow-up

- `CASERPT-TREND-CARRIER-01`
  - freeze one carrier strategy for terminal-event dates
- only after that:
  - `CASERPT-TREND-01`

## Design Conclusion

- `不可直接实现，必须先新增 prerequisite task(s)`
