# FPMS SPEC 2.0 Process-Follow Test Cases

> Role: Senior QA / Test Architect with 15 years of enterprise testing experience  
> Requirement baseline: `docs/FPMS SPEC 2.0.md`  
> Scope note: document-generation artifact rendering is excluded unless the business linkage itself must be validated.

## A. Test Strategy Summary

### 测试目标

- 基于 `FPMS SPEC 2.0.md` 建立一套面向业务闭环的主回归测试方案。
- 排除文档生成本体内容渲染细节，但保留文书驱动的业务联动验证。
- 覆盖从主数据、案件、往来文件、时限、费用、账单、收款、催款/坏账、提成、顾问/检索、设置/查询/报表的全链路 follow。

### 流程组织原则

- 按业务 `process / follow` 组织，不按前后端或 API 分层。
- 每条流程都验证：
  - 主流程
  - 分支流程
  - 异常流程
  - 跨模块 follow-up
- 以“数据如何流动”作为主线：
  - `Case -> Document -> Task -> FeeDraft -> PayList/Bill -> Payment/Offset -> CaseReceipt -> Commission/Report`

### 覆盖范围

- Module 1 到 Module 8 的非文档生成业务范围
- E2E 场景 A-H 与生命周期章节 18、状态迁移章节 20
- 查询、统计、导出、打印、提醒、权限、主数据依赖、角色差异

### 主要风险

- 状态迁移不一致
- 中间文件未正确触发任务/费用
- 账单、收款、冲销、个案收款拆分错误
- 年费/授权费多年度或多阶段累计错误
- 提成基数、WaitPay、ForceSettle 规则误算
- 查询/报表/导出与最新业务数据不一致
- 权限视图与角色范围错配

### 主要假设

- `Assumption`: 文书模板渲染内容本体不在本轮主覆盖范围，仅验证生成/挂接/联动是否发生。
- `Assumption`: 币种换算规则若 `SPEC` 未展开，测试只校验字段传递与金额归集，不强行假定汇率算法。
- `Needs Clarification`: 部分报表的精确汇总口径在 `SPEC` 中偏业务描述，自动化前建议再冻结统计公式。
- `Needs Clarification`: 某些角色边界在模块说明与 E2E 中可能存在“可看/可改”粒度差异，需在 UAT 前固化权限矩阵。

## B. Process Map

### P1 主数据准备

- P1.1 客户
- P1.2 申请人
- P1.3 国家/地区
- P1.4 菌种保藏单位
- P1.5 标准费率
- P1.6 时限模板
- P1.7 全局参数
- P1.8 文档模板/信头
- Follow:
  - 主数据影响案件选择、地址、费用计算、时限生成、报表维度

### P2 案件建立与维护

- P2.1 新案建立
- P2.2 扩展信息维护
- P2.3 限制修改视图
- P2.4 案件递交批处理
- Follow:
  - 递交后进入时限、费用、后续来文链路

### P3 中间文件与往来

- P3.1 来文登记
- P3.2 去文登记
- P3.3 自动生成时限任务
- P3.4 自动生成费用草单
- P3.5 附件与存档
- P3.6 邮寄、交接单、信封
- P3.7 文件查询与清单输出
- Follow:
  - `Document -> Task`
  - `Document -> FeeDraft`
  - `ReplyTo -> Task close / Status restore`

### P4 时限任务管理

- P4.1 模板维护
- P4.2 自动任务生成
- P4.3 手工任务
- P4.4 我的任务
- P4.5 监督任务
- P4.6 今日提醒
- P4.7 专项检索
- P4.8 导出/打印
- P4.9 日志审计
- Follow:
  - 任务跟随案件事件、文书事件、年费事件变化

### P5 费用管理

- P5.1 标准费率与草单
- P5.2 官费清单与缴费
- P5.3 授权费/年费
- P5.4 个案收款
- P5.5 支出录入与统计
- P5.6 费用情况查询一览
- Follow:
  - `FeeDraft -> PayList/Bill`
  - `GovPayment/CaseReceipt/Expense -> Query/Stats`

### P6 账单、收款、预收、催款、坏账

- P6.1 账单生成
- P6.2 打印
- P6.3 收款登记
- P6.4 冲销/反冲销
- P6.5 预收款
- P6.6 催款
- P6.7 坏账
- Follow:
  - `Bill -> PaymentLine -> Offset -> CaseReceipt`
  - `Overdue -> Dunning -> Recovery/BadDebt`

### P7 提成管理

- P7.1 提成规则
- P7.2 提成记录生成
- P7.3 多代理人分摊
- P7.4 WaitPay / ForceSettle
- P7.5 结算批次
- P7.6 结算报表
- Follow:
  - `BillItem(service fee) -> Commission`
  - `CaseReceipt/PaidRatio -> Settleability`

### P8 顾问/检索项目

- P8.1 项目立案
- P8.2 内部任务
- P8.3 项目支出
- P8.4 服务费草单
- P8.5 账单/收款
- P8.6 提成
- Follow:
  - 与普通案件共享费用、账单、提成主管道

### P9 设置、查询、报表总览

- P9.1 高级案件查询
- P9.2 中间文件查询
- P9.3 费用情况查询
- P9.4 时限检索
- P9.5 案件/费用/年费/应收/提成报表
- Follow:
  - 所有报表都必须跟随最新业务数据

### P10 权限与角色

- Admin
- Formalities
- Agent
- Finance
- Supervisor / Manager
- Follow:
  - 同一业务对象在不同角色下可见/可改/可结算范围不同

## C. Simulation Test Data Catalog

### 客户

- `CL-001`: 华东创新科技有限公司，客户编号 `CUST-001`，默认账单地址上海
- `CL-002`: 北方智权咨询有限公司，客户编号 `CUST-002`
- `CL-003`: Global IP Partners，客户编号 `CUST-003`，涉外代理样本

### 申请人

- `AP-001`: 华东创新科技有限公司，法人
- `AP-002`: 张三，自然人
- `AP-003`: Tokyo Mobility KK，外国申请人

### 国家/地区

- `CTY-CN`: 中国
- `CTY-US`: 美国
- `CTY-JP`: 日本
- `CTY-HK`: 中国香港

### 用户/角色

- `USR-ADM-01`: admin，Admin
- `USR-FM-01`: formalities01，Formalities
- `USR-AG-01`: agent01，Agent/PrimaryAgent
- `USR-AG-02`: agent02，SecondAgent
- `USR-SPV-01`: supervisor01，Supervisor
- `USR-FIN-01`: finance01，Finance
- `USR-ANN-01`: annuity01，年费员

### 部门

- `DEPT-001`: 专利流程部
- `DEPT-002`: 财务部
- `DEPT-003`: 顾问项目组

### 案件

- `CASE-A-001`: 普通发明新案，`CaseNo=CN-NORMAL-2026-001`
- `CASE-B-001`: OA阶段普通案，`CaseNo=CN-OA-2026-001`
- `CASE-C-001`: PCT国际案，`CaseNo=PCT-INTL-2026-001`
- `CASE-C-002`: PCT国家阶段案，`CaseNo=PCT-NAT-2026-001`
- `CASE-D-001`: 已授权且年费监视案，`CaseNo=CN-ANN-2024-001`
- `CASE-E-001`: 无效案件，`CaseNo=INV-2026-001`
- `CASE-F-001`: 预收款样本案，`CaseNo=CN-PREPAY-2026-001`
- `CASE-H-001`: 顾问项目，`CaseNo=CONSULT-2026-001`
- `CASE-H-002`: 检索项目，`CaseNo=SEARCH-2026-001`

### 中间文件模板

- `TPL-OA-NOTICE`: `OA_NOTICE`
- `TPL-OA-REPLY`: `OA_REPLY`
- `TPL-GRANT-NOTICE`: `GRANT_NOTICE`
- `TPL-ANNUITY-NOTICE`: `ANNUITY_NOTICE`
- `TPL-DUNNING`: `DUNNING_LETTER`

### 时限模板

- `TT-APPLY`: `APPLY_FEE_LIMIT`
- `TT-OA`: `OA_REPLY_LIMIT`
- `TT-PCT-NAT`: `PCT_NATIONAL_ENTRY_LIMIT`
- `TT-GRANT`: `GRANT_CERT_FEE_LIMIT`
- `TT-ANN`: `ANNUITY_FEE_LIMIT`

### 费用/草单/账单

- `FD-APPLY-001`: 申请费草单
- `FD-OA-001`: OA草单
- `FD-GRANT-001`: 授权费草单
- `FD-ANN-001`: 年费草单
- `FD-CONSULT-001`: 顾问服务费草单
- `PL-GOV-001`: 官费清单
- `BILL-AR-001`: 申请费账单
- `BILL-AR-002`: OA账单
- `BILL-AR-003`: 年费账单
- `BILL-AR-004`: 顾问项目账单

### 收款/预收/冲销

- `PAY-001`: 正常收款 10,000 CNY
- `PAY-002`: 部分收款 5,000 CNY
- `PAY-003`: 预收款 30,000 CNY
- `OFF-001`: 申请费账单冲销
- `OFF-002`: 预收款冲销多账单
- `OFF-003`: 反冲销样本

### 支出

- `EXP-001`: 检索数据库费 2,000 CNY
- `EXP-002`: 翻译费 3,500 CNY
- `EXP-003`: 差旅费 1,200 CNY
- `EXP-004`: 边界金额支出 999999.99 CNY
- `EXP-005`: 部门为空、经手人为空支出

### 提成规则

- `COMR-001`: NORMAL + SERVICE
- `COMR-002`: OA + SERVICE
- `COMR-003`: ANNUITY_SERVICE
- `COMR-004`: CONSULTING
- `COMR-005`: SEARCH

### 日期样本

- `DT-NEW-001`: `2026-04-01`
- `DT-FILING-001`: `2026-04-03`
- `DT-DUE-001`: `2026-05-03`
- `DT-OA-001`: `2026-06-10`
- `DT-GRANT-001`: `2026-08-20`
- `DT-ANN-001`: `2027-01-31`
- `DT-BAD-REV`: 起始日 `2026-12-31`，结束日 `2026-01-01`

### 非法/冲突数据

- `BAD-CASE-NO-001`: 重复案卷号 `CN-NORMAL-2026-001`
- `BAD-WORKER-404`: 不存在经手人 `USR-NO-404`
- `BAD-DEPT-404`: 不存在部门 `DEPT-404`
- `BAD-BILL-404`: 不存在账单号 `BILL-NO-404`
- `BAD-PERM-FIN-AGENT`: Agent 账号尝试执行 Finance 动作

## D. Test Case Suite

### P1 主数据准备

#### TC-MD-001

- `Test Case ID`: `TC-MD-001`
- `Process Area`: 主数据准备
- `Process Step`: 客户/申请人/国家主数据初始化
- `Title`: 建立业务主数据并用于后续流程引用
- `Objective`: 验证客户、申请人、国家主数据可被案件/账单/文书正确引用
- `Requirement Reference`: `2.3.2`, `2.4.3`, `9.2.1`
- `Priority`: 高
- `Preconditions`: Admin 已登录
- `Simulation Test Data`: `CL-001`, `CL-002`, `AP-001`, `AP-002`, `CTY-CN`, `CTY-US`
- `Steps`: 创建客户与申请人；设置默认地址；新建案件时引用这些主数据
- `Expected Results`: 主数据可选、可回填、地址跟随正确
- `Post-conditions`: 主数据处于可复用状态
- `Negative / Edge Variant`: 缺默认地址时系统应提示或警告
- `Regression Tag`: `masterdata`, `dependency`
- `Automation Candidate`: 高
- `Notes / Assumptions`: 地址缺失时是警告还是强校验需按实现冻结

### P2 案件建立与维护

#### TC-CM-001

- `Test Case ID`: `TC-CM-001`
- `Process Area`: 案件建立与维护
- `Process Step`: 新案建立
- `Title`: 创建普通新案并完成关键字段校验
- `Objective`: 验证新案建立、唯一案号、关键日期和参与方约束
- `Requirement Reference`: `FR-CM-01`, `FR-CM-02`, `2.4`
- `Priority`: 高
- `Preconditions`: 主数据已准备
- `Simulation Test Data`: `CASE-A-001`, `CL-001`, `AP-001`, `USR-AG-01`
- `Steps`: 录入 CaseNo、CaseType、PatentCategory、Client、Applicant、FilingDate 等并保存
- `Expected Results`: 保存成功；Case 状态和关联方正确入库；案号全局唯一
- `Post-conditions`: 生成可继续递交的案件主档
- `Negative / Edge Variant`: 用 `BAD-CASE-NO-001` 重复保存应失败；关键日期缺失应拦截
- `Regression Tag`: `case-create`
- `Automation Candidate`: 高
- `Notes / Assumptions`: 不验证文书生成

#### TC-CM-002

- `Test Case ID`: `TC-CM-002`
- `Process Area`: 案件建立与维护
- `Process Step`: 限制修改视图
- `Title`: 代理人仅能修改白名单字段
- `Objective`: 验证 `CaseEditLimited` 权限边界
- `Requirement Reference`: `FR-CM-06`, `2.6`
- `Priority`: 高
- `Preconditions`: `CASE-A-001` 已存在；Agent 用户已登录
- `Simulation Test Data`: `USR-AG-01`, `CASE-A-001`
- `Steps`: 进入补充信息视图；修改标题、发明人、备注；尝试修改 Status、CaseNo
- `Expected Results`: 白名单字段可保存；关键字段只读或保存失败
- `Post-conditions`: 仅允许字段被更新
- `Negative / Edge Variant`: 无 `CaseEditLimited` 权限时看不到入口
- `Regression Tag`: `permission`, `case-edit-limited`
- `Automation Candidate`: 中
- `Notes / Assumptions`: 权限入口可见性也需验证

#### TC-CM-003

- `Test Case ID`: `TC-CM-003`
- `Process Area`: 案件建立与维护
- `Process Step`: 案件递交批处理
- `Title`: 批量递交未递交案件并触发后续时限
- `Objective`: 验证 `NOT_FILED -> WAITING_RECEIPT` 与申请费时限 follow
- `Requirement Reference`: `FR-CM-07`, `2.7`, `10.4`, `10.5`
- `Priority`: 高
- `Preconditions`: 至少 2 个 `NOT_FILED` 案件存在
- `Simulation Test Data`: `CASE-A-001`, `DT-FILING-001`, `TT-APPLY`
- `Steps`: 检索未递交案件；勾选；设置递交日和是否同时提实审；执行批处理
- `Expected Results`: 状态更新；递交日写入；必要时生成申请费时限任务
- `Post-conditions`: 案件进入后续费用链
- `Negative / Edge Variant`: 空选中执行应提示；状态非 `NOT_FILED` 不应进入批处理结果
- `Regression Tag`: `batch-filing`, `follow-task`
- `Automation Candidate`: 中
- `Notes / Assumptions`: 递交清单文档内容不做本轮细测

### P3 中间文件与往来

#### TC-WD-001

- `Test Case ID`: `TC-WD-001`
- `Process Area`: 中间文件与往来
- `Process Step`: OA来文登记
- `Title`: 登记 OA 来文并自动生成 OA 答复时限任务
- `Objective`: 验证 `Document -> Task` 联动
- `Requirement Reference`: `FR-WD-04`, `3.4.3`, `11.3`, `11.4`
- `Priority`: 高
- `Preconditions`: `CASE-B-001` 处于实审阶段；`TPL-OA-NOTICE` 与 `TT-OA` 已配置
- `Simulation Test Data`: `CASE-B-001`, `TPL-OA-NOTICE`, `DT-OA-001`
- `Steps`: 走向导 Step1/2 登记 OA 来文；完成 Step3 任务生成
- `Expected Results`: 生成 `OA_REPLY_LIMIT` 任务，含 Deadline、InnerDeadline、Remind1-3、Worker/Supervisor
- `Post-conditions`: 案件具有待处理 OA 时限
- `Negative / Edge Variant`: 模板缺少 DeadlineTemplateCode 时不应生成任务且需明确提示
- `Regression Tag`: `document`, `task-linkage`
- `Automation Candidate`: 高
- `Notes / Assumptions`: 任务责任人选择优先级按模板/案件配置

#### TC-WD-002

- `Test Case ID`: `TC-WD-002`
- `Process Area`: 中间文件与往来
- `Process Step`: OA答复去文
- `Title`: 登记 OA 答复并自动核销对应时限任务
- `Objective`: 验证 `ReplyTo -> Task done / Status restore`
- `Requirement Reference`: `FR-WD-02`, `3.4.2`, `11.6`, `11.7`
- `Priority`: 高
- `Preconditions`: `TC-WD-001` 已完成
- `Simulation Test Data`: `CASE-B-001`, `TPL-OA-REPLY`
- `Steps`: 录入 OA_REPLY，指定 ReplyToID 指向 OA_NOTICE，完成向导
- `Expected Results`: 对应任务状态改为 DONE；DoneDate 写入；案件状态按模板恢复
- `Post-conditions`: OA 回复链闭环
- `Negative / Edge Variant`: ReplyToID 指向错误来文时不得错误核销其他任务
- `Regression Tag`: `replyto`, `task-close`
- `Automation Candidate`: 高
- `Notes / Assumptions`: StatusRestore 需按模板生效

#### TC-WD-003

- `Test Case ID`: `TC-WD-003`
- `Process Area`: 中间文件与往来
- `Process Step`: 授权通知联动
- `Title`: 授权通知同时驱动授权费任务与草单
- `Objective`: 验证 `Document -> FeeDraft + Grant task`
- `Requirement Reference`: `3.4.4`, `5.7`, `18.1.6`
- `Priority`: 高
- `Preconditions`: 待授权案件存在；授权模板配置完成
- `Simulation Test Data`: `TPL-GRANT-NOTICE`, `CASE-D-001`, `DT-GRANT-001`
- `Steps`: 录入授权通知；完成草单生成步骤
- `Expected Results`: 创建授权费任务/记录；生成 `GRANT_FEE` 草单
- `Post-conditions`: 可继续进入官费清单与账单
- `Negative / Edge Variant`: 缺失授权关键字段时不得生成不完整草单
- `Regression Tag`: `grant`, `fee-linkage`
- `Automation Candidate`: 中
- `Notes / Assumptions`: 授权费任务与 `T_GrantFeeTask` 都应被校验

### P4 时限管理

#### TC-DL-001

- `Test Case ID`: `TC-DL-001`
- `Process Area`: 时限管理
- `Process Step`: 时限模板维护
- `Title`: 创建时限模板并校验提醒规则
- `Objective`: 验证模板字段与 DailyRemind 约束
- `Requirement Reference`: `FR-DL-01`, `4.3.1`, `4.4`
- `Priority`: 高
- `Preconditions`: Admin/流程管理员登录
- `Simulation Test Data`: `TT-APPLY`, `TT-OA`, `TT-ANN`
- `Steps`: 创建模板；设置 Base、Offset、InnerOffset、R1/R2/R3、DailyRemind
- `Expected Results`: 合法模板保存成功
- `Post-conditions`: 模板可供自动任务使用
- `Negative / Edge Variant`: `DailyRemind=true` 但无起点规则时应校验失败
- `Regression Tag`: `task-template`
- `Automation Candidate`: 高
- `Notes / Assumptions`: `CUSTOM/CASE_EVENT` 基准依赖调用方传值

#### TC-DL-002

- `Test Case ID`: `TC-DL-002`
- `Process Area`: 时限管理
- `Process Step`: 作业人与监督人视图
- `Title`: 我的任务/监督任务/今日提醒按角色正确展示
- `Objective`: 验证角色维度和排序、筛选逻辑
- `Requirement Reference`: `FR-DL-03`, `FR-DL-04`, `FR-DL-05`, `FR-DL-08`
- `Priority`: 高
- `Preconditions`: 多条任务已生成
- `Simulation Test Data`: `USR-AG-01`, `USR-SPV-01`, 任务状态 `OPEN`, `DONE`, `OVERDUE`
- `Steps`: 分别以 Worker、Supervisor 登录查看三个视图
- `Expected Results`: Worker 只见本人任务；Supervisor 可按作业人筛；首页提醒只显示今日相关任务
- `Post-conditions`: 无
- `Negative / Edge Variant`: 无相关任务时列表为空但页面可正常加载
- `Regression Tag`: `task-view`, `role`
- `Automation Candidate`: 中
- `Notes / Assumptions`: 排序优先内部限后官方限

#### TC-DL-003

- `Test Case ID`: `TC-DL-003`
- `Process Area`: 时限管理
- `Process Step`: 手工任务维护与日志
- `Title`: 手工新增/编辑/核销/取消核销/取消任务并记录日志
- `Objective`: 验证高危操作权限和审计日志
- `Requirement Reference`: `FR-DL-06`, `FR-DL-10`, `4.6`, `4.3.3`
- `Priority`: 高
- `Preconditions`: 流程人员登录
- `Simulation Test Data`: 自定义任务 `TASK-MAN-001`
- `Steps`: 创建手工任务；修改日期；核销；取消核销；取消任务；查看日志
- `Expected Results`: 每一步均写日志；无权限用户不能删除/取消
- `Post-conditions`: 任务处于最终状态，日志完整
- `Negative / Edge Variant`: 非法状态下取消核销应失败
- `Regression Tag`: `task-log`, `manual-task`
- `Automation Candidate`: 中
- `Notes / Assumptions`: 日志动作码需与规格一致

#### TC-DL-004

- `Test Case ID`: `TC-DL-004`
- `Process Area`: 时限管理
- `Process Step`: 专项检索与清单输出
- `Title`: 申请费/实审时限检索及导出打印
- `Objective`: 验证专项检索条件和列表输出
- `Requirement Reference`: `FR-DL-07`, `FR-DL-09`, `4.8`, `4.9`
- `Priority`: 中
- `Preconditions`: 存在未缴申请费、未提实审的样本案
- `Simulation Test Data`: `CASE-A-001`, 到期窗口 `DT-DUE-001`
- `Steps`: 执行两类检索；导出；打印预览
- `Expected Results`: 只返回符合条件案件；导出集与页面一致；空结果也允许导出空清单
- `Post-conditions`: 导出记录可供审计
- `Negative / Edge Variant`: 日期倒置 `DT-BAD-REV` 应失败
- `Regression Tag`: `special-search`, `export-print`
- `Automation Candidate`: 中
- `Notes / Assumptions`: 只校验清单存在和数据一致，不校验文档排版像素细节

### P5 费用管理

#### TC-FE-001

- `Test Case ID`: `TC-FE-001`
- `Process Area`: 费用管理
- `Process Step`: 草单生成与金额计算
- `Title`: 从标准费率生成申请费/OA/授权费/年费草单
- `Objective`: 验证费率匹配、FeeItem 汇总、草单状态
- `Requirement Reference`: `FR-FE-01`, `FR-FE-02`, `FR-FE-03`, `5.4`, `5.5`
- `Priority`: 高
- `Preconditions`: 费率已配置
- `Simulation Test Data`: `FD-APPLY-001`, `FD-OA-001`, `FD-GRANT-001`, `FD-ANN-001`
- `Steps`: 分别触发四类草单；检查 FeeItem 和金额汇总
- `Expected Results`: 草单头、明细、金额字段正确；状态初始合理
- `Post-conditions`: 可用于官费清单或账单
- `Negative / Edge Variant`: 缺费率时应报配置缺失，不得生成空壳草单
- `Regression Tag`: `fee-draft`, `rate-calc`
- `Automation Candidate`: 高
- `Notes / Assumptions`: 汇率换算若存在，以系统配置为准

#### TC-FE-002

- `Test Case ID`: `TC-FE-002`
- `Process Area`: 费用管理
- `Process Step`: 官费清单与官方缴费
- `Title`: 从 GOV 明细生成官费清单并登记缴费
- `Objective`: 验证 `FeeDraft -> PayList -> GovPayment`
- `Requirement Reference`: `FR-FE-04`, `5.6`, `10.7`, `13.7`
- `Priority`: 高
- `Preconditions`: 有 GOV FeeItem 的草单已存在
- `Simulation Test Data`: `PL-GOV-001`, 发票号 `INV-GOV-001`
- `Steps`: 生成清单；登记 PaidAmt、PaidDate、InvoiceNo
- `Expected Results`: 只提取 GOV 明细；Paid 字段更新正确；可进入查询总览上半表
- `Post-conditions`: 官费缴费记录存在
- `Negative / Edge Variant`: 非 GOV 明细不得进入清单
- `Regression Tag`: `gov-payment`
- `Automation Candidate`: 中
- `Notes / Assumptions`: 导出官方系统文件仅验证存在

#### TC-FE-003

- `Test Case ID`: `TC-FE-003`
- `Process Area`: 费用管理
- `Process Step`: 支出录入与统计
- `Title`: 录入支出并验证案件/客户/经手人/部门/毛利统计
- `Objective`: 验证 `Expense -> Stats`
- `Requirement Reference`: `FR-FE-08`, `5.10.1`, `5.10.2`
- `Priority`: 高
- `Preconditions`: `CASE-H-001`、部门、经手人存在
- `Simulation Test Data`: `EXP-001`, `EXP-002`, `EXP-003`, `EXP-005`, `DEPT-003`, `USR-AG-01`
- `Steps`: 录入多笔支出；按案件、客户、经手人、部门查询；查看毛利分析
- `Expected Results`: 统计按指定维度正确聚合；空部门/空经手人记录不应错误归入其他桶
- `Post-conditions`: 支出进入统计口径
- `Negative / Edge Variant`: `BAD-WORKER-404` / `BAD-DEPT-404` 应失败；金额 `0` 或超大值按规则处理
- `Regression Tag`: `expense`, `stats`
- `Automation Candidate`: 高
- `Notes / Assumptions`: 毛利=收入-支出，按规格现有口径验证

#### TC-FE-004

- `Test Case ID`: `TC-FE-004`
- `Process Area`: 费用管理
- `Process Step`: 费用情况查询一览
- `Title`: 联查官费缴费与个案收款
- `Objective`: 验证双表查询、筛选、费用类型过滤
- `Requirement Reference`: `FR-FE-09`, `5.11`
- `Priority`: 高
- `Preconditions`: 官费缴费记录和个案收款记录都存在
- `Simulation Test Data`: `CASE-A-001`, `CASE-D-001`, `PL-GOV-001`, `PAY-001`
- `Steps`: 按案号、申请号、客户、费用类型、日期范围查询上半表和下半表
- `Expected Results`: 上下半表结果口径正确；费用类型过滤生效；无权限用户只能看授权范围内 pane
- `Post-conditions`: 无
- `Negative / Edge Variant`: 日期倒置应失败；无结果时页面空态正确
- `Regression Tag`: `fee-overview`
- `Automation Candidate`: 中
- `Notes / Assumptions`: 只验证查询结果，不验证打印版式

### P6 账单、收款、预收、催款、坏账

#### TC-BL-001

- `Test Case ID`: `TC-BL-001`
- `Process Area`: 账单与收款
- `Process Step`: 账单生成与打印
- `Title`: 从费用草单生成 AR 账单并执行打印
- `Objective`: 验证 `FeeDraft -> Bill` 以及打印入口
- `Requirement Reference`: `FR-BL-02`, `FR-BL-03`, `FR-BL-04`, `6.4`, `6.5`
- `Priority`: 高
- `Preconditions`: 草单已锁定且具备明细
- `Simulation Test Data`: `BILL-AR-001`, `FD-APPLY-001`
- `Steps`: 从草单生成账单；查看 BillItem；执行打印
- `Expected Results`: 金额、余额、状态初始正确；打印产物可触发
- `Post-conditions`: 账单可进入收款链
- `Negative / Edge Variant`: 未锁定草单不应允许开票
- `Regression Tag`: `billing`
- `Automation Candidate`: 中
- `Notes / Assumptions`: 不测模板排版内容

#### TC-BL-002

- `Test Case ID`: `TC-BL-002`
- `Process Area`: 账单与收款
- `Process Step`: 收款登记与冲销
- `Title`: 客户付款后完成收款、冲销和个案收款拆分
- `Objective`: 验证 `Payment -> Offset -> CaseReceipt`
- `Requirement Reference`: `FR-BL-05`, `10.9`, `6.6`
- `Priority`: 高
- `Preconditions`: 未结清账单存在
- `Simulation Test Data`: `PAY-001`, `OFF-001`, `BILL-AR-001`
- `Steps`: 创建收款；对账单冲销；查看账单余额、PaymentLine、CaseReceipt
- `Expected Results`: Balance 正确递减；账单状态更新；CaseReceipt 按 BillItem 比例拆分
- `Post-conditions`: 应收变实收
- `Negative / Edge Variant`: 冲销金额超过余额应失败；不存在账单 `BAD-BILL-404` 应失败
- `Regression Tag`: `payment`, `offset`, `case-receipt`
- `Automation Candidate`: 高
- `Notes / Assumptions`: 比例拆分精度需按系统 rounding 规则验证

#### TC-BL-003

- `Test Case ID`: `TC-BL-003`
- `Process Area`: 账单与收款
- `Process Step`: 反冲销
- `Title`: 已冲销账单执行反冲销并回滚余额
- `Objective`: 验证 `Offset` reversal 一致性
- `Requirement Reference`: `FR-BL-06`, `6.6.3`
- `Priority`: 中
- `Preconditions`: `TC-BL-002` 已完成
- `Simulation Test Data`: `OFF-003`
- `Steps`: 对已存在冲销执行反冲销
- `Expected Results`: Bill/PaymentLine/CaseReceipt 回滚到反冲销后的正确状态
- `Post-conditions`: 冲销记录反向生效
- `Negative / Edge Variant`: 已反转记录再次反转应失败
- `Regression Tag`: `offset-reversal`
- `Automation Candidate`: 中
- `Notes / Assumptions`: 保留审计历史

#### TC-BL-004

- `Test Case ID`: `TC-BL-004`
- `Process Area`: 预收款
- `Process Step`: 预收款登记与后续冲销
- `Title`: 预收款池被后续账单多次消耗并转化为案卷实收
- `Objective`: 验证 `Prepayment -> Offset -> CaseReceipt`
- `Requirement Reference`: `FR-BL-09`, `15.3` 至 `15.8`
- `Priority`: 高
- `Preconditions`: 客户尚无绑定账单
- `Simulation Test Data`: `PAY-003`, `BILL-AR-003`, `BILL-AR-004`, `OFF-002`
- `Steps`: 录入预收款；生成后续账单；用预收款分次冲销多张账单
- `Expected Results`: PaymentLine 余额递减；CaseReceipt 随具体账单和 BillItem 更新；未绑定余额仍保留为预收
- `Post-conditions`: 预收余额与案卷实收并存
- `Negative / Edge Variant`: 退款/负账单调整需正确减少预收余额
- `Regression Tag`: `prepayment`
- `Automation Candidate`: 中
- `Notes / Assumptions`: 直接改 PaymentLine 为不推荐路径，只做负面检查

#### TC-BL-005

- `Test Case ID`: `TC-BL-005`
- `Process Area`: 催款与坏账
- `Process Step`: 逾期、催款、坏账、坏账后回款
- `Title`: 催款与坏账生命周期闭环
- `Objective`: 验证 `Overdue -> Dunning -> BadDebt -> Recovery`
- `Requirement Reference`: `FR-BL-07`, `FR-BL-08`, `16.3` 至 `16.9`
- `Priority`: 高
- `Preconditions`: 逾期账单存在
- `Simulation Test Data`: `BILL-AR-002`, 催款轮次 `1/2/3`
- `Steps`: 识别逾期；生成催款单；发送催款函；标记坏账；坏账后登记回款
- `Expected Results`: Dunning 为快照；账龄正确；坏账标记正确；坏账后仍可收款；恢复策略按系统规则执行
- `Post-conditions`: 催款与坏账报表可见历史
- `Negative / Edge Variant`: 非逾期账单不得生成催款；坏账重复标记应被阻止
- `Regression Tag`: `dunning`, `bad-debt`
- `Automation Candidate`: 中
- `Notes / Assumptions`: 坏账恢复策略 A/B 需在 UAT 前确认

### P7 提成管理

#### TC-COM-001

- `Test Case ID`: `TC-COM-001`
- `Process Area`: 提成管理
- `Process Step`: 提成规则与生成
- `Title`: 服务费账单生成时自动产出提成记录并按多代理人分摊
- `Objective`: 验证 `BillItem(service) -> Commission`
- `Requirement Reference`: `FR-COM-01`, `FR-COM-02`, `FR-COM-03`, `7.4`, `7.5`
- `Priority`: 高
- `Preconditions`: 提成规则已配置；案件有多代理人分摊
- `Simulation Test Data`: `COMR-001`, `COMR-004`, `BILL-AR-001`, `USR-AG-01`, `USR-AG-02`
- `Steps`: 生成服务费账单；检查提成记录的 BaseFee、S1/S2、Agent 分配
- `Expected Results`: 规则匹配正确；多代理人拆分正确；非服务费不计入
- `Post-conditions`: 提成进入待结算池
- `Negative / Edge Variant`: 无匹配规则时应明确提示或不生成记录
- `Regression Tag`: `commission`
- `Automation Candidate`: 高
- `Notes / Assumptions`: BaseFee 模式需按规则字段验证

#### TC-COM-002

- `Test Case ID`: `TC-COM-002`
- `Process Area`: 提成管理
- `Process Step`: WaitPay / ForceSettle / 结算批次
- `Title`: 可结算识别与结算批次生成
- `Objective`: 验证 PaidRatio、WaitPay、ForceSettle 对可结算的影响
- `Requirement Reference`: `FR-COM-04`, `FR-COM-05`, `FR-COM-06`, `FR-COM-07`, `7.7`, `7.8`
- `Priority`: 高
- `Preconditions`: 已有提成记录和对应收款
- `Simulation Test Data`: `COMR-001`, `PAY-001`, `PAY-002`
- `Steps`: 分别构造未收款、部分收款、全额收款、ForceSettle 场景；生成结算批次；导出报表
- `Expected Results`: 只有满足条件的记录进入批次；导出报表数据与批次一致
- `Post-conditions`: 结算状态更新
- `Negative / Edge Variant`: 无权限用户不能生成批次；导出空集也应正常
- `Regression Tag`: `commission-settlement`
- `Automation Candidate`: 中
- `Notes / Assumptions`: 报表本体内容不做像素校验

### P8 顾问/检索项目

#### TC-CS-001

- `Test Case ID`: `TC-CS-001`
- `Process Area`: 顾问/检索项目
- `Process Step`: 项目立案到服务费草单
- `Title`: 顾问/检索项目从立案、内部任务、支出到服务费草单的主流程
- `Objective`: 验证项目案卷与普通案件共享主管道但具有独立 CaseType 语义
- `Requirement Reference`: `FR-CS-01`, `FR-CS-02`, `FR-CS-03`, `FR-CS-04`, `8.4`, `17.3` 至 `17.6`
- `Priority`: 高
- `Preconditions`: 主数据、费率、用户存在
- `Simulation Test Data`: `CASE-H-001`, `CASE-H-002`, `EXP-001`, `FD-CONSULT-001`
- `Steps`: 建立项目；创建内部任务；录入支出；生成顾问/检索服务费草单
- `Expected Results`: CaseType 正确；项目任务可管理；支出归集到项目；草单类型为 `CONSULT_FEE/SEARCH_FEE`
- `Post-conditions`: 可进入账单/收款/提成
- `Negative / Edge Variant`: 项目未立案不得录入支出或生成项目草单
- `Regression Tag`: `consulting-search`
- `Automation Candidate`: 中
- `Notes / Assumptions`: 内部任务是可选流程，但建议覆盖

#### TC-CS-002

- `Test Case ID`: `TC-CS-002`
- `Process Area`: 顾问/检索项目
- `Process Step`: 项目账单、收款与提成
- `Title`: 顾问/检索项目完整财务闭环
- `Objective`: 验证项目 `FeeDraft -> Bill -> Payment -> CaseReceipt -> Commission`
- `Requirement Reference`: `FR-CS-05`, `FR-CS-06`, `17.7`, `17.8`
- `Priority`: 高
- `Preconditions`: `TC-CS-001` 已完成
- `Simulation Test Data`: `BILL-AR-004`, `PAY-001`, `COMR-004`, `COMR-005`
- `Steps`: 从项目草单生成账单；登记收款；冲销；检查项目个案收款和提成
- `Expected Results`: 项目收入、实收、提成链路完整
- `Post-conditions`: 项目可用于报表与结算
- `Negative / Edge Variant`: 非项目 CaseType 不应套用顾问/检索规则
- `Regression Tag`: `consulting-finance`
- `Automation Candidate`: 中
- `Notes / Assumptions`: 顾问和检索可复用一套脚本参数化

### P9 查询、报表、导出、打印总览

#### TC-RPT-001

- `Test Case ID`: `TC-RPT-001`
- `Process Area`: 查询与报表
- `Process Step`: 全局高级查询与统计报表
- `Title`: 查询与报表跟随最新业务数据
- `Objective`: 验证设置、查询、报表总览对多模块数据的联动一致性
- `Requirement Reference`: `9.3`, `9.4`
- `Priority`: 高
- `Preconditions`: 上述主流程样本数据已全部建立
- `Simulation Test Data`: 全部 catalog 样本
- `Steps`: 执行高级案件查询、中间文件查询、费用情况查询、时限检索、案件/费用/年费/应收/提成报表
- `Expected Results`: 报表数值与明细来源一致；导出打印入口可用；空集场景正常
- `Post-conditions`: 无
- `Negative / Edge Variant`: 日期倒置、无权限、无结果、跨角色视图差异均应符合规则
- `Regression Tag`: `search`, `report`, `overview`
- `Automation Candidate`: 中
- `Notes / Assumptions`: 统计报表更适合接口断言 + 抽样 UI 验证

### P10 权限与角色影响

#### TC-SEC-001

- `Test Case ID`: `TC-SEC-001`
- `Process Area`: 权限与角色
- `Process Step`: 跨模块权限验证
- `Title`: 关键业务动作的角色隔离
- `Objective`: 验证 Agent、Finance、Formalities、Supervisor、Admin 的操作边界
- `Requirement Reference`: 各模块角色章节 `2.1`, `3.1.2`, `4.1.2`, `5.1.2`, `6.1.2`, `7.1.2`, `9.1.2`
- `Priority`: 高
- `Preconditions`: 多角色账号可用
- `Simulation Test Data`: `USR-ADM-01`, `USR-FM-01`, `USR-AG-01`, `USR-SPV-01`, `USR-FIN-01`
- `Steps`: 分别尝试限制修改、删除任务、生成账单、登记收款、生成结算批次、查看监督任务
- `Expected Results`: 只有授权角色能看到入口并执行成功；无权限动作返回拒绝
- `Post-conditions`: 无
- `Negative / Edge Variant`: `BAD-PERM-FIN-AGENT` 应失败
- `Regression Tag`: `permission`, `role-matrix`
- `Automation Candidate`: 高
- `Notes / Assumptions`: 建议配合角色矩阵单独维护

## E. Coverage Matrix

- `FR-CM-01/02/03/06/07 -> TC-CM-001, TC-CM-002, TC-CM-003`
  - 标签：`Happy Path`, `Negative`, `Permission`, `Follow-up linkage`
- `FR-WD-02/04/05/07/09/10 -> TC-WD-001, TC-WD-002, TC-WD-003`
  - 标签：`Happy Path`, `Negative`, `Report/Export/Print`, `Follow-up linkage`
- `FR-DL-01~10 -> TC-DL-001, TC-DL-002, TC-DL-003, TC-DL-004`
  - 标签：`Happy Path`, `Edge`, `Negative`, `Permission`, `Report/Export/Print`
- `FR-FE-01~09 -> TC-FE-001, TC-FE-002, TC-FE-003, TC-FE-004`
  - 标签：`Happy Path`, `Edge`, `Negative`, `Report/Export/Print`, `Follow-up linkage`
- `FR-BL-02~09 -> TC-BL-001, TC-BL-002, TC-BL-003, TC-BL-004, TC-BL-005`
  - 标签：`Happy Path`, `Edge`, `Negative`, `Report/Export/Print`, `Follow-up linkage`
- `FR-COM-01~07 -> TC-COM-001, TC-COM-002`
  - 标签：`Happy Path`, `Negative`, `Permission`, `Report/Export/Print`, `Follow-up linkage`
- `FR-CS-01~06 -> TC-CS-001, TC-CS-002`
  - 标签：`Happy Path`, `Edge`, `Negative`, `Follow-up linkage`
- `Search/Reports in 9.3/9.4 -> TC-RPT-001`
  - 标签：`Happy Path`, `Edge`, `Negative`, `Report/Export/Print`
- `Role coverage across modules -> TC-SEC-001`
  - 标签：`Permission`, `Negative`

## F. Residual Risks / Clarifications

### Needs Clarification

- 统计报表中多币种汇总是否统一折算为本位币，`SPEC` 未完全固化公式。
- 坏账后回款是否必须自动取消坏账标记，`SPEC` 给出了策略 A/B。
- 部分“警告还是强校验”的场景需要在测试执行前固定，例如缺地址、缺某些扩展字段。

### Assumption

- 文档模板/信头/交接单/催款函/信封打印只验证业务触发与数据带出，不验证文档排版像素级正确性。
- 导出/打印测试默认关注：
  - 功能可触发
  - 数据集正确
  - 空集与权限场景正确
- 不额外验证第三方官方系统实际导入成功。

### Residual Risks

- E2E 场景之间复用同一批数据时，容易出现状态污染，建议用“场景隔离数据集”执行。
- 提成、预收、坏账、年费滚动属于最容易出现回归的高风险区域，建议设为每轮版本必跑集。
- 若后续做自动化，建议拆为三层：
  - `smoke`: `TC-CM-001`, `TC-WD-001`, `TC-BL-002`, `TC-FE-003`, `TC-COM-001`
  - `regression`: 全部主流程 + 关键负向
  - `reporting`: 查询/导出/报表/权限矩阵
