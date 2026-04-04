# P2 #13 所有统计报表 Product Close Audit Design

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `doc-only close audit after residual implementation waves`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Problem Statement

`#13 所有统计报表` 在 refresh review 与 mitigation ledger 中仍停留在 `Needs Reclassification`，但这个结论已经落后于当前真实产品实现。现在仓库里不仅有 strict report-family ledger，还已经落成了 `RPT-CASE`、`RPT-FEE`、`RPT-ANN` 的多条 residual implementation waves，因此需要进行一次严格按产品证据的 close-audit refresh，把 `#13` 从 framing-only 状态更新为真实的 `Partially Closed`，同时保留仍未完成的 named family residuals。

## Assumptions

- 权威对象固定为：
  - `#13 product close-audit refresh`
- 关闭标准固定为：
  - real FE page / API / user path only
  - doc/spec/plan/contract do not count as product closure
- 当前已确认的 implemented report-family slices继续有效：
  - `RPT-PREPAY`
  - `RPT-BILL`
  - `RPT-COM`
- 当前已确认的 residual implementation waves继续有效：
  - `RPT-CASE`
    - `country_counts`
    - `agent_counts`
    - grant-rate metrics
  - `RPT-FEE`
    - grouped amount summaries
    - agent-attributed service income
    - billed / received / unpaid summaries
  - `RPT-ANN`
    - grouped amount summaries
    - success-rate metrics
- 当前仍未关闭的 named residuals 需要继续保留：
  - `RPT-CASE`
    - grouped `client` statistics
    - trend reporting prerequisite
  - `RPT-FEE`
    - time trend reporting
  - `RPT-ANN`
    - payment-status truth semantics beyond current amount/success slices

## Scope

- 更新 `FPMS_SPEC2_2nd_Review_REFRESH.md` 中 `#13` 的状态与说明
- 更新 `priority-ranked-mitigation-ledger.md` 中 `#13` 的状态、解释与 next-story candidates
- 更新 top-level counts 和 summary wording

## Explicit Non-scope

- 不关闭 `#13`
- 不重审 `#15/#19`
- 不新增任何产品实现补丁
- 不新开 residual spec / implementation story

## Current Product Evidence

- report-family ledger:
  - [2026-04-04-reports-implementation-ledger-design.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/docs/superpowers/specs/2026-04-04-reports-implementation-ledger-design.md)
- case residual implementation:
  - [2026-04-04-case-report-aggregate-design.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/docs/superpowers/specs/2026-04-04-case-report-aggregate-design.md)
  - [2026-04-04-case-report-grant-rate-implementation-design.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/docs/superpowers/specs/2026-04-04-case-report-grant-rate-implementation-design.md)
  - [2026-04-04-case-report-trend-prerequisite-design.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/docs/superpowers/specs/2026-04-04-case-report-trend-prerequisite-design.md)
- fee residual implementation:
  - [2026-04-04-fee-report-aggregate-design.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/docs/superpowers/specs/2026-04-04-fee-report-aggregate-design.md)
  - [2026-04-04-fee-report-agent-income-implementation-design.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/docs/superpowers/specs/2026-04-04-fee-report-agent-income-implementation-design.md)
  - [2026-04-05-fee-report-balance-implementation-design.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/docs/superpowers/specs/2026-04-05-fee-report-balance-implementation-design.md)
- annuity residual implementation:
  - [2026-04-05-annuity-report-amount-implementation-design.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/docs/superpowers/specs/2026-04-05-annuity-report-amount-implementation-design.md)
  - [2026-04-05-annuity-report-success-implementation-design.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/docs/superpowers/specs/2026-04-05-annuity-report-success-implementation-design.md)

## Required Refresh Updates

- Update `#13` from `Needs Reclassification` to `Partially Closed`
- Move `#13` into the mitigation ledger’s `Partially Closed` section
- Set `Needs Reclassification = 0`
- Keep `#13` in mitigation ledger with narrowed residual-family wording
- Do not remove `#13` from the ledger, because named residuals still remain

## Risks / Blockers

- Main risk: over-correcting from `Needs Reclassification` straight to `Closed`
- Main risk: forgetting that `RPT-CASE` still has `client` grouped statistics and trend residuals
- Main risk: treating `RPT-FEE` trend or `RPT-ANN` payment-truth semantics as already closed without explicit product evidence

## Exact Closure Slice Candidates

- `REPORTS-CLOSE-02`
  - refresh `#13` from `Needs Reclassification` to `Partially Closed`
- `REPORTS-QA-CLOSE-02`
  - evidence audit for the close-refresh wave

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
