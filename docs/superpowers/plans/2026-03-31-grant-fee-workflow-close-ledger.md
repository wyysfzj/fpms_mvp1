# P2 #15 Grant Fee Workflow Close Ledger

## Program

- Review item: `Priority P2 #15`
- Name: `授权费管理`
- Scope interpretation: `schema/model prerequisite + multiple workflow stories`
- Program status: `PASS (approved decomposition)`

## Approved Program Interpretation

`P2 #15` was explicitly decomposed into 4 executable slices:

1. `GF-PRE`
2. `GF-SM`
3. `GF-WL`
4. `GF-DRAFT`

Shared approved non-closure:

- `GF-DETAIL`
- `GF-BILL`
- `GF-DOC`
- `GF-RPT`
- `GF-SEARCH`
- `GF-IO`

## Item-to-Slice Ledger

### 1. `GF-PRE`

- Story name: `Grant Fee Workflow Prerequisite`
- Status: `PASS`
- Closure implemented:
  - 新增 `T_GrantFeeTask` 结构化承载
  - 新增 SQLite-safe migration
  - 冻结 `GrantFeeTask.Read / GrantFeeTask.Write`
  - 新增最小 grant-fee backend 模块骨架
- Evidence:
  - `artifacts/GFPRE-DB-01/**`
  - `artifacts/GFPRE-BE-01/**`
  - `artifacts/GFPRE-QA-01/**`
- Commit:
  - `ff561c4 feat: add grant fee workflow prerequisite`
- Residual gap:
  - 未实现 worklist/workbench
  - 未实现状态流转动作
  - 未实现 fee draft / bill / document linkage
- Close decision:
  - `covered under approved decomposition`

### 2. `GF-SM`

- Story name: `Grant Fee State Machine`
- Status: `PASS`
- Closure implemented:
  - grant-fee 主干状态机
  - 状态动作 contract
  - 非法转移 `400`
  - 缺失任务 `404`
  - `mark_draft_generated` 仅改状态、不生成草单
- Evidence:
  - `artifacts/GFSM-BE-01/**`
  - `artifacts/GFSM-QA-01/**`
- Commit:
  - `c95c59e feat: implement grant fee state machine`
  - `e1b4e36 docs: add grant fee state machine qa evidence`
- Residual gap:
  - 未实现 worklist/workbench
  - 未实现 fee draft linkage
  - 未实现 bill / document linkage
  - 未实现 frontend 状态动作 UI
- Close decision:
  - `covered under approved decomposition`

### 3. `GF-WL`

- Story name: `Grant Fee Worklist`
- Status: `PASS`
- Closure implemented:
  - `GET /api/v1/grant-fee-tasks/list`
  - grant-fee task 最小筛选与分页查询
  - grant-fee 专属 worklist 页面、路由、菜单入口
  - 状态只读展示与后续动作入口壳
- Evidence:
  - `artifacts/GFWL-BE-01/**`
  - `artifacts/GFWL-FE-01/**`
  - `artifacts/GFWL-QA-01/**`
- Commit:
  - `61a5e8e feat: implement grant fee worklist`
- Residual gap:
  - 未实现 fee draft linkage
  - 未实现 bill / document linkage
  - 未实现 detail/edit
  - 未实现前端真实状态动作执行
- Close decision:
  - `covered under approved decomposition`

### 4. `GF-DRAFT`

- Story name: `Grant Fee Draft Linkage`
- Status: `PASS`
- Closure implemented:
  - `POST /api/v1/grant-fee-tasks/{task_id}/generate-draft`
  - `GrantFeeTask -> FeeDraft` 最小草单生成链路
  - 幂等保护
  - 最小 `FeeItem` 创建
  - `draft_generated = true` 与状态投影进入 `DRAFT_GENERATED`
  - worklist 页面最小单行触发入口
- Evidence:
  - `artifacts/GFDRAFT-BE-01/**`
  - `artifacts/GFDRAFT-FE-01/**`
  - `artifacts/GFDRAFT-QA-01/**`
- Commit:
  - `b1bd3cb feat: implement grant fee draft linkage`
- Residual gap:
  - 未实现 bill linkage
  - 未实现 document/reminder linkage
  - 未实现 detail/edit
  - 未实现复杂批量选择器 / 失败重试 UI / reporting
- Close decision:
  - `covered under approved decomposition`

## Program Residual Gaps

The following remain intentionally open because they were explicitly outside the approved decomposition:

- `GF-DETAIL`
- `GF-BILL`
- `GF-DOC`
- `GF-RPT`
- `GF-SEARCH`
- `GF-IO`

## Final Close Decision

- `P2 #15` close decision: `covered under approved decomposition`
- Rationale:
  - `GF-PRE / GF-SM / GF-WL / GF-DRAFT` 均已实现
  - 每个 slice 都有 `PASS` evidence
  - 每个 slice 都完成了各自 task-gated close
  - 在已批准的 workflow decomposition 内不存在剩余未关闭 gap
- Important note:
  - This does **not** claim that every long-tail grant-fee enhancement is finished
  - It claims the approved decomposition of `P2 #15` is complete
