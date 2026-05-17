# Product Sidebar Navigation Design

- date: `2026-05-17`
- scope: `frontend product navigation information architecture and sidebar interaction design`
- approved_direction: `D - 工作导航默认 + 模块导航切换`
- mock: `.superpowers/brainstorm/85522-1778990749/sidebar-product-mock-02.html`

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `frontend-only`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Problem Statement

当前左侧菜单把业务实体、财务、报表、系统设置等模块直接铺开，正式使用时信息密度过高，且相同业务概念在多个分组重复出现。它能暴露功能，但不能很好地支持最终用户按日常工作路径完成案件生命周期、费用、账单、回款和授权后运营。

新版侧栏必须是上线后的正式产品导航，不是客户演示脚本。端到端流程应作为默认工作路径自然可见，但完整模块入口仍必须可访问、可发现、可权限过滤。

## Confirmed Direction

采用 `D - 工作导航默认 + 模块导航切换`：

- 默认视图是 `工作导航`，面向最终用户日常工作，不命名为“演示流程”。
- 第二视图是 `模块导航`，作为完整功能地图，保留现有模块覆盖面。
- 侧栏支持展开/折叠，折叠后保留高频图标入口和当前路由高亮。
- 不修改后端、路由语义、权限模型或 API contract。

## Current Navigation Audit

当前菜单主要问题：

- 同一入口重复出现，例如 `授权费任务` 同时在业务实体和财务中出现。
- 报表、财务、业务实体混排后，首屏没有清晰工作优先级。
- 所有用户都看到同一种模块堆叠，缺少“我今天该从哪里开始”的引导。
- 侧栏不可折叠，长菜单在小屏或演示投屏时占用空间。
- 现有视觉语言是白底、浅边框、蓝色 active、6-8px 圆角，应延续而不是重做品牌风格。

## Product Goals

- 支持最终用户日常使用：进入系统后默认看到待办、案件、文件、费用、账单、回款、授权后运营的主要工作路径。
- 支持完整功能发现：模块导航仍提供客户、案件、文件、任务、费用、账单、报表、系统设置等全量入口。
- 降低首屏噪音：默认菜单控制在可扫描范围内，长尾入口进入折叠组或模块导航。
- 保持权限兼容：继续按现有 `requiredPerms` 做 best-effort 过滤；空分组不显示。
- 保持中文和术语一致：所有用户可见导航文案必须是简体中文，并沿用 `terminology.ts` / `labels.zh.ts` 的术语口径。

## Non-goals

- 不做 backend 改动。
- 不改 API response envelope。
- 不改业务路由、权限码、数据库或登录流程。
- 不把菜单改成只服务演示的线性步骤列表。
- 不引入大规模设计系统或图标库重构。
- 不在本设计中实现命令面板；搜索可保留现状。

## Target Information Architecture

### 工作导航（默认）

面向工作路径和高频操作，默认展示：

1. `我的工作`
   - `工作台`
   - `今日提醒`
   - `任务与期限`
   - `专项期限检索`
2. `案件生命周期`
   - `案件列表`
   - `新建案件`
   - `往来文件`
   - `批量递交`
3. `费用到回款`
   - `授权费任务`
   - `费用草稿`
   - `官费清单`
   - `账单管理`
   - `回款与核销`
   - `个案收款登记`
4. `授权后运营`
   - `年费任务`
   - `催款管理`
   - `提成记录`
   - `提成结算`
5. 固定底部折叠组
   - `客户与主数据`
   - `报表分析`
   - `系统设置`

### 模块导航（完整功能地图）

面向模块发现和管理用户，覆盖现有能力：

- `客户与案件`
  - `客户管理`
  - `案件管理`
  - `案件批量递交`
- `文件与任务`
  - `往来文件`
  - `任务与期限`
  - `专项期限检索`
- `费用与账单`
  - `费用草稿`
  - `费率管理`
  - `授权费任务`
  - `官费清单`
  - `账单管理`
  - `回款与核销`
  - `冲销管理`
  - `个案收款登记`
  - `支出管理`
- `授权后与提成`
  - `年费任务`
  - `催款管理`
  - `提成规则`
  - `提成记录`
  - `提成结算`
- `报表分析`
  - `报表总览`
  - `案件统计`
  - `年费任务统计`
  - `账单统计`
  - `费用草稿统计`
  - `支出统计`
  - `费用情况一览`
  - `提成结算报表`
  - `顾问收益视图`
- `系统设置`
  - `系统配置`
  - `主数据入口`
  - `部门主数据`
  - `任务模板`
  - `文件模板`
  - `模板文件源`
  - `信纸抬头`

## Interaction Design

### Navigation Mode

- Sidebar header below logo shows a compact segmented control:
  - `工作导航`
  - `模块导航`
- Default mode: `工作导航`
- Persist mode in localStorage through UI store, e.g. `fpms_nav_mode`.
- Switching mode does not navigate by itself; it only changes visible menu structure.

### Collapse

- Expanded width uses existing token (`--sidebar-width`), currently `240px` or demo theme `220px`.
- Collapsed width should be tokenized, e.g. `--sidebar-collapsed-width: 60px`.
- Collapse state persists in localStorage, e.g. `fpms_sidebar_collapsed`.
- Collapsed state shows icons only.
- Hover/focus on collapsed item shows a tooltip with the Chinese menu label.
- Active route remains visible in both states.
- The collapse button is an icon button with accessible label:
  - 展开时：`收起侧栏`
  - 折叠时：`展开侧栏`

### Active State

- Existing `router-link-active` is insufficient for detail pages whose route path is a child of a list route.
- Each nav item should support route matching by:
  - exact route path for direct pages
  - optional `activePatterns` or route name list for list/detail/create pages
- Example:
  - `/cases`, `/cases/new`, `/cases/:id`, `/cases/:id/edit` all highlight `案件列表` or `案件管理` depending on selected IA.

### Permission Filtering

- Reuse existing `requiredPerms`.
- If a section has no visible children after filtering, hide the section.
- If all default work-navigation children in a lane are hidden, hide the lane and keep remaining lanes compact.
- Do not show disabled menu items for unauthorized routes in this iteration.

## Visual Design

- Preserve current FPMS style:
  - white sidebar
  - light borders (`#E2E8F0` / `#F1F5F9`)
  - primary blue active state
  - 6-8px radius
  - dense but readable 13-14px labels
- Keep cards out of the sidebar; sidebar should remain a navigation surface, not a dashboard.
- Avoid oversized hero or decorative treatment.
- Menu labels should not wrap in expanded mode; use `text-overflow: ellipsis` if needed.
- Collapsed mode must not rely on emoji meaning alone; tooltip/accessibility label is required.

## Data Model Changes

Update `frontend/src/constants/menu.ts` without changing route definitions:

- Introduce a richer nav section model for product navigation:
  - `mode: 'work' | 'module'`
  - `key`
  - `label`
  - `children`
  - `collapsible?: boolean`
  - `defaultCollapsed?: boolean`
- Extend `MenuItem` minimally:
  - `shortLabel?: string`
  - `activePatterns?: string[]`
  - `groupKey?: string`
- Keep `MENU_ITEMS` flat export backward-compatible.

Update `frontend/src/stores/ui.ts`:

- Add sidebar collapse state.
- Add navigation mode state.
- Persist both with localStorage.

Update `SidebarNav.vue`:

- Render selected nav mode.
- Render collapsible sections.
- Render collapsed icon rail.
- Apply permission filtering before section rendering.
- Preserve router-link based navigation.

Update `layout.css`:

- Add collapsed sidebar width and transition styles.
- Keep immersive mode behavior authoritative; immersive mode may still fully hide the sidebar.

## Implementation Boundary

Likely implementation can be one frontend atomic task if scoped to one page capability:

- `frontend/src/components/nav/SidebarNav.vue`
- `frontend/src/constants/menu.ts`
- `frontend/src/stores/ui.ts`
- `frontend/src/styles/layout.css`
- optional `frontend/src/constants/labels.zh.ts` only if shared labels are needed

If implementation discovers a broader shared component or route registry change, stop and split into a batch manifest before coding.

## Verification Expectations

- `cd frontend && npx eslint src --max-warnings 0`
- `cd frontend && npm run typecheck`
- `cd frontend && npm run build`
- Browser verification:
  - default login-to-dashboard sidebar shows `工作导航`
  - switching to `模块导航` shows full module map
  - collapse/expand works and persists after reload
  - active route remains highlighted on list/detail/create routes
  - unauthorized or unavailable items do not leave empty group headers
- Task gate:
  - `./scripts/task_validate.sh <TASK-ID>`

## Risks

- Over-indexing on E2E can make the sidebar feel like a tutorial. Mitigation: use product terms such as `工作导航`, `案件生命周期`, `费用到回款`, not `演示流程`.
- Two navigation modes can confuse users if the switch is too prominent. Mitigation: keep it compact and default to work navigation.
- Active route matching can become brittle. Mitigation: use explicit route names/patterns instead of string prefix guesses where possible.
- Permission filtering can create odd gaps. Mitigation: filter sections after children and hide empty sections.

## Exact Non-closure Boundary

- This design does not implement the sidebar.
- This design does not modify backend, routes, permissions, database, API contracts, or product workflows.
- This design does not decide mobile drawer behavior beyond preserving desktop responsiveness.
- This design does not introduce command palette or global search changes.

## Recommended Result Shape

Proceed to implementation planning for one atomic frontend task that delivers the D navigation shell:

`工作导航默认 + 模块导航切换 + sidebar collapse persistence`
