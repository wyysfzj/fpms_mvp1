# P2 #13 Reports Program Decomposition Design

## Problem Statement

`P2 #13 所有统计报表` 不是单一功能缺口，而是一个由多个报表族组成的 program-level review item。当前仓库只有零散 summary、dashboard 和部分 commission settlement reporting，缺少 SPEC 2.0 `9.4` 定义的完整统计报表族。因此，这条 item 不能诚实地直接进入实现，必须先拆成独立 stories，并明确本轮只推进其中一个报表族的最小闭环。

## Assumptions

- 权威报表族清单固定为 5 类：
  - `Case`
  - `Fee`
  - `Annuity`
  - `Billing`
  - `Commission`
- `Dashboard`、通用 KPI 总览和横向经营分析页不属于本条。
- 第一轮每个报表族的最小闭环统一为：
  - 筛选
  - summary cards
  - 明细列表
- 第一轮明确不纳入：
  - 图表
  - 打印
  - 复杂导出
  - drill-down / 透视分析
- 各报表族优先落在各自业务模块，而不是先做统一 `reports shell`。
- `P2 #13` 必须先拆成独立 stories，本轮只能选择其中 1 个进入实现。

## Scope

- 将 `P2 #13` 解释为 program-level item
- 冻结 5 个报表族
- 为每个报表族定义第一轮最小闭环
- 给出 decomposition recommendation 和优先顺序建议

## Non-scope

- 在同一轮里一起实现 5 个报表族
- 统一 `reports shell` 先行建设
- 图表/打印/复杂导出平台
- 通用 BI / 分析平台抽象

## Report Family Inventory

### 1. Case Statistics Report

- 目标：
  - 按客户统计案件数量与类型分布
  - 按国别统计案件数量
  - 按代理人统计案件数量和授权率
  - 按年度/月度统计新案/授权/终止数量趋势
- 主要数据源：
  - `T_Case`
  - `T_Country`
  - 案件参与方维度
- 当前现状：
  - 基本缺失

### 2. Fee Statistics Report

- 目标：
  - 按客户、案件类型、国别统计服务费/官方费收入
  - 按时间段统计费用类型总额
- 主要数据源：
  - `T_FeeDraft`
  - `T_FeeItem`
  - `T_Expense`
  - 相关账单数据
- 当前现状：
  - 零散费用页面存在，但无真正统计报表

### 3. Annuity Statistics Report

- 目标：
  - 按国别/客户/年份统计年费应缴/实缴情况
  - 统计年费监视成功率
- 主要数据源：
  - `T_AnnuityTask`
  - `T_GovPayment`
  - `T_CaseReceipt`
- 当前现状：
  - 有任务页和局部 summary，但无统计报表

### 4. Billing Statistics Report

- 目标：
  - 应收账款报表
  - 逾期账款报表
  - 坏账报表
  - 账龄统计
- 主要数据源：
  - `T_Bill`
  - `T_Offset`
  - `T_Dunning`
  - `T_Payment`
- 当前现状：
  - 账单与收款核心存在，但无完整统计报表

### 5. Commission Statistics Report

- 目标：
  - 按代理人/时间段统计提成金额
  - 按案件统计提成分配
  - 按案件类型/客户类型统计提成成本
- 主要数据源：
  - `T_Commission`
  - `T_CommissionSettlement`
  - `T_CommissionSettleLine`
- 当前现状：
  - 已有部分 settlement report 基础，但仍非完整统计报表族

## Per-family Minimum Closure Definition

每个子 story 第一轮最小闭环统一为：

- 筛选条件区
- summary cards
- 明细列表

但各报表族的统计口径与数据源不共享到可以被视为一个 story：

- `Case` 偏案件维度
- `Fee` 偏费用与收入维度
- `Annuity` 偏年费与实缴维度
- `Billing` 偏应收与账龄维度
- `Commission` 偏提成与结算维度

## Shared Shell / Routing Impact

当前更合理的第一轮策略是：

- 各报表族落在各自业务模块
- 不先做统一 `reports shell`

原因：

- 当前仓库没有成熟的统一报表模块
- 各报表族已有自然业务归属
- 如果强行做统一壳，路由、菜单、共享筛选、导出 contract 都会变成新的 shared prerequisite

## API / Service Impact

- 当前没有独立通用 `reports` 后端模块
- 已存在的报表相关 contract 主要集中在：
  - `commission settlement report`
- 其余 4 个报表族都更像新的聚合查询 slices

因此当前判断是：

- `P2 #13` 作为整体不应直接实现
- 应先做 `program decomposition`
- 再对选中的 1 个报表族单独进入 story 级 spec / plan

## UI / Permission Impact

- UI 优先落在各业务模块，而不是统一报表中心
- 权限优先沿用各业务模块 read/report 权限语义
- 前端全部用户可见文案必须为简体中文

## Export / Chart / Print Impact

第一轮统一列为 `non-closure`：

- 图表
- 打印
- 复杂导出
- drill-down
- 透视分析

## SQLite / Phase Compatibility Assessment

- `P2 #13` 作为整体不应进入实现
- 先拆 story 不涉及 schema
- 某些子 story 可能只需要聚合查询和前端页面，不一定触发 schema prerequisite
- 在未冻结具体报表族之前，不能诚实地宣称“当前可直接执行”

## Risks / Blockers

- 把 5 个报表族误当成一个 story
- 在统一统计口径前直接写共享 API/types
- 过早做统一 reports shell
- 把图表/导出/打印一起吸进第一轮 closure

## Exact Closure Slice Candidates

当前 program-level item 不应直接定义为“实现所有统计报表”，而应先拆成 5 个候选 stories：

- `RPT-CASE`
- `RPT-FEE`
- `RPT-ANN`
- `RPT-BILL`
- `RPT-COM`

它们共同的第一轮 explicit non-closure：

- 图表
- 打印
- 复杂导出
- drill-down
- BI 平台化
- “把剩余报表一起补齐”

## Program Decomposition Recommendation

推荐：

1. 先把 `P2 #13` 记录为 `program decomposition item`
2. 输出 5 个子 story 的 decomposition ledger
3. 本轮从中只选 1 个报表族进入后续完整流程

当前优先候选建议：

- `RPT-COM`
  - 原因：已有 settlement report 基础，最接近“已有 contract + 缺完整统计报表”
- `RPT-BILL`
  - 原因：账单、预收、坏账、逾期最近已有连续基础积累，但跨数据源复杂度高于 `RPT-COM`

## Final Design Judgment

正式结论：

- `P2 #13` 不是单一 story，而是 **program-level review item**
- `不可直接实现，必须先新增 prerequisite task(s)`

这里的 prerequisite 不是先指 schema，而是：

- 必须先做 `program decomposition`
- 不能直接把 5 类报表当作一个执行单元
