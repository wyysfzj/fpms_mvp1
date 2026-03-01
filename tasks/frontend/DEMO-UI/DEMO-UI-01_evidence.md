# Evidence Log — DEMO-UI-01

## Task
- ID: DEMO-UI-01
- Title: 全站核心中文化 + 导航命名/信息架构对齐 patent_ui.html
- Date: 2026-02-10
- Agent/Model: Claude Opus 4.6

## File Allowlist
- ✅ Confirmed all changes are within allowlist (+ index.html for lang/title)
- `frontend/src/constants/labels.zh.ts` — **new** (centralized Chinese labels)
- `frontend/src/constants/menu.ts` — rewritten (MenuGroup + grouped items + flat compat export)
- `frontend/src/components/nav/SidebarNav.vue` — rewritten (group rendering)
- `frontend/src/components/header/TopHeader.vue` — updated (Chinese breadcrumb + search + logout)
- `frontend/src/modules/auth/pages/Login.vue` — updated (Chinese labels)
- `frontend/src/main.ts` — updated (Element Plus zh-CN locale)
- `frontend/index.html` — updated (lang="zh-CN", title)

## Commands Executed
```bash
cd frontend
npm run lint       # ✅ pass
npm run typecheck  # ✅ pass
npm run build      # ✅ pass (1634 modules, 2.91s)
```

## Key Outputs
- lint: 0 warnings, 0 errors
- typecheck: 0 errors (vue-tsc --noEmit)
- build: ✓ 1634 modules transformed, built in 2.91s

## Changes Summary

### labels.zh.ts (new)
- Centralized Chinese string table with sections: app, login, nav, header, dashboard, route, common
- `ZH.route` maps route names to Chinese titles (used by TopHeader breadcrumb)
- `as const` for type safety

### menu.ts (rewritten)
- Added `MenuGroup` interface with `key`, `label`, `children`
- Grouped menu aligned to patent_ui.html:
  - (top): 工作台
  - 案件管理: 案件列表 / 文档管理 / 费用管理 / 账单管理
  - 期限监控: 任务列表
  - 客户中心: 客户列表
  - 系统设置: 系统配置
- Preserved `MENU_ITEMS` flat export via `MENU_GROUPS.flatMap()` for backward compatibility
- All `requiredPerms` unchanged

### SidebarNav.vue (rewritten)
- Now iterates `MENU_GROUPS` → renders group label + child items
- Groups with all children hidden (by perms) are auto-hidden
- Logo changed: "FPMS" → "⚖️ LegalFlow" (aligned to patent_ui.html)
- Added scoped `.nav-group-label` style

### TopHeader.vue (updated)
- Search placeholder: "Search..." → "搜索案件、客户..."
- Logout: "Logout" → "退出登录"
- Breadcrumb: uses `ZH.route[name]` lookup for Chinese title, fallback to capitalized route name

### Login.vue (updated)
- Title: "Login" → "系统登录"
- Labels: "Username" / "Password" → "用户名" / "密码"
- Button: "Login" → "登 录"
- Error fallback: "Login failed" → "用户名或密码错误"

### main.ts (updated)
- Added `import zhCn from 'element-plus/es/locale/lang/zh-cn'`
- Changed `app.use(ElementPlus)` → `app.use(ElementPlus, { locale: zhCn })`
- This automatically localizes el-pagination, el-date-picker, etc.

### index.html (updated)
- `<html lang="en">` → `<html lang="zh-CN">`
- `<title>FPMS MVP1</title>` → `<title>LegalFlow - 知识产权管理系统</title>`

## Manual Verification
### Steps
1. Login page should show: "系统登录" / "用户名" / "密码" / "登 录"
2. After login, sidebar should show grouped Chinese menus
3. Header breadcrumb should display Chinese route names
4. No English "Dashboard", "Search", "Logout", "Settings" visible

### Results
- Gates: PASS (lint + typecheck + build all clean)

## UI Reference Alignment Notes
- `reference/patent_ui.html` sidebar alignment: ✅ 工作台 / 案件管理 / 期限监控 / 客户中心 matching
- Settings → renamed to 系统设置, route → /system/params
- Original "Settings → /settings/clients" replaced; clients now under 客户中心
- Tokens safety (variables.css base block unchanged): ✅

## Notes
- router/index.ts was NOT modified (route names/paths unchanged). Chinese titles are resolved in TopHeader via labels.zh.ts lookup.
- MENU_ITEMS flat export kept for any other code that imports it.
