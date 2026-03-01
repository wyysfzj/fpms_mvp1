# DEMO-UI 实施计划（修订版）

> 决策确认：只用 **style-b**（现代科技）| labels 放 `src/constants/labels.zh.ts` | Documents/Fees/Billing 归入"案件管理"分组
>
> 生成日期：2026-02-10

---

## 0. 总体架构

```
┌─────────────────────────────────────────────────────────┐
│  VITE_DEMO_UI=1 开关                                     │
│  ├── style-b 主题 CSS 变量覆盖 (demo-themes.css)          │
│  ├── 全站中文文案 (constants/labels.zh.ts)                │
│  ├── Dashboard 工作台 KPI + 待办                          │
│  └── 关系链卡片 + 面包屑                                  │
│                                                         │
│  保持不变：路由体系 / RBAC / API 层 / auth / stores        │
└─────────────────────────────────────────────────────────┘
```

**执行顺序**：DEMO-UI-00 → 01 → 02 → 03（串行依赖）

**每个任务结束时必须通过**：
```bash
cd frontend && npm run lint && npm run typecheck && npm run build
```

---

## DEMO-UI-00：Style-B 主题应用 + VITE_DEMO_UI 开关

### 目标
- 当 `VITE_DEMO_UI=1` 时，自动应用 `patent_ui.html` 的 style-b CSS 变量覆盖
- 不需要 DemoToolbar / 主题切换按钮（只用 style-b）
- body 上加 `style-b` class，与现有 `mode-immersive` class 互不干扰
- 刷新后保持（基于 env 变量，无需 localStorage 持久化主题选择）

### 文件允许列表

| 文件 | 操作 | 说明 |
|------|------|------|
| `frontend/.env.example` | 修改 | 新增 `VITE_DEMO_UI=1` 说明 |
| `frontend/src/styles/demo-themes.css` | **新建** | 从 `patent_ui.html` 提取 style-b CSS 变量块 + 组件覆写 |
| `frontend/src/stores/ui.ts` | 修改 | 新增 `demoUI` computed + `applyDemoTheme()` 方法 |
| `frontend/src/main.ts` | 修改 | import `demo-themes.css`；启动时调用 `applyDemoTheme()` |
| `frontend/index.html` | 修改 | 加载 Lato 字体（style-b 用 Inter 已有，但备用） |

### 实施细节

#### 1. 创建 `frontend/src/styles/demo-themes.css`

从 `reference/patent_ui.html` 行 129-166 提取 style-b 变量，映射到项目已用的 CSS 变量名：

```css
/* demo-themes.css — Style B: 现代科技 (Tech Efficiency) */
/* 仅在 VITE_DEMO_UI=1 时 body 加 style-b class 激活 */

body.style-b {
  /* 背景 */
  --bg-body: #F1F5F9;
  --bg-panel: #FFFFFF;          /* 映射自 --bg-card */
  --bg-sidebar: #FFFFFF;
  --sidebar-border: 1px solid #E2E8F0;

  /* 文字 */
  --text-primary: #1E293B;       /* 映射自 --text-main */
  --text-secondary: #94A3B8;     /* 映射自 --text-sub */
  --color-primary: #2563EB;      /* 映射自 --text-highlight, --btn-bg */

  /* 侧边栏 */
  --sidebar-text: #64748B;
  --sidebar-active-bg: #EFF6FF;
  --sidebar-active-text: #2563EB;

  /* 按钮 */
  --btn-bg: #2563EB;
  --btn-text: #fff;

  /* 字体 */
  --font-family: "Inter", sans-serif;
  --font-family-serif: "Inter", sans-serif;
  --font-num: "Inter", sans-serif;

  /* 圆角/阴影/间距 */
  --radius-card: 8px;
  --radius-btn: 6px;
  --shadow-card: none;
  --border-card: 1px solid #E2E8F0;
  --border-color: #F1F5F9;

  /* 布局密度 */
  --content-padding: 20px;
  --card-padding: 15px;
  --table-padding: 8px 12px;
}

/* style-b 组件覆写 */
body.style-b .el-tag { border-radius: 4px; }

/* 状态标签颜色 */
body.style-b .tag-urgent { background: #FEE2E2; color: #EF4444; }
body.style-b .tag-warning { background: #FFFBEB; color: #D97706; }
body.style-b .tag-normal { background: #ECFDF5; color: #059669; }
```

> **注意**：上面的变量名需要在实施时逐一与 `variables.css` + `layout.css` 中的实际引用做映射校对。
> `variables.css` 中的 base token **数值不修改**，style-b 覆盖通过 `body.style-b` 选择器优先级生效。

#### 2. 修改 `frontend/src/stores/ui.ts`

```typescript
// 新增
const DEMO_UI = import.meta.env.VITE_DEMO_UI === '1'

// 在 store 中新增
demoUI: DEMO_UI,

applyDemoTheme() {
  if (DEMO_UI) {
    document.body.classList.add('style-b')
  } else {
    document.body.classList.remove('style-b')
  }
}
```

在 store 初始化时自动调用 `applyDemoTheme()`。

#### 3. 修改 `frontend/src/main.ts`

```typescript
import './styles/demo-themes.css'
// 在 app mount 之后
const uiStore = useUIStore()
uiStore.applyDemoTheme()
```

#### 4. 修改 `frontend/.env.example`

```
VITE_API_BASE_URL=http://localhost:8000/api/v1
# 启用 Demo UI 模式（style-b 主题 + 中文 + 工作台 + 关系链）
# VITE_DEMO_UI=1
```

### 验证清单
- [ ] `VITE_DEMO_UI=1` 时 body 有 `style-b` class，整体配色变为蓝白扁平风
- [ ] `VITE_DEMO_UI` 不设或 `=0` 时，body 无 `style-b`，UI 与之前完全一致
- [ ] `variables.css` 文件内容未被修改
- [ ] 现有 work/immersive 模式切换不受影响

---

## DEMO-UI-01：全站核心中文化 + 导航对齐 patent_ui.html

### 目标
- 登录前后全站核心文案中文化（登录页/Header/侧边栏/按钮/空态）
- 侧边栏菜单命名与 `patent_ui.html` 对齐
- Element Plus 组件内置文案中文化（分页、日期选择器等）
- 保持 RBAC best-effort 逻辑不变

### 文件允许列表

| 文件 | 操作 | 说明 |
|------|------|------|
| `frontend/src/constants/labels.zh.ts` | **新建** | 集中管理全站中文文案 |
| `frontend/src/constants/menu.ts` | 修改 | 菜单标签中文化 + 分组重组 |
| `frontend/src/components/nav/SidebarNav.vue` | 修改 | 支持分组渲染 |
| `frontend/src/components/header/TopHeader.vue` | 修改 | 搜索/退出/面包屑中文化；demo模式显示标题+日期 |
| `frontend/src/modules/auth/pages/Login.vue` | 修改 | 登录页中文化 |
| `frontend/src/router/index.ts` | 修改 | route meta 加中文 title |
| `frontend/src/main.ts` | 修改 | Element Plus locale 切换 zh-CN |

### 实施细节

#### 1. 新建 `frontend/src/constants/labels.zh.ts`

```typescript
export const ZH = {
  app: {
    name: 'LegalFlow',
    subtitle: '专利案件管理系统',
  },
  login: {
    title: '登录',
    username: '用户名',
    password: '密码',
    submit: '登 录',
    error: '用户名或密码错误',
  },
  nav: {
    dashboard: '工作台',
    caseGroup: '案件管理',
    cases: '案件列表',
    documents: '文档管理',
    fees: '费用管理',
    billing: '账单管理',
    tasks: '期限监控',
    clientGroup: '客户中心',
    clients: '客户列表',
    settingsGroup: '系统设置',
    templates: '模板管理',
    letterheads: '信头管理',
    systemParams: '系统参数',
    feeRates: '费率设置',
  },
  header: {
    searchPlaceholder: '搜索案件、客户...',
    logout: '退出登录',
    userMenu: '用户',
  },
  dashboard: {
    title: '工作台',
    date: '今日',
  },
  common: {
    create: '新建',
    edit: '编辑',
    delete: '删除',
    save: '保存',
    cancel: '取消',
    back: '返回',
    loading: '加载中...',
    empty: '暂无数据',
    confirm: '确认',
    search: '搜索',
    actions: '操作',
    status: '状态',
  },
  status: {
    urgent: '绝限警告',
    warning: '待答复',
    normal: '进行中',
    done: '已完成',
    cancelled: '已取消',
  },
} as const
```

#### 2. 修改 `frontend/src/constants/menu.ts` — 菜单分组重组

```typescript
// 新的 MenuItem interface 增加 group 和 children 支持
export interface MenuGroup {
  key: string
  label: string           // 中文分组标题
  children: MenuItem[]
}

export interface MenuItem {
  key: string
  label: string           // 中文
  icon: string
  route: string
  requiredPerms?: string[]
  bottom?: boolean
}

export const MENU_GROUPS: MenuGroup[] = [
  {
    key: 'top',
    label: '',              // 无分组标题
    children: [
      { key: 'dashboard', label: '工作台', icon: '📊', route: '/dashboard' },
    ],
  },
  {
    key: 'case-mgmt',
    label: '案件管理',
    children: [
      { key: 'cases', label: '案件列表', icon: '📂', route: '/cases', requiredPerms: ['cases:read'] },
      { key: 'documents', label: '文档管理', icon: '📄', route: '/documents', requiredPerms: ['documents:read'] },
      { key: 'fees', label: '费用管理', icon: '💰', route: '/fees/drafts', requiredPerms: ['fees:read'] },
      { key: 'billing', label: '账单管理', icon: '🧾', route: '/billing/bills', requiredPerms: ['billing:read'] },
    ],
  },
  {
    key: 'deadline',
    label: '期限监控',
    children: [
      { key: 'tasks', label: '任务列表', icon: '📅', route: '/tasks', requiredPerms: ['tasks:read'] },
    ],
  },
  {
    key: 'client-center',
    label: '客户中心',
    children: [
      { key: 'clients', label: '客户列表', icon: '👥', route: '/clients', requiredPerms: ['clients:read'] },
    ],
  },
  {
    key: 'settings',
    label: '系统设置',
    children: [
      { key: 'settings', label: '系统配置', icon: '⚙️', route: '/system/params', requiredPerms: ['settings:read'] },
    ],
  },
]
```

> **兼容**：保留原 `MENU_ITEMS` 导出（flatten 版本），避免其他文件 import 报错。

#### 3. 修改 `SidebarNav.vue` — 分组渲染

当前是扁平 `v-for` 渲染 `MENU_ITEMS`。改为遍历 `MENU_GROUPS`，每组渲染分组标题（小字灰色）+ 子项列表。仅增加分组标题的 `<div class="menu-group-label">` 渲染，不改底层 `<router-link>` 逻辑。

权限过滤逻辑保持：如果一个分组下所有子项都被隐藏，则整个分组标题也隐藏。

#### 4. 修改 `TopHeader.vue`

- `Search` placeholder → `ZH.header.searchPlaceholder`
- `Logout` → `ZH.header.logout`
- 面包屑从 route name 生成时，使用中文 route meta title
- Demo 模式下（`VITE_DEMO_UI=1`）：左侧显示页面标题 + 当前日期（对齐 patent_ui header 风格）

#### 5. 修改 `Login.vue`

- 标题、用户名 label、密码 label、登录按钮 → 引用 `ZH.login.*`

#### 6. 修改 `router/index.ts`

- 每个 route 的 `meta` 加 `title` 字段（中文），例如：
  ```typescript
  { path: '/cases', meta: { title: '案件列表', requiresAuth: true, ... } }
  ```

#### 7. 修改 `main.ts` — Element Plus 中文 locale

```typescript
import zhCn from 'element-plus/es/locale/lang/zh-cn'
// ...
app.use(ElementPlus, { locale: zhCn })
```

### 验证清单
- [ ] 登录页全中文（标题/输入框 label/按钮）
- [ ] 登录后侧边栏分组：工作台 / 案件管理(4项) / 期限监控 / 客户中心 / 系统设置
- [ ] Header 搜索框 placeholder 中文、退出按钮中文
- [ ] 面包屑显示中文
- [ ] 无 "Dashboard"、"Search"、"Logout"、"Settings" 等英文泄漏
- [ ] 权限未知时菜单不隐藏；权限已知时 best-effort 隐藏
- [ ] Element Plus 分页组件显示"共 X 条"等中文

---

## DEMO-UI-02：Dashboard 工作台对齐 patent_ui.html

### 目标
- Dashboard 结构：标题+日期 → KPI 卡片(4~6) → 待办表格 → 状态标签
- KPI 至少 2 个来自真实 API（clients total / cases total / tasks total 等）
- 待办表格使用真实任务数据（利用已有 `due_from`/`due_to` 后端筛选参数）
- 必须适配 style-b 主题（使用 CSS 变量，不写死颜色）

### 文件允许列表

| 文件 | 操作 | 说明 |
|------|------|------|
| `frontend/src/modules/dashboard/pages/Dashboard.vue` | 重写 | 替换 smoke test |
| `frontend/src/modules/dashboard/components/KpiCard.vue` | **新建** | KPI 卡片组件 |
| `frontend/src/modules/dashboard/components/TodoTable.vue` | **新建** | 待办表格组件 |
| `frontend/src/modules/dashboard/dashboard.api.ts` | **新建** | 聚合 API 调用 |
| `frontend/src/styles/dashboard.css` | **新建** | Dashboard 样式 |
| `frontend/src/main.ts` | 修改 | 仅在需要时 import dashboard.css |

### 实施细节

#### 1. `dashboard.api.ts` — 聚合现有 API

```typescript
import { getClients } from '@/api/clients'
import { getCases } from '@/api/cases'
import { getTasks } from '@/api/tasks'
import { getBills } from '@/api/billing'

export interface DashboardKpi {
  clientsTotal: number
  casesTotal: number
  tasksTotal: number
  tasksPendingTotal: number    // status=OPEN 的任务数
  billsTotal: number
}

export async function fetchDashboardKpi(): Promise<DashboardKpi> {
  const [clients, cases, tasks, pendingTasks, bills] = await Promise.all([
    getClients({ page: 1, page_size: 1 }),
    getCases({ page: 1, page_size: 1 }),
    getTasks({ page: 1, page_size: 1 }),
    getTasks({ page: 1, page_size: 1, status: 'OPEN' }),
    getBills({ page: 1, page_size: 1 }),
  ])
  return {
    clientsTotal: clients.total,
    casesTotal: cases.total,
    tasksTotal: tasks.total,
    tasksPendingTotal: pendingTasks.total,
    billsTotal: bills.total,
  }
}

export async function fetchTodoTasks() {
  // 使用后端已支持的 due_from/due_to 过滤
  // 取近期 10 条待办任务
  const res = await getTasks({
    page: 1,
    page_size: 10,
    status: 'OPEN',
  })
  return res
}
```

> **注意**：当前 `getTasks()` 只传了 `page/page_size/status`。需要确认 `getTasks` 函数签名是否支持 `status` 参数传入。若不支持，需在 `tasks.ts` 中扩展 params 类型（这超出了 DEMO-UI-02 的文件允许列表，需要作为前置微任务处理）。
>
> **已确认**：后端 `GET /tasks` 支持 `status` / `due_from` / `due_to` 过滤参数。前端 `getTasks()` 已传 `status`，可直接使用。如需 `due_from`/`due_to` 需扩展前端 API 函数。

#### 2. `KpiCard.vue`

```vue
<template>
  <div class="kpi-card">
    <span class="kpi-label">{{ label }}</span>
    <span class="kpi-value">{{ displayValue }}</span>
    <span v-if="sub" class="kpi-sub">{{ sub }}</span>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label: string        // 中文标题，如 "案件总数"
  value: number | string
  sub?: string         // 辅助说明
}>()

const displayValue = computed(() => /* 格式化数字 */)
</script>
```

样式使用 CSS 变量 `--bg-card` / `--shadow-card` / `--border-card` 等（由 style-b 覆盖）。

#### 3. `TodoTable.vue`

```vue
<template>
  <div class="data-panel">
    <div class="panel-header">
      <h3>待办案件</h3>
      <el-button type="primary" @click="$router.push('/tasks')">查看全部</el-button>
    </div>
    <el-table :data="tasks" stripe>
      <el-table-column prop="title" label="任务标题" />
      <el-table-column prop="case_id" label="关联案件">
        <template #default="{ row }">
          <router-link v-if="row.case_id" :to="`/cases/${row.case_id}`">
            {{ row.case_id.slice(0, 8) }}...
          </router-link>
          <span v-else class="text-muted">—</span>
        </template>
      </el-table-column>
      <el-table-column prop="due_date" label="期限">
        <template #default="{ row }">
          <span :class="isUrgent(row.due_date) ? 'text-danger' : ''">
            {{ row.due_date }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row.status)" size="small">
            {{ statusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>
```

> **数据降级**：后端 Task 不返回 `case_no` / `client_name`，关联案件列显示截断的 `case_id`（可点击跳转）。不为此新增后端 API。

#### 4. `Dashboard.vue` 重写

结构：
```
┌──────────────────────────────────────────┐
│  标题区：工作台    日期：2026-02-10       │
├──────────────────────────────────────────┤
│  ┌────────┐ ┌────────┐ ┌────────┐       │
│  │ KPI 1  │ │ KPI 2  │ │ KPI 3  │       │
│  │案件总数 │ │待办任务 │ │客户数量 │       │
│  └────────┘ └────────┘ └────────┘       │
├──────────────────────────────────────────┤
│  待办案件 (TodoTable)                    │
│  ┌──────┬────────┬───────┬──────┐       │
│  │ 标题 │关联案件 │ 期限  │ 状态 │       │
│  ├──────┼────────┼───────┼──────┤       │
│  │ ...  │ ...    │ ...   │  tag │       │
│  └──────┴────────┴───────┴──────┘       │
└──────────────────────────────────────────┘
```

加载状态：KPI 和表格分别有 skeleton loading。

#### 5. `styles/dashboard.css`

```css
/* KPI 网格 — 对齐 patent_ui.html style-b */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;                        /* style-b 的紧凑间距 */
  margin-bottom: 24px;
}

.kpi-card {
  background: var(--bg-card, #fff);
  padding: 20px;
  border-radius: var(--radius-card, 8px);
  box-shadow: var(--shadow-card, none);
  border: var(--border-card, 1px solid #E2E8F0);
}

.kpi-label {
  font-size: 13px;
  color: var(--text-sub, #94A3B8);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.kpi-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-highlight, #2563EB);
  font-family: var(--font-num, "Inter", sans-serif);
}

/* 数据面板 — 表格区 */
.data-panel {
  background: var(--bg-card, #fff);
  border-radius: var(--radius-card, 8px);
  box-shadow: var(--shadow-card, none);
  border: var(--border-card, 1px solid #E2E8F0);
  padding: var(--card-padding, 15px);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
```

### 数据来源验证

| KPI | API 来源 | 字段 |
|-----|----------|------|
| 案件总数 | `GET /cases?page_size=1` | `total` |
| 待办任务 | `GET /tasks?page_size=1&status=OPEN` | `total` |
| 客户数量 | `GET /clients?page_size=1` | `total` |
| 近期期限 | `GET /tasks?page_size=1&due_to=<7天后>` | `total`（可选，需扩展前端 API 参数） |

### 验证清单
- [ ] 登录后 `/dashboard` 第一屏：标题+日期、3+ KPI 卡片、待办表格
- [ ] KPI 数据来自真实 API（Network 面板可验证至少 3 个请求）
- [ ] 待办表格有真实任务数据（或空态时显示"暂无数据"）
- [ ] style-b 下 Dashboard 视觉贴近 patent_ui.html（截图对比）
- [ ] Loading skeleton 正常显示、无闪烁

---

## DEMO-UI-03：关系链 UX + 面包屑

### 目标
- 新增 `RelationChainCard` 组件：显示 客户→案件→文档→费用→账单 关系链
- 集成到 4 个详情页（CaseDetail / DocumentDetail / FeeDraftDetail / BillDetail）
- Demo 模式下 Header 面包屑增强（显示层级路径）
- 不新增后端 API，缺少字段时优雅降级

### 文件允许列表

| 文件 | 操作 | 说明 |
|------|------|------|
| `frontend/src/components/relations/RelationChainCard.vue` | **新建** | 关系链卡片 |
| `frontend/src/stores/pageContext.ts` | **新建** | 面包屑/标题 store |
| `frontend/src/components/header/TopHeader.vue` | 修改 | demo 模式读取 pageContext 面包屑 |
| `frontend/src/modules/cases/pages/CaseDetail.vue` | 修改 | 加 RelationChainCard + 设置面包屑 |
| `frontend/src/modules/documents/pages/DocumentDetail.vue` | 修改 | 同上 |
| `frontend/src/modules/fees/pages/FeeDraftDetail.vue` | 修改 | 同上 |
| `frontend/src/modules/billing/pages/BillDetail.vue` | 修改 | 同上 |
| `frontend/src/styles/relations.css` | **新建** | 关系链样式 |
| `frontend/src/main.ts` | 修改 | import relations.css |

### 实施细节

#### 1. `RelationChainCard.vue`

```vue
<template>
  <div class="relation-chain-card">
    <span class="chain-label">关系链</span>
    <div class="chain-items">
      <template v-for="(item, idx) in chainItems" :key="item.type">
        <span v-if="idx > 0" class="chain-arrow">→</span>
        <router-link v-if="item.id" :to="item.route" class="chain-link">
          {{ item.icon }} {{ item.display }}
        </router-link>
        <span v-else class="chain-muted">
          {{ item.icon }} 未关联
        </span>
      </template>
    </div>
  </div>
</template>
```

Props:
```typescript
interface Props {
  client?: { id: string; name?: string }
  case_?: { id: string; no?: string; title?: string }
  document?: { id: string; refNo?: string }
  feeDraft?: { id: string; label?: string }
  bill?: { id: string; no?: string }
}
```

路由映射（来自 `router/index.ts` 实际定义）：
| 实体 | 路由 |
|------|------|
| client | `/clients/${id}/edit` |
| case | `/cases/${id}` |
| document | `/documents/${id}` |
| feeDraft | `/fees/drafts/${id}` |
| bill | `/billing/bills/${id}` |

组件只渲染有值的节点；完全无关联数据时不显示整个卡片。

#### 2. `stores/pageContext.ts`

```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const usePageContext = defineStore('pageContext', () => {
  const breadcrumb = ref<string[]>([])
  const title = ref('')

  function setBreadcrumb(items: string[]) {
    breadcrumb.value = items
  }

  function clear() {
    breadcrumb.value = []
    title.value = ''
  }

  return { breadcrumb, title, setBreadcrumb, clear }
})
```

**生命周期管理**：在 `router.beforeEach` 中调用 `pageContext.clear()`，防止面包屑残留。此修改在 `router/index.ts` 的 navigation guard 中加一行即可。

> **注意**：`router/index.ts` 不在 DEMO-UI-03 的文件允许列表中，但 DEMO-UI-01 已经修改了它（加中文 title）。需要在 DEMO-UI-01 实施时预留 pageContext.clear() 调用，或者将 `router/index.ts` 加入 DEMO-UI-03 允许列表（最小改动：1 行）。
>
> **建议**：在 DEMO-UI-01 修改 `router/index.ts` 时，一并加入：
> ```typescript
> router.beforeEach(() => {
>   // DEMO-UI-03 will use this
>   const pc = usePageContext?.()
>   pc?.clear()
> })
> ```

#### 3. 各详情页集成

每个详情页在数据加载完成后：

**CaseDetail.vue**：
```typescript
// 加载数据后
pageContext.setBreadcrumb(['案件管理', '案件详情', caseData.case_no])

// RelationChainCard props
<RelationChainCard
  :client="caseData.client_id ? { id: caseData.client_id } : undefined"
  :case_="{ id: caseData.id, no: caseData.case_no, title: caseData.title }"
/>
```

**DocumentDetail.vue**：
```typescript
pageContext.setBreadcrumb(['案件管理', '文档详情', docData.ref_no || docData.id])

<RelationChainCard
  :case_="docData.case_id ? { id: docData.case_id } : undefined"
  :document="{ id: docData.id, refNo: docData.ref_no }"
/>
```

**FeeDraftDetail.vue**：
```typescript
pageContext.setBreadcrumb(['费用管理', '费用草稿', draftData.id])

<RelationChainCard
  :client="draftData.client_id ? { id: draftData.client_id } : undefined"
  :case_="draftData.case_id ? { id: draftData.case_id } : undefined"
  :feeDraft="{ id: draftData.id }"
/>
```

**BillDetail.vue**：
```typescript
pageContext.setBreadcrumb(['账单管理', '账单详情', billData.bill_no || billData.id])

<RelationChainCard
  :client="billData.client_id ? { id: billData.client_id } : undefined"
  :case_="billData.case_id ? { id: billData.case_id } : undefined"
  :bill="{ id: billData.id, no: billData.bill_no }"
/>
```

#### 4. TopHeader.vue 面包屑增强

Demo 模式下，如果 `pageContext.breadcrumb` 有值，替换现有面包屑渲染：

```vue
<template v-if="demoUI && pageContext.breadcrumb.length">
  <span v-for="(crumb, i) in pageContext.breadcrumb" :key="i">
    <span v-if="i > 0" class="breadcrumb-sep"> / </span>
    {{ crumb }}
  </span>
</template>
```

#### 5. `styles/relations.css`

```css
.relation-chain-card {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: var(--bg-card, #fff);
  border: var(--border-card, 1px solid #E2E8F0);
  border-radius: var(--radius-card, 8px);
  margin-bottom: 16px;
  font-size: 14px;
}

.chain-label {
  color: var(--text-sub, #94A3B8);
  font-weight: 600;
  white-space: nowrap;
}

.chain-arrow {
  color: var(--text-sub, #94A3B8);
  margin: 0 4px;
}

.chain-link {
  color: var(--color-primary, #2563EB);
  text-decoration: none;
  cursor: pointer;
}

.chain-link:hover {
  text-decoration: underline;
}

.chain-muted {
  color: var(--text-sub, #94A3B8);
  font-style: italic;
}
```

### 数据可用性（已验证）

| 详情页 | client_id | case_id | 其他关联 |
|--------|-----------|---------|----------|
| CaseDetail | ✅ 有 | 自身 | — |
| DocumentDetail | ❌ 无（需通过 case 反查） | ✅ 有 | — |
| FeeDraftDetail | ✅ 有 | ✅ 有 | — |
| BillDetail | ✅ 有 | ⚠️ 前端有映射但后端 BillResponse 未返回 | — |

> 缺少字段时组件显示"未关联"，不影响整体展示。

### 验证清单
- [ ] CaseDetail：关系链显示 客户(ID)→案件(案号)，可点击
- [ ] DocumentDetail：关系链显示 案件(ID)→文档(refNo)，可点击
- [ ] FeeDraftDetail：关系链显示 客户→案件→费用草稿，可点击
- [ ] BillDetail：关系链显示 客户→账单，可点击
- [ ] 缺少关联数据时显示"未关联"且不崩溃
- [ ] Header 面包屑在详情页显示层级路径
- [ ] 路由切换后面包屑自动清理
- [ ] 主题 style-b 下关系链卡片视觉协调

---

## 前置微任务（可能需要）

在执行 DEMO-UI-02 时，如果发现前端 `getTasks()` 不支持传 `status` 参数，需要先做：

### DEMO-UI-02-PRE：扩展 getTasks() 支持 status 参数

| 文件 | 操作 |
|------|------|
| `frontend/src/api/tasks.ts` | 修改 getTasks 参数类型，加 `status?: string` |
| `frontend/src/api/tasks.types.ts` | 修改 TaskListParams 类型 |

> 已确认后端支持，仅需前端函数签名扩展。是否需要此微任务取决于 `tasks.ts` 当前实现。

---

## 新建文件总览

| 任务 | 新文件 |
|------|--------|
| DEMO-UI-00 | `styles/demo-themes.css` |
| DEMO-UI-01 | `constants/labels.zh.ts` |
| DEMO-UI-02 | `dashboard/components/KpiCard.vue`, `dashboard/components/TodoTable.vue`, `dashboard/dashboard.api.ts`, `styles/dashboard.css` |
| DEMO-UI-03 | `components/relations/RelationChainCard.vue`, `stores/pageContext.ts`, `styles/relations.css` |

**总计**：8 个新文件，~12 个修改文件

## 修改文件总览

| 文件 | 被哪些任务修改 |
|------|---------------|
| `.env.example` | 00 |
| `main.ts` | 00, 01, 02(?), 03(?) |
| `stores/ui.ts` | 00 |
| `layout/MainLayout.vue` | ~~00~~ (不需要 DemoToolbar，跳过) |
| `constants/menu.ts` | 01 |
| `components/nav/SidebarNav.vue` | 01 |
| `components/header/TopHeader.vue` | 01, 03 |
| `modules/auth/pages/Login.vue` | 01 |
| `router/index.ts` | 01 (+ 预留 03 的 clear) |
| `modules/dashboard/pages/Dashboard.vue` | 02 |
| `modules/cases/pages/CaseDetail.vue` | 03 |
| `modules/documents/pages/DocumentDetail.vue` | 03 |
| `modules/fees/pages/FeeDraftDetail.vue` | 03 |
| `modules/billing/pages/BillDetail.vue` | 03 |

---

## 风险登记

| # | 风险 | 级别 | 缓解措施 |
|---|------|------|----------|
| 1 | CSS 变量名不匹配（patent_ui 用 `--bg-card`，项目用 `--bg-panel`） | 中 | DEMO-UI-00 在 `demo-themes.css` 中做变量映射，两套名称都定义 |
| 2 | Tasks API 前端未传 status 参数 | 低 | 实施时确认，必要时加前置微任务 |
| 3 | BillDetail 缺少 case_id / case_no | 低 | RelationChainCard 降级显示"未关联" |
| 4 | 菜单分组改动导致其他组件 import `MENU_ITEMS` 报错 | 低 | 保留 `MENU_ITEMS` 的 flatten 导出作为兼容 |
| 5 | Element Plus zh-CN locale import 路径变化 | 低 | 确认 element-plus@2.7.6 的实际导出路径 |
| 6 | TopHeader 被 01 和 03 两次修改 | 低 | 01 做基础中文化，03 在其上增加 pageContext 面包屑（增量修改） |
