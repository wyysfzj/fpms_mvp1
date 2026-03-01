# FPMS Code Review Report (SPEC 2.0) — Delta Update

- 审查基线：`docs/FPMS SPEC 2.0.md`（US/FR 全量 103 项）
- 本次审查日期：2026-03-01
- Delta 说明：本报告在上一版（2026-02-27）基础上直接更新，重新对照最新代码与测试结果。
- 审查约束：按你的要求，`document generation` 相关需求标记为 `Not Applicable`。

## 1. Executive Summary

- 总体符合度（加权）：**59.1%**（Fully=1，Partially=0.5，Missing=0，Not Applicable 不计入分母）
- 状态分布：`Fully Implemented=30`，`Partially Implemented=57`，`Missing=12`，`Not Applicable=4`
- 与上一版 Delta：符合度 **36.5% → 59.1%**，主要提升来自 `Annuity / Collections / Commission / Consulting / Expenses` 纵向模块落地。
- 关键结论：
  - 之前的 Critical（“全域模块在运行时架构缺失”）已明显收敛，相关域已接入路由并有 E2E 测试。
  - 仍存在 1 个发布阻断级安全问题：**管理员用户建档与引导仍使用 SHA-256，认证验证使用 bcrypt**，存在哈希策略不一致风险。
  - 若发布目标是“**SPEC 2.0 全量（除 document generation 外）**”，当前仍 **不建议直接上线**；若目标是“MVP1 增强版分阶段上线”，可在修复 P0 安全项后灰度。
- 维度审查结论（全量覆盖）：
  - 功能完整性与规格符合度：**59.1%**，核心链路可用，12 项仍缺失。
  - 架构一致性/模块划分/API 契约：模块化已形成，但部分域（Batch Filing、Consulting 内部任务）未闭环。
  - 代码质量（Clean Code/SOLID/可维护性）：整体中上；少量弱类型输入与错误契约不一致仍需收敛。
  - 安全性（认证授权/输入校验/OWASP）：RBAC 与鉴权主链路可用，但哈希策略不一致为 P0 风险。
  - 性能与可扩展性：未见明显 N+1 热点；模糊检索与前端主包体积存在扩展风险。
  - 错误处理与系统韧性：多数域已使用统一错误封装，但 admin 等端点仍混用 `HTTPException`。
  - 测试覆盖率与质量：后端回归通过（149 passed），但覆盖率百分比无法验证，前端自动化测试缺失。
  - 前端专项（响应式/a11y/组件复用/状态管理）：路由与模块覆盖已扩展，状态管理统一；自动化回归与包体积优化待补。
  - 后端专项（API/Schema/事务/索引/日志/配置）：核心事务链路存在并可工作；配置安全基线与部分 API 语义仍需强化。
  - 技术债与规范符合度：较上一版显著下降，但仍有 P0/P1 项需在上线前完成。

## 2. Functional Compliance Matrix

| User Story | Status | Evidence | Comments |
|---|---|---|---|
| US-CM-01 新案建立 | Partially Implemented | `backend/app/modules/cases/api.py`, `backend/app/modules/cases/service.py`, `backend/tests/test_case_fields.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| US-CM-02 扩展信息维护 | Partially Implemented | `backend/app/modules/cases/api.py`, `backend/app/modules/cases/service.py`, `backend/tests/test_case_fields.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| US-CM-03 参与方管理 | Partially Implemented | `backend/app/modules/cases/api.py`, `backend/app/modules/cases/service.py`, `backend/tests/test_case_fields.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| US-CM-04 案件信息补充（限制修改） | Fully Implemented | `backend/app/modules/cases/api.py`, `backend/app/modules/cases/service.py`, `backend/tests/test_case_fields.py` | 核心流程与数据结构已实现，并有后端测试证据。 |
| US-CM-05 案件递交批处理 | Missing | `backend/app/modules/cases/api.py`, `backend/app/modules/cases/service.py`, `backend/tests/test_case_fields.py` | 未发现批量递交接口/页面；仅有单案创建与更新流程。 |
| FR-CM-01 系统必须支持根据案件类型、专利类别、申请方向创建新案，案卷号在全系统唯一。 | Fully Implemented | `backend/app/modules/cases/api.py`, `backend/app/modules/cases/service.py`, `backend/tests/test_case_fields.py` | 核心流程与数据结构已实现，并有后端测试证据。 |
| FR-CM-02 保存时必须校验必填字段及组合规则（案卷号唯一、法律状态与申请号/申请日对应、优先权完整性等）。 | Partially Implemented | `backend/app/modules/cases/api.py`, `backend/app/modules/cases/service.py`, `backend/tests/test_case_fields.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| FR-CM-03 系统必须支持从主数据中选择客户、申请人、外方代理，并允许从案卷界面跳转创建新记录后回填。 | Partially Implemented | `backend/app/modules/cases/api.py`, `backend/app/modules/cases/service.py`, `backend/tests/test_case_fields.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| FR-CM-04 系统必须维护完整的法律状态枚举，并支持由中间文件/流程自动更新。 | Partially Implemented | `backend/app/modules/cases/api.py`, `backend/app/modules/cases/service.py`, `backend/tests/test_case_fields.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| FR-CM-05 系统必须支持 A）0..n 条优先权记录，B）0..n 条菌种保藏记录，C）PCT 国际/国家阶段字段，D）无效案专属字段。 | Partially Implemented | `backend/app/modules/cases/api.py`, `backend/app/modules/cases/service.py`, `backend/tests/test_case_fields.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| FR-CM-06 系统必须提供“限制修改视图”，只允许编辑白名单字段，权限独立控制。 | Fully Implemented | `backend/app/modules/cases/api.py`, `backend/app/modules/cases/service.py`, `backend/tests/test_case_fields.py` | 核心流程与数据结构已实现，并有后端测试证据。 |
| FR-CM-07 系统必须提供“案件递交批处理”，依据筛选条件列出案件，并批量设置递交日期、提实审与法律状态。 | Missing | `backend/app/modules/cases/api.py`, `backend/app/modules/cases/service.py`, `backend/tests/test_case_fields.py` | 未实现 Batch Filing 的筛选-批改-提交链路。 |
| US-WD-01 来文登记 | Partially Implemented | `backend/app/modules/documents/api.py`, `backend/app/modules/documents/service.py`, `backend/tests/test_b2_reply_chain.py`, `backend/tests/test_b3_fee_linking.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| US-WD-02 发文登记与自动核销 | Partially Implemented | `backend/app/modules/documents/api.py`, `backend/app/modules/documents/service.py`, `backend/tests/test_b2_reply_chain.py`, `backend/tests/test_b3_fee_linking.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| US-WD-03 期限联动 | Partially Implemented | `backend/app/modules/documents/api.py`, `backend/app/modules/documents/service.py`, `backend/tests/test_b2_reply_chain.py`, `backend/tests/test_b3_fee_linking.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| US-WD-04 费用联动 | Partially Implemented | `backend/app/modules/documents/api.py`, `backend/app/modules/documents/service.py`, `backend/tests/test_b2_reply_chain.py`, `backend/tests/test_b3_fee_linking.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| US-WD-05 电子档案存档 | Fully Implemented | `backend/app/modules/documents/api.py`, `backend/app/modules/documents/service.py`, `backend/tests/test_b2_reply_chain.py`, `backend/tests/test_b3_fee_linking.py` | 核心流程与数据结构已实现，并有后端测试证据。 |
| US-WD-06 中间文件查询 & 清单输出 | Partially Implemented | `backend/app/modules/documents/api.py`, `backend/app/modules/documents/service.py`, `backend/tests/test_b2_reply_chain.py`, `backend/tests/test_b3_fee_linking.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| US-WD-07 邮寄信息登记与交接单 & 信封 | Missing | `backend/app/modules/documents/api.py`, `backend/app/modules/documents/service.py`, `backend/tests/test_b2_reply_chain.py`, `backend/tests/test_b3_fee_linking.py` | 缺少邮寄登记、交接单、信封相关业务对象与接口。 |
| FR-WD-01 系统必须支持四大类中间文件（官方来文、致函官方、客户来文、致函客户），以及可配置子类型（常用文件定义）。 | Partially Implemented | `backend/app/modules/documents/api.py`, `backend/app/modules/documents/service.py`, `backend/tests/test_b2_reply_chain.py`, `backend/tests/test_b3_fee_linking.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| FR-WD-02 系统必须提供“中间文件录入向导”，支持对 1..N 个案件批量登记中间文件。 | Missing | `backend/app/modules/documents/api.py`, `backend/app/modules/documents/service.py`, `backend/tests/test_b2_reply_chain.py`, `backend/tests/test_b3_fee_linking.py` | 缺少 Step1-Step5 向导式批量登记 API。 |
| FR-WD-03 系统必须根据常用文件定义自动填充缺省字段（是否需通知代理人、是否需回复、时限模板、费用草单类型、案件状态变更等）。 | Partially Implemented | `backend/app/modules/documents/api.py`, `backend/app/modules/documents/service.py`, `backend/tests/test_b2_reply_chain.py`, `backend/tests/test_b3_fee_linking.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| FR-WD-04 对“需要回复”的中间文件，系统必须自动计算回复绝限、内部限和提醒日期，并建立对应的时限任务记录。 | Partially Implemented | `backend/app/modules/documents/api.py`, `backend/app/modules/documents/service.py`, `backend/tests/test_b2_reply_chain.py`, `backend/tests/test_b3_fee_linking.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| FR-WD-05 对定义了费用草单类型/费用项目的中间文件，系统必须自动生成关联费用草单，并可手工补充。 | Fully Implemented | `backend/app/modules/documents/api.py`, `backend/app/modules/documents/service.py`, `backend/tests/test_b2_reply_chain.py`, `backend/tests/test_b3_fee_linking.py` | 核心流程与数据结构已实现，并有后端测试证据。 |
| FR-WD-06 系统必须支持为每个中间文件存档 0..N 个电子附件，并支持查看/导出。 | Fully Implemented | `backend/app/modules/documents/api.py`, `backend/app/modules/documents/service.py`, `backend/tests/test_b2_reply_chain.py`, `backend/tests/test_b3_fee_linking.py` | 核心流程与数据结构已实现，并有后端测试证据。 |
| FR-WD-07 系统必须支持按多种条件查询中间文件，并输出不同格式的中间文件清单/证书清单。 | Partially Implemented | `backend/app/modules/documents/api.py`, `backend/app/modules/documents/service.py`, `backend/tests/test_b2_reply_chain.py`, `backend/tests/test_b3_fee_linking.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| FR-WD-08 系统必须支持“邮寄信息登记”，对一批中间文件统一输入挂号号，支持“一号复制给全部”或逐条录入。 | Missing | `backend/app/modules/documents/api.py`, `backend/app/modules/documents/service.py`, `backend/tests/test_b2_reply_chain.py`, `backend/tests/test_b3_fee_linking.py` | 未提供批量挂号号登记接口。 |
| FR-WD-09 系统必须支持为指定客户+邮寄日期生成“文件交接单”，并支持打印或基于模板生成 Word 版本。 | Missing | `backend/app/modules/documents/api.py`, `backend/app/modules/documents/service.py`, `backend/tests/test_b2_reply_chain.py`, `backend/tests/test_b3_fee_linking.py` | 未实现交接单实体与业务流程（打印/模板输出亦缺）。 |
| FR-WD-10 系统必须支持信封打印，按“客户地址/申请人联系人/申请人地址”的优先级自动选择收件人信息，并打印信封版式。 | Not Applicable | `backend/app/modules/documents/api.py`, `backend/app/modules/documents/service.py`, `backend/tests/test_b2_reply_chain.py`, `backend/tests/test_b3_fee_linking.py` | 文档生成范围（信封打印）按本次审查约束排除。 |
| US-DL-01 时限模板配置 | Partially Implemented | `backend/app/modules/tasks/api.py`, `backend/app/modules/tasks/task_generation_service.py`, `backend/tests/test_task_template.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| US-DL-02 自动创建时限任务 | Partially Implemented | `backend/app/modules/tasks/api.py`, `backend/app/modules/tasks/task_generation_service.py`, `backend/tests/test_task_template.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| US-DL-03 日常提醒 – 作业人视角 | Partially Implemented | `backend/app/modules/tasks/api.py`, `backend/app/modules/tasks/task_generation_service.py`, `backend/tests/test_task_template.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| US-DL-04 日常提醒 – 监督人视角 | Partially Implemented | `backend/app/modules/tasks/api.py`, `backend/app/modules/tasks/task_generation_service.py`, `backend/tests/test_task_template.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| US-DL-05 手工维护时限任务 | Partially Implemented | `backend/app/modules/tasks/api.py`, `backend/app/modules/tasks/task_generation_service.py`, `backend/tests/test_task_template.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| US-DL-06 专项检索：申请费 / 实审请求时限 | Missing | `backend/app/modules/tasks/api.py`, `backend/app/modules/tasks/task_generation_service.py`, `backend/tests/test_task_template.py` | 无“申请费时限/实审时限”专项检索接口。 |
| US-DL-07 登录提醒与清单打印 | Partially Implemented | `backend/app/modules/tasks/api.py`, `backend/app/modules/tasks/task_generation_service.py`, `backend/tests/test_task_template.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| FR-DL-01 系统必须支持维护时限模板（起算基准、年/月/日增量、提醒规则、默认监督人/责任人）。 | Partially Implemented | `backend/app/modules/tasks/api.py`, `backend/app/modules/tasks/task_generation_service.py`, `backend/tests/test_task_template.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| FR-DL-02 系统必须能根据时限模板，从案件事件/中间文件/年费任务中自动创建时限任务。 | Partially Implemented | `backend/app/modules/tasks/api.py`, `backend/app/modules/tasks/task_generation_service.py`, `backend/tests/test_task_template.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| FR-DL-03 每个时限任务必须区分“作业人”和“监督人”，并在不同视图中以不同角色展示。 | Fully Implemented | `backend/app/modules/tasks/api.py`, `backend/app/modules/tasks/task_generation_service.py`, `backend/tests/test_task_template.py` | 核心流程与数据结构已实现，并有后端测试证据。 |
| FR-DL-04 系统必须为作业人提供“我的时限任务”视图，按内部时限/官方绝限排序，支持核销/取消核销。 | Partially Implemented | `backend/app/modules/tasks/api.py`, `backend/app/modules/tasks/task_generation_service.py`, `backend/tests/test_task_template.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| FR-DL-05 系统必须为监督人提供“监督时限”视图，按作业人/类型/状态/逾期情况过滤任务。 | Partially Implemented | `backend/app/modules/tasks/api.py`, `backend/app/modules/tasks/task_generation_service.py`, `backend/tests/test_task_template.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| FR-DL-06 系统必须支持手工新增/编辑/删除时限任务（受角色/权限控制）。 | Partially Implemented | `backend/app/modules/tasks/api.py`, `backend/app/modules/tasks/task_generation_service.py`, `backend/tests/test_task_template.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| FR-DL-07 系统必须提供“申请费时限检索”和“实审时限检索”，用于批量查找尚未缴费/尚未提实审案件。 | Missing | `backend/app/modules/tasks/api.py`, `backend/app/modules/tasks/task_generation_service.py`, `backend/tests/test_task_template.py` | 未实现两类专项检索（申请费、实审）。 |
| FR-DL-08 登录或进入首页时，系统必须自动查询并展示当前用户相关的“今日提醒清单”。 | Partially Implemented | `backend/app/modules/tasks/api.py`, `backend/app/modules/tasks/task_generation_service.py`, `backend/tests/test_task_template.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| FR-DL-09 系统必须允许将任意时限列表导出/打印为期限清单。 | Not Applicable | `backend/app/modules/tasks/api.py`, `backend/app/modules/tasks/task_generation_service.py`, `backend/tests/test_task_template.py` | 导出/打印类需求属于 document generation 相关，本次排除。 |
| FR-DL-10 系统必须记录时限任务的关键操作日志（创建、修改、责任人变更、核销、取消核销、取消任务）以便审计。 | Fully Implemented | `backend/app/modules/tasks/api.py`, `backend/app/modules/tasks/task_generation_service.py`, `backend/tests/test_task_template.py` | 核心流程与数据结构已实现，并有后端测试证据。 |
| US-FE-01 费用草单生成与维护 | Fully Implemented | `backend/app/modules/fees/api.py`, `backend/app/modules/annuity/api.py`, `backend/app/modules/expenses/api.py`, `backend/tests/test_annuity_e2e.py` | 核心流程与数据结构已实现，并有后端测试证据。 |
| US-FE-02 标准费率与费减/折扣计算 | Partially Implemented | `backend/app/modules/fees/api.py`, `backend/app/modules/annuity/api.py`, `backend/app/modules/expenses/api.py`, `backend/tests/test_annuity_e2e.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| US-FE-03 官费清单与缴费 | Partially Implemented | `backend/app/modules/fees/api.py`, `backend/app/modules/annuity/api.py`, `backend/app/modules/expenses/api.py`, `backend/tests/test_annuity_e2e.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| US-FE-04 授权费 / 年登印费管理 | Partially Implemented | `backend/app/modules/fees/api.py`, `backend/app/modules/annuity/api.py`, `backend/app/modules/expenses/api.py`, `backend/tests/test_annuity_e2e.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| US-FE-05 年费管理（多年度） | Partially Implemented | `backend/app/modules/fees/api.py`, `backend/app/modules/annuity/api.py`, `backend/app/modules/expenses/api.py`, `backend/tests/test_annuity_e2e.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| US-FE-06 个案收款登记 | Partially Implemented | `backend/app/modules/fees/api.py`, `backend/app/modules/annuity/api.py`, `backend/app/modules/expenses/api.py`, `backend/tests/test_annuity_e2e.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| US-FE-07 支出费用管理 | Fully Implemented | `backend/app/modules/fees/api.py`, `backend/app/modules/annuity/api.py`, `backend/app/modules/expenses/api.py`, `backend/tests/test_annuity_e2e.py` | 核心流程与数据结构已实现，并有后端测试证据。 |
| US-FE-08 费用情况综合查询 | Partially Implemented | `backend/app/modules/fees/api.py`, `backend/app/modules/annuity/api.py`, `backend/app/modules/expenses/api.py`, `backend/tests/test_annuity_e2e.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| FR-FE-01 系统必须支持维护标准费率表 T_FeeRate，按费用类型/国别/专利类别/案件类型区分官费、服务费、杂费及默认金额与币种。 | Fully Implemented | `backend/app/modules/fees/api.py`, `backend/app/modules/annuity/api.py`, `backend/app/modules/expenses/api.py`, `backend/tests/test_annuity_e2e.py` | 核心流程与数据结构已实现，并有后端测试证据。 |
| FR-FE-02 系统必须支持按“案件+草单类型”创建费用草单 T_FeeDraft，并包含 1..N 条费用明细 T_FeeItem。 | Fully Implemented | `backend/app/modules/fees/api.py`, `backend/app/modules/annuity/api.py`, `backend/app/modules/expenses/api.py`, `backend/tests/test_annuity_e2e.py` | 核心流程与数据结构已实现，并有后端测试证据。 |
| FR-FE-03 系统必须根据标准费率表 + 案件参数 + 费减比例/折扣率，自动计算费用明细金额，可被用户手工覆盖。 | Partially Implemented | `backend/app/modules/fees/api.py`, `backend/app/modules/annuity/api.py`, `backend/app/modules/expenses/api.py`, `backend/tests/test_annuity_e2e.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| FR-FE-04 系统必须支持基于费用草单构造“官费清单 T_PayList + 官费缴费明细 T_GovPayment”，并支持导出、缴费登记以及状态追踪。 | Partially Implemented | `backend/app/modules/fees/api.py`, `backend/app/modules/annuity/api.py`, `backend/app/modules/expenses/api.py`, `backend/tests/test_annuity_e2e.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| FR-FE-05 系统必须支持年登印费管理：从授权案件中提取登记费任务，记录客户指示与通知状态，并自动生成相关草单与通知函。 | Partially Implemented | `backend/app/modules/fees/api.py`, `backend/app/modules/annuity/api.py`, `backend/app/modules/expenses/api.py`, `backend/tests/test_annuity_e2e.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| FR-FE-06 系统必须支持年费管理：按到期区间提取年费任务，记录客户指示/通知状态，并自动生成年费草单与通知函。 | Partially Implemented | `backend/app/modules/fees/api.py`, `backend/app/modules/annuity/api.py`, `backend/app/modules/expenses/api.py`, `backend/tests/test_annuity_e2e.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| FR-FE-07 系统必须支持个案收款登记 T_CaseReceipt，记录应收/实收、欠款标记、可提成标记和发票信息。 | Partially Implemented | `backend/app/modules/fees/api.py`, `backend/app/modules/annuity/api.py`, `backend/app/modules/expenses/api.py`, `backend/tests/test_annuity_e2e.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| FR-FE-08 系统必须支持第三方支出记录 T_Expense，并可按案件、项目、时间查询与统计。 | Fully Implemented | `backend/app/modules/fees/api.py`, `backend/app/modules/annuity/api.py`, `backend/app/modules/expenses/api.py`, `backend/tests/test_annuity_e2e.py` | 核心流程与数据结构已实现，并有后端测试证据。 |
| FR-FE-09 系统必须提供“费用情况查询”，将官方缴费记录与个案收款记录以两张一览表方式展示。 | Partially Implemented | `backend/app/modules/fees/api.py`, `backend/app/modules/annuity/api.py`, `backend/app/modules/expenses/api.py`, `backend/tests/test_annuity_e2e.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| US-BL-01 从费用草单生成账单 | Fully Implemented | `backend/app/modules/billing/api.py`, `backend/app/modules/collections/api.py`, `backend/tests/test_b5_billing_polish.py`, `backend/tests/test_collections_e2e.py` | 核心流程与数据结构已实现，并有后端测试证据。 |
| US-BL-02 手工维护账单 | Partially Implemented | `backend/app/modules/billing/api.py`, `backend/app/modules/collections/api.py`, `backend/tests/test_b5_billing_polish.py`, `backend/tests/test_collections_e2e.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| US-BL-03 账单打印与模板输出 | Not Applicable | `backend/app/modules/billing/api.py`, `backend/app/modules/collections/api.py`, `backend/tests/test_b5_billing_polish.py`, `backend/tests/test_collections_e2e.py` | 账单打印/模板输出属于 document generation 相关，本次排除。 |
| US-BL-04 收款登记与账单冲销 | Fully Implemented | `backend/app/modules/billing/api.py`, `backend/app/modules/collections/api.py`, `backend/tests/test_b5_billing_polish.py`, `backend/tests/test_collections_e2e.py` | 核心流程与数据结构已实现，并有后端测试证据。 |
| US-BL-05 冲销反转（反冲销） | Fully Implemented | `backend/app/modules/billing/api.py`, `backend/app/modules/collections/api.py`, `backend/tests/test_b5_billing_polish.py`, `backend/tests/test_collections_e2e.py` | 核心流程与数据结构已实现，并有后端测试证据。 |
| US-BL-06 坏账与催款管理 | Partially Implemented | `backend/app/modules/billing/api.py`, `backend/app/modules/collections/api.py`, `backend/tests/test_b5_billing_polish.py`, `backend/tests/test_collections_e2e.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| US-BL-07 预收款管理 | Partially Implemented | `backend/app/modules/billing/api.py`, `backend/app/modules/collections/api.py`, `backend/tests/test_b5_billing_polish.py`, `backend/tests/test_collections_e2e.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| FR-BL-01 系统必须支持维护账单头 T_Bill 与账单明细 T_BillItem，包括收付方向（应收/应付）、账单状态（尚未冲销/部分冲销/已经冲销/坏账）、折扣率、坏账信息等。 | Partially Implemented | `backend/app/modules/billing/api.py`, `backend/app/modules/collections/api.py`, `backend/tests/test_b5_billing_polish.py`, `backend/tests/test_collections_e2e.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| FR-BL-02 系统必须支持从费用草单 T_FeeDraft/T_FeeItem 自动生成账单（应收为主），并绑定账单明细与原草单/费用明细。 | Fully Implemented | `backend/app/modules/billing/api.py`, `backend/app/modules/collections/api.py`, `backend/tests/test_b5_billing_polish.py`, `backend/tests/test_collections_e2e.py` | 核心流程与数据结构已实现，并有后端测试证据。 |
| FR-BL-03 系统必须支持纯手工创建账单，允许直接录入明细行（不依赖草单），同时支持 AR（应收）与 AP（应付）方向。 | Partially Implemented | `backend/app/modules/billing/api.py`, `backend/app/modules/collections/api.py`, `backend/tests/test_b5_billing_polish.py`, `backend/tests/test_collections_e2e.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| FR-BL-04 系统必须支持基于模板系统打印/导出账单文档（中/英、不同版式）。 | Not Applicable | `backend/app/modules/billing/api.py`, `backend/app/modules/collections/api.py`, `backend/tests/test_b5_billing_polish.py`, `backend/tests/test_collections_e2e.py` | 模板打印/导出属于 document generation 相关，本次排除。 |
| FR-BL-05 系统必须支持记录收款 T_Payment，并通过 T_Offset 将收款分配到一个或多个账单上，自动更新账单余额与状态。 | Fully Implemented | `backend/app/modules/billing/api.py`, `backend/app/modules/collections/api.py`, `backend/tests/test_b5_billing_polish.py`, `backend/tests/test_collections_e2e.py` | 核心流程与数据结构已实现，并有后端测试证据。 |
| FR-BL-06 系统必须支持对冲销记录进行反冲销（在时间/权限控制下），恢复账单余额与收款余额。 | Fully Implemented | `backend/app/modules/billing/api.py`, `backend/app/modules/collections/api.py`, `backend/tests/test_b5_billing_polish.py`, `backend/tests/test_collections_e2e.py` | 核心流程与数据结构已实现，并有后端测试证据。 |
| FR-BL-07 系统必须支持将账单标记为坏账/从坏账恢复，并在催款与普通统计中区别显示。 | Partially Implemented | `backend/app/modules/billing/api.py`, `backend/app/modules/collections/api.py`, `backend/tests/test_b5_billing_polish.py`, `backend/tests/test_collections_e2e.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| FR-BL-08 系统必须支持生成催款单 T_Dunning/T_DunningLine，按客户+截止日期列出未结账单，并可基于模板生成催款函。 | Partially Implemented | `backend/app/modules/billing/api.py`, `backend/app/modules/collections/api.py`, `backend/tests/test_b5_billing_polish.py`, `backend/tests/test_collections_e2e.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| FR-BL-09 系统必须支持预收款管理：允许登记预收收款行，在未分配到账单时保持“预收状态”，并在后续冲销账单时从预收款中扣减。 | Partially Implemented | `backend/app/modules/billing/api.py`, `backend/app/modules/collections/api.py`, `backend/tests/test_b5_billing_polish.py`, `backend/tests/test_collections_e2e.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| US-COM-01 提成规则配置 | Fully Implemented | `backend/app/modules/commission/api.py`, `backend/app/modules/commission/service.py`, `backend/tests/test_commission_e2e.py` | 核心流程与数据结构已实现，并有后端测试证据。 |
| US-COM-02 提成记录自动生成 | Partially Implemented | `backend/app/modules/commission/api.py`, `backend/app/modules/commission/service.py`, `backend/tests/test_commission_e2e.py` | 已在账单生成后挂接自动提成，但能力仍偏单路径。 |
| US-COM-03 多代理人分摊 | Missing | `backend/app/modules/commission/api.py`, `backend/app/modules/commission/service.py`, `backend/tests/test_commission_e2e.py` | 提成生成当前按主办代理人单人路径，未实现多代理人分摊。 |
| US-COM-04 款到后才能结算 | Fully Implemented | `backend/app/modules/commission/api.py`, `backend/app/modules/commission/service.py`, `backend/tests/test_commission_e2e.py` | 核心流程与数据结构已实现，并有后端测试证据。 |
| US-COM-05 强制可结算（特殊标记） | Fully Implemented | `backend/app/modules/commission/api.py`, `backend/app/modules/commission/service.py`, `backend/tests/test_commission_e2e.py` | 核心流程与数据结构已实现，并有后端测试证据。 |
| US-COM-06 提成结算批次与报表 | Partially Implemented | `backend/app/modules/commission/api.py`, `backend/app/modules/commission/service.py`, `backend/tests/test_commission_e2e.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| FR-COM-01 系统必须支持维护提成规则 T_CommissionRule，包括一次/二次提成比例、基数计算方式和适用范围。 | Fully Implemented | `backend/app/modules/commission/api.py`, `backend/app/modules/commission/service.py`, `backend/tests/test_commission_e2e.py` | 核心流程与数据结构已实现，并有后端测试证据。 |
| FR-COM-02 系统必须支持在服务费账单生成时，根据提成规则自动为相关案件和代理人生成或更新提成记录 T_Commission。 | Partially Implemented | `backend/app/modules/commission/api.py`, `backend/app/modules/commission/service.py`, `backend/tests/test_commission_e2e.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| FR-COM-03 系统必须支持多代理人（主办/协办/团队成员）按比例分摊提成基数，并分别记录各自提成金额。 | Missing | `backend/app/modules/commission/api.py`, `backend/app/modules/commission/service.py`, `backend/tests/test_commission_e2e.py` | 未实现主办/协办/团队成员按比例分摊。 |
| FR-COM-04 系统必须支持 WaitPay（款到后才能结算）逻辑，即在相关账单收款比例未达条件时，将提成记录标记为“不可结算”。 | Fully Implemented | `backend/app/modules/commission/api.py`, `backend/app/modules/commission/service.py`, `backend/tests/test_commission_e2e.py` | 核心流程与数据结构已实现，并有后端测试证据。 |
| FR-COM-05 系统必须支持 ForceSettle（案件可结算酬金）逻辑，以允许对特殊案件提前结算提成。 | Fully Implemented | `backend/app/modules/commission/api.py`, `backend/app/modules/commission/service.py`, `backend/tests/test_commission_e2e.py` | 核心流程与数据结构已实现，并有后端测试证据。 |
| FR-COM-06 系统必须支持提成结算批次 T_CommissionSettlement 的创建，与结算明细 T_CommissionSettleLine 的生成，并标记对应的提成记录（S1_Done/S2_Done）。 | Partially Implemented | `backend/app/modules/commission/api.py`, `backend/app/modules/commission/service.py`, `backend/tests/test_commission_e2e.py` | 已支持结算批次与行生成，但未完整覆盖 S1/S2 结算完成标记规则。 |
| FR-COM-07 系统必须提供提成结算报表，按代理人/案件/时间区间统计提成金额，并支持导出。 | Partially Implemented | `backend/app/modules/commission/api.py`, `backend/app/modules/commission/service.py`, `backend/tests/test_commission_e2e.py` | 已提供报表查询接口，导出能力未见实现。 |
| US-CS-01 顾问/检索项目立案 | Partially Implemented | `backend/app/modules/consulting/api.py`, `backend/app/modules/consulting/service.py`, `backend/tests/test_consulting_e2e.py` | 已可创建 CONSULTING/SEARCH 案件，但项目专属字段不足。 |
| US-CS-02 内部任务管理（可选） | Missing | `backend/app/modules/consulting/api.py`, `backend/app/modules/consulting/service.py`, `backend/tests/test_consulting_e2e.py` | 未发现顾问/检索内部任务（非官方时限）专用接口。 |
| US-CS-03 支出费用记录 | Fully Implemented | `backend/app/modules/consulting/api.py`, `backend/app/modules/consulting/service.py`, `backend/tests/test_consulting_e2e.py` | 核心流程与数据结构已实现，并有后端测试证据。 |
| US-CS-04 服务费草单生成 | Fully Implemented | `backend/app/modules/consulting/api.py`, `backend/app/modules/consulting/service.py`, `backend/tests/test_consulting_e2e.py` | 核心流程与数据结构已实现，并有后端测试证据。 |
| US-CS-05 账单、收款与提成 | Partially Implemented | `backend/app/modules/consulting/api.py`, `backend/app/modules/consulting/service.py`, `backend/tests/test_consulting_e2e.py` | 主链路可用，但与 SPEC 细节仍有差距。 |
| FR-CS-01 系统必须支持以 CaseType=CONSULTING/SEARCH 的方式为顾问/检索项目建立案卷记录，并记录项目专属属性（范围、负责人、预计工时等）。 | Partially Implemented | `backend/app/modules/consulting/api.py`, `backend/app/modules/consulting/service.py`, `backend/tests/test_consulting_e2e.py` | 缺少范围、预计工时等项目属性。 |
| FR-CS-02 系统必须允许在顾问/检索案卷上创建内部任务 T_Task（非官方时限任务），用于项目执行管理。 | Missing | `backend/app/modules/consulting/api.py`, `backend/app/modules/consulting/service.py`, `backend/tests/test_consulting_e2e.py` | 缺少顾问/检索项目内部任务域模型与 API。 |
| FR-CS-03 系统必须支持记录顾问/检索项目的支出费用 T_Expense，按案件/类别/时间进行查询和统计。 | Fully Implemented | `backend/app/modules/consulting/api.py`, `backend/app/modules/consulting/service.py`, `backend/tests/test_consulting_e2e.py` | 核心流程与数据结构已实现，并有后端测试证据。 |
| FR-CS-04 系统必须支持为顾问/检索项目生成服务费草单 T_FeeDraft/T_FeeItem，支持固定报价、按工时计费或混合模式。 | Fully Implemented | `backend/app/modules/consulting/api.py`, `backend/app/modules/consulting/service.py`, `backend/tests/test_consulting_e2e.py` | 核心流程与数据结构已实现，并有后端测试证据。 |
| FR-CS-05 系统必须支持从顾问/检索草单生成账单 T_Bill/T_BillItem，并使用收款/冲销机制处理相关款项。 | Fully Implemented | `backend/app/modules/consulting/api.py`, `backend/app/modules/consulting/service.py`, `backend/tests/test_consulting_e2e.py` | 核心流程与数据结构已实现，并有后端测试证据。 |
| FR-CS-06 系统必须支持按照 T_CommissionRule 的 CONSULTING/SEARCH 规则为顾问/检索项目生成提成记录 T_Commission，并纳入结算批次。 | Partially Implemented | `backend/app/modules/consulting/api.py`, `backend/app/modules/consulting/service.py`, `backend/tests/test_consulting_e2e.py` | 主链路可用，但与 SPEC 细节仍有差距。 |

## 3. Detailed Findings

### Critical

1. 密码哈希策略不一致（发布阻断）
- 问题描述：管理员建用户与 bootstrap 管理员仍使用 `sha256`；登录验证使用 `bcrypt`。会导致安全基线不一致，且存在认证兼容风险。
- 证据：
  - `backend/app/modules/admin/api.py:78`（`hashlib.sha256(...)`）
  - `backend/app/modules/admin/api.py:183`（bootstrap 同样 `sha256`）
  - `backend/app/core/security.py:11-16`（`get_password_hash` / `verify_password` 为 bcrypt）
  - `backend/app/modules/auth/service.py:24`（登录使用 `verify_password`）
- 建议修复：统一所有写入路径到 `get_password_hash()`；为历史哈希提供迁移/兼容策略（一次性重哈希或版本化哈希前缀）。

### High

1. 案件递交批处理缺失（CM-05/FR-CM-07）
- 问题描述：缺少按筛选批量更新递交日期/实审状态/法律状态的专用链路。
- 证据：`backend/app/modules/cases/api.py` 仅有 list/create/update/limited-edit/export，无 batch filing endpoint。
- 建议修复：新增批处理 API（筛选、预校验、批量更新、结果回执）并补齐前端批处理页面。

2. 中间文件邮寄/交接单域缺失（WD-07/FR-WD-08/09）
- 问题描述：当前文档模块有模板、登记、附件，但无邮寄登记、交接单实体与流程。
- 证据：`backend/app/modules/documents/models.py` 仅 `Document/DocTemplate/DocAttachment`，无 `DocDispatch` 类；`backend/app/modules/documents/api.py` 无对应路由。
- 建议修复：补齐 `DocDispatch/DocDispatchLine` 及批量挂号号登记接口，前端增加登记与查询页面。

3. 时限专项检索与删除能力缺口（DL-06/FR-DL-06/07）
- 问题描述：缺少申请费/实审专项检索，且任务删除能力未实现。
- 证据：`backend/app/modules/tasks/api.py` 无专项检索路由、无 `DELETE /tasks/{id}`。
- 建议修复：新增专项查询 API + 删除接口（软删优先），并同步权限与审计日志策略。

4. 提成多代理人分摊未实现（US-COM-03/FR-COM-03）
- 问题描述：提成生成按单一主办代理人处理，未覆盖主办/协办/团队成员分摊。
- 证据：`backend/app/modules/commission/service.py:541` 仅取 `case.primary_agent_id`。
- 建议修复：引入案件-代理人分摊结构（比例校验=100%），提成生成按分摊拆分记录。

5. 顾问/检索内部任务域缺失（US-CS-02/FR-CS-02）
- 问题描述：顾问/检索只实现立案与服务费草单，未实现项目内部任务管理。
- 证据：`backend/app/modules/consulting/api.py` 仅 `/consulting/cases` 与 `/consulting/fee-drafts`。
- 建议修复：新增 consulting task 实体与 API（创建/分配/进度/完工），避免与官方时限任务混用。

6. 测试覆盖率质量门未达可判定状态（目标 ≥80%）
- 问题描述：后端测试通过，但覆盖率插件/工具缺失导致无法输出覆盖率百分比；前端无自动化测试脚本。
- 证据：
  - `backend`：`pytest -q` 149 passed；`python3 -m coverage --version` 报 `No module named coverage`
  - `frontend/package.json` 无 `test` 脚本
- 建议修复：纳入 `pytest-cov + coverage gate`，前端增加 Vitest + E2E（Playwright/Cypress）并接 CI 质量门。

### Medium

1. 附件类型白名单未启用
- 问题描述：上传只做大小限制，MIME/扩展名 allow-list 变量为 `None`。
- 证据：`backend/app/modules/documents/service.py:222-223`
- 建议修复：由系统参数驱动 allow-list，并增加文件头签名校验。

2. Case 搜索使用 `ilike`，与 SQLite PoC 约束不一致
- 问题描述：`ilike` 在跨方言可移植性上存在风险。
- 证据：`backend/app/modules/cases/api.py:67-70`、`:418-421`
- 建议修复：统一改为 `func.lower(...) LIKE ...` 策略并配合索引优化。

3. 管理端 API 合同不够强类型
- 问题描述：`payload: dict[str, Any]` + `HTTPException(detail=...)` 与统一错误信封不一致。
- 证据：`backend/app/modules/admin/api.py:48`, `:102`
- 建议修复：改为 Pydantic 入参模型 + `BusinessError` 统一错误契约。

4. 前端主包体积偏大
- 问题描述：构建产物主 chunk 超 500 kB 告警。
- 证据：`npm run build` 输出 `dist/assets/index-*.js ~1073.13 kB`。
- 建议修复：按业务域做路由级懒加载、手动分包与依赖拆分。

### Low

1. 依赖与框架弃用告警
- 问题描述：`passlib crypt` 弃用、Pydantic v2 兼容参数告警。
- 证据：`cd backend && pytest -q` 的 3 条 warning。
- 建议修复：升级 passlib 依赖链并修正 `Field(..., strip_whitespace=...)` 写法。

2. JWT 默认密钥仍为弱默认值
- 问题描述：默认 `dev-secret-change-me` 不应在非开发环境运行。
- 证据：`backend/app/core/config.py:13`
- 建议修复：在非 dev 环境启动时强制校验 secret 强度并 fail-fast。

3. 依赖漏洞扫描工具链未就绪
- 问题描述：`pip_audit` 未安装，`npm audit` 因网络不可达失败。
- 证据：
  - `python3 -m pip_audit -h` -> `No module named pip_audit`
  - `npm audit --json` -> `ENOTFOUND registry.npmjs.org`
- 建议修复：在 CI 提供联网镜像源 + 固定审计任务（Python/Node）。

## 4. Security & Performance Issues

### Security

- **P0**：密码哈希写入与验证策略不一致（sha256 vs bcrypt）。
- 附件上传缺少 MIME/扩展名/签名多重校验。
- Admin API 仍有弱类型 payload，错误契约不统一。
- 依赖漏洞扫描未形成持续化、可复现链路。

### Performance & Scalability

- 多处模糊查询与 `%like%` 搜索（如 cases/documents）在数据量增长后存在全表扫描风险。
- 前端主包体积偏大，首屏与弱网体验受影响。
- 暂未发现显著 N+1 热点（tasks/documents 列表存在批量回填 case/client 的优化实践）。

## 5. Test Coverage Summary

- 后端自动化测试：`cd backend && pytest -q` -> **149 passed**, 0 failed, 33.43s（3 warnings）。
- 前端质量门：`cd frontend && npm run lint && npm run typecheck && npm run build` -> 全部通过。
- 覆盖率数据：
  - 目标要求：`>=80%`
  - 现状：**无法给出可验证百分比**（环境未安装 `coverage/pytest-cov`）。
- 前端测试自动化：未发现单元/集成/E2E 测试脚本（`package.json` 无 `test`）。
- 关键未覆盖路径（高风险）：
  - Admin 用户创建/引导哈希与登录兼容链路
  - Case Batch Filing
  - Documents 邮寄登记/交接单
  - Deadline 专项检索与删除
  - Commission 多代理人分摊

## 6. Recommendations & Action Items

| Priority | Action Item | Estimated Effort | Owner Suggestion |
|---|---|---:|---|
| P0 | 统一密码哈希策略到 bcrypt，并做历史哈希迁移 | 1-2 天 | Backend |
| P0 | 建立覆盖率质量门（backend>=80%，frontend 测试接入） | 2-4 天 | QA + Backend + Frontend |
| P1 | 实现 Case Batch Filing（API + FE + 测试） | 3-5 天 | Backend + Frontend |
| P1 | 实现 Documents 邮寄登记/交接单全链路 | 4-6 天 | Backend + Frontend |
| P1 | 实现 Deadline 专项检索与任务删除（含审计） | 2-3 天 | Backend |
| P1 | 提成多代理人分摊模型与计算改造 | 4-7 天 | Architect + Backend |
| P2 | 顾问/检索内部任务域（与官方时限隔离） | 3-5 天 | Backend + Frontend |
| P2 | 附件白名单与文件签名校验 | 1-2 天 | Backend |
| P2 | 前端分包优化（减少首包） | 1-2 天 | Frontend |

## 7. Conclusion & Next Steps

- 结论：当前版本已从“结构性缺失”进展为“可运行的多域 MVP1 增强版”，但尚未达到“SPEC 2.0（除 document generation）全量完成”标准。
- 上线建议：
  - 若目标为 **全量 SPEC 2.0（排除文档生成）**：**暂不建议上线**。
  - 若目标为 **阶段性业务试运行**：在完成 `P0` 后可小流量灰度，并将 `P1` 作为上线后首个迭代关卡。
- 下一步执行顺序：`P0 安全/质量门` -> `P1 业务缺口补齐` -> `P2 体验与可维护性优化`。
