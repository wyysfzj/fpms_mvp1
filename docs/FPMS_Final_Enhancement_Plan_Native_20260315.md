# FPMS Final Enhancement Plan Native

日期: 2026-03-15

状态: Planning Only

输出方式说明:
- 当前执行采用单线程 gated handoff。
- `default / explorer / worker / monitor` 在本文中仅作为职责标签与输出分区标签使用。
- 本文是后续实施阶段的蓝本，不包含任何已执行的代码修改结果。

## 1. 目标与边界

### 1.1 总目标

基于现有代码与文档，对 FPMS 项目进行最终增强规划，目标是收敛 `docs/FPMS_Code_Review_Report_SPEC_2.0_20260227.md` 中 Functional Compliance Matrix 里全部 `Partially Implemented` 条目，使系统达到“SPEC 2.0 非 document generation 范围内可验收”的实施准备状态。

### 1.2 本文适用范围

- 仅覆盖 `Partially Implemented` 条目
- 必须参考 `docs/FPMS_Final_Enhancement_Plan_and_Task_Breakdown_SPEC_2.0_20260228.md`
- 完全排除 `document generation` 相关功能
- 当前文档仅作为计划与审计蓝本，不代表任何功能已经修复

### 1.3 明确排除项

以下内容不纳入本轮修复目标:
- `Fully Implemented`
- `Missing`
- `Not Applicable`
- 导出
- 打印
- 模板文档生成
- 通知函生成
- 任何其他 `document generation` 子能力

### 1.4 最小必要波及原则

仅当修复某个 `Partially Implemented` 条目时，确实必须调整共享类型、共享校验逻辑、共享测试夹具或共享基础设施，才允许最小必要波及。所有此类波及必须满足以下要求:
- 明确波及原因
- 明确波及边界
- 明确如何避免范围扩大
- 明确如何验证未引入额外功能性变更

## 2. 输入文档与证据基线

### 2.1 主证据文档

- `docs/FPMS_Code_Review_Report_SPEC_2.0_20260227.md`
- `docs/FPMS_Final_Enhancement_Plan_and_Task_Breakdown_SPEC_2.0_20260228.md`

### 2.2 审查结论基线

根据审查报告:
- `Fully Implemented = 30`
- `Partially Implemented = 57`
- `Missing = 12`
- `Not Applicable = 4`

本计划仅处理这 57 条 `Partially Implemented`。

## 3. 运行方式说明

### 3.1 Native 4-Role Workflow 映射

- `default` -> Team Lead / Orchestrator
- `explorer` -> Architect / Evidence Gatherer
- `worker` -> Implementer
- `monitor` -> Validator

### 3.2 当前执行模式

本次生成文档时:
- 未真实 spawn 多代理
- 未执行多代理并行实施
- 采用单线程 gated handoff 模拟 `default` 与 `explorer` 的职责分工
- `worker` 与 `monitor` 在本文中仅保留为后续实施阶段的职责定义

## 4. 【default / Team Lead】任务边界摘要

### 4.1 任务边界

- 本次只覆盖 `Partially Implemented`
- 本次明确排除 `document generation`
- 本次仅生成计划文档，不执行代码修改
- 后续实施时必须避免对 `Fully / Missing / N/A` 条目造成意外改动

### 4.2 任务收敛目标

计划层面的 Done Definition 如下:
- 每个 `Partially Implemented` 条目都被映射到明确修复簇
- 每个修复簇都有文件范围、测试范围和风险说明
- 每个实施批次都有进入条件、完成条件和回滚点
- 顾问/检索项目中的潜在结构性阻塞被单独显式标记

## 5. 【default / Team Lead】依赖与风险概览

### 5.1 跨域依赖顺序

建议的依赖顺序如下:
1. `cases`
2. `documents + tasks`
3. `fees + annuity + expenses`
4. `billing + collections`
5. `commission + consulting`

原因:
- 案件字段和法律状态是后续文书与时限联动的前提
- 文书和时限逻辑决定后续费用触发语义
- 费用与年费逻辑决定账单与缴费口径
- 账单与回款口径稳定后，提成结算才能稳定
- 顾问/检索项目的收费与提成最终依赖前述金额语义

### 5.2 共享模块依赖

高频共享依赖包括:
- `backend/app/modules/cases/service.py`
- `backend/app/modules/documents/service.py`
- `backend/app/modules/tasks/task_generation_service.py`
- `backend/app/modules/fees/service.py`
- `backend/app/modules/billing/service.py`
- `backend/app/modules/commission/service.py`
- `frontend/src/api/*.ts`
- `frontend/src/api/*.types.ts`

### 5.3 主要风险

#### 风险 A: 法律状态与跨模块触发耦合

案件法律状态同时被案件域、文书域和时限域引用。若状态机未先冻结，后续修复容易产生不一致。

#### 风险 B: 金额口径跨模块扩散

费率、草单、账单、收款、预收款、提成结算之间共享金额基础口径。若前序批次未稳定，后序批次会反复返工。

#### 风险 C: 顾问/检索项目存在结构承载风险

顾问/检索项目页面已采集专属属性，但当前前端 payload 未发送，后端创建逻辑也未持久化对应属性。若严格禁止 schema 变更，则必须先确认现有承载方式；否则应标记为 `BLOCKED`。

#### 风险 D: 范围失控

导出、打印、模板文档和通知函需求很容易在费用、账单、提成报表、文书清单修复中被误带入。后续实施必须持续排除这些路径。

## 6. 【explorer】Partially Implemented 完整清单

### 6.1 Cluster C1: Cases

- `US-CM-01` 新案建立
- `US-CM-02` 扩展信息维护
- `US-CM-03` 参与方管理
- `FR-CM-02` 保存时必须校验必填字段及组合规则
- `FR-CM-03` 从主数据中选择客户、申请人、外方代理，并支持创建后回填
- `FR-CM-04` 完整法律状态枚举与自动更新
- `FR-CM-05` 优先权、菌种保藏、PCT、无效案专属字段

### 6.2 Cluster C2: Documents

- `US-WD-01` 来文登记
- `US-WD-02` 发文登记与自动核销
- `US-WD-03` 期限联动
- `US-WD-04` 费用联动
- `US-WD-06` 中间文件查询与清单输出
- `FR-WD-01` 四大类中间文件与可配置子类型
- `FR-WD-03` 常用文件定义自动填充缺省字段
- `FR-WD-04` 需回复文件自动计算时限并建任务
- `FR-WD-07` 多条件查询与清单输出

### 6.3 Cluster C3: Tasks / Deadlines

- `US-DL-01` 时限模板配置
- `US-DL-02` 自动创建时限任务
- `US-DL-03` 日常提醒作业人视角
- `US-DL-04` 日常提醒监督人视角
- `US-DL-05` 手工维护时限任务
- `US-DL-07` 登录提醒与清单打印
- `FR-DL-01` 维护时限模板
- `FR-DL-02` 从案件事件/中间文件/年费任务自动创建时限任务
- `FR-DL-04` 我的时限任务视图
- `FR-DL-05` 监督时限视图
- `FR-DL-06` 手工新增/编辑/删除时限任务
- `FR-DL-08` 首页今日提醒

### 6.4 Cluster C4: Fees / Annuity / Expenses

- `US-FE-02` 标准费率与费减/折扣计算
- `US-FE-03` 官费清单与缴费
- `US-FE-04` 授权费 / 年登印费管理
- `US-FE-05` 年费管理
- `US-FE-06` 个案收款登记
- `US-FE-08` 费用情况综合查询
- `FR-FE-03` 标准费率表 + 案件参数 + 费减比例/折扣率自动计算
- `FR-FE-04` 官费清单与官费缴费明细
- `FR-FE-05` 年登印费管理
- `FR-FE-06` 年费管理
- `FR-FE-07` 个案收款登记
- `FR-FE-09` 费用情况查询

### 6.5 Cluster C5: Billing / Collections

- `US-BL-02` 手工维护账单
- `US-BL-06` 坏账与催款管理
- `US-BL-07` 预收款管理
- `FR-BL-01` 账单头与账单明细维护
- `FR-BL-03` 纯手工创建账单，支持 AR/AP
- `FR-BL-07` 坏账与恢复
- `FR-BL-08` 生成催款单
- `FR-BL-09` 预收款管理与后续冲销扣减

### 6.6 Cluster C6: Commission

- `US-COM-02` 提成记录自动生成
- `US-COM-06` 提成结算批次与报表
- `FR-COM-02` 服务费账单生成时自动生成提成记录
- `FR-COM-06` 结算批次与明细生成，并标记 `S1_Done/S2_Done`
- `FR-COM-07` 提成结算报表

### 6.7 Cluster C7: Consulting / Search

- `US-CS-01` 顾问/检索项目立案
- `US-CS-05` 账单、收款与提成
- `FR-CS-01` 记录项目专属属性
- `FR-CS-06` 按 `CONSULTING/SEARCH` 规则生成提成并纳入结算批次

## 7. 【explorer】每一项的证据来源

### 7.1 C1 Cases 证据

文档证据:
- 审查报告 Functional Compliance Matrix 第 33-42 行
- 最终增强拆解文档第 18-24 行

代码证据:
- `backend/app/modules/cases/service.py`
- `backend/app/modules/cases/schemas.py`
- `backend/app/modules/cases/enums.py`
- `backend/tests/test_case_fields.py`

关键观察:
- 当前已实现申请人唯一首位校验与基础 CRUD
- 当前已实现 A3 扩展字段 round-trip
- 仍缺跨字段组合校验、参与方主数据回填闭环、完整法律状态自动迁移规则

### 7.2 C2 Documents 证据

文档证据:
- 审查报告第 45-58 行
- 最终增强拆解文档第 25-33 行

代码证据:
- `backend/app/modules/documents/service.py`
- `backend/app/modules/documents/fee_linking_service.py`
- `backend/app/modules/tasks/task_generation_service.py`
- `backend/tests/test_b2_reply_chain.py`
- `backend/tests/test_b3_fee_linking.py`

关键观察:
- 模板级 `need_reply`、`status_effect`、`reply_to_id`、`reply_date` 已工作
- 模板触发费用草单已存在
- 仍缺完整默认值覆盖、查询维度闭环和部分联动规则细化

### 7.3 C3 Tasks / Deadlines 证据

文档证据:
- 审查报告第 62-76 行

代码证据:
- `backend/app/modules/tasks/api.py`
- `backend/app/modules/tasks/service.py`
- `backend/app/modules/tasks/task_generation_service.py`
- `backend/tests/test_task_template.py`
- `frontend/src/modules/tasks/pages/TodayReminders.vue`

关键观察:
- 已有模板管理、自动建任务、手工任务、今日提醒页面
- 仍缺作业人/监督人视图细化、排序筛选和登录提醒闭环

### 7.4 C4 Fees / Annuity / Expenses 证据

文档证据:
- 审查报告第 80-95 行

代码证据:
- `backend/app/modules/fees/service.py`
- `backend/app/modules/annuity/api.py`
- `backend/tests/test_annuity_e2e.py`

关键观察:
- 年费任务生成草单、创建官费清单、登记官费支付链路已存在
- `calculate_fee_amount()` 当前仅完整实现 `FIXED`，其他计算模式只是回退到默认金额

### 7.5 C5 Billing / Collections 证据

文档证据:
- 审查报告第 97-111 行

代码证据:
- `backend/app/modules/billing/service.py`
- `backend/app/modules/collections/service.py`
- `backend/tests/test_b5_billing_polish.py`
- `backend/tests/test_collections_e2e.py`
- `frontend/src/modules/billing/pages/BillCreate.vue`

关键观察:
- 草单转账单、冲销、反冲销、坏账/催款基础能力已存在
- 手工账单前端已提供“手工录入”页
- 仍缺 AR/AP、状态口径、预收款可见性和完整统计闭环

### 7.6 C6 Commission 证据

文档证据:
- 审查报告第 113-124 行

代码证据:
- `backend/app/modules/commission/service.py`
- `backend/tests/test_commission_e2e.py`

关键观察:
- 自动提成生成、结算批次创建、结算行生成、报表查询均已存在
- 仍缺完整的 `S1_Done/S2_Done` 完成标记规则与更完整的报表聚合口径

### 7.7 C7 Consulting / Search 证据

文档证据:
- 审查报告第 125-135 行

代码证据:
- `backend/app/modules/consulting/service.py`
- `backend/tests/test_consulting_e2e.py`
- `frontend/src/modules/consulting/pages/ConsultingCaseCreate.vue`
- `frontend/src/api/consulting.ts`

关键观察:
- 前端页面已采集 `consulting_scope`、`estimated_hours`、`search_keywords`、`search_database`
- 前端 `buildPayload()` 当前未发送这些字段
- 后端 `create_consulting_case()` 当前只落基本案件字段
- 因此该簇存在明确的“前端收集但后端未承载”的部分实现缺口

## 8. 【explorer】受影响模块与建议修改文件

### 8.1 Cluster C1

- `backend/app/modules/cases/api.py`
- `backend/app/modules/cases/service.py`
- `backend/app/modules/cases/schemas.py`
- `backend/app/modules/cases/enums.py`
- `frontend/src/modules/cases/pages/CaseCreate.vue`
- `frontend/src/modules/cases/pages/CaseEdit.vue`
- `frontend/src/modules/cases/pages/CaseDetail.vue`
- `frontend/src/api/cases.ts`
- `frontend/src/api/cases.types.ts`
- `backend/tests/test_case_fields.py`

### 8.2 Cluster C2

- `backend/app/modules/documents/api.py`
- `backend/app/modules/documents/service.py`
- `backend/app/modules/documents/schemas.py`
- `backend/app/modules/documents/fee_linking_service.py`
- `backend/app/modules/tasks/task_generation_service.py`
- `frontend/src/modules/documents/pages/DocumentCreate.vue`
- `frontend/src/modules/documents/pages/DocumentEdit.vue`
- `frontend/src/modules/documents/pages/DocumentDetail.vue`
- `frontend/src/modules/documents/pages/DocumentList.vue`
- `frontend/src/api/documents.ts`
- `frontend/src/api/documents.types.ts`
- `backend/tests/test_b2_reply_chain.py`
- `backend/tests/test_b3_fee_linking.py`

### 8.3 Cluster C3

- `backend/app/modules/tasks/api.py`
- `backend/app/modules/tasks/service.py`
- `backend/app/modules/tasks/task_generation_service.py`
- `backend/app/modules/tasks/schemas.py`
- `frontend/src/modules/tasks/pages/TaskList.vue`
- `frontend/src/modules/tasks/pages/TaskDetail.vue`
- `frontend/src/modules/tasks/pages/TaskCreate.vue`
- `frontend/src/modules/tasks/pages/TodayReminders.vue`
- `frontend/src/api/tasks.ts`
- `frontend/src/api/tasks.types.ts`
- `backend/tests/test_task_template.py`

### 8.4 Cluster C4

- `backend/app/modules/fees/api.py`
- `backend/app/modules/fees/service.py`
- `backend/app/modules/fees/schemas.py`
- `backend/app/modules/annuity/api.py`
- `backend/app/modules/annuity/service.py`
- `backend/app/modules/expenses/api.py`
- `backend/app/modules/expenses/service.py`
- `frontend/src/modules/fees/*`
- `frontend/src/modules/annuity/*`
- `frontend/src/modules/expenses/*`
- `backend/tests/test_annuity_e2e.py`

### 8.5 Cluster C5

- `backend/app/modules/billing/api.py`
- `backend/app/modules/billing/service.py`
- `backend/app/modules/billing/schemas.py`
- `backend/app/modules/collections/api.py`
- `backend/app/modules/collections/service.py`
- `frontend/src/modules/billing/*`
- `frontend/src/modules/collections/*`
- `backend/tests/test_b5_billing_polish.py`
- `backend/tests/test_collections_e2e.py`

### 8.6 Cluster C6

- `backend/app/modules/commission/api.py`
- `backend/app/modules/commission/service.py`
- `frontend/src/modules/commission/pages/CommissionList.vue`
- `frontend/src/modules/commission/pages/CommissionSettlement.vue`
- `frontend/src/api/commission.ts`
- `frontend/src/api/commission.types.ts`
- `backend/tests/test_commission_e2e.py`

### 8.7 Cluster C7

- `backend/app/modules/consulting/api.py`
- `backend/app/modules/consulting/service.py`
- `frontend/src/modules/consulting/pages/ConsultingCaseCreate.vue`
- `frontend/src/modules/consulting/pages/ConsultingProfitability.vue`
- `frontend/src/api/consulting.ts`
- `frontend/src/api/consulting.types.ts`
- 必要时最小波及:
  - `backend/app/modules/cases/service.py`
  - `backend/app/modules/commission/service.py`
- `backend/tests/test_consulting_e2e.py`

## 9. 【explorer】不应触碰的模块/文件

### 9.1 明确禁区

- 所有 migration / alembic 文件
- 所有数据库 schema 变更
- 所有模板渲染导出相关实现
- 所有打印、导出、通知函生成功能

### 9.2 当前不应作为修复目标的文件

- `backend/app/modules/billing/doc_render_bill_context.py`
- `backend/app/modules/tasks/doc_render_task_sheet_context.py`

### 9.3 共享文件最小必要波及说明

允许但需单独说明原因的共享文件:
- `backend/app/modules/cases/enums.py`
- `backend/app/modules/cases/service.py`
- `backend/app/modules/tasks/task_generation_service.py`
- `backend/app/modules/commission/service.py`
- `frontend/src/api/*.types.ts`

## 10. 【explorer】测试建议

### 10.1 单元测试建议

- 案件跨字段规则矩阵
- 文书模板默认值解析
- 时限到期计算与内部限计算
- 费率多计算模式
- 预收款扣减与反冲销
- 提成可结算状态计算
- 顾问/检索项目专属字段映射

### 10.2 集成测试建议

直接扩充现有测试:
- `backend/tests/test_case_fields.py`
- `backend/tests/test_b2_reply_chain.py`
- `backend/tests/test_b3_fee_linking.py`
- `backend/tests/test_task_template.py`
- `backend/tests/test_annuity_e2e.py`
- `backend/tests/test_b5_billing_polish.py`
- `backend/tests/test_collections_e2e.py`
- `backend/tests/test_commission_e2e.py`
- `backend/tests/test_consulting_e2e.py`

### 10.3 E2E 测试建议

- 案件建立与编辑
- 文书登记 -> 回复 -> 自动核销 -> 自动任务
- 今日提醒双视角
- 年费任务 -> 草单 -> 官费清单 -> 官费缴费
- 手工账单 -> 冲销 -> 反冲销
- 顾问项目建档 -> 收费 -> 提成

## 11. 【default / Team Lead】建议的执行批次

### 11.1 Batch 1

范围:
- Cluster C1 Cases

目标:
- 冻结案件字段规则矩阵
- 完整化跨字段保存校验
- 完整化参与方闭环
- 冻结法律状态枚举与合法迁移

排序原因:
- 为后续文书与时限联动提供稳定状态基础

### 11.2 Batch 2

范围:
- Cluster C2 Documents
- Cluster C3 Tasks / Deadlines

目标:
- 完整化模板默认值
- 完整化回复链、时限联动与费用联动
- 完整化作业人/监督人视图与今日提醒

排序原因:
- 文书与任务共享触发语义，宜同批收敛

### 11.3 Batch 3

范围:
- Cluster C4 Fees / Annuity / Expenses

目标:
- 完整化费率计算模式
- 完整化年费与官费链路
- 完整化个案收款和费用查询

排序原因:
- 费用金额口径必须在账单前稳定

### 11.4 Batch 4

范围:
- Cluster C5 Billing / Collections

目标:
- 完整化手工账单
- 完整化坏账/催款
- 完整化预收款分配与反冲销

排序原因:
- 账单与收款口径必须在提成结算前稳定

### 11.5 Batch 5

范围:
- Cluster C6 Commission
- Cluster C7 Consulting / Search

目标:
- 完整化提成生成、结算与报表
- 完整化顾问/检索项目专属属性和联动闭环

排序原因:
- 提成与顾问项目均依赖前序金额与状态口径

## 12. 【default / Team Lead】每个批次的进入条件与完成条件

### 12.1 Batch 1

Entry Criteria:
- 确认不做数据库 schema 变更
- 冻结案件域状态与字段边界

Exit Criteria:
- `CM` 相关条目全部有统一业务校验与错误口径
- 案件域测试集稳定
- 未误触 document generation

### 12.2 Batch 2

Entry Criteria:
- Batch 1 的案件状态和字段语义已稳定

Exit Criteria:
- `WD` 与 `DL` 相关条目达到闭环
- 回复链、自动任务、今日提醒均可验证
- 所有导出/打印路径保持排除

### 12.3 Batch 3

Entry Criteria:
- Batch 2 的文书与时限联动语义已稳定

Exit Criteria:
- `FE` 相关条目达到可验证闭环
- 多金额模式与年费链路稳定
- 所有通知函/导出子项仍排除

### 12.4 Batch 4

Entry Criteria:
- Batch 3 的费用项与付款语义已稳定

Exit Criteria:
- `BL` 相关条目达到可验证闭环
- 手工账单、坏账、催款、预收款链路稳定

### 12.5 Batch 5

Entry Criteria:
- Batch 4 的账单、回款和冲销口径已稳定
- 顾问/检索专属属性承载方案已经确认

Exit Criteria:
- `COM` 相关条目闭环
- `CS` 相关条目若无结构阻塞则闭环
- 若仍存在结构阻塞，必须显式标记 `BLOCKED`，不得硬推进

## 13. 【default / Team Lead】最终执行计划

### 13.1 Fix Matrix

| Item | Current Gap | Proposed Fix | Files | Tests | Risk |
|---|---|---|---|---|---|
| `US-CM-01 / FR-CM-02` | 案件保存缺少组合规则与跨字段校验 | 建立统一案件业务校验器与错误码口径 | `cases api/service/schemas + cases pages + cases api types` | `test_case_fields + cases E2E` | Medium |
| `US-CM-02 / FR-CM-05` | 扩展信息字段录入与校验不足 | 补齐扩展字段映射、条件展示与业务校验 | `cases service/schemas + case create/edit pages` | `test_case_fields + cases E2E` | Medium |
| `US-CM-03 / FR-CM-03` | 参与方主数据选择、创建、回填不闭环 | 补主数据回填链路与关系一致性 | `cases + masterdata clients + case forms` | `test_case_fields + cases E2E` | Medium |
| `FR-CM-04` | 法律状态枚举与自动迁移不完整 | 冻结状态机并接入文书联动更新 | `cases enums/service + documents service` | `test_case_fields + test_b2_reply_chain` | High |
| `US-WD-01 / FR-WD-01 / FR-WD-03` | 文书模板默认值覆盖不足 | 完善模板默认值解析与前端回显 | `documents api/service/schemas + document forms` | `test_b2_reply_chain + document E2E` | Medium |
| `US-WD-02 / US-WD-04` | 自动核销与费用联动覆盖不足 | 补 reply chain write-off 与 fee linking 分支 | `documents service + fee_linking_service` | `test_b2_reply_chain + test_b3_fee_linking` | Medium |
| `US-WD-03 / FR-WD-04` | 期限联动细则不全 | 文书创建统一接时限计算与自动建任务服务 | `documents service + tasks generation service` | `test_b2_reply_chain + test_task_template` | High |
| `US-WD-06 / FR-WD-07` | 查询条件不足，导出子项应排除 | 仅扩查询和列表，不做导出/打印 | `documents api/service + document list page` | `documents integration + list E2E` | Medium |
| `US-DL-01 / FR-DL-01` | 时限模板能力未完整覆盖 | 补模板维护和启停/校验规则 | `tasks api/service/schemas` | `test_task_template` | Medium |
| `US-DL-02 / FR-DL-02` | 自动建任务来源覆盖不足 | 扩文书/事件/年费来源并收敛幂等逻辑 | `tasks generation service + related callers` | `test_task_template + test_annuity_e2e` | High |
| `US-DL-03 / FR-DL-04` | 作业人视角能力不足 | 补排序、过滤、核销体验和页面回显 | `tasks api + task list/detail pages` | `test_task_template + tasks E2E` | Medium |
| `US-DL-04 / FR-DL-05` | 监督人视角能力不足 | 补 supervisor 维度过滤和逾期视图 | `tasks api + today reminders/list pages` | `test_task_template + tasks E2E` | Medium |
| `US-DL-05 / FR-DL-06` | 手工维护任务能力不全 | 补新增/编辑/删除权限与状态约束 | `tasks api/service + task pages` | `test_task_template + tasks E2E` | Medium |
| `US-DL-07 / FR-DL-08` | 今日提醒已存在但登录闭环不足 | 固化 today API 口径和首页提醒入口 | `tasks api + TodayReminders page` | `tasks integration + E2E` | Medium |
| `US-FE-02 / FR-FE-03` | 费率多计算模式未实现 | 实现 `FIXED` 之外的计算模式与减缴/折扣规则 | `fees service/api` | `test_annuity_e2e + fee unit tests` | High |
| `US-FE-03 / FR-FE-04` | 官费清单与缴费状态细节不足 | 补 pay list、gov payment 状态与校验口径 | `annuity api/service + fees/expenses` | `test_annuity_e2e + E2E` | Medium |
| `US-FE-04 / FR-FE-05` | 授权费/年登印费联动不足 | 完成非文档生成范围内的状态与草单链路 | `annuity + fees + expenses` | `test_annuity_e2e` | Medium |
| `US-FE-05 / FR-FE-06` | 多年度年费与客户指示闭环不全 | 补提取、指示状态与多年度草单规则 | `annuity service/api` | `test_annuity_e2e + annuity E2E` | Medium |
| `US-FE-06 / FR-FE-07` | 个案收款可见性与欠款/提成口径不足 | 补 receipt 口径与页面展示 | `fees/expenses + billing shared logic` | `test_annuity_e2e + test_b5_billing_polish` | Medium |
| `US-FE-08 / FR-FE-09` | 费用综合查询口径不足 | 建查询视图，不纳入导出 | `fees/expenses pages + query apis` | `fees integration + E2E` | Medium |
| `US-BL-02 / FR-BL-03` | 手工账单 AR/AP、折扣、明细口径不足 | 收敛 `POST /bills/manual` 与前端表单规则 | `billing api/service/schemas + BillCreate page` | `test_b5_billing_polish + billing E2E` | Medium |
| `FR-BL-01` | 账单头/明细/状态口径仍偏 MVP | 完整化账单状态、折扣、坏账信息语义 | `billing service/schemas` | `test_b5_billing_polish` | Medium |
| `US-BL-06 / FR-BL-07 / FR-BL-08` | 坏账/催款/统计仍有缺口 | 补坏账恢复、催款生成条件和统计口径，不做催款函 | `billing + collections` | `test_collections_e2e + billing E2E` | Medium |
| `US-BL-07 / FR-BL-09` | 预收款登记到后续冲销扣减可见性不足 | 补预收状态、分配进度、反冲销一致性 | `billing + collections + payment pages` | `test_b5_billing_polish + test_collections_e2e` | High |
| `US-COM-02 / FR-COM-02` | 自动提成生成覆盖路径偏单一 | 扩到账单/收款状态变化触发点并保证幂等 | `commission service + billing hooks` | `test_commission_e2e` | Medium |
| `US-COM-06 / FR-COM-06` | `S1_Done/S2_Done` 标记规则未完整落地 | 固化结算确认与完成标记更新规则 | `commission service/api` | `test_commission_e2e` | High |
| `FR-COM-07` | 报表查询存在但维度与完整性不足 | 补按代理人/案件/时间区间聚合，不做导出 | `commission service/api + commission pages` | `test_commission_e2e + commission E2E` | Medium |
| `US-CS-01 / FR-CS-01` | 专属属性前端采集但未发送，后端未承载 | 先冻结“无 schema 条件下”的承载方案，再补 API/UI/校验 | `consulting api/service + consulting page + api types` | `test_consulting_e2e + consulting E2E` | High / BLOCKED |
| `US-CS-05 / FR-CS-06` | 顾问检索项目到账单/收款/提成串联存在缺口 | 补 consulting 与 billing/commission 间编排与状态回显 | `consulting + billing + commission` | `test_consulting_e2e + test_commission_e2e` | High |

### 13.2 批次顺序

批次顺序:
1. `Batch 1 = C1`
2. `Batch 2 = C2 + C3`
3. `Batch 3 = C4`
4. `Batch 4 = C5`
5. `Batch 5 = C6 + C7`

执行策略:
- 建议串行
- 不建议在同一波次并行编辑共享服务文件
- 前端共享 API 类型文件也按同样原则串行处理

### 13.3 共享文件冲突规避方式

以下文件视为共享 ownership 文件，实施阶段必须串行:
- `backend/app/modules/cases/service.py`
- `backend/app/modules/documents/service.py`
- `backend/app/modules/tasks/task_generation_service.py`
- `backend/app/modules/fees/service.py`
- `backend/app/modules/billing/service.py`
- `backend/app/modules/commission/service.py`
- `frontend/src/api/*.ts`
- `frontend/src/api/*.types.ts`

### 13.4 回滚点

- Rollback Point 1: Batch 1 完成后，只保留案件域规则收敛结果
- Rollback Point 2: Batch 2 完成后，只保留文书/任务联动收敛结果
- Rollback Point 3: Batch 3 完成后，只保留费用与年费金额口径收敛结果
- Rollback Point 4: Batch 4 完成后，只保留账单/催款/预收款口径收敛结果
- Rollback Point 5: Batch 5 中 `COM` 与 `CS` 分开验收，`CS` 可单独阻塞，不影响 `COM` 收口

### 13.5 Done Definition

- 仅修复 `Partially Implemented` 项
- 每项都有验证证据
- 不引入对 `Fully / Missing / N/A` 的意外改动
- 所有 `document generation` 子项必须明确排除
- 每一处共享最小波及都必须写明原因、边界和验证方式
- 最终实施完成后，需保留本文件作为总控蓝本

## 14. Batch-Level 实施建议摘要

### 14.1 Batch 1 实施重点

- 先从 `cases` 建立统一业务校验器
- 再补前端案件录入规则矩阵
- 最后冻结法律状态迁移与参与方回填链路

### 14.2 Batch 2 实施重点

- 先收敛文书模板默认值
- 再收敛 reply chain 与 task generation
- 最后收敛任务视图与今日提醒页面口径

### 14.3 Batch 3 实施重点

- 先补费率计算模式
- 再补年费链路
- 最后补查询与个案收款口径

### 14.4 Batch 4 实施重点

- 先补手工账单规则
- 再补坏账/催款
- 最后补预收款与反冲销一致性

### 14.5 Batch 5 实施重点

- 先收敛提成自动生成与结算规则
- 再处理顾问/检索项目
- 若顾问/检索属性无法在无 schema 约束下落地，则必须中止该子项并保留 `BLOCKED`

## 15. Blocked / Assumption 清单

### 15.1 BLOCKED

- `US-CS-01 / FR-CS-01`

阻塞原因:
- 现有后端 `Case` 模型不包含顾问/检索专属属性字段
- 前端已采集这些属性，但当前 payload 未提交，后端也未承载
- 若不允许 schema 变更，则必须先确认是否允许使用现有可兼容承载方式

### 15.2 Assumption

- 后续实施阶段仍以“无 schema 变更”为铁约束
- 所有 document generation 子项在实施中仍持续排除
- 提成与顾问项目可复用既有账单/费用基础口径，不需新增独立会计模型

## 16. 后续实施要求

实施阶段每个原子任务都应至少输出:
- 执行的 task/runbook
- 角色
- 修改文件列表
- 验证命令与预期状态码
- 对应 evidence 路径
- 最终状态 `PASS / FAIL / BLOCKED`

本文件仅作为实施前的母计划文档。
