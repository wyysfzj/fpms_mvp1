# POST-ENHANCEMENT Atomic Tasks — Frontend Batches

## 0. 执行协议（给 Agent Team）
- 一次执行 1 个 Task ID。
- 并行前提：allowlist 文件不重叠。
- 必须遵循现有前端规范：
  - Vue3 + TS + Pinia + Element Plus
  - 保持现有错误处理（`http.ts` + `normalizeApiError`）
  - 不破坏既有路由和页面行为
- 每个任务交付必须包含：
  - 修改文件清单
  - `npm run lint && npm run typecheck` 结果
  - 关键页面手工验证记录

## 1. 批次总览（建议顺序）
1. FE-B0（权限与契约对齐）
2. FE-B1（Annual Fee / Gov Payment）
3. FE-B2（Dunning / Bad Debt）
4. FE-B3（Commission）
5. FE-B4（Consulting/Search + Expense）
6. FE-B5（集成与质量硬化）

---

## FE-B0 — 权限与契约对齐

### PE-FE-00-01 (service)
- 目标：统一前端权限常量与后端权限码命名（`Title.Action`）。
- Allowlist:
  - `frontend/src/constants/perms.ts`
  - `frontend/src/constants/menu.ts`
- 依赖：无
- 验收：菜单鉴权不再使用 `cases:read` 这类旧风格。
- 验证：`cd frontend && npm run lint && npm run typecheck`

### PE-FE-00-02 (service)
- 目标：登录后拉取真实权限并写入 auth store（避免 permissive unknown）。
- Allowlist:
  - `frontend/src/stores/auth.ts`
  - `frontend/src/api/system.ts` 或新增 `frontend/src/api/auth.ts`
- 依赖：PE-FE-00-01
- 验收：`hasAnyPermission` 在权限已加载后可准确控制 UI。
- 验证：`cd frontend && npm run lint && npm run typecheck`

### PE-FE-00-03 (doc)
- 目标：补充前端错误码与状态码处理对照文档。
- Allowlist:
  - `docs/FPMS_Frontend_Manual_Test_User_Guide.md`
- 依赖：无
- 验收：新增域错误处理路径可复用。
- 验证：文档自检。

---

## FE-B1 — Annual Fee / Gov Payment

### PE-FE-AN-01 (service)
- 目标：新增 annuity API client（任务列表、指示更新、生成草单）。
- Allowlist:
  - `frontend/src/api/annuity.ts` (new)
  - `frontend/src/api/annuity.types.ts` (new)
- 依赖：PE-BE-AN-02~05
- 验收：API 请求/响应类型完整，错误处理一致。
- 验证：`npm run lint && npm run typecheck`

### PE-FE-AN-02 (endpoint page)
- 目标：年费任务列表页（筛选、分页、状态展示）。
- Allowlist:
  - `frontend/src/modules/annuity/pages/AnnuityTaskList.vue` (new)
  - `frontend/src/router/index.ts`
- 依赖：PE-FE-AN-01
- 验收：可查询并分页展示年费任务。
- 验证：`npm run lint && npm run typecheck`

### PE-FE-AN-03 (endpoint page)
- 目标：客户指示编辑对话框（PAY/ABANDON/DEFER）。
- Allowlist:
  - `frontend/src/modules/annuity/components/InstructionDialog.vue` (new)
  - `frontend/src/modules/annuity/pages/AnnuityTaskList.vue`
- 依赖：PE-FE-AN-02
- 验收：指示保存成功后列表刷新，错误提示正确。
- 验证：`npm run lint && npm run typecheck`

### PE-FE-AN-04 (endpoint page)
- 目标：草单批量生成操作（选中任务→调用生成接口）。
- Allowlist:
  - `frontend/src/modules/annuity/pages/AnnuityTaskList.vue`
- 依赖：PE-FE-AN-03
- 验收：结果回执显示成功/失败明细。
- 验证：`npm run lint && npm run typecheck`

### PE-FE-AN-05 (endpoint page)
- 目标：官费清单 + 缴费登记页面。
- Allowlist:
  - `frontend/src/api/govPayments.ts` (new)
  - `frontend/src/api/govPayments.types.ts` (new)
  - `frontend/src/modules/annuity/pages/PayList.vue` (new)
  - `frontend/src/modules/annuity/pages/GovPaymentCreate.vue` (new)
- 依赖：PE-BE-AN-06, PE-BE-AN-07
- 验收：清单可查、缴费可录、状态可见。
- 验证：`npm run lint && npm run typecheck`

---

## FE-B2 — Dunning / Bad Debt

### PE-FE-CL-01 (service)
- 目标：新增 collections API client（催款、坏账、恢复）。
- Allowlist:
  - `frontend/src/api/collections.ts` (new)
  - `frontend/src/api/collections.types.ts` (new)
- 依赖：PE-BE-CL-02~05
- 验收：接口类型与错误映射完整。
- 验证：`npm run lint && npm run typecheck`

### PE-FE-CL-02 (endpoint page)
- 目标：催款批次创建页（截止日+客户过滤）。
- Allowlist:
  - `frontend/src/modules/collections/pages/DunningCreate.vue` (new)
- 依赖：PE-FE-CL-01
- 验收：成功创建后跳转详情或列表。
- 验证：`npm run lint && npm run typecheck`

### PE-FE-CL-03 (endpoint page)
- 目标：催款列表/详情页。
- Allowlist:
  - `frontend/src/modules/collections/pages/DunningList.vue` (new)
  - `frontend/src/modules/collections/pages/DunningDetail.vue` (new)
- 依赖：PE-FE-CL-02
- 验收：支持轮次/状态筛选与行明细查看。
- 验证：`npm run lint && npm run typecheck`

### PE-FE-CL-04 (endpoint page)
- 目标：在账单详情页接入坏账标记/恢复动作。
- Allowlist:
  - `frontend/src/modules/billing/pages/BillDetail.vue`
- 依赖：PE-FE-CL-01
- 验收：按钮权限可控，状态变化可视化。
- 验证：`npm run lint && npm run typecheck`

---

## FE-B3 — Commission

### PE-FE-COM-01 (service)
- 目标：新增 commission API client（规则/记录/结算/报表）。
- Allowlist:
  - `frontend/src/api/commission.ts` (new)
  - `frontend/src/api/commission.types.ts` (new)
- 依赖：PE-BE-COM-01~10
- 验收：所有 commission 端点有类型封装。
- 验证：`npm run lint && npm run typecheck`

### PE-FE-COM-02 (endpoint page)
- 目标：提成规则管理页。
- Allowlist:
  - `frontend/src/modules/commission/pages/CommissionRuleList.vue` (new)
- 依赖：PE-FE-COM-01
- 验收：新增/编辑/启停规则可用。
- 验证：`npm run lint && npm run typecheck`

### PE-FE-COM-03 (endpoint page)
- 目标：提成记录查询页（agent/case/status/date 过滤）。
- Allowlist:
  - `frontend/src/modules/commission/pages/CommissionList.vue` (new)
- 依赖：PE-FE-COM-01
- 验收：列表分页与筛选可用。
- 验证：`npm run lint && npm run typecheck`

### PE-FE-COM-04 (endpoint page)
- 目标：结算批次页（创建批次、生成明细、查看报表）。
- Allowlist:
  - `frontend/src/modules/commission/pages/CommissionSettlement.vue` (new)
- 依赖：PE-FE-COM-01
- 验收：批次状态与统计结果可视化。
- 验证：`npm run lint && npm run typecheck`

---

## FE-B4 — Consulting/Search + Expense

### PE-FE-CS-01 (endpoint page)
- 目标：顾问/检索项目立案页。
- Allowlist:
  - `frontend/src/modules/consulting/pages/ConsultingCaseCreate.vue` (new)
  - `frontend/src/api/consulting.ts` (new)
  - `frontend/src/api/consulting.types.ts` (new)
- 依赖：PE-BE-CS-01
- 验收：支持创建 CONSULTING/SEARCH 项目并校验专属字段。
- 验证：`npm run lint && npm run typecheck`

### PE-FE-CS-02 (endpoint page)
- 目标：支出录入与列表页（可复用于普通案件与顾问项目）。
- Allowlist:
  - `frontend/src/modules/expenses/pages/ExpenseList.vue` (new)
  - `frontend/src/modules/expenses/pages/ExpenseCreate.vue` (new)
  - `frontend/src/api/expenses.ts` (new)
  - `frontend/src/api/expenses.types.ts` (new)
- 依赖：PE-BE-CS-02, PE-BE-CS-03
- 验收：按案件/类别/时间筛选。
- 验证：`npm run lint && npm run typecheck`

### PE-FE-CS-03 (endpoint page)
- 目标：顾问/检索服务费草单生成页。
- Allowlist:
  - `frontend/src/modules/consulting/pages/ConsultingFeeDraftCreate.vue` (new)
- 依赖：PE-BE-CS-05
- 验收：支持固定/工时/混合模式参数输入。
- 验证：`npm run lint && npm run typecheck`

### PE-FE-CS-04 (endpoint page)
- 目标：顾问项目收益视图（收入/支出/毛利）。
- Allowlist:
  - `frontend/src/modules/consulting/pages/ConsultingProfitability.vue` (new)
- 依赖：PE-BE-CS-06
- 验收：能按项目查看收益指标。
- 验证：`npm run lint && npm run typecheck`

---

## FE-B5 — 集成与质量硬化

### PE-FE-QA-01 (service)
- 目标：统一新增模块路由、菜单、权限 gate（不影响旧菜单行为）。
- Allowlist:
  - `frontend/src/router/index.ts`
  - `frontend/src/constants/menu.ts`
- 依赖：FE-B1~B4 完成
- 验收：新模块可访问，旧模块不回归。
- 验证：`npm run lint && npm run typecheck`

### PE-FE-QA-02 (service)
- 目标：新增页面响应式与 a11y 最低标准修复（键盘可达、语义标签、错误提示可读）。
- Allowlist:
  - `frontend/src/modules/**/pages/*.vue`（仅新增页面）
  - `frontend/src/styles/*.css`（必要最小变更）
- 依赖：PE-FE-QA-01
- 验收：桌面/移动端均可用，基础可访问性通过人工检查。
- 验证：`npm run lint && npm run typecheck && npm run build`

### PE-FE-QA-03 (doc)
- 目标：补充新增业务链路手工冒烟文档。
- Allowlist:
  - `docs/frontend_smoke_flows.md`
  - `docs/FPMS_Frontend_Manual_Test_User_Guide.md`
- 依赖：PE-FE-QA-01
- 验收：覆盖 annuity/collections/commission/consulting/expense。
- 验证：文档自检。

---

## 2. 每个任务统一验证模板
```bash
cd frontend
npm run lint
npm run typecheck
# 页面/路由改动任务建议额外执行
npm run build
```

## 3. 多 Agent 并行建议
- 可并行：
  - 不同模块下新建页面任务（`annuity` vs `commission` vs `consulting`）
  - API client 新文件任务
- 必须串行：
  - `router/index.ts`、`constants/menu.ts`、`stores/auth.ts`
  - 同一页面文件的多次改动任务
