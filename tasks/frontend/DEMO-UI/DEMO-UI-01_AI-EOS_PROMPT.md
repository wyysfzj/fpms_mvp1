# AI‑EOS PROMPT — DEMO‑UI‑01
## Title
DEMO‑UI‑01: 全站核心标签中文化 + 导航命名/信息架构对齐 `reference/patent_ui.html`

## Context
当前 UI 偏“英文工程化 MVP 文案”（Dashboard/Search/Logout/Settings 等）。客户 Demo 需要更贴近专利律所语境，并与 `reference/patent_ui.html` 左侧菜单命名对齐。

## Objective (Closed-loop)
1) 全站核心可见标签中文化（至少覆盖：登录、侧边栏、Header、Dashboard、全局按钮/空态的关键文案）。
2) 侧边栏对齐 `patent_ui.html` 的一级菜单命名（示例：工作台/案件管理/期限监控/客户中心/设置）。
3) 将当前菜单中的 **Settings**（若存在）调整为“客户中心/客户列表”语义，并与参考稿一致（避免英文 Settings 暴露在 Demo）。
4) 保持 RBAC best-effort：菜单仍可按 permissions 隐藏；perms unknown 时不隐藏。

## Non‑Goals (hard)
- 不做 Dashboard 结构大改（DEMO‑UI‑02 做）
- 不改变路由结构与权限策略
- 不引入 i18n 框架（用轻量常量表即可）

## File Allowlist (ONLY modify/add these)
- `frontend/src/modules/auth/pages/Login.vue` (update: 中文化)
- `frontend/src/components/layout/TopHeader.vue` (update: 中文化; demo模式可显示标题+日期)
- `frontend/src/components/nav/SidebarNav.vue` (update: 中文化显示; 分组/图标对齐)
- `frontend/src/constants/menu.ts` (update: labels中文化 + 信息架构对齐)
- `frontend/src/router/index.ts` (update: route meta title 中文化，若你们用它显示标题/面包屑)
- `frontend/src/ui/labels.zh.ts` (new: 集中管理中文文案)
- `frontend/src/main.ts` (update ONLY if needed: Element Plus locale to zh-CN)
- Evidence:
  - `task/frontend/DEMO-UI/DEMO-UI-01_evidence.md`

If more files are needed: STOP and propose smallest follow-up task.

## Implementation Steps
### 1) 建立中文文案表（轻量）
- 新建 `frontend/src/ui/labels.zh.ts`
  - export object with keys for:
    - login.title / login.username / login.password / login.submit
    - nav.dashboard / nav.cases / nav.tasks / nav.clients / nav.settings
    - header.searchPlaceholder / header.logout
    - dashboard.title, etc.
- 在相关组件中引用该表，而不是散落硬编码。

### 2) Sidebar 菜单对齐参考稿命名
- 更新 `frontend/src/constants/menu.ts`：
  - 一级分组：工作台 / 案件管理 / 期限监控 / 客户中心 / 设置
  - 将原 “Settings” 菜单项替换为：
    - 客户中心（分组）下的：客户列表
  - 仍保留你们已有模块入口（文档/费用/账单/系统），但可放入合适分组（例如 案件管理 或 设置）。
  - 保持 `requiredPerms` 逻辑不变。

### 3) Sidebar 渲染中文
- `SidebarNav.vue`：
  - 支持分组标题（如果当前菜单是扁平结构，则用最小改动新增分组渲染）
  - 图标与 hover/active 行为延续现有 tokens 设计

### 4) Header 中文化并贴近专利业务语气
- `TopHeader.vue`：
  - 将 Search placeholder、Logout 等改为中文
  - Demo 模式（VITE_DEMO_UI=1）下：header 左侧优先显示“标题 + 日期/时间”风格（参考 patent_ui），同时保留用户菜单（退出登录）

### 5) Login 页中文化
- 替换英文 label 与错误提示为中文（错误 code/message 可保留原样，但 UI 文案中文）

### 6) Manual Verification
- 登录前后全站不出现英文 “Dashboard/Search/Logout/Settings”
- Sidebar 菜单命名与 `patent_ui.html` 对齐（截图对比）
- 权限未知时菜单不隐藏；权限已知时仍可 best-effort 隐藏

## Gates (mandatory)
```bash
cd frontend
npm run lint
npm run typecheck
npm run build
```

## Evidence Log (mandatory)
Write `task/frontend/DEMO-UI/DEMO-UI-01_evidence.md`:
- Screenshots: 登录页 + 登录后 header/sidebar
- List changed labels summary
- Gates outputs
