# P2 #13 所有统计报表 Strict Report-family Implementation Ledger Design

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `family ledger before implementation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

`P2 #13 所有统计报表` 不能再沿用 old review 的 `single missing feature` framing。当前仓库已经存在多个真实报表 family 的产品切片，但各 family 的完成度不一致；如果不先建立一份严格的 report-family implementation ledger，后续很容易再次把 representative slice、partial query page 或 doc-only planning 误判成 full-family closure。

## Assumptions

- 权威对象固定为：
  - `#13 strict report-family implementation ledger`
- 关闭标准固定为：
  - 只有真实页面/API/用户路径存在，family 才能计入 `Implemented`
- doc/spec/plan/contract 不得单独支撑：
  - `Implemented`
  - `Closed`
- representative family 不得外推出整个 `#13` 已闭合
- 第一轮结果形态固定为：
  - `strict report-family ledger`
  - `family decomposition / reclassification`
- 第一轮不自动包含：
  - export
  - print
  - chart
  - drill-down
  - cross-report shell

## Scope

- 对 `#13` 做 strict report-family inventory
- 标记各 family 为：
  - `Implemented`
  - `Partially Implemented`
  - `Contract/Plan Only`
  - `Missing`
- 冻结 `#13` 的 family 边界和 non-closure
- 给出后续 implementation family priority 建议

## Explicit Non-scope

- 任何报表 family 的产品实现补丁
- 任何 review close update
- 任何 export / print / chart / analytics 实现
- document search / dispatch / wizard / envelope 等非本条核心 closure

## Exact Current Report-family Inventory

### `RPT-PREPAY`

- Current product evidence:
  - `frontend/src/modules/billing/pages/PaymentList.vue`
  - `backend/app/modules/billing/api.py`
- Observed capability:
  - 页面标题为 `预收款管理报表`
  - 有筛选、summary cards、列表、分页
- Current classification:
  - `Implemented`

### `RPT-BILL`

- Current product evidence:
  - `frontend/src/modules/billing/pages/BillList.vue`
  - `backend/app/modules/billing/api.py`
- Observed capability:
  - 应收 / 逾期 / 坏账 / 账龄 summary
  - 筛选、明细列表
- Current classification:
  - `Implemented`

### `RPT-COM`

- Current product evidence:
  - `frontend/src/modules/commission/pages/CommissionSettlement.vue`
  - `backend/app/modules/commission/api.py`
- Observed capability:
  - `GET /commission/reports/settlement`
  - 结算报表与统计
  - 按代理人统计、按案件统计、明细列表
- Current classification:
  - `Implemented`

### `RPT-CASE`

- Current product evidence:
  - `frontend/src/modules/cases/pages/CaseList.vue`
  - `backend/app/modules/cases/api.py`
- Observed capability:
  - 案件数量、状态、类型 summary
  - 筛选、分布卡片、列表
- Residual concern:
  - 更像 representative case statistics slice，尚未证明 full family parity
- Current classification:
  - `Partially Implemented`

### `RPT-FEE`

- Current product evidence:
  - `frontend/src/modules/billing/pages/FeeUnifiedQuery.vue`
  - `frontend/src/modules/expenses/pages/ExpenseList.vue`
  - billing / fees / expenses backend carriers
- Observed capability:
  - 统一费用查询
  - 支出统计卡片和列表
- Residual concern:
  - 费用 / 收入 family 仍缺完整统计口径收敛
- Current classification:
  - `Partially Implemented`

### `RPT-ANN`

- Current product evidence:
  - `frontend/src/modules/annuity/pages/AnnuityTaskList.vue`
  - `backend/app/modules/annuity/api.py`
- Observed capability:
  - 年费任务筛选
  - 状态/年度 summary
  - 明细列表
- Residual concern:
  - 更像年费任务统计 / worklist slice，尚未证明 full annuity report parity
- Current classification:
  - `Partially Implemented`

## Family Boundary Freeze

### Included in `#13`

- `RPT-PREPAY`
- `RPT-BILL`
- `RPT-CASE`
- `RPT-FEE`
- `RPT-ANN`
- `RPT-COM`

### Explicit non-closure / deferred from `#13` first-round ledger

- document search
- dispatch / envelope
- document wizard
- pure workbench pages that do not satisfy report semantics
- export / print / chart / drill-down / BI shell
- cross-report unified shell

## Product-closure Standard

### `Implemented`

- A real FE page and/or user path exists
- The supporting backend/API contract exists
- The page expresses report semantics, not only raw CRUD/workbench behavior

### `Partially Implemented`

- A real product slice exists
- But the family is still only representative / partial relative to spec semantics

### `Contract/Plan Only`

- Only doc/spec/plan/task evidence exists
- No sufficient product behavior is reachable

### `Missing`

- No sufficient product behavior exists
- No usable family slice can be honestly credited

## Residual Family Ledger

### Residual family candidates

- `RPT-CASE`
  - residual case-statistics parity
- `RPT-FEE`
  - residual fee / income report parity
- `RPT-ANN`
  - residual annuity-report parity

### Already implemented families to preserve, not reopen by default

- `RPT-PREPAY`
- `RPT-BILL`
- `RPT-COM`

## Shared-file / Ownership Analysis

### Current ledger story

- doc-only shared ownership:
  - `docs/superpowers/specs/2026-04-04-reports-implementation-ledger-design.md`
  - `docs/superpowers/plans/2026-04-04-reports-implementation-ledger.md`
  - `tasks/postenhancement/backend/REPORTS-LEDGER-01.md`
  - `tasks/postenhancement/backend/REPORTS-QA-LEDGER-01.md`

### Future shared ownership hotspots

- `frontend/src/api/cases.ts`
- `frontend/src/api/cases.types.ts`
- `frontend/src/api/billing.ts`
- `frontend/src/api/billing.types.ts`
- `frontend/src/api/annuity.ts`
- `frontend/src/api/annuity.types.ts`
- module-level report pages under:
  - `frontend/src/modules/cases/pages/**`
  - `frontend/src/modules/billing/pages/**`
  - `frontend/src/modules/annuity/pages/**`
- backend query carriers:
  - `backend/app/modules/cases/api.py|service.py|schemas.py`
  - `backend/app/modules/billing/api.py|service.py|schemas.py`
  - `backend/app/modules/annuity/api.py|service.py|schemas.py`

## API / Service Impact

- This ledger story makes no API change
- Subsequent implementation stories should prefer module-local query enhancement
- No unified `reports` backend module should be introduced by default

## UI / Export / Print Impact

- This ledger story makes no UI change
- Export / print / chart are explicitly deferred
- Presence of a table or export button must not be treated as family closure by itself

## Cross-module Impact

- The program spans:
  - `billing`
  - `commission`
  - `cases`
  - `annuity`
  - `fees`
  - `expenses`
- It does not automatically absorb:
  - `documents`
  - `dispatch`
  - `search`
  - `wizard`

## SQLite / Phase Compatibility Assessment

- Compatible because this story is doc-only ledger work
- No schema / migration change is needed
- Subsequent family implementation stories must re-evaluate phase and ownership constraints independently

## Risks / Blockers / Prerequisite Tasks

- Main risk: treating representative slices as full family closure
- Main risk: treating old reports decomposition docs as closure authority
- Main risk: mixing export / print / chart / analytics into first-round closure
- Current prerequisite judgment:
  - No schema prerequisite is required for the ledger story itself

## Exact Closure Slice Candidates

### Preferred slice

- `REPORTS-LEDGER-01`
  - strict report-family implementation ledger and reclassification for `#13`

### Explicit non-closure

- no product implementation
- no close decision update
- no export / print / chart work
- no non-report module work

## First Recommended Implementation Family After Ledger

- `RPT-CASE`
  - reason:
    - existing `CaseList.vue` and `GET /cases` already form a reachable report slice
    - residual gap is narrower than a full fee or annuity family rewrite
    - shared ownership can stay mostly within the `cases` module

## Design Conclusion

- `受 shared-ownership / family decomposition 约束，当前应先做 ledger/reclassification`
- The atomic task is a doc-only strict report-family implementation ledger for `#13`.
