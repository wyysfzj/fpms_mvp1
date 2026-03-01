# FPMS Case Workflow Stepper V3 设计规范（AI可执行版）

## 1. 文档目标
本规范用于指导 Codex/Claude/Gemini 实现 FPMS 的 V3 界面原型（或前端页面），并确保与 `newpatent_V3.html` 的交互和视觉一致。

本版核心要求：
- 保留 `newpatent_static.html` 的视觉风格与左侧导航结构（尤其是 `业务实体`、`财务` 分区）。
- 在 Dashboard 提供可点击的 Case Workflow Stepper 阶段统计。
- 在 Dashboard 保留并展示“财务状况”面板。
- 在 Case Detail 明确显示“当前是第几步/共5步”。
- **不得**展示“业务状态映射（UI + 业务层）”面板（映射逻辑可保留在代码层）。

---

## 2. 输入与输出约束

### 2.1 输入
- 视觉与结构基线：`newpatent_static.html`
- 交互能力基线：`newpatent_V3.html`
- 样式附件：`attachments/v3_styles.css`

### 2.2 输出
至少交付：
1. 可运行页面（HTML 或前端页面）
2. 完整样式（可直接复用 `v3_styles.css`）
3. 可点击交互：Dashboard -> 列表 -> 详情

---

## 3. 全局视觉与布局规范

### 3.1 视觉基调（必须）
- 采用 Modern Tech 风格：冷灰背景 + 白色卡片 + 蓝色主色。
- 字体：`Inter` 为主，`JetBrains Mono` 用于编号/金额。
- 圆角与边框：小圆角（`--radius: 6px`）+ 细边框（`--border`）。

### 3.2 页面框架（必须）
- 左侧 Sidebar（固定宽度）
- 顶部 Header（搜索 + 用户区）
- 右侧主视图区（支持 view 切换）

### 3.3 Sidebar 结构（必须完全保留）
必须存在以下分区与顺序：
1. `总览 Dashboard`
2. `业务实体 (Entity)`
: `客户 Clients` / `案件 Cases` / `案件详情`
3. `财务 (Finance)`
: `费用 & 账单` / `回款 & 核销`

---

## 4. Dashboard 规范

### 4.1 顶部 Pipeline 卡片（保留）
保留四卡：
- `NEW CASES`
- `PENDING TASKS`
- `UNBILLED DRAFTS`
- `UNALLOCATED`

每卡必须包含：
- 顶部彩条（`pipe-bar`）
- 数值（`pipe-num`）
- 说明（`pipe-label`）

### 4.2 Workflow Stepper 统计区（新增核心）
组件名称建议：`workflow-overview`

必须实现：
- 5 个阶段卡：`受理 / 初审 / 公布 / 实审 / 授权`
- 每卡显示：数量 + 占比
- 点击任一卡 -> 按该阶段筛选案件并进入列表页
- 支持“查看全部案件”清除筛选

### 4.3 阶段案件列表（Dashboard 内）
必须列字段：
- 案号
- 客户
- 案件名称
- 当前步骤（格式：`第N步/5 · 阶段名`）
- 法律状态
- 操作（查看详情）

### 4.4 财务状况面板（必须保留）
Dashboard 右侧必须保留“财务状况”卡块，至少含：
- 待核销 Payment（绿色高亮）
- 逾期账单
- 待付款账单

---

## 5. Cases 列表页规范

### 5.1 列表行为
- 支持承接 Dashboard 的阶段筛选条件。
- 显示当前筛选说明（例如：`案件列表 · 实审`）。
- 支持“清除阶段筛选”。

### 5.2 列字段
- 案号
- 客户
- 案件名称
- 当前步骤（第N步/5）
- 法律状态
- 申请日
- 负责人

点击行可进入详情页。

---

## 6. Case Detail 规范

### 6.1 Stepper 显示（必须）
- 5 步固定顺序：`受理 -> 初审 -> 公布 -> 实审 -> 授权`
- 视觉状态：
  - 已完成：`done`
  - 当前：`active`
  - 未到达：默认

### 6.2 当前步信息（必须）
页面需明确展示：
- 当前步骤名称
- 步骤序号（格式：`第N步 / 5`）
- 法律状态
- 下一动作

### 6.3 右侧信息区（必须）
保留：
- Deadline 卡
- 关联任务列表

### 6.4 分支状态提示（建议）
若状态为分支（如 `REJECTED` / `TERMINATED` / `INVALIDATED`），可在详情页显示提示，但不改变主干 5 步定义。

---

## 7. 业务状态映射规范（逻辑层）

> 注意：本映射用于逻辑计算，**不以单独面板展示在 UI 中**。

| Status | 映射阶段 | 步序 |
|---|---|---|
| WAITING_RECEIPT | 受理 | 1 |
| PRELIM_EXAM / PRELIM_PASS / AMENDMENT | 初审 | 2 |
| PUBLISHED | 公布 | 3 |
| SUB_EXAM / OA1 / OA2 / REEXAM | 实审 | 4 |
| GRANTED | 授权 | 5 |
| REJECTED | 实审（分支） | 4 |
| TERMINATED / INVALIDATED | 授权（分支历史） | 5 |

---

## 8. 交互流（必须）

1. 在 Dashboard 点击阶段卡（例如“实审”）
2. 系统设置筛选条件并切换到 Cases 列表
3. 列表仅展示该阶段案件
4. 点击任一案件进入 Case Detail
5. 详情页展示该案 `第N步 / 5`
6. 返回列表与返回 Dashboard 保持可用

---

## 9. 响应式与可用性

### 9.1 断点要求
- `<=1260px`：多栏降级（列表与财务上下堆叠）
- `<=780px`：卡片与 Stepper 继续降级为窄屏布局

### 9.2 UX Best Practice
- 点击目标明确：阶段卡与案件行可点击且反馈清晰。
- 信息层级清晰：总览分布 -> 列表筛选 -> 个案详情。
- 决策信息前置：详情页第一屏就看到 `第N步/5` 与下一动作。

---

## 10. CSS 附件说明

- 附件文件：`attachments/v3_styles.css`
- 用途：V3 视觉和布局基线
- 要求：
  - 可直接 `<link>` 引入，或复制到工程样式系统
  - 允许按技术栈拆分，但必须保持视觉等效

---

## 11. 验收清单（DoD）

- [ ] 左侧导航保留 `业务实体` 与 `财务` 分区结构
- [ ] Dashboard 有 5 阶段 Stepper 统计卡，支持点击筛选
- [ ] Dashboard 保留“财务状况”面板
- [ ] UI 中没有“业务状态映射（UI + 业务层）”展示区
- [ ] Case Detail 显示 `第N步 / 5`
- [ ] 列表/详情/总览的跳转与返回链路可用
- [ ] 移动端与窄屏不破版

---

## 12. 可直接给 Codex/Claude/Gemini 的执行指令

```text
请按以下约束实现页面：
1) 以 newpatent_static.html 视觉风格和左侧导航结构为基线，保留“业务实体(Entity)”和“财务(Finance)”分区。
2) 在 Dashboard 增加 Case Workflow Stepper 统计区（受理/初审/公布/实审/授权），每卡可点击筛选并跳转案件列表。
3) 在 Dashboard 保留“财务状况”面板（待核销、逾期、待付款）。
4) 不要在 UI 中展示“业务状态映射（UI + 业务层）”面板；映射逻辑可保留在代码里。
5) 在 Case Detail 必须显示当前处于第几步（格式：第N步/5）和当前步骤名称。
6) 保证返回路径可用：Dashboard -> 列表 -> 详情 -> 返回。
7) 优先复用附件 CSS（v3_styles.css），保持 V3 视觉一致。
8) 输出代码时给出关键 class 与状态映射实现说明，并附验收结果对应 DoD 清单。
```

