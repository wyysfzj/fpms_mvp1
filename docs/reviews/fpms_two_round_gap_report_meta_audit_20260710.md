# FPMS 两轮 Gap Review 独立复核与 Meta-Audit

日期：2026-07-10  
任务：`FPMS-TWO-ROUND-GAP-REPORT-META-AUDIT-20260710-01`  
复核对象：

- 第一轮：`docs/reviews/fpms_gap_analysis_report_20260708.md`
- 第二轮：`docs/reviews/fpms_gap_analysis_report_v2_20260709.md`

复核角色：主线程，按中国专利代理机构解决方案架构与专利流程业务双视角执行。本文是独立审计，不修改两轮报告及其产品实现。

## 1. 审计结论

### 1.1 总体结论

两轮报告有较高的问题发现价值，也确实补到了若干 demo 可见缺口；但它们目前只能作为**工程工作记录和候选差距清单**，不能作为以下任一结论的验收依据：

- 不能作为 `AGENTS.md` 意义上的原子任务或批次 `PASS` 证据；
- 不能证明 P1 国内专利主线已经达到生产级可信闭环；
- 不能证明信函、官费、缴费、时限和文书导出已经满足事务所正式运营要求；
- 不能直接作为合并当前脏工作树的批准文件。

建议处置：**有条件接受两轮报告中的问题发现，不接受其批量修复闭环和生产就绪声明。** 当前实现应保持在待拆分、待复核状态，按独立原子任务重新验收。

### 1.2 分轮评价

| 复核对象 | 问题发现价值 | 业务结论可信度 | 实施闭环可信度 | `AGENTS.md` 合规 | 处置 |
|---|---:|---:|---:|---:|---|
| 第一轮 2026-07-08 | 中高 | 中 | 低 | 不通过 | 可保留为 working report；不得视为 PASS |
| 第二轮 2026-07-09 | 高 | 中低 | 低 | 不通过 | 可保留差距清单；V2-01..10 必须逐项重验 |

### 1.3 三层就绪度

| 层级 | 判断 | 说明 |
|---|---|---|
| Demo 可见性 | 部分达到 | 案号、费用项目、来源状态、打印/导出按钮、映射 seed 等可见能力增加。 |
| 人工操作闭环 | 部分达到 | 多数外部提交、缴费、回执和信函交接仍依赖人工；部分状态只是内部记录或路径字符串。 |
| 生产级控制闭环 | 未达到 | 真实格式函生成、费率来源 fail-closed、回执内容门禁、override 权限、完整法律状态、官方缴费模板、文档版本链及产品审计仍未闭合。 |

## 2. 审计范围与方法

本次按 `AGENTS.md §0.3` 的证据优先级执行：客户原始材料/截图优先，其次提取文本、P1 FS 与既有 ledger，再其次是当前代码和测试。

实际核对包括：

- 完整读取两轮 gap 报告、2026-07-05 功能正确性审计及整改设计；
- 核对 `docs/FPMS SPEC 2.0.md`、P1 FS、收费场景 gap/触发设计、FR-FE-04 post ledger；
- 核对 `信函生成操作.docx` 与 `相关流程操作-20260526.docx` 的提取文本，并渲染原始 DOCX 页面检查格式函、系统操作和清单截图；
- 核对当前 `HEAD ff3d58b` 上的脏工作树 diff、迁移、后端服务、前端页面和新增测试；
- 串行运行四个相关测试文件，结果为 `38 passed, 3 warnings`。该结果只证明现有测试通过，不证明下面指出的业务语义已被覆盖；
- 未重复运行全仓测试，因为本任务是单一文档审计，不是最终批次 close。

当前两轮报告和相关实现均处于未提交/脏工作树状态。审计将它们视为待验收对象，不把未提交内容视为既成产品基线。

## 3. 关键发现

### 3.1 P0：验收与生产风险

#### MA-01：两轮实施均无原子任务、batch manifest 和必需 evidence，不能认定 PASS

- 第一轮同时修改费用、年费、授权费、申请人主数据测试、多个前端页面和 E2E 断言；第二轮又同时修改迁移、PayList/GovPayment、信函、目录 seed、计费、时限打印、文书导出和 demo cleanup。
- 当前已跟踪 diff 至少涉及 30 个文件、约 `1122` 行新增；另有迁移、新服务文件、模板、测试和两份报告等未跟踪文件。
- 未找到与两份报告对应的一个任务文件、显式 batch manifest、`results.jsonl`、`summary.md`、scoped `git/diff.patch`、脏基线或 task gate。
- 这直接违反 `AGENTS.md §1`、`§1.1`、`§11`、`§12`、`§13`。

影响：测试数字即使真实，也无法证明每个 closure slice 的允许文件、前置条件、共享文件串行、non-closure 和残余 gap 均被遵守。

处置：两轮报告的修复状态应从“本轮修复/通过”降级为“待原子化验收”。

#### MA-02：V2-01/02/03 未解除 Phase 3 BLOCKED 状态即实施 schema 和 API 扩展

- `tasks/fr-fe-04/blocked/FRFE04-BLOCK-01.md` 和 `BLOCK-02.md` 明确写明 `Status: BLOCKED`，原因是 Phase 3 禁止 schema/migration；`BLOCK-03` 又依赖前两项。
- `docs/FRMS_SPEC2_2nd_POST.md:20-36` 只是登记 approved blocked follow-up，并没有批准在当前 Phase 3 直接实施。
- 第二轮把三项合并为一个迁移、模型、API、service 和测试变更，没有新的阶段授权、任务状态变更或一任务一闭环证据。
- 新迁移 `backend/alembic/versions/frfe04_paylist_govpayment_struct.py` 还使用 `PRAGMA table_info`；这虽然能在 SQLite 工作，但属于方言专用 SQL，与 `AGENTS.md §8.4` 的方言无关约束不一致。

影响：属于范围和治理上的 acceptance blocker；不能用“迁移能跑”替代“任务已获授权”。

处置：在重新分类阶段、更新三个独立 task 文件并生成各自 evidence 前，不接受 V2-01/02/03 为已闭环。

#### BIZ-01：格式函 `READY` 是假阳性；当前没有真正生成可交付 Word

- 客户原始格式函截图显示正式函至少包含称谓、我方案号/对方案号、官文名称、申请号、申请日、申请人、登记期限/金额、附件说明及事务所落款；提取文本还要求按官文匹配、生成 Word、命名并交给龙虾系统。
- V2 新建的 8 个模板只是标题、称谓、案号、申请号和一句通用提示：`backend/scripts/seed_dev.py:1380-1391`。
- `get_letter_handoff_preview` 只在模板记录 enabled 时把 `template_status` 设为 `READY`，并拼接 `letters/...docx` 路径：`backend/app/modules/official_workflows/service.py:1680-1716`。
- `prepare_letter_handoff` 只保存该路径和 payload：`official_workflows/service.py:1788-1833`；未调用仓库已有 `DocxTemplate` renderer，也未创建输出文件。
- 第二轮实测只证明路径字符串命名正确和模板记录可匹配：`fpms_gap_analysis_report_v2_20260709.md:90-93`，没有证明输出文件存在、内容正确、可打开或格式一致。
- P1 FS `§11.3-5` 和 final review ledger 已明确把真实格式函 DOCX 样例列为待确认。

影响：用户可能看到“READY/已生成附件”，实际文件不存在或内容不满足客户正式信函要求；这是客户沟通、期限提示和职业责任风险。

处置：在真实模板、渲染、文件落盘、附件归档和视觉验收完成前，应显示 `PENDING_TEMPLATE` 或等价阻塞状态，不得声明 READY。

#### FEE-01：费率来源门禁是 denylist，不是事务所官费应有的 fail-closed

- 第一轮新增 `fee_rate_source_enabled_condition`，允许 `source_status IS NULL` 及任何不在 `PENDING_CONFIRMATION/PENDING/DISABLED` 中的字符串：`backend/app/modules/fees/service.py:647-655`。
- `FeeRateCreateIn/UpdateIn` 的 `source_status` 仍是自由字符串：`backend/app/modules/fees/schemas.py:211-263`。
- 因此空值、拼写错误或未来未知状态仍可参与自动预览/草单；第一轮只测试了精确值 `PENDING_CONFIRMATION`。
- 收费 gap review `GAP-MODEL-002` 已指出自由字符串、状态迁移和启用门禁同时缺失；第一轮只关闭了其中一个窄分支。

影响：官费金额属于高风险财务/法务数据。来源不明确的费率不应通过“未命中禁止词”获得执行资格。

处置：自动计算应默认只允许明确 `CONFIRMED` 且在生效期内的费率；历史空值需要独立迁移/人工确认策略，不能静默放行。

### 3.2 P1：业务语义和范围误判

#### BIZ-02：国内客户映射被全局启用，联系人规则也仍未确认

- 客户源写的是“国内客户天下先格式函对应官文”：`信函生成操作` P0007。
- 新 seed 将 8 条映射全部全局 `enabled=True`；`_find_letter_mapping` 只按文书模板/代码/标题打分，没有客户国内/境外属性过滤：`official_workflows/service.py:1476-1513`。
- seed 同时固定 `contact_rule_code=CLIENT_PRIMARY_CONTACT`，而 P1 FS `§11.7-1` 明确要求确认旧系统“标为客户”是否等同 `ClientContact.is_primary`。

影响：涉外客户或外方代理案件可能错误套用国内客户格式函；称谓来源也可能选错。

处置：映射必须带客户类型/业务方向适用条件；联系人来源和称谓规则确认前保持人工选择。

#### BIZ-03：22 项“致函官方”目录被误判为无需客户决策

- 第二轮把 V2-06 列入“可执行、无需客户决策”：`fpms_gap_analysis_report_v2_20260709.md:25-38`。
- P1 FS `§5.3` 明确将“官文代码和致函官方清单是否作为新系统初始化字典”列为待确认：`postdemo_p1_functional_spec_20260531.md:250-255`。
- 客户原文 P0063-P0066 表明这些文件当前只在天下先内部存档，不能直接导入专利业务办理系统；下拉没有合适项时还允许任意选择后改名。
- 当前实现却把 22 项作为全局 enabled `DocTemplate` 稳定目录。

影响：把旧系统可变的归档候选项误当成新系统稳定业务词典，后续可能错误绑定状态、时限、费用或官方文件角色。

处置：在客户确认前应作为 `候选目录/历史别名`，而不是 enabled 的权威模板目录。

#### FEE-02：V2-08 固化了未经确认的说明书页数口径

- 第一轮将 `GAP-CALC-003` 保持 open，原因是页数口径待客户确认：`fpms_gap_analysis_report_20260708.md:105`。
- 第二轮却把 PER_PAGE 列为“无需客户决策”，并直接采用 `spec_pages + draw_pages`：`backend/app/modules/fees/service.py:1664-1770`。
- 如果 `spec_pages` 已包含附图页数，该算法会重复计数；若不包含，则还需要确认官方口径、页码基准及空值处理。
- 当前 seed 的相关费率虽 disabled/pending，但通用计算器已经接受该假设；配合自由字符串来源状态，误启用风险不能忽略。

影响：可能直接造成申请附加费金额错误。

处置：保留 disabled；先冻结字段定义和客户/官方口径，再建立独立 PER_PAGE 原子任务。

#### PAY-01：V2-01/02/03 只完成部分结构写入，未闭合 SPEC 的缴费规则

- SPEC 要求 `PayList.Type` 必填，并要求 `Status != PAID` 时不应填写 `ActualPayDate/InvoiceNoFrom/To`：`docs/FPMS SPEC 2.0.md:2563-2581`。
- 新 API 把 `list_type/flow_dir/invoice_no_from/to` 全设为 optional，并允许在历史清单创建时直接填写；普通从费用项生成的清单没有稳定填充 `list_type`。
- SPEC 要求缴费登记时填写发票范围并更新每条 GovPayment 的 paid/voucher/invoice 字段：`FPMS SPEC 2.0.md:7044-7051`。当前发票范围主要在历史清单创建路径写入，缺少与 PAID transition 一致的验证和更新闭环。
- 手工 GovPayment 把 `planned_amt` 直接等同 `paid_amount`，不能表达“计划应缴”和“实际支付”差异。
- 第二轮验证只做 round-trip 和过滤，没有覆盖 V-PL-02、V-PL-03、V-GP-02/03、权限审计或前端可操作性。

影响：数据表“有列”不等于财务/官费业务完整；可能形成不一致或不可审计的已缴记录。

处置：把 schema unblock、领域校验、登记 API、查询和 UI 分开验收；V2-01/02/03 不得整体标为 full close。

#### DL-01：“今日提醒打印”打印的不是页面上同一集合

- 今日提醒页面读取 `/tasks/today`；当前 service 集合是 `due_date == today OR internal_due_date == today`：`backend/app/modules/tasks/service.py:399-423`。
- 新打印按钮却调用通用 `/tasks/print` 并只传 `due_from=today&due_to=today`，该路径只过滤 `Task.due_date`：`frontend/src/modules/tasks/pages/TodayReminders.vue:111-139`、`backend/app/modules/tasks/service.py:121-159`。
- 所以仅内部期限为今天的任务会显示在页面，却不出现在打印清单。
- 更上层的 SPEC 语义还包括 `Remind1/2/3=今日` 和 daily reminder 区间；当前 `/tasks/today` 本身尚未覆盖：`docs/FPMS SPEC 2.0.md:1945-1957`。
- 第二轮实测只检查 HTTP 200 和标题：`fpms_gap_analysis_report_v2_20260709.md:95`。

影响：流程人员打印出的纸质清单可能漏掉当天内部期限/提醒任务，影响期限管理。

处置：打印必须复用“今日提醒”同一查询或同一任务 ID 集合，并覆盖内部期限、提醒日、daily reminder、已完成/取消状态测试。

#### DOC-01：V2-10 是最小 Excel 导出，不是 US-WD-06 / FR-WD-07 全闭环

- 新端点固定 `page_size=1000`，超过 1000 条会静默截断：`backend/app/modules/documents/api.py:365-383`。
- 输出只有 8 列，缺 SPEC 要求的 AppNo、客户、转发日、收/发文登记号、期限和附件状态等字段。
- SPEC 还要求通用清单纵向/横向、证书清单以及 Excel/Word/PDF：`docs/FPMS SPEC 2.0.md:1323-1352`。
- 第二轮测试只验证一个过滤后的 xlsx 可打开：`fpms_gap_analysis_report_v2_20260709.md:96`。

影响：可用于小规模 demo，但不能作为统计、报备或审计清单的完整实现。

处置：将 V2-10 判为 `Partially Implemented`；明确最大行数、完整字段、证书视图和格式边界后再关闭。

#### TRACE-01：授权/年费 deadline preview 被描述为符合设计，实际只完成窄化版本

- 设计 `§6.8` 要求至少返回源对象、`trigger_event`、费用类别/子类、期限、依据、`source_status`、`review_mode` 和中文状态说明。
- 已实现的是 `trigger_rule/deadline_rule/fee_basis/fee_node_explanation` 四个通用字符串；第一轮 open 表只列了 `review_mode`，遗漏 `source_status`、类别/子类及稳定 trigger event 的差距。
- 第一轮 A-1 还把设计 `§6.6/§6.7` 概括为“年费金额由 AnnuityTask 承载，不重算”；原文 `§6.6` 实际讨论 due date 不重算，`§6.7` 要求继续按 FeeRate 年度阶梯选择。真正的 GOV-only 行为来源是独立任务 `PD-FEE-SCENARIO-ANNUITY-GOV-RATE-20260705-01`。

影响：追踪引用不准确，容易把 demo 解释字段误认为完整、稳定、可审计的触发合同。

处置：把当前能力标为 `demo explanation fields`，不要标为收费触发输出合同已完成。

### 3.3 P2：报告质量与方法问题

#### QA-01：内部统计和全量审计表述不严谨

- 第一轮总览写 B 类 5 项，但正文实际有 B-1 至 B-6 共 6 项：`fpms_gap_analysis_report_20260708.md:17-21,46-76`。
- 第二轮声称按 `AGENTS.md` “全量文档索引”核对，但没有 source-by-source coverage ledger，也没有把每个 open 项映射到 required slices/evidence/residual gap。
- 第二轮“22 项历史 gap 已闭环”没有附逐项 ledger，无法独立复算。
- 第二轮第 21 行出现“第一轮агент”混合语言，反映出报告未做最终文字校验。

影响：不一定改变单项技术事实，但削弱“全量”“已闭环”“无残留”等强结论的可信度。

处置：保留具体 file:line finding，撤回无法由 ledger 支撑的总量结论。

## 4. 两轮逐项复核摘要

### 4.1 第一轮可接受部分

- 正确识别 17 个旧测试与新行为的漂移；相关原子任务 evidence 能支持 GOV-only 年费和 deadline preview 的窄 closure。
- `case_no`、费用项目名称、费率来源字段及 `PENDING_CONFIRMATION` 显示问题属于真实前后端缺口。
- UM/DES 申请费补测试、费率生效期和 GRANTED readiness 的既有闭环判断基本有代码/evidence 支撑。

### 4.2 第一轮不能接受为闭环的部分

- 修复跨越多个 closure slice，没有 task/evidence；
- fee source gate 仍 fail-open；
- deadline preview 的设计覆盖被高估；
- open ledger 不完整，不能代表收费、文件和状态全部残差。

### 4.3 第二轮可接受部分

- 正确发现 FR-FE-04 五项 blocked follow-up 仍存在；
- 正确发现 8 行官文到格式函映射和 22 行致函官方候选清单此前未配置；
- 正确发现今日提醒缺打印、文书列表缺导出；
- demo cleanup 外键问题属于明确、可复现的测试基础设施缺陷。

### 4.4 第二轮不能接受为闭环的部分

- 未获授权地实施 blocked schema tasks，并混入多个 endpoint/UI/service closure；
- 把占位模板和路径字符串误判为格式函 READY；
- 把待确认目录、联系人规则和页数口径误判为无需客户决策；
- 将今日提醒打印和文书导出最小能力描述为故事闭合；
- 缺少 per-task evidence 和 batch item-to-slice ledger。

## 5. 业务风险排序

| 排序 | 风险 | 当前状态 | 建议优先级 |
|---:|---|---|---:|
| 1 | 格式函 READY 假阳性、未真正生成 Word | 未闭合 | P0 |
| 2 | 未确认/未知来源费率可能参与自动金额 | 未闭合 | P0 |
| 3 | 回执内容门禁与 override 独立权限（IC-02/03） | 两轮均保持 open | P0 |
| 4 | 说明书页数口径被提前固化 | 未确认 | P0/P1 |
| 5 | PayList/GovPayment 状态、金额和审计语义不完整 | 部分实现 | P1 |
| 6 | 今日提醒页面与打印集合不一致 | 错误实现 | P1 |
| 7 | 国内客户映射/联系人规则被全局启用 | 未确认 | P1 |
| 8 | 文书导出静默截断且字段/格式不完整 | 部分实现 | P1 |
| 9 | 法律状态 transition、文档版本链、产品审计导出 | 两轮均保持 open | P1 |
| 10 | 官方缴费 Excel 模板、外部失败/重试 | 待样例/未闭合 | P1/P2 |

## 6. `AGENTS.md` 合规审计

| 检查项 | 第一轮 | 第二轮 | 判断 |
|---|---:|---:|---|
| 一 agent 一 task file / 单一 closure | FAIL | FAIL | 两轮均是多模块批量修复 |
| Story Shape Classification / chosen runbook | FAIL | FAIL | 报告即执行计划，但未记录 |
| 显式 batch manifest / wave / shared file serialization | FAIL | FAIL | 未提供 |
| task evidence、dirty baseline、scoped diff、task gate | FAIL | FAIL | 未找到对应 artifacts |
| Phase 3 无 schema/migration 变更 | N/A | FAIL | blocked task 未解锁即加迁移 |
| SQLite PoC 兼容 | 未发现新迁移 | PARTIAL | 可运行，但引入 PRAGMA 方言 SQL |
| FastAPI permission 参数注入 | PASS | PASS | 新文书导出使用 `Doc.Read` 参数注入 |
| FastAPI 200/201/204 语义 | 未发现新增冲突 | PASS | 新导出 200 二进制响应一致 |
| 前端可见文本简体中文 | PASS | PASS | 本轮新增 UI 文案为简体中文 |
| 全仓验证可追溯 | FAIL | FAIL | 报告有数字，无对应命令日志/evidence |
| final batch item-to-slice ledger | FAIL | FAIL | 未提供 |

## 7. 处置建议

### 7.1 对当前两轮报告

1. 保留两份文件作为 `DRAFT / WORKING REVIEW`，在标题或结论处明确“不得作为 PASS/生产就绪证明”。
2. 不直接删除其中 findings；每项应转入新的 item-to-slice ledger，状态限定为 `Verified Gap / Partially Implemented / Needs Confirmation / Deferred / Covered`。
3. 撤回“全量文档已核对”“22 项已闭环”“template READY”“V2-09/10 通过即故事闭环”等强表述，直到有对应证据。

### 7.2 对当前脏工作树

1. 不按“两轮报告”整体合并。
2. 先为现有变更建立显式 batch manifest，按共享文件和依赖拆波次。
3. FRFE04-BLOCK-01/02/03 必须先完成阶段授权和任务重写，再分别验收 schema、领域规则/API、查询。
4. 信函至少拆为：映射目录、国内客户适用范围、真实模板导入、DOCX 渲染落盘、附件归档/下载、联系人/称谓规则、视觉验收。
5. 收费至少拆为：source status allowlist、历史空值迁移、PER_PAGE 口径确认与计算、费率计算快照/人工复核。
6. 今日提醒打印和文书导出分别独立成页面能力任务，不与 seed、迁移或收费混合。

### 7.3 待确认

- 客户可否提供 8 种格式函的真实 DOCX 模板和至少一份成功生成样例；
- “国内客户”的系统判定字段，以及涉外/外方代理案件应使用何种信函；
- 天下先“标为客户”是否等于 `ClientContact.is_primary`，称谓来源及无联系人默认规则；
- 22 项致函官方清单是否作为权威初始化字典，还是只作为历史候选/别名；
- `spec_pages` 是否已经包含附图页，说明书附加费的精确官方计页口径；
- PayList Type/FlowDir、发票范围、planned/paid 金额及已缴修改权限的实际操作合同；
- 文书清单需要的最大数据量、必需列、证书清单及 Excel/Word/PDF 范围；
- 今日提醒是否严格按提醒日、内部期限、官方期限和 daily reminder 并集生成。

## 8. 关闭判断

本 meta-audit 的结论不是“前两轮工作无效”，而是：**问题发现大体有价值，批量实施的验收方式和若干业务闭环判断不成立。** 当前代码更接近可演示原型，但仍不能以两份报告作为生产级专利事务管理系统的完成证明。

本审计只关闭“两轮报告的独立复核与处置建议”这一文档切片；未修改产品代码、两轮源报告、客户材料或任何既有实现，也未替代后续逐任务验收。
