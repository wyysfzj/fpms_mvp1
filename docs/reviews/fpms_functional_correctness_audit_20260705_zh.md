# FPMS 功能完整性与实现正确性审查

日期：2026-07-05

任务：`FPMS-FUNCTIONAL-CORRECTNESS-AUDIT-ZH-20260705-01`

英文原报告：`docs/reviews/fpms_functional_correctness_audit_20260705.md`

## 核心职责理解

本审查基于仓库 source document index、post-demo P1 Functional Spec、后续收费设计、近期 evidence summary 和当前前后端代码，对 FPMS 当前实现做两类检查：

- 功能完整性：哪些客户流程中应该存在的能力仍缺失或不完整。
- 实现正确性：已经实现的能力是否存在状态、字段、费用、文件、证据或集成边界上的逻辑风险。

本轮不修改产品代码，只输出审查文档和 evidence。

## 审查范围与方法

审查证据按以下顺序使用：

- 仓库权威规则：`AGENTS.md`，尤其是 `0.3 Source Document Index for Reviews and Audits`。
- `AGENTS.md` 索引中的客户和设计文档语料：通过已入库 Markdown spec、既有提取文本和 evidence ledger 复核 `docs/TXX.pdf`、`docs/postdemo/相关流程操作-20260526.docx`、`docs/postdemo/OA答复流程.docx`、`docs/postdemo/信函生成操作.docx`、`docs/postdemo/专利收费场景-20260626.docx`、`/Users/cfcc/Documents/相关问题解答.docx`、P1 Functional Spec、生命周期 demo 设计和收费后续设计。
- `artifacts/PD-ENH-*`、`artifacts/PD-P1-*`、`artifacts/PD-FEE-SCENARIO-*`、`artifacts/PD-DOC-*` 下的 evidence summary。
- 当前实现：`backend/app/modules/cases`、`documents`、`official_workflows`、`fees`、`grant_fees`、`annuity`、`templates`，以及相关前端页面和测试。

## 总体判断

| 维度 | 总体评价 | 风险等级 | 主要原因 |
|---|---|---:|---|
| 功能完整性 | P1 国内主线已经基本成形，但若按生产级闭环要求，仍有若干客户可见闭合点不完整或仍是人工表示。 | 高 | 已具备案件官方字段、新申请/OA 工作包、回执归档面板、附件角色、官方来文目录、费减转换、费率目录、复审预览、授权/年费 demo 支撑和信函交接。剩余缺口集中在状态门禁、结构化回执校验、官方缴费模板兼容、文件版本/校验和审计导出。 |
| 实现正确性 | 当前实现可以支撑 demo 和已验证的 P1 定向流程，但部分状态和证据规则弱于 spec 的业务表达。 | 高 | 最重要风险包括授权状态字段门禁不一致、回执硬门禁只验证弱证据、费率选择忽略生效期、多文件角色 manifest 覆盖、案件状态流转校验过宽。 |

已经确认实现或部分实现的能力：

- 申请人/发明人官方字段已在案件申请人/发明人行上维护，并在案件 UI/API 可见：`backend/app/modules/cases/models.py:162`、`backend/app/modules/cases/models.py:185`、`frontend/src/modules/cases/pages/CaseEdit.vue:203`。
- 总委托书备案编号已经进入申请人主数据：`backend/app/modules/masterdata/applicants/models.py:16`，并在官方工作包字段完整性中检查：`backend/app/modules/official_workflows/service.py:315`。
- 附件官方角色、历史别名、哈希、归档证据、回执证据字段已经存在：`backend/app/modules/documents/models.py:16`。
- 官方来文目录已按客户 TABLE 001 补齐 60 项 seeded `DocTemplate`，见 `artifacts/PD-DOC-OFFICIAL-NOTICE-CATALOG-20260705-01/summary.md`。
- PCT/Hague/IC 费用已经参数化，但按设计保持不自动触发，符合 `docs/postdemo/postdemo_fee_followup_trigger_design_20260705.md:15` 的边界。

## 功能缺失清单

| ID | 缺失/不完整功能 | 预期场景描述 | 当前代码情况 | 影响严重度 | 建议优先级 | 备注 |
|---|---|---|---|---:|---:|---|
| FG-01 | 代理人资格证号档案 | 新申请递交和官方请求书页面应能复用代理人资格证号，避免人工重复填写。 | 案件只存 `primary_agent_id`、`second_agent_id`、`draftor_id`，未发现稳定的代理人资格证号字段：`backend/app/modules/cases/models.py:105`。官方字段完整性只检查代理人是否存在，不检查资格证号：`backend/app/modules/official_workflows/service.py:238`。 | 高 | P0 | 客户文档明确旧系统可带入该值；维护来源仍在 `docs/postdemo/postdemo_p1_functional_spec_20260531.md:252` 标为待确认。 |
| FG-02 | 文档版本与替换链 | 权利要求书、OA 意见陈述、PDF 保真附件、补正文件等需要版本关系：当前版本、被替换版本、来源文件和替换原因。 | `DocAttachment` 有文件元数据和哈希，但没有版本号、supersedes 链、当前版本标记或附件生命周期：`backend/app/modules/documents/models.py:16`。 | 高 | P0 | 没有版本链时，难以证明最终提交的是哪一版权利要求书或意见陈述。 |
| FG-03 | 按附件角色进行文件校验 | 官方提交包应至少按角色校验扩展名/MIME：Word、PDF、XML zip、回执 PDF、权利要求书、证明文件等。 | `add_attachment` 中 `allowed_mime_types` 和 `allowed_exts` 恒为 `None`，不会执行按角色的类型/扩展名限制：`backend/app/modules/documents/service.py:2027`。 | 高 | P0 | 直接影响官方提交包质量，无法提前发现错传文件。 |
| FG-04 | 回执 PDF 解析和收到文件清单结构化校验 | OA 和新申请工作包应把回执可见元数据、收到文件清单与 required manifest 角色进行核对后再归档。 | 回执字段以自由文本保存：`backend/app/modules/official_workflows/models.py:74`，未见 PDF 解析或 manifest-to-receipt 对比。 | 高 | P0 | FS 要求回执元数据和收到文件清单支撑关闭条件：`docs/postdemo/postdemo_p1_functional_spec_20260531.md:160`。 |
| FG-05 | 官方缴费 Excel 模板兼容 | 费用流程应区分内部 pay-list 导出和官网“补充缴费信息模板”兼容，并在确认后提供官方字段。 | 当前年费导出生成内部 Excel 并推进 pay-list 状态：`backend/app/modules/annuity/service.py:1369`。P1 evidence 已说明未实现官方 Excel 生成：`artifacts/PD-P1-BE-FEE-LINKAGE-API-01/summary.md`。 | 高 | P1 | 客户截图体现官方网页上传/校验路径；当前实现是人工就绪，不是官方模板就绪。 |
| FG-06 | 外部操作失败与重试流程 | 官方系统上传失败、缴费失败、回执下载失败等应有失败状态、重试负责人、重试期限和恢复路径。 | 官方工作包有状态和 override，但未发现结构化外部失败事件或重试队列：`backend/app/modules/official_workflows/models.py:12`。 | 中 | P1 | P1 可保持人工操作，但产品应记录失败的官方操作，而不是只靠备注。 |
| FG-07 | 产品级审计/证据导出 | 客户侧审计应能导出谁准备、谁复核、谁人工提交、谁上传回执、谁 override、哪些状态被修改。 | 仓库有开发 evidence，产品表也有 audit mixin、哈希和 override 记录，但未发现面向用户的案件/工作包审计导出。 | 高 | P1 | 这与 `artifacts/*` 开发证据不同；客户需要产品内证据。 |
| FG-08 | 官方 direct submit / 自动回执下载 | 客户理想状态包含 CPC/官方系统集成、直接提交、自动上传和自动下载。 | P1 明确排除 CPC/OA direct submit、RPA、签名、支付自动化和回执自动下载：`docs/postdemo/postdemo_p1_functional_spec_20260531.md:46`。 | 高 | P2/P3 | 不是 P1 缺陷，但仍是相对客户理想状态的重要后续缺口。 |
| FG-09 | 格式函“最新官方通知”选择规则 | 信函生成从案件入口启动时，应由最新官方通知驱动，而不是完全依赖人工选择 source document。 | 信函交接预览需要 `source_document_id`，并只映射该文档：`backend/app/modules/official_workflows/service.py:1553`。未发现最新官文选择规则。 | 中 | P1 | 最新官文同日判定仍是客户待确认问题：`docs/postdemo/postdemo_p1_functional_spec_20260531.md:255`。 |
| FG-10 | 龙虾交接传输合同 | 系统应产出龙虾系统实际需要的格式，或明确为人工交接。 | 当前交接 payload 包含邮件标题、生成 Word 路径和附件：`backend/app/modules/official_workflows/service.py:1597`，状态可人工更新：`backend/app/modules/official_workflows/service.py:1726`。 | 中 | P1/P2 | P1 手工交接可能够用，但龙虾实际格式仍需确认。 |
| FG-11 | 持久化收费触发规则目录 | 费率参数回答“多少钱”，触发规则回答“什么时候、为什么产生费用”。 | 当前官方费用预览只在 service code 中支持 `FILING_ACCEPTED` 和 `REEXAM_REQUESTED`：`backend/app/modules/fees/service.py:902`。收费设计建议建立触发规则层：`docs/postdemo/postdemo_fee_scenario_integration_design_20260704.md:176`。 | 中 | P1.5/P2 | P1.5 用服务层规则可接受，但可审计/可维护的持久化触发规则仍不完整。 |
| FG-12 | PCT/Hague/IC 自动触发 | 未来 PCT、海牙、集成电路布图设计应在样例和字段确认后再自动触发。 | 费率目录已有参数行，但 `preview_official_fee_candidates` 会拒绝未支持 trigger：`backend/app/modules/fees/service.py:902`。 | 中 | P2/P3 | 当前冻结是正确设计边界；不应当作 P1 失败。 |

## 实现正确性问题清单

| ID | 问题位置（文件/函数） | 问题描述 | 证据/代码引用 | 可能影响 | 根因分析 | 修复建议 | 严重度 | 优先级 |
|---|---|---|---|---|---|---|---:|---:|
| IC-01 | `backend/app/modules/documents/service.py::_has_required_grant_fields`；`backend/app/modules/cases/service.py::validate_status_required_fields`；`backend/app/modules/grant_fees/service.py::_case_has_required_grant_fields` | 授权状态 readiness 不一致。上传授权通知附件可使用比案件服务更少的字段把案件推进到 `GRANTED`。 | 附件路径要求 `app_no`、`filing_date`、`issue_date`、`grant_no`、`grant_date`、`first_annuity_year`、`valid_until`：`documents/service.py:209`。案件服务对 `GRANTED` 还要求 `pub_no` 和 `pub_date`：`cases/service.py:645`。授权费服务同样要求公开字段：`grant_fees/service.py:334`。 | 案件可能通过文件上传进入“已授权”，但普通案件状态校验会拒绝同样状态，误导 demo 和生产状态展示。 | 三套 readiness predicate 独立演化，发生漂移。 | 抽出统一的 GRANTED readiness 服务函数，让附件上传、授权费动作、案件编辑共用。补充缺 `pub_no` / `pub_date` 的回归测试。 | 高 | P0 |
| IC-02 | `backend/app/modules/official_workflows/service.py::_has_archived_receipt`、`record_official_work_package_receipt`、`evaluate_official_work_package` | 回执硬门禁只检查回执附件和归档状态，不检查回执元数据或收到文件清单。 | `_has_archived_receipt` 只要 `receipt_attachment_id` 存在且 `archive_status` 为归档状态即通过：`official_workflows/service.py:463`。`record_official_work_package_receipt` 只把 `received_file_list` 作为文本保存：`official_workflows/service.py:1842`。 | 即使接收案件编号、提交人、接收时间或收到文件清单缺失/错误，工作包仍可能归档。 | 门禁实现为“证据存在”，不是“证据内容完整”。 | 归档前要求元数据完整或明确标记不适用；可选增加 manifest 与回执文件清单核对。 | 高 | P0 |
| IC-03 | `backend/app/modules/official_workflows/api.py::archive_official_work_package_endpoint` 和 `archive_official_work_package` | 归档 override 与普通工作包更新共用 `OfficialWorkflow.Update` 权限。 | 归档接口使用 `OfficialWorkflow.Update`：`official_workflows/api.py:317`。override 逻辑记录原因/负责人，但没有独立 override 权限或角色校验：`official_workflows/service.py:1947`。 | 只要能更新官方工作包的用户，就可能在 UI/API 允许时绕过缺回执归档门禁。 | 授权粒度没有区分普通更新和合规 override。 | 增加独立权限，例如 `OfficialWorkflow.OverrideArchive`，保留原因和后续责任要求，并补权限测试。 | 高 | P0 |
| IC-04 | `backend/app/modules/official_workflows/service.py::_upsert_manifest_role` | 官方提交包 manifest 按角色唯一，重复角色会覆盖附件。 | 查询条件只有 `package_id` 和 `official_file_role`：`official_workflows/service.py:374`，随后替换 `attachment_id`：`official_workflows/service.py:400`。 | OA “其他证明文件”或多个证明文件可能在 manifest 中被压成一行，丢失完整附件可见性。 | 把 role 当成唯一文件身份，但官方页面可能允许同一上传类别多个文件。 | 对多文件角色使用 line-level manifest 或 `role + attachment_id` 行；只对真正单文件角色保留单行逻辑。 | 高 | P1 |
| IC-05 | `backend/app/modules/fees/service.py::_enabled_fee_rates_by_code`；`backend/app/modules/annuity/service.py::_rate_amount`；`backend/app/modules/grant_fees/service.py::_select_matching_gov_rate` | 费率选择忽略 `effective_from` 和 `effective_to`。 | `FeeRate` 有生效期字段：`fees/models.py:117`，但选择器主要按 enabled/currency/group/code 过滤并按更新时间排序：`fees/service.py:640`、`annuity/service.py:808`、`grant_fees/service.py:260`。 | 若未来费率或过期费率仍 enabled 且更新时间更近，可能被错误选中。 | 参数模型增加了生效期，但计算选择器尚未接入。 | 增加 `as_of_date` 选择规则，并过滤 `effective_from <= as_of <= effective_to or null`。补重叠旧/现行/未来费率测试。 | 高 | P1 |
| IC-06 | `backend/app/modules/annuity/service.py::export_pay_list` | pay-list 导出在用户证明成功下载或官方接受前就把状态改为 `EXPORTED`。 | `pay_list.status = "EXPORTED"` 在提交和返回前设置：`annuity/service.py:1400`。 | 如果浏览器下载失败或官方网页后续拒绝 Excel，内部状态会提前表示已进展。 | 内部文件生成和外部官方上传接受被合并成一个状态。 | 拆分状态：内部文件已生成、已下载、官方上传待处理、官方接受/拒绝。至少增加重试/回退动作和证据字段。 | 中 | P1 |
| IC-07 | `backend/app/modules/cases/service.py::validate_case_status_transition` | 案件状态流转校验对大多数非终态跳转过宽。 | 该函数只在当前状态属于 terminal transition map 时限制目标状态：`cases/service.py:1036`。 | 用户或自动化可能跳过生命周期状态，导致法律状态故事和费用/任务触发不一致。 | 当前依赖必填字段和终态限制，而不是完整状态机。 | 建立法律状态 transition matrix，或对敏感状态要求由文件/任务触发。 | 高 | P1 |
| IC-08 | `backend/app/modules/grant_fees/service.py::derive_grant_fee_task_state` 和 `_apply_grant_fee_task_mutation` | 授权费任务状态由标志和 `notify_count` 推导，而不是显式持久化状态。 | `notify_count >= 4` 表示 `DONE`；`draft_generated`、客户指令、`notice_sent` 决定状态：`grant_fees/service.py:317`。 | 导入或人工修改数据时可能产生不可能状态，且状态含义难审计。 | 为快速实现采用派生状态，但用 magic counter 承载业务状态。 | 增加显式 state 或 transition event log；现有字段只作为展示辅助。 | 中 | P1 |
| IC-09 | `backend/app/modules/documents/service.py::add_attachment` | 上传服务有文件名和大小检查，但按角色的文件类型限制未启用。 | `allowed_mime_types` 和 `allowed_exts` 恒为 `None`：`documents/service.py:2027`，角色元数据在文件写入后才解析：`documents/service.py:2075`。 | 错误类型文件可被标为回执、XML zip 或 OA 意见陈述，削弱后续官方包检查。 | 上传逻辑是通用型，角色元数据是后加的。 | 写入前先解析角色并应用角色级扩展名/MIME allowlist；人工 override 必须留原因。 | 高 | P0 |
| IC-10 | `backend/app/modules/official_workflows/service.py::_find_letter_mapping` 和 `get_letter_handoff_preview` | 信函交接只映射传入的 source document，没有实现“最新官方通知”选择。 | mapping 对当前文档打分：`official_workflows/service.py:1378`，preview 从 `source_document_id` 开始：`official_workflows/service.py:1553`。 | 同一案件有多份同日官文时，可能人工选择错误来源，格式函不一致。 | 现 API 是文档中心，而客户流程描述是案件中“最新官文”驱动。 | 客户确认同日判定规则后，增加案件级 latest official notice resolver；在此之前 UI 明确显示“人工选择的来源文书”。 | 中 | P1 |

## 高风险缺失功能和错误实现排序

1. `IC-01` 授权状态 readiness predicate 漂移。最高风险，因为它可能显示错误法律状态。
2. `IC-02` / `FG-04` 回执归档证据未做结构化校验，可能错误关闭官方工作包。
3. `IC-09` / `FG-03` 缺少按角色的上传文件校验，可能污染文件驱动工作流。
4. `IC-05` 费率生效期未参与选择，费率更新后可能计算错误官费。
5. `FG-05` 官方缴费 Excel 模板兼容未实现，限制 pay-list 之后的收费节点闭环。
6. `IC-04` 多文件角色在 manifest 中可能被覆盖，影响 OA 证明文件和附件密集场景。
7. `IC-07` 案件状态流转过宽，不利于生命周期 demo 和生产状态一致性。

## 建议的原子任务拆分

| 建议任务 ID | closure slice | non-closure boundary | 建议优先级 |
|---|---|---|---:|
| `FPMS-GRANT-STATUS-READINESS-GATE-20260705-01` | 统一 GRANTED readiness，让授权通知上传、授权费动作、案件状态更新共用同一必填字段校验。 | 不重构完整法律状态模型。 | P0 |
| `FPMS-RECEIPT-STRUCTURED-ARCHIVE-GATE-20260705-01` | 归档前要求回执元数据完整或明确不适用，并尽可能按 manifest 校验收到文件清单。 | 不实现 OCR 或自动下载回执。 | P0 |
| `FPMS-ATTACHMENT-ROLE-VALIDATION-20260705-01` | 为回执 PDF、XML zip、Word、PDF、证明文件等增加角色级扩展名/MIME 校验。 | 不改附件存储路径，不加入病毒扫描。 | P0 |
| `FPMS-OFFICIAL-WORKFLOW-OVERRIDE-PERMISSION-20260705-01` | 为归档 override 增加独立权限和测试。 | 不重构全部权限码。 | P0 |
| `FPMS-FEE-RATE-EFFECTIVE-DATE-SELECTION-20260705-01` | 官方费用和年费/授权费选择费率时使用生效期。 | 不改费率金额或 seed 目录内容。 | P1 |
| `FPMS-OFFICIAL-MANIFEST-MULTI-FILE-ROLE-20260705-01` | 支持 OA 其他证明文件等多文件角色的多行 manifest。 | 不改官方来文目录或附件角色词表。 | P1 |
| `FPMS-DOCUMENT-VERSION-LINEAGE-20260705-01` | 为官方提交包附件增加版本/替换链元数据。 | 不迁移历史文件，除非另行批准。 | P1 |
| `FPMS-PAY-LIST-OFFICIAL-TEMPLATE-COMPAT-20260705-01` | 增加官方 Excel 模板兼容状态、字段、样例导入校验和 UI 提示。 | 不自动缴费，不自动浏览器上传。 | P1 |
| `FPMS-LEGAL-STATUS-TRANSITION-MATRIX-20260705-01` | 定义并执行案件法律状态 active lifecycle transition matrix。 | 不在同一任务改费用任务状态机。 | P1 |
| `FPMS-AGENT-OFFICIAL-PROFILE-20260705-01` | 增加代理人资格证号来源字段和官方工作包 readiness 检查。 | 不建设 HR/员工管理模块。 | P1 |
| `FPMS-LETTER-LATEST-OFFICIAL-NOTICE-RESOLVER-20260705-01` | 客户确认判定规则后，增加案件级最新官方通知 resolver。 | 不替换龙虾邮件发送。 | P1/P2 |
| `FPMS-PRODUCT-AUDIT-EXPORT-20260705-01` | 增加案件/工作包证据导出：字段来源、文件哈希、状态变化、人工动作、override、回执。 | 不改变仓库 evidence artifacts。 | P1/P2 |

## 待确认问题

- 代理人资格证号归属：用户/员工档案、代理人档案，还是案件分工记录。
- 最新官方通知判定：官文日、接收日、入库时间、官文代码优先级，还是人工选择。
- 回执 override 权限：哪个角色可以无回执归档，需要什么审批记录。
- 官方缴费 Excel：空模板、成功上传样例、字段说明和官方校验报错。
- 龙虾交接合同：只接收 Word 文件、邮件正文、附件路径、Excel 清单、API payload，还是人工取件目录。
- PCT/Hague/IC 自动触发前需要的客户样例和字段。
- 回执收到文件清单是否必须系统解析，还是允许人工录入后做 checklist 校验。

## 关闭判断

本审查不认为 P1 全范围缺失。当前 demo 可见的 P1 路径整体已经存在，但若要达到生产级可信闭环，若干高风险 closure semantics 还不够强。下一步开发应优先处理 P0 evidence gates：授权状态 readiness、回执归档内容校验、按角色文件校验和 override 权限分离。
