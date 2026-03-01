# 前端 UI 冒烟流程（MVP1）

## 适用范围
本运行手册用于 MVP1 前端手工冒烟，使用绝对路由与可复现操作步骤。

> **DEMO-UI 模式（VITE_DEMO_UI=1）**：启用 Demo 层后，界面标签为中文。文中若出现历史英文按钮名（如 `New Case`、`View`），请按其中文按钮名执行；完整映射见第 9 节。

## 全局前置条件
- Backend API 已启动：`http://localhost:8000/api/v1`
- Frontend 已启动：`http://localhost:5173`
- 数据库已迁移并完成 seed（`admin/admin123` 可登录）
- 浏览器无陈旧登录态（建议先清理 localStorage）

## 全局错误与 RequestId 处理
- API 错误在 `http.ts` / `errors.ts` 做统一归一化。
- `requestId` 来源：响应头 `X-Request-Id`。
- `requestId` 显示位置：
  - 登录页错误提示（`/login`）
  - 业务页面 `ApiErrorBanner`（`Request ID: <code>`）
  - 无权限页（`/forbidden`）中的 `rid`

## 1) 登录与会话链路（Auth / Session）
### 前置条件
- 测试用户存在（`admin/admin123`）。

### UI 步骤
1. 打开 `/login`。
2. 输入用户名与密码。
3. 点击登录。
4. 验证跳转到 `/dashboard`。
5. 使用错误密码提交，验证失败提示。

### 预期 API
- `POST /auth/login`
  - `200`：登录成功。
  - `401`：账号或密码错误。
  - `422`：请求参数校验错误。

### 预期 UI
- 成功：进入登录后主框架，侧边栏可见。
- 失败：登录页展示行内错误。

### 失败语义（401/403/422/409）
- `401`：提示账号或密码错误，若返回 `requestId` 则显示。
- `403`：该接口通常不返回。
- `422`：提示参数格式错误。
- `409`：该接口通常不返回。

## 2) 客户链路（列表 / 新建 / 编辑 / 停用）
### 前置条件
- 当前账号具有客户模块权限。

### UI 步骤
1. 打开 `/clients`。
2. 点击`新建客户`。
3. 填写客户名称与可选联系字段。
4. 点击`创建客户`。
5. 在列表行菜单（`⋮`）点击`编辑`。
6. 点击`保存变更`。
7. 在编辑页点击`停用`并确认。

### 预期 API
- `GET /clients?page=1&page_size=20` -> `200`。
- `POST /clients` -> `201`（或 `422`）。
- `GET /clients/{id}` -> `200`。
- `PUT /clients/{id}` -> `200`。
- `PUT /clients/{id}/deactivate` -> `200`。

### 预期 UI
- 列表支持分页、空态、错误态。
- 新建/编辑页显示字段级校验提示。
- 停用后返回列表并出现成功提示。

### 失败语义（401/403/422/409）
- `401`：清理 token 后跳转 `/login`。
- `403`：跳转 `/forbidden`，展示权限与 `requestId`。
- `422`：字段错误或 banner 错误提示。
- `409`：业务冲突通过 banner/toast 提示。

## 3) 案件链路（列表 / 新建 / 详情 / 编辑 / 快速编辑）
### 前置条件
- 至少存在 1 个可用客户（用于创建案件）。

### UI 步骤
1. 打开 `/cases`。
2. 点击`新建案件`。
3. 填写案号、标题并选择客户。
4. 点击`创建案件`。
5. 在列表中点击`查看`进入详情。
6. 点击`编辑案件`并保存。
7. 在详情页打开`快速编辑`，修改备注并保存。

### 预期 API
- `GET /cases?page=1&page_size=20` -> `200`。
- `GET /clients?page=1&page_size=100` -> `200`。
- `POST /cases` -> `201`。
- `GET /cases/{id}` -> `200`。
- `PUT /cases/{id}` -> `200`。
- `POST /cases/{id}/limited-edit` -> `200`。

### 预期 UI
- 详情页展示头部信息卡与分栏标签。
- 快速编辑保存后刷新详情数据。

### 失败语义（401/403/422/409）
- `401`：跳转 `/login`。
- `403`：跳转 `/forbidden` 并显示 `requestId`。
- `422`：表单校验错误可见。
- `409`：如重复案号，显示冲突提示。

## 4) 任务链路（列表 / 新建 / 关闭 / 重开 / 取消 / 今日）
### 前置条件
- 至少存在 1 个案件（用于创建任务）。

### UI 步骤
1. 打开 `/tasks`。
2. 点击`新建任务`。
3. 填写标题、案件 ID 与其它可选字段。
4. 点击`创建任务`。
5. 在列表行菜单（`⋮`）执行`关闭`/`重开`/`取消`并确认。
6. 打开 `/tasks/today`，切换`我的任务`与`团队任务`。

### 预期 API
- `GET /tasks?page=1&page_size=20` -> `200`。
- `POST /tasks` -> `201`。
- `POST /tasks/{id}/close` -> `200`。
- `POST /tasks/{id}/reopen` -> `200`。
- `POST /tasks/{id}/cancel` -> `200`。
- `GET /tasks/today?as=worker|supervisor` -> `200`。

### 预期 UI
- 列表支持加载态/空态/错误态/分页。
- 状态流转弹窗与成功提示正常。
- 今日任务页可按模式切换展示。

### 失败语义（401/403/422/409）
- `401`：跳转 `/login`。
- `403`：跳转 `/forbidden` 并展示 `requestId`。
- `422`：字段或页面级错误提示可见。
- `409`：少见，若返回则通过 banner/toast 展示。

## 5) 文书链路（列表 / 新建 / 详情 / 上传 / 下载）
### 前置条件
- 若后端策略要求 `case_id`，需准备可用案件。

### UI 步骤
1. 打开 `/documents`。
2. 点击`新建文书`。
3. 填写标题、可选案件 ID 与元数据。
4. 点击`创建文书`。
5. 打开 `/documents/{id}` 详情页。
6. 在`附件`区域点击`上传文件`并选择本地文件。
7. 点击下载按钮触发附件下载。

### 预期 API
- `GET /documents?page=1&page_size=20` -> `200`。
- `POST /documents` -> `201`。
- `GET /documents/{id}` -> `200`。
- `GET /documents/{id}` 返回中包含 `attachments`。
- `POST /documents/{id}/attachments` -> `201`。
- `GET /documents/{id}/attachments/{attachment_id}/download` -> `200`（blob）。

### 预期 UI
- 详情页显示文书元数据与附件区域。
- 上传后列表刷新，下载触发浏览器保存。

### 失败语义（401/403/422/409）
- `401`：跳转 `/login`。
- `403`：跳转 `/forbidden` 并展示 `requestId`。
- `422`：表单或 payload 校验错误可见。
- `409`：冲突错误通过 banner 提示。

## 6) 费用链路（费率 / 草稿 / 明细项 / 锁定）
### 前置条件
- 草稿创建所需案件已存在。
- 如后端要求 `rate_id`，先准备费率数据。

### UI 步骤
1. 打开 `/fees/rates`，点击`新建费率`并提交。
2. 打开 `/fees/drafts`，点击`新建草稿`，填写 `Case ID` 并提交。
3. 打开 `/fees/drafts/{id}`。
4. 在`明细`标签点击`+ 添加项目`，填写后保存。
5. 点击`锁定`（或`解锁`）并确认。

### 预期 API
- 费率：
  - `GET /fees/rates?page=1&page_size=50` -> `200`。
  - `POST /fees/rates` -> `201`。
  - `PUT /fees/rates/{id}` -> `200`。
- 草稿：
  - `GET /fees/drafts?page=1&page_size=20` -> `200`。
  - `POST /fees/drafts` -> `201`。
  - `GET /fees/drafts/{id}` -> `200`。
- 明细项：
  - `POST /fees/drafts/{id}/items` -> `201`。
  - `PUT /fees/drafts/{id}/items/{item_id}` -> `200`。
  - `DELETE /fees/items/{item_id}` -> `204`。
- 锁定：
  - `POST /fees/drafts/{id}/lock` -> `200`。
  - `POST /fees/drafts/{id}/unlock` -> `200`。

### 预期 UI
- 费率与草稿列表支持分页与异常提示。
- 草稿锁定后进入只读状态。

### 失败语义（401/403/422/409）
- `401`：跳转 `/login`。
- `403`：跳转 `/forbidden` 并展示 `requestId`。
- `422`：对话框或页面显示校验错误。
- `409`：锁定冲突/编辑冲突提示可见。

## 7) 账单链路（账单 / 打印 / 回款 / 核销 / 收款汇总）
### 前置条件
- 已有费用草稿与客户数据。
- 进行打印冒烟前需完成模板准备：
  - `scripts/dev/setup_printing.sh <BILL_ID>`
  - `BILL_ID` 可来自 `/billing/bills` 或 `GET /bills?page=1&page_size=20`
  - 预期准备成功信号：`GET /bills/{id}/print` 返回 `200` 且为 DOCX blob

### UI 步骤
1. 打开 `/billing/bills`。
2. 打开 `/billing/bills/new`。
3. 在`从费用草稿`或`手工录入`页签创建账单。
4. 打开 `/billing/bills/{id}`。
5. 点击`打印账单`。
6. 打开 `/billing/payments`，点击`登记回款`并提交。
7. 在回款页点击`创建核销`，选择回款、回款行、账单并提交。
8. 打开 `/cases/{id}` 的账单/收款相关标签，查看汇总。

### 预期 API
- 账单：
  - `GET /bills?page=1&page_size=20` -> `200`。
  - `POST /bills/from-drafts` -> `201`。
  - `POST /bills/manual` -> `201`。
  - `GET /bills/{id}` -> `200`。
  - `GET /bills/{id}/print` -> `200`（blob）。
- 回款/核销：
  - `GET /payments?page=1&page_size=20` -> `200`。
  - `POST /payments` -> `201`。
  - `GET /offsets` 当前后端未暴露。
  - `POST /offsets` -> `201`。
  - `POST /offsets/{id}/reverse` -> `201`。
- 收款汇总：
  - `GET /cases/{id}/receipts` -> `200`（无数据时可能 `404`）。

### 预期 UI
- 账单详情有`明细/概览`并可执行打印。
- 回款页显示回款与核销区域。
- 案件页可显示收款汇总组件。

### 失败语义（401/403/422/409）
- `401`：跳转 `/login`。
- `403`：跳转 `/forbidden` 并展示 `requestId`。
- `422`：表单提交错误可见。
- `409`：例如打印模板未配置，出现冲突提示。

## 8) 系统配置链路（模板/参数/信头）
### 前置条件
- 已登录且具备系统配置权限。

### UI 步骤
1. 打开 `/system/doc-templates`，点击`新增模板`并保存。
2. 打开 `/system/task-templates`，点击`新增模板`并保存。
3. 打开 `/system/params`，在`新增参数`填写键值并提交。
4. 打开 `/system/letterheads`，点击`新增信头`并提交。

### 预期 API
- 文件模板：
  - `GET /doc-templates?page=1&page_size=20` -> `200`。
  - `POST /doc-templates` -> `201`（部分环境可能 `200`）。
  - `PUT /doc-templates/{id}` -> `200`。
- 任务模板：
  - `GET /task-templates` -> `200`。
  - `POST /task-templates` -> `201`（部分环境可能 `200`）。
  - `PUT /task-templates/{id}` -> `200`。
- 系统参数：
  - `GET /system/params` -> `200`。
  - `PUT /system/params/{key}` -> `200`。
- 信头：
  - `GET /letterheads` -> `200`。
  - `POST /letterheads` -> `201`（部分环境可能 `200`）。

### 预期 UI
- 新增/编辑后列表刷新并出现成功提示。
- `422/400` 错误在弹窗或 `ApiErrorBanner` 中可见。

### 失败语义（401/403/422/409）
- `401`：跳转 `/login`。
- `403`：跳转 `/forbidden` 并展示 `requestId`。
- `422`：字段级校验错误可见。
- `409`：编码冲突等通过 banner/toast 展示。

## 8A) 新增业务链路手工冒烟（PE-FE-QA-03）
### 8A.1 年费链路（annuity）
#### 路由与页面
- `/annuity/tasks`：年费任务列表（筛选、编辑指示、批量生成草单）。
- `/annuity/pay-lists`：官费清单生成与回执。
- `/annuity/gov-payments/new`：官方缴费登记。

#### UI 步骤
1. 打开 `/annuity/tasks`，确认列表与筛选可用。
2. 任选任务点击`编辑指示`并保存。
3. 勾选多条任务后点击`批量生成草单`，确认回执弹窗出现。
4. 打开 `/annuity/pay-lists`，输入费用项编号并点击`生成官费清单`。
5. 在回执中点击`登记缴费`，跳转 `/annuity/gov-payments/new` 且参数自动带入。
6. 在 `/annuity/gov-payments/new` 提交登记并核对结果卡片。

#### 预期 API 与结果
- `GET /annuity/tasks` -> `200`。
- `PUT /annuity/tasks/{taskId}/instruction` -> `200`。
- `POST /annuity/tasks/generate-drafts` -> `200`。
- `POST /pay-lists/from-fee-items` -> `200`。
- `POST /gov-payments` -> `200`。
- 页面成功提示与回执明细与后端返回一致。

### 8A.2 催款链路（collections）
#### 路由与页面
- `/collections/dunning`：催款批次列表。
- `/collections/dunning/new`：创建催款批次。
- `/collections/dunning/{id}`：催款批次详情。

#### UI 步骤
1. 打开 `/collections/dunning`，确认列表与筛选正常。
2. 点击`创建催款批次`进入 `/collections/dunning/new`。
3. 填写`截止日期`，选择客户范围后提交。
4. 创建成功后跳转详情（单批次）或返回列表（多批次）。
5. 进入 `/collections/dunning/{id}`，核对批次信息、状态、金额、日期。

#### 预期 API 与结果
- `GET /dunning?page=1&page_size=20` -> `200`。
- `POST /dunning` -> `200` 或 `201`。
- 列表与详情数据一致；失败时显示 `ApiErrorBanner` 与 `requestId`。

### 8A.3 提成链路（commission）
#### 路由与页面
- `/commission/rules`：提成规则管理。
- `/commission`（别名 `/commission/records`）：提成记录查询。
- `/commission/settlements`：提成结算批次、明细生成、报表。

#### UI 步骤
1. 打开 `/commission/rules`，新增规则并保存，再编辑并切换启停。
2. 打开 `/commission`，按案件/代理人/状态筛选查询。
3. 打开 `/commission/settlements`，创建结算批次。
4. 在同页输入批次 ID，点击`生成明细`。
5. 在报表区设置筛选并点击`查询报表`，核对统计卡和明细表。

#### 预期 API 与结果
- `GET /commission/rules` -> `200`。
- `POST /commission/rules` -> `201`（部分环境可能 `200`）。
- `PUT /commission/rules/{id}` -> `200`。
- `GET /commission` -> `200`。
- `POST /commission/settlements` -> `201`（部分环境可能 `200`）。
- `POST /commission/settlements/{id}/generate-lines` -> `200`。
- `GET /commission/reports/settlement` -> `200`。

### 8A.4 顾问链路（consulting）
#### 路由与页面
- `/consulting/cases/new`：顾问/检索项目立案。
- `/consulting/fee-drafts/new`：顾问/检索服务费草单生成。
- `/consulting/profitability`：顾问项目收益视图。

#### UI 步骤
1. 打开 `/consulting/cases/new`，按项目类型填写必填项并提交。
2. 成功后应跳转到 `/cases/{id}`。
3. 打开 `/consulting/fee-drafts/new`，按模式填写参数并点击`生成服务费草单`。
4. 核对草单 ID、行数、总金额。
5. 打开 `/consulting/profitability`，输入项目 ID 并查询收益。

#### 预期 API 与结果
- `POST /consulting/cases` -> `201`（部分环境可能 `200`）。
- `POST /consulting/fee-drafts` -> `201` 或 `200`。
- `GET /cases/{id}/receipts` -> `200`（无数据时可能 `404`）。
- `GET /expenses`（按项目筛选）-> `200`。
- `409/422` 错误有明确提示，不出现空白页。

### 8A.5 支出链路（expense）
#### 路由与页面
- `/expenses`：支出列表、筛选、统计卡片。
- `/expenses/new`：录入支出。

#### UI 步骤
1. 打开 `/expenses`，按项目编号/类别/日期范围筛选并查询。
2. 点击`录入支出`进入 `/expenses/new`。
3. 填写必填项（案件/项目编号、类别、日期、金额、币种）并提交。
4. 成功后返回列表，核对新记录与统计卡变化。

#### 预期 API 与结果
- `GET /expenses` -> `200`。
- `POST /expenses` -> `201`（部分环境可能 `200`）。
- `422` 字段错误可见，`401/403` 按全局策略跳转。

## FE-3 备注
- 本文档用于保证路由、按钮、状态码可复现验证。
- 如需查看历史执行证据，可参考：
  - `task/frontend/FE-3/FE-3-01_evidence.md`

## 9) DEMO-UI 冒烟流程（VITE_DEMO_UI=1）

> 本节用于验证 Demo UI 层：style-b 主题、中文化、分组导航、Dashboard KPI 与链路一致性。

### 前置条件
- 以前端环境变量 `VITE_DEMO_UI=1` 启动。
- 在 DevTools Elements 中可看到 `body.style-b`。
- 数据库至少有 1 条客户、案件、任务、费用草稿、账单数据。

### DEMO-UI 标签映射（英文 -> 中文）
#### 通用按钮
| 英文标签 | 中文标签 |
|---------|---------|
| Back | 返回 |
| Actions | 操作 |
| View | 查看 |
| Edit | 编辑 |
| Delete | 删除 |
| Save | 保存 |
| Cancel | 取消 |
| Refresh | 刷新 |
| Status | 状态 |
| Confirm | 确认 |

#### 列表页
| 页面 | 标题 | 新建按钮 | 关键列头 |
|------|------|---------|---------|
| `/cases` | 案件列表 | 新建案件 | 编号 / 案号 / 标题 / 客户 / 状态 / 更新时间 / 操作 |
| `/tasks` | 任务列表 | 新建任务 | 编号 / 标题 / 案件 / 状态 / 优先级 / 截止日期 / 负责人 / 操作 |
| `/billing/bills` | 账单列表 | 新建账单 | 账单号 / 客户 / 状态 / 金额 / 余额 / 开票日 |
| `/fees/drafts` | 费用草稿 | 新建草稿 | 草稿编号 / 案件 / 客户 / 币种 / 状态 / 金额 / 操作 |
| `/documents` | 文档列表 | 新建文档 | 编号 / 方向 / 标题 / 案件 / 类型 / 日期 / 创建时间 / 操作 |

#### 详情页
| 页面 | 返回按钮 | 主操作按钮 | 标签页 | 信息标签 |
|------|---------|-----------|-------|---------|
| `/cases/{id}` | 返回 | 编辑案件 | 概览 / 权利要求 / 官方文件 / 费用 / 账单 / 任务 | 案件信息 / 案号 / 标题 / 客户 / 状态 / 申请日 / 优先权日 / 备注 |
| `/documents/{id}` | 返回 | 编辑文档 | — | 文档内容 / 文档信息 / 编号 / 方向 / 创建时间 / 更新时间 |
| `/fees/drafts/{id}` | 返回 | 刷新 / 锁定 / 解锁 | 明细 / 概览 | 草稿信息 / 草稿编号 / 状态 / 案件编号 / 客户编号 / 类型 / 币种 |
| `/billing/bills/{id}` | 返回 | 打印账单 / 刷新 | 明细 / 概览 | 账单明细 / 描述 / 数量 / 单价 / 金额 / 合计 / 账单信息 / 账单号 / 客户 / 案件 / 币种 / 开票日 / 到期日 |

#### 确认弹窗
| 动作 | 弹窗标题 | 确认按钮 | 文案示例 |
|------|---------|---------|---------|
| 关闭任务 | 关闭任务 | 关闭 | 确定要关闭"{title}"吗？ |
| 重开任务 | 重新打开任务 | 重新打开 | 确定要重新打开"{title}"吗？ |
| 取消任务 | 取消任务 | 确认 | 确定要取消"{title}"吗？ |
| 锁定草稿 | 锁定草稿 | 锁定 | 锁定此草稿后将无法编辑... |
| 解锁草稿 | 解锁草稿 | 解锁 | 解锁此草稿后可以继续编辑... |

### 9.1 style-b 主题验证（FIX-01）
1. 以 `VITE_DEMO_UI=1` 启动应用。
2. 确认 `body` 包含 `style-b` 类。
3. 点击任一侧边栏菜单项（如`案件列表`）。
4. 检查激活项 `.nav-item.router-link-active`：
   - `background-color` 应解析为 `#EFF6FF`（`--sidebar-active-bg`）。
   - `color` 应解析为 `#2563EB`（`--sidebar-active-text`）。
5. 悬停未激活菜单项：
   - `background-color` 应解析为 `#F1F5F9`（`--sidebar-hover-bg`）。

### 9.2 列表页中文验证（FIX-03）
对 `/cases`、`/tasks`、`/billing/bills`、`/fees/drafts`、`/documents` 逐页检查：
1. 页面标题为中文。
2. 表格列头为中文。
3. 新建按钮为中文。
4. 总数格式为 `N 条`（不是 `N total`）。
5. 有数据时，操作列按钮为中文（如`操作`/`查看`）。
6. 空态标题与说明为中文。

### 9.3 详情页中文验证（FIX-02）
对 `/cases/{id}`、`/documents/{id}`、`/fees/drafts/{id}`、`/billing/bills/{id}` 逐页检查：
1. 返回按钮显示`返回`。
2. 主操作按钮为中文。
3. 标签页名称为中文。
4. 信息字段标签为中文。
5. 不存在 ID 时，空态提示为中文（未找到案件/文档/草稿/账单）。

### 9.4 确认弹窗中文验证（FIX-02/03）
1. 在 `/tasks` 行操作中点击`关闭`，验证弹窗标题与按钮为中文。
2. 在 `/fees/drafts/{id}` 点击`锁定`，验证弹窗标题与按钮为中文。

### 9.5 英文泄漏检查
- 按主导航完整浏览页面，不应出现英文 UI 标签/按钮/空态/弹窗文案。
- 例外：业务数据值可保留英文大写（如 `OPEN`、`LOCKED`、`CNY`），这些属于数据字段。
