# FPMS Post-demo 三线主流程 V8 Mitigation Design

- 任务：`PD-POSTDEMO-V8-MITIGATION-DESIGN-20260712-01`
- 日期：2026-07-12
- 状态：V8 权威设计基线；尚未进入实施计划或产品实现
- 运行手册：`P0-prereq-heavy-story`
- 设计角色：中国专利代理机构流程、业务架构与软件实施

## 1. 文档权威性（Authority）

本设计是下一步实施计划、原子任务清单和后续实现的业务与架构标准。

权威关系如下：

1. 法律、官方费率和官方操作口径，以国家知识产权局及其引用的现行法规、公告和指南为准。
2. 客户内部操作、服务费、模板和归档习惯，以客户原始文档、工作簿、样例和书面答复为准。
3. `docs/reviews/fpms_postdemo_three_lane_pre_fix_audit_20260712.md` 是本设计的复审输入。
4. 本 V8 设计把复审结论转成可实施合同；与 V7 业务语义冲突时，以 V8 为准。
5. `docs/postdemo/postdemo_p1_lifecycle_demo_design_v7_20260711.md` 保留为历史演示基线，不回写、不删除、不改造为 V8。
6. `docs/superpowers/specs/2026-07-10-fpms-additional-gap-mitigation-design.md` 及 Tasks 01–70 的关闭证据，在其原七项解释范围内继续有效；V8 继承而不重做。
7. 客户澄清文档中的未决项，只有在取得客户确认记录后才成为对应模块的实施输入；实现者不得自行选择。

若后续官方规则或客户原件发生变化，应先更新来源台账、复审结论和本设计版本，再写实施任务；不得让代码现状反向改变来源事实。

## 2. 目标、原则与 Story Shape Classification

### 2.1 设计目标

V8 要建立一个证据驱动的案件主线，使同一案件在一个一致快照中同时显示：

- 居中的案件生命周期；
- 一侧的文件与工作包证据线；
- 另一侧的官费与服务费节点线。

中央主线必须分别表达事务所业务阶段、官方程序阶段和权利法律状态。文件、任务、费用草单、内部清单或付款登记均不得自行充当权利法律状态。

### 2.2 设计原则

1. 事件先于状态：先记录受控事件和证据，再更新状态投影。
2. 真实来源先于推算：真实官文金额、期限和分项优先于费率预览。
3. 义务先于草单：法律缴费义务、客户指示、内部草单、支付和官方凭证分开。
4. 文件不可覆盖：修订、转换、递交和回执形成版本谱系，不能用“最新附件”覆盖历史。
5. 未确认即关闭自动化：缺少来源、版本、客户政策或复核权限时，相关自动动作 fail-closed。
6. 替换旧副作用，不叠加第二套判断：状态、文件和费用复杂性收进深层模块。
7. 兼容迁移：先新增事件与投影、双读对账，再关闭旧写入口；不伪造旧证据。
8. 已关闭切片不重做：V8 新任务只关闭新增残余或原明确非闭包。

### 2.3 Story Shape Classification

- `shared_file_density`: high。案件、文书、工作包、费用、授权、年费和案件详情页面存在多个共享所有权文件。
- `prereq_dependency_density`: high。状态事件、文件版本和费用义务 schema 是后续集成与 UI 的共同前置。
- `be_fe_coupling`: high。前端三线同屏必须消费一个稳定、完整的后端读取合同，不能自行拼接。
- `evidence_cost`: high。迁移、法律状态、费用计算、宏工作簿和长期案件分页均需要直接证据。
- `chosen_runbook`: `P0-prereq-heavy-story`。

## 3. 已考虑方案与选择

### 3.1 方案 A：在 V7 后追加零散增量

优点是文档改动小；缺点是状态、收费和模板规则散落在多个版本，后续计划容易继续引用 V7 已被收窄的语义。

### 3.2 方案 B：建立新的 V8 权威设计（已选）

V8 明确继承 Tasks 01–70、扣除已完成工作，并把新复审的三线合同、决策门、迁移和验收集中在一个标准中。V7 保留为历史演示证据。

### 3.3 方案 C：直接重写 V7

文档表面集中，但会破坏历史运行证据和版本可追溯性，不采用。

## 4. 已完成工作扣除（Closed-work subtraction）

### 4.1 继承且不得重做的能力

下列 Additional-GAP 能力已经有 Tasks 01–70 的直接证据，V8 只做定向回归或适配新模块：

- 文书向导请求上限及真实路径；
- 文书创建及必需副作用的原子提交/回滚；
- 文书语义 resolver、60 项来文可执行/仅参考分类和 fail-closed；
- filing/OA 工作包 `resolve_key`、existing-first service、读取入口和可达 UI；
- OA_OUT 不提前关闭任务或恢复案件；
- 回执同案、同源、历史扫描、归档前重验、恰好一个任务和幂等归档；
- 结构化官方期限 carrier、创建/编辑/向导/UI 及未确认期限 fail-closed；
- 授权任务来源、确认期限、替换谱系、旧任务禁用和中文 UI；
- 默认无客户缴费指示时不提前生成通用授权费草单；
- manifest-scoped release gate、代表性真实路径、最终关闭台账和证据脱敏。

新模块若替换这些能力内部对 `Case.status` 的写法，必须保持上述可观察合同；这属于适配与回归，不是重新声明旧任务未完成。

### 4.2 P0 对账

| GAP | 继承基础 | V8 残余实现 | 客户决策门 |
| --- | --- | --- | --- |
| `P0-01` 三种状态和事件史 | 文书语义、OA 回执事务、期限、授权谱系 | 三轴状态、不可变事件、证据引用、旧 `Case.status` 兼容投影、关闭所有直接状态写入口 | 仅授权证据载体和人工复核权限 |
| `P0-02` OA 闭环 | source-keyed OA package、OA_OUT 保持任务开放、回执归属与唯一关闭 | OA_OUT 与唯一工作包原子关联；拆分内部准备、人工外部提交、官方回执和正式闭环时间；修正 `reply_date/REPLIED` 投影 | 无 |
| `P0-03` 授权法律状态 | 授权来源/期限/替换谱系、旧任务禁用、默认不提前出草单 | 删除附件上传和授权费任务完成推进 `GRANTED` 的两条捷径；增加授权公告确认事件和登记簿核验 | `DG-GRANT-*` |
| `P0-04` 文件谱系 | 附件角色、MIME、哈希、工作包 manifest 和回执载体 | 完整 Word、修订稿、拆分文件、XML、最终 PDF/XML、回执的版本与派生关系；正式 `FILING_FULL_WORD` 门禁 | 旧表单分类 |
| `P0-05` 费减字段 | `FeeRate.allow_reduction`、合法比例算法、费率生效区间 | 单一规范字段、批准范围、旧值迁移和非法/未知值 fail-closed | 无全局政策门；逐案批准证据必需 |
| `P0-06` 费用义务来源 | 文书期限、授权来源和费率预览来源字段 | 持久费用义务、真实通知分项、来源、期限、费率版本、唯一键；移除固定 `FILING_ACCEPTED` 预览 | `DG-FEE-*-DRAFT` |
| `P0-07` 缴费文件 | PayList/GovPayment、人工支付、模板状态字段 | 内部清单与官方上传产物分离；经验证模板 adapter；导出/上传/支付/核验分状态 | `DG-PAYMENT-WORKBOOK` |
| `P0-08` 三线同屏 | 各模块现有读取与授权谱系投影 | 单一一致 `lifecycle-overlay`、完整游标、中央三状态和两侧证据关联 | 无 |

### 4.3 P1 稳定标识

V8 为复审报告的 P1 残余冻结设计级标识，供下一实施计划引用：

| ID | 设计闭包 |
| --- | --- |
| `P1-01` | 22 项去文及后续来文语义继续逐项确认；未确认行保持 reference-only。 |
| `P1-02` | 导入客户真实格式函、模板族/变体、字段合同、版本、真实渲染和归档。 |
| `P1-03` | 可复制/不可复制 OA 的条件附件组合及 PDF→附页派生证据。 |
| `P1-04` | 法定官费来源审批、费率分类、五档滞纳金及逐费种事件—义务闭环。 |
| `P1-05` | 服务费独立版本、审批、税、币种、折扣和适用范围。 |
| `P1-06` | 年费类型、年度、期限、前十年费减、客户指示和终止规则的真实用例。 |
| `P1-07` | 长期案件完整读取；任何 overlay 不得以固定前 20/50 条冒充全量。 |

一个原子切片可以服务多个 GAP，但不能复制实现；最终台账必须逐 GAP 展开 required slices。

## 5. 固定规则与 Decision gates

### 5.1 已冻结、不得再次询问客户

- `0.85` 表示减缴 85%、实缴 15%；`0.7` 表示减缴 70%、实缴 30%；显式 `0` 表示不减缴。
- 显式 `0` 不要求费减批准文件，但必须来自本次明确录入或已确认迁移；历史缺失、非法字符串或语义不明不能静默转成 `0`。
- `0.7/0.85` 必须有已确认的批准证据，并保存费种、年度和有效区间。当前可减缴范围为：申请费（不含公布印刷费和申请附加费）、发明实审费、复审费，以及自授权当年起十年的年费。
- PCT 不得整体标记为可减或不可减：国家知识产权局作为受理局并进行国际检索的 PCT 进入中国国家阶段时免缴申请费及申请附加费；国家知识产权局作出国际检索报告或专利性国际初步报告的，国家阶段提出实审请求时免缴实审费；国家阶段其他收费按国内规则，符合条件的复审费和年费可以申请费减；国际阶段代收项目按当期版本处理。
- 申请费真实义务优先采用缴纳申请费通知书中的分项、金额和期限。
- 授权/办理登记通知只进入授权登记待办；通知书中的授权当年年费是独立义务。
- 授权通知、证书收件、草单、PayList、支付或授权费任务完成均不产生授权生效。
- 发明、实用新型和外观设计专利权自授权公告日起生效；登记簿核验后续状态，证书是凭证。
- 年费滞纳金以未减缴当年全额年费为基数：超期不满或不超过一个月为 0%；超过一个月至两个月为 5%；后续依次为 10%/15%/20%/25%，最高 25%、补缴期最长六个月；具体通知书的日期分段优先。
- 不可复制 OA：整份答复先转 PDF 并作为内部来源保存，再提取“意见陈述书附页”，仅附页以“其他证明文件”递交。
- 内部完整 Word、修订 Word、结构化递交文件、官方最终 PDF/XML、回执和客户函是不同证据角色。
- 客户已经提供 8 份真实信函模板；缺口是导入、字段、版本、渲染和归档，不是等待模板。
- 当前 `.xlsm` 未证明为清洁当前版本；普通 `.xlsx` 只能是内部清单。
- 客户《标准费率》及天悦网页不能替代国家知识产权局法定费率来源。

主要官方依据：

- [中华人民共和国专利法第三十九、四十条](https://www.cnipa.gov.cn/art/2020/11/23/art_2197_155169.html)
- [专利和集成电路布图设计缴费服务指南](https://www.cnipa.gov.cn/attach/0/b2d5a31081404b83a36c0df1ebe591e7.pdf)
- [国家知识产权局第 594 号公告](https://www.cnipa.gov.cn/art/2024/8/6/art_2468_205759.html)
- [PCT 进入中国国家阶段费减答复](https://www.cnipa.gov.cn/jact/front/mailpubdetail.do?sysid=6&transactId=472598)
- [授权或驳回后相关事项介绍](https://www.cnipa.gov.cn/art/2020/6/5/art_1517_92474.html)

### 5.2 客户决策门

未确认时采用安全默认值，只阻塞表中对应自动化：

| Gate | 客户需确认 | 未确认默认 | 仅阻塞 |
| --- | --- | --- | --- |
| `DG-FEE-APPLICATION-DRAFT` | 申请费义务确认后自动建待核对草单，还是等待客户指示 | 不自动，等待 `PAY` | 义务→申请费草单；不阻塞通知、义务、期限和估算 |
| `DG-FEE-GRANT-YEAR-DRAFT` | 授权当年年费是否自动建待核对草单 | 不自动，等待 `PAY` | 义务→授权当年年费草单 |
| `DG-FEE-FUTURE-ANNUITY` | 后续年费是否允许客户/案件例外自动草单 | 一律先取得客户指示 | 后续年费自动草单 |
| `DG-GRANT-EVIDENCE-SOURCE` | 授权公告和登记簿的受控数据来源 | 只归档为待复核 | 自动推进授权法律状态 |
| `DG-GRANT-MANUAL-REVIEW` | 人工补录、冲突处理、提出人和第二复核人权限 | 禁止人工覆盖 | 授权异常人工确认 |
| `DG-PAYMENT-WORKBOOK` | `.xlsm` 当前版本、清洁副本、行数、必填、校验、回传和上传证明 | 只允许内部清单 | 官方上传工作簿生成与“可上传”状态 |
| `DG-SERVICE-RATE-VERSION` | 服务费版本、审批、币种、税、区间和适用项目 | 不激活服务费 | 服务费报价/应收；官费不受阻塞 |
| `DG-LEGACY-FORM-CLASS` | 旧 `.DOC` 是历史、内部使用还是拟官方递交 | 只作历史/内部参考 | 旧表单递交就绪资格 |

决策必须保存来源、版本、确认人、生效时间和适用范围。不得为这些少量选择引入通用工作流规则引擎。

`DG-LEGACY-FORM-CLASS` 只门控旧 `.DOC` 是否具备官方递交就绪资格；它不门控客户已经确认的 8 份格式函模板。8 份格式函在完成模板导入、字段映射、版本、渲染和归档后即可实施。

## 6. 深层模块（Deep modules）

V8 选择四个深层模块。调用方和测试只跨越这些 interface；复杂判断留在 implementation 内部。

### 6.1 案件生命周期模块（Lifecycle）

Seam：所有案件中央状态变化的唯一入口。

```text
apply_lifecycle_event(command, transaction) -> LifecycleTransitionResult
```

`command` 至少包含 `case_id`、`event_type`、`effective_at`、`evidence_refs[]`、`actor_id`、条件性的 `reviewer_id`、`idempotency_key`、`payload`。

不变量：

- 外层业务用例拥有事务；模块只 `flush`，不自行 `commit`。
- 同一事件原子追加事件、校验证据并更新三个状态投影。
- 同案同幂等键同载荷返回既有结果；同键不同载荷返回 409。
- 事件只追加；更正通过新事件和 `supersedes_event_id`，不修改历史。
- 只有 `CONFIRMED` 事件可改变投影。
- 不暴露“任意 event_type”的通用写入口；具体业务 adapter 负责业务门禁。
- 文书、工作包、任务、费用模块不得直接写三个投影或旧 `Case.status`。

`resolve_document_semantics()` 保留为内部 adapter，但应输出明确的 `lifecycle_event_type`，不再以 `case_status_effect` 直接赋值。

### 6.2 文件证据模块（Document evidence）

Seam：附件进入案件后，统一管理角色、版本、派生、当前有效、最终递交和回执关联。

```text
register_evidence_version(command, transaction) -> EvidenceVersion
prepare_oa_reply(command, transaction) -> OaReplyPackageResult
finalize_external_submission(command, transaction) -> SubmissionEvidenceResult
render_customer_letter(command, transaction) -> RenderedLetterResult
```

不变量：

- 二进制和哈希不可覆盖；修改产生新版本。
- 来源和派生必须同案；跨案关系返回 400。
- 每条谱系只有一个当前工作版本；已关联回执的最终递交版本不能普通替换。
- 工作包 manifest 引用证据版本，而不是只有无版本语义的附件。
- OA_OUT 必须通过唯一 OA 工作包原子创建并关联。
- 可复制与不可复制 OA 使用条件组合；整份 PDF 不等于“其他证明文件”。
- 格式函必须产生真实文件、哈希和归档关系；预计路径不等于已生成。

### 6.3 费用义务模块（Fee obligation）

Seam：位于官方事件/通知与现有草单、PayList、支付登记之间。

```text
preview_estimate(case_id, trigger_context) -> FeeEstimate
recognize_obligation(command, transaction) -> FeeObligation
record_client_instruction(obligation_id, instruction, transaction) -> FeeObligation
prepare_draft(obligation_id, transaction) -> DraftLinkResult
record_payment_evidence(obligation_id, payment_evidence, transaction) -> FeeObligation
```

不变量：

- `preview_estimate` 永远只读，不创建义务或草单。
- 真实官文金额、分项和期限优先；差异保留并复核，不静默覆盖。
- 同一来源事件、费种、年度只有一个有效义务；更正通过 supersede。
- 义务、指示、草单、清单、支付和官方凭证分别记录。
- 官费和服务费分别选择版本、分别审批，不共享确认状态。
- 官费费减只接受 `0/0.7/0.85`：本次明确录入或已确认迁移的 `0` 表示不减缴，不要求批准文件；`0.7/0.85` 必须有已确认批准证据和适用范围；缺失、非法或语义不明返回 409。
- 未验证模板只能产生“内部导出”。

现有 `FeeDraft`、`FeeItem`、`PayList`、`GovPayment`、`T_GrantFeeTask` 和 `AnnuityTask` 继续作为下游 adapter/执行载体，不再承担义务真相。

### 6.4 三线同屏读取模块（Lifecycle overlay）

Seam：案件详情读取的唯一三线聚合入口。

```text
read_lifecycle_overlay(case_id, after_sequence, limit, as_of_revision?) -> LifecycleOverlay
```

不变量：

- 一个只读事务产生一个 `lifecycle_revision` 一致快照。
- 三线共享同案 append-only activity sequence。每条 activity 带 `lane=LIFECYCLE|DOCUMENT|FEE`；只有白名单 `LIFECYCLE` 事件允许非空 `center_changes`。
- 文件版本、客户指示、草单、PayList、支付和格式函等 lane-only 变化也必须产生独立 activity，并以 `center_changes={}` 进入 milestone；不能只挂在最初来源事件的当前汇总下。
- 三线通过 activity ID、来源 activity ID 和证据链接关联，不按标题或日期猜测。
- 前端不得分别读取多个截断列表自行拼接。
- 历史使用共享 activity sequence 的 keyset 分页；无固定 20/50 条全量假象。
- 读取模块无写副作用。

## 7. 三轴状态和事件合同（Lifecycle contracts）

### 7.1 最小状态词汇

| 维度 | 状态 |
| --- | --- |
| 事务所业务阶段 | `NEW_CASE`、`FILING_PREPARATION`、`WAITING_EXTERNAL_RECEIPT`、`PROSECUTION_MANAGEMENT`、`OA_REPLY_IN_PROGRESS`、`GRANT_REGISTRATION_IN_PROGRESS`、`POST_GRANT_MAINTENANCE`、`CLOSED` |
| 官方程序阶段 | `NOT_SUBMITTED`、`SUBMITTED_WAITING_RECEIPT`、`SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE`、`ACCEPTED`、`PRELIMINARY_EXAMINATION`、`RECTIFICATION_RESPONSE`、`PUBLISHED`、`SUBSTANTIVE_EXAMINATION`、`OFFICE_ACTION_RESPONSE`、`REEXAMINATION`、`GRANT_REGISTRATION`、`GRANT_ANNOUNCED`、`PROCEDURE_CLOSED` |
| 权利法律状态 | `NOT_ESTABLISHED`、`APPLICATION_PENDING`、`APPLICATION_REJECTED`、`APPLICATION_WITHDRAWN`、`APPLICATION_ABANDONED`、`PATENT_IN_FORCE`、`PATENT_TERMINATED`、`PATENT_EXPIRED`、`PATENT_INVALIDATED`、`UNKNOWN` |

OA 次数是事件属性 `oa_sequence`，不是权利法律状态。

### 7.2 最小事件矩阵

| Activity | Lane | 必需证据 | 允许作用 |
| --- | --- | --- | --- |
| `CASE_OPENED` | `LIFECYCLE` | 案件记录 | 初始化三投影 |
| `FILING_PREPARATION_STARTED` | `LIFECYCLE` | filing 工作包 | 只改业务阶段 |
| `FILING_EXTERNAL_SUBMISSION_RECORDED` | `LIFECYCLE` | 同案最终递交版本、人工外部提交记录 | 业务进入等待外部回执；官方进入已提交待回执；法律保持未建立 |
| `FILING_RECEIPT_ARCHIVED` | `LIFECYCLE` | 同案最终递交版本和有效回执 | 业务进入审查管理；官方进入已确认提交待受理；法律进入申请待审 |
| `ACCEPTANCE_NOTICE_RECORDED` | `LIFECYCLE` | 可执行受理通知 | 官方进入受理 |
| `PRELIMINARY_EXAMINATION_STARTED` | `LIFECYCLE` | 已确认初审来源或受控程序事件 | 官方进入初步审查 |
| `PRELIMINARY_EXAMINATION_PASSED` | `LIFECYCLE` | 初审合格官方证据 | 官方保持初审阶段，并为 legacy 投影记录“初审合格”事件 |
| `RECTIFICATION_NOTICE_RECORDED` | `LIFECYCLE` | 可执行补正通知及确认期限 | 业务进入答复处理中；官方进入补正答复；法律不变 |
| `PUBLICATION_NOTICE_RECORDED` | `LIFECYCLE` | 公布通知或受控公告证据 | 官方进入公布；法律保持申请待审 |
| `SUBSTANTIVE_EXAMINATION_STARTED` | `LIFECYCLE` | 进入实审通知或受控程序证据 | 业务进入审查管理；官方进入实质审查 |
| `OA_NOTICE_RECORDED` | `LIFECYCLE` | 可执行 OA 来文及确认期限 | 业务进入 OA 答复；官方进入 OA 答复期；法律不变 |
| `OA_REPLY_PREPARED` | `DOCUMENT` | OA 工作包及 OA_OUT | 只记录文件/工作包事实，`center_changes={}` |
| `OA_RECEIPT_ARCHIVED` | `LIFECYCLE` | 同案、同源、完整回执 | 关闭唯一 OA 任务；业务回审查管理；官方回实审 |
| `REEXAMINATION_STARTED` | `LIFECYCLE` | 复审受理或可执行复审来源 | 可从申请驳回或申请待审进入；业务进入审查管理，官方进入复审；若原为申请驳回，法律恢复为申请待审 |
| `GRANT_REGISTRATION_NOTICE_RECORDED` | `LIFECYCLE` | 授权/办理登记通知及确认期限 | 业务进入授权办理；官方进入授权登记；法律保持申请待审 |
| `GRANT_ANNOUNCEMENT_CONFIRMED` | `LIFECYCLE` | 受控公告来源、公告日及所需复核 | 业务进入授权后维护；官方进入授权公告；法律进入 `PATENT_IN_FORCE` |
| `CERTIFICATE_ARCHIVED` | `DOCUMENT` | 专利证书 | 只增加凭证，`center_changes={}`，不改变生效日 |
| `PATENT_REGISTER_STATUS_CONFIRMED` | `LIFECYCLE` | 受控登记簿证据 | 只记录与当前法律状态一致的核验或冲突；发生终止、届满、无效、恢复等变化时必须分派到下列具体事件 |
| `APPLICATION_REJECTION_CONFIRMED` | `LIFECYCLE` | 驳回决定或受控复审终局证据 | 仅允许从申请待审进入业务关闭、程序关闭和申请驳回 |
| `APPLICATION_WITHDRAWAL_CONFIRMED` | `LIFECYCLE` | 撤回请求及官方确认/登记 | 仅允许从未授权申请进入业务关闭、程序关闭和申请撤回 |
| `APPLICATION_ABANDONMENT_CONFIRMED` | `LIFECYCLE` | 视为放弃/放弃取得权利的官方证据 | 仅允许从未授权申请进入业务关闭、程序关闭和申请放弃 |
| `PATENT_TERMINATION_CONFIRMED` | `LIFECYCLE` | 终止通知或登记簿证据 | 仅允许从专利有效进入业务关闭、程序关闭和专利终止 |
| `PATENT_EXPIRY_CONFIRMED` | `LIFECYCLE` | 期限届满及登记簿证据 | 仅允许从专利有效进入业务关闭、程序关闭和期限届满 |
| `PATENT_INVALIDATION_CONFIRMED` | `LIFECYCLE` | 生效无效决定及登记簿证据 | 仅允许从专利有效进入业务关闭、程序关闭和专利无效 |
| `APPLICATION_RIGHT_RESTORATION_CONFIRMED` | `LIFECYCLE` | 官方恢复权利决定 | 仅允许从申请放弃恢复为申请待审；业务/程序按恢复证据指定的阶段重建 |
| `PATENT_RIGHT_RESTORATION_CONFIRMED` | `LIFECYCLE` | 官方恢复权利决定及登记簿证据 | 仅允许从专利终止恢复为专利有效、授权后维护和授权公告阶段 |

`FEE_OBLIGATION_RECOGNIZED`、`FEE_DRAFT_CREATED`、`PAY_LIST_EXPORTED`、`PAYMENT_RECORDED` 和 `GRANT_FEE_TASK_DONE` 是 `FEE` lane activity，但明确不属于中央状态转换事件，必须携带 `center_changes={}`。

所有模块通过内部 `append_case_activity()` 写同案共享单调序号。Activity 至少保存 lane、类型、发生/生效/记录时间、条件性的旧/新三投影、确认状态、操作者、复核者、幂等键、更正来源和 JSON 文本快照。证据链接保存类型、对象引用、内容哈希、采集时间，并强制同案。`(case_id, sequence)` 与 `(case_id, idempotency_key)` 必须唯一；序号分配、activity、证据链接、三投影、兼容 `Case.status` 和 `lifecycle_revision` 更新必须在同一事务内完成。

### 7.3 LegacyCaseStatusProjection 单向兼容合同

`Case.status` 只能由一个纯 `LegacyCaseStatusProjection` adapter 从已确认三轴状态、最新确认的生命周期事件和 `oa_sequence` 派生。新业务门禁只读取三轴/事件，不读取旧状态；旧状态绝不反向驱动三轴。

映射按下表从上到下取第一个匹配项：

| 已确认条件 | 兼容 `Case.status` |
| --- | --- |
| 法律=`PATENT_INVALIDATED` | `INVALIDATED` |
| 法律=`PATENT_TERMINATED` | `TERMINATED` |
| 法律=`PATENT_EXPIRED` | `EXPIRED` |
| 法律=`PATENT_IN_FORCE` | `GRANTED` |
| 法律=`APPLICATION_REJECTED` | `REJECTED` |
| 法律=`APPLICATION_WITHDRAWN` | `WITHDRAWN` |
| 法律=`APPLICATION_ABANDONED` | `ABANDONED` |
| 官方=`GRANT_REGISTRATION` | `GRANT_PENDING` |
| 官方=`REEXAMINATION` | `REEXAM` |
| 官方=`OFFICE_ACTION_RESPONSE` 且 `oa_sequence=1` | `OA1` |
| 官方=`OFFICE_ACTION_RESPONSE` 且 `oa_sequence>=2` | `OA2` |
| 官方=`RECTIFICATION_RESPONSE` | `AMENDMENT` |
| 官方=`SUBSTANTIVE_EXAMINATION` | `SUB_EXAM` |
| 官方=`PUBLISHED` | `PUBLISHED` |
| 最新确认的生命周期事件=`PRELIMINARY_EXAMINATION_PASSED` | `PRELIM_PASS` |
| 官方=`PRELIMINARY_EXAMINATION` | `PRELIM_EXAM` |
| 官方=`ACCEPTED` | `ACCEPTED` |
| 官方=`SUBMITTED_WAITING_RECEIPT` 或 `SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE` | `WAITING_RECEIPT` |
| 法律=`APPLICATION_PENDING` 且没有更具体官方阶段 | `PENDING` |
| 官方=`NOT_SUBMITTED` | `NOT_FILED` |

优先级是：已确认法律终局/专利有效 > 授权/复审/OA/补正 > 其他官方阶段 > 申请待审 fallback。`UNKNOWN`、三轴冲突或 `lifecycle_verification_status != CONFIRMED` 时，adapter 不覆盖原存量 `Case.status`，把差异写入 `legacy_conflicts`；任何依赖准确状态的新写动作返回 409。只有一次性 `LEGACY_IMPORT` 可从旧状态生成未核验导入事件。

## 8. 文件、OA、XML 与格式函合同（Document evidence）

### 8.1 文件角色

至少区分：

1. 内部完整确认 Word；
2. 保留修订痕迹的修订 Word；
3. 从指定 Word 拆出的申请文件组成项；
4. 外部转换形成的 XML 或压缩包；
5. 官方页面识别后的递交清单；
6. 官方页面形成的最终 PDF；
7. 实际递交 XML；
8. 官方提交/接收回执；
9. 给客户的格式函 Word。

每个版本保存哈希、格式、大小、来源版本、派生规则、替代关系、当前/最终标志、工作包、制作/复核人与时间。证据角色不同，即使哈希相同也不能互换。

### 8.2 初始申请链

```text
完整确认 Word
  → 按客户规则去除摘要附图的转换输入
  → XML 压缩包
  → 官方系统识别分配
  → 官方最终 PDF / 实际 XML
  → 回执
```

FPMS 只保存转换前后文件、manifest、哈希和证据关系；不声称自行生成或解析真实可提交 XML。

### 8.3 OA/补正链

- 修改从指定确认稿产生修订稿并保留痕迹。
- 只拆分实际修改的摘要、权利要求书、说明书、附图等组成项。
- 修改对照页、结构化申请文件和意见陈述附件使用独立角色。
- 可复制分支可把正文进入官方意见陈述。
- 不可复制分支保存整份内部 PDF，再抽取“意见陈述书附页”；只有附页作为“其他证明文件”。
- 缺少 PDF→附页派生、附件角色错误或跨案文件时，不能进入“可提交”。

时间语义至少拆成：内部答复创建、工作包准备完成、人工外部提交记录、官方回执确认、OA 正式闭环。创建 OA_OUT 只记录内部准备，并原子关联工作包；回执才形成正式闭环。

### 8.4 格式函

- 从最新且明确的 IN 官方来文产生，而不是任意 OUT 文书。
- 使用 8 个客户确认映射及“模板族 + 变体/字段规则 + 来源官文 + 模板版本”。
- 不涉及答复/缴费期限，且无需添加其他特殊信息的官文，可复用初审模板并替换文件名称和醒目标头。
- 授权通知函与专利证书函是不同节点。
- 授权函金额和期限取自具体通知；OA/复审期限取结构化官文期限，不硬编码。
- 默认称谓为“尊敬的：您好”；存在明确选择的信函联系人时，使用联系人姓名和称谓。
- 输出名遵循 `{内部案号}-给{申请人名称}的邮件`。
- 渲染后的真实 Word 作为新证据版本归档；系统不声称已经自动发送邮件。

## 9. 费用义务、费减、费率和缴费文件合同（Fee obligation）

### 9.1 费用状态分层

一个费用节点至少分别显示：

1. `estimate_status`：预计；
2. `obligation_status`：真实义务；
3. `client_instruction_status`：客户指示；
4. `draft_status`：内部草单；
5. `pay_list_status`：官费清单；
6. `payment_status`：实际支付；
7. `official_evidence_status`：官方凭证核验。

任一状态不得自动推断下一状态。

### 9.2 申请费与授权当年年费

- 申请费估算可以存在，但实际义务来自核对后的缴费通知。
- 通知值与费率候选不一致时保留双方和差异，进入复核。
- 授权通知形成授权登记待办；办理登记通知中的授权当年年费逐项形成义务。
- 不建立固定“年登印费”合并费码，不自行添加通知书未列项目。
- 草单生成时点由 `DG-FEE-APPLICATION-DRAFT`、`DG-FEE-GRANT-YEAR-DRAFT` 控制；未确认时等待 `PAY`。

### 9.3 费减与年费滞纳金

- 显式 `0` 可直接表示不减缴；`0.7/0.85` 必须同时具有已确认批准证据和适用范围。
- 可费减费种、年度和有效期从批准证据读取。
- 年费滞纳金基数是未减缴全额年费；首月 0%，随后为 5%/10%/15%/20%/25%；具体通知的日期段和金额优先。
- `标准费率.XLS` 中的 25% 行仅是最高档参考，不是完整算法。
- PCT 国际阶段、国家阶段专项费、法定免缴和国内规则费种分别判断；代收项目必须版本化。国家知识产权局作为受理局并进行国际检索时，国家阶段申请费及申请附加费免缴；国家知识产权局作出国际检索报告或专利性国际初步报告时，国家阶段实审费免缴；复审费、年费逐费种适用国内费减规则。

### 9.4 官费与服务费分域

| 官费 | 服务费 |
| --- | --- |
| 法定应付 | 客户应收 |
| 官方来源和生效版本 | 客户批准价格版本 |
| 官文、期限、付款凭证 | 服务项目、税、折扣、审批、开票和收款 |
| 不被服务费表覆盖 | 不从官费自动推导 |

集成电路布图设计 7 项和期限补偿 2 项已有 seed，但在来源审批、版本激活和触发闭环完成前不得简单启用。官费 rate book 必须保留下列当前官方规则及来源版本：

| 费种 | 当前金额/规则 |
| --- | --- |
| 布图设计登记费 | 1000 元 |
| 布图设计登记复审请求费 | 1000 元 |
| 恢复布图设计登记权利请求费 | 500 元 |
| 布图设计著录事项变更手续费 | 50 元 |
| 布图设计延长期限请求费 | 150 元 |
| 非自愿许可使用布图设计请求费 | 150 元 |
| 非自愿许可使用布图设计支付报酬裁决费 | 150 元 |
| 专利权期限补偿请求费 | 每件 200 元 |
| 专利权补偿期年费 | 每件每年 8000 元，不足一年不收 |
| 开放许可实施期间年费 | 减免 15%；与其他减免取最优惠，不得叠加 |

### 9.5 内部清单与官方工作簿

两个真实 adapter 位于同一导出 seam：

- `InternalPayListWorkbookAdapter`：生成内部普通清单；
- `VerifiedOfficialPaymentWorkbookAdapter`：只填充经验证的清洁 `.xlsm`。

当前客户样例的工作簿身份是：可见表 `网上缴费`；隐藏表 `Sheet2`、`sheet1`。可见表 9 个字段顺序固定为：

1. 序号；
2. 申请号/专利号/国际申请号/海牙转交编号；
3. 业务类型；
4. 票据抬头；
5. 统一社会信用代码；
6. 费用种类；
7. 外币金额；
8. 费用金额（人民币）；
9. 备注。

官方 adapter 必须保留上述工作表名称和顺序、9 字段顺序、隐藏字典、验证和 VBA 宏部件；服务端不得执行宏。当前样例含示例/残留值，只是参考载体；未通过 `DG-PAYMENT-WORKBOOK` 取得清洁当前版本和受控上传证明时，adapter 不可用并返回 409。

内部导出、官方工作簿生成、官方页面接受、实际支付和票据核验是五个不同事实。普通内部导出不得直接把清单标为官方 `EXPORTED`。

## 10. 三线读取合同（Lifecycle overlay）

读取结果至少包含：

```text
case_id
lifecycle_revision
generated_at
center_snapshot:
  business_stage
  official_procedure_stage
  legal_status
  effective_at
  verification_status
  source_event_id
milestones[]:
  sequence
  activity_id
  lane
  activity_type
  source_activity_id
  effective_at
  center_changes
  document_evidence[]
  work_packages[]
  tasks[]
  fee_obligations[]
  evidence_summary
  warnings[]
decision_gates[]
legacy_conflicts[]
next_cursor
has_more
```

文件节点直接返回角色、谱系、版本、当前/最终、来源/派生、工作包、递交、回执及缺失门禁。

费用节点直接返回来源事件/文书、期限、标准金额、费减、应缴金额、指示、草单、清单、支付、凭证和 `fee_domain=GOV|SERVICE`。

前端以 `milestones` 为行，中央渲染案件生命周期，两侧渲染文件与费用。`demo-lifecycle-spec2-overlay-v3.html` 仅作布局参考，不复用其状态推导。

建议 HTTP adapter 为 bodyless `GET /cases/{case_id}/lifecycle-overlay`。读取完整案件信息时要求 `Case.Read`、`Doc.Read`、`Task.Read`、`Fee.Read` 作为函数参数权限依赖；若未来需要部分可见性，应另行冻结政策，不能静默裁剪并称为完整快照。

## 11. Schema 与 Migration

### 11.1 生命周期

在 `t_case` 增加可空兼容列：

- `business_stage`
- `official_procedure_stage`
- `legal_status`
- `lifecycle_revision`（同案每次提交任何 lane activity 均递增，用作 overlay 快照 revision）
- `lifecycle_verification_status`

新建：

- `t_case_activity_event`
- `t_case_activity_event_evidence`

`t_case_activity_event` 是三线唯一 append-only 历史，至少包含同案唯一单调 `sequence`、`lane`、`activity_type`、`source_activity_id`、发生/生效/记录时间、确认状态、条件性的旧/新三投影、操作者、复核者、幂等键、更正来源和 JSON 文本快照。`(case_id, sequence)` 与 `(case_id, idempotency_key)` 必须唯一。只有 `lane=LIFECYCLE` 且事件在白名单内时允许非空中央状态变化；`DOCUMENT` 和 `FEE` activity 的 `center_changes` 必须为空。三个模块都调用同一个内部 append seam，不得另建文件历史或费用历史来驱动 overlay。序号分配、activity、证据链接、三投影、兼容 `Case.status` 和 revision 更新必须同事务。

保留 `t_case.status` 作为兼容投影；切换后只能由生命周期模块同步写，案件编辑和其他模块不能直接写。

### 11.2 文件证据

新建：

- `t_document_evidence_version`
- `t_document_evidence_derivation`

版本表引用现有附件，保存 `lineage_key`、角色、版本号、状态、当前唯一身份、复核状态和最终递交时间。工作包 manifest 增加可空 `evidence_version_id`，兼容期保留 `attachment_id`。

### 11.3 费用

新建或扩展为明确的独立 carrier：

- `t_fee_obligation`
- `t_fee_obligation_line`
- `t_fee_reduction_approval`
- 官费 `t_fee_rate_book`
- 服务费 `t_service_price_book`
- `t_fee_obligation_draft_item_link`
- `t_fee_obligation_payment_evidence_link`
- `t_pay_list_export_artifact`

现有 FeeRate 可关联官费 rate book；服务费不得复用官费来源审批。授权/年费任务仅引用义务，不把任务金额反向确认为义务。

### 11.4 旧数据迁移

1. 新增结构，不删除旧列或历史。
2. 运行只读预检，输出冲突清单。
3. 可确定项用 `LEGACY_IMPORT` 事件回填，并标 `LEGACY_UNVERIFIED`。
4. 旧 `GRANTED` 不得直接回填 `PATENT_IN_FORCE`，因为历史可能来自错误捷径。
5. 旧附件建立未核验版本；角色冲突不猜当前版本。
6. 旧授权来源/期限谱系保留，但不自动确认法律状态或费用义务。
7. 旧草单、清单和支付保留为财务历史；只有同案、同源、同费种明确时才关联义务。
8. `NONE/PARTIAL/FULL` 仅在申请人构成和客户来源能共同确认时映射；否则标记 `NEEDS_CONFIRMATION`。
9. 已明确表示“不减缴”的 `0` 可确认为 `NO_REDUCTION`；`0.7/0.85` 缺批准来源或适用范围时保持待核验；缺失、非法字符串或语义不明不得迁移成 `0`。
10. 双读对账通过后切换新写入口，最后禁用旧写入口。

所有 Alembic migration 前向执行、SQLite 兼容，基于执行时唯一 head 串行创建。

## 12. 必须替换而非叠加的旧行为

1. 文书、回执、授权任务和案件编辑对混合 `Case.status` 的直接业务写入，统一改走生命周期事件模块。
2. 所有兼容 `Case.status` 写入统一改由单向 `LegacyCaseStatusProjection` 产生；旧状态不得反向驱动三轴。
3. `case_status_effect` 从直接赋值改为事件解析 adapter。
4. 删除授权通知附件上传推进 `GRANTED` 的副作用。
5. 删除授权费 `mark_done → GRANTED` 的副作用。
6. 替换“创建 OA_OUT 即把来源 `reply_date` 显示为 REPLIED”的语义；正式回复完成来自有效回执。
7. 文件 readiness 改由证据版本计算，不在扁平附件摘要上再叠一套版本状态。
8. OA 固定 Word/PDF 组合和整份 PDF=其他证明文件的规则，改为条件附件策略。
9. `CaseFeesTab` 固定 `FILING_ACCEPTED` 请求改为真实义务；估算单独显示。
10. 停止费减静默默认、夹取和实际义务的 `NO_SOURCE` 路径。
11. 授权/年费任务从确认义务生成草单，不再按任务或费率猜义务。
12. 下载普通 `.xlsx` 不再直接产生官方 `EXPORTED` 状态。
13. 格式函从“预计路径/READY”改为真实模板版本、实际渲染、哈希和归档。
14. 三线历史统一追加到同案 activity ledger；文件或费用模块不得以自己的列表代替 overlay 历史。

## 13. 错误、权限、SQLite 与 UI 约束

### 13.1 错误语义

- 400：同案关系错误、合法字段组合不成立、业务动作不允许。
- 404：案件、事件、证据、义务或来源不存在。
- 409：证据未确认、决策门未解决、旧数据待核验、状态/唯一键冲突、配置/模板/费率未激活、同幂等键载荷冲突。
- 422：请求结构、日期、枚举或金额格式错误。
- 401/403：认证和权限。

任一必要副作用失败，文件、任务、费用和状态全部回滚。创建资源返回 201；读取、动作和幂等复用返回 200；GET 无请求体；204 无响应体和 response model。

### 13.2 权限

- 不新增可任意改变状态的案件编辑入口。
- 自动事件继承发起业务入口权限并记录 actor。
- 授权人工确认在客户明确岗位和双人复核前保持禁用。
- 所有权限使用函数参数形式 `Depends(require_perm(...))`。

### 13.3 SQLite

- UUID 由应用生成并存 `String(36)`；自增仅用 Integer PK。
- 默认时间使用 `CURRENT_TIMESTAMP`。
- JSON 快照存 Text；禁止 JSONB、ARRAY、PG 函数和 correctness 依赖 RETURNING。
- 插入后 `flush()`；外键保持开启。
- 唯一幂等键和可空当前身份承担并发约束；冲突后重读。
- 写事务短小，所有写 SQLite 测试串行。
- overlay 在一个只读事务中读取一致 revision。

### 13.4 简体中文 UI

所有页面标题、按钮、字段、状态、警告、空态和错误提示使用简体中文。英文仅用于内部技术码、ID、枚举和日志。

中央主线必须视觉居中；文件与费用同时出现，不再互斥于不同 Tab。未核验、客户待确认、来源冲突和仅供参考必须明确显示，不能隐藏为“暂无数据”。

## 14. Execution waves

### Wave 0：计划门与逐项对账

- 建立初始 V8 item-to-slice ledger。
- 冻结状态事件、文件角色/派生、费用义务状态机和 decision gate 记录。
- 引用 Tasks 01–70 证据，不重复广泛来源分析。
- 客户澄清并行进行；未回复只门控对应 lane。

### Wave 1：Schema spine，完全串行

下列每一行是一个依赖段，不是一个可直接实施的“大任务”。下一实施计划必须把每一行分别冻结为一个 exact task file 和一个 migration closure，并严格按顺序串行：

| 顺序 | 依赖段 | 精确 carrier closure |
| --- | --- | --- |
| `W1-L1` | 生命周期投影 | 只增加 `t_case` 三轴、revision 和核验状态兼容列 |
| `W1-L2` | 共享活动账本 | 只增加 `t_case_activity_event` 及同案 sequence/idempotency 约束；依赖 `W1-L1` |
| `W1-L3` | 活动证据链接 | 只增加 `t_case_activity_event_evidence` 及同案约束；依赖 `W1-L2` |
| `W1-D1` | 文件证据版本 | 只增加 `t_document_evidence_version`；依赖 `W1-L2` |
| `W1-D2` | 文件派生关系 | 只增加 `t_document_evidence_derivation`；依赖 `W1-D1` |
| `W1-D3` | 工作包版本链接 | 只为 manifest 增加可空 `evidence_version_id`；依赖 `W1-D1` |
| `W1-F1` | 费用义务头 | 只增加 `t_fee_obligation`；依赖 `W1-L2` |
| `W1-F2` | 费用义务明细 | 只增加 `t_fee_obligation_line`；依赖 `W1-F1` |
| `W1-F3` | 义务—草单关系 | 只增加 `t_fee_obligation_draft_item_link`；依赖 `W1-F2` |
| `W1-F4` | 义务—支付证据关系 | 只增加 `t_fee_obligation_payment_evidence_link`；依赖 `W1-F2` |
| `W1-F5` | 费减批准 | 只增加 `t_fee_reduction_approval` 及适用范围；依赖 `W1-F1` |

官费 rate book 留到 Wave 4 的官费版本任务，服务费 price book 留到 Wave 6 的客户确认任务，PayList 导出产物 carrier 留到 Wave 5；不得塞入任何 Wave 1 任务。每个 migration 执行前重新检查唯一 head，执行干净 SQLite `upgrade head` 和旧数据预检。不得伪造公告、回执、费用或费减来源。

### Wave 2：三个深模块核心，可并行开发、串行 SQLite 验证

- Lifecycle lane：共享 activity append seam、事件验证、三轴转换和单向兼容投影；涉及同一共享 seam 的任务内部串行。
- Document evidence lane：版本、派生和 manifest 纯模块。
- Fee obligation lane：义务、费减和来源金额规则。

### Wave 3：共享入口集成，按文件串行

1. document semantic effect 接入 lifecycle event；
2. OA_OUT 与唯一 OA package 原子关联；
3. receipt archive 通过生命周期事件承载，同时保留 Tasks 14–17 合同；
4. 删除两条 `GRANTED` 捷径并接入授权公告事件；
5. notice → fee obligation，禁止 notice → generic draft。

### Wave 4：Document 与 Fee 产品 lane

Document lane：完整 Word 门禁、谱系、OA 条件附件、真实格式函。

Fee lane：规范费减、真实通知义务、官费 rate book 版本、费率分类、滞纳金、授权当年年费和后续年费正确性。官费 rate book schema、来源审批/激活和各规则实现仍须拆成独立串行任务。

共享 `seed_dev.py`、接口类型、状态中文映射和同一页面仍需内部串行。

### Wave 5：客户无关的清单边界

先以独立 carrier 任务增加 `t_pay_list_export_artifact`，再实现内部导出与官方产物状态分离。未确认模板时，官方 adapter 保持不可用，但内部清单和人工支付登记继续。

### Wave 6：客户决策 lane

只有收到对应确认材料后，才实施草单策略、授权证据 adapter/人工复核、官方 `.xlsm`、服务费版本、旧表单激活和年费例外。不同且不冲突的 lane 可并行。

### Wave 7：Overlay 与 UI

三个读取合同稳定后，先完成单一 overlay adapter，再实现中央主线和左右两线 UI。前端不复制状态机。

### Wave 8：真实路径与最终关闭

串行完成 migration/seed、后端全量、前端 lint/typecheck/build、真实 UI E2E、逐任务门、最终 ledger 和 release gate。此前不得提前运行最终关闭流程。

## 15. Atomic task standard

下一实施计划中的每个任务必须只有一个可观察行为，并明确：

- 一个 exact task file；
- 一个 closure slice 和明确 non-closure；
- 前置事件、输入证据、同案/同源约束；
- 唯一/幂等键；
- 成功只允许改变的对象、字段、事件和投影；
- 失败必须保持不变的对象；
- 400/404/409/422 语义；
- 旧数据投影与未核验规则；
- 精确 allowlist、共享文件顺序和 remaining follow-up；
- 一个公共 module/interface/HTTP/UI RED 和最小 GREEN；
- 受影响 Tasks 01–70 的定向回归；
- SQLite 测试锁、脏基线、scoped diff、独立复核、证据校验和 task gate。

额外规则：

- 生命周期任务只关闭一个事件或一个投影。
- 文件任务只关闭一种关系、角色、组合或门禁。
- 费用任务只关闭一种义务触发、费率规则或策略。
- UI 任务只关闭一个页面能力，并消费冻结后端合同。
- customer-gated 任务缺确认材料时保持 gated/BLOCKED，不得代选。
- 实施代理不得批准自己的任务。
- 两个任务若共享 migration、schema、router、seed、前端接口、状态词典或页面，必须拆分或分波串行。

## 16. Acceptance

### 16.1 必须覆盖的业务场景

| 领域 | 最小验收 |
| --- | --- |
| 状态 | OA1/OA2 不进入法律状态；授权通知、费用完成不产生 `PATENT_IN_FORCE`；授权公告事件以公告日生效；证书不重复推进；登记簿冲突进入复核；覆盖 `REJECTED → REEXAMINATION_STARTED → APPLICATION_PENDING/REEXAM → 维持驳回或其他受控结果`。 |
| OA | OA_OUT 原子关联唯一 package；任务保持开放；错案/错源/缺回执无副作用；正确回执只关闭一个任务并返回后续程序。 |
| filing | 缺完整 Word、父版本或来源不明 XML 时不可递交就绪；最终 PDF/XML/回执可追溯同一来源。 |
| OA 文件 | 可复制与不可复制分支附件不同；不可复制必须保留完整 PDF→附页关系，仅附页为其他证明文件。 |
| 格式函 | 使用真实模板版本和来源官文，实际生成 Word 可回读；授权函与证书函不混淆。 |
| 费减 | 本次明确录入 `0` 可在无批准文件时表示不减缴；有已确认批准及范围的 900 元申请费按 `0.85` 实缴 135 元；公布印刷费仍全额；`0.7/0.85` 无批准/范围、缺失、非法或语义不明均 409，且不得静默变成 `0`。 |
| 义务 | 真实通知覆盖估算；同源同内容幂等；同源冲突 409；义务、草单、支付分开。 |
| 年费 | 全额年费 1200、减后 180 时，超期首月滞纳金为 0；进入 5% 档时滞纳金为 60 而非 9；随后验证 10%/15%/20%/25% 和六个月边界；通知日期段优先。 |
| PCT | CNIPA 作为受理局并完成国际检索时国家阶段申请费及附加费免缴；具有 CNIPA 国际检索报告或国际初步报告时国家阶段实审费免缴；其他国家阶段费、复审费、年费和国际代收项目逐费种、逐版本判断。 |
| 专项官费 | 布图设计 7 项按 1000/1000/500/50/150/150/150 元校验；期限补偿请求费 200 元、补偿期年费每年 8000 元且不足一年不收；开放许可实施期间年费减免 15%，与其他减免取最优且不叠加。 |
| 服务费 | 缺服务费版本不生成应收，但官费义务继续。 |
| PayList | 普通 `.xlsx` 始终为内部清单；未验证 `.xlsm` 不能生成官方可上传状态；上传不等于支付。 |
| Overlay | 同一 revision 返回中央三状态和两侧关联；长期案件完整游标，不漏历史 OA/费用/证据。 |
| UI | 简体中文、生命周期居中、两线同屏；未核验和门控原因可见。 |

### 16.2 最终 item-to-slice ledger

每行至少包含：

- V8 GAP ID；
- required slices；
- inherited Tasks 01–70 及证据；
- V8 新任务 IDs 与直接证据；
- customer decision gate、来源和状态；
- migration/backfill；
- 定向 regression；
- residual GAP；
- close decision。

代表性 E2E 不能代替逐 slice 证据。Customer-gated 项未解决时不能写 `covered`；只能明确排除当前 batch 或标 `customer-gated`。只有范围内 required slices 全部 PASS、所有范围内 gate 已解决且 residual 为 `None` 时，项目才可 `covered`。

## 17. Non-goals

- 本设计不创建实施计划、batch manifest 或原子实现任务。
- 不修改或重做 V6/V7 历史演示文档及 Tasks 01–70。
- 不生成或解析真实官方 XML。
- 不直接登录、连接、提交国家知识产权局系统。
- 不实现签名、二维码、RPA、自动回执下载或自动缴费。
- 不执行客户工作簿宏。
- 不自动发送客户邮件。
- 不替客户决定草单、服务费、模板版本或授权人工复核政策。
- 不以天悦网页或客户旧 Excel 直接激活官费。
- 不把旧 `.DOC` 自动认定为现行官方表单。
- 不扩大为全部 60 项官文、完整 PCT/海牙/布图设计自动化。
- 不把静态 HTML、任务完成、内部草单、清单导出或付款登记当作法律状态来源。

## 18. 下一步进入实施计划的条件

只有以下条件全部满足，才可调用 writing-plans 形成实施计划：

1. 本 V8 设计通过独立设计审查和任务门。
2. 建立初始 V8 item-to-slice ledger，并对 Tasks 01–70 完成证据引用而非重做。
3. Wave 1 的 `W1-L1` 至 `W1-F5` 每个依赖段被拆成独立任务和串行 migration 顺序；官费 rate book、服务费 price book 和 PayList 导出产物不被提前塞入 Wave 1。
4. 每个 customer gate 标明已确认、当前 batch 排除或明确 gated；不得静默采用默认业务政策。
5. 计划记录本设计的 Story Shape Classification 和 `P0-prereq-heavy-story`。
6. 每个执行代理只有一个 exact task file、一个 allowlist 和一个 closure slice。

本设计通过后，下一份文档应为 `PD-POSTDEMO-V8-MITIGATION-IMPLEMENTATION-PLAN-20260712-01`；不得从 V7 脚本直接跳到实现。
