# CASERPT-TREND-CARRIER-01 Design

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `prerequisite freeze before implementation`
- `evidence_cost`: `low`

## chosen_runbook

- `P0-single-lane-story`

## Problem Statement

`#13 所有统计报表` 在 `RPT-CASE` 维度上，当前只剩 `year/month trend reporting` 未闭合。现有仓库已经具备：

- `filing_date` -> 可支撑“新案趋势”
- `grant_date` -> 可支撑“授权趋势”

但仍缺少终止/无效/撤回/放弃等 terminal-event 的独立日期 carrier。若继续直接实现 `CASERPT-TREND-01`，就只能：

- 用当前 `status` 近似历史事件
- 或用 `updated_at` 冒充终止日期

这两种都不符合 `SPEC 2.0 9.4.1` 的真实统计语义。

## Scope

- 冻结 `RPT-CASE trend` 当前唯一剩余 blocker
- 明确 terminal-event trend 需要独立 carrier strategy
- 明确 `CASERPT-TREND-01` 在当前阶段仍不可直接执行
- 给出后续 prerequisite 方向

## Explicit Non-scope

- 不实现 trend API/UI
- 不新增 schema / migration
- 不修改 `backend/app/modules/cases/*` 产品逻辑
- 不修改 `frontend/src/modules/cases/*`
- 不更新 `#13` close decision

## Carrier Judgment

### Available carriers

- `Case.filing_date`
- `Case.grant_date`
- current `Case.status`

### Missing carriers for honest terminal-event trend reporting

- `terminated_date`
- `invalidated_date`
- `withdrawn_date`
- `abandoned_date`
- or one approved event ledger that can deterministically derive those dates

## Frozen Conclusion

- `新案趋势` 可在现有 carrier 下成立
- `授权趋势` 可在现有 carrier 下成立
- `终止/无效/撤回/放弃趋势` 在现有 carrier 下不能诚实实现
- 因而 full `CASERPT-TREND-01` 仍必须维持 `blocked by prerequisite`

## Recommended Follow-up

- `CASERPT-TREND-CARRIER-DB-01`
  - decide one persistent carrier strategy for terminal-event dates
- only after that:
  - `CASERPT-TREND-01`

## Design Conclusion

- `不可直接实现，必须先新增 prerequisite task(s)`
