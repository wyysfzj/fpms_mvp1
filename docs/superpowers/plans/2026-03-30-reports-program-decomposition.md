# Reports Program Decomposition Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 `P2 #13 所有统计报表` 从 program-level review item 拆解为可执行的独立子 stories，并确定本轮只推进一个报表族。

**Architecture:** 不直接实现报表功能；先冻结 5 个报表族的 story 边界、最小闭环、推荐优先级和 deferred 清单。后续每个报表族都应拥有自己的 spec、plan、task manifest 和执行 wave。

**Tech Stack:** Markdown specs/plans, existing module APIs/pages, Superpowers planning workflow

---

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `program-level decomposition before implementation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Decomposition Ledger

### Sub-story 1: `RPT-CASE`

- Domain: `cases`
- Minimum closure:
  - 筛选
  - summary cards
  - 明细列表
- Default non-closure:
  - 图表
  - 打印
  - 导出
  - drill-down
- Likely files:
  - `backend/app/modules/cases/api.py`
  - `backend/app/modules/cases/service.py`
  - `frontend/src/api/cases.ts`
  - `frontend/src/api/cases.types.ts`
  - `frontend/src/modules/cases/pages/<report-page>.vue`
- Prereq risk:
  - 统计口径冻结
  - 国家/申请人维度完整性
- Status:
  - `deferred until selected`

### Sub-story 2: `RPT-FEE`

- Domain: `fees`
- Minimum closure:
  - 筛选
  - summary cards
  - 明细列表
- Default non-closure:
  - 图表
  - 打印
  - 导出
  - 毛利 drill-down
- Likely files:
  - `backend/app/modules/fees/api.py`
  - `backend/app/modules/fees/service.py`
  - `frontend/src/api/fees.ts`
  - `frontend/src/api/fees.types.ts`
  - `frontend/src/modules/fees/pages/<report-page>.vue`
- Prereq risk:
  - 费用/收入统计口径跨 draft/bill/expense
- Status:
  - `deferred until selected`

### Sub-story 3: `RPT-ANN`

- Domain: `annuity`
- Minimum closure:
  - 筛选
  - summary cards
  - 明细列表
- Default non-closure:
  - 图表
  - 打印
  - 导出
- Likely files:
  - `backend/app/modules/annuity/api.py`
  - `backend/app/modules/annuity/service.py`
  - `frontend/src/api/annuity.ts`
  - `frontend/src/api/annuity.types.ts`
  - `frontend/src/modules/annuity/pages/<report-page>.vue`
- Prereq risk:
  - 应缴/实缴口径需要联结 gov payment / receipt
- Status:
  - `deferred until selected`

### Sub-story 4: `RPT-BILL`

- Domain: `billing`
- Minimum closure:
  - 筛选
  - summary cards
  - 明细列表
- Default non-closure:
  - 图表
  - 打印
  - 导出
  - 催款效果高级分析
- Likely files:
  - `backend/app/modules/billing/api.py`
  - `backend/app/modules/billing/service.py`
  - `frontend/src/api/billing.ts`
  - `frontend/src/api/billing.types.ts`
  - `frontend/src/modules/billing/pages/<report-page>.vue`
- Prereq risk:
  - AR/overdue/bad-debt 统计口径跨 bill/offset/dunning/payment
- Status:
  - `candidate`

### Sub-story 5: `RPT-COM`

- Domain: `commission`
- Minimum closure:
  - 筛选
  - summary cards
  - 明细列表
- Default non-closure:
  - 图表
  - 打印
  - 导出
  - 多代理拆分深度分析
- Likely files:
  - `backend/app/modules/commission/api.py`
  - `backend/app/modules/commission/service.py`
  - `frontend/src/api/commission.ts`
  - `frontend/src/api/commission.types.ts`
  - `frontend/src/modules/commission/pages/CommissionSettlement.vue` or sibling page
- Prereq risk:
  - 最低，已有 settlement report 基础
- Status:
  - `recommended first story`

## First-story Recommendation

推荐本轮优先做：

1. `RPT-COM`
   - 原因：
     - 已有 backend settlement report contract
     - 已有 frontend settlement reporting page
     - 最容易收敛成“扩展为完整 commission statistics report”的 story
2. `RPT-BILL`
   - 备选原因：
     - 近期 billing 相关基础已经连续补齐
     - 但数据口径复杂度明显高于 `RPT-COM`

## Execution Rule

- 当前 plan 只关闭 `P2 #13` 的 decomposition closure
- 不授权直接实现任何一个报表族
- 只有在用户明确选择一个子 story 之后，才可以为该子 story 进入新的 brainstorming/spec/plan cycle

## Explicit Non-closure

- 不实现任何一个报表页面
- 不新增报表 API
- 不做统一 reports shell
- 不做图表/打印/导出
- 不做“剩余报表收尾”

## Recommended Next Step

- Ask user to choose one:
  - `RPT-COM`（推荐）
  - `RPT-BILL`
  - `RPT-CASE`
  - `RPT-FEE`
  - `RPT-ANN`

用户选定后，为该子 story 单独开启：

- brainstorming
- spec sign-off
- writing-plans
- implementation
