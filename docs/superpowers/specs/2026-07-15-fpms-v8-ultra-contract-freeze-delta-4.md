# FPMS V8 Ultra 契约冻结增量设计 4（2026-07-15）

## Purpose

本文是已接受 V8、Ultra delta-1、delta-2 与 delta-3 的窄范围后继增量。它只处理
High 执行、独立复审或当前代码可重复检查已经证明的合同缺口：

1. 四个首段生命周期规则只检查 `evidence_refs` 是 tuple，没有检查证据种类、对象、
   数量与同案关系；
2. filing preparation、外部提交、回执和 batch filing 的既有入口缺少可达、可验证的
   文书证据链；
3. generated attachment 与 copyable OA 没有可达的正式 evidence role、promotion 与
   derivation 路径；
4. 三个既有 API 任务没有冻结 route、DTO、权限、响应和事务所有权；
5. 年费、PCT、布图设计登记费与旧费减迁移缺少精确的权威来源、载体或公开 callable；
6. 一个已完整冻结的 obligation-detail read 任务只是执行机制失活，不是新的业务
   设计问题。

本文不重新分析客户 Word、V8 总设计或 283-path catalog，不改写任何旧 PASS/REJECTED
证据，也不实施产品代码。它只冻结可执行合同、新增不可省略的原子 prerequisite，并
定义后继 materialization、独立复审、序列化与 High handoff。

## Authority and immutable parents

权威继承顺序：

1. `AGENTS.md`；
2. `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`；
3. `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`；
4. delta-1、delta-2、delta-3；
5. 本文仅覆盖本文列出的 proven gaps、依赖、共享 ownership 和 close 传播。

Immutable input SHA-256：

- V8 design：
  `62da1cb75b6b4c98ee51b9a6dd0ce5e3b5669616159a8c6f27146cf9a8992f4f`；
- V8 plan：
  `0a50fb22cb23095670377ce8d680101d4b35cfc842d844c39487dd1e05aadafb`；
- delta-1 spec：
  `f7723e335cdb7d1dc5e7eff443418bffe306c4236a0462b959b9cbf979ba5fef`；
- delta-2 spec：
  `724a21d30d10014f4fcced1a047b7969deb6df27c79a094c620243a7d51fad98`；
- delta-3 spec：
  `a76875f9afcb5c597d823c4277874167964eecaa4a8257894a10f0e32fbff124`；
- delta-3 batch manifest：
  `321b795e3a91f4f2df90f823542dc74114f3723b7308180c50c4c6a0eae9d4dd`。

旧 spec、plan、manifest、overlay、task file、task evidence 与 PASS/REJECTED history
全部只读。本增量通过新 task contracts 与 cumulative overlay 追加事实；不得通过改写
历史来掩盖本轮发现。

## Story Shape Classification

- `shared_file_density`: high — lifecycle、case、official workflow、documents、fees、
  annuity 与 migration 均有共享 ownership；
- `prereq_dependency_density`: high — 12 个新 prerequisite/correction 解除 17 个旧任务
  的 blocker，并传播到 Foundation/Full/Final；
- `be_fe_coupling`: medium — 三个 API wire 与既有 UI adapter 相连，但本增量不新增
  前端 closure；
- `evidence_cost`: high — 法律状态、文书证据、官费、费减、migration 和 final close
  均为 HIGH，SQLite 与 shared-file verification 必须串行；
- `chosen_runbook`: `P0-prereq-heavy-story`。

## Approved approach and fail-closed boundary

- 保留旧任务的一个 closure slice；合同缺口通过 additive correction/prerequisite
  解决，旧 PASS history 不回写。
- pure lifecycle rules 只验证传入证据 tuple 的 exact shape；DB source truth、hash 与
  关系由 adapter/resolver 在同一 transaction 内验证。
- generated 与 OA structured evidence 使用新的明确 role；enum 增长不得自动扩大
  registration 或 external-submission 权限。
- 官方费率只从 CNIPA primary source materialize 为 `PENDING/INACTIVE` candidate；
  本增量和 candidate task 都不得审批或激活。
- 客户/Tianyue seed 只保留其历史 provenance，不得升级为官方费率。
- `DEFER` 不等同 `HOLD`；旧费减字符串不等同审批；缺 source、approval、manifest、
  lineage 或 customer decision 时继续 fail closed。
- 所有 caller-owned service 不 commit/rollback；API 或既有外层 entrypoint 在全部
  service 成功后只 commit 一次，异常只 rollback 一次。

## Proven blocker inventory

| Catalog/task | Proven blocker | Delta-4 disposition |
| --- | --- | --- |
| 21 filing receipt rule | tuple-only evidence guard | re-freeze exact evidence matrix |
| 50 generated evidence adapter | creator、role、template identity/lineage 不可达 | depend on role + matrix correction |
| 51 document review API | route/DTO/response/transaction 未冻结 | freeze wire contract |
| 59 filing preparation adapter | actor、package evidence/hash/transaction 未冻结 | freeze adapter contract |
| 60 batch filing adapter | final version 与 manual submission evidence 不可解析 | depend on resolver + exact rule guard |
| 65 filing external adapter | entrypoint lacks evidence resolution and actor propagation | widen only its adapter allowlist |
| 66 filing receipt adapter | receipt service commits internally; no final-version linkage | depend on resolver + exact receipt rule |
| 72 copyable OA policy | runtime role source unattainable; modified claims cardinality conflict | formal promotion + exact singleton |
| 73 prepare OA seam | cannot consume reviewed typed OA evidence | depend on promotion/policy |
| 95 fee-reduction approval API | path/body boundary and transaction not frozen | freeze wire contract |
| 110 obligation detail read | contract already frozen; repeated zero-progress workers | changed-mechanism recovery only |
| 121 annuity instruction adapter | no exact persisted task→obligation link; DEFER ambiguity | depend on lineage + 133 |
| 133 future annuity obligation | no authoritative active rate/source/link mapping | candidate + lineage + exact source |
| 135 PCT policy | callable/evidence/error/Decimal contract missing | freeze pure legal policy |
| 136 layout registration rule | no reviewed candidate/callable/selection error surface | candidate + exact read rule |
| 169 decision-gate list API | audit history semantics not frozen | freeze read-only persisted list |
| 255 legacy fee-reduction import | grammar/provenance/manifest/atomicity missing | provenance carrier + exact importer |

## Lifecycle evidence contract

### Exact matrix

每个下列 rule 仍保持原 projection decision，只新增 exact evidence acceptance。任何
数量、kind、object type、same-case、hash 或 capture-time 不匹配均返回 no decision；
rule 保持 pure/read-only，绝不访问 transaction。

| Event | Exact evidence tuple |
| --- | --- |
| `CASE_OPENED` | exactly 1 `CASE_RECORD` / `Case` |
| `FILING_PREPARATION_STARTED` | exactly 1 `FILING_WORK_PACKAGE` / `OfficialWorkPackage` |
| `FILING_EXTERNAL_SUBMISSION_RECORDED` | exactly 1 `FINAL_SUBMISSION_VERSION` / `DocumentEvidenceVersion` plus exactly 1 `MANUAL_EXTERNAL_SUBMISSION_RECORD` / `CaseActivityEvent` |
| `FILING_RECEIPT_ARCHIVED` | exactly 1 `FINAL_SUBMISSION_VERSION` / `DocumentEvidenceVersion` plus exactly 1 `VALID_FILING_RECEIPT` / `OfficialWorkPackageReceipt` |

共同要求：

- tuple 中每个值的 exact type 为 `EvidenceReference`；
- every `reference.case_id == command.case_id`；object identities 不重复；
- `content_hash` exact full-match `sha256:[0-9a-f]{64}`；
- `captured_at` 是 naive `datetime`；
- tuple order 不构成权限；rule 按 kind/object identity 识别，缺一、多一、重复或未知项
  均 fail closed；
- rule 不查询 object 是否存在。source existence、current/review/status/hash linkage 由
  下游 adapter/resolver 在调用 `apply_lifecycle_event()` 前验证。

### Additive correction tasks

1. `FPMS-V8-LC-CASE-OPENED-EVIDENCE-GUARD-20260715-01` 只修
   `CASE_OPENED` evidence matrix；它可以迁移该 rule 的旧 task test fixture，但不重开
   旧 PASS task。
2. `FPMS-V8-LC-FILING-PREPARATION-EVIDENCE-GUARD-20260715-01` 只修
   preparation rule 与其旧 fixture。
3. `FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-EVIDENCE-GUARD-20260715-01` 只修
   external-submission rule 与其旧 fixture。
4. catalog task 21 自身重冻结 receipt rule；它拥有自己尚未 PASS 的 test，无需新增
   第二个 receipt correction task。

### Case-create adapter correction

`FPMS-V8-CASE-CREATE-OPENED-EVIDENCE-ADAPTER-20260715-01` 只修既有
`create_case()` 的 `CASE_OPENED` command：

- source object 是刚创建且同 transaction 可见的 `Case`；
- canonical snapshot exact keys/order 为 `case_id`, `case_no`, `case_type`, `client_id`；
- UTF-8 JSON 使用 sorted keys、compact separators、no ASCII escaping 后计算
  `sha256:<64-lower-hex>`；
- lifecycle payload 必须持久化且仅持久化以下三项；`source_snapshot` 是上述四键
  object（nullable value 必须显式 JSON `null`，不得省略），`source_snapshot_hash`
  是该 object canonical UTF-8 bytes 的 hash：

  ```json
  {"evidence_schema":"FPMS_CASE_OPENED_EVIDENCE_V1","source_snapshot":{"case_id":"<Case.id>","case_no":"<Case.case_no>","case_type":"<Case.case_type>","client_id":null},"source_snapshot_hash":"sha256:<64-lower-hex>"}
  ```

  The shown null variant is exact；when `Case.client_id` is non-null, its exact JSON string
  replaces `null` and no other byte changes；
  `append_case_activity()` 的 canonical payload bytes 是唯一 durable replay truth；exact
  retry 必须比较完整三键 payload 和 evidence ref，后续 Case mutable field 不得重建或
  替换这份 snapshot；
- evidence object ID 是 case ID，captured/effective/occurred time 使用同一 naive
  `opened_at`；actor 仍是 server-owned current user；
- case insert、activity、evidence、projection 在现有外层 transaction 中一次 commit；
  任何失败不得留下 case 或 direct status write；
- 不改变 POST route、201 response、输入 status gate 或其余 case-create behavior。

## Filing evidence resolution and adapter contracts

### Shared final-evidence resolver

新增 `FPMS-V8-FILING-SUBMISSION-EVIDENCE-RESOLVER-20260715-01`，唯一 public seam：

```python
def resolve_filing_final_evidence(
    package_id: str,
    transaction: Session,
) -> FilingFinalEvidenceResolution:
    ...
```

`FilingFinalEvidenceResolution` 是 frozen/slotted/kw-only DTO，包含：

- `package_id`, `case_id`, `evidence_version_id`, `content_hash`；
- `reviewer_id`, `reviewed_at`, `final_submitted_at`；
- nullable `submission_activity_id`, `submission_activity_hash`。

Selection：

1. exact one `FILING_PREP` package；
2. exact one `present=True` manifest entry links an evidence version；
3. manifest/version/package 同案，manifest `content_hash` exact equals version hash；
4. version is current, `FINAL`, independently `APPROVED`, has valid reviewer tuple and one
   delta-3 external-submission eligible role；
5. zero/multiple candidate, malformed hash, case/current/review/manifest mismatch is 409
   `FILING_FINAL_EVIDENCE_CONFLICT`; bad input is 400; missing package/version is 404；
6. if `final_submitted_at is None`, no matching finalized activity may exist and nullable
   activity fields are `None`；
7. if `final_submitted_at` exists, exactly one same-case
   `DOCUMENT_EVIDENCE_EXTERNAL_SUBMISSION_FINALIZED` `CaseActivityEvent` and its evidence
   link/canonical payload/reviewer/time must match the version. Its canonical event snapshot
   hash supplies `submission_activity_hash`; absence/multiplicity/mismatch is 409；
8. read-only under `no_autoflush`; no clock, write, flush, commit, rollback or identity-map
   mutation。

The finalized document activity already has an accepted immutable four-key payload；Delta-4
does not rewrite that PASS seam。For resolver verification, its payload must be exactly：

```json
{"evidence_version_id":"<version.id>","lineage_key":"<version.lineage_key>","role":"<version.role>","submitted_at":"<final_submitted_at.isoformat()>"}
```

The resolver computes `submission_activity_hash` from one exact independently reconstructible
snapshot, serialized as UTF-8 with sorted keys、compact separators and no ASCII escaping：

```json
{"activity_id":"<activity.id>","activity_type":"DOCUMENT_EVIDENCE_EXTERNAL_SUBMISSION_FINALIZED","actor_id":"<activity.actor_id>","case_id":"<case_id>","confirmation_status":"CONFIRMED","effective_at":"<final_submitted_at.isoformat()>","evidence":[{"captured_at":"<final_submitted_at.isoformat()>","content_hash":"<version.content_hash>","evidence_kind":"DOCUMENT_EVIDENCE_VERSION","object_id":"<version.id>","object_type":"DocumentEvidenceVersion"}],"idempotency_key":"document-external-submission:<adapter-base-key>","lane":"DOCUMENT","occurred_at":"<final_submitted_at.isoformat()>","payload":{"evidence_version_id":"<version.id>","lineage_key":"<version.lineage_key>","role":"<version.role>","submitted_at":"<final_submitted_at.isoformat()>"},"reviewer_id":"<version.reviewer_id>"}
```

`submission_activity_hash = sha256:<64-lower-hex>` over those exact bytes。The activity must
have exactly one evidence link matching the one-element `evidence` array；`captured_at` is
the exact submission time。The lifecycle evidence reference is therefore exactly
`MANUAL_EXTERNAL_SUBMISSION_RECORD / CaseActivityEvent / activity.id /
submission_activity_hash / final_submitted_at`。No created/updated timestamp、database row
order or mutable version field participates。

### Task 59 — filing preparation

Re-freeze `FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01`：

- API propagates `current_user.id`; service requires nonblank `actor_id`；
- new package writes `created_by/updated_by=actor_id`；existing package must already have
  a stable nonblank creator or 409，不得把当前用户猜成历史 creator；
- package snapshot exact keys are `case_id`, `id`, `package_kind`, `resolve_key`；canonical
  JSON hash becomes `FILING_WORK_PACKAGE` / `OfficialWorkPackage` evidence；
- activity payload is exactly
  `{"evidence_schema":"FPMS_FILING_PREPARATION_EVIDENCE_V1","source_snapshot":{"case_id":"<package.case_id>","id":"<package.id>","package_kind":"<package.package_kind>","resolve_key":"<package.resolve_key>"},"source_snapshot_hash":"sha256:<64-lower-hex>"}`；
  nested snapshot and full payload use UTF-8 sorted-key compact JSON with no ASCII escaping；
  exact replay compares persisted payload/evidence bytes and never reconstructs truth from a
  later mutable package；
- `captured_at/effective_at/occurred_at` uses package `created_at`；
- idempotency key exact `filing-preparation-started:<package.id>`；
- ensure/refresh/event in caller transaction, no internal commit/rollback；fresh and exact
  replay return the same package; changed provenance is 409；
- does not create final submission evidence or change external/receipt state。

### Tasks 65 and 60 — external submission

Both adapters must：

1. resolve package by exact identity and call `resolve_filing_final_evidence()`；
2. require resolver activity fields are `None` before fresh finalization；
3. call `finalize_external_submission()` once with server-owned actor and deterministic
   submitted datetime/idempotency；
4. re-resolve and require exact matching persisted finalized activity；
5. call `apply_lifecycle_event(FILING_EXTERNAL_SUBMISSION_RECORDED)` with the exact two
   evidence refs in this spec；
6. never assign `Case.status`/projection directly and never duplicate role/review/current
   validation；
7. keep all writes in the caller transaction and commit once only after both document and
   lifecycle events succeed。

Task 65 exact existing entrypoint behavior：

- only normalized operation code `EXTERNAL_SUBMISSION_RECORDED` enters this path；other
  existing checklist operation semantics remain unchanged；
- API propagates current user；`occurred_at` is the submission time；adapter base key is
  exact `filing-external:<package_id>:<occurred_at.isoformat()>`；the document event key is
  exact `document-external-submission:filing-external:<package_id>:<occurred_at.isoformat()>`
  and the lifecycle event key is exact
  `filing-external-lifecycle:<package_id>:<occurred_at.isoformat()>`；
- the only allowlist addition is `backend/app/modules/official_workflows/api.py` for actor
  propagation；no schema、router or other source path is added。

Task 60 batch behavior：

- process selected cases in the request's stable de-duplicated order；for each case resolve
  exact `FILING_PREP:<case_id>` package；
- submission time is deterministic naive
  `datetime.combine(submitted_date, time.min)` because the accepted request carries a date,
  not an invented wall clock；adapter base idempotency is exact
  `batch-filing:<case_id>:<submitted_date.isoformat()>`，document event key is exact
  `document-external-submission:batch-filing:<case_id>:<submitted_date.isoformat()>`，and
  lifecycle event key is exact
  `batch-filing-lifecycle:<case_id>:<submitted_date.isoformat()>`；
- one invalid case aborts and rolls back the whole batch；document/list/task side effects
  and every lifecycle transition are one transaction；
- `apply_exam_now` and `generate_list` keep existing meaning；no direct
  `WAITING_RECEIPT` assignment。

### Task 66 — filing receipt

Re-freeze `FPMS-V8-FILING-RECEIPT-LIFECYCLE-ADAPTER-20260712-01`：

- only `FILING_PREP` package plus a receipt with `archive_status=ARCHIVED`, non-null same-case
  receipt attachment and naive `received_at` can advance lifecycle；PENDING receipt alone
  does not advance；
- validate receipt attachment bytes/hash and persisted ownership; resolve exact final
  evidence and require its exact finalized activity；
- build exact final-version + `OfficialWorkPackageReceipt` refs, with receipt object ID and
  attachment content hash；
- idempotency exact `filing-receipt-archived:<receipt.id>`，effective/occurred/captured time
  is `received_at`；actor is current user；
- receipt creation/attachment flags/event/projection share one transaction；remove internal
  commit/refresh from the path；failure rolls back all；
- OA receipt behavior remains non-closure and must keep Tasks 14–16 regressions green。

## Document evidence and OA contracts

### Evidence role extension

`FPMS-V8-DE-DELTA4-EVIDENCE-ROLE-EXTENSION-20260715-01` adds exactly two ordered values
after `RAW_ATTACHMENT`：

```text
GENERATED_ATTACHMENT
OA_STRUCTURED_ATTACHMENT
```

- existing first ten names, values and order do not change；
- this task also owns the inherited exact-iteration regression
  `backend/tests/test_v8_document_evidence_contracts.py` solely to extend its accepted
  ordered expectation from the existing ten pairs to the same exact twelve pairs。The
  inherited test is a required GREEN input, not a second product closure；no other
  assertion in that file changes；
- neither new role is automatically externally submittable；delta-3 positive allowlist
  remains exact nine values；
- no OA manifest label becomes an `EvidenceRole`。OA labels remain manifest roles, while
  the version role records that formal OA promotion occurred。

### Registration matrix correction

`FPMS-V8-DE-DELTA4-REGISTRATION-MATRIX-CORRECTION-20260715-01` additively changes only
the explicit matrix in `register_evidence_version()`：

| EvidenceRole | DRAFT | FINAL |
| --- | --- | --- |
| `GENERATED_ATTACHMENT` | allow | deny |
| `OA_STRUCTURED_ATTACHMENT` | allow | allow |

RAW and original nine values keep delta-3 behavior；unknown/future roles still deny；both
new roles remain denied by external-submission positive allowlist。Rejected registration
must occur before DB access and use existing 400 error surface。

### Generated attachment adapter (Task 50)

- documents API/wizard propagates `current_user.id` to the generated-attachment service；
- one generated output is registered as `GENERATED_ATTACHMENT`, `DRAFT`, `PENDING` review,
  never final/currently external-submitted；
- content hash is the persisted generated attachment bytes；creator is server-owned actor；
- lineage key exact form is
  `generated:<template-id>:<first-16-lower-hex-of-sha256(template-code)>:<attachment-id>`；
  together with `Document.doc_template_id` it persistently identifies the resolved template
  ID and exact code identity without adding an unfrozen carrier。Template resolution must
  not fall back to a different/latest template；
- generated attachment and version are one transaction；no fake derivation is created when
  there is no parent evidence version；
  existing template render result and wizard ordering remain unchanged。

### Formal OA structured promotion

新增 `FPMS-V8-DE-OA-STRUCTURED-ATTACHMENT-PROMOTION-20260715-01`，唯一 closure 是把
一个 reviewed manifest classification 与一个 RAW DRAFT version 正式提升为新的 typed
version：

```python
def promote_oa_structured_attachment(
    command: PromoteOaStructuredAttachmentCommand,
    transaction: Session,
) -> PromoteOaStructuredAttachmentResult:
    ...
```

Command exact fields：`case_id`, `package_id`, `manifest_id`,
`raw_evidence_version_id`, `target_state`, `actor_id`, `promoted_at`,
`idempotency_key`。`target_state` only DRAFT or FINAL。

Freeze：

- package is exact same-case `OA_REPLY`；manifest is present, same package, links the raw
  attachment/version and carries exactly one permitted OA role；
- permitted manifest roles：`OA_STATEMENT_WORD`, `OA_MODIFIED_CLAIMS`,
  `OA_AMENDMENT_COMPARISON`, `OA_OTHER_PROOF`, `OA_ADDITIONAL_FILE`；
- parent is current RAW DRAFT, hash matches manifest/attachment, and is not independently
  reclassified by upload filename；
- create/reuse a same-content `OA_STRUCTURED_ATTACHMENT` version with same hash and exact
  lineage `<parent.lineage_key>|OA|<manifest-role>`；
- register one `OFFICIAL_RECOGNITION` derivation whose canonical source snapshot includes
  parent/child IDs and hashes, manifest/package IDs, exact OA role, actor and promoted time；
- before any fresh write compute `promotion_identity_key = sha256:<64-lower-hex>` over the
  UTF-8 sorted-key/compact/no-ASCII-escaping bytes of exactly this command/source object：

  ```json
  {"actor_id":"<actor_id>","case_id":"<case_id>","command_idempotency_key":"<idempotency_key>","manifest_id":"<manifest_id>","manifest_role":"<exact-OA-role>","package_id":"<package_id>","promoted_at":"<promoted_at.isoformat()>","raw_content_hash":"<raw-version.content_hash>","raw_evidence_version_id":"<raw-version.id>","target_state":"<DRAFT-or-FINAL>"}
  ```

- append exactly one `OA_STRUCTURED_ATTACHMENT_PROMOTED` DOCUMENT activity with
  `confirmation_status=CONFIRMED`, unchanged central projection and durable idempotency
  `oa-structured-promotion:<command.idempotency_key>`。Its payload and the
  `OFFICIAL_RECOGNITION` derivation `source_snapshot` are byte-identical canonical JSON with
  exactly these keys：

  ```json
  {"actor_id":"<actor_id>","case_id":"<case_id>","command_idempotency_key":"<idempotency_key>","manifest_id":"<manifest_id>","manifest_role":"<exact-OA-role>","package_id":"<package_id>","promoted_at":"<promoted_at.isoformat()>","promotion_identity_key":"sha256:<64-lower-hex>","raw_content_hash":"<raw-version.content_hash>","raw_evidence_version_id":"<raw-version.id>","schema":"FPMS_OA_STRUCTURED_ATTACHMENT_PROMOTION_V1","target_state":"<DRAFT-or-FINAL>","typed_content_hash":"<child-version.content_hash>","typed_evidence_version_id":"<child-version.id>"}
  ```

  The activity has exactly two references captured at `promoted_at`：
  `RAW_ATTACHMENT_VERSION / DocumentEvidenceVersion / parent.id / parent.content_hash` and
  `OA_STRUCTURED_ATTACHMENT_VERSION / DocumentEvidenceVersion / child.id /
  child.content_hash`；
- update only manifest's `evidence_version_id/content_hash` to the typed child in the same
  transaction；do not alter `official_file_role`；
- replay lookup first uses the unique same-case activity key
  `oa-structured-promotion:<command.idempotency_key>`。It must parse the exact payload,
  recompute/compare `promotion_identity_key`, resolve exactly one named child and exactly one
  matching derivation, require the manifest still names that child/hash, and compare both
  evidence refs before returning reuse。Missing/multiple/tampered carrier or different
  role/hash/state/actor/time/source under the same idempotency is 409；no second child,
  derivation or activity；creator cannot self-approve here；promotion itself leaves child
  review `PENDING`；
- no external submission, OA reply preparation, lifecycle status or customer decision。

### Copyable OA policy (Task 72) and prepare seam (Task 73)

Task 72 discards the rejected candidate's ORM-role shortcut but preserves its evidence
history。Public policy consumes a frozen DTO containing both typed version identity/hash and
the exact manifest role/link。Cardinality：

- exactly one `OA_STATEMENT_WORD`；
- exactly one `OA_MODIFIED_CLAIMS`；
- at most one `OA_AMENDMENT_COMPARISON`；
- zero-or-more `OA_OTHER_PROOF` and `OA_ADDITIONAL_FILE`；
- duplicate evidence ID, duplicate manifest ID, cross-case/package, RAW/non-promoted,
  hash/link/state/review mismatch and unknown role fail closed。

Every supplied version must be `OA_STRUCTURED_ATTACHMENT`, current, independently
`APPROVED`, and exactly linked by its same-case manifest。Task 73 depends on promotion and
the corrected policy；it reads the exact manifest/version relation and creates only its
existing DRAFT OA_OUT/package closure。它不得从 `DocAttachment.official_file_role` 或文件名
直接推断 typed evidence。

## Exact API wire contracts

### Task 51 — document evidence review

- route：`POST /api/v1/documents/evidence-versions/{evidence_version_id}/review`；
- permission：function parameter `_perm: None = Depends(require_perm("Doc.Edit"))`；
- strict body exact order：`case_id`, `decision`, `reviewed_at`, `idempotency_key`；
- `decision` exact `APPROVE | REJECT`；`reviewed_at` naive；version ID path-only；reviewer
  server-owned current user；unknown/extra/missing fields 422；
- delegate exactly once to `review_evidence_version()`；maker/reviewer separation stays in
  service；
- direct service-result response，no invented envelope；200 fresh and exact replay；
- outer adapter commits once on fresh/replay success, rolls back once on any service error；
- 400 invalid/path-case mismatch, 404 case/version missing, 409 state/review/idempotency/
  self-review conflict, plus 401/403/422；no 201/204。

### Task 95 — fee-reduction approval create

- route：`POST /api/v1/fees/cases/{case_id}/reduction-approvals`；permission `Fee.Edit`；
- strict body exact order：`case_id`, `scope_type`, `applicant_ids`,
  `eligibility_attributes_version`, `eligibility_attributes_json`, `reduction_ratio`,
  `fee_codes`, `fee_year_from`, `fee_year_to`, `effective_from`, `effective_to`,
  `source_evidence_version_id`, `expected_source_content_hash`, `confirmed_at`；
- body `case_id` is intentionally retained to make the accepted wrong-case boundary
  observable。path/body mismatch is pre-service 400
  `FEE_REDUCTION_APPROVAL_CASE_MISMATCH` with both IDs in details；
- confirmed actor is server-owned current user；`confirmed_at` naive/client-stable；
- direct `{approval_id}` response；service `CREATED` → 201，`REUSED` → 200；
- commit once on either success, rollback once on error；service evidence-case mismatch
  remains 409；401/403/404/409/422 follow existing error surface。

### Task 169 — decision-gate audit list

- route：`GET /api/v1/system/decision-gates`；no request body and no query parameters；
- permission `SystemParam.Read`；
- direct list of persisted audit rows，not an effective-behavior envelope；
- include all stored history in `recorded_at, gate_id` ascending order, including current,
  superseded, revoked and future-effective rows；
- response preserves gate/source/version/scope/status/current identity/actor/time/supersede
  facts；
- explicit SELECT under `no_autoflush`，zero writes/clock/commit；
- must not call `resolve_decision_gate()` because that service resolves effective business
  behavior and cannot represent complete audit history。

## Official-fee, annuity and migration contracts

### Primary legal sources

- CNIPA Announcement 594：
  `https://www.cnipa.gov.cn/art/2024/8/6/art_2468_205759.html`；
- CNIPA Announcement 246：
  `https://www.cnipa.gov.cn/art/2017/6/30/art_74_27462.html`；
- CNIPA current fee page：
  `https://www.cnipa.gov.cn/art/2024/8/6/art_1518_155983.html`；
- CNIPA payment service guide, updated 2026-03-30：
  `https://www.cnipa.gov.cn/attach/0/b2d5a31081404b83a36c0df1ebe591e7.pdf`。

The guide's Annex 2 freezes these full annual fee tiers：

| Category | Exact full annual fee tiers (CNY) |
| --- | --- |
| INV | years 1–3 `900.00`; 4–6 `1200.00`; 7–9 `2000.00`; 10–12 `4000.00`; 13–15 `6000.00`; 16–20 `8000.00` |
| UM | years 1–3 `600.00`; 4–5 `900.00`; 6–8 `1200.00`; 9–10 `2000.00` |
| DES | years 1–3 `600.00`; 4–5 `900.00`; 6–8 `1200.00`; 9–10 `2000.00`; 11–15 `3000.00` |

Announcement 246 and the guide freeze `IC_LAYOUT_REGISTRATION_FEE=1000.00 CNY`。

### CNIPA candidate materializers

`FPMS-V8-CNIPA-246-LAYOUT-RATE-CANDIDATE-20260715-01`：

- materializes/reuses exactly one `CNIPA_LAYOUT_246`, version `2017-07-01`, effective
  `[2017-07-01, None)` candidate and one linked rate
  `IC_LAYOUT_REGISTRATION_FEE=1000.00 CNY`；
- rate is `GOV/FIXED`, `allow_reduction=False`, enabled, exact source/hash linkage；
- linked rate keeps legacy `source_status=PENDING_CONFIRMATION` so generic pre-V8 fee
  queries cannot consume an inactive candidate；strict consumers use the linked book's
  approved/active state as authority and do not reinterpret that legacy safety field；
- candidate remains `PENDING/INACTIVE` with null approval/activation/current identity；
- canonical data file and `CNIPA_RATE_SOURCE_V1` snapshot are hash-locked；changed replay
  is 409；no activation or customer seed promotion。

`FPMS-V8-CNIPA-ANNUITY-RATE-CANDIDATE-20260715-01`：

- materializes/reuses one `CNIPA_PATENT_ANNUITY_20260330`, version `2026-03-30`, effective
  `[2026-03-30, None)` candidate；this interval says only when this reviewed source snapshot
  is used, not an unsupported historical claim；
- creates exactly three linked `GOV/CNY/TIER` rates：`CN_ANNUITY_FEE_INV`,
  `CN_ANNUITY_FEE_UM`, `CN_ANNUITY_FEE_DES`，with canonical `tiers` JSON exactly matching
  the table above, full amounts, `allow_reduction=True`；
- each `FeeRate.calc_params` is exact UTF-8 JSON object text, with sorted object keys,
  compact separators, no ASCII escaping and no trailing newline。The three complete strings
  are frozen byte-for-byte：

  ```text
  CN_ANNUITY_FEE_INV={"schema":"CNIPA_ANNUITY_TIER_V1","tiers":[{"amount":"900.00","from":1,"to":3},{"amount":"1200.00","from":4,"to":6},{"amount":"2000.00","from":7,"to":9},{"amount":"4000.00","from":10,"to":12},{"amount":"6000.00","from":13,"to":15},{"amount":"8000.00","from":16,"to":20}]}
  CN_ANNUITY_FEE_UM={"schema":"CNIPA_ANNUITY_TIER_V1","tiers":[{"amount":"600.00","from":1,"to":3},{"amount":"900.00","from":4,"to":5},{"amount":"1200.00","from":6,"to":8},{"amount":"2000.00","from":9,"to":10}]}
  CN_ANNUITY_FEE_DES={"schema":"CNIPA_ANNUITY_TIER_V1","tiers":[{"amount":"600.00","from":1,"to":3},{"amount":"900.00","from":4,"to":5},{"amount":"1200.00","from":6,"to":8},{"amount":"2000.00","from":9,"to":10},{"amount":"3000.00","from":11,"to":15}]}
  ```

  strict consumers accept top-level keys exactly `schema`, `tiers`；schema exactly
  `CNIPA_ANNUITY_TIER_V1`；each tier keys exactly `amount`, `from`, `to`；`from`/`to` are
  positive non-bool integers with inclusive endpoints；tiers stay in ascending order,
  start at year 1, are contiguous and neither overlap nor gap；amount is an exact positive
  two-place decimal string。Unknown/missing/extra key, reordered/non-canonical text,
  non-contiguous interval or year outside the category's final endpoint is 409 and no rate
  is selected。Task 133 uses this strict parser, not a permissive legacy TIER helper；
- all three linked rates are enabled but keep
  `source_status=PENDING_CONFIRMATION`，preventing generic legacy selectors from using the
  inactive candidate；only a strict active-book-aware consumer may use them after explicit
  activation；
- candidate remains `PENDING/INACTIVE`；activation is only through accepted
  `activate_official_rate_book()` with accountable actors/times；
- no `date.today()`, auto approval/activation, customer/Tianyue fallback or partial write。

Both materializers are caller-owned transaction services；fresh/replay success does not
commit internally。Their SQLite tests and activation regressions are globally serialized。

### Annuity task→obligation lineage carrier

`FPMS-V8-ANNUITY-TASK-OBLIGATION-LINEAGE-CARRIER-20260715-01` adds nullable legacy-safe
columns to `t_annuity_task`：

- `source_activity_id` → `t_case_activity_event.id` RESTRICT；
- `source_document_id` → `t_document.id` RESTRICT；
- `source_evidence_version_id` → `t_document_evidence_version.id` RESTRICT；
- `source_evidence_content_hash` `String(128)`；
- `fee_obligation_id` → `t_fee_obligation.id` RESTRICT + unique；
- `grant_fee_year_key` integer；
- all six are null together for legacy rows or non-null together with
  `grant_fee_year_key >= 1`；
- service input and new writes require `source_evidence_content_hash` full-match
  `sha256:[0-9a-f]{64}`；the migration adds no guessed/backfilled hash；
- existing IDs remain SQLite `INTEGER PRIMARY KEY`；no server `now()`、PG-only type or
  destructive backfill。

Migration file/revision contract and exact chain：

- `backend/alembic/versions/v8_delta4_annuity_obligation_lineage.py` has
  `revision="v8_d4_annuity_lineage_01"` and
  `down_revision="v8_w5_pay_list_export_artifact_01"`；
- `backend/alembic/versions/v8_delta4_legacy_fee_reduction_provenance.py` has
  `revision="v8_d4_legacy_fee_provenance_01"` and
  `down_revision="v8_d4_annuity_lineage_01"`；

```text
v8_w5_pay_list_export_artifact_01
→ v8_d4_annuity_lineage_01
→ v8_d4_legacy_fee_provenance_01
```

The carrier does not infer or backfill legacy mappings；consumers fail closed when null。

### Task 133 — future annuity obligation

Public seam：

```python
def recognize_future_annuity_obligation(
    command: RecognizeFutureAnnuityObligationCommand,
    transaction: Session,
) -> RecognizeFutureAnnuityObligationResult:
    ...
```

Command exact fields：`annuity_task_id`, `source_activity_id`, `source_document_id`,
`source_evidence_version_id`, `source_evidence_content_hash`, `grant_fee_year_key`,
`rate_effective_on`, `reduction_input`, `reduction_approval_id`, `actor_id`,
`idempotency_key`。

Freeze：

- source activity is same-case exact `GRANT_ANNOUNCEMENT_CONFIRMED`, `lane=LIFECYCLE`,
  `confirmation_status=CONFIRMED`；its complete evidence set is exactly one
  `DOCUMENT_EVIDENCE_VERSION / DocumentEvidenceVersion` reference whose object ID and hash
  equal the two command evidence fields and whose `captured_at` equals the activity's naive
  effective time；zero/multiple/extra/unknown links fail 409；
- for a fresh recognition, that version belongs to the same case and `source_document_id`,
  has role exactly `OFFICIAL_FINAL_PDF`, state `FINAL`, review state `APPROVED`, non-null
  naive `reviewed_at`, nonblank reviewer different from creator, exact stored hash and exact
  current identity `f"{case_id}|{lineage_key}"`；the Document is same-case。The event link,
  version and carrier must agree byte-for-byte；case must be in accepted grant/post-grant
  projection；
- an exact existing idempotent obligation/task-carrier replay is resolved and compared
  before the fresh-current guard, so a later reviewed replacement does not invalidate the
  immutable old replay；changed source/hash/carrier under the same key is 409；
- supplied source/year/due values must match task facts；never infer source from latest,
  `first_annuity_year` or wall clock；
- category maps exact fee code INV/UM/DES；obligation type `FUTURE_ANNUITY`, fee year key
  task year number, due task due date, currency CNY；
- exact one active/approved/effective `CNIPA_PATENT_ANNUITY_20260330` book and linked rate；
  select full tier by `grant_fee_year_key`；
- validate reduction with `validate_annuity_fee_reduction()` and exact approval coverage；
  finite Decimal, two-place `ROUND_HALF_UP`; retain full annual fee as late-fee base；
- initial instruction remains pending；do not copy legacy PAY/ABANDON/DEFER；
- delegate once to `recognize_obligation()` then atomically set/reuse the six lineage
  fields；no draft/letter or legacy instruction mutation；caller owns transaction；
- exact replay reuses；source/rate/link/idempotency mismatch is 409。

Dependencies：annuity candidate → explicit activation → lineage carrier → Task 133。

### Task 121 — annuity instruction adapter

```python
def record_annuity_task_instruction(
    command: RecordAnnuityTaskInstructionCommand,
    transaction: Session,
) -> RecordAnnuityTaskInstructionResult:
    ...
```

Command：`annuity_task_id`, `instruction`, `actor_id`, `idempotency_key`；instruction exact
`PAY | HOLD | ABANDON`。Resolve exact persisted task→obligation link and delegate once to
`record_client_instruction()`。`DEFER` must return 400 and never map to HOLD；zero/multiple/
cross-case/wrong type/year links are 404/409 as appropriate。Exact replay reuses；changed
replay 409。No internal commit, duplicate activity or legacy `client_instruction` mutation。

Dependencies：Task 133 + lineage carrier + accepted client-instruction service。

### Task 135 — PCT national-stage fee policy

Pure callable：

```python
def evaluate_pct_national_stage_fee_policy(
    command: EvaluatePctNationalStageFeePolicyCommand,
) -> EvaluatePctNationalStageFeePolicyResult:
    ...
```

Rule/source `CN_PCT_NATIONAL_STAGE_POLICY_594`, effective `[2024-08-06, None)`。

The same module owns the pure prerequisite
`validate_confirmed_pct_evidence_set(case_id, effective_on, evidence)`；there is no unnamed
upstream trust shortcut。Its frozen/slotted/kw-only `ConfirmedPctEvidence` has exactly：
`case_id`, `source_document_id`, `evidence_version_id`, `content_hash`, `lineage_key`,
`current_identity_key`, `issuer`, `document_type`, `issued_on`, `role`, `state`,
`review_state`, `creator_id`, `reviewer_id`, `reviewed_at`。Validation requires same exact
case, nonblank identities, full `sha256:[0-9a-f]{64}`, `issuer="CNIPA"`, role
`OFFICIAL_FINAL_PDF`, state `FINAL`, review state `APPROVED`, nonblank reviewer different
from creator, naive non-null `reviewed_at`, `current_identity_key ==
f"{case_id}|{lineage_key}"`, and `issued_on <= effective_on`。No DB lookup is implied；the
DTO is accepted only after this callable validates every field。

- confirmed CNIPA receiving-office plus CNIPA international-search evidence exempts
  `CN_INV_APPLICATION_FEE`, `CN_UM_APPLICATION_FEE`, `CN_EXCESS_CLAIM_FEE`,
  `CN_SPEC_PAGE_31_300_FEE`, `CN_SPEC_PAGE_301_PLUS_FEE`；
- confirmed CNIPA ISR or IPRP exempts `CN_SUBSTANTIVE_EXAM_FEE`；
- document types are exact `CNIPA_RO_RECEIPT`, `CNIPA_ISR`, `CNIPA_IPRP`。For one of the
  five application/excess/page fee codes the evidence tuple contains exactly one RO receipt
  and one ISR, no third item；for substantive examination it contains exactly one ISR XOR
  one IPRP；for ordinary domestic reduction it is empty。Duplicate version/document/hash,
  duplicate document type, unknown/extra item or wrong cardinality fails closed；
- ordinary domestic per-fee reduction applies only to exact codes
  `CN_REEXAM_FEE_INV`, `CN_REEXAM_FEE_UM`, `CN_REEXAM_FEE_DES`,
  `CN_ANNUITY_FEE_INV`, `CN_ANNUITY_FEE_UM`, `CN_ANNUITY_FEE_DES`；international-stage/
  WIPO items are outside；no whole-case PCT flag；
- command exact fields are `case_id`, `fee_code`, `full_amount`, `effective_on`,
  `evidence`, `reduction_context`；`evidence` is a tuple of the exact DTO above；
- result carries rule/source interval, disposition, evidence IDs, full amount,
  reduction/payable ratios and payable amount；
- amount positive finite with at most 2 scale；exemption `0.00`; otherwise
  `(full_amount * payable_ratio).quantize(0.01, ROUND_HALF_UP)`；ratios four-place exact；
- case type alone, missing/foreign/conflicting/effective-date evidence, unsupported key,
  international-stage key, malformed hash/amount or out-of-scope reduction fails closed；
- pure exceptions expose exactly one code：`PCT_POLICY_COMMAND_INVALID`,
  `PCT_POLICY_EFFECTIVE_DATE_UNSUPPORTED`, `PCT_POLICY_FEE_CODE_UNSUPPORTED`,
  `PCT_POLICY_EVIDENCE_MISSING`, `PCT_POLICY_EVIDENCE_INVALID`,
  `PCT_POLICY_EVIDENCE_CONFLICT`, or `PCT_POLICY_REDUCTION_INVALID`。A future HTTP adapter
  maps command/date/code/reduction errors to 400 and evidence missing/invalid/conflict to
  409；this pure task adds no HTTP behavior；
- no DB, rate activation, I/O, clock or mutation。Dependencies are accepted fee-reduction
  and annuity-reduction validators, not customer approval。

### Task 136 — layout registration fee read rule

```python
def get_layout_registration_fee(
    command: GetLayoutRegistrationFeeCommand,
    transaction: Session,
) -> GetLayoutRegistrationFeeResult:
    ...
```

- exact fee key `IC_LAYOUT_REGISTRATION_FEE`; date must be on/after 2017-07-01；
- select exactly one approved/active/effective `CNIPA_LAYOUT_246` book and exactly one
  enabled linked `GOV/CNY/FIXED/no-reduction` rate；
- stored amount must be exact `1000.00`; return rate/book/source/version/interval IDs and
  values；no recalculation/rounding；
- invalid input 400；missing/unapproved/ambiguous/malformed book/rate 409；
- read-only `no_autoflush`; no write/clock；never use customer/Tianyue row。

### Legacy fee-reduction provenance carrier

`FPMS-V8-LEGACY-FEE-REDUCTION-PROVENANCE-CARRIER-20260715-01` adds append-only table
`t_legacy_fee_reduction_provenance`：

- application-generated UUID TEXT PK；
- `case_id` FK RESTRICT；exact `legacy_value` in `0|0.7|0.85`；
- `source_reference`, `source_version`, `source_snapshot_hash(64)`,
  `manifest_hash(64)`, `confirmed_by` FK RESTRICT, naive `confirmed_at`；
- `approval_id` nullable FK RESTRICT；must be null for `0` and non-null for `0.7/0.85`；
- exact unique identity `(case_id, manifest_hash)` and immutable creation audit；
- no guessed actor/time, server `now()`, nullable confirmation or automatic backfill。

Carrier task owns only ORM/migration/schema tests；it neither confirms a customer manifest
nor creates a fee-reduction approval。

### Task 255 — legacy importer

```python
def import_legacy_fee_reductions(
    *,
    transaction: Session,
    manifest: LegacyFeeReductionMigrationManifest,
    dry_run: bool,
    expected_plan_sha256: str | None = None,
) -> LegacyFeeReductionImportResult:
    ...
```

- accept only exact strings `"0"`, `"0.7"`, `"0.85"`; no trim/numeric normalization；
- externally approved manifest supplies version/hash, actor/time, case ID, exact legacy
  value, source reference/version/hash and nullable approval ID；
- deterministic case-ID order；dry-run zero writes and emits input/plan hash + row
  classification；apply requires exact dry-run plan hash；
- `0` may create/reuse only the exact confirmed provenance row from the approved manifest；
  it must not infer “missing means zero”；
- `0.7/0.85` requires exactly one pre-existing confirmed approval matching ratio,
  case/applicant/fee/year/effective/evidence scope and hash, then creates/reuses provenance；
  importer never creates approval；
- update only the legacy case fee-reduction field to the exact canonical string when the
  row passes；whole batch atomic；exact replay no mutation；changed replay 409；
- result counts：scanned, explicit-zero, reused-70, reused-85, unchanged, invalid,
  missing-approval, ambiguous-approval, planned-writes plus input/plan/output hashes；
- without the real approved manifest, implementation can PASS synthetic tests but actual
  migration remains a customer-gated operation and must not run。

## Task 110 execution recovery classification

`FPMS-V8-FO-OBLIGATION-DETAIL-READ-20260712-01` is **NO CONTRACT CHANGE**。Its delta-2
public seam, DTO, 400/404/409 matrix, four-SELECT/no-autoflush/read-only contract and
allowlist remain authoritative。

Recovery rules：

- preserve valid RED
  `artifacts/FPMS-V8-FO-OBLIGATION-DETAIL-READ-20260712-01/outputs/20260715T105402_red.log`；
- preserve the 728-line partial task test and current Evidence 1.1 baseline；
- do not reinitialize, rerun RED or spawn another identical controller worker；
- resume in a changed-mechanism High lane owned by main thread or a bounded direct worker；
- finish missing historical/source-lineage/current/supersede/read-only coverage in durable
  increments；after every increment inspect diff/artifact growth；
- apply the two-observation no-progress rule。This classification is not a new product node。

## New product task catalog (12)

Every row is HIGH, Foundation, `CONTRACT FROZEN`, owns one exact task file and one closure。
Each allowlist also includes its own task file and `artifacts/<TASK-ID>/**`。

| # | Task ID | One closure | Product/test allowlist | Direct dependencies |
| --- | --- | --- | --- | --- |
| D4-01 | `FPMS-V8-LC-CASE-OPENED-EVIDENCE-GUARD-20260715-01` | exact CASE_OPENED evidence matrix | `backend/app/modules/cases/lifecycle_rules.py`; `backend/tests/test_v8_lifecycle_case_opened.py`; `backend/tests/test_v8_lc_case_opened_evidence_guard.py` | accepted CASE_OPENED |
| D4-02 | `FPMS-V8-CASE-CREATE-OPENED-EVIDENCE-ADAPTER-20260715-01` | case create supplies case-record evidence | `backend/app/modules/cases/service.py`; `backend/tests/test_v8_case_create_opened_evidence_adapter.py` | D4-01; accepted Task 55 |
| D4-03 | `FPMS-V8-LC-FILING-PREPARATION-EVIDENCE-GUARD-20260715-01` | exact preparation evidence matrix | `backend/app/modules/cases/lifecycle_rules.py`; `backend/tests/test_v8_lifecycle_filing_preparation_started.py`; `backend/tests/test_v8_lc_filing_preparation_evidence_guard.py` | D4-01; accepted Task 19 |
| D4-04 | `FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-EVIDENCE-GUARD-20260715-01` | exact external-submission evidence matrix | `backend/app/modules/cases/lifecycle_rules.py`; `backend/tests/test_v8_lifecycle_filing_external_submission.py`; `backend/tests/test_v8_lc_filing_external_submission_evidence_guard.py` | D4-03; accepted Task 20 |
| D4-05 | `FPMS-V8-FILING-SUBMISSION-EVIDENCE-RESOLVER-20260715-01` | read exact final version and optional finalized activity | `backend/app/modules/official_workflows/filing_evidence_resolver.py`; `backend/tests/test_v8_filing_submission_evidence_resolver.py` | accepted DE finalization seam + delta-3 role allowlist |
| D4-06 | `FPMS-V8-DE-DELTA4-EVIDENCE-ROLE-EXTENSION-20260715-01` | add two exact typed evidence roles | `backend/app/modules/documents/evidence_contracts.py`; `backend/tests/test_v8_document_evidence_contracts.py`; `backend/tests/test_v8_delta4_evidence_role_extension.py` | accepted RAW role task; inherited exact-iteration regression |
| D4-07 | `FPMS-V8-DE-DELTA4-REGISTRATION-MATRIX-CORRECTION-20260715-01` | add two exact role/state rows | `backend/app/modules/documents/evidence_service.py`; `backend/tests/test_v8_delta4_registration_matrix.py` | D4-06; delta-3 registration guard |
| D4-08 | `FPMS-V8-DE-OA-STRUCTURED-ATTACHMENT-PROMOTION-20260715-01` | formal RAW→OA structured promotion + derivation/link | `backend/app/modules/documents/oa_attachment_promotion_service.py`; `backend/tests/test_v8_oa_structured_attachment_promotion.py` | D4-06; D4-07; register version/derivation |
| D4-09 | `FPMS-V8-CNIPA-246-LAYOUT-RATE-CANDIDATE-20260715-01` | materialize reviewed layout candidate | `backend/app/modules/fees/cnipa_layout_rate_candidate.py`; `backend/app/modules/fees/data/cnipa_246_layout_rate.json`; `backend/tests/test_v8_cnipa_246_layout_rate_candidate.py` | rate-book carrier |
| D4-10 | `FPMS-V8-CNIPA-ANNUITY-RATE-CANDIDATE-20260715-01` | materialize reviewed annuity candidate | `backend/app/modules/fees/cnipa_annuity_rate_candidate.py`; `backend/app/modules/fees/data/cnipa_payment_guide_20260330_annuity_rates.json`; `backend/tests/test_v8_cnipa_annuity_rate_candidate.py` | rate-book carrier |
| D4-11 | `FPMS-V8-ANNUITY-TASK-OBLIGATION-LINEAGE-CARRIER-20260715-01` | add six-column exact lineage carrier | `backend/app/modules/annuity/models.py`; `backend/alembic/versions/v8_delta4_annuity_obligation_lineage.py`; `backend/tests/test_v8_annuity_task_obligation_lineage_carrier.py` | exact parent `v8_w5_pay_list_export_artifact_01`; revision `v8_d4_annuity_lineage_01` |
| D4-12 | `FPMS-V8-LEGACY-FEE-REDUCTION-PROVENANCE-CARRIER-20260715-01` | add append-only migration provenance carrier | `backend/app/modules/fees/models.py`; `backend/alembic/versions/v8_delta4_legacy_fee_reduction_provenance.py`; `backend/tests/test_v8_legacy_fee_reduction_provenance_carrier.py` | exact parent/revision D4-11 `v8_d4_annuity_lineage_01`; revision `v8_d4_legacy_fee_provenance_01` |

No two D4 rows editing the same source/test may execute concurrently。D4-01→03→04 and
D4-06→07→08 are serialized chains。D4-11→12 is the sole migration chain and all Alembic/
SQLite verification is serialized。

## Existing task materialization set (17)

The successor controller updates only these exact task contracts；it does not implement
them or erase prior evidence：

1. `FPMS-V8-LC-FILING-RECEIPT-ARCHIVED-20260712-01`；
2. `FPMS-V8-DE-GENERATED-ATTACHMENT-EVIDENCE-ADAPTER-20260712-01`；
3. `FPMS-V8-DE-REVIEW-API-20260712-01`；
4. `FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01`；
5. `FPMS-V8-CASE-BATCH-FILING-EVENT-ADAPTER-20260712-01`；
6. `FPMS-V8-FILING-EXTERNAL-SUBMISSION-ADAPTER-20260712-01`；
7. `FPMS-V8-FILING-RECEIPT-LIFECYCLE-ADAPTER-20260712-01`；
8. `FPMS-V8-OA-COPYABLE-ATTACHMENT-POLICY-20260712-01`；
9. `FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01`；
10. `FPMS-V8-FEE-REDUCTION-APPROVAL-CREATE-API-20260712-01`；
11. `FPMS-V8-FO-OBLIGATION-DETAIL-READ-20260712-01`（execution recovery only）；
12. `FPMS-V8-ANNUITY-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01`；
13. `FPMS-V8-FUTURE-ANNUITY-OBLIGATION-20260712-01`；
14. `FPMS-V8-PCT-FEE-POLICY-20260712-01`；
15. `FPMS-V8-LAYOUT-REGISTRATION-FEE-RULE-20260712-01`；
16. `FPMS-V8-DECISION-GATE-LIST-API-20260712-01`；
17. `FPMS-V8-LEGACY-FEE-REDUCTION-IMPORT-20260712-01`。

Materialization adds exactly `backend/app/modules/official_workflows/api.py` to both Task 59
and Task 65, solely for server-owned actor propagation；it adds no schema/router/other path,
and Task 59 owns that shared API before Task 65。Task 50 adds exactly
`backend/app/modules/documents/api.py` and is serialized before Task 51。All other
allowlists remain their current exact product/test paths unless this spec names a new
prerequisite file。Task 72 retains rejected review and candidate patch as history；its
new Status is `READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-15 / CORRECTION REQUIRED`。
Task 110 becomes `READY FOR HIGH / CHANGED-MECHANISM RECOVERY / VALID RED PRESERVED`。

## Shared ownership and serialization

### Lifecycle rules

```text
accepted CASE_OPENED
→ D4-01 CASE_OPENED evidence guard
→ D4-03 preparation evidence guard
→ D4-04 external-submission evidence guard
→ catalog Task 21 receipt rule correction
→ later lifecycle rules in original order
```

### Case service

```text
accepted Task 55
→ D4-02 case-create evidence adapter
→ Task 60 batch filing adapter
```

### Official workflow service/API

```text
Task 59 preparation adapter
→ Task 65 external-operation adapter
→ Task 66 receipt adapter
```

D4-05 resolver is a new file and may be implemented independently, but consumers wait for
its PASS。Task 59 and Task 65 each add exactly
`backend/app/modules/official_workflows/api.py`；ownership is exact Task 59 → Task 65 and
they never execute concurrently。No schema path is added；current-user injection is explicit
and no router rewire occurs。

### Document contracts/services

```text
accepted RAW role
→ D4-06 role extension
→ D4-07 registration matrix
→ D4-08 OA promotion
→ Task 72 correction
→ Task 73 prepare seam
```

Task 50 waits for D4-06/D4-07 but owns `documents/service.py` separately。The delta-3
external-submission allowlist remains the serialization gate for any later change to
`evidence_workflow_service.py`。Task 50 may add `documents/api.py` only to propagate the
server-owned actor；therefore Task 50 → Task 51 is an explicit shared-API order and the two
must never execute concurrently。

### Fee and migration

- D4-09 and D4-10 use separate new source/data files and may implement in parallel, but
  their SQLite tests and activation verification are serialized；
- D4-11 then D4-12 own the single Alembic head chain；never parallelize them or any other
  migration；
- `official_rate_book.py` shared owners remain serialized：activation/provider → Task 136；
- `annuity/service.py` order：D4-11 carrier PASS → Task 133 → Task 121；
- actual legacy import is after D4-12 and requires approved manifest；synthetic task tests
  do not authorize production migration。

Every SQLite-writing test acquires `GLOBAL_SQLITE_SERIAL_QUEUE`，maximum writer 1。Read-only
inspection, non-SQLite lint and conflict-free independent review may run in parallel。

## Effective counts and close propagation

Delta-4 adds 12 product Foundation nodes：

```text
effective product graph = 290 + 12 = 302
effective Foundation    = 204 + 12 = 216
deferred                = 86（不变）
```

This spec task、materialization controller/review/overlay 是 audit-only governance gates，
不计入 302/216。

后继 materialization must also update exactly these four close contracts：

1. `FPMS-V8-FOUNDATION-CLOSE-20260712-01` requires all 216 Foundation product nodes、
   delta-1/2/3/4 controllers and governance gates；
2. `FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01` may start only after effective
   Foundation close and existing customer decision gates；
3. `FPMS-V8-FINAL-ITEM-SLICE-LEDGER-20260712-01` lists all 302 product nodes, 12 D4
   additions, 17 re-freezes and all four delta overlays without miscounting governance；
4. `FPMS-V8-FINAL-CLOSE-20260712-01` validates cumulative delta-4 graph/hashes/gates and
   runs the release gate only at its manifest-defined final step。

No repo-wide Ruff/pytest/frontend build/full Playwright/release gate runs during spec、
materialization or ordinary High task execution unless an exact task contract requires it。

## Delta-4 materialization contract

Successor controller：
`FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-4-20260715-01`。

It creates one explicit supplemental batch manifest with：

- 12 new task-file rows；
- 17 existing task re-freeze/recovery rows；
- 4 close-propagation rows；
- 1 serialized controller row owning only manifest/overlay/controller artifacts。

Total：34 exact rows。Rows 1–33 each have one task-file owner；row 34 owns the common batch
manifest and deterministic cumulative overlay。No materializer edits product code/tests。

The row-to-owner map is exact；a materializer may not derive paths from IDs or write a
different task file：

| Row | Exact owned task-file path | Row class |
| ---: | --- | --- |
| 01 | `tasks/postdemo/v8/FPMS-V8-LC-CASE-OPENED-EVIDENCE-GUARD-20260715-01.md` | new D4 product task |
| 02 | `tasks/postdemo/v8/FPMS-V8-CASE-CREATE-OPENED-EVIDENCE-ADAPTER-20260715-01.md` | new D4 product task |
| 03 | `tasks/postdemo/v8/FPMS-V8-LC-FILING-PREPARATION-EVIDENCE-GUARD-20260715-01.md` | new D4 product task |
| 04 | `tasks/postdemo/v8/FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-EVIDENCE-GUARD-20260715-01.md` | new D4 product task |
| 05 | `tasks/postdemo/v8/FPMS-V8-FILING-SUBMISSION-EVIDENCE-RESOLVER-20260715-01.md` | new D4 product task |
| 06 | `tasks/postdemo/v8/FPMS-V8-DE-DELTA4-EVIDENCE-ROLE-EXTENSION-20260715-01.md` | new D4 product task |
| 07 | `tasks/postdemo/v8/FPMS-V8-DE-DELTA4-REGISTRATION-MATRIX-CORRECTION-20260715-01.md` | new D4 product task |
| 08 | `tasks/postdemo/v8/FPMS-V8-DE-OA-STRUCTURED-ATTACHMENT-PROMOTION-20260715-01.md` | new D4 product task |
| 09 | `tasks/postdemo/v8/FPMS-V8-CNIPA-246-LAYOUT-RATE-CANDIDATE-20260715-01.md` | new D4 product task |
| 10 | `tasks/postdemo/v8/FPMS-V8-CNIPA-ANNUITY-RATE-CANDIDATE-20260715-01.md` | new D4 product task |
| 11 | `tasks/postdemo/v8/FPMS-V8-ANNUITY-TASK-OBLIGATION-LINEAGE-CARRIER-20260715-01.md` | new D4 product task |
| 12 | `tasks/postdemo/v8/FPMS-V8-LEGACY-FEE-REDUCTION-PROVENANCE-CARRIER-20260715-01.md` | new D4 product task |
| 13 | `tasks/postdemo/v8/FPMS-V8-LC-FILING-RECEIPT-ARCHIVED-20260712-01.md` | existing re-freeze |
| 14 | `tasks/postdemo/v8/FPMS-V8-DE-GENERATED-ATTACHMENT-EVIDENCE-ADAPTER-20260712-01.md` | existing re-freeze |
| 15 | `tasks/postdemo/v8/FPMS-V8-DE-REVIEW-API-20260712-01.md` | existing re-freeze |
| 16 | `tasks/postdemo/v8/FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01.md` | existing re-freeze |
| 17 | `tasks/postdemo/v8/FPMS-V8-CASE-BATCH-FILING-EVENT-ADAPTER-20260712-01.md` | existing re-freeze |
| 18 | `tasks/postdemo/v8/FPMS-V8-FILING-EXTERNAL-SUBMISSION-ADAPTER-20260712-01.md` | existing re-freeze |
| 19 | `tasks/postdemo/v8/FPMS-V8-FILING-RECEIPT-LIFECYCLE-ADAPTER-20260712-01.md` | existing re-freeze |
| 20 | `tasks/postdemo/v8/FPMS-V8-OA-COPYABLE-ATTACHMENT-POLICY-20260712-01.md` | existing re-freeze |
| 21 | `tasks/postdemo/v8/FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01.md` | existing re-freeze |
| 22 | `tasks/postdemo/v8/FPMS-V8-FEE-REDUCTION-APPROVAL-CREATE-API-20260712-01.md` | existing re-freeze |
| 23 | `tasks/postdemo/v8/FPMS-V8-FO-OBLIGATION-DETAIL-READ-20260712-01.md` | recovery re-freeze |
| 24 | `tasks/postdemo/v8/FPMS-V8-ANNUITY-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01.md` | existing re-freeze |
| 25 | `tasks/postdemo/v8/FPMS-V8-FUTURE-ANNUITY-OBLIGATION-20260712-01.md` | existing re-freeze |
| 26 | `tasks/postdemo/v8/FPMS-V8-PCT-FEE-POLICY-20260712-01.md` | existing re-freeze |
| 27 | `tasks/postdemo/v8/FPMS-V8-LAYOUT-REGISTRATION-FEE-RULE-20260712-01.md` | existing re-freeze |
| 28 | `tasks/postdemo/v8/FPMS-V8-DECISION-GATE-LIST-API-20260712-01.md` | existing re-freeze |
| 29 | `tasks/postdemo/v8/FPMS-V8-LEGACY-FEE-REDUCTION-IMPORT-20260712-01.md` | existing re-freeze |
| 30 | `tasks/postdemo/v8/FPMS-V8-FOUNDATION-CLOSE-20260712-01.md` | close propagation |
| 31 | `tasks/postdemo/v8/FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01.md` | close propagation |
| 32 | `tasks/postdemo/v8/FPMS-V8-FINAL-ITEM-SLICE-LEDGER-20260712-01.md` | close propagation |
| 33 | `tasks/postdemo/v8/FPMS-V8-FINAL-CLOSE-20260712-01.md` | close propagation |
| 34 | `tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-4-20260715-01.md` | serialized controller |

Row 34 alone also owns exact shared outputs
`tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-4-20260715-01.md` and
`artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-4-20260715-01/analysis/cumulative_delta4_overlay.json`
plus its task-local deterministic validator/evidence family。Rows 01–33 do not edit either
shared output during materialization。

The cumulative delta-4 overlay must：

- hash-lock all immutable parent bytes and delta-3 manifest；
- use prior normalized task hashes as trust anchors before applying D4 latest-wins
  contract overrides；unknown non-Status drift fails closed；
- preserve Task 72's rejected successor section/evidence and Task 110's valid RED/partial
  test；
- prove 302 unique product nodes、216 Foundation、86 deferred、0 unresolved、0 cycle；
- prove all 12 new closures/allowlists/dependencies and all 17 re-freezes；
- prove migration head chain、shared-file order、SQLite queue、Foundation→Full→ledger→
  final→release order；
- produce deterministic validator, manifest/overlay hashes and separate per-task review
  verdicts；
- never treat current dirty peer files as current task output；use captured baselines and
  G2 concurrent validator rules。

## High execution handoff

After this spec and materialization each pass two independent review axes：

1. H4-0：D4-01→D4-03→D4-04 lifecycle guards serialized；D4-02 starts after D4-01；
2. H4-1：D4-06→D4-07→D4-08 document chain；Task 50 can start after D4-07；
3. H4-2：D4-05 resolver independent；then Tasks 59→65→66 and Task 60 with shared-source
   serialization；
4. H4-3：D4-09/D4-10 parallel implementation, serialized SQLite；D4-11→D4-12 migration
   single lane；
5. H4-4：dependency-ready API Tasks 51/95/169 and pure PCT Task 135 can run in
   non-conflicting lanes；
6. H4-5：activate synthetic/approved test candidates only inside scoped tests；production
   activation remains explicit。Then Tasks 136、133→121、255；
7. H4-R：Task 110 changed-mechanism recovery in a bounded direct lane；
8. release slots immediately feed independent cross-review or next dependency-ready
   task；all SQLite verification remains serialized。

High must not change this legal/evidence/rate/cardinality/transaction contract。A proven
contradiction stops only that lane with exact task/evidence/decision required and requests
manual Ultra reroute；it must not reopen broad V8 analysis。

## Acceptance

Delta-4 is Ultra-frozen only when：

- 12 new product tasks and 17 existing re-freezes have exact closure/non-closure/
  allowlist/dependency/TDD/error/transaction contracts；
- four lifecycle evidence kinds/object types/cardinalities and all adapter source/hash
  rules are exact；
- generated/OA typed evidence is runtime reachable without filename or RAW-role inference；
- three API routes/permissions/DTO/status/transaction semantics are exact；
- official PCT/layout/annuity facts cite primary CNIPA sources，candidate remains inactive，
  customer seed is never promoted；
- annuity/legacy carriers are SQLite-safe, migration-serialized and fail closed for legacy
  null/unapproved facts；
- Task 110 is correctly classified as liveness recovery, not rematerialized business
  design；
- graph count is 302/216/86，governance is excluded；
- independent domain/fail-closed reviewer and dependency/ownership reviewer both APPROVE；
- spec task scoped lint/test/scope、task gate and atomic evidence validation PASS；
- no product implementation、repo-wide gate、release gate、commit/push/reset/clean/stash/
  discard occurred。
