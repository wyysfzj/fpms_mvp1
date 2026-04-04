# Priority-Ranked Mitigation Ledger

This ledger is derived from [FPMS_SPEC2_2nd_Review_REFRESH.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/docs/FPMS_SPEC2_2nd_Review_REFRESH.md) and only covers items that are not currently `Closed`.

## 1. Mitigation Summary

Current non-`Closed` items: `3`

- `Still Missing`
  - `None`
- `Partially Closed`
  - `#13 所有统计报表`
  - `#15 授权费管理`
  - `#19 中间文件专项查询`
- `Blocked by Prerequisite`
  - `None`
- `Needs Reclassification`
  - `None`

## 2. Priority-ranked Mitigation Ledger

### `#13 所有统计报表`
- `Current Status`: `Partially Closed`
- `Recommended Interpretation`: multi-family reports residual program with named remaining family gaps
- `Why This Interpretation Is Correct`: strict report-family ledger already exists, and real residual product slices have landed for `RPT-CASE` / `RPT-FEE` / `RPT-ANN`, but named family residuals still remain
- `Exact Closure Slice`: preserve implemented report families and narrow follow-up work to the remaining family residuals only
- `Explicit Non-closure`: do not reopen already-implemented report slices; do not treat the whole reports program as `Closed`
- `Likely Ownership`: `shared`
- `Prerequisite Needed?`: `No`
- `Suggested Story Shape`: `multi-lane`
- `Recommended Next Action`: `write spec`

### `#15 授权费管理`
- `Current Status`: `Partially Closed`
- `Recommended Interpretation`: first-round workflow exists; residual workflow breadth remains
- `Why This Interpretation Is Correct`: carrier/worklist/state/draft-generation exist, but full lifecycle breadth is not proven closed
- `Exact Closure Slice`: residual workflow mapping after current post-draft state
- `Explicit Non-closure`: no carrier/state-machine rewrite
- `Likely Ownership`: `shared`
- `Prerequisite Needed?`: `No`
- `Suggested Story Shape`: `frontend-heavy`
- `Recommended Next Action`: `write spec`

### `#19 中间文件专项查询`
- `Current Status`: `Partially Closed`
- `Recommended Interpretation`: first-round query closed except `DocType` semantics
- `Why This Interpretation Is Correct`: current query covers multiple approved filters but not full spec parity
- `Exact Closure Slice`: explicit `DocType` carrier/filter decision
- `Explicit Non-closure`: no dispatch/reply/reporting/full-text
- `Likely Ownership`: `backend`
- `Prerequisite Needed?`: `Potentially`
- `Suggested Story Shape`: `single-lane`
- `Recommended Next Action`: `write spec`

## 3. Next-story Candidates

### For `#13 所有统计报表`

#### Candidate 1
- `Story ID`: `CASERPT-CLIENT-AGG-01`
- `Title`: 案件统计按客户聚合 residual
- `Exact Closure Slice`: add grouped client statistics to the existing case report summary and page
- `Explicit Non-closure`: do not touch fee/annuity reports; do not start trend reporting
- `Likely Ownership`: `shared`
- `Suggested Story Shape`: `frontend-heavy`
- `Recommended Next Action`: `write spec`

#### Candidate 2
- `Story ID`: `CASERPT-TREND-CARRIER-01`
- `Title`: 案件趋势统计 terminal-event carrier prerequisite
- `Exact Closure Slice`: freeze one carrier strategy for terminal-event dates before case trend reporting
- `Explicit Non-closure`: do not implement trend UI/API; do not touch fee/annuity reports
- `Likely Ownership`: `backend`
- `Suggested Story Shape`: `single-lane`
- `Recommended Next Action`: `write spec`

### For `#15 授权费管理`

#### Candidate 1
- `Story ID`: `GF-RESIDUAL-SPEC-01`
- `Title`: 授权费管理 residual workflow spec
- `Exact Closure Slice`: define closed vs residual workflow map
- `Explicit Non-closure`: no prerequisite rewrite
- `Likely Ownership`: `shared`
- `Suggested Story Shape`: `frontend-heavy`
- `Recommended Next Action`: `write spec`

#### Candidate 2
- `Story ID`: `GF-POSTDRAFT-01`
- `Title`: 授权费 post-draft residual transition
- `Exact Closure Slice`: one post-draft workflow rule
- `Explicit Non-closure`: do not touch carrier/worklist
- `Likely Ownership`: `backend`
- `Suggested Story Shape`: `single-lane`
- `Recommended Next Action`: `implement after spec`

### For `#19 中间文件专项查询`

#### Candidate 1
- `Story ID`: `DOCSEARCH-DOCTYPE-SPEC-01`
- `Title`: 中间文件专项查询 `DocType` residual spec
- `Exact Closure Slice`: decide whether `DocType` needs independent carrier/filter
- `Explicit Non-closure`: no dispatch/reply/reporting/full-text
- `Likely Ownership`: `backend`
- `Suggested Story Shape`: `single-lane`
- `Recommended Next Action`: `write spec`

#### Candidate 2
- `Story ID`: `DOCSEARCH-DOCTYPE-PRE-01`
- `Title`: `DocType` carrier prerequisite
- `Exact Closure Slice`: one carrier / mapping prerequisite
- `Explicit Non-closure`: do not add FE page/reporting
- `Likely Ownership`: `prereq-heavy`
- `Suggested Story Shape`: `prereq-heavy`
- `Recommended Next Action`: `split prerequisite if needed`

## 4. Recommended Priority Queue

1. `REPORTS-LEDGER-01`
   - Completed; use it as authority, do not reopen it as product work.
2. `GF-RESIDUAL-SPEC-01`
   - Existing workflow should be clarified before any further implementation.
3. `DOCSEARCH-DOCTYPE-SPEC-01`
   - Small residual gap, but contract semantics are important.
4. `CASERPT-CLIENT-AGG-01`
   - Remaining `#13` residuals should now stay inside named family slices only.
