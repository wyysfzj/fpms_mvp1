# Commission Statistics Report Design

## Problem Statement

当前仓库虽然已经存在 commission settlement report 的部分基础，但还没有一个明确收敛的 `Commission Statistics Report` story 来闭合 SPEC 2.0 `9.4.5` 和 review 对“提成报表”的缺口。`RPT-COM` 第一轮不应扩成成本分析平台，而应先补齐一个最小可用的金额统计报表闭环：按代理人、案件、时间区间对已生成提成记录和结算数据进行筛选、汇总和列表展示。

## Assumptions

- 第一轮只统计**已生成的提成记录与结算数据**。
- 第一轮不统计潜在但尚未生成的提成机会。
- 页面继续落在现有 `frontend/src/modules/commission/pages/CommissionSettlement.vue`。
- 第一轮最小筛选集固定为：
  - `agent_id`
  - `case_id`
  - `date_range`
  - `time_field`
  - `settlement_status`
  - `line_status`
  - `currency`
- 第一轮最小闭环固定为：
  - 筛选
  - summary cards
  - 按代理人统计
  - 按案件统计
  - 明细列表
- 第一轮明确不纳入：
  - 客户类型/案件类型成本分析
  - 提成占服务费比例
  - 图表
  - 打印
  - 导出

## Scope

- `commission` 模块内的 report contract 收敛与补齐
- 现有 `CommissionSettlement.vue` 上的统计报表能力补齐
- 已生成提成与结算数据的金额统计

## Non-scope

- 独立 `CommissionReport.vue` 新页面
- 成本占比分析
- 图表、打印、导出
- 潜在提成预测
- 多代理拆分深度分析

## Current State Assessment

- backend 已有：
  - `GET /commission/reports/settlement`
  - 主要文件：
    - `backend/app/modules/commission/api.py`
    - `backend/app/modules/commission/service.py`
- frontend 已有：
  - `frontend/src/modules/commission/pages/CommissionSettlement.vue`
  - `frontend/src/api/commission.ts`
  - `frontend/src/api/commission.types.ts`
- 已存在的报表基础包括：
  - 筛选项
  - summary cards
  - `by_agent`
  - `by_case`
  - `by_time`
  - `details`

## API / Service Impact

第一轮更像是：

- backend contract refinement
- frontend reporting completion

主要目标：

- 确认并补齐 report contract 是否稳定覆盖：
  - `totals`
  - `by_agent`
  - `by_case`
  - `details`
- 保证筛选语义与前端展示一致
- 避免前端自行拼装关键统计结果

## UI / Permission Impact

- UI 继续落在 `CommissionSettlement.vue`
- 权限继续沿用 `Commission.Read`
- 不新增专门 report 权限码，除非实现时发现必须细分

## SQLite / Phase Compatibility

- 当前高概率无需 schema 变更
- 因此 story 预计可保持在当前 Phase 约束内执行

## Risks / Blockers

- 现有 settlement report 可能只是近似实现，而不是 story 级闭环
- `CommissionSettlement.vue` 同时承担批次创建、明细生成、报表查询三种职责，前端任务必须严格只关闭报表 slice
- 如果 contract 不稳定，前端容易被迫拼装统计结果

## Exact Closure Slice

`在 commission 模块中，基于已生成的提成记录与结算数据，提供按代理人 / 案件 / 时间区间统计提成金额的报表最小闭环，包括筛选、summary cards、按代理人与案件分组统计、以及明细列表展示。`

## Final Design Judgment

- `可在当前约束下拆成可执行原子任务`
- 推荐进入 `writing-plans`
