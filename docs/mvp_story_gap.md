# FPMS MVP1 User Story GAP Analysis

> **Author**: Senior Architect & BA
> **Date**: 2026-02-23
> **Method**:逐条对比 `docs/FPMS SPEC 2.0.md` 中定义的 45 条 User Story 与当前实现，评估实现程度
> **评级标准**: ✅ 已实现 | 🟡 部分实现 | ❌ 未实现 | 🚫 MVP1 明确排除

---

## 1. 案卷维护 (Case Maintenance) — US-CM-01 ~ US-CM-05

### US-CM-01 新案建立 ✅/🟡

> 作为 **流程人员**，我希望在一个表单中录入案件的基本信息、参与方、重要日期和控制标记，并保存为新案卷，确保案卷号唯一，字段完整且符合规则。

| 子能力 | 实现状态 | 说明 |
|---|---|---|
| 基本信息录入 (case_no, case_type, patent_category, flow_dir, title_cn/en) | ✅ | `CaseCreate` schema + `CaseCreate.vue` |
| 案卷号唯一校验 | ✅ | 后端 service 层校验 |
| 客户关联 (client_id) | ✅ | FK 到 T_Client |
| 申请人列表录入 | 🟡 | 以 JSON list 存储，非独立表；无 FK 到 T_Applicant 主数据；无 IsPrimary 标记 |
| 发明人列表录入 | 🟡 | 以 JSON list 存储，非独立表 |
| 优先权列表录入 | 🟡 | 以 JSON list 存储，非独立表；无 PrioDate 自动聚合 |
| 控制标记 (IsFeeMonitor, FeeReduction, ApplicantKind, NoPower, NoPrioText, HasExamRequest) | ❌ | 模型中无这些字段 |
| 日期字段 (RecvDate, FilingDate) | 🟡 | filing_date, recv_date 存在；缺 PubDate, GrantDate, PubNo, GrantNo, PatentNo |
| 代理人指定 (PrimaryAgentID, SecondAgentID, DraftorID) | ❌ | 模型中无代理人指派字段 |
| 规格信息 (SpecPages, ClaimCount) | ❌ | 模型中无 |
| 国别信息 (FromCountry, ToCountry, ForeignAgentID) | ❌ | 模型中无 |

**综合评级**: 🟡 核心 CRUD 可用，但 SPEC 要求的 50+ 字段中仅实现约 15 个

---

### US-CM-02 扩展信息维护 🚫

> 作为 **流程人员**，我希望为案件维护优先权、菌种保藏、PCT 信息以及无效案专属字段，以便准确反映案件的法律与技术状态。

| 子能力 | 实现状态 | 说明 |
|---|---|---|
| 优先权维护 | 🟡 | JSON list 可录入，非独立表 |
| 菌种保藏 (T_BioDeposit) | ❌ | 未实现 |
| PCT 信息 (RO, ISA, IPEA, IntlAppNo/Date, IntlPubNo/Date, NeedIPER) | ❌ | 未实现 |
| 无效案专属字段 (OriginalCaseID, InvalidationType, etc.) | ❌ | 未实现 |

**综合评级**: 🚫 PCT/无效属 MVP1 明确排除范围；菌种保藏为低优先级

---

### US-CM-03 参与方管理 🟡

> 作为 **流程人员**，我希望在案件中选择或新增客户、申请人、外方代理、发明人，以及指定文件邮址与账单邮址，确保后续所有信函与账单地址正确。

| 子能力 | 实现状态 | 说明 |
|---|---|---|
| 客户选择/关联 | ✅ | client_id FK |
| 客户新增 | ✅ | T_Client CRUD |
| 申请人选择/新增 (T_Applicant 主数据) | ❌ | 无申请人主数据表，以 JSON 自由文本录入 (MVP1 scope 允许) |
| 外方代理 (ForeignAgentID) | ❌ | 未实现 |
| 发明人录入 | 🟡 | JSON list 方式 |
| 文件邮址/账单邮址指定 | ❌ | T_Client 只有单地址，无多地址标记用途 |

**综合评级**: 🟡 客户关联可用，但参与方管理较为粗糙

---

### US-CM-04 案件信息补充（限制修改） ✅

> 作为 **代理人**，我希望在没有完整案卷修改权限的情况下，只能补充少量字段（名称、发明人、规格等），且不会误改关键法律信息。

| 子能力 | 实现状态 | 说明 |
|---|---|---|
| 限制修改白名单 (title_cn, title_en, inventors) | ✅ | `CaseUpdateLimited` schema + PATCH endpoint |
| RBAC 权限控制 (Agent 角色) | ✅ | `require_perm("Case.LimitedEdit")` |
| 规格字段 (SpecPages/ClaimCount) 不在白名单 | N/A | 模型中暂无这些字段 |

**综合评级**: ✅ 核心机制已实现，白名单字段可在模型扩展后同步扩展

---

### US-CM-05 案件递交批处理 🚫

> 作为 **流程人员**，我希望按条件筛选"未递交"案件，成批设置递交日期及是否提实审请求，系统自动更新法律状态并生成递交清单。

| 子能力 | 实现状态 | 说明 |
|---|---|---|
| 按条件筛选 NOT_FILED 案件 | ❌ | 无批处理筛选界面 |
| 批量设置递交日期 | ❌ | 无批量状态更新 API |
| 自动生成递交清单 (Word) | ❌ | 无 |
| Status: NOT_FILED → WAITING_RECEIPT | 🟡 | 状态值存在但无批量操作 |

**综合评级**: 🚫 批量操作属 MVP1 明确排除范围

---

## 2. 中间文件与往来管理 (Documents) — US-WD-01 ~ US-WD-07

### US-WD-01 来文登记 🟡

> 作为 **流程人员**，我希望能按案件批量录入中间文件，并记录发文日/转寄日/挂号号等信息，包括官方来文和客户来文。

| 子能力 | 实现状态 | 说明 |
|---|---|---|
| 文档 CRUD (创建/编辑/删除) | ✅ | T_Document + API endpoints |
| 关联案件 (case_id) | ✅ | FK 到 T_Case |
| 方向 (IN/OUT) | ✅ | direction 字段 |
| 文档类型 (doc_type) | ✅ | OFFICIAL_IN, OFFICIAL_OUT, CLIENT_IN, CLIENT_OUT |
| 发文日 (DispatchDate) | 🟡 | 只有单一 doc_date，无 DispatchDate vs ReceiveDate 区分 |
| 转寄日 (ForwardDate) | ❌ | 未实现 |
| 挂号号 (IncomingRegNo/OutgoingRegNo) | ❌ | 未实现 |
| 按案件批量录入 | ❌ | 仅单条录入 |

**综合评级**: 🟡 基础 CRUD 可用，缺少专业知识产权来文字段

---

### US-WD-02 发文登记与自动核销 ❌

> 作为 **流程人员/代理人**，我希望在登记去文时可以标明"回复了哪份来文"，系统自动核销对应的时限任务。

| 子能力 | 实现状态 | 说明 |
|---|---|---|
| ReplyToID (标明回复哪份来文) | ❌ | T_Document 无 ReplyToID 字段 |
| 自动核销时限任务 (Task.Status → DONE) | ❌ | Document 与 Task 无联动逻辑 |
| NeedReply / ReplyDate 字段 | ❌ | 未实现 |

**综合评级**: ❌ 来文↔去文链 + 任务自动核销完全未实现

---

### US-WD-03 期限联动 ❌

> 作为 **流程人员**，我希望对需要回复的中间文件，系统根据预定义规则自动计算官方绝限、内部限和提醒日期，并生成时限任务。

| 子能力 | 实现状态 | 说明 |
|---|---|---|
| T_DocTemplate 配置 (DeadlineTemplateCode) | ❌ | 无文档模板配置表 |
| 从文档事件自动创建 T_Task | ❌ | 无自动化联动 |
| 时限计算 (BaseDate + AddMonths/Days = Deadline) | ❌ | 无 T_TaskTemplate 计算引擎 |

**综合评级**: ❌ 这是 SPEC 中最核心的自动化引擎之一，完全未实现

---

### US-WD-04 费用联动 ❌

> 作为 **流程人员/财务**，我希望对授权通知、年费催缴通知等中间文件，系统自动生成相应的费用草单。

| 子能力 | 实现状态 | 说明 |
|---|---|---|
| T_DocTemplate 配置 (FeeDraftType, FeeItemList) | ❌ | 无文档模板配置表 |
| 从文档事件自动创建 T_FeeDraft | ❌ | 无自动化联动 |

**综合评级**: ❌ 文档→费用联动未实现

---

### US-WD-05 电子档案存档 🟡

> 作为 **流程人员**，我希望每份中间文件都能对应 0..N 份电子附件，并可随时预览/下载。

| 子能力 | 实现状态 | 说明 |
|---|---|---|
| 单文件附件上传/下载 | ✅ | file_path 字段 + storage 模块 |
| 多附件支持 (T_DocAttachment: 0..N) | ❌ | 只支持单文件 |
| 附件预览 | ❌ | 只有下载 |

**综合评级**: 🟡 单附件可用，缺多附件

---

### US-WD-06 中间文件查询 & 清单输出 🟡

> 作为 **管理/流程人员**，我希望按时间、类型、案件等条件查询中间文件，并输出清单用于统计、报备或审计。

| 子能力 | 实现状态 | 说明 |
|---|---|---|
| 文档列表/查询 | 🟡 | 基础列表，筛选条件有限 |
| 按多维度高级筛选 (DocType, Template, 日期范围, Case, Client) | ❌ | 仅基础筛选 |
| 清单输出 (导出 Excel/Word) | ❌ | 未实现 |

**综合评级**: 🟡 基础查询可用，高级搜索和导出缺失

---

### US-WD-07 邮寄信息登记与交接单 & 信封 🚫

> 作为 **流程人员**，我希望对同一批寄出的文件统一登记挂号号，为客户生成"文件交接单"，并打印信封。

| 子能力 | 实现状态 | 说明 |
|---|---|---|
| T_DocDispatch (邮寄跟踪) | ❌ | 整个邮寄模块未实现 |
| 文件交接单生成 | ❌ | 未实现 |
| 信封打印 | ❌ | 未实现 |

**综合评级**: 🚫 属于进阶功能，MVP1 未规划

---

## 3. 时限管理 (Deadline & Docket) — US-DL-01 ~ US-DL-07

### US-DL-01 时限模板配置 ❌

> 作为 **管理员**，我希望通过参数界面维护各种时限模板（起算基准、年/月/日增量、内部时限、提醒规则、默认监督人/责任人），使系统在各个业务场景中自动计算期限。

| 子能力 | 实现状态 | 说明 |
|---|---|---|
| T_TaskTemplate 表 | ❌ | 无此表 |
| 时限模板 CRUD UI | ❌ | 无此页面 |
| 时限计算参数 (DeadlineBase, AddYears/Months/Days, InnerOffsetDays, R1/R2/R3_OffsetDays) | ❌ | 无计算引擎 |

**综合评级**: ❌ MVP1 scope 要求 "Task templates (minimal set)" 但未实现

---

### US-DL-02 自动创建时限任务 ❌

> 作为 **流程/形式审查人员**，当录入某些中间文件或案件事件时，我希望系统自动按照配置生成时限任务。

| 子能力 | 实现状态 | 说明 |
|---|---|---|
| 从文档事件自动创建任务 | ❌ | 无联动 |
| 从案件事件自动创建任务 | ❌ | 无联动 |
| 基于 T_TaskTemplate 计算绝限/内部限/提醒 | ❌ | 无计算引擎 |

**综合评级**: ❌ 依赖 US-DL-01 的模板表

---

### US-DL-03 日常提醒 – 作业人视角 🟡

> 作为 **代理人/作业人**，我希望每天看到属于我负责的、即将到期和已到期的任务列表，并能快速核销或修改完成日。

| 子能力 | 实现状态 | 说明 |
|---|---|---|
| 任务列表 (按 assigned_to 筛选) | ✅ | TaskList.vue + API |
| 按到期状态筛选 (即将到期/已过期) | 🟡 | 前端有基础筛选 |
| 核销/标记完成 | ✅ | 状态更新 API |
| 今日提醒页面 | ✅ | TodayReminders.vue |
| 无 InnerDeadline 区分 (官方绝限 vs 内部限) | ❌ | 模型中无此字段 |

**综合评级**: 🟡 基础任务视图可用，缺内部限/多级提醒

---

### US-DL-04 日常提醒 – 监督人视角 ❌

> 作为 **监督人/组长/合伙人**，我希望按作业人、任务类型、期限状态等维度查看本组任务，监督未完成或已超期任务，并能调整责任人或关闭任务。

| 子能力 | 实现状态 | 说明 |
|---|---|---|
| 监督人专属视图 | ❌ | 无 SupervisorID 字段，无监督人视图 |
| 按作业人/类型/状态多维筛选 | ❌ | 仅基础筛选 |
| 调整责任人 | 🟡 | 可修改 assigned_to，但无 supervisor 角色 |

**综合评级**: ❌ 无 Worker/Supervisor 双角色机制

---

### US-DL-05 手工维护时限任务 ✅

> 作为 **流程人员**，我希望可以为特殊案件手工新增、编辑、删除时限任务，以应对非常规的期限要求。

| 子能力 | 实现状态 | 说明 |
|---|---|---|
| 任务 CRUD (创建/编辑/删除) | ✅ | 完整的 Task API |
| 权限控制 | ✅ | require_perm |
| 状态变更 (OPEN → COMPLETED/CANCELLED) | ✅ | 已实现 |
| T_TaskLog (操作日志) | ❌ | 无审计日志 |

**综合评级**: ✅ 手工 CRUD 可用（缺 TaskLog，但核心功能满足）

---

### US-DL-06 专项检索：申请费 / 实审请求时限 🚫

> 作为 **流程人员**，我希望有专门的"申请费时限检索"和"实审请求时限检索"界面。

| 子能力 | 实现状态 | 说明 |
|---|---|---|
| 申请费时限检索界面 | ❌ | 未实现 |
| 实审请求时限检索界面 | ❌ | 未实现 |

**综合评级**: 🚫 依赖 T_TaskTemplate + 专项时限类型，属于进阶功能

---

### US-DL-07 登录提醒与清单打印 🟡

> 作为 **任何用户**，我希望登录系统时能看到属于自己的"今日提醒清单"，并能将列表打印。

| 子能力 | 实现状态 | 说明 |
|---|---|---|
| 今日提醒清单页面 | ✅ | TodayReminders.vue |
| 打印清单 | ❌ | 无打印功能 |

**综合评级**: 🟡 页面存在但无打印

---

## 4. 费用管理 (Fee Management) — US-FE-01 ~ US-FE-08

### US-FE-01 费用草单生成与维护 ✅

> 作为流程/财务人员，我希望按"案件 + 草单类型"生成并维护费用草单，草单里可以有多条费用明细，支持自动从标准费率表计算金额，也支持手工调整。

| 子能力 | 实现状态 | 说明 |
|---|---|---|
| 草单 CRUD (T_FeeDraft) | ✅ | API + FeeDraftCreate.vue / FeeDraftDetail.vue |
| 草单明细 CRUD (T_FeeItem) | ✅ | API 支持明细操作 |
| 手工调整金额 | ✅ | 明细可编辑 |
| 从费率表自动计算 | ❌ | 无 CalcMode/CalcParams 引擎 |
| TotalGov/TotalService/TotalMisc 分项汇总 | ❌ | 只有 total_amount |

**综合评级**: ✅ 手工 CRUD 满足 MVP1 要求；自动计算为增强功能

---

### US-FE-02 标准费率与费减/折扣计算 🟡

> 作为财务人员，我希望通过标准费率表维护各国各类费用，草单生成时根据案件类型、国别、年号、费减比例、折扣率自动计算金额。

| 子能力 | 实现状态 | 说明 |
|---|---|---|
| 费率表 CRUD (T_FeeRate) | ✅ | API + FeeRates.vue |
| 多维度费率 (Group, CountryCode, CaseType, PatentCategory) | ❌ | 只有 fee_code, fee_type, category |
| CalcMode 计算引擎 (FIXED/PER_CLAIM/PER_PAGE/TIER/FORMULA) | ❌ | 无计算引擎 |
| 费减计算 (AllowReduction + Case.FeeReduction) | ❌ | 无费减逻辑 |
| 折扣计算 (DiscountRate) | ❌ | 无折扣逻辑 |
| 有效期 (EffectiveFrom/To) | ❌ | 无时间范围字段 |

**综合评级**: 🟡 基础费率 CRUD 可用，自动计算引擎未实现

---

### US-FE-03 官费清单与缴费 🚫

> 作为财务人员，我希望从多个案件的草单中汇总官方费用，生成"官费清单"，导出给官方客户端，缴费后登记实际缴费日期、发票号、凭证号等。

| 子能力 | 实现状态 | 说明 |
|---|---|---|
| T_PayList (官费清单头) | ❌ | 未实现 |
| T_GovPayment (官费缴费明细) | ❌ | 未实现 |
| 导出官方客户端适配格式 | ❌ | 未实现 |
| 缴费登记 (PaidAmt, PaidDate, InvoiceNo, VoucherNo) | ❌ | 未实现 |

**综合评级**: 🚫 官费清单全流程未实现，属于进阶功能

---

### US-FE-04 授权费 / 年登印费管理 🚫

> 作为流程/财务人员，我希望从"已授权但尚未缴登记费"的案件中批量提取应缴费项，根据客户指示生成通知函和草单。

**综合评级**: 🚫 依赖授权流程 + 批量操作，MVP1 排除

---

### US-FE-05 年费管理（多年度） 🚫

> 作为年费人员，我希望按到期区间批量提取年费案件，管理客户指示，生成年费草单+通知函。

**综合评级**: 🚫 MVP1 明确排除 "Annual fee/renewal batch, grace rules"

---

### US-FE-06 个案收款登记 🟡

> 作为财务人员，我希望针对每个案件登记收到的款项，记录费用代码、金额、币种、是否欠款、是否可计酬和发票号。

| 子能力 | 实现状态 | 说明 |
|---|---|---|
| T_CaseReceipt 表 | ✅ | 基础字段已有 |
| FeeCode / YearNo | ❌ | 未实现 |
| IsArrears (是否欠款) | ❌ | 未实现 |
| IsCommissionable (是否可计酬) | ❌ | 未实现 |
| InvoiceNo (发票号) | ❌ | 未实现 |
| 从 Offset 拆分自动写入 | 🟡 | 基础联动存在 |

**综合评级**: 🟡 基础记录可用，丰富字段缺失

---

### US-FE-07 支出费用管理 🚫

> 作为财务或部门负责人，我希望记录每个案件的翻译费、绘图费、交通费等支出费用。

**综合评级**: 🚫 T_Expense 未实现，属于进阶功能

---

### US-FE-08 费用情况综合查询 ❌

> 作为管理层或财务，我希望查询某案件或某客户的"缴费情况一览 + 收款情况一览"。

| 子能力 | 实现状态 | 说明 |
|---|---|---|
| 官费缴费一览 (T_GovPayment) | ❌ | 无此表 |
| 个案收款一览 (T_CaseReceipt) | 🟡 | CaseReceiptsSummary 组件，但字段不完整 |
| 双表对照查询界面 | ❌ | 未实现 |

**综合评级**: ❌ 无综合查询界面

---

## 5. 账单、收款、催款与坏账 (Billing) — US-BL-01 ~ US-BL-07

### US-BL-01 从费用草单生成账单 ✅

> 作为财务，我希望能选择若干费用草单，为指定客户生成账单，账单中按案件+费用明细展开，并自动拆分为官费/服务费/杂费小计。

| 子能力 | 实现状态 | 说明 |
|---|---|---|
| 从草单生成账单 (multi-draft → one bill) | ✅ | POST /api/v1/billing/bills/from-drafts |
| 同一客户约束 | ✅ | 后端校验 |
| 账单明细 (T_BillItem) | ✅ | 从 FeeItem 复制 |
| TotalGov/TotalService/TotalMisc 小计 | ❌ | 只有 total_amount |
| 折扣率 (DiscountRate) | ❌ | 未实现 |

**综合评级**: ✅ 核心生成流程可用

---

### US-BL-02 手工维护账单 ✅

> 作为财务，我希望在没有草单的情况下也能手工录入账单头和明细。

| 子能力 | 实现状态 | 说明 |
|---|---|---|
| 手工创建账单 | ✅ | POST /api/v1/billing/bills |
| 手工添加明细 | ✅ | BillItem CRUD |
| Direction (AR/AP) | ❌ | 无应收/应付方向区分 |
| 调整性账单 (Credit Note) | ❌ | 不支持负账单 |

**综合评级**: ✅ 基础手工账单可用

---

### US-BL-03 账单打印与模板输出 ✅

> 作为财务和客户经理，我希望账单可以按不同版式打印或导出 Word/Excel。

| 子能力 | 实现状态 | 说明 |
|---|---|---|
| 账单 Word 模板生成 (docxtpl) | ✅ | doc_render_bill_context.py + template rendering |
| 中文版账单 | ✅ | 已实现 |
| 英文版账单 | 🟡 | 取决于模板文件是否已准备 |
| Excel 导出 | ❌ | 未实现 |

**综合评级**: ✅ Word 输出可用，是 MVP1 成功标准之一

---

### US-BL-04 收款登记与账单冲销 ✅

> 作为财务，我希望记录每一笔来自客户的收款，并通过"冲销"机制将收款金额分配到具体账单上。

| 子能力 | 实现状态 | 说明 |
|---|---|---|
| 收款登记 (T_Payment) | ✅ | Payment CRUD |
| 冲销到账单 (T_Offset) | ✅ | Offset endpoint |
| 更新账单余额/状态 | ✅ | Bill.balance/status 自动更新 |
| T_PaymentLine (分配行) | ❌ | 无 PaymentLine 拆分 |
| 一笔收款冲销多张账单 | 🟡 | 基础实现，无精细 PaymentLine 分配 |

**综合评级**: ✅ 核心冲销流程可用

---

### US-BL-05 冲销反转（反冲销） 🚫

> 作为财务，我希望当冲销出错时可以对冲销记录进行反转。

| 子能力 | 实现状态 | 说明 |
|---|---|---|
| T_Offset.IsReversed / ReversedAt / ReversedBy | ❌ | 无反冲销字段 |
| 反冲销 API | ❌ | 未实现 |
| 反冲销后恢复 Bill.Balance/Status | ❌ | 未实现 |

**综合评级**: 🚫 属于进阶财务功能

---

### US-BL-06 坏账与催款管理 🚫

> 作为管理层/财务，我希望可以将长期未收账单标记为坏账，并生成催款单和催款函。

**综合评级**: 🚫 MVP1 明确排除 "Dunning, bad debt"

---

### US-BL-07 预收款管理 🚫

> 作为财务，我希望可以先登记客户预收款，之后陆续冲抵不同案件的账单。

| 子能力 | 实现状态 | 说明 |
|---|---|---|
| 预收款登记 (Payment without Bill) | 🟡 | 可创建 Payment，但无 PaymentLine.BalanceAmt 跟踪 |
| 预收款→账单冲销 | ❌ | 无 PaymentLine 分配机制 |
| 预收余额查询 | ❌ | 无 |

**综合评级**: 🚫 依赖 T_PaymentLine 表，属于进阶功能

---

## 6. 代理人酬金管理 (Commission) — US-COM-01 ~ US-COM-06

### US-COM-01 提成规则配置 🚫
### US-COM-02 提成记录自动生成 🚫
### US-COM-03 多代理人分摊 🚫
### US-COM-04 款到后才能结算 🚫
### US-COM-05 强制可结算（特殊标记） 🚫
### US-COM-06 提成结算批次与报表 🚫

**综合评级**: 🚫 整个模块 MVP1 明确排除 "Commission calculation & settlement"

---

## 7. 顾问/检索项目 (Consulting & Search) — US-CS-01 ~ US-CS-05

### US-CS-01 顾问/检索项目立案 🚫
### US-CS-02 内部任务管理 🚫
### US-CS-03 支出费用记录 🚫
### US-CS-04 服务费草单生成 🚫
### US-CS-05 账单、收款与提成 🚫

**综合评级**: 🚫 整个模块 MVP1 明确排除

---

## 汇总统计

### 按评级分布

| 评级 | 数量 | User Story IDs |
|---|---|---|
| ✅ 已实现 | 8 | US-CM-04, US-DL-05, US-FE-01, US-BL-01, US-BL-02, US-BL-03, US-BL-04, (partial US-DL-07) |
| 🟡 部分实现 | 9 | US-CM-01, US-CM-03, US-WD-01, US-WD-05, US-WD-06, US-DL-03, US-DL-07, US-FE-02, US-FE-06 |
| ❌ 未实现 (应在 MVP1 范围) | 5 | US-WD-02, US-WD-03, US-WD-04, US-DL-01, US-DL-02 |
| ❌ 未实现 (可选/增强) | 3 | US-DL-04, US-DL-06, US-FE-08 |
| 🚫 MVP1 明确排除 | 20 | US-CM-02, US-CM-05, US-WD-07, US-FE-03~05, US-FE-07, US-BL-05~07, US-COM-01~06, US-CS-01~05 |
| **合计** | **45** | |

### MVP1 范围内最关键的未实现 User Story（建议优先补齐）

| 优先级 | US ID | 名称 | 影响 |
|---|---|---|---|
| **P0** | US-DL-01 | 时限模板配置 | MVP1 scope 明确要求 "Task templates (minimal set)"；是 US-DL-02/03/04 的前置依赖 |
| **P0** | US-DL-02 | 自动创建时限任务 | 依赖 US-DL-01；是"收到 OA → 自动生成答复时限"的核心 |
| **P1** | US-WD-02 | 发文登记与自动核销 | "登记去文回复某来文 → 自动核销时限"是知产业务核心流程 |
| **P1** | US-WD-03 | 期限联动 | 文档→时限自动化引擎，是 US-DL-02 的触发源 |
| **P1** | US-WD-04 | 费用联动 | 文档→费用自动化，是全流程自动化的关键一环 |
| **P2** | US-DL-04 | 监督人视角 | Worker/Supervisor 双角色机制 |
| **P2** | US-FE-08 | 费用情况综合查询 | 管理层需要的报表视图 |
| **P2** | US-CM-01 补全 | 新案建立字段扩展 | 控制标记、代理人指派、国别等 35+ 字段 |

### MVP1 成功标准 vs 实现状态

| # | MVP1 成功标准 | 依赖的 User Story | 状态 |
|---|---|---|---|
| 1 | 用户可以创建案件、搜索案件、打开案件详情 | US-CM-01, US-CM-04 | ✅ 可用 |
| 2 | 用户可以登记 OA 通知（文档+附件），系统可以创建时限任务 | US-WD-01, US-WD-03, US-DL-02 | 🟡 可手工登记文档+手工创建任务；**自动联动未实现** |
| 3 | 用户可以创建费用草单并生成账单；财务可以登记收款和冲销 | US-FE-01, US-BL-01, US-BL-04 | ✅ 可用 |
| 4 | 用户可以从模板生成 Word 账单并发送给客户 | US-BL-03 | ✅ 可用 |

**结论**: MVP1 的 4 项成功标准中，标准 1/3/4 已满足；标准 2 的自动化部分（文档→时限联动）缺失，但手工流程可以绕过。
