# Post-demo 收费后续触发规则设计

任务：`PD-FEE-SCENARIO-FOLLOWUP-TRIGGER-DESIGN-20260705-01`

## 1. 设计结论

本轮是分析设计，不写产品代码。后续收费增强应继续沿用现有费用底座：

- 官费参数继续由 `FeeRate` 承载。
- 费用候选继续通过 `official-fee-preview` 或同类预览能力暴露。
- 人工确认后再生成 `FeeDraft / FeeItem`。
- 已确认官费明细继续进入 `PayList / GovPayment`。
- 授权后费用继续复用 `GrantFeeTask`。
- 年费继续复用 `AnnuityTask`。
- PCT、海牙、集成电路布图设计先作为参数化和显式预览规则，不直接进入自动生成草单。

推荐下一步采用“服务层触发规则注册表”方式：先在服务层建立稳定的 `trigger_event -> required_fields -> rate_codes -> deadline_rule -> idempotency_key` 规则，等客户确认更多样例后再决定是否落成数据库表。不要回退到 `DocTemplate.fee_item_list` 的静态金额模式，因为复审、年费、PCT、海牙和 IC 布图设计都依赖案件字段、源文件、期限、费减和人工决策。

## 2. 证据和现状

### 2.1 已完成能力

已完成任务 evidence：

- `PD-FEE-SCENARIO-REDUCTION-SEMANTICS-FIX-20260705-01`：`0.85` 表示减缴 85%，实际应缴 15%。
- `PD-FEE-SCENARIO-CATEGORY-SUBTYPE-MODEL-20260705-01`：`FeeRate` 已支持 `fee_domain / fee_section / fee_category / fee_subtype / reduction_scope`。
- `PD-FEE-SCENARIO-DEADLINE-RULES-20260705-01`：`FILING_ACCEPTED` 预览候选已返回触发规则和期限规则，申请费期限为 `申请日/受理通知起 2 个月`。
- `PD-FEE-SCENARIO-CATALOG-AMOUNTS-COMPLETE-20260705-01`：补偿、海牙、IC 布图设计等收费条目已作为官费参数行补齐，但复杂场景仍是 disabled/pending。
- `PD-FEE-SCENARIO-FINAL-REGRESSION-20260705-01`：收费增强回归通过。

### 2.2 现有代码承载点

- `backend/app/modules/fees/service.py`：`preview_official_fee_candidates` 当前只支持 `FILING_ACCEPTED`。
- `backend/app/modules/fees/models.py`：`FeeRate` 已能表达收费项目、细分类型和减缴范围。
- `backend/app/modules/grant_fees/service.py`：`GrantFeeTask` 已有状态机、客户指令、草单生成和通知生成。
- `backend/app/modules/annuity/service.py`：`AnnuityTask` 已能按已授权案件生成多年年费任务，并已有年费官费金额。
- `backend/app/modules/documents/models.py`：`Document / DocTemplate` 可作为官文源文件，但 `fee_item_list` 是静态金额，不适合后续动态触发规则。
- `backend/app/modules/official_workflows/models.py`：`OfficialWorkPackage` 可作为 OA/官方业务工作包承载，但本轮不改变其状态机。

### 2.3 设计边界

本设计只覆盖“如何设计后续触发规则”。不承诺自动提交、自动缴费、RPA、扫码签名、CPC/OA direct submit，也不把参数表中 disabled/pending 的复杂收费立即变成自动草单。

## 3. 方案比较

### 方案 A：服务层触发规则注册表（推荐）

在 `fees` 服务层增加可测试的规则定义，例如：

| 字段 | 含义 |
| --- | --- |
| `trigger_event` | 触发事件，如 `REEXAM_REQUESTED`、`GRANT_NOTICE_RECEIVED` |
| `source_object_kind` | 来源对象，`document`、`grant_fee_task`、`annuity_task`、`case_action` |
| `required_case_fields` | 计算前必须具备的案件字段 |
| `rate_code_selector` | 根据案件类型、专利类型、年度等选择费率 |
| `deadline_rule` | 客户可读期限规则 |
| `idempotency_key` | 去重键 |
| `review_mode` | 只预览、预览后确认、生成草单后人工审核 |

优点：改动小、可 TDD、符合当前已做的 `official-fee-preview` 形态。缺点：规则运维暂时仍需开发发版。

### 方案 B：新增数据库规则表

新增 `OfficialFeeScenarioRule` 表，支持后台维护触发规则。

优点：长期可配置。缺点：本阶段字段还没完全稳定，PCT/海牙/IC 的触发条件缺样例，过早落表会把不稳定规则固化。

### 方案 C：继续扩展 `DocTemplate.fee_item_list`

把复审、授权、年费、PCT、海牙等费用挂到文书模板静态列表。

优点：改动小。缺点：不能表达权利要求项数、年度阶梯、费减、PCT 免缴、海牙分期、IC 独立域，也难以解释“为什么产生这笔费”。不推荐。

## 4. 推荐实施顺序

| 顺序 | 任务 | 推荐阶段 | 理由 |
| --- | --- | --- | --- |
| 1 | 复审触发预览 | P1.5 | 国内主线，客户容易理解；费率已在参数表，字段需求相对明确 |
| 2 | 授权/年费 deadline preview | P1.5 | 已有 `GrantFeeTask / AnnuityTask`，需要把期限和计算依据对甲方讲清楚 |
| 3 | PCT/Hague 触发规则设计为 disabled preview | P2/P3 | 参数已入表，但字段、免缴和官方样例仍需确认 |
| 4 | IC 布图设计触发规则设计为独立 domain | P3 | 不是专利案件主线，不应混进普通专利生命周期 |

## 5. 复审触发规则设计

### 5.1 业务语义

复审费不应在收到驳回决定时自动生成草单。正确触发应是：

1. 收到驳回决定官文。
2. 系统提示“可复审费用候选”。
3. 客户或代理人决定复审。
4. 系统预览复审费。
5. 人工确认后生成复审费草单。

这样避免“收到驳回但客户放弃”时误生成费用。

### 5.2 触发事件

| trigger_event | 触发来源 | 行为 |
| --- | --- | --- |
| `REJECTION_RECEIVED` | 驳回决定官文入库 | 只提示，不生成草单 |
| `REEXAM_REQUESTED` | 人工选择复审 / 复审工作包创建 | 预览复审费候选 |

### 5.3 费率选择

| 专利类型 | rate_code | 金额 | 费减 |
| --- | --- | ---: | --- |
| 发明 | `CN_REEXAM_FEE_INV` | 1000 | 是 |
| 实用新型 | `CN_REEXAM_FEE_UM` | 300 | 是 |
| 外观设计 | `CN_REEXAM_FEE_DES` | 300 | 是 |

费减语义沿用已确认规则：`fee_reduction=0.85` 表示减缴 85%，应缴 15%。

### 5.4 必需字段

| 字段 | 来源 | 说明 |
| --- | --- | --- |
| `case_id` | `Case` | 必需 |
| `patent_category` | `Case` | 决定复审费费率 |
| `fee_reduction` | `Case` | 决定应缴比例 |
| `source_document_id` | `Document` | 驳回决定源文件 |
| `doc_date` 或官方期限字段 | `Document` / `OfficialWorkPackage` | 计算或展示期限 |
| `customer_decision` | 新增动作或工作包字段 | 必须明确为复审才生成草单 |

### 5.5 期限规则

建议先输出客户可读规则：

- `驳回决定起 3 个月`

具体日期优先级：

1. 若官文或工作包已结构化 `reply_due_date`，直接使用。
2. 否则使用 `Document.doc_date + 3 个月` 作为预估，并标记“待人工核对”。
3. 如果 `doc_date` 缺失，只展示规则文本，不计算日期。

### 5.6 幂等规则

建议：

- 预览幂等键：`case_id + REEXAM_REQUESTED + source_document_id`
- 草单幂等键：`FeeDraft.draft_type=REEXAM_FEE` + `FeeItem.remark` 或后续显式来源字段

### 5.7 输出

复审预览候选应至少返回：

- `fee_category=复审费`
- `fee_subtype=发明专利 / 实用新型专利 / 外观设计专利`
- `trigger_rule=收到驳回决定且决定复审`
- `deadline_rule=驳回决定起 3 个月`
- `source_document_id`
- `amount_before_reduction`
- `reduction_ratio`
- `payable_ratio`
- `amount`

### 5.8 待确认

1. “驳回决定”在客户现有官文代码/官文名称中如何稳定识别？
2. 客户是否希望收到驳回决定时立即提示费用，但不生成草单？
3. 复审请求是否和“复审意见陈述”共用 OA 答复工作包，还是单独工作包？
4. 复审期限是否以官方页面结构化期限为准，而不是按发文日推算？

## 6. 授权/年费 deadline preview 设计

### 6.1 业务语义

甲方 demo 时最关心的是“一个案子走到授权后，费用节点和法律状态如何变化”。因此授权/年费增强优先不是新增更多金额，而是把现有 `GrantFeeTask / AnnuityTask` 的期限、触发来源、计算依据和状态解释清楚。

### 6.2 授权触发

| trigger_event | 来源 | 行为 |
| --- | --- | --- |
| `GRANT_NOTICE_RECEIVED` | 授权通知 / 办理登记手续通知官文 | 创建或展示授权费工作包，预览授权相关官费 |
| `GRANT_CLIENT_PAY_CONFIRMED` | 客户指示缴费 | 生成授权费草单 |
| `GRANT_PAYMENT_RECORDED` | 官费缴费登记 | 更新费用节点和后续年费衔接 |

### 6.3 授权阶段费用边界

当前客户资料和系统实现都提到“授权费/授权费任务”，但客户提供的最新收费清单主要明确了年费、补偿费、海牙和其他官费。下一轮实现必须先冻结授权阶段到底包含哪些官方收费：

| 候选费用 | 建议处理 |
| --- | --- |
| 授权当年年费 | P1.5 应覆盖，接 `AnnuityTask.first_annuity_year` |
| 办理登记手续相关官费 | 待确认是否仍为客户业务口径中的稳定费用项 |
| 公告印刷费 / 印花税等旧口径费用 | 待确认，不应按旧系统习惯硬编码 |

### 6.4 授权期限规则

建议预览先输出：

- `deadline_rule=以办理登记手续通知书/授权通知书载明期限为准`

如果源官文没有结构化期限，则使用 `GrantFeeTask.due_date` 展示，不从服务里重新推算。

### 6.5 年费触发

| trigger_event | 来源 | 行为 |
| --- | --- | --- |
| `ANNUITY_DUE` | `AnnuityTask` 到期节点 | 预览年费 |
| `ANNUITY_CLIENT_PAY_CONFIRMED` | 客户指示缴费 | 生成年费草单/进入官费清单 |
| `ANNUITY_LATE` | 到期后补缴 | 预览年费滞纳金 |

### 6.6 年费期限规则

建议预览先输出：

- 常规年费：`以年费任务 due_date 为准`
- 滞纳金：`每超过规定缴费时间 1 个月，加收当年全额年费 5%`

具体到期日已由 `AnnuityTask.due_date` 承载。下一轮实现不应重算并覆盖 existing due date，除非有专门任务校验年费期限算法。

### 6.7 费率选择

年费费率应继续按：

- `FeeRate.fee_type=GOV`
- `rate_group=ANNUITY`
- `patent_category`
- `year_no`
- `calc_mode=TIER`

选择匹配年度阶梯。滞纳金按“当年全额年费 × 5% × 逾期月数”预览，是否自动计算逾期月数仍待确认。

### 6.8 输出

授权/年费 deadline preview 应至少返回：

- 源对象：`GrantFeeTask.id` 或 `AnnuityTask.id`
- `trigger_event`
- `fee_category`
- `fee_subtype`
- `deadline_rule`
- `due_date`
- `fee_basis`
- `source_status`
- `review_mode`
- 当前节点状态中文说明

### 6.9 待确认

1. 授权阶段客户说的“授权费”是否只指授权当年年费，还是还包括办理登记手续费等项目？
2. 授权通知书中是否已有结构化期限字段可读取？若没有，是否允许只显示 `GrantFeeTask.due_date`？
3. 年费滞纳金是否由系统自动计算逾期月数，还是只提示规则由财务人工确认金额？
4. 开放许可年费减缴是否近期需要纳入，还是保留为 P3？

## 7. PCT 触发规则设计

### 7.1 总体判断

PCT 不应进入下一轮自动生成草单主线。原因：

- PCT 国际阶段部分费用可能参照 WIPO 人民币标准，来源版本更敏感。
- PCT 进入中国国家阶段存在免缴规则。
- 当前案件字段虽然有 PCT 基础字段，但缺少单一性主题数量、国际检索来源、国际初步审查来源、译文改正阶段等触发字段。

建议 P2/P3 先做“显式预览”而不是“自动触发”：只有用户在 PCT 场景页面或工作包里明确选择触发事件，系统才预览费用。

### 7.2 PCT 国际阶段事件

| trigger_event | 费用 | 必需字段 |
| --- | --- | --- |
| `PCT_INTERNATIONAL_FILED` | 检索费、优先权文件费等 | `case_type=PCT_INTL`、国际申请号、优先权项数 |
| `PCT_ADDITIONAL_SEARCH_REQUIRED` | 附加检索费 | 单一性主题数量 |
| `PCT_PRELIM_EXAM_REQUESTED` | 初步审查费、初审附加费 | 是否请求初审、附加主题数量 |
| `PCT_LATE_PAYMENT` | 滞纳金 | 未缴费用、上限基准 |

### 7.3 PCT 进入中国国家阶段事件

| trigger_event | 费用 | 必需字段 |
| --- | --- | --- |
| `PCT_NATIONAL_PHASE_ENTERED` | 宽限费、国内规则费用 | 国际申请日、进入日、是否超过 30 个月 |
| `PCT_TRANSLATION_CORRECTION_REQUESTED` | 译文改正费 | 阶段：初审/实审 |
| `PCT_UNITY_RESTORE_REQUESTED` | 单一性恢复费 | 官方要求或客户动作 |
| `PCT_PRIORITY_RESTORE_REQUESTED` | 优先权恢复费 | 优先权恢复动作 |

### 7.4 免缴规则

PCT 进入中国阶段必须支持免缴提示：

- CNIPA 作为受理局并进行国际检索的 PCT，进入中国国家阶段时免缴申请费及申请附加费。
- CNIPA 作出国际检索报告/专利性国际初步报告的 PCT，进入中国并提出实审请求时免缴实审费。

这些字段在当前系统中不能稳定判断，应列为待确认字段，不应硬编码推断。

### 7.5 待确认

1. 客户近期是否真的需要 PCT 自动触发，还是只需要费率参数查询？
2. PCT 国际阶段费用来源是否以 WIPO/CNIPA 官方最新人民币表为准？
3. CNIPA 受理局、国际检索单位、国际初步审查报告来源是否已有结构化字段？
4. PCT 进入中国国家阶段的 30/32 个月规则是否要系统计算，还是由工作人员输入是否宽限？

## 8. Hague / 外观设计国际注册触发规则设计

### 8.1 总体判断

海牙/外观设计国际注册指定中国费用已进入参数表，但不建议自动触发。原因是它不完全等同普通国内外观申请，且第一期、第二期、第三期的触发节点、缴费节点和官方通知样例需要客户确认。

### 8.2 触发事件

| trigger_event | 费用 | 费减 | 说明 |
| --- | --- | --- | --- |
| `HAGUE_CN_DESIGNATION_FIRST_DUE` | 指定中国单独指定费第一期 | 是 | 金额 4100 |
| `HAGUE_CN_DESIGNATION_SECOND_DUE` | 指定中国单独指定费第二期 | 是 | 金额 7600 |
| `HAGUE_CN_DESIGNATION_THIRD_DUE` | 指定中国单独指定费第三期 | 否 | 金额 15000 |

### 8.3 必需字段

- 海牙/国际注册申请号。
- 指定中国状态。
- 分期阶段：第一期、第二期、第三期。
- 官方通知或客户动作来源。
- 是否符合费用减缴条件。
- 到期日或官方期限。

### 8.4 输出规则

预览候选必须明确：

- `fee_category=指定中国单独指定费`
- `fee_subtype=第一期/第二期/第三期`
- 第一期、第二期可费减。
- 第三期不可费减。
- `review_mode=预览后人工确认`

### 8.5 待确认

1. 客户是否有海牙指定中国的实际成功样例？
2. 三期费用的触发节点分别来自哪个官方通知或页面动作？
3. 海牙案件在系统中应作为 `case_type=HAGUE`，还是 `patent_category=DES` 下的特殊流程？

## 9. IC_LAYOUT 触发规则设计

### 9.1 总体判断

集成电路布图设计不是普通专利案件生命周期的一部分，不应混入“专利案件提交 -> OA -> 授权 -> 年费”的主线 demo。它应作为独立 `fee_domain=IC_LAYOUT` 的参数域和后续专门流程。

### 9.2 触发事件

| trigger_event | 费用 |
| --- | --- |
| `IC_LAYOUT_REGISTRATION_FILED` | 布图设计登记费 |
| `IC_LAYOUT_REEXAM_REQUESTED` | 布图设计登记复审请求费 |
| `IC_LAYOUT_BIBLIO_CHANGE_SUBMITTED` | 著录事项变更手续费 |
| `IC_LAYOUT_EXTENSION_REQUESTED` | 延长期限请求费 |
| `IC_LAYOUT_RESTORE_RIGHT_REQUESTED` | 恢复布图设计登记权利请求费 |
| `IC_LAYOUT_NONVOLUNTARY_LICENSE_REQUESTED` | 非自愿许可使用请求费 |
| `IC_LAYOUT_REMUNERATION_ADJUDICATION_REQUESTED` | 非自愿许可使用支付报酬裁决费 |

### 9.3 必需字段

- 是否存在 IC 布图设计案件对象或案件类型。
- 登记号/申请号。
- 触发动作。
- 源文件或客户指令。
- 官方期限。

### 9.4 设计边界

下一轮不建议实现 IC 自动触发。建议只保持参数表可查，并等客户确认确实有该业务量后再建立独立任务。

### 9.5 待确认

1. 客户是否实际办理集成电路布图设计业务？
2. 如果办理，是否使用同一案件系统，还是应作为独立业务类型？
3. IC 布图设计是否需要进入客户 demo 的主线？

## 10. 下一轮开发任务建议

### 10.1 P1.5 推荐任务

1. `PD-FEE-SCENARIO-REEXAM-TRIGGER-PREVIEW-20260705-01`
   - closure：扩展官方费用预览支持 `REEXAM_REQUESTED`，按专利类型选择复审费，返回期限规则和费减计算。
   - non-closure：不自动创建复审工作包，不自动提交复审请求。

2. `PD-FEE-SCENARIO-GRANT-ANNUITY-DEADLINE-PREVIEW-20260705-01`
   - closure：授权费任务和年费任务输出中文期限规则、触发来源和计算依据，供 demo 解释费用节点线。
   - non-closure：不重算年费期限，不自动生成新类型草单。

### 10.2 P2/P3 推荐任务

3. `PD-FEE-SCENARIO-PCT-HAGUE-TRIGGER-RULES-20260705-01`
   - closure：冻结 PCT/Hague trigger event、必需字段、disabled preview 设计。
   - non-closure：不启用自动生成，不处理官方接口。

4. `PD-FEE-SCENARIO-IC-LAYOUT-TRIGGER-RULES-20260705-01`
   - closure：冻结 IC_LAYOUT 独立业务域设计。
   - non-closure：不把 IC 布图设计混入普通专利案件生命周期。

## 11. 验收标准草案

后续实现应满足：

1. 每个预览候选都能解释“为什么产生这笔费”。
2. 每个候选都有 `fee_category / fee_subtype / trigger_rule / deadline_rule / reduction_scope`。
3. 每个触发都必须有幂等键，避免同一官文或同一任务重复生成草单。
4. 国内主线可以进入 P1.5；PCT/Hague/IC 只有在字段和客户样例确认后才启用自动触发。
5. 所有用户可见状态和规则说明必须是简体中文。
6. 任何无法确认的期限或金额只能标记“待确认/待人工核对”，不能假装精确。

## 12. 当前推荐结论

下一步开发应先做复审触发预览，再做授权/年费 deadline preview。PCT/Hague/IC 应保持参数化和设计冻结，不应进入下一轮自动触发实现，除非客户明确表示这些场景是近期高频业务并提供成功样例。
