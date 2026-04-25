# FPMS Automation Skeleton Pack 到真实项目映射与落地计划

> 生成日期：2026-04-17
> 范围：只读分析结果沉淀 + 后续动作计划
> 约束：本文档不改变 handler / testcase id / YAML / JSON / schema；后续实施仍需按仓库 `AGENTS.md` 的 atomic task discipline 拆分。

## 0. 结论摘要

`FPMS_Automation_Skeleton_Pack/` 与真实项目存在较高业务域对齐度。真实项目已经具备以下主要模块：

- 后端：`auth`、`rbac`、`masterdata`、`cases`、`documents`、`tasks`、`fees`、`billing`、`annuity`、`collections`、`commission`、`consulting`、`expenses`、`system`、`templates`
- 前端：登录、案卷、客户/申请人/国家主数据、系统参数、任务模板、文档模板、案件批量递交、时限、费用草单、官费清单、账单、收款、冲销、催款、坏账、提成、顾问项目、查询页面
- 数据库：核心表名与 skeleton 文档中的 `T_*` 概念大体对应，真实表名采用小写 `t_*`

首批建议只做 `W0 + A` 的 P0 主链路，先补齐认证、seed、API client、DB assert、UI page object 的最小能力，再逐步打开 skeleton handlers。

---

## 1. 模块映射表

### 1.1 已确认映射

| Skeleton Wave | 业务范围 | 真实前端路由 / 页面落点 | 真实后端 API 落点 | 真实 DB 表 |
|---|---|---|---|---|
| W0 | 主数据、参数、模板、权限 | `/clients`, `/clients/new`, `/settings/masterdata/applicants`, `/settings/masterdata/countries`, `/system/params`, `/system/task-templates`, `/system/doc-templates`, `/system/letterheads`, `/commission/rules`, `/login` | `/api/v1/auth/login`, `/api/v1/auth/me`, `/api/v1/clients`, `/api/v1/applicants`, `/api/v1/countries`, `/api/v1/system/params`, `/api/v1/task-templates`, `/api/v1/doc-templates`, `/api/v1/templates`, `/api/v1/letterheads`, `/api/v1/commission/rules`, `/api/v1/admin/users`, `/api/v1/admin/seed/roles-permissions` | `t_user`, `t_role`, `t_role_perm`, `t_user_role`, `t_client`, `t_client_address`, `t_client_contact`, `t_applicant`, `t_country`, `t_system_param`, `t_task_template`, `t_doc_template`, `t_template`, `t_letter_head`, `t_fee_rate`, `t_commission_rule` |
| A | 新案立案、批量递交、申请费、官费清单、账单、收款、提成 | `/cases/new`, `/cases`, `/cases/:id`, `/cases/:id/edit`, `/cases/batch-filing`, `/tasks`, `/fees/drafts`, `/fees/rates`, `/annuity/pay-lists`, `/annuity/gov-payments/new`, `/billing/bills`, `/billing/bills/new`, `/billing/payments`, `/billing/payments/new`, `/billing/offsets`, `/billing/case-receipts`, `/commission` | `/api/v1/cases`, `/api/v1/cases/{id}`, `/api/v1/cases/{id}/limited-edit`, `/api/v1/cases/batch-filing/candidates`, `/api/v1/cases/batch-filing/submit`, `/api/v1/tasks`, `/api/v1/fees/drafts`, `/api/v1/fees/rates`, `/api/v1/pay-lists`, `/api/v1/gov-payments`, `/api/v1/bills`, `/api/v1/payments`, `/api/v1/payments/{id}/offsets`, `/api/v1/case-receipts`, `/api/v1/commission` | `t_case`, `t_case_applicant`, `t_case_inventor`, `t_priority`, `t_bio_deposit`, `t_case_agent_split`, `t_task`, `t_task_log`, `t_fee_draft`, `t_fee_item`, `t_fee_rate`, `t_pay_list`, `t_gov_payment`, `t_bill`, `t_bill_item`, `t_payment`, `t_payment_line`, `t_offset`, `t_case_receipt`, `t_commission` |
| B | OA / 补正、中间文件、答复时限、费用账单收款提成 | `/documents`, `/documents/new`, `/documents/wizard`, `/documents/:id`, `/documents/:id/edit`, `/tasks`, `/fees/drafts`, `/billing/bills`, `/billing/payments`, `/commission` | `/api/v1/documents`, `/api/v1/documents/{id}`, `/api/v1/documents/{id}/attachments`, `/api/v1/doc-templates`, `/api/v1/tasks`, `/api/v1/fees/drafts`, `/api/v1/bills`, `/api/v1/payments`, `/api/v1/commission` | `t_document`, `t_doc_attachment`, `t_doc_template`, `t_task`, `t_task_log`, `t_fee_draft`, `t_fee_item`, `t_bill`, `t_bill_item`, `t_payment`, `t_offset`, `t_commission` |
| C | PCT 国际到国家阶段 | `/cases/new`, `/cases/:id/edit`, `/cases`, `/tasks`, `/documents/wizard` | `/api/v1/cases`, `/api/v1/cases/{id}`, `/api/v1/tasks`, `/api/v1/documents` | `t_case` 的 PCT 字段：`ro`, `isa`, `ipea`, `intl_app_no`, `intl_app_date`, `intl_pub_no`, `pct_national_entry_date`；以及 `t_task`, `t_document` |
| G0 | 授权阶段、授权费、年费初始化、提成 | `/documents/wizard`, `/grant-fee/tasks`, `/fees/drafts`, `/billing/bills`, `/annuity/tasks`, `/commission` | `/api/v1/documents`, `/api/v1/grant-fee-tasks`, `/api/v1/grant-fee-tasks/{id}/state`, `/api/v1/grant-fee-tasks/{id}/generate-draft`, `/api/v1/fees/drafts`, `/api/v1/bills`, `/api/v1/annuity/tasks`, `/api/v1/commission` | `t_case`, `t_document`, `t_grant_fee_task`, `t_fee_draft`, `t_fee_item`, `t_bill`, `t_bill_item`, `t_annuity_task`, `t_commission` |
| D | 年费周期、年费通知、官费清单、缴费、收款 | `/annuity/tasks`, `/annuity/pay-lists`, `/annuity/pay-lists/:id`, `/annuity/gov-payments/new`, `/fees/drafts`, `/billing/bills`, `/billing/payments`, `/billing/fee-unified-query` | `/api/v1/annuity/tasks`, `/api/v1/annuity/tasks/generate-drafts`, `/api/v1/pay-lists`, `/api/v1/pay-lists/{id}`, `/api/v1/pay-lists/{id}/export`, `/api/v1/pay-lists/{id}/mark-paid`, `/api/v1/gov-payments`, `/api/v1/fees/drafts`, `/api/v1/bills`, `/api/v1/payments` | `t_annuity_task`, `t_pay_list`, `t_gov_payment`, `t_fee_draft`, `t_fee_item`, `t_bill`, `t_bill_item`, `t_payment`, `t_case_receipt` |
| E | 无效 / 诉讼 | `/cases/new`, `/cases/:id`, `/documents/wizard`, `/tasks`, `/fees/drafts`, `/billing/bills`, `/commission` | `/api/v1/cases`, `/api/v1/documents`, `/api/v1/tasks`, `/api/v1/fees/drafts`, `/api/v1/bills`, `/api/v1/commission` | `t_case` 的无效字段：`original_case_id`, `invalid_client_id`, `invalid_patentee`, `invalid_requester`, `invalid_role`；以及 `t_document`, `t_task`, `t_fee_draft`, `t_bill`, `t_commission` |
| F | 预收款、后续冲销、CaseReceipt、提成影响 | `/billing/payments`, `/billing/payments/new`, `/billing/offsets`, `/billing/case-receipts`, `/billing/bills`, `/billing/fee-unified-query`, `/commission` | `/api/v1/payments`, `/api/v1/payments/{id}`, `/api/v1/payments/{id}/offsets`, `/api/v1/payment-lines`, `/api/v1/case-receipts`, `/api/v1/bills`, `/api/v1/commission` | `t_payment`, `t_payment_line`, `t_offset`, `t_case_receipt`, `t_bill`, `t_bill_item`, `t_commission` |
| G | 催款、坏账、坏账恢复 | `/collections/dunning`, `/collections/dunning/new`, `/collections/dunning/:id`, `/billing/bills`, `/billing/bills/:id` | `/api/v1/dunning`, `/api/v1/dunning/{id}`, `/api/v1/bills/{id}/bad-debt`, `/api/v1/bills/{id}/bad-debt/restore`, `/api/v1/bills/{id}/bad-debt-mark`, `/api/v1/bills/{id}/bad-debt-recover` | `t_dunning`, `t_dunning_line`, `t_bill`, `t_bad_debt_voucher`, `t_bad_debt_recovery`, `t_payment`, `t_offset` |
| H | 顾问 / 检索项目 | `/consulting/cases/new`, `/consulting/fee-drafts/new`, `/consulting/profitability`, `/expenses`, `/expenses/new`, `/fees/drafts`, `/billing/bills`, `/billing/payments`, `/commission` | `/api/v1/consulting/cases`, `/api/v1/consulting/fee-drafts`, `/api/v1/expenses`, `/api/v1/fees/drafts`, `/api/v1/bills`, `/api/v1/payments`, `/api/v1/commission` | `t_case`, `t_expense`, `t_fee_draft`, `t_fee_item`, `t_bill`, `t_bill_item`, `t_payment`, `t_commission` |
| X | 查询、报表、审计、手工账单、状态机回归 | `/cases`, `/billing/fee-unified-query`, `/tasks/special-search`, `/tasks/today`, `/billing/bills/new`, `/commission`, `/consulting/profitability` | `/api/v1/cases`, `/api/v1/cases/export`, billing API 内的费用综合查询接口，`/api/v1/tasks/*`, `/api/v1/bills/manual`, `/api/v1/commission/*` | 跨表查询：`t_case`, `t_document`, `t_task`, `t_fee_draft`, `t_fee_item`, `t_pay_list`, `t_gov_payment`, `t_bill`, `t_payment`, `t_offset`, `t_case_receipt`, `t_commission`, `t_task_log` |

### 1.2 待确认假设

| 项 | 假设 / 缺口 |
|---|---|
| API 前缀 | 前端确认使用 `VITE_API_BASE_URL`，默认 `http://localhost:8000/api/v1`；skeleton Playwright fixture 当前默认 `http://localhost:8000/api`，需要调整为 `/api/v1`。 |
| 枚举映射 | Skeleton 使用 `INVENTION / IN_IN / PCT_NATIONAL`，真实前端/后端可见值包含 `INV / CN_DOMESTIC / PCT_NATL` 等，需要建立枚举归一化 helper。 |
| 生物保藏单位 | Skeleton 明确 `DS-BIO-UNIT-001` 缺 seed；真实 DB 目前只确认案卷子表 `t_bio_deposit.deposit_unit_name`，未确认独立保藏单位主数据表。 |
| PCT / 无效 / 诉讼 | ORM 字段已存在，通用 `cases` API 可承载，但是否有专门 UI 流程和强规则仍需逐接口验证。 |
| 报表 API | 有查询页面和部分 report 测试/服务，但 skeleton X wave 的每个报表口径需要逐条对照现有 API 响应字段。 |

---

## 2. 技术落地清单

### 2.1 pytest 需要补的 client / helper / db assert

| 类型 | 需要补齐 |
|---|---|
| Auth client | `login(username, password)`、`auth_headers(role)`、`me()`；真实登录为 `POST /api/v1/auth/login`，token 字段为 `access_token`。 |
| Masterdata client | `create_client`、`create_client_address`、`create_client_contact`、`create_applicant`、`create_country`、`create_fee_rate`、`create_task_template`、`create_doc_template`、`create_commission_rule`。 |
| Case client | `create_case`、`get_case`、`search_case_by_case_no`、`limited_edit_case`、`batch_filing_candidates`、`submit_batch_filing`。 |
| Document client | `create_document`、`wizard_create_document`、`upload_attachment`、`get_document`、`list_doc_templates`。 |
| Task client | `list_tasks`、`get_task`、`close/reopen/cancel/assign`、`get_logs`、按 `case_id/type/status` 查询。 |
| Fee client | `create_fee_draft`、`lock_fee_draft`、`add/update/delete_fee_item`、`list_fee_rates`、`create_fee_rate`。 |
| PayList / GovPayment client | `create_pay_list_from_fee_items`、`list_pay_lists`、`mark_paid`、`register_gov_payment`。 |
| Billing client | `create_bill_from_drafts`、`create_manual_bill`、`create_payment`、`offset_payment`、`reverse_offset`、`list_case_receipts`。 |
| Commission client | `list_commissions`、`list_rules`、`create_rule`、`settle_commission`。 |
| DB helper | 直接复用真实 SQLAlchemy ORM 比 skeleton `DbAssert` 字符串 SQL 更稳；补 `fetch_one_model`、`assert_count`、`assert_case_status`、`assert_child_rows`、`assert_money_equals`、`assert_audit_fields`。 |
| RUN_ID helper | 统一生成 `CASE-A-{RUN_ID}-001`、`BILL-{RUN_ID}-001`、`PAY-{RUN_ID}-001`，并提供清理/查询范围过滤。 |
| Enum helper | Skeleton 值到真实值映射：`INVENTION -> INV`、`UTILITY -> UM`、`DESIGN -> DES`、`IN_IN -> CN_DOMESTIC` 等。 |
| Money/date assert | Decimal 比较、日期 ISO 序列化、SQLite date/datetime 兼容断言。 |
| Warning helper | 区分 400 阻断、200/201 带 warning、UI 弹窗确认三类结果。 |

### 2.2 Playwright 需要补的 page object / selector / fixture

| 类型 | 需要补齐 |
|---|---|
| LoginPage | 当前 skeleton 使用英文 label；真实 UI 是中文 `用户名`、`密码`，需要改成中文 label/placeholder/role selector，并等待跳转或 token 落 localStorage。 |
| Auth fixture | 支持 API 登录后注入 `localStorage.fpms_token`，避免每条 UI 用例重复表单登录；保留角色登录矩阵。 |
| CasePage | `CaseCreatePage`、`CaseListPage`、`CaseDetailPage`、`CaseEditPage`、`CaseBatchFilingPage` 拆分；覆盖 Element Plus select/date/input-number/table 操作。 |
| Masterdata pages | `ClientPage`、`ApplicantPage`、`CountryPage`、`SystemParamPage`、`TaskTemplatePage`、`DocTemplatePage`、`FeeRatePage`。 |
| DocumentPage | 文档向导、附件上传、模板选择、来文/发文状态联动、详情断言。 |
| TaskPage | 任务列表筛选、今日提醒、详情操作、日志断言、打印/导出 smoke。 |
| FeePage | 草单创建、明细表格编辑、锁定、费率维护。 |
| PayListPage / GovPaymentPage | 官费清单查询、导出、标记已缴、登记缴费。 |
| BillingPage | 账单创建、账单详情、收款创建、冲销、CaseReceipt、坏账面板。 |
| CollectionsPage | 催款单创建、详情、坏账/恢复。 |
| CommissionPage | 提成列表、规则、结算。 |
| ReportPage | 案卷查询、费用综合查询、时限特殊查询、利润/报表查询。 |
| Selector 策略 | 当前真实前端几乎没有 `data-testid`，多数可用中文 label/button/table header；高风险页面建议后续补 `data-testid`，但应作为独立前端 atomic task。 |
| Fixture | `runId`、`api`、`db`、`authAsAdmin/Formalities/Finance/Limited`、`seedW0`、`createCaseViaApi`、`cleanupByRunId`、`expectApiToast`。 |

---

## 3. 高风险项

### 3.1 已确认风险

| 风险 | 说明 |
|---|---|
| 登录方式 | 后端是 JWT Bearer：`POST /api/v1/auth/login`，前端 token key 为 `fpms_token`；skeleton Playwright 默认 API URL 少了 `/v1`，登录 selector 也是英文。 |
| 动态数据冲突 | `case_no`、`bill_no` 唯一；`pay_no` 在用例中要求同客户唯一，但模型上未确认唯一约束。必须强制所有唯一业务号带 `RUN_ID`。 |
| 数据 seed 缺口 | 真实测试 `conftest.py` 只 seed admin、角色权限、少量任务模板和文档模板；skeleton W0 需要客户、地址、联系人、申请人、国家、费率、系统参数、信头、提成规则等。 |
| warning vs blocking 差异 | 用例多处允许“警告或阻断”，真实 API 多数更可能直接 400；UI 的强制确认模式未确认。自动化断言必须先定义环境模式。 |
| 选择器不稳定 | 真实 UI 基于 Element Plus，缺 `data-testid`；中文 label 可用但表格、下拉浮层、日期组件 selector 容易脆。 |
| 缺少 DB 只读权限 | Skeleton `DbAssert` 需要 DB DSN；真实后端测试可用 SQLAlchemy fixture，但对外部运行环境是否提供只读 DB 账号未确认。 |
| 枚举不一致 | Skeleton 规格枚举和真实实现有差异，直接套用 YAML 值会造成 422/400。 |
| 前后端路径差异 | 前端 `/grant-fee/tasks` 对应 API `/grant-fee-tasks/*`；前端 `/annuity/pay-lists` 对应 API `/pay-lists`，不是同路径前缀。 |
| 并发 SQLite | 后端测试使用 SQLite；批量 E2E 并发写库有锁风险，应串行执行写库用例。 |

### 3.2 待确认假设

| 风险 | 待确认点 |
|---|---|
| 多角色账号 | 真实 seed 是否有 `formalities1 / finance1 / agent.primary / agent.limited`；目前测试 fixture 只确认 `admin/admin123`。 |
| 业务规则强度 | 案件组合校验、涉外代理所类型、申请人主申请人规则、日期编号一致性是否已在 API 层完整实现。 |
| 文档输出 | 模板渲染、附件存储、导出文件是否可在 CI 环境稳定生成。 |
| 提成触发时点 | 账单生成、收款后、或手工触发提成的真实触发点需确认。 |

---

## 4. 首批建议实现范围

### 4.1 Story Shape Classification / Runbook

| 项 | 建议 |
|---|---|
| `shared_file_density` | 高：pytest framework、Playwright fixtures、API client、DB assert、seed helper 都是共享文件。 |
| `prereq_dependency_density` | 高：A wave 依赖 W0 主数据、费率、模板、权限。 |
| `be_fe_coupling` | 中高：P0 主链路需要 API + DB + UI 双层验证。 |
| `evidence_cost` | 高：每条链路涉及 API 响应、DB 行、UI 状态、金额计算。 |
| `chosen_runbook` | `P0-prereq-heavy-story`。先稳定 W0 seed / auth / client，再落 A 主链路。 |

### 4.2 只建议 `W0 + A` 的 P0 主链路

| 批次 | Testcase ID | 落地建议 |
|---|---|---|
| W0-Seed/Auth | `TC-W0-001` | 客户、地址、联系人 seed/API/UI smoke。 |
| W0-Seed/Fee | `TC-W0-007` | 申请费固定费率 seed/API/DB 断言。 |
| W0-Seed/DocTemplate | `TC-W0-010` | 文档模板配置 seed/API/DB 断言。 |
| W0-Authz | `TC-W0-014` | 先做 API 权限矩阵 smoke，再补 UI 菜单/按钮。 |
| A-CaseCreate | `TC-A-001` | 新案最小必填创建，作为后续 A 主链路基准案。 |
| A-Uniqueness | `TC-A-003` | 案卷号唯一阻断，API 优先。 |
| A-ForeignRequired | `TC-A-005` | 涉外必填/外方代理规则，先 API。 |
| A-ApplicantRules | `TC-A-006` | 申请人列表规则，先 API 参数化。 |
| A-DateRules | `TC-A-008` | 日期与编号一致性，服务层/API 参数化。 |
| A-LimitedEdit | `TC-A-010` | 受限编辑入口和无副作用，API + UI。 |
| A-BatchFiling | `TC-A-011` | 批量递交成功，API + DB，UI smoke。 |
| A-BatchValidation | `TC-A-012` | 批量递交校验，API 参数化。 |
| A-TaskGeneration | `TC-A-013` | 申请费时限自动生成，DB 断言 `t_task/t_task_log`。 |
| A-FeeDraft | `TC-A-015` | 申请费草单生成，金额和明细 DB 断言。 |
| A-PayList | `TC-A-017` | 官费清单与缴费，API + DB。 |
| A-Bill | `TC-A-019` | 申请费账单生成，API + DB。 |
| A-PaymentOffset | `TC-A-021` | 客户付款与冲销，API + DB。 |
| A-Commission | `TC-A-023` | 提成生成与可结算入口，DB 断言优先。 |

---

## 5. 拟改文件清单

仅列文件。本清单是后续实施候选，不代表本文档已修改这些文件。

```text
FPMS_Automation_Skeleton_Pack/pytest_python/framework/api_client.py
FPMS_Automation_Skeleton_Pack/pytest_python/framework/db_assert.py
FPMS_Automation_Skeleton_Pack/pytest_python/framework/helpers.py
FPMS_Automation_Skeleton_Pack/pytest_python/framework/runtime.py
FPMS_Automation_Skeleton_Pack/pytest_python/conftest.py
FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py
FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py
FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_wave_w0.py
FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_wave_a.py
FPMS_Automation_Skeleton_Pack/playwright_ts/src/fixtures/fpms.fixtures.ts
FPMS_Automation_Skeleton_Pack/playwright_ts/src/clients/apiClient.ts
FPMS_Automation_Skeleton_Pack/playwright_ts/src/clients/dbClient.ts
FPMS_Automation_Skeleton_Pack/playwright_ts/src/pages/LoginPage.ts
FPMS_Automation_Skeleton_Pack/playwright_ts/src/pages/CasePage.ts
FPMS_Automation_Skeleton_Pack/playwright_ts/src/pages/FeePage.ts
FPMS_Automation_Skeleton_Pack/playwright_ts/src/pages/BillingPage.ts
FPMS_Automation_Skeleton_Pack/playwright_ts/src/pages/TaskPage.ts
FPMS_Automation_Skeleton_Pack/playwright_ts/src/pages/DocumentPage.ts
FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/helpers.ts
FPMS_Automation_Skeleton_Pack/playwright_ts/src/handlers/waveW0.ts
FPMS_Automation_Skeleton_Pack/playwright_ts/src/handlers/waveA.ts
```

后续如果允许为真实前端补稳定选择器，建议另立独立前端 atomic task，候选文件是：

```text
frontend/src/modules/auth/pages/Login.vue
frontend/src/modules/cases/pages/CaseCreate.vue
frontend/src/modules/cases/pages/CaseBatchFiling.vue
frontend/src/modules/fees/pages/FeeDraftCreate.vue
frontend/src/modules/billing/pages/BillCreate.vue
frontend/src/modules/billing/pages/PaymentCreate.vue
frontend/src/modules/annuity/pages/PayList.vue
frontend/src/modules/annuity/pages/GovPaymentCreate.vue
```

---

## 6. 建议执行命令

### 6.1 资产校验

```bash
python FPMS_Automation_Skeleton_Pack/scripts/validate_assets.py
```

### 6.2 后端真实项目基线

```bash
cd backend
pytest -q tests/test_admin_users.py tests/test_case_batch_filing_action.py tests/test_case_fields.py tests/test_b5_billing_polish.py
```

### 6.3 Skeleton pytest 首批

```bash
cd FPMS_Automation_Skeleton_Pack/pytest_python
pytest tests/test_asset_integrity.py -q
pytest tests/test_wave_w0.py -m p0 -q
pytest tests/test_wave_a.py -m p0 -q
pytest -m "p0 and happy" -q
```

### 6.4 前端真实项目基线

```bash
cd frontend
npm run typecheck
npm run lint
npm run build
```

### 6.5 Skeleton Playwright 首批

```bash
cd FPMS_Automation_Skeleton_Pack/playwright_ts
npx playwright test src/tests/asset-integrity.spec.ts
npx playwright test src/tests/wave-w0.setup.spec.ts --grep "@P0"
npx playwright test src/tests/wave-a.case-creation.spec.ts --grep "@P0"
```

### 6.6 联调环境建议

```bash
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

```bash
cd frontend
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1 npm run dev -- --host 127.0.0.1 --port 5173
```

```bash
cd FPMS_Automation_Skeleton_Pack/playwright_ts
FPMS_BASE_URL=http://127.0.0.1:5173 FPMS_API_URL=http://127.0.0.1:8000/api/v1 npx playwright test src/tests/wave-a.case-creation.spec.ts --grep "@P0"
```

---

## 7. 下一步行动计划

### 7.1 执行原则

后续实施必须按一个 atomic task file 一次一个闭环执行。由于 `W0 + A` 属于 `P0-prereq-heavy-story`，建议先做共享底座，再逐条打开 testcase handler。不要一次性把整个 W0/A wave 改完。

### 7.2 建议 Wave 0：自动化底座

| 顺序 | 建议任务 | 闭环目标 | 主要文件 | 验证 |
|---|---|---|---|---|
| 1 | API base/auth client | skeleton pytest 能登录真实后端并自动带 Bearer token | `pytest_python/framework/api_client.py`, `pytest_python/framework/runtime.py`, `pytest_python/conftest.py` | `pytest tests/test_asset_integrity.py -q` + 一个 auth smoke |
| 2 | DB assert 接入 | skeleton pytest 能只读断言 SQLite/Postgres 目标表 | `pytest_python/framework/db_assert.py`, `pytest_python/framework/runtime.py` | 针对 `t_user` 或 `t_client` 的只读 smoke |
| 3 | RUN_ID 与枚举 helper | 用例数据能映射真实枚举并避免唯一键冲突 | `pytest_python/framework/helpers.py` | helper 单测或 W0 dry run |
| 4 | W0 seed helper | 可幂等准备客户、申请人、国家、费率、模板、权限所需数据 | `pytest_python/framework/helpers.py`, `pytest_python/handlers/wave_w0.py` | `pytest tests/test_wave_w0.py -m p0 -q` |
| 5 | Playwright auth fixture | UI 测试可通过 API 登录注入 token，避开重复登录 | `playwright_ts/src/fixtures/fpms.fixtures.ts`, `playwright_ts/src/pages/LoginPage.ts` | `npx playwright test src/tests/asset-integrity.spec.ts` |

### 7.3 建议 Wave A：P0 主链路

| 顺序 | Testcase | 建议自动化层 | 闭环目标 |
|---|---|---|---|
| 1 | `TC-A-001` | API + DB，UI smoke | 创建最小必填案卷，确认 `t_case/t_case_applicant`。 |
| 2 | `TC-A-003` | API + DB | 重复案卷号被拒，DB 无重复行。 |
| 3 | `TC-A-005` | API first | 涉外必填和外方代理规则落地；如真实系统是 warning，先记录差异。 |
| 4 | `TC-A-006` | API 参数化 | 申请人列表规则、主申请人规则、申请人类型规则。 |
| 5 | `TC-A-008` | API 参数化 | 日期与状态/编号一致性规则。 |
| 6 | `TC-A-010` | API + UI | 受限编辑仅能修改白名单，且无状态/任务/费用副作用。 |
| 7 | `TC-A-011` | API + DB，UI smoke | 批量递交把状态推进到目标值并生成相关文档/任务前置。 |
| 8 | `TC-A-012` | API 参数化 | 批量递交空选择、非法日期、边界日期。 |
| 9 | `TC-A-013` | DB assert | 递交后生成申请费时限任务和任务日志。 |
| 10 | `TC-A-015` | API/service + DB | 申请费草单与金额计算。 |
| 11 | `TC-A-017` | API + DB | 官费清单、缴费登记。 |
| 12 | `TC-A-019` | API + DB | 申请费账单生成与明细绑定。 |
| 13 | `TC-A-021` | API + DB | 收款、冲销、账单余额、CaseReceipt。 |
| 14 | `TC-A-023` | DB assert | 提成生成、分摊、WaitPay / ForceSettle 初值。 |

### 7.4 建议暂缓事项

- 暂缓 B/C/G0/D/E/F/G/H/X 的 handler 实现，直到 W0 seed 和 A 主链路稳定。
- 暂缓补真实前端 `data-testid`，除非 Playwright selectors 在 A 主链路上已经证明不稳定。
- 暂缓 repo-wide lint/format 写操作；单任务只做 scoped lint/format。
- 暂缓并发跑写库测试；SQLite 环境优先串行。

### 7.5 下一批需要产出的计划文件

建议在正式实施前新增一个显式 batch manifest 或 task plan，至少包含：

- `Story Shape Classification`
- `chosen_runbook: P0-prereq-heavy-story`
- 每个 atomic task 的 exact task file path
- 每个任务的 exact closure slice
- explicit non-closure statement
- allowed files
- verification commands
- evidence path

推荐第一份 atomic task：

```text
tasks/automation/W0-AUTO-PY-AUTH-CLIENT-01.md
```

闭环范围：

- 只实现 skeleton pytest 的真实 API base/auth client 能力
- 不实现 W0/A testcase handler
- 不改 Playwright
- 不改真实业务代码
