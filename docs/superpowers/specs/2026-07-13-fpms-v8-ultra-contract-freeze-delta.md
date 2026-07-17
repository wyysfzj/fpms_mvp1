# FPMS V8 Ultra 契约冻结增量设计（2026-07-13）

## Purpose（目的）

本文是 V8 设计的窄范围增量，不重写 V8，也不改变客户决策门。它解决 High
执行中实际暴露的九个契约缺口，并补齐三个此前未物化的原子前置任务，使后续
开发可以继续按 TDD、独立复审和 task gate 执行。

权威继承顺序保持不变：

1. `AGENTS.md`；
2. `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`；
3. `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`；
4. 本文仅覆盖下列明确冲突或遗漏。

## Approved approach（已批准方案）

采用用户批准的方案 A：**原子前置优先、fail-closed、生产路径可达**。

- 不用测试 fake 掩盖生产 Provider 或官文费用行来源缺失。
- 不把新前置条件塞入既有任务形成 mega task。
- 对既有文档无法决定的运营策略使用最小安全默认，不激活客户决策。
- 新发现的共享前置、共享文件冲突或可达性问题通过新任务和依赖修正解决。

未采用的方案：

- 只实现可注入 fake：测试可绿，但生产入口不可达。
- 扩大既有任务：减少任务数量，但违反原子闭包和共享文件序列化。

## Frozen contracts（冻结契约）

### 1. 生命周期统一入口

任务：`FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01`。

- Public seam 保持：
  `apply_lifecycle_event(command, transaction) -> LifecycleTransitionResult`。
- `lifecycle_service.py` 定义冻结、slots、keyword-only 的
  `LifecycleRuleDecision(current_projection, oa_sequence=None)`，以及规则 callable：
  `(command, previous_projection, transaction) -> LifecycleRuleDecision`。
- 通过延迟加载 `lifecycle_rules.get_lifecycle_rule(event_type)` 取得规则。统一入口
  不包含具体事件规则；未注册事件返回 409 `LIFECYCLE_RULE_NOT_REGISTERED`。
- 本入口只接受 `lane=LIFECYCLE` 且 `confirmation_status=CONFIRMED`。一次性
  `LEGACY_IMPORT/LEGACY_UNVERIFIED` 继续走其独立导入任务和 append seam。
- 新事件先读取同案投影和兼容状态，再调用只读规则；规则结果必须是精确类型。
- 兼容状态只由 `project_legacy_case_status()` 单向派生。OA 次数来自规则决定，且
  OA 事件的 canonical payload 必须保存同一 `oa_sequence`，用于稳定重放。
- `RETAINED_CONFLICT` 返回 409 `LIFECYCLE_LEGACY_PROJECTION_CONFLICT`，整个调用
  无写入；不得猜测或直接保留后继续中央状态变化。
- 同案同幂等键重放先读取已存 activity，重建其旧/新投影并按已存事件及 payload
  派生原兼容状态，再交给 `append_case_activity()` 做完整事实/证据比较。案件后来
  已前进不得使原请求失去可重放性。
- 规则解析失败或返回错误类型为 409；command 形状/lane/status 错误为 400；
  append seam 的 404、409、CAS 和 caller-owned transaction 语义原样保留。
- 不新增通用 HTTP lifecycle-write endpoint。

### 2. 案件完整更新的状态输入门禁

任务：`FPMS-V8-CASE-UPDATE-STATUS-INPUT-GATE-20260712-01`。

- 仅当 `business_stage`、`official_procedure_stage`、`legal_status`、
  `lifecycle_verification_status`、`lifecycle_revision` 五项全部为 `NULL` 时，案件
  才视为 lifecycle inactive。
- 任一项非空即受生命周期保护；残缺值、非法枚举、revision `0` 或负数也按受保护
  处理，不在本任务修复存量数据。
- `status` 省略、显式 `null` 或显式同值均为 no-op，允许其他字段继续更新。
- 受保护案件显式提交不同状态返回 409：
  `CASE_STATUS_MANAGED_BY_LIFECYCLE` / `案件状态已由生命周期管理，不能直接修改`。
  details 固定包含 `case_id/current_status/requested_status/lifecycle_revision`。
- 五项全空的旧案件继续使用原 transition 和 required-field 规则。
- 门禁位于 Case 读取之后、其他校验或 ORM 修改之前。旧案件的状态写入使用“五项
  仍全空且原状态未变”的 CAS；失败返回同一 409，确保无 TOCTOU 和部分更新。

### 3. 客户费用指示

任务：`FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01`。

- Public seam：
  `record_client_instruction(command, transaction) -> RecordFeeObligationInstructionResult`，
  复用已冻结 FO DTO/枚举。
- 只有 `RECOGNIZED + NOT_CREATED + UNPAID + official evidence 未 VERIFIED` 的义务
  可接受新的 `PAY/HOLD/ABANDON`。
- `PENDING/PAY/HOLD/ABANDON` 可在下游执行前切换到不同目标；新幂等键的同态输入
  返回 409，同键同事实返回原结果 `reused=True`。
- 已建草单、已支付、已有官方缴费凭证或义务已 supersede 后，默认禁止修改指示。
- `ABANDON` 仅表示不执行该费用义务，不改变案件法律状态或表示放弃专利权。
- 追加 `FEE_CLIENT_INSTRUCTION_RECORDED` FEE activity；来源为唯一 recognition
  activity，变更指示 supersede 上一指示 activity，中央投影和 `Case.status` 不变。
- payload schema 固定为 `FPMS_FEE_CLIENT_INSTRUCTION_RECORDED_V1`；header CAS、
  activity append 和 revision 位于同一 SAVEPOINT，service 只 flush。
- 默认不强制上传客户指示原文；认证操作者和 activity 是本任务审计事实。未来附件
  要求另立任务。

### 4. 官费版本来源审批与激活

任务：`FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01`。

- 激活一个已持久化 candidate；创建/import candidate 不属于本任务。
- Command 精确包含 `rate_book_id`、approval actor/time、activation actor/time、
  `expected_current_rate_book_id`。两个 actor 必须是 active user，默认允许同一人；
  API/授权岗位与未来四眼规则属于运营层。
- `source_snapshot` 使用 schema `CNIPA_RATE_SOURCE_V1`、canonical JSON 和双层
  SHA-256。来源 URL 默认只信任 canonical HTTPS `www.cnipa.gov.cn`；客户 Excel、
  天悦网页、其他商业域和未核实内容均不得激活。
- effective interval 为闭区间；ACTIVE/RETIRED 全历史不得重叠，同日衔接也算重叠。
  不猜测或自动截短开放区间。
- exact replay 返回 `REUSED`；不同 payload、expected-current 不符或唯一键竞争
  返回 409。前版 RETIRED 与新版本 ACTIVE 在同一 SAVEPOINT 内完成。
- seed 不创建、审批、激活或链接真实 rate book；没有已复核 CNIPA snapshot、hash、
  version、effective interval 和责任人时保持未激活。
- 详细 snapshot 字段和错误矩阵以
  `artifacts/FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01/analysis/ultra_freeze_proposal.md`
  为任务物化输入。

### 5. 费减批准记录

任务：`FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01`。

- Public seam：`record_fee_reduction_approval(command, transaction)`；命令/结果为
  frozen、slots、keyword-only DTO。
- 只接受精确有限 Decimal `0.7` 或 `0.85`；`0` 不需要批准记录。`0.85` 要求一个
  申请人，`0.7` 要求至少两个不同申请人。
- CASE 和 canonical APPLICANT_SET 身份互斥；申请人集合排序、严格 JSON、snapshot
  及 SHA-256 均由 service 生成，拒绝重复键、NaN/Infinity 和调用方预算身份。
- 来源 evidence version 必须同案、FINAL、APPROVED、录入时 current，且实际 hash
  等于 expected hash。批准形成后不因证据后来不再 current 而改写历史。
- fee code 集合、可选年度闭区间、有效期闭区间均显式提供，不推断。
- 现有 carrier 没有 current/supersede/CAS 字段，因此使用确定性 identity、精确
  snapshot 比较和 SAVEPOINT 唯一竞争复用；不得伪造“当前批准”。
- 重叠批准保留历史；后续读取出现多个适用记录时 409，不自动选择或覆盖。
- 客户资格属性词汇与新批准是否替代旧批准仍是后续客户决策；默认只保存带版本的
  opaque eligibility attributes，不推断。

### 6. PayList 导出产物 carrier

任务：`FPMS-V8-PAYLIST-EXPORT-ARTIFACT-CARRIER-20260712-01`。

- 新增唯一表/ORM：`t_pay_list_export_artifact` / `PayListExportArtifact`。
- kind 仅 `INTERNAL_XLSX|OFFICIAL_XLSM`；status 仅
  `GENERATED|OFFICIAL_SITE_ACCEPTED`。
- 保存 PayList FK、content SHA-256、managed storage path、nullable template version、
  generated actor/time、同 PayList scoped idempotency key、nullable official-site
  acceptance evidence ref/hash/time 和 updated_at。
- INTERNAL 不得带 template version 或官方接受证明；OFFICIAL_XLSM 必须有 template
  version；OFFICIAL_SITE_ACCEPTED 必须完整携带 ref/hash/time。
- 不增加 UPLOADED、PAID、ticket、failure 或“当前 artifact”状态；不唯一 content
  hash。`DG-PAYMENT-WORKBOOK` 未确认时只能生成 INTERNAL。
- Migration 紧接当前 official-rate-book head，SQLite 使用 String UUID、
  `CURRENT_TIMESTAMP`、FK/CHECK/UNIQUE/index，forward-only。

### 7. 客户决策门读取

任务：`FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01`。

- Public seam：`resolve_decision_gate(command, transaction) -> DecisionGateReadResult`；
  command 精确包含 gate enum、scope key、调用方提供的 naive `as_of`。
- 非 legacy：`GLOBAL` 精确读取；`case:<id>` 按 `case > GLOBAL`。
- legacy form：只接受 `form-001..form-022`，按 `form-NNN > ALL-22`；`ALL-22` 不是
  单项公共请求，只作为完整 22 项 map 的 fallback carrier。
- 更具体 current row 即使 REVOKED、future 或 corrupt，也必须阻断 fallback。
- `as_of` 只判断 current row 是否已生效，不做 bitemporal 历史重建；未来 current
  不得复活旧 confirmed row。
- absence、revocation、future、scope/current identity 不一致、candidate multiplicity
  和 corrupt ALL-22 均 409；非法 command/scope/aware datetime 为 400。
- 单次 SELECT、只读、无 clock、flush、commit、rollback 或任何状态推断。

### 8. 授权当年年费义务

任务：`FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01`。

- 该 adapter 只消费“已复核、不可变的官文费用行快照”，不得 OCR、解析 PDF、读取
  `task.gov_fee_amt`、查 rate book 猜金额、判断费减资格或创建草单。
- 每行显式包含非空 fee name、正整数且不重复 year、正且最多两位小数的 source
  amount、精确 `0/0.7/0.85` reduction ratio。
- patent category 仅映射 INV/UM/DES 对应年费 code；其他值 409。
- obligation 固定 GOV/CNY/GRANT_YEAR_ANNUITY，due date 与 source document 来自
  confirmed GrantFeeTask 谱系；来源 activity 必须是同案、CONFIRMED 的
  `GRANT_REGISTRATION_NOTICE_RECORDED`，其 evidence 和 fee-line snapshot 必须匹配。
- 真实官文金额原样成为 payable/source amount；full amount 保持空，difference
  review 为 REVIEW_REQUIRED，不自动补登记费或“年登印费”。
- 更正通知只按唯一直接 predecessor supersede 旧义务；歧义或无谱系冲突 409。
- 只调用 `recognize_obligation()`，不重复追加 FEE activity，不创建草单。
- 默认不自动出授权当年年费草单，也不添加官文未列费用。

### 9. 官费估算 HTTP adapter

任务：`FPMS-V8-FO-PREVIEW-HTTP-ADAPTER-20260712-01`。

- 保留 `POST /api/v1/fees/official-fee-preview` 与函数参数权限 `Fee.Read`。
- Strict request（extra forbid）必须显式包含 `case_id`、
  `trigger_context {trigger, source_document_id}`、`currency=CNY`、
  `rate_effective_on`。日期只来自请求，禁止系统时间、案件日期或文书日期兜底。
- 旧 `trigger_event` shape 返回 422，不做静默兼容。
- Direct response 精确投影 `FeeEstimate`，固定 `estimate_status="ESTIMATE"`；金额为
  两位小数字符串、比例为四位小数字符串、日期 ISO，保持 candidate 顺序。
- 不返回 obligation/draft/activity/pay-list/payment/idempotency ID。
- 200 success；400 仅 invalid command/unsupported trigger；401/403；404 case；
  409 rate/source/reduction/ambiguity；422 Pydantic shape/type。
- API 只能注入生产 `SqlAlchemyOfficialFeeEstimateRateProvider`；禁止旧
  `preview_official_fee_candidates` 或未关联 FeeRate fallback。
- success 和所有 error 都必须证明不创建 obligation、draft、activity 或 payment。

## New atomic prerequisites（新增原子前置任务）

### A. `FPMS-V8-GRANT-NOTICE-FEE-LINE-SNAPSHOT-20260713-01`

- Closure：定义并验证 canonical `GrantFeeLines` JSON snapshot；从来源 Document 的
  existing `extra_data` 读取显式费用行，绑定 reviewed evidence-version ID/hash，生成
  canonical snapshot/hash；不 OCR、不改 schema、不创建义务。
- 建议 source/test：`backend/app/modules/documents/grant_fee_lines.py` 与一个 exact test。
- `FPMS-V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-20260712-01` 随后把 snapshot/hash 写入
  immutable lifecycle activity payload；grant-year adapter 只消费该 activity 事实，
  不重新信任可变 Document.extra_data。

### B. `FPMS-V8-OFFICIAL-FEE-ESTIMATE-RATE-PROVIDER-20260713-01`

- Closure：只读 `SqlAlchemyOfficialFeeEstimateRateProvider(Session)`，把已激活
  OfficialRateBook/关联 FeeRate 和已实现的具体 rate rule 映射到冻结 provider DTO。
- 建议 source/test：`backend/app/modules/fees/official_rate_book.py` 与一个 exact test。
- 只 SELECT；缺失、未审批、区间歧义、来源不可信均 fail-closed；不实现 HTTP、
  preview calculation、obligation 或 legacy fallback。

### C. `FPMS-V8-OFFICIAL-FEE-PREVIEW-LEGACY-TEST-MIGRATION-20260713-01`

- Closure：仅迁移 `backend/tests/test_official_fee_preview_api.py` 中被 V8 废止的旧
  request/unlinked-rate expectation，使其验证 strict V8 request 和 no fallback。
- 不为维持旧测试而恢复产品兼容路径，不修改产品源码。

## Dependency and runbook corrections（依赖与 runbook 修正）

- LC apply seam：`prereq_dependency_density=medium`，改用
  `P0-prereq-heavy-story`；首个 lifecycle rule 任务必须实现冻结 registry interface。
- Case update status gate：增加 CAS 验收，不增加新依赖。
- Fee-reduction approval：新增已 PASS 的
  `FPMS-V8-DE-REVIEW-SERVICE-20260712-01`；dependency medium、evidence high、
  `P0-prereq-heavy-story`。
- Grant-year annuity：依赖新增 fee-line snapshot、grant-notice lifecycle adapter 和
  FO recognize；dependency high、evidence high、`P0-prereq-heavy-story`。
- Preview HTTP：依赖 rate provider；legacy test migration 在 HTTP 后串行，并在
  Foundation close 前完成。
- Provider：依赖 official-rate-book activation 及其实际支持的 rate-rule tasks。
- PayList carrier 继续占用 GLOBAL_ALEMBIC_HEAD，所有 migration/SQLite verification
  串行。
- 所有 task allowlist、batch manifest、catalog/dependency/shared-file index 必须在
  task materialization 批次中同步更新；不得只改 prose。

## Non-closure（非闭包）

本文不实施任何服务、API、schema、migration、UI、测试或客户决策；不激活真实
费率、官方工作簿、自动草单、legacy form 或授权法律状态；不承诺 CPC/RPA/邮件
直连；不修改 Tasks 01–23 历史；不执行 repo-wide gate；不 commit/push。

## Acceptance（验收）

本文通过后，下一阶段只做契约物化：

1. 九个既有任务分别写入上述 exact contract、dependency、runbook、RED/GREEN；
2. 新建三个原子任务及 explicit batch manifest；
3. 重建 catalog/dependency/shared-file materialization 并做独立审查；
4. 用户确认书面 spec 后，才切回 High 执行 implementation；
5. High 继续一 agent 一 task、maximal safe waves、SQLite/shared-file 串行、独立复审
   和 atomic task gates。
