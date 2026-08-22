# FPMS V8 Ultra 契约冻结增量设计 2（2026-07-14）

## Purpose

本文是 2026-07-13 Ultra delta 的第二个窄范围增量。它只处理该 delta 之后
High 执行实际暴露的八个阻塞，以及一个必然要求公开 DTO 的 overlay preflight。
它不重写 V8，不重做 43 个已 PASS Foundation 任务，也不重新生成 283/197/86
不可变基线。

本增量的目标是一次性解除已经证实的契约、旧测试、共享文件顺序和前端调用点
冲突，使下一次 High continuation 可以按 maximal safe wave 继续，而不再为同一类
公开合同歧义反复切回 Ultra。

## Scope and precedence

权威继承顺序：

1. `AGENTS.md`；
2. `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`；
3. `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`；
4. `docs/superpowers/specs/2026-07-13-fpms-v8-ultra-contract-freeze-delta.md`；
5. 本文只覆盖下列明确 blocker 或 public-contract omission。

采用的本地事实包括：

- High blocker task/summary/evidence；
- 已接受的 lifecycle/document/fee/decision-gate deep-module contracts；
- 当前 module API、ORM 和继承测试；
- 客户 Functional Spec 中“旧附件分类不得等同稳定官方角色”的边界；
- 三线 overlay 设计 §6.4/§10 及其后续 join、cursor、HTTP、FE 任务。

本文不重新复核全部客户原始资料，因为本轮不改变已冻结业务语义；只有附件角色
冲突使用了已索引客户来源来证明不能猜测正式法律证据角色。

## Story Shape Classification

- `shared_file_density`: high — lifecycle registry、evidence contracts/policy、fees API
  与 frontend fee API 都有严格串行链。
- `prereq_dependency_density`: high — 两个外部原子前置分别解除 accepted-test 和
  evidence-role 冲突；frontend callsite 已有 canonical 原子任务拥有。
- `be_fe_coupling`: high — strict preview backend contract 已 PASS，frontend adapter
  与旧页面调用必须按明确顺序迁移。
- `evidence_cost`: high — 每个实施任务仍独立 TDD/evidence/review/gate；本轮 Ultra
  只做 deterministic task materialization evidence。
- `chosen_runbook`: `P0-prereq-heavy-story`。

## Approved approach

采用最小增量、fail-closed、生产路径可达方案：

- 保留 2026-07-13 delta overlay；新建 delta-2 overlay，不修改旧 PASS 历史。
- 只为真实冲突新建两个原子前置；不把第二 closure 塞回旧任务。
- 不把旧附件角色猜成正式证据角色；未分类附件只能进入非门禁角色。
- 不恢复 strict preview 已废止的旧 wire shape；迁移旧调用点。
- read service 使用现有持久化事实，不等待尚未冻结的未来 activity 来制造依赖环。
- public API、DTO、错误、事务和 cursor 必须冻结；纯内部局部实现细节留给 High。
- 本文完成后先物化 task contracts；产品 RED/GREEN 仍由 High 执行。

未采用：

- 扩大现有 blocker allowlist 吸收旧测试/页面：违反一任务一 closure。
- 将 18 个附件角色近似映射到 9 个法律证据角色：会制造虚假证据语义。
- 用 legacy frontend overload 维持旧调用：会削弱 strict V8 request。
- 对所有尚未开始的一行 catalog task 做全量再设计：成本高且超出真实 blocker。

## New atomic prerequisites

### P1. `FPMS-V8-LC-RULE-REGISTRY-LEGACY-TEST-MIGRATION-20260714-01`

唯一 closure：迁移 accepted CASE_OPENED 测试中的未来事件否定断言，使其只验证
CASE_OPENED 和一个真正未知事件，不永久禁止后续合法 registry 扩展。

- 只允许修改 `backend/tests/test_v8_lifecycle_case_opened.py`、任务和 evidence。
- 将 `get_lifecycle_rule("FILING_PREPARATION_STARTED") is None` 改为
  `get_lifecycle_rule("UNREGISTERED_EVENT") is None`。
- RED：当前 accepted test 与注册第二个合法事件冲突。
- GREEN：CASE_OPENED exact contract 仍全绿，测试不再声明未来合法事件不存在。
- 不修改 lifecycle product source，不注册任何事件。
- `FPMS-V8-LC-FILING-PREPARATION-STARTED-20260712-01` 新增本任务为前置。

### P2. `FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01`

唯一 closure：在 document deep contract 中追加一个 fail-closed intake role：

```python
class EvidenceRole(str, Enum):
    # 原九项顺序保持不变
    RAW_ATTACHMENT = "RAW_ATTACHMENT"
```

`RAW_ATTACHMENT` 表示由通用 attachment POST 保存、但尚未由专用业务 adapter
证明其正式语义的原始附件。它有以下硬边界：

- 不满足 filing、OA、grant、external-submission 或 receipt gate；
- 不等于 `FILING_COMPONENT`、`OFFICIAL_FINAL_PDF`、`SUBMITTED_XML` 或
  `OFFICIAL_RECEIPT`；
- 后续专用 adapter 必须登记新的正式角色版本/派生事实，不能原地改写角色；
- 相同 hash 不表示相同法律证据。

只允许修改：

- `backend/app/modules/documents/evidence_contracts.py`；
- `backend/tests/test_v8_document_evidence_contracts.py`；
- 任务和 evidence。

RED/GREEN 只证明第十个 enum member、顺序和非门禁定义；不改上传 API/service。
原 `FPMS-V8-DE-CONTRACTS-20260712-01` 保持历史 PASS，本任务是 additive contract
extension，不重写其 evidence。

## Frozen contract overrides

### 1. Lifecycle `FILING_PREPARATION_STARTED`

任务：`FPMS-V8-LC-FILING-PREPARATION-STARTED-20260712-01`。

- 保持 exact closure：只把 `business_stage` 从 `NEW_CASE` 改为
  `FILING_PREPARATION`；其他三项投影不变，`oa_sequence=None`。
- 只注册 exact uppercase event；未知或 malformed input 返回 `None`，由 apply seam
  转为已冻结 409。
- 只读规则，不访问 transaction；前一投影必须为 exact CASE_OPENED projection。
- 依赖顺序改为 CASE_OPENED → legacy-test migration → 本任务。
- `lifecycle_rules.py` order key 保持 `2`，不得与后续 event rule 并发。
- 本任务解除 blocker 后重新跑自己的 RED/GREEN；不得修改 inherited CASE_OPENED
  test。

### 2. Filing XML reviewed-Word lineage policy

任务：`FPMS-V8-FILING-XML-DERIVATION-GATE-20260712-01`。

共享顺序修正：先完成
`FPMS-V8-FILING-FULL-WORD-READINESS-GATE-20260712-01`，再运行本任务；两者都编辑
`evidence_policy.py`，不得并发或从被拒绝 candidate 直接续跑。

公开 callable 保持纯只读规则：

```python
def require_filing_xml_reviewed_word_source(
    *,
    case_id: str,
    source_word: DocumentEvidenceVersion,
    xml_evidence: DocumentEvidenceVersion,
    parent_xml_evidence: DocumentEvidenceVersion | None,
    source_derivation: DocumentEvidenceDerivation,
    submission_derivation: DocumentEvidenceDerivation | None,
) -> None:
```

精确路径：

- `EXTERNAL_XML_PACKAGE`：`parent_xml_evidence=None`，且唯一 edge 为
  `source_word -> xml_evidence` / `FORMAT_CONVERSION`；
- `SUBMITTED_XML`：`parent_xml_evidence` 必须是同案同 lineage 的
  `EXTERNAL_XML_PACKAGE`；两条 edge 必须依次为
  `source_word -> parent` / `FORMAT_CONVERSION` 和
  `parent -> xml_evidence` / `EXTERNAL_SUBMISSION`；
- source 必须为同案 current、`FILING_FULL_WORD`、`APPROVED`，且 reviewer 非
  creator、reviewed_at 为 naive datetime；
- 所有对象、edge、case、lineage、parent/child identity 必须精确匹配。

公开 error enum 在现有 candidate 基础上冻结：

```text
FILING_XML_DERIVATION_INVALID_CONTEXT
FILING_XML_SOURCE_NOT_FILING_WORD
FILING_XML_SOURCE_NOT_CURRENT
FILING_XML_SOURCE_NOT_APPROVED
FILING_XML_SOURCE_NOT_INDEPENDENTLY_REVIEWED
FILING_XML_TARGET_NOT_XML
FILING_XML_DERIVATION_CASE_MISMATCH
FILING_XML_DERIVATION_LINEAGE_MISMATCH
FILING_XML_DERIVATION_PATH_SHAPE_MISMATCH
FILING_XML_DERIVATION_EDGE_MISMATCH
FILING_XML_DERIVATION_TYPE_MISMATCH
```

异常仍为 `FilingXmlDerivationPolicyError(ValueError)`，暴露 `.code`；规则无 ORM
query/write、XML parsing/generation、zip handling、clock 或 transaction side effect。

### 3. Generic attachment evidence atomic adapter

任务：`FPMS-V8-DE-ATTACHMENT-EVIDENCE-ATOMIC-ADAPTER-20260712-01`，新增 P2 前置。

HTTP wire 保持现有 multipart attachment POST、`Doc.Attach`、201
`DocAttachmentOut`；不新增 evidence form field，不提前改变响应体。API 增加
`current_user: T_User = current_user_dep`，actor 必须是 `current_user.id`。

通用上传映射以原始 multipart `official_file_role` 字段为唯一法律角色判定输入，
并且必须在 `_resolve_attachment_manifest_metadata()` 的 legacy alias 归一化之前、
与其持久化展示元数据相互独立地决定：

- 原始字段 exact `FILING_FULL_WORD` → `EvidenceRole.FILING_FULL_WORD`；
- 其余 17 个现有 official-file roles、空 role 和 alias-only upload →
  `EvidenceRole.RAW_ATTACHMENT`；
- alias-only 包括 `source_role_alias="完整递交文件"`：即使 legacy metadata resolver
  为兼容展示把持久化 `DocAttachment.official_file_role` 归一化成
  `FILING_FULL_WORD`，该请求的 evidence role 仍必须是 `RAW_ATTACHMENT`；不得从
  归一化后的附件元数据反向推断法律证据角色；
- 初始 evidence state/review 固定 `DRAFT/PENDING`；
- `lineage_key=f"attachment:{attachment.id}"`；每个成功 POST 建独立 lineage，
  version `1`；不按 hash 去重或推断替换。

不得把 OA PDF、XML ZIP、电子回执、内部合并 PDF、技术交底或委托指示映射成
正式提交、官方 PDF/XML、回执或 filing component。其晋升属于专用 adapter。

服务返回未提交结果：

```python
@dataclass(frozen=True, slots=True)
class PendingAttachmentEvidenceUpload:
    attachment: DocAttachment
    evidence_version: EvidenceVersionResult
    managed_file_path: Path
```

服务写 managed file、attachment、version、DOCUMENT activity/evidence link 并只
flush；API 是外层 transaction owner，只 commit 一次。EvidenceVersion creator 和
DOCUMENT activity actor 都必须是 `current_user.id`，不得继续传 `actor_id=None`。

本任务不吸收既有
`FPMS-V8-GRANT-ATTACHMENT-NO-GRANTED-20260712-01` 的独立 closure，也不删除或
重定义 `_advance_grant_notice_case_after_attachment()`：

- attachment evidence adapter 自身不得新增 legal status、fee obligation、draft、
  payment 或 grant-lifecycle inference；
- 现有 `T_GrantFeeTask` 只保留为 V8 §6.3 已接受的兼容下游 execution carrier，不是
  `FeeObligation`，其现存 ensure 调用与 attachment/evidence 写入处于同一 outer
  transaction；
- 现存 attachment → `Case.status=GRANTED` shortcut 是明确 residual，只由 task 75
  独立删除。Foundation close 与 direct-status-write gate 必须依赖 task 75 PASS；
  在此之前不得声称通用 attachment 已法律状态中立；
- attachment adapter 和 task 75 继续按 `documents/service.py` order key `1`、`7`
  串行，不得并发，也不得互相吞并 closure。

managed file 的补偿责任和顺序冻结如下；数据库与文件系统不是 XA：

1. service 先完成 document、显式角色、文件名、MIME 和 actor 校验；managed file
   创建前失败时不执行删除；
2. 文件写入过程中失败时，service 删除已创建路径。既有业务校验（例如超限）在
   补偿成功后保留原 400；普通 storage exception 转为
   `ATTACHMENT_STORAGE_WRITE_FAILED`；
3. service 在文件已创建后、返回 `PendingAttachmentEvidenceUpload` 前的任何
   attachment/version/activity/link validation 或 flush 失败，由 service 删除文件后
   重新抛出：`BusinessError` 保持原样，普通异常转为
   `ATTACHMENT_PERSIST_FAILED`；service 不 commit/rollback；
4. API 捕获 service pre-return failure 时 rollback；API 收到 pending result 后调用
   commit，commit 失败时 API 先 rollback，再同步删除 `managed_file_path`，然后抛出
   `ATTACHMENT_PERSIST_FAILED`；
5. 任一需要删除的路径若删除失败，补偿错误优先于原始 persistence/write 错误，
   统一返回 `ATTACHMENT_STORAGE_COMPENSATION_FAILED`，记录原始异常和残留路径到
   server log；响应不得暴露绝对路径、残留相对路径或原始文件名；
6. `FileNotFoundError` 视为补偿成功。service pre-return cleanup 成功后不得把
   不存在的 path 交给 API；API 只补偿已经收到 pending result 的 commit failure，
   避免双重删除；commit 成功即结束补偿窗口。

任何 database/service 失败按上述边界 rollback；managed file 采用同步补偿删除：

- 补偿成功但持久化失败：500 `ATTACHMENT_PERSIST_FAILED`；
- 文件写失败：500 `ATTACHMENT_STORAGE_WRITE_FAILED`；
- rollback 后补偿删除失败：500 `ATTACHMENT_STORAGE_COMPENSATION_FAILED`，必须
  明确记录残留，不能声称完整回滚。

400 沿用文件/关系业务校验；401/403；404 `DOCUMENT_NOT_FOUND`；409 保留
lifecycle projection conflict；缺 file 为 422。相同成功请求再次 POST 仍创建新
事实，不提供 HTTP idempotency。

### 4. Customer decision-gate record HTTP

任务：`FPMS-V8-DECISION-GATE-CONFIRM-API-20260712-01`。

唯一 route：

```text
POST /api/v1/system/decision-gates
```

同一 resource-collection endpoint 通过 `decision_status=CONFIRMED|REVOKED` 支持
确认、撤销和撤销后重确认；不创建 `/confirm` 或 `/revoke` 第二 endpoint。

Strict request `DecisionGateRecordIn` 使用 `ConfigDict(extra="forbid")`，字段顺序：

```text
gate_code: DecisionGateCode
scope_key: str
decision_value: str | None
decision_status: DecisionGateStatus
source_reference: str
source_version: str
effective_at: datetime
idempotency_key: str
expected_current_gate_id: str | None
```

所有字段 required，包括两个 nullable 字段。`confirmed_by` 是 server-owned
`current_user.id`；客户端提交它为 extra，返回 422。schema 只处理 JSON
shape/type/enum/datetime parsing；scope/value/aware datetime 等业务校验交给已 PASS
record service，保持其 400 顺序。

Direct response `DecisionGateRecordOut` 无 success envelope，逐字段镜像 accepted
`DecisionGateRecordResult`：

```text
gate_id, gate_code, scope_key, decision_value, decision_status,
source_reference, source_version, confirmed_by, effective_at,
supersedes_gate_id, decision_snapshot, idempotency_key,
current_identity_key, disposition
```

`CREATED` 返回 201；`REUSED` 返回 200 且完整 body/gate_id 不变。API 构造 command，
不复制业务规则；调用 service 后 commit 一次。BusinessError 或 commit failure 均
rollback 并原样抛出；不 refresh/二次 SELECT。

错误：401/403；400 `DECISION_GATE_INVALID`；正常认证下 actor 404 不应出现但删除
竞态仍原样透传；现有 idempotency/current/revocation/write 409 原样透传；422 只属
request validation。

### 5. Fee-obligation client-instruction HTTP

任务：`FPMS-V8-FO-INSTRUCTION-HTTP-20260712-01`。

唯一 route：

```text
POST /api/v1/fees/obligations/{obligation_id}/instruction
```

`obligation_id` 只在 path；strict body `FeeObligationInstructionIn`：

```text
instruction: FeeClientInstruction  # PAY|HOLD|ABANDON
idempotency_key: str
```

`actor_id` 为 server-owned `current_user.id`；body extra forbid。Direct response
`FeeObligationInstructionOut`：

```text
obligation_id: str
client_instruction_status: FeeClientInstructionStatus
activity_id: str
idempotency_key: str
reused: bool
```

成功和 exact replay 均 200。adapter 只调用已 PASS
`record_client_instruction()`；不得创建 draft、PayList、payment 或法律状态变化。
API 是 outer transaction owner：success（含 reused）commit 一次；BusinessError 或
commit failure rollback；不修改 service error code/details。

错误矩阵：401/403；path/body well-typed 但业务非法为 service 400；missing obligation
404；non-actionable、same-state-new-key、idempotency/current conflict 为现有 409；
shape/enum/extra 为 422。不得恢复第二 route 或 legacy request。

### 6. Official-fee preview frontend adapter and callsite

任务：`FPMS-V8-FO-PREVIEW-FE-ADAPTER-20260712-01`。

保留已冻结 exact exports：`OfficialFeeEstimateContext`、
`OfficialFeeEstimateResult`、existing `previewOfficialFeeCandidates`。类型必须镜像
strict backend：

```text
case_id
trigger_context { trigger, source_document_id }
currency 'CNY'
rate_effective_on YYYY-MM-DD
estimate_status 'ESTIMATE'
candidates[].line decimal strings
candidates[].source provenance/status
total_payable_amount decimal string
```

无 obligation/draft/activity/payment/idempotency identity。

为打破旧 `CaseFeesTab.vue` dependency cycle，adapter task 的 GREEN 改为：

- dedicated contract probe 的 isolated TypeScript compile；
- exact-file ESLint；
- scoped diff/evidence/gate。

它不在旧 callsite 尚未迁移时运行 full frontend typecheck，也不把该已知 expected
failure 报成 repo regression。既有 canonical
`FPMS-V8-CASE-FEES-ESTIMATE-OBLIGATION-UI-ADAPTER-20260712-01` 已精确拥有
`CaseFeesTab.vue` 与
`FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-fees-estimate-obligation.spec.ts`；
该任务在 FE adapter 和 overlay FE adapter 就绪后迁移旧 callsite、执行 exact
Playwright、exact-file ESLint 及其物化后要求的 full typecheck。不得创建重复前置，
不得让两个任务并发拥有同一页面或 Playwright 文件。

顺序固定：preview HTTP PASS → FE adapter isolated probe → 既有 canonical fee UI
task；instruction FE adapter 仍按 `fees.ts/types.ts` shared-file order 串行，但不拥有
`CaseFeesTab.vue`。

建议 isolated probe command：

```bash
cd frontend && npx tsc --noEmit --skipLibCheck --target ES2022 \
  --module ESNext --moduleResolution Bundler \
  src/api/contracts/v8_fee_estimate_preview.contract.ts
```

High 可在 RED 后按当前 frontend toolchain 做等价的最小参数修正，但不得改成 full
scope 或加入 legacy overload。

### 7. Fee-obligation detail read

任务：`FPMS-V8-FO-OBLIGATION-DETAIL-READ-20260712-01`。

Public seam：

```python
def get_fee_obligation(
    obligation_id: str,
    transaction: Session,
) -> FeeObligation:
```

直接复用 frozen `FeeObligation` 及嵌套 DTO；不新建重复 read DTO。

- ID 必须 exact nonblank stripped string、无 NUL、长度 ≤36；否则 400
  `FEE_OBLIGATION_DETAIL_INVALID`，details `{"field":"obligation_id"}`，0 SQL。
- header 不存在：404 `FEE_OBLIGATION_NOT_FOUND`。
- header 存在后的 missing/cross-link/malformed/multiplicity：409
  `FEE_OBLIGATION_STORED_STATE_INVALID`，不得伪装为 request 404。
- `estimate_status=None`；header 的 obligation/instruction/draft/payment/official
  evidence status 严格 enum 投影，不互相推断。
- `pay_list_status=CREATED` 当且仅当存在合法持久化关系：
  `ObligationLine -> DraftItemLink -> FeeItem -> GovPayment -> PayList`；否则
  `NOT_CREATED`。不得读取 PayList/GovPayment 状态来推断 payment/evidence。
- SERVICE obligation 出现 GOV PayList 关系，或任一链路 case/currency 不一致，409。
- 至少一行；`(fee_code, fee_year_key)` 唯一；返回排序
  `(fee_code, fee_year_key, id)`；Decimal/date 不转换。
- header、lines、source activity、唯一 recognition activity/canonical payload、
  current identity/supersede 必须与 accepted recognize contract 一致。
- `SUPERSEDED` 历史 detail 合法；不只读 current。

全程 `transaction.no_autoflush` 和显式列/mapping 查询；忽略并保留未 flush
new/dirty/deleted state，不污染 identity map。禁止 add/flush/commit/rollback/
begin_nested/refresh/expire/lock/clock。invalid 0 SELECT、missing 1、success exact 4：
header、lines、source+recognition activities、PayList relation set；无 N+1。

依赖增加已 PASS `FPMS-V8-W1-F3-OBLIGATION-DRAFT-LINK-CARRIER-20260712-01`，不依赖
未来 PayList activity adapter。

### 8. First-ten-year annuity reduction scope

任务：`FPMS-V8-ANNUITY-FIRST-TEN-YEAR-REDUCTION-SCOPE-20260712-01`。

为保持已 PASS `fee_reduction.py` 的 exact `__all__`/enum contract，本任务改用独立
module：

```text
backend/app/modules/fees/annuity_reduction.py
```

Public callable：

```python
def validate_annuity_fee_reduction(
    *,
    reduction_input: FeeReductionInput,
    context: FeeReductionEvaluationContext,
    approval: FeeReductionApprovalContext | None,
    grant_fee_year_key: int,
) -> FeeReductionValidationResult:
```

- `context.fee_year_key` 与 `grant_fee_year_key` 都是同一专利年度 ordinal，不是
  calendar year 或已归一化 grant-relative year；两者为正整数。
- `grant_relative_year = context.fee_year_key - grant_fee_year_key + 1`。
- 可执行 fee code 只有 `CN_ANNUITY_FEE_INV`、`CN_ANNUITY_FEE_UM`、
  `CN_ANNUITY_FEE_DES`。
- ratio `0` 仍由 base validator 处理，不需要 statutory reduction window。
- 对合法 non-zero `0.7/0.85`，只有 relative year `1..10` 可进入 base validator；
  之前/第 11 年及以后 fail-closed。
- window 通过后仍必须由 `validate_fee_reduction()` 验证 confirmed/current source、
  fee code、patent-year interval 和 effective date scope；wrapper 不复制这些规则。

新 error surface：

```text
ANNUITY_REDUCTION_INVALID_CONTEXT
ANNUITY_REDUCTION_FEE_CODE_UNSUPPORTED
ANNUITY_REDUCTION_YEAR_OUT_OF_SCOPE
```

异常 `AnnuityReductionScopeError(ValueError)` 暴露 `.code` 和只读 `.details`。
错误优先级：wrapper shape/year/fee-code → 对 exact non-zero legal ratio 的 statutory
window → base validator；非法/missing/ambiguous ratio/provenance 始终由 base error
surface 返回，不被伪装为 year error。纯函数，无 DB/I/O/clock/money rounding。

### 9. Lifecycle overlay public contracts

任务：`FPMS-V8-OVERLAY-CONTRACTS-20260712-01`。

所有 DTO 使用 `@dataclass(frozen=True, slots=True, kw_only=True)`，集合为 tuple；
复用 deep enums/DTO，不复制其词汇。public module 明确导出下列类型。

Enums：

```text
OverlayCenterAxis: BUSINESS_STAGE | OFFICIAL_PROCEDURE_STAGE | LEGAL_STATUS
OverlayWarningKind: UNVERIFIED | CUSTOMER_DECISION_GATE | CONFLICT | REFERENCE_ONLY
OverlayFeeRelatedFactKind: DRAFT | PAY_LIST | PAYMENT | OFFICIAL_EVIDENCE
OverlayGateResolutionStatus: RESOLVED | UNRESOLVED
```

DTO fields/order：

```text
LifecycleOverlayQuery
  after_sequence: int
  limit: int
  as_of_revision: int | None

OverlayCenterSnapshot
  business_stage: BusinessStage | None
  official_procedure_stage: OfficialProcedureStage | None
  legal_status: LegalStatus | None
  effective_at: datetime | None
  verification_status: ConfirmationStatus | None
  source_event_id: str | None

OverlayCenterAxisChange
  previous_value: BusinessStage | OfficialProcedureStage | LegalStatus | None
  current_value: BusinessStage | OfficialProcedureStage | LegalStatus | None

OverlayDocumentEvidence
  version: EvidenceVersionResult
  derivations: tuple[EvidenceDerivationResult, ...]

OverlayWorkPackageReceipt
  receipt_id: str
  receipt_kind: str
  receipt_attachment_id: str | None
  receiving_case_no: str | None
  submitter: str | None
  received_at: datetime | None
  archive_status: str

OverlayWorkPackage
  package_id: str
  package_kind: str
  status: str
  source_document_id: str | None
  reply_document_id: str | None
  manifest_evidence_version_ids: tuple[str, ...]
  receipts: tuple[OverlayWorkPackageReceipt, ...]
  missing_gate_codes: tuple[str, ...]

OverlayTask
  task_id: str
  document_id: str | None
  task_template_id: str | None
  title: str | None
  due_date: date | None
  internal_due_date: date | None
  status: str
  done_at: datetime | None

OverlayFeeLine
  line_id: str
  fee_code: str
  fee_name: str
  fee_year_key: int
  official_full_amount: str | None
  reduction_ratio: str
  payable_amount: str
  source_amount: str | None
  source_date: date | None
  difference_review_state: FeeDifferenceReviewState

OverlayFeeRelatedFact
  kind: OverlayFeeRelatedFactKind
  object_id: str
  status: str

OverlayFeeObligation
  obligation_id: str
  source_activity_id: str
  source_document_id: str | None
  source_status: FeeSourceStatus
  fee_domain: FeeDomain
  obligation_type: str
  due_date: date | None
  currency: str
  statuses: FeeObligationStatuses
  lines: tuple[OverlayFeeLine, ...]
  related_facts: tuple[OverlayFeeRelatedFact, ...]
  supersedes_obligation_id: str | None
  supersede_reason: str | None

OverlayWarning
  kind: OverlayWarningKind
  code: str
  message: str
  activity_id: str | None
  source_object_type: str | None
  source_object_id: str | None

OverlayDecisionGate
  gate_code: DecisionGateCode
  requested_scope_key: str
  resolution_status: OverlayGateResolutionStatus
  gate_id: str | None
  resolved_scope_key: str | None
  decision_value: str | None
  source_reference: str | None
  source_version: str | None
  confirmed_by: str | None
  effective_at: datetime | None
  unresolved_reason: str | None

OverlayLegacyConflict
  code: str
  activity_id: str | None
  message: str | None

OverlayMilestone
  sequence: int
  activity_id: str
  lane: ActivityLane
  activity_type: str
  source_activity_id: str | None
  effective_at: datetime
  confirmation_status: ConfirmationStatus
  center_changes: Mapping[OverlayCenterAxis, OverlayCenterAxisChange]
  document_evidence: tuple[OverlayDocumentEvidence, ...]
  work_packages: tuple[OverlayWorkPackage, ...]
  tasks: tuple[OverlayTask, ...]
  fee_obligations: tuple[OverlayFeeObligation, ...]
  evidence_summary: tuple[EvidenceReference, ...]
  warnings: tuple[OverlayWarning, ...]

LifecycleOverlay
  case_id: str
  lifecycle_revision: int
  generated_at: datetime
  center_snapshot: OverlayCenterSnapshot
  milestones: tuple[OverlayMilestone, ...]
  decision_gates: tuple[OverlayDecisionGate, ...]
  warnings: tuple[OverlayWarning, ...]
  legacy_conflicts: tuple[OverlayLegacyConflict, ...]
  next_cursor: int | None
  has_more: bool
```

Wire invariants：

- DOCUMENT/FEE milestone 的 `center_changes` 必须是空 mapping，不是 `None`/list；
- fee money 在 overlay contract 中为两位 decimal string，ratio 为四位 string；
- milestone warning 保留 activity 局部关联；top-level warnings 是当前 page/snapshot
  聚合，二者都存在，聚合/去重由后续 join task 定义；
- `decision_gates` 覆盖八个 distinct `DecisionGateCode`，但固定返回 29 个 scoped
  entries，不是每个 code 只一条。按 enum 顺序遍历：七个 non-legacy code 各生成
  `requested_scope_key=f"case:{case_id}"` 一条；`DG-LEGACY-FORM-CLASS` 按升序展开
  `form-001..form-022` 二十二条。entry identity 是
  `(gate_code, requested_scope_key)`，legacy gate code 可以重复；
- overlay 绝不请求或输出 `requested_scope_key="ALL-22"`。每个 form entry 通过既有
  read service 以其 exact `form-NNN` 请求；若 resolver 选择 fallback carrier，结果
  仍无损保留 `requested_scope_key=form-NNN`、`resolved_scope_key=ALL-22` 及该 form
  的提取值和来源；
- 一次 overlay invocation 只捕获一个 timezone-naive UTC `generated_at`，并把同一值
  作为全部 29 次 resolve 的 `as_of`，复用同一 caller transaction；不得直接查询
  `ALL-22`、复制 scope precedence 或加入 blanket fallback；
- 每个 entry 独立解析。read service 的
  `DECISION_GATE_NOT_FOUND|DECISION_GATE_REVOKED|DECISION_GATE_NOT_EFFECTIVE|DECISION_GATE_CANDIDATE_MULTIPLICITY|DECISION_GATE_CURRENT_IDENTITY_CONFLICT|DECISION_GATE_CURRENT_ROW_CORRUPT|DECISION_GATE_LEGACY_MAP_CORRUPT`
  409 只把该 entry 投影为 `UNRESOLVED`，`unresolved_reason` 原样使用 error code，
  record/source fields 全为 `None`；不得阻断其他 28 entries 或三条主线；
- 内部构造若触发 400 `DECISION_GATE_INVALID`，属于 overlay contract defect，必须
  fail whole request 为 409 `LIFECYCLE_OVERLAY_DECISION_GATE_CONTRACT_INVALID`；
  其他 unexpected error 不得吞掉或伪装为普通 unresolved；
- resolved gate 无损投影 read result。legacy value `HISTORICAL|INTERNAL_ONLY` 仍是
  有来源支持的 `RESOLVED` 分类，但仅作 reference-only；只有
  `CURRENT_OFFICIAL` 可供后续对应 form lane activation，overlay 自身不激活；
- schema task 不查询 DB、不决定 join/applicability 或 UI 文案；其 tuple contract
  必须允许重复 gate code。后续 HTTP/FE 以 composite identity 为 key，不得按
  gate code 去重。

Cursor：

- 首次 `after_sequence=0, as_of_revision=None`；
- service 读取并冻结 revision `R`；后续请求必须复用 `as_of_revision=R`；
- page 条件 `sequence > after_sequence AND sequence <= R`；
- `next_cursor` 仅在 `has_more=True` 时等于本页最后 sequence，否则 `None`；
- query limit 业务校验由 keyset task 冻结；contract 只固定字段和类型。

## Dependency and runbook corrections

- 新增两个 external Foundation prerequisite；effective Foundation close 从 200 增至
  202 个要求，但不可变 baseline 仍为 197，旧 delta effective count 仍为 200。
- lifecycle chain：CASE_OPENED → P1 → FILING_PREPARATION_STARTED → 后续 event rules。
- document contracts：原 DE-CONTRACTS PASS → P2 → attachment evidence adapter；
  既有 shared order 保持 attachment adapter `1` → grant notice lifecycle adapter
  `6` → `GRANT-ATTACHMENT-NO-GRANTED` `7`。P2 不是旧 catalog row，也不改旧 PASS
  evidence；编辑 `documents/service.py` 的任务必须串行。Foundation close 和
  direct-status-write gate 仍要求 task 75 PASS。
- evidence policy chain：full-Word readiness → XML derivation gate。
- fee preview frontend chain：preview HTTP PASS → FE adapter isolated probe → 既有
  canonical fee UI task（在 overlay FE dependency 就绪后执行 exact Playwright 与
  full typecheck）；instruction FE adapter 继续按 shared `fees.ts/types.ts` 串行。
- decision-gate API、instruction HTTP、attachment API 均为 outer transaction owner；
  SQLite write tests 使用 `/tmp/fpms_v8_sqlite.lockdir` 串行。
- obligation detail read 增加 F3 dependency；保持只读，可与不共享文件的实现并行，
  但其 SQLite verification 仍进入全局队列。
- annuity scope改用独立 module，避免修改已 PASS exact `fee_reduction.py` contract。
- overlay contract 依赖 LC/DE/FO contracts、P2 及已 PASS decision-gate record service；
  后者只用于复用 exact enum，不执行 read service。overlay decision-gate join 保持
  read service + overlay fee join 依赖，验收改为 29 scoped entries；overlay HTTP、
  FE adapter 和 gates/warnings UI 继承 composite identity 与不按 code 去重要求，
  无新依赖或 shared-file owner。
- 上述 blocker tasks 统一改为 `P0-prereq-heavy-story`；P1/P2 为
  `P0-single-lane-story`。
- task materialization 必须生成 delta-2 overlay，记录 old/new dependency、task hash、
  shared-file order、202 effective close requirement，并验证无 cycle。

## Non-closure

本文不实施任何 product source/test/API/UI/schema/migration；不激活客户 decision
gate、费率、官方工作簿、自动草单或法律状态；不生成/解析真实 XML；不改变
attachment POST wire；不新增真实 OA evidence role；不冻结尚未执行的 layout、
payment-evidence、PayList export、case-create 等 catalog rows；不运行 repo-wide
Ruff/pytest/build/Playwright/release gate；不 commit/push/reset/clean/stash。

## Acceptance

1. 设计只覆盖八个正式 blocker、一个 overlay public-contract preflight 和两个最小
   prerequisites；
2. 每个 override 具有 exact public surface、errors/transaction/TDD boundary；
3. 两个新任务各自只有一个 closure 和一个明确 allowlist；
4. dependency/shared-file/cursor/transaction 图无 cycle 或并发冲突；
5. 独立 reviewer 确认未削弱 fail-closed、证据谱系、官费状态分离或 task gates；
6. 下一任务只创建 materialization plan；随后 controller 更新 task contracts 和
   additive delta-2 overlay；
7. materialization PASS 后先执行用户要求的 `AGENTS.md vNext` 独立治理任务，再
   请求切回 High 继续开发。
