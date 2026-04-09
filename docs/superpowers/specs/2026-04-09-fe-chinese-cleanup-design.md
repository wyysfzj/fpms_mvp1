# FE Chinese Cleanup Design

- date: `2026-04-09`
- scope: `frontend user-facing Simplified Chinese cleanup only`

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `frontend-only cleanup story`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Problem Statement

当前前端大多数用户可见文案已经是简体中文，但仍存在真实英文残留，主要集中在两类：

- 原始英文状态值 / 枚举值 / 类型值直接展示给用户
- 英文技术词直接作为 UI 文案出现，例如 `ID`

这违反 `AGENTS.md` 中“所有 user-facing UI text 必须为简体中文”的铁律。当前专项目标是清零这些前端用户可见英文残留，不扩展为产品功能、视觉或接口改造。

## Assumptions

- 只有真实 FE 页面上的英文残留被替换或映射为简体中文，专项才能计入 `Closed`
- 只做 FE 用户可见文案清理
- 不做 backend
- 不改 API contract
- 不做视觉重构
- 技术值可以保留在代码层，但不能直接裸露给用户

## Scope

- 页面标题、菜单、按钮、标签、placeholder、helper text、toast、dialog、empty state
- 直接渲染到页面的状态值、枚举值、类型值
- 现有 “中文 + ID” 用户可见标签/placeholder 的中文化规范

## Non-scope

- backend 改动
- API contract 改动
- 数据库存储值、枚举 code、内部常量重命名
- 页面结构/视觉重构

## Confirmed English Residue Categories

### 1. Raw enum / status exposure

- `frontend/src/modules/cases/components/CaseFeesTab.vue`
  - 直接显示 `row.status`
- `frontend/src/modules/commission/pages/CommissionRuleList.vue`
  - `case_type` / `fee_type` 直接显示原始值

### 2. English technical words as UI labels

- `frontend/src/modules/commission/pages/CommissionRuleList.vue`
  - 列标题 `ID`

### 3. Mixed Chinese + technical English boundary labels

- `frontend/src/modules/expenses/pages/ExpenseCreate.vue`
  - `部门ID（可选）`
- `frontend/src/modules/expenses/pages/ExpenseList.vue`
  - `部门ID`
  - `经手人用户ID`

## Shared-file / Ownership Analysis

- `frontend/src/constants/displayText.ts`
  - 共享显示文本映射入口，必须串行独占
- `frontend/src/constants/labels.zh.ts`
  - 若本轮需要补通用中文标签，也必须串行独占
- `frontend/src/modules/cases/components/CaseFeesTab.vue`
  - 核心高可见页面，单独归入核心页面 wave
- `frontend/src/modules/commission/pages/CommissionRuleList.vue`
  - 核心高可见页面，单独归入核心页面 wave
- `frontend/src/modules/expenses/pages/ExpenseCreate.vue`
- `frontend/src/modules/expenses/pages/ExpenseList.vue`
  - 归入长尾页面 wave

## Cleanup Strategy

### Wave A: shared display text / common mapping

- 目标：补齐/规范共享显示映射，使后续页面替换不重复堆逻辑

### Wave B: high-visibility core pages

- 目标：清掉当前最明显、用户最容易看到的英文残留
- 页面：
  - `CaseFeesTab.vue`
  - `CommissionRuleList.vue`

### Wave C: long-tail boundary pages

- 目标：把剩余 “中文 + ID” 等用户可见边界标签统一成更自然的简体中文
- 页面：
  - `ExpenseCreate.vue`
  - `ExpenseList.vue`

### Wave D: QA close-audit

- 目标：验证 allowlist 页面清理完成，且 repo 内未剩下本专项定义的真实英文残留

## Verification Expectations

- `cd frontend && npm run lint -- <allowlist files>`
- `cd frontend && npm run typecheck`
- `rg -n` 对 allowlist 做英文残留复查
- `./scripts/task_validate.sh <TASK-ID>`

## Risks / Blockers

- 最大风险是把代码层技术值与用户可见文案混为一谈
- 第二个风险是多个 FE cleanup 任务同时改共享显示映射文件
- 第三个风险是把长尾边界项和核心高风险页面塞进一个 broad task

## Exact Non-closure Boundary

- 不做 backend
- 不改 API contract
- 不重构页面结构
- 不做视觉改版
- 不把整个前端中文化专项压成单一 mega task

## Recommended Result Shape

- `可进入 frontend cleanup implementation planning`
