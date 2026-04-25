# FPMS Phase 1 增强方案：案卷主线 + 文件门禁

版本：Phase 1 修订版
目标：把“文件驱动”从口号落到案卷动作的输入、证据、门禁、影响计划和效果账本，同时保留 FPMS 既有案卷主线。

## Story Shape Classification

| 指标 | 结论 |
|---|---|
| shared_file_density | 高。会涉及案件、文书、任务、费用、权限、前端路由和设置页。 |
| prereq_dependency_density | 高。必须先冻结文件资产、文书事件、门禁快照、影响计划、效果账本的数据合同。 |
| be_fe_coupling | 高。前端每个关键页面都依赖后端预览和门禁结果。 |
| evidence_cost | 高。需要证明状态、任务、费用不会重复落账，并证明缺材料时阻止或审计放行。 |

chosen_runbook：P0-prereq-heavy-story。

执行原则：先做模型和 API 合同，再分波次做收案、递交、来文登记、卷宗账本和规则后台。不得把十个页面一次性当成一个实现任务。

## 1. 产品定位

本阶段不建设独立的文件主流程。用户仍然围绕案卷工作：

- 新建案卷
- 案件详情
- 案件递交
- 案内登记来文
- OA 答复
- 授权、证书、年费

变化是：每个动作都必须说明它依据哪些文件、满足哪些门禁、会产生哪些状态/任务/费用影响，并留下可审计账本。

一句话定义：

案卷是主工作对象；文件是案卷动作的证据；文书事件是状态、任务、费用变化的驱动单元。

## 2. 修订后的核心原则

### 2.1 文件不直接改案件

文件只能先形成文书事件或明确的案卷动作。状态、任务、费用由文书事件的影响计划确认后落账。

错误链路：上传文件 → 自动改案件状态。

正确链路：上传文件 → 文件资产 → 文件核验 → 文书事件 → 影响计划 → 用户确认 → 效果账本。

### 2.2 新建案卷必须有真实收案文件，但递交必须检查最终文件

建案检查的是收案事实：

- 客户指示或委托邮件
- 说明书收案稿
- 权利要求书收案稿
- 摘要
- 附图或外观图

递交检查的是最终递交材料：

- 最终说明书
- 最终权利要求书
- 最终摘要
- 最终附图或外观图
- 申请书/请求书
- 委托书或后补审计
- 费用减缴材料或不申请费减说明
- 客户确认记录

所以“收案材料完整”不等于“可递交”。

### 2.3 门禁结果必须可解释

每次门禁要记录：

- 检查场景：建案、撰写、客户确认、递交、来文登记
- 要求项
- 满足该要求的文件
- 文件角色：来源文件、收案稿、最终递交稿、签章件、生成件
- 文件状态：已收到、已识别、已核验、已替换、已事件化、已用于递交、已作废
- 结论：通过、软通过、硬阻止、需人工覆盖
- 覆盖人和覆盖原因

### 2.4 状态要拆维度

单一案件状态不足以表达代理所业务。建议拆为四个维度：

| 维度 | 作用 | 示例 |
|---|---|---|
| ApplicationStatus | 官方/法律程序状态 | 未递交、等待受理、实审、一通、授权、驳回、撤回 |
| AgencyWorkflowStage | 所内作业阶段 | 收案、撰写准备、客户确认、递交、来文处理、答复中 |
| ClientServiceStatus | 客户服务状态 | 待客户材料、待客户确认、已转达、领证待转交 |
| RightsStatus | 权利维护状态 | 未授权、有效、终止、恢复中、无效、届满 |

兼容策略：现有 T_Case.status 在第一阶段保留，可作为 ApplicationStatus 的兼容投影；新设计不得继续把客户服务状态和权利状态塞回同一个字段。

### 2.5 规则矩阵拆成匹配规则和效果项

文书状态规则不应一行同时承担所有副作用。建议结构：

- 规则头：匹配什么文书事件和文件类型。
- 状态效果项：改哪个状态维度。
- 任务效果项：创建、完成或建议更新哪个任务。
- 费用效果项：创建费用草单或明确不生成。
- 文件效果项：文件状态从已核验变为已事件化，或被标记为递交使用。
- 幂等键：防止重复生成任务、费用和状态历史。

## 3. 核心数据模型

### 3.1 FilePackage

一次导入或上传批次，例如客户邮件、扫描批次、CNIPA 下载包。

关键字段：

- id
- source_channel
- source_ref
- subject
- sender_name
- received_at
- intake_status
- suggested_case_id
- suggested_action
- created_by / created_at

### 3.2 FileAsset

单个不可变文件。替换文件时新增版本或新资产，不覆盖旧文件。

关键字段：

- id
- package_id
- original_file_name
- mime_type
- file_size
- storage_key
- sha256_hash
- file_kind
- file_role
- file_status
- version_no
- replaces_file_id
- parse_status
- extracted_metadata
- uploaded_by / uploaded_at

建议 file_status：

- RECEIVED
- IDENTIFIED
- VERIFIED
- EVENTIZED
- USED_FOR_FILING
- REPLACED
- VOIDED

### 3.3 DocumentEvent

有业务意义的文书事件。它不是普通附件，也不是文件本身。

示例：

- CLIENT_INTAKE：客户新申请委托
- OA_NOTICE：审查意见通知书
- GRANT_NOTICE：授权通知书
- PATENT_CERTIFICATE：专利证书
- RIGHT_TERMINATION_NOTICE：专利权终止通知
- FILING_PACKAGE：递交材料包

关键字段：

- id
- case_id
- event_type
- doc_template_id
- direction
- event_date
- title
- source
- status: DRAFT / PREVIEWED / CONFIRMED / CANCELLED
- idempotency_key
- created_by / created_at

### 3.4 FileLink

把文件资产连接到案卷、文书事件、任务、费用草单。

关键字段：

- id
- file_id
- target_type: CASE / DOCUMENT_EVENT / TASK / FEE_DRAFT
- target_id
- link_role: SOURCE_FILE / INTAKE_DRAFT / FINAL_FILING_COPY / SIGNED_AUTHORIZATION / GENERATED_OUTPUT / SUPPORTING_EVIDENCE
- created_by / created_at

### 3.5 GateEvaluation

一次门禁检查快照，必须可回放。

关键字段：

- id
- case_id
- gate_scope: INTAKE_CREATE / DRAFTING / CLIENT_CONFIRM / BATCH_FILING / DOCUMENT_EVENT_REGISTER
- result: PASS / SOFT_PASS / HARD_BLOCK / OVERRIDE_REQUIRED / OVERRIDDEN
- evaluated_at
- evaluated_by
- override_reason
- items_json

### 3.6 ImpactPlan

提交前影响预览。用户看到的是它，不是后台直接改状态。

关键字段：

- id
- case_id
- document_event_id
- matched_rule_id
- status_effects_json
- task_effects_json
- fee_effects_json
- file_effects_json
- requires_manual_confirm
- confirmed_by / confirmed_at

### 3.7 EffectLedger

落账记录。用于审计和防重复。

关键字段：

- id
- impact_plan_id
- effect_type: STATUS / TASK / FEE / FILE
- target_type
- target_id
- from_value
- to_value
- idempotency_key
- applied_by / applied_at

## 4. 关键流程

### 4.1 新建案卷

步骤：

1. 收案文件包：上传客户邮件、申请材料、压缩包或扫描件。
2. 文件识别：系统建议文件类型和文件角色，流程人员核验。
3. 案件信息：填写客户、案名、类型、发明人、申请人等。
4. 文件核验清单：检查收案节点要求。
5. 缺失任务：对可后补材料生成任务。
6. 创建预览：展示将创建的案卷、客户收案文书事件、文件链路、门禁快照和任务。

创建成功后：

- 创建 T_Case。
- 创建 CLIENT_INTAKE 类型 DocumentEvent。
- 将收案文件通过 FileLink 连接到 Case 和 DocumentEvent。
- 保存 GateEvaluation。
- 生成缺失材料任务。
- 不触发递交、不生成最终稿、不生成官费时限。

### 4.2 案件详情

详情页不应只是字段表。建议固定三块：

- 左侧：所内工作流阶段。
- 中间：当前节点推荐动作和阻止原因。
- 右侧：文件材料区，显示当前节点要求项、满足文件、缺失项和门禁结果。

### 4.3 案件递交

批量递交保留，但检查对象必须是最终递交材料。

执行前分组：

- 可递交：所有硬要求满足。
- 可后补递交：只有允许后补项缺失，必须写审计。
- 不可递交：缺最终说明书、权利要求书、外观图等核心材料。

被硬阻止的案件不得进入同一递交事务。

### 4.4 案内登记来文

官方来文必须绑定来源文件。

流程：

1. 选择案卷。
2. 上传或选择已核验来源文件。
3. 选择文书事件类型和模板。
4. 系统生成 ImpactPlan。
5. 普通规则由流程人员确认；特殊规则由律师或管理员确认。
6. 确认后落 EffectLedger，并更新状态、任务、费用和文件状态。

### 4.5 待归档文件

待归档文件只是辅助队列。它只能把游离文件送回主流程：

- 创建新案卷。
- 案内登记来文。
- 补充已有案卷材料。
- 登记证书、年费通知或终止通知。

不得在待归档文件页直接改案件状态、生成费用或关闭任务。

## 5. API 合同建议

第一阶段 API 不应一次性做全量。建议按竖切推进。

### 5.1 上传文件资产

POST /file-assets/upload

返回 file_id、file_kind 建议、file_status、sha256_hash、parse_status。

### 5.2 收案门禁预览

POST /cases/intake-gate/preview

输入案件类型、专利类型、流向、文件列表。返回 GateEvaluation 草案。

### 5.3 创建案卷并归档收案文件

POST /cases/from-intake-files

创建案卷、CLIENT_INTAKE 文书事件、文件链路、缺失任务和门禁快照。

### 5.4 递交门禁预览

POST /cases/batch-filing/gate-preview

返回每个候选案件的最终材料门禁结果。

### 5.5 文书事件影响预览

POST /document-events/impact-preview

只预览，不落账。

### 5.6 确认文书事件影响

POST /document-events/{event_id}/confirm-impact

确认后落状态、任务、费用和文件状态效果。

## 6. 第一阶段范围修订

建议不要把所有页面一次实现。按以下竖切拆分：

| Phase | 闭合切片 | 非闭合 |
|---|---|---|
| 1A | 新建案卷绑定收案文件，创建 CLIENT_INTAKE 事件和缺失任务 | 不做递交门禁、不做 OA 规则 |
| 1B | 递交前最终材料门禁 | 不做来文登记规则后台 |
| 1C | 官方来文登记影响预览，覆盖 OA、授权、证书、终止通知 | 不做邮件自动拉取 |
| 1D | 卷宗事件账本和文件状态列表 | 不做全文 OCR |
| 1E | 待归档文件队列和规则试跑器 | 不做自动 CNIPA 下载 |

## 7. 种子规则修订

本包的数据种子已改为与现有枚举兼容：

- CaseType 使用 NORMAL。
- PatentCategory 使用 INV、UM、DES。
- FlowDir 使用 CN_DOMESTIC、CN_OUTBOUND、FOREIGN_INBOUND。
- 递交规则明确区分收案稿和最终递交稿。

## 8. 原型页面

1. 案件工作台总览
2. 新建案卷 - 收案文件
3. 新建案卷 - 文件核验清单
4. 新建案卷 - 事件提交预览
5. 案件详情 - 工作流与文件材料区
6. 案件详情 - 卷宗事件账本
7. 案件递交 - 最终材料门禁
8. 案内登记来文 - 影响预览
9. 待归档文件 - 辅助队列
10. 状态规则矩阵 - 试跑器

## 9. 验收标准

### 新建案卷

Given 用户上传客户申请材料。
When 完成案卷信息和文件核验。
Then 系统创建案卷、CLIENT_INTAKE 文书事件、文件链路、门禁快照和缺失材料任务。
And 系统不生成递交事件、不生成官费时限。

### 递交门禁

Given 某案只有收案说明书但没有最终说明书。
When 用户进入批量递交。
Then 系统显示最终材料缺失。
And 阻止该案进入递交事务。

### 登记 OA 通知

Given 案件处于实审阶段，且来源文件已核验。
When 用户登记 OA_NOTICE。
Then 系统先展示影响计划。
And 用户确认后生成 OA 答复时限任务、写入效果账本和状态历史。

### 登记专利证书

Given 案件已授权。
When 用户登记专利证书。
Then 申请状态保持授权，客户服务状态变为领证。
And 不重复生成授权费。
And 要求人工确认。

## 10. 最终判断

本修订版保留案卷主线，但把“文件驱动”落到了可执行对象：

- 文件资产记录真实文件。
- 文书事件表达业务事实。
- 门禁快照解释能不能推进。
- 影响计划先预览再确认。
- 效果账本保证可审计和不重复。

这比只在案件工作流中增加附件检查更稳，也更接近中国专利代理事务所围绕来文、去文、客户指示和官方通知推进工作的实际方式。
