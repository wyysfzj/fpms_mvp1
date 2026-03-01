# FPMS V3 Case Workflow Stepper UI Enhancement — Implementation Plan

> **版本**: 1.0
> **日期**: 2026-02-22
> **作者**: Architect Agent
> **状态**: 待审批

---

## 1. 现状分析

### 1.1 现有 Dashboard

**文件**: `frontend/src/modules/dashboard/pages/Dashboard.vue`

当前 Dashboard 包含：
- **Pipeline Cards** (4 卡): NEW CASES / PENDING TASKS / UNBILLED DRAFTS / UNALLOCATED
- **ActionCenter**: 待办任务列表（从后端 tasks API 聚合）
- **FinancePanel**: 财务状况（待核销 Payment、逾期账单、待付款账单）
- **NewCaseDrawer**: 新建案件抽屉

**数据来源** (`dashboard.api.ts`): 客户端聚合 5 个现有 API（cases, tasks, feeDrafts, bills, payments），无服务端聚合接口。

**缺失项（对比 V3 规范）**:
- 无 Case Workflow Stepper 统计区（5 阶段卡片：受理/初审/公布/实审/授权）
- 无阶段案件列表（Dashboard 内嵌的筛选表格）
- 无"查看全部案件"按钮

### 1.2 现有 Case List

**文件**: `frontend/src/modules/cases/pages/CaseList.vue`

当前功能：
- el-table 展示：编号 / 案号 / 标题 / 客户 / 状态 / 更新时间
- 分页（PaginationBar）
- 简单的查看操作跳转至详情页

**缺失项**:
- 不支持接收 Dashboard 传来的阶段筛选条件
- 无"当前步骤"（第N步/5）列
- 无筛选说明（如 `案件列表 · 实审`）
- 无"清除阶段筛选"按钮
- 缺失列：申请日、负责人

### 1.3 现有 Case Detail

**文件**: `frontend/src/modules/cases/pages/CaseDetail.vue`

当前功能：
- 案件头信息（案号、申请日、客户、标题、状态 tag）
- el-tabs: 概览 / 权利要求 / 官方文件 / 费用 / 账单 / 任务
- 概览 tab: 案件信息表格、发明人标签、快捷操作
- 侧栏: 发明人、快捷操作
- RelationChainCard 面包屑导航

**缺失项**:
- 无 Stepper 可视化（5 步进度条：受理 → 初审 → 公布 → 实审 → 授权）
- 无"当前步骤"KPI 卡片（当前步骤名称、步骤序号 `第N步/5`、法律状态、下一动作）
- 无 Deadline 卡片
- 无关联任务列表
- 无分支状态提示（REJECTED / TERMINATED / INVALIDATED）

### 1.4 现有 Sidebar 导航

**文件**: `frontend/src/constants/menu.ts` + `SidebarNav.vue`

当前分组：
- 工作台
- 案件管理（案件列表 / 文档管理 / 费用管理 / 账单管理）
- 期限监控（任务列表）
- 客户中心（客户列表）
- 系统设置

**V3 规范要求**:
- 总览 Dashboard
- 业务实体 (Entity): 客户 Clients / 案件 Cases / 案件详情
- 财务 (Finance): 费用 & 账单 / 回款 & 核销

### 1.5 后端 API 现状

#### Cases API (`backend/app/modules/cases/api.py`)

| 端点 | 说明 | 不足 |
|---|---|---|
| `GET /cases` | 列表，支持 q/status/client_id 筛选 | 返回字段缺少 `filing_date`、`recv_date`；无 workflow_step 计算 |
| `GET /cases/{id}` | 详情 | 仅返回基础字段 (id/case_no/case_type/patent_category/flow_dir/client_id)，**缺少** title_cn、status、filing_date、app_no 等 |
| `POST /cases` | 创建 | — |
| `PUT /cases/{id}` | 更新 | — |

#### Case Model (`backend/app/modules/cases/models.py`)

`Case` 表已有：`status` (String(32), default 'NOT_FILED'), `filing_date`, `recv_date`

#### CaseStatus Enum (`backend/app/modules/cases/enums.py`)

现有状态: `NOT_FILED / PENDING / GRANTED / REJECTED / WITHDRAWN / ABANDONED / EXPIRED`

**V3 规范需要的状态**: `WAITING_RECEIPT / PRELIM_EXAM / PRELIM_PASS / AMENDMENT / PUBLISHED / SUB_EXAM / OA1 / OA2 / REEXAM / GRANTED / REJECTED / TERMINATED / INVALIDATED`

**Gap**: 现有 CaseStatus 枚举与 V3 Workflow Stepper 所需的状态映射不兼容。需要扩展枚举。

### 1.6 Gap Analysis 总结

| 规范要求 | 现有支持 | Gap 级别 |
|---|---|---|
| Dashboard Workflow Stepper 统计 | 无 | **新增** |
| Dashboard 阶段案件列表 | 无 | **新增** |
| Dashboard 财务状况面板 | 已有 FinancePanel | 兼容 |
| Dashboard Pipeline 四卡 | 已有 PipeCard | 兼容 |
| Case List 阶段筛选 | 无 | **新增** |
| Case List 步骤列 | 无 | **新增** |
| Case Detail Stepper | 无 | **新增** |
| Case Detail KPI 卡片 | 无 | **新增** |
| Case Detail Deadline 卡片 | 无 | **新增** |
| Case Detail 关联任务 | 无 | **新增** |
| Case Detail 分支状态提示 | 无 | **新增** |
| Sidebar 业务实体/财务分区 | 不匹配 | **修改** |
| 后端 CaseStatus 枚举扩展 | 不兼容 | **修改** |
| 后端 GET /cases/{id} 返回完整字段 | 缺字段 | **修改** |
| 后端 GET /cases 返回 filing_date | 缺字段 | **修改** |
| 前端状态到 Workflow Step 映射 | 无 | **新增** |
| v3_styles.css 集成 | 无 | **新增** |
| 响应式断点处理 | 部分 | **增强** |

---

## 2. 增强建议

### 2.1 后端增强

#### 2.1.1 扩展 CaseStatus 枚举

**方案**: 在 `enums.py` 中添加 V3 所需的所有法律状态值。保留现有值以保持向后兼容。

```python
class CaseStatus(str, Enum):
    # 现有（保留）
    NOT_FILED = "NOT_FILED"
    PENDING = "PENDING"
    GRANTED = "GRANTED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"
    ABANDONED = "ABANDONED"
    EXPIRED = "EXPIRED"
    # V3 新增
    WAITING_RECEIPT = "WAITING_RECEIPT"
    PRELIM_EXAM = "PRELIM_EXAM"
    PRELIM_PASS = "PRELIM_PASS"
    AMENDMENT = "AMENDMENT"
    PUBLISHED = "PUBLISHED"
    SUB_EXAM = "SUB_EXAM"
    OA1 = "OA1"
    OA2 = "OA2"
    REEXAM = "REEXAM"
    TERMINATED = "TERMINATED"
    INVALIDATED = "INVALIDATED"
```

**风险**: 数据库中 status 是 String(32)，新值均 ≤ 32 字符，无需迁移。

#### 2.1.2 丰富 GET /cases/{id} 返回字段

当前 `get_case` 仅返回 6 个字段。需补充：`title_cn`, `title_en`, `status`, `filing_date`, `recv_date`, `app_no`, `client_name`（通过 join 或额外查询）, `created_at`, `updated_at`。

#### 2.1.3 丰富 GET /cases 列表返回字段

当前缺少 `filing_date`, `recv_date`。需在列表 items 中补充。

#### 2.1.4 新增 GET /cases/workflow-stats 端点（可选）

**方案 A（推荐）**: 新增服务端聚合接口，按 workflow step 分组统计案件数量。
```
GET /api/v1/cases/workflow-stats
Response: { steps: [{ key: "ACCEPTED", count: 2 }, ...], total: 12 }
```

**方案 B**: 前端本地计算（基于全量 cases 列表）。MVP 阶段可接受，但数据量大时性能不佳。

**建议**: MVP 阶段使用方案 B（前端计算），后续迭代迁移到方案 A。

### 2.2 前端增强

#### 2.2.1 新增 Workflow 状态映射模块

在 `frontend/src/constants/` 下新建 `workflow.ts`，定义：
- `WORKFLOW_STEPS`: 5 步定义（key, label, color）
- `STATUS_STEP_MAP`: 法律状态 → workflow step 映射
- `getWorkflowStep(status)`: 计算函数
- `getStepLabel(status)`: 格式化 `第N步/5 · 阶段名`

#### 2.2.2 Dashboard Workflow Overview 组件

新建 `WorkflowOverview.vue`，实现：
- 5 阶段卡片（wf-card），显示数量和占比
- 点击卡片跳转至 CaseList 并携带筛选参数
- "查看全部案件"按钮清除筛选

#### 2.2.3 Dashboard 阶段案件列表

新建 `WorkflowCaseTable.vue`，在 Dashboard 内嵌显示：
- 表头：案号 / 客户 / 案件名称 / 当前步骤 / 法律状态 / 操作
- 支持按选中阶段筛选
- "进入完整列表"按钮

#### 2.2.4 Case Detail Stepper 组件

新建 `CaseStepper.vue`，实现：
- 5 步可视化（done/active/未到达三态）
- KPI 卡片（当前步骤、步骤序号、法律状态、下一动作）
- 分支状态警告提示

#### 2.2.5 Case Detail 右侧面板

新建 `CaseDeadlineCard.vue` 和 `CaseTaskList.vue`：
- Deadline 卡片（红色边框，显示日期和剩余天数）
- 关联任务列表

#### 2.2.6 CaseList 增强

- 接收 route query `?step=ACCEPTED` 等筛选参数
- 新增"当前步骤"列
- 筛选说明标题
- "清除阶段筛选"按钮

#### 2.2.7 Sidebar 重构

修改 `menu.ts` 分组结构以匹配 V3 规范要求。

### 2.3 兼容性考虑

| 考虑项 | 处理方式 |
|---|---|
| 现有 CaseStatus 枚举值 | 保留所有现有值，新增 V3 状态。未映射的状态默认归入"受理" |
| 现有 Dashboard 功能 | 完全保留 Pipeline 四卡和 FinancePanel，新增 WorkflowOverview |
| 现有 CaseDetail tabs | 保留所有 tabs，在概览 tab 顶部新增 Stepper |
| 现有 CSS 变量 | v3_styles.css 变量名与 variables.css 对应良好，通过别名映射 |
| 前端路径别名 | 不使用 `@/`，严格使用相对路径 |
| SQLite 兼容性 | 无新迁移需求，status 字段已有足够宽度 |

### 2.4 风险与挑战

| 风险 | 影响 | 缓解措施 |
|---|---|---|
| Case 表缺少 deadline 字段 | Detail 页无法显示真实绝限 | 关联 tasks 表的 due_date 取最近绝限 |
| Case 无负责人字段 (owner) | List 页无法显示负责人列 | 使用 `created_by` 或关联用户，MVP 可显示 "-" |
| 前端状态映射逻辑与后端不一致 | 步骤计算错误 | 映射逻辑集中在 `workflow.ts`，单元测试覆盖 |
| workflow-stats 在大数据量下性能 | 列表页加载慢 | MVP 使用前端计算，page_size=200；后续增加服务端聚合 |
| v3_styles.css 与 Element Plus 冲突 | 样式错乱 | v3 样式限定在特定 class scope 下，不全局覆盖 |

---

## 3. 任务分解（Work Breakdown Structure）

### Phase 0: 基础设施

| ID | 标题 | 描述 | 优先级 | 影响文件 | 依赖 |
|---|---|---|---|---|---|
| V3-00 | 创建 Workflow 常量与映射模块 | 新建 `frontend/src/constants/workflow.ts`，定义 WORKFLOW_STEPS、STATUS_STEP_MAP、getWorkflowStep()、getStepLabel()、getStatusTagClass() 等工具函数 | P0 | `frontend/src/constants/workflow.ts` (新) | 无 |
| V3-01 | 扩展 CaseStatus 枚举 | 在 `backend/app/modules/cases/enums.py` 添加 V3 所需的法律状态值 | P0 | `backend/app/modules/cases/enums.py` | 无 |

### Phase 1: 后端 API 增强

| ID | 标题 | 描述 | 优先级 | 影响文件 | 依赖 |
|---|---|---|---|---|---|
| V3-02 | 丰富 GET /cases/{id} 返回字段 | 补充 title_cn, title_en, status, filing_date, recv_date, app_no, client_name, applicants, inventors, priorities, created_at, updated_at | P0 | `backend/app/modules/cases/api.py` | V3-01 |
| V3-03 | 丰富 GET /cases 列表返回字段 | 在列表 items 中补充 filing_date, recv_date, title_en | P0 | `backend/app/modules/cases/api.py` | V3-01 |
| V3-04 | 更新种子数据 | 在 seed_dev.py 中添加包含 V3 法律状态的案件数据，覆盖所有 13 种状态 | P1 | `backend/scripts/seed_dev.py` | V3-01 |

### Phase 2: 前端 API 层更新

| ID | 标题 | 描述 | 优先级 | 影响文件 | 依赖 |
|---|---|---|---|---|---|
| V3-05 | 更新 Case 类型定义 | 在 cases.types.ts 中补充 workflow 相关字段（recv_date 等）；更新 BackendCase 和 mapCase | P0 | `frontend/src/api/cases.types.ts`, `frontend/src/api/cases.ts` | V3-02, V3-03 |
| V3-06 | 新增 Dashboard workflow API | 在 dashboard.api.ts 中新增 fetchWorkflowStats() 函数，获取全量 cases 并按 workflow step 分组统计 | P0 | `frontend/src/modules/dashboard/dashboard.api.ts` | V3-00, V3-05 |

### Phase 3: Dashboard 增强

| ID | 标题 | 描述 | 优先级 | 影响文件 | 依赖 |
|---|---|---|---|---|---|
| V3-07 | 实现 WorkflowOverview 组件 | 5 阶段卡片 (wf-card)，显示数量 + 占比，可点击跳转 CaseList | P0 | `frontend/src/modules/dashboard/components/WorkflowOverview.vue` (新) | V3-00, V3-06 |
| V3-08 | 实现 WorkflowCaseTable 组件 | Dashboard 内嵌阶段案件表格，支持按阶段筛选 | P0 | `frontend/src/modules/dashboard/components/WorkflowCaseTable.vue` (新) | V3-00, V3-06 |
| V3-09 | 集成 Dashboard 主页面 | 在 Dashboard.vue 中集成 WorkflowOverview + WorkflowCaseTable，调整布局为 split-grid（左：案件表，右：财务面板） | P0 | `frontend/src/modules/dashboard/pages/Dashboard.vue` | V3-07, V3-08 |

### Phase 4: CaseList 增强

| ID | 标题 | 描述 | 优先级 | 影响文件 | 依赖 |
|---|---|---|---|---|---|
| V3-10 | CaseList 阶段筛选支持 | 接收 route query `?step=SUB_EXAM`，过滤显示；添加"当前步骤"列；筛选说明标题；"清除阶段筛选"按钮 | P0 | `frontend/src/modules/cases/pages/CaseList.vue` | V3-00, V3-05 |

### Phase 5: CaseDetail 增强

| ID | 标题 | 描述 | 优先级 | 影响文件 | 依赖 |
|---|---|---|---|---|---|
| V3-11 | 实现 CaseStepper 组件 | 5 步可视化进度条 + KPI 4 卡（当前步骤、步骤序号、法律状态、下一动作）+ 分支状态警告 | P0 | `frontend/src/modules/cases/components/CaseStepper.vue` (新) | V3-00 |
| V3-12 | 实现 CaseDeadlineCard 组件 | 绝限提醒卡片，显示最近 deadline 日期和剩余天数 | P1 | `frontend/src/modules/cases/components/CaseDeadlineCard.vue` (新) | 无 |
| V3-13 | 实现 CaseRelatedTasks 组件 | 关联任务列表（从 tasks API 按 case_id 获取） | P1 | `frontend/src/modules/cases/components/CaseRelatedTasks.vue` (新) | 无 |
| V3-14 | 集成 CaseDetail 页面 | 在 CaseDetail.vue 概览 tab 中集成 CaseStepper；添加右侧面板 (CaseDeadlineCard + CaseRelatedTasks)；调整布局为 case-detail-container grid | P0 | `frontend/src/modules/cases/pages/CaseDetail.vue` | V3-11, V3-12, V3-13 |

### Phase 6: 导航与样式

| ID | 标题 | 描述 | 优先级 | 影响文件 | 依赖 |
|---|---|---|---|---|---|
| V3-15 | 重构 Sidebar 导航分组 | 修改 menu.ts 为 V3 规范要求的分组：总览 / 业务实体 (客户/案件/案件详情) / 财务 (费用&账单/回款&核销) | P1 | `frontend/src/constants/menu.ts` | 无 |
| V3-16 | 集成 v3_styles.css | 将 V3 样式拆解为主题变量和组件样式，集成到现有样式系统中（workflow.css, stepper.css）；不覆盖全局 Element Plus 样式 | P1 | `frontend/src/styles/workflow.css` (新), `frontend/src/styles/stepper.css` (新), `frontend/src/main.ts` | 无 |
| V3-17 | 更新 labels.zh.ts | 添加 V3 相关的中文标签（workflow 阶段名、KPI 标签等） | P1 | `frontend/src/constants/labels.zh.ts` | 无 |

### Phase 7: 响应式 & 收尾

| ID | 标题 | 描述 | 优先级 | 影响文件 | 依赖 |
|---|---|---|---|---|---|
| V3-18 | 响应式断点处理 | 确保 <=1260px 和 <=780px 断点下布局正常降级 | P1 | `frontend/src/styles/workflow.css`, 各新增组件 | V3-16 |
| V3-19 | 交互流端到端验证 | 验证 Dashboard → CaseList → CaseDetail → 返回 的完整链路 | P0 | 无代码变更，测试验证 | V3-09, V3-10, V3-14 |

---

## 4. 优先序与依赖关系图

### 4.1 执行顺序

```
Phase 0 (基础) ─── V3-00 (workflow.ts)
                └── V3-01 (CaseStatus enum)
                         │
Phase 1 (后端) ─── V3-02 (GET /cases/{id}) ──┐
                └── V3-03 (GET /cases list) ──┤
                └── V3-04 (seed data)          │
                                               │
Phase 2 (API 层) ── V3-05 (types) ────────────┤
                 └── V3-06 (dashboard API) ────┤
                                               │
Phase 3 (Dashboard) ── V3-07 (WorkflowOverview) ─┐
                    └── V3-08 (WorkflowTable)  ───┤
                    └── V3-09 (Dashboard 集成) ────┤
                                                   │
Phase 4 (CaseList) ── V3-10 (筛选增强) ───────────┤
                                                   │
Phase 5 (Detail) ── V3-11 (CaseStepper)           │
                 └── V3-12 (DeadlineCard)          │
                 └── V3-13 (RelatedTasks)          │
                 └── V3-14 (Detail 集成) ──────────┤
                                                   │
Phase 6 (导航/样式) ── V3-15 (Sidebar)             │
                    └── V3-16 (CSS 集成)           │
                    └── V3-17 (labels)             │
                                                   │
Phase 7 (收尾) ── V3-18 (响应式) ─────────────────┤
               └── V3-19 (E2E 验证) ──────────────┘
```

### 4.2 依赖关系表

| 任务 | 前置依赖 |
|---|---|
| V3-00 | 无 |
| V3-01 | 无 |
| V3-02 | V3-01 |
| V3-03 | V3-01 |
| V3-04 | V3-01 |
| V3-05 | V3-02, V3-03 |
| V3-06 | V3-00, V3-05 |
| V3-07 | V3-00, V3-06 |
| V3-08 | V3-00, V3-06 |
| V3-09 | V3-07, V3-08 |
| V3-10 | V3-00, V3-05 |
| V3-11 | V3-00 |
| V3-12 | 无 |
| V3-13 | 无 |
| V3-14 | V3-11, V3-12, V3-13 |
| V3-15 | 无 |
| V3-16 | 无 |
| V3-17 | 无 |
| V3-18 | V3-16 |
| V3-19 | V3-09, V3-10, V3-14 |

### 4.3 并行化建议

以下任务组可并行执行：
- **并行组 1**: V3-00 + V3-01 + V3-15 + V3-16 + V3-17（无依赖基础任务）
- **并行组 2**: V3-02 + V3-03 + V3-04（后端改造，均只依赖 V3-01）
- **并行组 3**: V3-11 + V3-12 + V3-13（Detail 组件，互不依赖）
- **并行组 4**: V3-07 + V3-08 + V3-10（页面增强，均依赖 V3-05/V3-06）

---

## 5. API Contract 草稿

### 5.1 修改: GET /api/v1/cases/{case_id}

**当前返回**:
```json
{
  "id": "uuid",
  "case_no": "P2310-001",
  "case_type": "NORMAL",
  "patent_category": "INV",
  "flow_dir": "CN_DOMESTIC",
  "client_id": "uuid"
}
```

**修改后返回**:
```json
{
  "id": "uuid",
  "case_no": "P2310-001",
  "case_type": "NORMAL",
  "patent_category": "INV",
  "flow_dir": "CN_DOMESTIC",
  "client_id": "uuid",
  "client_name": "蔚来汽车",
  "title_cn": "智能充电桩控制方法",
  "title_en": null,
  "app_no": "202410012345.6",
  "status": "WAITING_RECEIPT",
  "filing_date": "2024-01-18",
  "recv_date": "2024-01-15",
  "applicants": [],
  "inventors": [],
  "priorities": [],
  "created_at": "2024-01-15T10:00:00",
  "updated_at": "2024-01-15T10:00:00"
}
```

**兼容性**: 纯增量字段，不改变现有字段含义。现有前端消费方不受影响。

### 5.2 修改: GET /api/v1/cases (列表)

**在 items 中新增字段**:
```json
{
  "items": [
    {
      "id": "uuid",
      "case_no": "P2310-001",
      "case_type": "NORMAL",
      "patent_category": "INV",
      "client_id": "uuid",
      "client_name": "蔚来汽车",
      "title_cn": "智能充电桩控制方法",
      "status": "WAITING_RECEIPT",
      "filing_date": "2024-01-18",
      "recv_date": "2024-01-15"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 12
}
```

**兼容性**: 增量字段，无破坏性变更。

### 5.3 可选新增: GET /api/v1/cases/workflow-stats

> **MVP 阶段不实现**，前端本地计算。预留接口设计供后续迭代。

```
GET /api/v1/cases/workflow-stats
Authorization: Bearer <token>

Response 200:
{
  "steps": [
    { "key": "ACCEPTED", "label": "受理", "count": 2, "percent": 17 },
    { "key": "PRELIM", "label": "初审", "count": 2, "percent": 17 },
    { "key": "PUBLISHED", "label": "公布", "count": 2, "percent": 17 },
    { "key": "SUB_EXAM", "label": "实审", "count": 4, "percent": 33 },
    { "key": "GRANTED", "label": "授权", "count": 2, "percent": 17 }
  ],
  "total": 12
}
```

---

## 6. 前端组件架构

### 6.1 新增组件列表

| 组件 | 路径 | 职责 |
|---|---|---|
| `WorkflowOverview.vue` | `modules/dashboard/components/` | Dashboard 5 阶段统计卡片 + "查看全部"按钮 |
| `WorkflowCaseTable.vue` | `modules/dashboard/components/` | Dashboard 内嵌阶段案件表格 |
| `CaseStepper.vue` | `modules/cases/components/` | 5 步可视化进度条 + KPI 卡片 + 分支告警 |
| `CaseDeadlineCard.vue` | `modules/cases/components/` | 绝限提醒卡片 |
| `CaseRelatedTasks.vue` | `modules/cases/components/` | 关联任务列表 |

### 6.2 新增常量/工具模块

| 模块 | 路径 | 职责 |
|---|---|---|
| `workflow.ts` | `constants/` | Workflow Step 定义、状态映射、计算函数 |

### 6.3 现有组件修改计划

| 组件 | 修改内容 |
|---|---|
| `Dashboard.vue` | 新增 WorkflowOverview 区域；调整 split-grid 布局为左 (WorkflowCaseTable) + 右 (FinancePanel) |
| `CaseList.vue` | 添加 route query 筛选支持、步骤列、筛选说明、清除按钮 |
| `CaseDetail.vue` | 在概览 tab 顶部集成 CaseStepper；添加右侧面板；使用 grid 布局 |
| `SidebarNav.vue` | 无需修改（由 menu.ts 驱动） |
| `menu.ts` | 重构分组结构以匹配 V3 规范 |
| `labels.zh.ts` | 新增 workflow、stepper、deadline 相关中文标签 |

### 6.4 状态管理方案

**不需要新的 Pinia store**。原因：
- Workflow 统计数据由 Dashboard 组件本地管理（生命周期内有效）
- 阶段筛选条件通过 Vue Router query params 传递（`?step=SUB_EXAM`）
- Stepper 计算是纯函数（status → step），无需状态持久化

### 6.5 路由变更

无新路由需要添加。变更点：
- CaseList 路由支持 query param: `?step=ACCEPTED` 等
- 路由跳转方式：Dashboard WorkflowOverview 点击 → `router.push({ path: '/cases', query: { step: 'SUB_EXAM' } })`

---

## 7. 样式集成策略

### 7.1 v3_styles.css 集成方式

**策略**: 拆分提取，不全量导入。

v3_styles.css 包含完整的全局重置（`* { margin: 0; padding: 0 }`）和布局覆盖，直接导入会与 Element Plus 冲突。

**拆分为**:
1. **`workflow.css`** — 提取 workflow-overview、wf-card、wf-topline、wf-title、wf-count、wf-hint、workflow-grid、summary-note 等 Dashboard 特定样式
2. **`stepper.css`** — 提取 stepper、step、step.done、step.active、flow-state-card、kpi-box、kpi-label、kpi-value、alert-note、deadline-card 等 Detail 特定样式
3. **CSS 变量映射** — v3_styles.css 的 `:root` 变量已在 `variables.css` 中有对应别名，无需重复定义

### 7.2 与 Element Plus 主题协调

| v3 变量 | Element Plus 变量 | 处理 |
|---|---|---|
| `--primary` | `--el-color-primary` | variables.css 已映射 |
| `--bg-body` | `--el-bg-color` | 已兼容 |
| `--border` | `--el-border-color` | 已兼容 |
| `--text-main` | — | 通过 `base.css` 定义 |
| `--text-sub` | — | 通过 `base.css` 定义 |
| `--radius` | `--el-border-radius-base` | v3 使用 6px，与项目一致 |

**原则**: V3 组件使用自定义 class（如 `.wf-card`, `.stepper`, `.step`），不使用 Element Plus 组件，因此不会冲突。仅需确保 CSS 变量正确引用。

### 7.3 响应式断点处理

遵循 V3 规范的两个断点：

```css
/* <= 1260px: 多栏降级 */
@media (max-width: 1260px) {
  .workflow-grid { grid-template-columns: repeat(3, 1fr); }
  .split-grid { grid-template-columns: 1fr; }
  .case-detail-container { grid-template-columns: 1fr; }
  .flow-state-card { grid-template-columns: repeat(2, 1fr); }
}

/* <= 780px: 窄屏布局 */
@media (max-width: 780px) {
  .workflow-grid { grid-template-columns: repeat(2, 1fr); }
  .stepper { grid-template-columns: 1fr; }
}
```

现有 `pipeline.css` 已有 `@media (max-width: 1100px)` 断点，需与 V3 的 1260px 协调——统一为 1260px。

---

## 8. 测试策略

### 8.1 后端 API 测试

| 测试场景 | 文件 | 断言 |
|---|---|---|
| GET /cases/{id} 返回完整字段 | `tests/test_cases.py` | 验证 title_cn, status, filing_date, client_name 等 |
| GET /cases 列表包含新字段 | `tests/test_cases.py` | 验证 filing_date 在 items 中 |
| CaseStatus 枚举扩展 | `tests/test_cases.py` | 创建含 V3 状态的 case 并验证 |
| Seed data 正确性 | `tests/test_seed.py` | 运行 seed，验证各状态案件存在 |

### 8.2 前端组件测试要点

| 组件 | 测试要点 |
|---|---|
| `workflow.ts` | getWorkflowStep() 对所有 13 种状态返回正确 step；未知状态默认受理 |
| `WorkflowOverview.vue` | 渲染 5 张卡片；点击触发 emit；selected 状态正确 |
| `CaseStepper.vue` | 各状态下 done/active/未到达 class 正确；分支状态显示警告 |
| `CaseList.vue` | query 参数筛选生效；清除筛选后恢复全部 |

### 8.3 E2E 测试场景

| 场景 | 步骤 |
|---|---|
| 主流程导航 | Dashboard → 点击"实审"卡 → CaseList 显示筛选 → 点击案件行 → CaseDetail 显示 Stepper |
| 清除筛选 | CaseList 点击"清除阶段筛选" → 恢复显示全部案件 |
| 返回链路 | CaseDetail → 返回案件列表 → 返回仪表盘，确保每步可用 |
| 分支状态 | 打开 REJECTED 案件 → 验证分支警告显示 |
| 响应式 | 窗口缩小到 780px → 验证 workflow-grid 和 stepper 降级 |

### 8.4 种子数据要求

需确保 seed_dev.py 中包含以下状态的案件各至少 1 条：
`WAITING_RECEIPT`, `PRELIM_EXAM`, `PRELIM_PASS`, `AMENDMENT`, `PUBLISHED`, `SUB_EXAM`, `OA1`, `OA2`, `REEXAM`, `GRANTED`, `REJECTED`, `TERMINATED`, `INVALIDATED`

---

## 9. 验收清单（DoD）

### 9.1 V3 规范 DoD（直接引用）

- [ ] 左侧导航保留 `业务实体` 与 `财务` 分区结构
- [ ] Dashboard 有 5 阶段 Stepper 统计卡，支持点击筛选
- [ ] Dashboard 保留"财务状况"面板
- [ ] UI 中没有"业务状态映射（UI + 业务层）"展示区
- [ ] Case Detail 显示 `第N步 / 5`
- [ ] 列表/详情/总览的跳转与返回链路可用
- [ ] 移动端与窄屏不破版

### 9.2 补充技术验收项

- [ ] `workflow.ts` 单元测试覆盖所有 13 种状态映射
- [ ] 后端 GET /cases/{id} 返回 title_cn, status, filing_date, client_name
- [ ] 后端 GET /cases 列表返回 filing_date, recv_date
- [ ] CaseStatus 枚举包含所有 V3 所需状态值
- [ ] seed_dev.py 包含 13 种状态的测试案件
- [ ] CaseStepper 组件正确显示 done/active/未到达三态
- [ ] 分支状态（REJECTED/TERMINATED/INVALIDATED）显示黄色警告
- [ ] Dashboard WorkflowOverview 点击阶段卡正确跳转并传递 query param
- [ ] CaseList 正确接收 `?step=` 参数并筛选显示
- [ ] CaseList 标题显示筛选说明（如 `案件列表 · 实审`）
- [ ] "清除阶段筛选"按钮在 CaseList 和 Dashboard 均可用
- [ ] `npm run lint && npm run typecheck && npm run build` 全部通过
- [ ] `ruff check --fix . && ruff format .` 后端无 lint 错误
- [ ] `pytest -q` 后端测试全部通过
- [ ] 所有 UI 文字使用简体中文
- [ ] 前端不使用 `@/` 路径别名
- [ ] v3_styles.css 视觉效果与原型一致（不需要像素完美，但视觉风格匹配）
- [ ] 1260px 和 780px 两个断点均正常降级

---

## 附录 A: workflow.ts 核心设计

```typescript
// frontend/src/constants/workflow.ts

export interface WorkflowStep {
  key: string
  label: string
  color: string
}

export const WORKFLOW_STEPS: WorkflowStep[] = [
  { key: 'ACCEPTED', label: '受理', color: '#2563eb' },
  { key: 'PRELIM', label: '初审', color: '#f59e0b' },
  { key: 'PUBLISHED', label: '公布', color: '#8b5cf6' },
  { key: 'SUB_EXAM', label: '实审', color: '#1d4ed8' },
  { key: 'GRANTED', label: '授权', color: '#10b981' },
]

export interface StatusRule {
  stepKey: string
  legalText: string
  stepText: string
  nextAction: string
  branchNote?: string
}

export const STATUS_STEP_MAP: Record<string, StatusRule> = {
  WAITING_RECEIPT: { stepKey: 'ACCEPTED', legalText: 'WAITING_RECEIPT', stepText: '受理', nextAction: '收到受理通知后进入初审节点。' },
  PRELIM_EXAM: { stepKey: 'PRELIM', legalText: 'PRELIM_EXAM', stepText: '初审', nextAction: '初审通过后进入公布节点。' },
  PRELIM_PASS: { stepKey: 'PRELIM', legalText: 'PRELIM_PASS', stepText: '初审', nextAction: '完成公开手续后进入公布节点。' },
  AMENDMENT: { stepKey: 'PRELIM', legalText: 'AMENDMENT', stepText: '初审', nextAction: '补正完成后回到初审并推进公开。' },
  PUBLISHED: { stepKey: 'PUBLISHED', legalText: 'PUBLISHED', stepText: '公布', nextAction: '进入实审流程（可能经历 OA 往返）。' },
  SUB_EXAM: { stepKey: 'SUB_EXAM', legalText: 'SUB_EXAM', stepText: '实审', nextAction: '实审通过后录入授权通知进入授权。' },
  OA1: { stepKey: 'SUB_EXAM', legalText: 'OA1', stepText: '实审', nextAction: '提交 OA 答复后回到实审。' },
  OA2: { stepKey: 'SUB_EXAM', legalText: 'OA2', stepText: '实审', nextAction: '继续答复审查意见，满足条件后可授权。' },
  REEXAM: { stepKey: 'SUB_EXAM', legalText: 'REEXAM', stepText: '实审', nextAction: '复审结果决定是否转入授权或驳回。' },
  GRANTED: { stepKey: 'GRANTED', legalText: 'GRANTED', stepText: '授权', nextAction: '进入授权后费用和年费管理。' },
  REJECTED: { stepKey: 'SUB_EXAM', legalText: 'REJECTED', stepText: '实审', nextAction: '可按策略进入复审或结案。', branchNote: '该案已进入分支状态：驳回。主干 Stepper 停留在第4步（实审），未进入"授权"。' },
  TERMINATED: { stepKey: 'GRANTED', legalText: 'TERMINATED', stepText: '授权', nextAction: '检查年费/恢复权利策略。', branchNote: '该案已进入分支状态：终止。主干 Stepper 保留"授权"历史位置。' },
  INVALIDATED: { stepKey: 'GRANTED', legalText: 'INVALIDATED', stepText: '授权', nextAction: '查看无效决定文书并评估后续动作。', branchNote: '该案已进入分支状态：无效。主干 Stepper 保留"授权"历史位置。' },
}

/** 兼容现有 CaseStatus 枚举的默认映射（NOT_FILED → 受理） */
const DEFAULT_RULE: StatusRule = {
  stepKey: 'ACCEPTED',
  legalText: 'UNKNOWN',
  stepText: '受理',
  nextAction: '请更新案件法律状态。',
}

export function getStatusRule(status: string | undefined): StatusRule {
  if (!status) return DEFAULT_RULE
  return STATUS_STEP_MAP[status] || { ...DEFAULT_RULE, legalText: status }
}

export function getStepIndex(stepKey: string): number {
  const idx = WORKFLOW_STEPS.findIndex(s => s.key === stepKey)
  return idx >= 0 ? idx : 0
}

export function getCaseWorkflow(status: string | undefined) {
  const rule = getStatusRule(status)
  const stepIndex = getStepIndex(rule.stepKey)
  return {
    rule,
    stepIndex,
    stepLabel: WORKFLOW_STEPS[stepIndex].label,
    stepNoText: `第${stepIndex + 1}步/5`,
  }
}

export function getStatusTagClass(status: string): string {
  if (status === 'GRANTED') return 'green'
  if (status === 'WAITING_RECEIPT') return 'blue'
  if (['PRELIM_EXAM', 'PRELIM_PASS', 'AMENDMENT'].includes(status)) return 'orange'
  if (status === 'PUBLISHED') return 'indigo'
  if (['SUB_EXAM', 'OA1', 'OA2', 'REEXAM'].includes(status)) return 'blue'
  if (['REJECTED', 'INVALIDATED'].includes(status)) return 'red'
  if (status === 'TERMINATED') return 'gray'
  return 'gray'
}
```

---

## 附录 B: menu.ts V3 分组结构

```typescript
export const MENU_GROUPS: MenuGroup[] = [
  {
    key: 'top',
    label: '',
    children: [
      { key: 'dashboard', label: '总览 Dashboard', icon: '📊', route: '/dashboard' },
    ],
  },
  {
    key: 'entity',
    label: '业务实体 (Entity)',
    children: [
      { key: 'clients', label: '客户 Clients', icon: '👥', route: '/clients', requiredPerms: [Perms.CLIENTS_READ] },
      { key: 'cases', label: '案件 Cases', icon: '📂', route: '/cases', requiredPerms: [Perms.CASES_READ] },
      { key: 'tasks', label: '任务 & 期限', icon: '📅', route: '/tasks', requiredPerms: [Perms.TASKS_READ] },
    ],
  },
  {
    key: 'finance',
    label: '财务 (Finance)',
    children: [
      { key: 'fees', label: '费用 & 账单', icon: '💰', route: '/fees/drafts', requiredPerms: [Perms.FEES_READ] },
      { key: 'payments', label: '回款 & 核销', icon: '🧾', route: '/billing/payments', requiredPerms: [Perms.BILLING_READ] },
    ],
  },
  {
    key: 'settings',
    label: '系统设置',
    children: [
      { key: 'settings', label: '系统配置', icon: '⚙️', route: '/system/params', requiredPerms: [Perms.SETTINGS_READ] },
    ],
  },
]
```

---

*本文档由 Architect Agent 自动生成，待 Team Lead 和用户批准后方可执行。*
