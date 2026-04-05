# P2 #15 授权费管理 Strict Workflow Implementation Ledger Design

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `workflow ledger before implementation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

`P2 #15 授权费管理` 不能再沿用 old review 的 `single missing feature` framing。当前仓库已经存在真实的授权费 carrier、state machine、worklist、draft generation、post-draft completion、bill visibility 和 notice carrier visibility；但这些 slice 仍不足以证明 `#15` 已按 `FPMS SPEC 2.0` 完整闭合。如果不先建立一份严格的 grant-fee workflow implementation ledger，后续很容易再次把 representative slice、只读 visibility 或 doc-only freeze 误判成 full workflow closure。

## Assumptions

- 权威对象固定为：
  - `#15 strict grant-fee workflow implementation ledger`
- 关闭标准固定为：
  - 只有真实页面/API/用户路径存在，workflow slice 才能计入 `Implemented`
- doc/spec/plan/contract 不得单独支撑：
  - `Implemented`
  - `Closed`
- 只读 visibility 不得外推出整个 `#15` 已闭合
- 第一轮结果形态固定为：
  - `strict workflow ledger`
  - `workflow decomposition / reclassification`
- 第一轮不自动包含：
  - bill generation
  - 真实授权费通知函生成
  - 真实 reminder/task generation
  - detail/edit page
  - batch actions
  - receipt/payment/settlement 深水区语义

## Scope

- 对 `#15` 做 strict workflow inventory
- 标记各 workflow slice 为：
  - `Implemented`
  - `Partially Implemented`
  - `Contract/Plan Only`
  - `Missing`
- 冻结 `#15` 的 workflow 边界与 non-closure
- 给出后续 implementation slice priority 建议

## Explicit Non-scope

- 任何 grant-fee 产品实现补丁
- 任何 review close update
- bill generation
- 真实 `GRANT_FEE_NOTICE` 文书生成与存档
- 真实 reminder/task generation
- detail/edit page
- batch actions
- receipt/payment/settlement 深水区语义

## Exact Current Workflow Inventory

### `GF-CARRIER`

- Current product evidence:
  - `backend/app/modules/fees/models.py`
  - `backend/tests/test_grant_fee_prereq_schema.py`
- Observed capability:
  - `T_GrantFeeTask` minimal carrier 已存在
  - SQLite-safe schema / migration path 已有测试
- Current classification:
  - `Implemented`

### `GF-STATE`

- Current product evidence:
  - `backend/app/modules/grant_fees/api.py`
  - `backend/app/modules/grant_fees/service.py`
  - `backend/tests/test_grant_fee_state_machine_api.py`
- Observed capability:
  - `GET /grant-fee-tasks/{task_id}/state`
  - `PUT /grant-fee-tasks/{task_id}/state`
  - 真实状态机：
    - `OPEN`
    - `WAITING_CLIENT`
    - `READY_TO_DRAFT`
    - `DRAFT_GENERATED`
    - `DONE`
- Current classification:
  - `Implemented`

### `GF-WORKLIST`

- Current product evidence:
  - `backend/app/modules/grant_fees/api.py`
  - `backend/app/modules/grant_fees/service.py`
  - `backend/tests/test_grant_fee_worklist_api.py`
  - `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`
- Observed capability:
  - `GET /grant-fee-tasks/list`
  - 筛选、分页、状态/草单/通知/账单列
  - grant-fee 真实用户路径 `/grant-fee/tasks`
- Current classification:
  - `Implemented`

### `GF-DRAFT`

- Current product evidence:
  - `backend/app/modules/grant_fees/api.py`
  - `backend/app/modules/grant_fees/service.py`
  - `backend/tests/test_grant_fee_draft_linkage_api.py`
  - `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`
- Observed capability:
  - `POST /grant-fee-tasks/{task_id}/generate-draft`
  - 为单行任务生成真实 `FeeDraft(Type=GRANT_FEE)` 与 `FeeItem`
  - 已有 idempotent reuse 语义
- Residual concern:
  - 仍不是 SPEC 里的 full fee-rate-driven parity
- Current classification:
  - `Implemented`

### `GF-POSTDRAFT`

- Current product evidence:
  - `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`
  - `frontend/src/api/grantFees.ts`
  - `backend/app/modules/grant_fees/api.py`
- Observed capability:
  - 对 `DRAFT_GENERATED` 行提供真实 `标记完成`
  - 完成后刷新 worklist，状态可进入 `DONE`
- Current classification:
  - `Implemented`

### `GF-BILL-VIS`

- Current product evidence:
  - `backend/app/modules/grant_fees/schemas.py`
  - `backend/app/modules/grant_fees/service.py`
  - `backend/tests/test_grant_fee_worklist_api.py`
  - `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`
- Observed capability:
  - worklist payload 投影：
    - `billed`
    - `linked_bill_id`
    - `linked_bill_no`
  - 页面显示只读账单列并可跳到 `/billing/bills/:id`
- Residual concern:
  - 仅是 linkage visibility，不是 bill generation / settlement workflow
- Current classification:
  - `Partially Implemented`

### `GF-DOC-VIS`

- Current product evidence:
  - `backend/app/modules/grant_fees/schemas.py`
  - `backend/app/modules/grant_fees/service.py`
  - `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`
- Observed capability:
  - `notify_count`
  - `notice_sent`
  - 页面明确展示内部通知 carrier
- Residual concern:
  - 不等价于真实 `Document` 或 reminder `Task` existence
- Current classification:
  - `Partially Implemented`

### `GF-CLIENT-INSTRUCTION`

- Current product evidence:
  - `backend/app/modules/grant_fees/service.py`
  - `backend/tests/test_grant_fee_state_machine_api.py`
- Observed capability:
  - 后端支持：
    - `record_pay_instruction`
    - `record_abandon_instruction`
  - 前端尚未提供 SPEC 要求的批量用户路径
- Current classification:
  - `Partially Implemented`

### `GF-DETAIL`

- Current product evidence:
  - no dedicated FE route
  - no dedicated detail endpoint
- Observed capability:
  - 当前仅有 worklist page
- Current classification:
  - `Missing`

### `GF-BATCH`

- Current product evidence:
  - `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`
- Observed capability:
  - 页面按钮 `状态操作（预留）` 仍为 disabled
  - 没有多选批量设置 `ClientInstruction`
- Current classification:
  - `Missing`

### `GF-DOC-GEN`

- Current product evidence:
  - `docs/FPMS SPEC 2.0.md` §5.7.2 明确要求
  - 当前 repo 中 grant-fee 页面未接真实文书生成链
- Observed capability:
  - 无真实 `T_Document(TemplateCode=GRANT_FEE_NOTICE)` 生成与存档用户路径
- Current classification:
  - `Missing`

### `GF-BILL-GEN`

- Current product evidence:
  - 当前 grant-fee 页仅有 bill visibility
- Observed capability:
  - 无 grant-fee 页内 bill generation path
- Current classification:
  - `Missing`

### `GF-SETTLEMENT`

- Current product evidence:
  - no confirmed in-scope grant-fee specific user path yet
- Observed capability:
  - 需要与 billing 独立能力做边界判断
- Current classification:
  - `Contract/Plan Only`

## Workflow Boundary Freeze

### Included in `#15`

- grant-fee task carrier / state / worklist
- client instruction and notice operations inside grant-fee UI
- grant-fee draft generation and in-page linkage
- in-page bill / document linkage user paths
- grant-fee detail/edit / batch operations when explicitly required by spec

### Explicit non-closure / deferred from `#15` first-round ledger

- billing module独立 settlement / receipt 全流程
- documents module通用编辑页能力
- tasks module通用工作台能力
- 任何超出授权费页面内置用户路径的跨模块完整流程

## Product-closure Standard

### `Implemented`

- A real FE page and/or user path exists
- The supporting backend/API contract exists
- The slice expresses the workflow semantics required by spec

### `Partially Implemented`

- A real product slice exists
- But the slice is still only representative / partial relative to spec semantics

### `Contract/Plan Only`

- Only doc/spec/plan/task evidence exists
- Or workflow boundaries are not yet product-confirmed

### `Missing`

- No sufficient product behavior exists
- No reachable user path can be honestly credited

## Residual Workflow Ledger

### Residual slice candidates

- `GF-BATCH`
  - batch PAY / ABANDON operation path
- `GF-DOC-GEN`
  - real `GRANT_FEE_NOTICE` generation and archival
- `GF-DETAIL`
  - detail/edit capability if confirmed in-scope
- `GF-BILL-GEN`
  - in-page bill generation if confirmed in-scope
- `GF-SETTLEMENT`
  - downstream settlement semantics only if spec truly binds them into `#15`

### Already implemented slices to preserve, not reopen by default

- `GF-CARRIER`
- `GF-STATE`
- `GF-WORKLIST`
- `GF-DRAFT`
- `GF-POSTDRAFT`

## Shared-file / Ownership Analysis

### Current ledger story

- doc-only shared ownership:
  - `docs/superpowers/specs/2026-04-05-grant-fee-implementation-ledger-design.md`
  - `docs/superpowers/plans/2026-04-05-grant-fee-implementation-ledger.md`
  - `tasks/postenhancement/backend/GF-LEDGER-01.md`
  - `tasks/postenhancement/backend/GF-QA-LEDGER-01.md`

### Future shared ownership hotspots

- `backend/app/modules/grant_fees/api.py`
- `backend/app/modules/grant_fees/service.py`
- `backend/app/modules/grant_fees/schemas.py`
- `frontend/src/api/grantFees.ts`
- `frontend/src/api/grantFees.types.ts`
- `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`

## API / Service Impact

- Current residuals will likely continue to extend existing grant-fee endpoints and service helpers
- Real document generation would cross:
  - `grant_fees`
  - `documents`
- Bill-generation style slices would cross:
  - `grant_fees`
  - `billing`
  - possibly `fees`

## UI / State-action / Linkage Impact

- Current page is a single worklist surface
- Residual slices are likely to continue landing on the same page rather than a new module shell
- This increases FE shared ownership pressure and argues against parallel mixed-slice implementation

## Cross-module Impact

- `grant_fees`
- `fees`
- `billing`
- `documents`
- potentially `tasks`

## SQLite / Phase Compatibility Assessment

- This ledger story is doc-only and fully compatible with current phase constraints
- No schema / migration is required for the ledger itself
- Future `GF-DOC-GEN` or `GF-BILL-GEN` stories must explicitly re-check phase and prerequisite status before execution

## Risks / Blockers / Prerequisite Tasks

- Largest risk:
  - misreading worklist/state/draft generation as full workflow closure
- Second risk:
  - treating visibility as real document/bill linkage closure
- Third risk:
  - absorbing billing/documents independent capability into `#15`
- Current most appropriate first prerequisite/authority task:
  - `GF-LEDGER-01`

## Exact Closure Slice Candidates

### First-round ledger-only closure

- `GF-LEDGER-01`

### Most likely first implementation follow-up after ledger

- `GF-BATCH-INSTRUCTION-01`
  - direct SPEC 5.7.2 gap
  - narrower than real document generation
  - closes an actual user-path deficiency without absorbing cross-module document work
