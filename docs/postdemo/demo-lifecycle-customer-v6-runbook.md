# FPMS 客户演示 Runbook V6：同案双轨费用闭环

版本：2026-08-29
受众：客户业务、流程与财务负责人
数据边界：`SYNTHETIC_TEST_ONLY`，采用真实业务形态的合成测试数据，非客户授权、非生产输入。

## 演示前重置与预检

演示前由主持人在不共享的终端启动一个全新隔离 run；不得把旧 run 作为 reset 输入，也不得在 preflight 删除旧 run 或在旧数据库中按表删行后复用。必须使用新的 run ID、run root、数据库、业务号和证据目录，并确认新的数据库、WAL、SHM 与证据目录均不存在，runtime bundle、authority、官费费率簿和服务费来源摘要匹配，Network Error 与 console 采集已开启且网络预检通过。旧 run 只可在演示结束后通过已验证 exact run root 的独立 cleanup/归档流程处理；失败 artifact 必须保留。任何预检失败都停止，不进入客户共享页面，也不得靠重试或过滤错误继续演示。

统一场景：澄岳智造技术（苏州）有限公司；联系人周岚；案件 `CYIP-CN-INV-<run suffix>`；案名“一种柔性制造产线中视觉检测工位的自适应标定方法”。客户共享屏幕只出现正常业务页面，不出现主持人控制页面。

### 当前客户投影检查点

- 客户详情顶部显示“客户管理 / 客户详情 / 澄岳智造技术（苏州）有限公司”的客户名称面包屑，不把 UUID 当作业务名称。
- 案件列表在授权登记阶段显示“第5阶段/5 · 授权登记”，状态列名为“流程状态”；案件详情继续使用权威生命周期投影。
- 文书录入与详情展示结构化文书字段：标题、文书日期、内部文号、需要回复、回复来源文件和补充说明；证据版本与来源关系仍可审计。
- 授权登记阶段的首次申请规则显示“历史首次申请递交材料核验”，并明确不作为当前授权登记的阻断结论；不得伪造历史规则 PASS。
- 授权费用任务页的“预览官费”和“确认官费”按钮在当前任务上可见、可点；旧任务仍只读，确认前仍无官费义务。
- 案件详情首屏按文件、程序、费用三轨显示当前优先摘要；每轨都有“现在是什么状态”“最近发生了什么”“下一步是什么”。
- “查看完整历史”默认收起。完整历史展开后仍先显示中文业务事实；UUID、哈希和原始英文状态默认隐藏，只有显式展开“审计信息”后才可见。

## 冻结的 UI-only 执行合同

- 唯一合同：`FPMS_Automation_Skeleton_Pack/data/testcases/demo_v6_ui_parity_v1.json`，schema 为 `fpms.demo-v6-ui-parity/v1`；共 103 个输入/来源字段和 30 个可见输出字段。
- `EXPLICIT_INPUT` 必须由 HUMAN 与 CODEX 在正常页面输入相同固定值或相同 `<run suffix>` 模板；`SOURCE_BOUND` 必须从当前页面读取并选择；`APP_GENERATED` 只能由系统生成。
- 允许不同的只有 run suffix、UUID/自增 ID、数据库/文件路径、动态凭据、幂等键和系统时间戳。日期、金额、原因、来源摘要及业务状态不得不同。
- 允许页面为 `/demo/inputs` 只读预检、客户/案件/文书/流程/授权费用/草单/清单/回款/核销等正常页面；禁止进入隐藏演示控制路由，禁止 curl、直接 HTTP/SQL、内部 ID 抄写、旧 artifact 复用或 observer 发起 mutation。
- 每阶段结束点击页面顶部“记录阶段 NN 截图”。第 11 阶段后回到 `/demo/inputs`，点击“完成并导出本轮证据”。只有 11 张不同截图、可见 action/mutation 一一对应且 Network/console 为零，才生成 actor `pass-receipt.json`。

### 十二份上传文件的附件角色

`upload-manifest.json` 的 `evidence_key` 是场景证据身份，不是“附件角色”下拉框的值。每次必须先选择文件，再从下拉框点击下表中的中文附件角色；页面显示正确角色后才能点击“确认上传”。不得把 `evidence_key` 输入下拉框，也不得上传“未标注”附件。

| 阶段 | `evidence_key` | 中文标题 | 附件角色 |
| --- | --- | --- | --- |
| `03` | `FILING_FINAL_SUBMISSION` | 发明专利请求书及申请文件 | 合并PDF |
| `03` | `FILING_RECEIPT` | 发明专利申请递交回执 | 电子申请回执 |
| `03` | `ACCEPTANCE_NOTICE` | 发明专利申请受理通知书 | 官方通知书PDF |
| `03` | `PRELIMINARY_EXAMINATION_SOURCE` | 发明专利申请初步审查合格通知书 | 官方通知书PDF |
| `03` | `PUBLICATION_NOTICE` | 发明专利申请公布通知书 | 官方通知书PDF |
| `03` | `SUBSTANTIVE_EXAMINATION_SOURCE` | 发明专利申请进入实质审查阶段通知书 | 官方通知书PDF |
| `04` | `OA_NOTICE_1` | 第一次审查意见通知书 | 官方通知书PDF |
| `04` | `OA_RECEIPT_1` | 第一次审查意见答复递交回执 | 电子申请回执 |
| `05` | `OA_NOTICE_2` | 第二次审查意见通知书 | 官方通知书PDF |
| `05` | `OA_RECEIPT_2` | 第二次审查意见答复递交回执 | 电子申请回执 |
| `06` | `GRANT_NOTICE_ORIGINAL` | 办理登记手续通知书 | 官方通知书PDF |
| `06` | `GRANT_NOTICE_REPLACEMENT` | 办理登记手续更正通知书 | 官方通知书PDF |

### 正常页面路线

| 阶段 | 路线（动态 ID 由当前页面链接带入，不手抄） |
| --- | --- |
| `01` | `/clients/new` → `/clients/:id` → `/cases/new` → `/cases/:id` |
| `02` | `/documents/wizard` → `/official-workflows/filing-preparation` |
| `03` | `/documents/:id` → `/official-workflows/filing-preparation` → `/cases/:id` |
| `04` | `/documents/new` → `/documents/:id` → `/official-workflows/oa-reply` |
| `05` | `/documents/new` → `/documents/:id` → `/official-workflows/oa-reply` → `/cases/:id` |
| `06` | `/grant-fee/tasks` → `/cases/:id` |
| `07` | `/grant-fee/tasks` → `/fees/drafts/:id` |
| `08` | `/fees/drafts/new` → `/fees/drafts/:id` → `/fees/drafts` |
| `09` | `/fee-management/pay-lists` → `/fee-management/pay-lists/:id` → `/fee-management/gov-payments/new` |
| `10` | `/billing/bills/new` → `/billing/bills/:id` → `/billing/payments/new` → `/billing/payments` |
| `11` | `/cases/:id`（只读，无新业务写入） |

### 完整字段分类索引

字段的值、控件、来源选择器和 normalization 以唯一 JSON 合同为准；本表覆盖全部字段键，防止人工或 Codex 自行改分类。

| 阶段 | `EXPLICIT_INPUT` | `SOURCE_BOUND` | `APP_GENERATED` | 可见输出及分类 |
| --- | --- | --- | --- | --- |
| `01` | customer_name, customer_code, customer_email, contact_name, contact_title, contact_email, contact_is_primary, case_no, case_title, case_type, patent_category, flow_direction, fee_reduction | client_binding, first_applicant | — | unique_customer_and_primary_contact [APP_GENERATED], unique_case [APP_GENERATED], same_case_primary_contact_and_first_applicant [APP_GENERATED] |
| `02` | — | current_case, filing_catalog_60 | — | same_filing_package [APP_GENERATED], catalog_execution_boundary [SOURCE_BOUND] |
| `03` | filing_submission_completed_at, filing_submission_note, filing_receipt_no, filing_receipt_received_at, filing_receipt_receiver | filing_final_submission_evidence, filing_receipt_evidence, acceptance_notice_evidence, preliminary_examination_evidence, publication_notice_evidence, substantive_examination_evidence | — | submission_and_receipt_lineage, acceptance_projection, preliminary_projection, publication_and_substantive_projection [APP_GENERATED] |
| `04` | oa_sequence, oa_notice_at, oa_due_date | oa_notice_evidence, oa_reply_output_roles, oa_receipt_evidence, oa_receipt_received_at | — | oa1_unique_chain, oa1_reply_output_bindings [APP_GENERATED] |
| `05` | oa_sequence, oa_notice_at, oa_due_date | oa_notice_evidence, oa_reply_output_roles, oa_receipt_evidence, oa_receipt_received_at | — | oa2_unique_chain, oa_round_identity_separation [APP_GENERATED] |
| `06` | original_grant_notice_at, original_grant_due_date, replacement_grant_notice_at, replacement_grant_due_date, replacement_grant_reason, current_task_instruction | original_grant_evidence, replacement_grant_evidence, current_task_waiting_client | — | original_task_superseded_read_only, current_task_pay_once, no_gov_before_confirmation [APP_GENERATED] |
| `07` | — | current_grant_task, reviewed_replacement_evidence, rate_book_digest, rate_row_digests, preview_digest, preview_line_amounts | confirmation_time, confirmation_idempotency_key | gov_preview_total [SOURCE_BOUND], unique_gov_obligation_and_draft, gov_lines_read_only [APP_GENERATED] |
| `08` | service_item_1, service_item_2, service_item_2_quantity_before, service_item_2_quantity_after, service_adjustment_reason | — | — | one_gov_and_one_service_draft, service_adjustment_total, both_drafts_locked [APP_GENERATED] |
| `09` | planned_pay_date, pay_list_remark | gov_line_amounts, official_receipt_fields, voucher_fields, invoice_fields | — | one_two_line_pay_list, pending_official_evidence_per_line [APP_GENERATED] |
| `10` | bill_no, bill_date, bill_due_date, payment_1_amount, payment_1_date, payment_1_method, payment_1_no, payment_1_bank_ref, payment_1_remark, offset_1_date, payment_2_date, payment_2_method, payment_2_no, payment_2_bank_ref, payment_2_remark, offset_2_date | service_locked_draft, payment_1_bill, payment_1_currency, offset_1_payment_line, offset_1_bill, offset_1_amount, payment_2_bill, payment_2_amount, payment_2_currency, offset_2_payment_line, offset_2_bill, offset_2_amount | bill_idempotency_key, payment_1_idempotency_key, offset_1_idempotency_key, payment_2_idempotency_key, offset_2_idempotency_key | bill_settlement_transition, two_payments_and_offsets, payment_offset_bill_equation [APP_GENERATED] |
| `11` | — | — | — | same_case_gov_pending_evidence, same_case_service_settled [SOURCE_BOUND], cross_track_consistency [APP_GENERATED] |

## 两轮技术演练收据

既有严格技术收据证明严格 UI 技术路径已通过；未来 tag 仍须在 actor 会话前 fresh 执行一次 `--strict-ui --runs 1 --headless`。HUMAN、CODEX 与 comparator receipt 当前仍待完成，不能由技术收据代替。冻结业务值保持不变：11 个 V6 阶段、12 个证据绑定，官费 950.00 CNY；服务费 1,500.00 调整为 1,800.00 CNY；两次回款与核销为 1,200.00 + 600.00 = 1,800.00 CNY，最终已结清、余额 0.00 CNY。

## 阶段 01：客户与案件

**演示话术**：从一个真实业务形态的客户、联系人和中国发明申请开始，后续全部对象归于同一案件。
**UI/操作**：依次打开客户新建、联系人新建、案件新建和案件详情页。
**输入**：澄岳智造技术（苏州）有限公司；周岚；知识产权经理；`zhou.lan@chengyue-ip.example`；`CYIP-CN-INV-<run suffix>`。
**屏幕输出**：客户名称面包屑、主联系人、案号、案名、案件列表当前阶段与流程状态。
**期待结果**：客户、联系人、案件各一条；列表与详情投影一致，关联关系唯一。
**验证方法**：比对客户名称面包屑、案件列表“当前阶段/流程状态”和 canonical IA-01/IA-02 的对象身份与计数。
**事实边界**：业务字段模拟真实形态，但整组数据仍为合成测试输入。
**停止条件**：首次加载 Network Error、重复对象、关联错误或英文新增状态。
**最近新增**：fresh-run 隔离与真实业务形态的动态业务号。

## 阶段 02：文件与递交准备

**演示话术**：先证明模板和目录来源，再建立可复用的递交准备工作包。
**UI/操作**：打开文书向导与案件递交准备页；同一案件重复 resolve 一次。
**输入**：runtime 模板代码、模板 SHA-256、60 行官方文书目录。
**屏幕输出**：目录可执行/仅参考状态和同一工作包身份。
**期待结果**：目录请求成功，重复 resolve 不产生第二个工作包。
**验证方法**：canonical IA-00、IA-03、IA-04 核对 provenance、目录数和工作包 ID。
**事实边界**：递交准备不等于系统已经向官方递交。
**停止条件**：摘要不匹配、目录数量错误、请求 422 或重复工作包。
**最近新增**：runtime bundle 与模板来源门禁。

## 阶段 03：受理与审查

**演示话术**：案件状态只由已复核文件和可追踪活动推动。
**UI/操作**：上传、复核并消费递交文件、递交回执、受理、初审、公布与实审通知。
**输入**：六份独立文件及其 SHA-256。
**屏幕输出**：结构化文书字段、附件、证据版本、复核状态、活动和案件审查投影。
**期待结果**：六份证据身份独立，案件依事实进入实质审查。
**验证方法**：canonical IA-05 核对证据版本、内容哈希和消费对象。
**事实边界**：内部登记外部操作不代表本系统直接连接官方系统。
**停止条件**：未复核、哈希缺失、证据复用或页面与权威投影不一致。
**最近新增**：证据版本—活动—生命周期消费的完整 lineage。

## 阶段 04：第一轮 OA

**演示话术**：第一轮通知、期限、答复包、任务和回执是一套独立事实。
**UI/操作**：登记通知与期限，生成答复包，验证错误回执 no-write，再登记正确回执。
**输入**：第一次审查意见通知书、答复输出、答复递交回执和确认期限三元组。
**屏幕输出**：开放任务、期限、答复文件、回执和归档状态。
**期待结果**：错误回执被拒绝且不写入；正确回执只关闭目标任务。
**验证方法**：canonical IA-05 至 IA-08 比较错误请求前后快照。
**事实边界**：本轮日期是合成输入，不是通用法定期限。
**停止条件**：期限漂移、错误回执写入、任务提前或错误关闭。
**最近新增**：错误回执的 4xx + no-write 可验证门禁。

## 阶段 05：第二轮 OA

**演示话术**：第二轮不是覆盖第一轮，而是独立的通知、期限、答复和回执。
**UI/操作**：完成第二轮通知、答复包、任务和回执，再回看第一轮历史。
**输入**：第二次审查意见通知书、答复输出与递交回执。
**屏幕输出**：第二轮独立身份与保持不变的第一轮历史。
**期待结果**：两轮互不污染，第二轮完成后回到实质审查。
**验证方法**：canonical IA-09 对比两轮 source/package/task/receipt。
**事实边界**：两轮不得复用证据或期限。
**停止条件**：任一身份重复、第一轮历史被改变或错误任务关闭。
**最近新增**：多轮 OA 的独立身份与可重放结果。

## 阶段 06：授权登记准备

**演示话术**：更正通知显式替代原通知，旧任务失效后不能继续写。
**UI/操作**：复核原始和更正通知，查看替代关系与“历史首次申请递交材料核验”，验证旧任务写入被拒绝，在当前任务记录 PAY。
**输入**：办理登记手续通知书、办理登记手续更正通知书及各自证据版本。
**屏幕输出**：当前阶段为授权登记；历史首次申请规则不冒充当前阻断；当前唯一可操作任务上官费动作可见。
**期待结果**：旧任务 409/no-write，当前 PAY 恰好一条。
**验证方法**：canonical IA-10 至 IA-12 核对 supersession 和旧任务门禁。
**事实边界**：PAY 只是办理指示；此时尚未确认官费，不能生成金额。
**停止条件**：旧任务可写、替代边缺失、PAY 重复或提前出现官费对象。
**最近新增**：来源替代 durable lineage 与旧任务 fail-closed。

## 阶段 07：生效官费预览

**演示话术**：现在从已激活的官费费率簿计算不少于两行候选金额；“候选预览，尚未形成缴费义务”。
**UI/操作**：打开授权费用任务正常页面，确认“预览官费”和“确认官费”按钮可见、可点；先预览并核对来源、版本、生效日、摘要和逐行金额，再确认。
**输入**：当前任务、已复核更正通知版本、active rate-book digest、逐行确认金额和幂等键。
**屏幕输出**：多行 GOV 候选、合计、source authority、rate-book version、SHA-256 和预览摘要。
**期待结果**：确认后形成唯一 GOV obligation 与 GOV 草单；多行官费合计 950.00 CNY，重放返回相同对象。
**验证方法**：比对 preview digest、证据版本/哈希、费率簿摘要、行数和草单 ID。
**事实边界**：预览不是缴费义务；只有确认成功才形成只读官费草单。
**停止条件**：来源未激活、摘要漂移、少于两行、金额不一致或产生重复草单。
**最近新增**：active 官费来源门禁、多行预览和 digest-bound confirmation。

## 阶段 08：双草单与服务费调整

**演示话术**：同一案件同时保留 GOV 与 SERVICE 两条费用轨；官费只读，服务费只有一个授权项目可调整一次。
**UI/操作**：在正常草单页查看 GOV 来源；创建 SERVICE obligation/草单，在 OPEN 状态点击“调整数量”，输入中文原因，然后锁定两份草单。
**输入**：`FWSQDJ001`、`FWSQDJ002`；将可调整项目数量从 1 改为 2；原因“客户确认增加一份附加文件处理”。
**屏幕输出**：GOV 只读多行；SERVICE 两行；before/after total、adjustment activity、来源摘要；两份草单均已锁定。
**期待结果**：GOV 无编辑入口；SERVICE 只产生一次 superseding revision，金额从 1,500.00 CNY 变为 1,800.00 CNY。
**验证方法**：在页面“关联事实”中核对 fee domain、adjustable、adjustment activity、数量、金额和 LOCKED；被动 receipt 证明 persisted-only adjustment read seam 与 revision-aware overlay 指向当前 revision。
**事实边界**：服务费来自 runtime 服务费来源，不是官费；通用编辑不能替代审计活动。
**停止条件**：GOV 可编辑、SERVICE 可重复调整、原因/活动缺失或锁定后仍可编辑。
**最近新增**：GOV/SERVICE 双草单、一次可追溯 SERVICE adjustment、persisted-only adjustment read seam、revision-aware overlay 和 fail-closed source facts。

## 阶段 09：官费清单与待凭证登记

**演示话术**：逐行官费进入缴费清单后，只登记内部缴费事实；没有官方凭证时绝不显示为官方支付成功。
**UI/操作**：从 GOV 草单生成 PayList，逐行登记计划金额，再打开正常清单详情页。
**输入**：GOV fee item IDs、计划缴费日、每行 planned amount、同一命令幂等键；收据/凭证/发票均为 null。
**屏幕输出**：“已登记，待官方凭证核验”；official receipt、voucher、invoice 均为空。
**期待结果**：每个 GOV 行恰好一条 GovPayment；技术状态不得被显示成绿色支付成功。
**验证方法**：刷新正常清单页对账，核对 `REGISTERED_PENDING_OFFICIAL_EVIDENCE`、对象身份和三个空凭证字段；transport unknown 时只允许页面自身执行 GET-first 恢复。
**事实边界**：内部登记事实不等于已取得、核验或匹配官方凭证。
**停止条件**：Network Error、重复 GovPayment、任一空凭证被填充或页面显示“已缴费成功”。
**最近新增**：per-line GovPayment、待凭证事实边界以及 transport unknown 的 GET-first 恢复。

## 阶段 10：两次客户回款与核销

**演示话术**：账单、回款和核销是三个对象；第一笔核销后显示部分结清，第二笔金额必须读取权威余额。
**UI/操作**：从锁定 SERVICE 草单开 AR 账单；登记第一笔 1,200.00 CNY 回款并核销；刷新账单；读取余额后登记第二笔回款并核销；查看账单、回款和核销正常页面。
**输入**：`AR-CYZN-<run suffix>`；两组 `RCPT-CYZN` / `BTR-CYZN`；第二笔金额取第一笔核销后的 authoritative bill balance。
**屏幕输出**：先 `PARTIALLY_SETTLED` / 部分结清 / 600.00 CNY，再 `SETTLED` / 已结清 / 0.00 CNY。
**期待结果**：两笔独立回款、两条有效核销；1,200.00 + 600.00 = 1,800.00 CNY。
**验证方法**：比对 bill、payment line、offset、case receipt 的身份、状态、余额和金额等式。
**事实边界**：登记回款不等于账单核销；只有 offset 才减少账单余额。
**停止条件**：回款即结清、部分结清不出现、第二笔未读取余额、金额等式不成立或对象重复。
**最近新增**：两次回款/核销、部分结清到完全结清和 durable idempotency recovery。

## 阶段 11：同案双轨汇总

**演示话术**：回到案件详情，统一查看官费轨和服务费轨，但不混淆两种付款事实。
**UI/操作**：打开案件详情当前优先的文件、程序、费用三轨摘要；核对三组“现在是什么状态 / 最近发生了什么 / 下一步是什么”；确认“查看完整历史”默认收起，再按需展开历史和各卡片“审计信息”。
**输入**：前十阶段已经形成的权威对象，无新业务写入。
**屏幕输出**：当前优先三轨摘要；官费应缴/清单/待凭证登记；服务费应收/两笔回款/两次核销/余额 0.00 CNY。默认不显示 UUID、哈希和原始英文状态，展开审计信息后仍可追溯。
**期待结果**：所有对象同案；SERVICE 账单 `SETTLED`，GOV 仍明确待官方凭证核验；网络和 console 错误均为空。
**验证方法**：检查 `v6-stages.json` 01–11 顺序、对象身份、金额等式、最终截图、network/console arrays 和 PASS receipt。
**事实边界**：服务费结清不代表官费官方凭证已核验；本轮不证明正式客户输入已激活。
**停止条件**：任一轨缺失、跨案关联、英文新增状态、Network Error、console error 或事实被合并夸大。
**最近新增**：同案双轨费用概览、fresh-run evidence 和客户页面端到端验收。

演示完成后不得复用本次数据库。保留只读 evidence artifact；下一次演示必须创建不同 run ID、不同数据库与相同输入摘要的全新运行。
