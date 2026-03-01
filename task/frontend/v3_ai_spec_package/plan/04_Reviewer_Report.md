# FPMS V3 Case Workflow Stepper — 审查报告

> **版本**: 1.0
> **日期**: 2026-02-22
> **作者**: Reviewer Agent
> **状态**: 完成

---

## 1. 总体评价

### 结论：✅ 有条件通过

V3 Case Workflow Stepper 的实现整体质量良好，所有 DoD 验收项均已满足。代码结构清晰，前后端协作一致，状态映射逻辑集中管理（`workflow.ts`），种子数据覆盖了全部 13 种法律状态。

质量门禁结果：
- `npm run lint`: ✅ 0 errors, 0 warnings
- `npm run typecheck`: ✅ 通过
- `npm run build`: ✅ 2.91s 构建成功
- `ruff check .`: ✅ 0 remaining errors
- `pytest -q`: ✅ 34 passed (含 29 条 V3 测试)

### 通过条件

需修复以下 Major 级别问题后方可正式发布：
1. CaseListItem / CaseDetail Pydantic schema 需与 API 实际返回字段对齐
2. WorkflowCaseTable 硬编码 step label 应改用 WORKFLOW_STEPS 常量

---

## 2. 各维度评分

| 维度 | 评分 | 说明 |
|---|---|---|
| V3 规范符合度 | ⭐⭐⭐⭐⭐ 5/5 | DoD 7 项全部满足，交互流程完整 |
| 代码质量与最佳实践 | ⭐⭐⭐⭐ 4/5 | 整体良好，Pydantic schema 未同步更新，存在少量硬编码 |
| 安全性 | ⭐⭐⭐⭐⭐ 5/5 | 权限检查一致，无 XSS/SQL 注入风险 |
| 性能 | ⭐⭐⭐⭐ 4/5 | MVP 可接受，`page_size=200` 全量拉取需后续优化 |
| 一致性 | ⭐⭐⭐⭐ 4/5 | 与既有代码风格一致，相对路径正确，个别 schema 不同步 |
| 无障碍 (a11y) | ⭐⭐⭐ 3/5 | 缺少 ARIA 属性和语义化标签，点击目标可达但键盘支持有限 |

---

## 3. DoD 验收结果

| # | 验收项 | 结果 | 说明 |
|---|---|---|---|
| 1 | 左侧导航保留 `业务实体` 与 `财务` 分区结构 | ✅ | `menu.ts` 分组：`entity`（业务实体 Entity）+ `finance`（财务 Finance） |
| 2 | Dashboard 有 5 阶段 Stepper 统计卡，支持点击筛选 | ✅ | `WorkflowOverview.vue` 渲染 5 个 `.wf-card`，click→`emit('select')` |
| 3 | Dashboard 保留"财务状况"面板 | ✅ | `FinancePanel` 在 `split-grid` 右侧保留 |
| 4 | UI 中没有"业务状态映射（UI + 业务层）"展示区 | ✅ | 映射逻辑仅在 `workflow.ts` 代码层，UI 无展示面板 |
| 5 | Case Detail 显示 `第N步 / 5` | ✅ | `CaseStepper.vue` 显示 `stepNoText`（如"第4步/5"）+ KPI 4 卡 |
| 6 | 列表/详情/总览的跳转与返回链路可用 | ✅ | Dashboard→CaseList（query param）→CaseDetail→返回（goBack） |
| 7 | 移动端与窄屏不破版 | ✅ | `workflow.css` 和 `stepper.css` 均有 1260px/780px 两个断点 |

---

## 4. 发现的问题

### 4.1 Critical（无）

无 Critical 级别问题。

### 4.2 Major

#### M-1: `CaseListItem` Pydantic schema 缺少字段

**文件**: `backend/app/modules/cases/schemas.py:86-95`

**问题**: `CaseListItem` schema 缺少 `filing_date`, `recv_date`, `client_name` 字段，与 API 实际返回不一致。虽然当前 API 直接返回 dict（未使用 response_model），不影响运行时，但 schema 作为文档和类型契约应保持同步。

**建议修复**:
```python
class CaseListItem(BaseModel):
    id: str
    case_no: str
    case_type: str
    patent_category: str
    client_id: str | None
    client_name: str | None = None   # 新增
    title_cn: str | None
    title_en: str | None
    status: str
    filing_date: str | None = None   # 新增
    recv_date: str | None = None     # 新增
```

#### M-2: WorkflowCaseTable 硬编码阶段标签

**文件**: `frontend/src/modules/dashboard/components/WorkflowCaseTable.vue:70`

**问题**: `panelTitle` 计算属性内硬编码了 `{ ACCEPTED: '受理', PRELIM: '初审', ... }` 映射，应复用 `WORKFLOW_STEPS` 常量避免不一致。

**建议修复**:
```typescript
import { WORKFLOW_STEPS } from '../../../constants/workflow'

const panelTitle = computed(() => {
  if (props.selectedStep) {
    const step = WORKFLOW_STEPS.find(s => s.key === props.selectedStep)
    const name = step?.label || props.selectedStep
    return ZH.workflow.stageTitleFiltered.replace('{name}', name)
  }
  return ZH.workflow.stageTitleAll
})
```

#### M-3: `CaseDetail` Pydantic schema 字段类型不准确

**文件**: `backend/app/modules/cases/schemas.py:68-83`

**问题**: `CaseDetail` schema 的 `created_at` 和 `updated_at` 定义为 `str`（必填），但 API 可能返回 `null`。同时缺少 `filing_date`, `recv_date`, `client_name` 字段。

**建议修复**:
```python
class CaseDetail(BaseModel):
    # ... existing fields ...
    client_name: str | None = None   # 新增
    filing_date: str | None = None   # 新增
    recv_date: str | None = None     # 新增
    created_at: str | None = None    # 改为可选
    updated_at: str | None = None    # 改为可选
```

### 4.3 Minor

#### m-1: CaseDeadlineCard 和 CaseRelatedTasks 全量拉取任务

**文件**: `frontend/src/modules/cases/components/CaseDeadlineCard.vue:42`, `CaseRelatedTasks.vue:34`

**问题**: 两个组件均调用 `getTasks({ page: 1, page_size: 50, status: 'OPEN' })` 后在前端按 `case_id` 过滤。如果后端 tasks API 支持 `case_id` 参数，应改为服务端过滤以减少数据传输。

**影响**: MVP 数据量小，性能可接受。生产环境需优化。

#### m-2: CaseList 筛选时 page_size=200

**文件**: `frontend/src/modules/cases/pages/CaseList.vue:153`

**问题**: 当存在 `stepFilter` 时，`fetchCases` 使用 `page_size: 200` 全量拉取，然后前端过滤。大数据量下性能不佳。

**建议**: MVP 可接受。后续应增加后端 `workflow_step` 筛选参数或使用 `status` 多值过滤。

#### m-3: CaseDetail 页 inventor key 可能重复

**文件**: `frontend/src/modules/cases/pages/CaseDetail.vue:156`

**问题**: `v-for="inventor in caseData.inventors" :key="inventor"` — 当 `inventors` 是 string 数组时，如果有同名发明人，key 会重复。

**建议修复**: 使用 index 作为 key：
```html
<span v-for="(inventor, idx) in caseData.inventors" :key="idx" ...>
```

#### m-4: 前端 `getCases` 未传递后端支持的 `status` 参数

**文件**: `frontend/src/api/cases.ts:43-53`

**问题**: `getCases` 函数仅传递 `page` 和 `page_size` 参数，未支持后端已有的 `status`, `q`, `client_id` 等筛选参数。这导致 CaseList 的阶段筛选只能全量拉取后前端过滤。

**建议**: 扩展 `CaseListParams` 和 `getCases` 函数以支持更多查询参数。

#### m-5: `ilike` 使用注意

**文件**: `backend/app/modules/cases/api.py:60-63, 335-338`

**问题**: CLAUDE.md 明确要求"No PG-only functions (ILIKE)"。SQLAlchemy `.ilike()` 在 SQLite 上能工作（内部转换为 `LOWER(x) LIKE LOWER(?)`），但违反了文档约束。此为预存问题，非 V3 引入。

**建议**: 后续统一改为 `.contains()` 或 SQLAlchemy `func.lower()` 组合。

#### m-6: `export_cases` 与 `get_cases` 逻辑重复

**文件**: `backend/app/modules/cases/api.py:295-397`

**问题**: `export_cases` 端点几乎完全复制了 `get_cases` 的逻辑（筛选、排序、client name 解析）。此为预存问题，V3 改动未加剧。

**建议**: 后续提取公共函数。

### 4.4 Suggestion

#### S-1: 为 Stepper 添加 ARIA 属性

**文件**: `frontend/src/modules/cases/components/CaseStepper.vue`

**建议**: 增加无障碍语义：
```html
<div class="stepper" role="group" aria-label="案件流程步骤">
  <div
    v-for="(step, idx) in steps"
    :key="step.key"
    class="step"
    :class="stepClass(idx)"
    role="listitem"
    :aria-current="idx === flow.stepIndex ? 'step' : undefined"
  >
    {{ idx + 1 }}. {{ step.label }}
  </div>
</div>
```

#### S-2: 为 Workflow 卡片添加键盘可访问性

**文件**: `frontend/src/modules/dashboard/components/WorkflowOverview.vue`

**建议**: 为 `.wf-card` 添加 `role="button"`, `tabindex="0"`, `@keydown.enter`：
```html
<div
  v-for="step in steps"
  :key="step.key"
  class="wf-card"
  :class="{ selected: selectedStep === step.key }"
  role="button"
  tabindex="0"
  :aria-pressed="selectedStep === step.key"
  @click="emit('select', step.key)"
  @keydown.enter="emit('select', step.key)"
>
```

#### S-3: 考虑使用语义化 HTML

**建议**: Stepper 可使用 `<ol>/<li>` 替代 `<div>` 以提升语义清晰度。WorkflowCaseTable 的 `<table>` 已使用语义化标签（良好）。

#### S-4: chunk 体积优化

**问题**: 构建警告 `index-C1xCav8N.js` 1073 kB 超过 500 kB。

**建议**: 后续可通过 `build.rollupOptions.output.manualChunks` 拆分 Element Plus 和 Vue 到独立 chunk。

---

## 5. 具体代码修改建议

### 5.1 后端

| 文件 | 行号 | 修改 | 优先级 |
|---|---|---|---|
| `schemas.py` | 86-95 | `CaseListItem` 补充 `filing_date`, `recv_date`, `client_name` 字段 | Major |
| `schemas.py` | 68-83 | `CaseDetail` 补充 `client_name`, `filing_date`, `recv_date`；`created_at`/`updated_at` 改为 Optional | Major |
| `api.py` | 60-63 | 预存问题：`.ilike()` 可后续统一替换为 `.contains()` | Minor |

### 5.2 前端

| 文件 | 行号 | 修改 | 优先级 |
|---|---|---|---|
| `WorkflowCaseTable.vue` | 70 | 消除硬编码映射，改用 `WORKFLOW_STEPS.find()` | Major |
| `CaseDetail.vue` | 156 | `v-for` key 改为 index | Minor |
| `cases.ts` | 43-53 | 扩展 `getCases` 参数以支持 `status` 等后端筛选 | Minor |
| `CaseStepper.vue` | 4 | 添加 `role="group"` + `aria-label` | Suggestion |
| `WorkflowOverview.vue` | 12-17 | 添加 `role="button"`, `tabindex="0"`, `@keydown.enter` | Suggestion |

---

## 6. 总结与建议

### 6.1 亮点

1. **状态映射逻辑集中管理** — `workflow.ts` 将所有 13 种法律状态到 5 步 Workflow 的映射集中在一处，包含完整的 `StatusRule`（含 `branchNote`），确保前端各组件一致。

2. **前后端协作良好** — API Contract 定义清晰，后端 `get_case` 和 `get_cases` 均通过 batch resolve 实现 `client_name`，避免 N+1 查询。

3. **测试覆盖全面** — 29 条后端测试覆盖枚举验证、字段验证、状态筛选和端到端流程，全部通过。

4. **种子数据完整** — `seed_dev.py` 覆盖全部 13 种 V3 法律状态，每条包含完整的客户、申请人、发明人关联。

5. **CSS 隔离良好** — V3 样式拆分为 `workflow.css` 和 `stepper.css`，使用自定义 class（`.wf-card`, `.step`），不覆盖 Element Plus 全局样式。

6. **响应式断点正确** — 两个断点（1260px / 780px）在 workflow 和 stepper CSS 中均有实现。

### 6.2 改进建议（按优先级）

| 优先级 | 建议 | 工作量 |
|---|---|---|
| P0 | 修复 M-2: WorkflowCaseTable 硬编码标签 | 5 min |
| P0 | 修复 M-1/M-3: 同步 Pydantic schemas | 15 min |
| P1 | 修复 m-3: inventor key 改用 index | 2 min |
| P1 | 修复 m-4: 扩展 getCases 参数 | 15 min |
| P2 | S-1/S-2: 增加 ARIA 属性 | 20 min |
| P2 | m-1: CaseDeadlineCard/CaseRelatedTasks 服务端过滤 | 30 min |
| P3 | S-4: Chunk 体积优化 | 30 min |

### 6.3 结论

V3 Case Workflow Stepper 的核心功能已完整实现，满足设计规范的全部 DoD 验收项。代码质量良好，安全性无风险。建议在修复 Major 级别的 schema 同步和硬编码问题后正式合并。Minor 和 Suggestion 级别问题可在后续迭代中逐步优化。

---

*本文档由 Reviewer Agent 自动生成。*
