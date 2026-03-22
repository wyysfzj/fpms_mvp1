# FPMS MVP1 前端手工测试指南（后端已启动）

本指南用于你在完成 **NEXT‑1/2/3** 后，对前端做一次**可复现、可记录证据**的手工测试（从启动前端开始）。

**已知信息（来自运行冒烟证据）：**
- 后端 Base URL：`http://localhost:8000/api/v1`
- 登录接口：`POST /api/v1/auth/login`（JSON）
- 登录返回 token 字段：`access_token`
- 测试账号：`admin / admin123`  
这些信息已在 FE‑3 运行冒烟证据中验证。 fileciteturn0file0

---

## 0. 测试准备（强烈建议）

### 0.0 DEMO-UI 模式说明

当环境变量 `VITE_DEMO_UI=1` 时，前端启用演示层：
- **Style-B 主题**：`body` 添加 `style-b` 类，侧边栏激活态/悬浮态使用 CSS 变量覆盖
- **全站中文化**：所有按钮、表格列头、对话框、空状态文本均为中文（源自 `labels.zh.ts`）
- **分组菜单**：侧边栏按 工作台/案件管理/期限监控/客户中心/系统设置 分组
- **工作台 KPI**：工作台显示 4 个统计卡片与待办任务表格

本指南中的历史英文按钮名称（如 "New Case"、"Edit Case"）在 Demo 模式下对应中文标签（如 "新建案件"、"编辑案件"）。完整映射见 `docs/frontend_smoke_flows.md` 第 9 节。

如需测试 Demo 层，请确保 `.env` 中设置 `VITE_DEMO_UI=1` 后再启动前端。

### 0.1 建议准备的“证据采集工具”
- 浏览器开发者工具（DevTools：Network + Console）
- 终端（用于保存 curl 输出 / 启动日志）
- 截图工具（关键页面与关键错误提示）

### 0.2 建议的“证据记录模板”（复制到你自己的测试记录里）
- 测试时间：
- 前端提交版本（commit / tag）：
- 后端提交版本（commit / tag）：
- 前端启动命令与端口：
- 后端启动命令与端口（你已启动）：
- 测试账号：
- 结论：通过 / 部分通过 / 失败
- 失败项清单（每条包含：页面/步骤/期望/实际/requestId/截图）

---

## 1. 后端连通性确认（你已启动，但建议再确认一次）

在终端执行（不带 token 预期返回 401，而不是 000）：

```bash
curl -i "http://localhost:8000/api/v1/clients?page=1&page_size=1"
```

**预期：**
- HTTP 401，且 body 为标准错误包（`{"error":{"code","message","details"}}}`）
- 响应头通常包含 `x-request-id`（用于定位问题）
你们之前的冒烟也观察到了这种返回。 fileciteturn0file0

如果这里不是 401/403/200，而是 `000`，说明端口/服务仍不通——此时不要继续测前端。

---

## 2. 手工启动前端（Vite）

### 2.1 安装依赖（首次或依赖变更后）
```bash
cd frontend
npm install
```

### 2.2 启动开发服务器
```bash
npm run dev
```

**预期：**
- 终端输出类似：
  - `VITE vX.Y.Z  ready in ...`
  - `Local: http://localhost:5173/`（端口以实际输出为准）
- 浏览器访问该地址后应能加载登录页或自动重定向到登录页。

### 2.3 确认前端指向正确的后端 Base URL
在前端界面打开后，建议在 DevTools Console 查看应用是否打印了 API baseURL（若有 About/Debug 页也可从那里确认）。
若无界面提示，则用 Network 面板确认请求是否发往：
- `http://localhost:8000/api/v1/...`

---

## 3. 登录与会话

### 3.1 登录
1) 打开前端页面（Vite 本地地址）  
2) 输入：
   - username：`admin`
   - password：`admin123`
3) 点击登录

**预期：**
- 调用 `POST /api/v1/auth/login`，返回 200，响应含 `access_token`。 fileciteturn0file0
- 登录成功后进入应用主框架（侧边栏 + 顶栏 + 内容区）

### 3.2 token 持久化验证（localStorage）
1) 登录成功后，打开 DevTools → Application → Local Storage  
2) 找到 token（key 名以实现为准）  
3) 刷新页面（F5），应保持登录态，不应回到登录页。

### 3.3 401 路由守卫验证
1) 在 Local Storage 中删除 token  
2) 访问一个受保护页面（例如 `/clients`）  
**预期：**
- 自动跳转到登录页（或提示未登录）

---

## 4. 前端可复用错误码与状态码处理规范（对齐后端 Envelope）

> 目的：把错误处理沉淀为可复用规则，供所有页面/弹窗/表单统一使用。

### 4.1 后端错误包（Envelope）与 requestId 读取规则
后端错误响应统一按以下结构处理：

```json
{
  "error": {
    "code": "SOME_CODE",
    "message": "可读错误信息",
    "details": {}
  }
}
```

前端统一规则：
- 从响应头读取 `x-request-id`（大小写不敏感，Axios 中通常为小写键）。
- 界面错误文案统一追加 requestId：`{message}（请求ID：{requestId}）`；若无 requestId，仅显示 message。
- 日志/测试记录最少保留：`path + method + status + error.code + requestId`。
- 对 403 若 `details.required_perm` 存在，页面应可显示“所需权限”。

### 4.2 状态码处理矩阵（400/401/403/404/409/422）
| HTTP | 后端语义 | 前端处理（可复用） |
|---|---|---|
| 400 | 业务校验失败（BusinessError） | 显示业务错误提示（banner/toast）；保留当前表单输入；展示 requestId。 |
| 401 | 未认证/登录失效 | 清理本地 token；跳转登录页；提示“会话已过期，请重新登录”。 |
| 403 | 无权限 | 跳转或展示无权限页面；展示 `required_perm`（若有）与 requestId。 |
| 404 | 资源不存在 | 列表页提示“数据不存在或已删除”；详情页跳转 NotFound 或返回列表。 |
| 409 | 冲突/重复/配置缺失 | 用“冲突/已存在/当前状态不允许”语义提示；引导用户修正输入后重试。 |
| 422 | 请求参数校验失败 | `details.errors`/字段错误映射到表单项；同时显示页面级错误摘要与 requestId。 |

### 4.3 页面层统一落地流程（建议）
1) API 调用失败后，先走统一错误归一化（`status/code/message/details/requestId`）。  
2) 按 4.2 矩阵分支处理；禁止每个页面自定义“另一套”错误语义。  
3) 表单页优先展示字段错误（422），再展示全局 banner（400/409 等）。  
4) 任何可见错误提示都应支持携带 requestId，便于后端日志定位。  

### 4.4 全局错误交互验证用例（含 requestId）
#### 4.4.1 400 业务校验失败
- 在任意业务动作中构造业务校验失败（如状态不允许的操作）。
**预期：**
- 显示业务错误 message；
- 保留当前页面上下文；
- 错误提示包含 requestId（若后端返回）。

#### 4.4.2 401 未认证
- 删除 Local Storage token 后直接访问受保护页面（如 `/clients`）。
**预期：**
- 自动跳转登录页；
- 已失效会话不应继续调用受保护接口；
- 如显示错误提示，应包含 requestId（若有）。

#### 4.4.3 403 权限不足
- 用低权限账号访问受限动作。
**预期：**
- 显示无权限页面/卡片；
- 如后端返回 `required_perm`，页面可见；
- requestId 可见。

#### 4.4.4 404 资源不存在
- 手工访问不存在资源详情（如 `/cases/<不存在ID>`）。
**预期：**
- 显示“资源不存在/已删除”语义；
- 页面可恢复（返回列表或 NotFound）；
- requestId 可见（若有）。

#### 4.4.5 409 冲突
- 案件：重复 `case_no` 提交（你们运行冒烟中出现过 duplicate case_no 的 409） fileciteturn0file1
**预期：**
- 冲突语义提示明确；
- 不出现空白页；
- requestId 可见（若有）。

#### 4.4.6 422 参数校验错误（表单字段错误）
在任一创建表单故意漏填必填字段提交：
- Clients：必填字段（如 name_cn 映射后的字段）
- 任务：`due_date` 必填（你们运行合同修复里明确了 due_date 是必填） fileciteturn0file1
**预期：**
- 字段级错误显示在对应输入项附近；
- 非字段错误显示在页面顶部 banner；
- requestId 可见（若后端返回）。

---

## 5. 业务链路手工冒烟（按模块顺序）

下列步骤覆盖 MVP1 核心模块。建议你边测边在 Network 面板记录：
- URL + method
- status
- requestId（若有）
- 错误包（若失败）

### 5.1 客户（Clients）
**目标：** 列表 → 新建 → 编辑 → 停用
1) 进入客户列表（侧边栏点击或直接路由 `/clients`）
   - 预期：列表加载成功；分页可用
2) 点击`新建客户`
   - 填写必要字段提交
   - 预期：201/200，回到列表或显示成功提示
3) 编辑客户
   - 修改并保存
4) 停用客户
   - 预期：状态变化；列表可反映

### 5.2 案件（Cases）
**目标：** 列表 → 新建（关联客户）→ 详情 → 编辑 → 快速编辑
1) 进入案件列表 `/cases`
2) 新建案件
   - 选择/填写 client_id（或通过 UI 选择客户）
   - case_no 需要唯一（避免 409）
3) 进入案件详情 `/cases/:id`
4) 编辑 / 快速编辑
   - 提交成功后 detail 刷新

**沉浸模式（如有该开关）：**
- 在案件详情长文本标签页（如 Claims）切换沉浸模式
- 预期：布局变为单栏阅读流，侧栏/时间线隐藏，排版更适合阅读（参考 `reference/case_detail.html` 的行为范式）

### 5.3 任务（Tasks）
**目标：** 列表 → 新建（case_id + due_date）→ 关闭/重开/取消 → 今日任务
1) `/tasks` 列表加载
2) 新建任务 `/tasks/new`
   - 必填：`case_id`、`due_date`
3) 在列表行操作中执行关闭/重开/取消
4) `/tasks/today`
   - 切换 worker / supervisor（如界面存在）

### 5.4 文书（Documents）
**目标：** 列表 → 新建 → 详情 → 上传/下载附件
1) `/documents` 列表
2) 新建文书 `/documents/new`
   - 注意：你们之前合同修复指出 `doc_date`、`doc_template_id` 等字段存在“key 必须出现”的要求（doc_template_id 可为 null 但 key 需要存在） fileciteturn0file1
3) 进入 detail `/documents/:id`
4) 上传附件
   - NEXT‑1 完成后：预期 upload 返回 2xx，不再 500；失败也应显示 requestId
5) 下载附件
   - 预期：浏览器触发下载（blob）

### 5.5 费用（Fees）
**目标：** 费率 → 草稿 → 明细项 → 锁定/解锁
1) 费率页（Fee rates）：创建/编辑费率（fee_code/fee_type 等应按你们修复后的字段）
2) Fee drafts：创建草稿
3) 草稿详情：添加明细项、编辑明细项、删除明细项
4) lock/unlock：锁定后明细项不可编辑

### 5.6 账单（Billing）
**目标：** 账单 → 回款 → 打印 → 核销 → 收款汇总（如支持）
1) 账单列表 `/billing/bills`
2) 新建账单（从 drafts 或 manual 模式）
3) 打印账单
   - NEXT‑2 完成后：预期不再 409（模板未配置），应返回 200 blob 并下载/预览
4) 回款
   - 创建 payment（注意 client_id 等字段应由界面或适配层保证）
5) 核销
   - NEXT‑3 完成后：创建 offset 需要有效 `payment_line_id`；应能在界面中选择并创建成功
6) 案件收款汇总
   - 若你们后端/数据支持，应能显示 summary；否则记录 404/empty 的原因

### 5.7 系统配置（模板/参数/信头）
**目标：** 模板/参数/信头
1) 模板列表与创建（注意：你们运行证据指出模板上传在后端是 metadata-only（file_path）语义，而不是 multipart 上传语义） fileciteturn0file1
2) 参数列表与 upsert
3) 信头列表与创建

### 5.8 DEMO-UI 层验证（VITE_DEMO_UI=1 时执行）

> 此节验证 DEMO-UI FIX-01/02/03 的修复效果。需在 `VITE_DEMO_UI=1` 模式下运行前端。

#### 5.8.1 Style-B 主题 — 侧边栏激活态（FIX-01）
1) 打开 DevTools → Elements，确认 `body` 有 `style-b` class
2) 点击任一侧边栏菜单项
3) 检查激活项 `.nav-item.router-link-active` 的 computed style：
   - `background-color` 应为 `#EFF6FF`
   - `color` 应为 `#2563EB`
4) 悬浮在另一个非激活菜单项上：
   - `background-color` 应为 `#F1F5F9`

#### 5.8.2 列表页中文标签（FIX-03）
遍历以下列表页，确认所有 UI 标签为中文：
- `/cases` — 标题「案件列表」，列头「编号/案号/标题/客户/状态/更新时间/操作」，按钮「新建案件」
- `/tasks` — 标题「任务列表」，列头含「优先级/截止日期/负责人」
- `/billing/bills` — 标题「账单列表」，列头含「账单号/金额/余额/开票日」
- `/fees/drafts` — 标题「费用草稿」，列头含「草稿编号/币种」
- `/documents` — 标题「往来文件列表」，列头含「方向/类型/日期」

#### 5.8.3 详情页中文标签（FIX-02）
进入以下详情页，确认所有 UI 标签为中文：
- `/cases/{id}` — 按钮「返回/编辑案件」，tab「概览/申请人/发明人/往来文件/费用/账单与收款/任务」，字段标签「案件信息/案号/标题/客户/状态/申请日/优先权日/备注」
- `/documents/{id}` — 按钮「返回/编辑往来文件」，标签「文件内容/文件信息/编号/方向/创建时间/更新时间」
- `/fees/drafts/{id}` — 按钮「返回/刷新/锁定/解锁」，tab「明细/概览」，标签「草稿信息/草稿编号/状态/案件编号/客户编号/类型/币种」
- `/billing/bills/{id}` — 按钮「返回/打印账单/刷新」，tab「明细/概览」，列头「描述/数量/单价/金额」，标签「账单信息/账单号/客户/案件/币种/开票日/到期日」

#### 5.8.4 确认对话框中文（FIX-02/03）
- 任务列表点击「操作 → 关闭」 — 弹窗标题「关闭任务」，确认按钮「关闭」
- 费用草稿详情点击「🔒 锁定」 — 弹窗标题「锁定草稿」，确认按钮「锁定」

#### 5.8.5 无英文泄漏检查
在 Demo 模式下完整浏览所有页面，确认：
- 无英文按钮标签、表头、空状态文本
- 例外：数据值（状态码 `OPEN`/`LOCKED`、币种 `CNY` 等）保持英文大写，属于数据而非 UI 标签

### 5.9 年费（Annuity）
**目标：** 年费任务 → 草单生成 → 官费清单 → 官方缴费登记

**页面路由（前端）**
- `/annuity/tasks`
- `/annuity/pay-lists`
- `/annuity/gov-payments/new`

**建议步骤**
1) 进入 `/annuity/tasks`，确认列表与筛选可用。  
2) 点击某行 `编辑指示`，提交后提示成功。  
3) 勾选多条任务，点击 `批量生成草单`，核对回执弹窗中的成功/失败明细。  
4) 进入 `/annuity/pay-lists`，输入费用项编号并点击 `生成官费清单`。  
5) 在回执区点击 `登记缴费`，应跳转到 `/annuity/gov-payments/new` 且自动带入参数。  
6) 提交官方缴费登记，核对结果卡片中的缴费记录与清单状态。  

**对应 API（后端）**
- `GET /annuity/tasks` -> `200`
- `PUT /annuity/tasks/{id}/instruction` -> `200`
- `POST /annuity/tasks/generate-drafts` -> `200`
- `POST /pay-lists/from-fee-items` -> `200`
- `POST /gov-payments` -> `200`

### 5.10 催款（Collections）
**目标：** 催款批次列表 → 创建催款批次 → 详情校验

**页面路由（前端）**
- `/collections/dunning`
- `/collections/dunning/new`
- `/collections/dunning/{id}`

**建议步骤**
1) 进入 `/collections/dunning`，验证筛选（轮次、状态）与分页。  
2) 点击 `创建催款批次` 进入 `/collections/dunning/new`。  
3) 填写 `截止日期`，按需要选择客户范围并提交。  
4) 成功后检查跳转：单批次应进入详情，多批次返回列表。  
5) 在详情页核对批次号、轮次、状态、金额、日期是否正确。  

**对应 API（后端）**
- `GET /dunning` -> `200`
- `POST /dunning` -> `200/201`（以后端实现为准）

### 5.11 提成（Commission）
**目标：** 规则维护 → 记录查询 → 结算批次与报表

**页面路由（前端）**
- `/commission/rules`
- `/commission`（兼容别名 `/commission/records`）
- `/commission/settlements`

**建议步骤**
1) 进入 `/commission/rules`，新增规则并保存。  
2) 编辑同一规则，切换启用/停用并确认列表状态变化。  
3) 进入 `/commission`，按案件/代理人/状态查询记录。  
4) 进入 `/commission/settlements`，创建结算批次。  
5) 使用批次 ID 点击 `生成明细`，确认统计值更新。  
6) 在报表区设置筛选后点击 `查询报表`，核对统计卡与明细表。  

**对应 API（后端）**
- `GET /commission/rules` -> `200`
- `POST /commission/rules` -> `201/200`
- `PUT /commission/rules/{id}` -> `200`
- `GET /commission` -> `200`
- `POST /commission/settlements` -> `201/200`
- `POST /commission/settlements/{id}/generate-lines` -> `200`
- `GET /commission/reports/settlement` -> `200`

### 5.12 顾问（Consulting）
**目标：** 项目立案 → 服务费草单 → 项目收益查询

**页面路由（前端）**
- `/consulting/cases/new`
- `/consulting/fee-drafts/new`
- `/consulting/profitability`

**建议步骤**
1) 进入 `/consulting/cases/new`，按项目类型填写必填项并提交。  
2) 提交成功后应跳转 `/cases/{id}`（项目映射到案件详情）。  
3) 进入 `/consulting/fee-drafts/new`，按 `FIXED/HOURLY/HYBRID` 任一模式填写并提交。  
4) 核对结果区域：草单 ID、草单金额、明细行数。  
5) 进入 `/consulting/profitability`，输入项目 ID 后查询收益。  
6) 核对“应收/已收/支出/毛利/毛利率”及支出分类统计。  

**对应 API（后端）**
- `POST /consulting/cases` -> `201/200`
- `POST /consulting/fee-drafts` -> `201/200`
- `GET /cases/{id}/receipts` -> `200`（无汇总时可能 `404`）
- `GET /expenses`（`case_id` 过滤）-> `200`

### 5.13 支出（Expense）
**目标：** 支出列表筛选 → 新增支出 → 列表与统计回显

**页面路由（前端）**
- `/expenses`
- `/expenses/new`

**建议步骤**
1) 进入 `/expenses`，按项目编号、类别、日期范围筛选。  
2) 点击 `录入支出` 进入 `/expenses/new`。  
3) 填写必填字段（案件/项目编号、支出类别、支出日期、金额、币种）并提交。  
4) 返回列表后确认新记录可见，统计卡（总笔数/总金额）同步变化。  

**对应 API（后端）**
- `GET /expenses` -> `200`
- `POST /expenses` -> `201/200`

---

## 6. 手工测试“快速回归”清单（10–15 分钟）
当你只想快速确认“没有回归”，跑下面 12 条即可：

1) 前端 `npm run dev` 能启动并打开页面  
2) `admin` 登录成功（拿到 token） fileciteturn0file0  
3) 客户列表加载 + 新建客户成功  
4) 案件新建 + 进入详情成功  
5) 任务新建（case_id + due_date）成功  
6) 文书新建 + 上传附件成功（NEXT‑1 验证点）  
7) 账单打印成功（NEXT‑2 验证点）  
8) 核销创建成功（NEXT‑3 验证点）  
9) `/annuity/tasks` 批量生成草单成功  
10) `/collections/dunning/new` 创建催款批次成功  
11) `/commission/settlements` 创建批次并生成明细成功  
12) `/consulting/profitability` 与 `/expenses` 查询成功

---

## 7. 出现问题时如何记录（最小可修复证据）
对任何失败步骤，请至少记录：
- 页面路由（例如 `/documents/xxx`）
- 触发动作（按钮名）
- 网络请求：URL + status + response body
- `x-request-id`（如果有）
- 后端 uvicorn 控制台报错栈（如果是 500）
- 截图（错误提示 + 控制台/网络详情）

这样你再交给 Codex/Claude/Gemini 修复时，就能完全基于证据推进，避免猜测。
