# REPORTS-CLOSE-03 Design

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `doc-only close audit after product evidence`
- `evidence_cost`: `low`

## chosen_runbook

- `P0-single-lane-story`

## Problem Statement

`#13 所有统计报表` 之前保持 `Partially Closed`，是因为 `RPT-CASE`、`RPT-FEE`、`RPT-ANN` 仍有 named residuals。当前这些 residual product slices 已全部落地，且最后的 `CASERPT-TREND-CARRIER-DB-01` + `CASERPT-TREND-01` 已关闭 case trend blocker。因此需要一次严格基于真实产品证据的 close audit，把 `#13` 从 `Partially Closed` 更新为 `Closed`。

## Scope

- 更新 `docs/FPMS_SPEC2_2nd_Review_REFRESH.md`
- 更新 `docs/priority-ranked-mitigation-ledger.md`
- 同步 refresh summary counts 与 `#13` ledger removal

## Explicit Non-scope

- 不做任何产品代码实现
- 不重审 `#15/#19`
- 不新增 residual story

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
