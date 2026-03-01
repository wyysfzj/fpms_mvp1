# FPMS MVP1 Frontend Development Plan (Vue3 + TS + Pinia + Element Plus + Vite)

## 0. 文档元信息

- **范围**：FPMS MVP1 Web 前端（对接已稳定的后端模块与 API 规范）
- **后端基址**：`http://localhost:8000/api/v1`
- **关键后端约束**：
  - JWT Bearer：`Authorization: Bearer <token>`
  - Error envelope：`{"error":{"code","message","details"}}`
  - List pagination：`{items, page, page_size, total}`
  - 常见状态码：401/403/422/409/200/201
- **信息架构与权限依据**：MVP1 IA / RBAC / permissions_matrix / api_usage_guide / error_codes

---

## 1) MVP1 成功标准（前端视角的验收目标）

对齐 “confidence milestones”，前端验收用**可操作链路**描述：

1. **案卷链路可用**
   - 登录 → 案卷列表检索 → 新建案卷 → 打开案卷详情（tabs）→ 更新案卷字段（Formalities 全量 / Agent limited）
2. **文书与时限链路可用**
   - 案卷下登记来文/去文（document）→ 上传附件 → 在任务队列看到任务（或手工创建任务）→ 关闭/重开任务 → 今日提醒页可用
3. **费用到开票链路可用**
   - 维护收费标准（rate）→ 创建 fee draft → 添加 items → lock → 生成 bill → 打印 bill（下载/打开）
4. **回款/冲抵链路可用**
   - 登记 payment → 进行 offsets（若依赖 payment_line_id，则 UI 以“后端可提供的数据结构”为准）→ 案卷 receipts 汇总可查看

> 上述每条在 FE‑3 结束时必须有“端到端 smoke steps（等价 curl guide 的 UI 版本）”。

---

## 2) 当前前端仓库基线审计（基于已上传 frontend 源码）

### 2.1 已存在的技术栈（✅符合偏好）

- Vue 3 / TypeScript / Vite
- Pinia、Vue Router、Element Plus、axios、dayjs
- 目录已有雏形：`src/api`、`src/router`、`src/layout`、`src/modules/*`

### 2.2 关键缺口（影响 FE‑0 执行）

**(A) 构建阻塞：缺少 `index.html`**

- 证据：`npm run build` 失败：`Could not resolve entry module "index.html".`
- 结论：在任何功能开发前，必须先做一个**最小修复任务**补齐 Vite 入口文件，使 build/dev 可运行。

**(B) FE‑0 标准未达：缺少 lint/typecheck 门禁脚本**

- 当前 scripts 只有 `dev/build/preview`
- AI‑EOS 要求每个原子任务都要能跑 lint/typecheck/build 出证据，因此需要先补齐工具链与脚本。

**(C) Auth/Session 仍是“直连 localStorage + 无 guard”**

- Login 直写 `localStorage`，无 Pinia auth store、无启动恢复、无全局 401 处理、无 403 统一 UX

**(D) API client 未满足规范**

- baseURL 逻辑可能是 `VITE_API_BASE_URL` + `/api/v1`（但系统约束要求 baseURL 本身就是 `/api/v1`）
- 缺少：
  - error envelope 归一化
  - request_id（X-Request-ID）捕获
  - 401/403/422/409 的统一处理策略

**(E) 业务页面大多是 TODO stub**

- Router 已挂载 Cases/Docs/Tasks/Fees/Billing/Settings，但页面仍是占位文本

---

## 3) 架构蓝图（MVP1 适配“专利律师事务所：现代、克制、高效率”的 UI/UX）

### 3.1 页面骨架（App Shell）

- Layout：左侧 Sidebar（模块）+ 顶部 Header（面包屑/全局动作/用户菜单）+ Main（内容区）
- Element Plus 组件建议：
  - `el-container / el-aside / el-header / el-main`
  - `el-menu`（侧边导航）
  - `el-page-header` 或自建 `PageHeader`（标题+操作）
  - `el-card`（信息分区）
  - `el-tabs`（Case detail tabs）

### 3.2 现代律所风格的 UI 规范（MVP 可落地版本）

- **颜色**：低饱和主色 + 中性灰背景；避免花哨渐变
- **密度**：表格/列表为核心；默认密度略紧凑（适合高信息量）
- **信息层级**：编号/状态/时间等元数据固定在详情页顶部“Meta 区”
- **反馈**：所有 API 行为必须有 loading/empty/error；错误要显示 `request_id` 便于审计

> 主题实现策略：先用 CSS Variables 覆盖 Element Plus 主色/字体/圆角；需要更深主题定制再单独立 task 评估（不与业务页面耦合）。

### 3.3 权限与导航（无 `/auth/me` 的现实策略）

后端可能没有 auth profile endpoint，因此前端权限渲染采取：

- **最佳努力**：若 JWT claims 内含 perms/roles → 解析并用于菜单 show/hide
- **兜底**：无 perms → 菜单可显示，但所有 API/页面以 403 为最终裁决
- 403 页面显示 `details.required_perm`，指导用户执行后端 perms sync + re-login（对齐 api_usage_guide）

### 3.4 API Client 统一层（强制）

所有模块请求必须通过 `src/api/http.ts`：

- `baseURL = VITE_API_BASE_URL`（应为 `http://localhost:8000/api/v1`）
- request interceptor：注入 Bearer token
- response interceptor：
  - 捕获 `X-Request-ID`
  - 将错误归一成统一 `ApiError`（status/code/message/details/requestId）
  - 401：清 session → 跳登录
  - 403：统一 PermissionDenied UX（或抛给页面，但体验必须一致）
  - 422：结构化映射到表单字段（Element Plus `el-form-item`）
  - 409：显示冲突提示（ElMessageBox/ElAlert）

### 3.5 类型策略（MVP1）

- 先手写 `src/api/types.ts`（分页/错误/基础 DTO）
- 每个模块建立最小 DTO（list item + create/update payload）
- 如后续提供 OpenAPI export，再评估生成 types（单独原子任务，不与业务页面耦合）

---

## 4) 分阶段交付计划（Atomic Task Register）

> 每个任务都是 PR-sized，并具备：
> 
> - File Allowlist（精确到目录/文件）
> - Quality Gates：lint + typecheck + build
> - Evidence Log：命令与关键输出
> - Stop Condition：遇到 endpoint mismatch/CORS/auth 缺失 → 立即停止并提出最小修复任务

---

# Phase FE‑0：Bootstrapping & Standards

## FE‑0‑00：修复 Vite 入口 + 建立质量门禁（前置阻塞清理）

**目标**：让项目 dev/build 可运行；并补齐 lint/typecheck 脚本，满足后续每个任务可出证据。

**File Allowlist**

- `index.html`（新增）
- `src/main.ts`（必要时微调挂载点）
- `package.json`
- `tsconfig.json`（必要时）
- `vite.config.ts`（必要时）
- `src/vite-env.d.ts`（新增）
- （若引入 eslint/prettier）`.eslintrc*` / `eslint.config.*`、`.prettierrc`、`.editorconfig`

**Quality Gates**

- `npm run build` 必须通过
- `npm run typecheck` 必须通过（新增：`vue-tsc --noEmit`）
- `npm run lint` 必须通过（新增：eslint）

**Acceptance Criteria**

- `dist/` 正常生成
- `npm run dev` 能启动并渲染 `/login`

---

## FE‑0‑01：Auth + Session + API Client 归一化 + 路由守卫（闭环）

**目标**：UI 能登录拿 token，启动恢复 token；访问受保护接口可成功；401 自动回登录；错误 envelope 正确显示。

**File Allowlist**

- `src/api/http.ts`
- `src/api/errors.ts`（新增）
- `src/api/types.ts`（新增/完善）
- `src/stores/auth.ts`（新增）
- `src/router/index.ts`
- `src/modules/auth/pages/Login.vue`
- `src/modules/dashboard/pages/Dashboard.vue`（protected smoke）
- `.env` / `.env.example`（baseURL 对齐为 `/api/v1`）

**Quality Gates**

- lint/typecheck/build 全通过
- 手工 smoke：
  - 登录成功 → 跳 dashboard
  - dashboard 调 `GET /clients?page=1&page_size=1` 成功展示 total/empty

**Acceptance Criteria**

- Token 存储：localStorage
- Boot restore：刷新保持登录态
- 401：清 token 并重定向到 `/login`
- 403：PermissionDenied 显示 required_perm（若后端返回）
- error 包含 requestId（若存在）

---

# Phase FE‑1：Layout + Navigation + Global Error UX

## FE‑1‑01：现代化 App Shell（Element Plus Layout + Sidebar + Header）

**Allowlist**

- `src/layout/MainLayout.vue`
- `src/components/layout/*`
- `src/styles/*`
- `src/App.vue`

**Acceptance Criteria**

- Sidebar `el-menu`（支持折叠可选）
- Header：系统名 + 面包屑/标题 + 用户下拉（logout）
- 主内容区统一 padding/背景

---

## FE‑1‑02：RBAC-aware Navigation（菜单 show/hide + route meta）

**Allowlist**

- `src/router/index.ts`
- `src/components/nav/*`
- `src/stores/auth.ts`
- `src/constants/perms.ts`
- `src/constants/menu.ts`

**Acceptance Criteria**

- 路由 meta.requiredPerms 与 docs matrix 对齐
- 无 perms 时不阻塞使用，403 兜底

---

## FE‑1‑03：统一错误 UX（401/403/422/409）

**Allowlist**

- `src/api/errors.ts`
- `src/components/errors/*`
- `src/views/PermissionDenied.vue`
- `src/views/NotFound.vue`
- `src/router/index.ts`

**Acceptance Criteria**

- 422：字段级提示（优先 details 字段信息）
- 409：统一冲突提示
- toast/banner 展示 requestId（若存在）

---

# Phase FE‑2：Feature Pages（MVP1）

> 顺序遵循业务优先级：Clients → Cases → Tasks → Documents → Fees → Billing → System/Templates。

## Clients（客户）

- **FE‑2‑01**：Client List + Pagination（GET /clients）
- **FE‑2‑02**：Client Create/Edit/Deactivate（POST/PUT/PUT deactivate）

## Cases（案卷）

- **FE‑2‑03**：Case List + Create（GET/POST /cases，含 client_id）
- **FE‑2‑04**：Case Detail + Edit（GET/PUT /cases/{id}）
- **FE‑2‑05**：Limited Edit（POST /cases/{id}/limited-edit）

## Tasks（时限/任务）

- **FE‑2‑06**：Task List（GET /tasks + filters）
- **FE‑2‑07**：Task Create（POST /tasks，case_id 必填）
- **FE‑2‑08**：Task Close/Reopen/Cancel（POST action）
- **FE‑2‑09**：Today Reminders（GET /tasks/today?as=worker|supervisor）

## Documents（文书/来往函件）

- **FE‑2‑10**：Document List + Create（GET/POST /documents）
- **FE‑2‑11**：Document Detail + Edit（GET/PUT /documents/{id}）
- **FE‑2‑12**：Attachments Upload/Download（POST upload + GET download）

## Fees（费用）

- **FE‑2‑13**：Fee Rates（GET/POST/PUT /fees/rates）
- **FE‑2‑14**：Fee Drafts List/Create/Detail（GET/POST/GET/PUT /fees/drafts）
- **FE‑2‑15**：Draft Items CRUD（POST/PUT/DELETE）
- **FE‑2‑16**：Draft Lock/Unlock（POST /lock /unlock）

## Billing（账单/应收）

- **FE‑2‑17**：Bills List + Detail（GET /bills, GET /bills/{id}）
- **FE‑2‑18**：Bill Create（POST /bills/from-drafts & /bills/manual）
- **FE‑2‑19**：Bill Print（GET /bills/{id}/print）
- **FE‑2‑20**：Payments + Offsets（/payments, /offsets, reverse）
- **FE‑2‑21**：Case Receipts Summary（GET /cases/{case_id}/receipts）

## System/Templates（系统参数/模板）

- **FE‑2‑22**：Templates List/Upload（GET/POST /templates）
- **FE‑2‑23**：System Params List/Upsert（GET /system/params + PUT /system/params/{key}）
- **FE‑2‑24**：Letterheads（GET/POST /letterheads）

---

# Phase FE‑3：Integration & Polish

## FE‑3‑01：端到端 Smoke Flows（对齐 curl guide）

**交付物**：`docs/frontend_smoke_flows.md`（步骤/预期/错误定位 + requestId）

## FE‑3‑02：空态/加载态/分页一致性

- 列表页 skeleton、empty、统一 pagination 组件
- 详情页 Meta 区 + Tabs 一致

## FE‑3‑03：可访问性与一致性检查（MVP）

- 表单 label、键盘可达、对话框可关闭
- 危险操作二次确认

---

## 5) 统一质量门禁（适用于每个原子任务）

每个任务提交必须包含 Evidence Log（最少三条）：

1. `npm run lint`
2. `npm run typecheck`
3. `npm run build`

并附：关键成功输出行；若有手工 smoke，给出可复现步骤与结果描述（可选截图）。

---

## 6) Stop Conditions（遇到即停止，提出最小修复任务）

- endpoint 与 docs/OpenAPI 不一致
- CORS 阻塞
- login 返回结构与预期不同（token 字段名差异）
- 关键字段（如 payment_line_id）无法获取导致链路不可完成

遇到上述情况：停止当前任务，输出最小修复任务，而不是在前端做猜测性 workaround。
