# Priority-Ranked Mitigation Ledger

This ledger is derived from [FPMS_SPEC2_2nd_Review_REFRESH.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/docs/FPMS_SPEC2_2nd_Review_REFRESH.md) and only covers items that are not currently `Closed`.

## 1. Mitigation Summary

Current non-`Closed` items: `5`

- `Still Missing`
  - `#5 多代理人提成分成`
- `Partially Closed`
  - `#8 中间文件 5 步向导`
  - `#15 授权费管理`
  - `#19 中间文件专项查询`
- `Blocked by Prerequisite`
  - `None`
- `Needs Reclassification`
  - `#13 所有统计报表`

## 2. Priority-ranked Mitigation Ledger

### `#5 多代理人提成分成`
- `Current Status`: `Still Missing`
- `Recommended Interpretation`: true structural gap, not a small rule patch
- `Why This Interpretation Is Correct`: current commission carrier remains single-agent centric
- `Exact Closure Slice`: multi-agent allocation carrier + ratio semantics
- `Explicit Non-closure`: no commission report redesign, no full settlement UX rewrite
- `Likely Ownership`: `prereq-heavy`
- `Prerequisite Needed?`: `Yes`
- `Suggested Story Shape`: `prereq-heavy`
- `Recommended Next Action`: `split prerequisite`

### `#8 中间文件 5 步向导`
- `Current Status`: `Partially Closed`
- `Recommended Interpretation`: wizard residual program, not one missing story
- `Why This Interpretation Is Correct`: wizard shell exists but full 5-step closure does not
- `Exact Closure Slice`: Step 3 deadline linkage first
- `Explicit Non-closure`: no dispatch/reporting/full-text
- `Likely Ownership`: `shared`
- `Prerequisite Needed?`: `Maybe`
- `Suggested Story Shape`: `multi-lane`
- `Recommended Next Action`: `replan`

### `#13 所有统计报表`
- `Current Status`: `Needs Reclassification`
- `Recommended Interpretation`: report-family residual program
- `Why This Interpretation Is Correct`: several report families already have first-round slices
- `Exact Closure Slice`: build residual report-family ledger first
- `Explicit Non-closure`: do not reopen already-closed report slices
- `Likely Ownership`: `shared`
- `Prerequisite Needed?`: `No`
- `Suggested Story Shape`: `multi-lane`
- `Recommended Next Action`: `replan`

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

### For `#5 多代理人提成分成`

#### Candidate 1
- `Story ID`: `COMMSPLIT-PRE-01`
- `Title`: 提成多代理分成 prerequisite
- `Exact Closure Slice`: freeze allocation carrier / ratio / settlement ownership semantics
- `Explicit Non-closure`: no report redesign
- `Likely Ownership`: `prereq-heavy`
- `Suggested Story Shape`: `prereq-heavy`
- `Recommended Next Action`: `write spec`

#### Candidate 2
- `Story ID`: `COMMSPLIT-BE-01`
- `Title`: 多代理提成计算最小后端闭环
- `Exact Closure Slice`: allocation logic after prerequisite
- `Explicit Non-closure`: no FE editor, no report work
- `Likely Ownership`: `backend`
- `Suggested Story Shape`: `single-lane`
- `Recommended Next Action`: `split prerequisite`

### For `#8 中间文件 5 步向导`

#### Candidate 1
- `Story ID`: `DOCWIZ-STEP3-SPEC-01`
- `Title`: 向导 Step 3 时限联动 residual spec
- `Exact Closure Slice`: freeze Step 3 deadline linkage contract
- `Explicit Non-closure`: no Step 4/5, no dispatch
- `Likely Ownership`: `shared`
- `Suggested Story Shape`: `multi-lane`
- `Recommended Next Action`: `write spec`

#### Candidate 2
- `Story ID`: `DOCWIZ-STEP4-SPEC-01`
- `Title`: 向导 Step 4 费用联动 residual spec
- `Exact Closure Slice`: freeze fee linkage semantics
- `Explicit Non-closure`: no dispatch/reporting
- `Likely Ownership`: `shared`
- `Suggested Story Shape`: `multi-lane`
- `Recommended Next Action`: `write spec`

### For `#13 所有统计报表`

#### Candidate 1
- `Story ID`: `REPORTS-LEDGER-01`
- `Title`: 报表 residual ledger 重分类
- `Exact Closure Slice`: enumerate report families and residuals
- `Explicit Non-closure`: no code changes, no report implementation
- `Likely Ownership`: `shared`
- `Suggested Story Shape`: `multi-lane`
- `Recommended Next Action`: `write spec`

#### Candidate 2
- `Story ID`: `CASERPT-RESIDUAL-01`
- `Title`: 案件统计报表 residual closure
- `Exact Closure Slice`: case statistics residual family
- `Explicit Non-closure`: do not touch annuity / commission / billing reports
- `Likely Ownership`: `shared`
- `Suggested Story Shape`: `multi-lane`
- `Recommended Next Action`: `implement after ledger`

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

1. `COMMSPLIT-PRE-01`
   - Only remaining clearly structural gap.
2. `REPORTS-LEDGER-01`
   - Reclassification must happen before any honest reports closure claims.
3. `DOCWIZ-STEP3-SPEC-01`
   - Wizard shell already exists, so residual-slice confusion risk is high.
4. `GF-RESIDUAL-SPEC-01`
   - Existing workflow should be clarified before any further implementation.
5. `DOCSEARCH-DOCTYPE-SPEC-01`
   - Small residual gap, but contract semantics are important.
