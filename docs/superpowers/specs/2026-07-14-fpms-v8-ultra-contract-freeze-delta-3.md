# FPMS V8 Ultra 契约冻结增量设计 3（2026-07-14）

## Purpose

本文是已接受 V8、Ultra delta-1 与 delta-2 的窄范围后继增量。它只处理 High
执行实际证明的四个问题：

1. `EvidenceRole` 追加 `RAW_ATTACHMENT` 后，通用登记服务会允许原始附件直接以
   `FINAL` 登记；
2. 同一枚举扩展会让外部提交服务把原始附件自动视为一个可提交角色；
3. 仓库 task gate 依赖 JSON 文本空格和字段顺序，而不是解析 JSONL；
4. 外部 atomic evidence helper 不理解显式并发 wave 的互斥 ownership，会把合法
   peer dirt 当作当前任务越界。

本增量不重做客户资料、V8 业务设计或 283-path catalog。上述四项均由代码审查或
可重复工具复现直接证明，不需要猜测新的法律、收费或客户政策。

## Authority and immutable parents

权威继承顺序：

1. `AGENTS.md`；
2. `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`；
3. `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`；
4. `docs/superpowers/specs/2026-07-13-fpms-v8-ultra-contract-freeze-delta.md`；
5. `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-2.md`；
6. 本文仅覆盖下列四个明确 closure 与其必要依赖、序列化和 close 传播。

以下父事实不可改写：

- 原 catalog：`283 = 197 Foundation + 86 deferred`；
- delta-1：3 个产品外部 prerequisite；
- delta-2：2 个产品外部 prerequisite；
- delta-1 spec SHA-256：
  `f7723e335cdb7d1dc5e7eff443418bffe306c4236a0462b959b9cbf979ba5fef`；
- delta-1 manifest SHA-256：
  `a6e29490775cc7079c995e63a3f0eecc0ac64ac2aa15ec71bbee92b952bbb420`；
- delta-1 overlay SHA-256：
  `47b5415a480c7c58c9074895c887a38a3c7d0717ba70a958e91608b6469bca3d`；
- delta-2 spec SHA-256：
  `724a21d30d10014f4fcced1a047b7969deb6df27c79a094c620243a7d51fad98`；
- delta-2 manifest SHA-256：
  `2ca2f161be0adb55ee69c0bd45f0ec2618c0b8e8f5faace1c2ac7fd9482fc723`；
- delta-2 overlay SHA-256：
  `211ad7fdc7bf0f71cbc2ddbd330de28e39003a33777d4358799dff95877fcf6b`。

旧 spec、plan、manifest、overlay、task evidence 和 PASS history 全部只读。delta-3
通过新的 cumulative overlay 追加事实，不回写旧历史。

## Story Shape Classification

- `shared_file_density`: high — 两个产品 guard 分别插入
  `evidence_service.py` 与 `evidence_workflow_service.py` 的既有串行链；两个工具各有
  仓库级共享脚本 ownership。
- `prereq_dependency_density`: high — RAW enum 任务必须等待两个 guard，外部提交
  adapter 和 Foundation/Full/Release close 都必须继承新 gate。
- `be_fe_coupling`: low — 本增量不改变 HTTP DTO、前端 wire 或 UI。
- `evidence_cost`: high — 四个实现任务均需独立 TDD、review、scope、dirty baseline
  与 task/atomic gates；SQLite-writing 产品测试仍全局串行。
- `chosen_runbook`: `P0-prereq-heavy-story`。

## Approved approach

- 建立两个产品 Foundation prerequisite；一个 task 只关闭一个 service rule。
- 先把允许状态/角色写成显式正向集合，再追加 RAW enum；枚举增长不得自动扩大
  登记或外部提交权限。
- 保留原九个角色的既有行为。本增量没有客户或设计依据把其中任何角色缩窄为
  “永远不可外部提交”；只明确排除 RAW 和未来未登记角色。
- 复用现有错误 surface，不制造新的 API envelope 或状态码。
- 建立两个 audit-only 仓库治理任务；它们修复执行工具，不计入产品 catalog 或
  Foundation 产品节点。
- 新的并发 validator 组合而不是修改外部 skill：先证明 peer ownership，再在临时
  本地 clone 中调用原 helper。没有 peer 时直接调用原 helper。
- materialization 只创建 task contracts、manifest 和 deterministic overlay；产品
  RED/GREEN 仍由 High 执行。

未采用：

- 把两个产品 guard 合成一个任务：会跨两个独立 shared source 和两个 closure；
- 只允许 `SUBMITTED_XML`：会未经业务证据缩窄已接受服务并阻断尚未实现的 OA
  adapter 角色选择；
- 在 RAW enum 任务内顺手修 service：违反原子边界并让该任务自证自己的 gate；
- 修改外部 `/Users/cfcc/.codex/skills/**`：超出仓库治理边界且不可审计发布；
- 让 validator 忽略全部 concurrent dirt：会削弱 scope fail-closed。

## Product prerequisite P1 — RAW registration state guard

任务：
`FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01`。

唯一 closure：在 `register_evidence_version(command, transaction)` 的任何 DB
读取、写入、flush 或 activity append 之前，按明确 role-value/state matrix 验证
登记权限。

允许文件：

- `backend/app/modules/documents/evidence_service.py`；
- `backend/tests/test_v8_raw_attachment_registration_guard.py`；
- 本任务文件与 `artifacts/<TASK-ID>/**`。

依赖：

- `FPMS-V8-DE-CONTRACTS-20260712-01` — PASS；
- `FPMS-V8-DE-REGISTER-VERSION-20260712-01` — PASS。
- `REPO-CONCURRENT-WAVE-ATOMIC-EVIDENCE-VALIDATION-20260714-01` — audit gate
  prerequisite；不计入产品 graph。P1 可在 G2 前只读分析，但不得初始化、编辑、验收
  或声称 PASS。

### Exact role/state matrix

原九个 role value 均保持既有 `DRAFT | FINAL` 登记能力：

```text
FILING_FULL_WORD
TRACKED_REVISED_WORD
FILING_COMPONENT
EXTERNAL_XML_PACKAGE
OFFICIAL_SUBMISSION_LIST
OFFICIAL_FINAL_PDF
SUBMITTED_XML
OFFICIAL_RECEIPT
CLIENT_LETTER_WORD
```

新增和未来值：

| role value | DRAFT | FINAL | outcome |
| --- | --- | --- | --- |
| `RAW_ATTACHMENT` | allow | deny | denied FINAL is 400 `EVIDENCE_VERSION_INVALID`, `details={"field":"state"}` |
| any future enum value not explicitly listed | deny | deny | 400 `EVIDENCE_VERSION_INVALID`, `details={"field":"role"}` |

guard 可在 RAW enum 尚未加入时使用字符串值冻结未来边界；不得通过 fallback、
`else: allow` 或“只要是 `EvidenceRole` 就允许”实现。原命令类型、文本、enum 类型、
hash 校验顺序保持；role/state matrix 在上述基本校验之后、第一次 transaction access
之前执行。

### TDD and verification

- RED 使用测试内的 forward enum（原九项 + `RAW_ATTACHMENT` + 一个 future value）
  替换 service module 的 enum 引用；当前 service 会越过预期 guard 并访问 transaction。
- GREEN 通过公开 `register_evidence_version()` 证明：RAW+DRAFT 可以正常创建
  `PENDING` evidence；RAW+FINAL 和 future role 在 DB 前失败且零写入；原九项接受
  行为不变。
- 测试不得提前修改 `evidence_contracts.py` 或把 RAW enum 加入本任务。
- targeted pytest 使用 SQLite，进入 `GLOBAL_SQLITE_SERIAL_QUEUE`，最大并发写者 1。

显式 non-closure：不追加 enum，不改 API/attachment adapter/review/promotion，不改
schema/migration，不改变原九项语义。

## Product prerequisite P2 — external-submission role allowlist

任务：
`FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01`。

唯一 closure：在 `finalize_external_submission(command, transaction)` 的 replay、
state/review 检查、CAS update 和 activity append 之前，按明确正向角色集合验证 stored
evidence role；CAS predicate 同时锁定已验证的 exact role。

允许文件：

- `backend/app/modules/documents/evidence_workflow_service.py`；
- `backend/tests/test_v8_external_submission_role_allowlist.py`；
- 本任务文件与 `artifacts/<TASK-ID>/**`。

依赖：

- `FPMS-V8-DE-FINALIZE-EXTERNAL-SUBMISSION-SEAM-20260712-01` — PASS。
- `REPO-CONCURRENT-WAVE-ATOMIC-EVIDENCE-VALIDATION-20260714-01` — audit gate
  prerequisite；不计入产品 graph。P2 可在 G2 前只读分析，但不得初始化、编辑、验收
  或声称 PASS。

### Exact positive set and failure behavior

正向集合恰为 RAW 扩展前已经被 accepted seam 接受的九个 role value：

```text
FILING_FULL_WORD
TRACKED_REVISED_WORD
FILING_COMPONENT
EXTERNAL_XML_PACKAGE
OFFICIAL_SUBMISSION_LIST
OFFICIAL_FINAL_PDF
SUBMITTED_XML
OFFICIAL_RECEIPT
CLIENT_LETTER_WORD
```

- `RAW_ATTACHMENT` 和任何未来未显式加入集合的 enum value 均拒绝；
- 复用 409 `EXTERNAL_SUBMISSION_EVIDENCE_CONFLICT`，不新增未经设计的公开 code；
- 拒绝发生在 projection capture、idempotency replay、carrier mutation、CAS 和
  activity append 之前；fresh 与 replay 均零写入；
- CAS where 条件新增 `DocumentEvidenceVersion.role == version.role`，防止验证后角色
  并发变化；rowcount 冲突继续使用既有
  `EXTERNAL_SUBMISSION_CONCURRENCY_CONFLICT`；
- malformed stored role 继续使用既有 409 evidence-conflict 语义。

### TDD and verification

- RED 使用 forward enum 使 RAW/未来值通过当前 `_validate_stored_identity()`，证明
  当前公开 service 会继续进入 replay/update 路径。
- GREEN 通过公开 `finalize_external_submission()` 证明原九项兼容、RAW 与未来值在
  fresh/replay 路径均 fail closed、CAS 包含 exact role、case projection 和 evidence
  carrier 没有拒绝副作用。
- targeted pytest 使用 SQLite，必须与 P1 及所有其他 SQLite-writing test 串行。

显式 non-closure：不追加 RAW enum，不改变 review/current/final 规则，不实现 filing
或 OA adapter，不收窄原九项，不新增 HTTP。

## Re-freeze of the blocked RAW role task

任务：`FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01`。

delta-3 materialization 将它从
`BLOCKED / ULTRA CONTRACT UPDATE REQUIRED` 重新冻结为
`READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-14 / NOT STARTED`，但仅在 task contract
明确加入 P1 与 P2 两个依赖之后。

原 closure、allowlist、RED/GREEN 和非门禁含义保持不变。GREEN 后除自己的 contract
test 外，必须只读重跑 P1、P2 两个 guard suite，且使用真实
`EvidenceRole.RAW_ATTACHMENT`，证明：

- RAW 只能以 DRAFT 登记；
- RAW 无法 fresh 或 replay external submission；
- 原九个 enum member、值和顺序保持，RAW 仍是第十项；
- attachment adapter 与 overlay contracts 保留对本 task 的既有依赖。

## Governance G1 — structural JSONL repository task gate

任务：`REPO-TASK-GATE-JSONL-STRUCTURAL-VALIDATION-20260714-01`。

唯一 closure：把 `scripts/task_validate.sh` 的 lint/test 成功判断从 whitespace-sensitive
`grep` 改为 stdlib JSON structural validation。

允许文件：

- `scripts/task_validate.sh`；
- `scripts/tests/test_task_validate_jsonl.py`；
- 本任务文件与 `artifacts/<TASK-ID>/**`。

精确 contract：

- 每个非空行必须是合法 JSON object；malformed JSON、array/string/number/null line
  全部 fail closed，并报告 line number；
- 对 `lint` 与 `test` 各要求至少一个 exact `step` 且 `type(rc) is int and rc == 0` 的
  record；`false`、`"0"`、浮点 `0.0` 均不是成功；
- 允许 JSON whitespace、key order 和额外字段变化；
- unrelated string 中的伪 `"step":"lint"` substring 不能通过；
- 保留“早期 RED/失败 + 后续 GREEN 成功即可通过”的现有语义；
- missing artifact/summary/results/diff 的既有检查与输出 `Task Gate PASS` 保持；
- 只用 shell + Python stdlib，不改 `evidence_run.sh`、`release_gate.sh`、外部 skill 或
  历史 evidence。

测试为仓库级临时目录/subprocess 测试，不导入 backend conftest、不写 SQLite。lint
至少运行 `bash -n scripts/task_validate.sh` 和 Python compile/format-scope check。

显式 non-closure：不增加新的 required evidence step，不改变 atomic helper，不处理
并发 ownership，不运行 release gate。

## Governance G2 — concurrent-wave atomic evidence validator

任务：`REPO-CONCURRENT-WAVE-ATOMIC-EVIDENCE-VALIDATION-20260714-01`，依赖 G1 PASS。

唯一 closure：新增仓库 wrapper，在不修改外部 atomic helper 的前提下，验证一个
显式 batch manifest 中非重叠 peer ownership，并在隔离 clone 中调用原 helper 完成
当前任务的 atomic evidence validation。

允许文件：

- `scripts/atomic_evidence_validate.py`；
- `scripts/tests/test_atomic_evidence_validate.py`；
- 本任务文件与 `artifacts/<TASK-ID>/**`。

### Exact CLI

```bash
python3 scripts/atomic_evidence_validate.py <TASK-ID> \
  --required-step lint --required-step test \
  --required-step independent_review --required-step scope \
  --manifest <COMMON-EXECUTION-BATCH-MANIFEST> \
  --concurrent-task <PEER-TASK-ID>
```

`--required-step` 与 `--concurrent-task` 可重复；peer ID 不得重复或等于 current task。
有 peer 时 `--manifest` 必须恰好出现一次，且该共同 manifest 必须同时列出 current
与所有 peers。没有 `--concurrent-task` 时不得传 manifest，wrapper 直接调用原
external helper，保持原行为和 rc。

### Fail-closed ownership proof

有 peer 时 wrapper 必须：

1. 加载 current 与每个 peer 的 `artifacts/<ID>/task.json`；task ID、task file、
   allowlist、repo root 缺失或不匹配即失败；task file path 的 stem 必须等于 task ID；
2. 结构化解析唯一共同 manifest。支持既有 `## NNN. <TASK-ID>` + exact
   `- Task file: \`path\`` entry，和包含 exact task-file path 的表格 row；current 与
   每个 peer 必须各有且仅有一个 ID↔path 精确 row。CLI 的 current+peer 集合就是本次
   active wave；wrapper 不自行调度，但拒绝任何不在同一共同 execution manifest 的
   task；
3. 结构化解析每个 task file 的 `## Allowed Files`，要求规范化后的精确集合与
   `task.json.allowlist` 完全相等；不能只信任 evidence init CLI；
4. 规范化 repo-relative path，拒绝 absolute path、`..`、symlink escape、目录
   allowlist、rename/copy status 和模糊 glob；仅允许每个 task 自己的 exact
   `artifacts/<TASK-ID>/**` evidence glob；
5. 证明 current 与 peers 的所有非 evidence allowlist path 两两不重叠；一个 path
   不能由两个 peer 声称，目录前缀也不能产生交叠；
6. 使用 `git status --porcelain=v1 -z --untracked-files=all` 读取 NUL-safe exact
   status；rename/copy 的两个 path 均触发显式拒绝，不用空白切割或 ` -> ` 猜测；
7. 读取 current init 时的 `baseline_external_files.txt`。当前 worktree 中每个不属于
   current allowlist、又不在该 baseline 的 dirty path，必须由恰好一个已声明 peer
   的 exact allowlist 拥有；未知或多重 ownership 均失败；
8. 不改写 baseline、不追加 blanket ignore、不信任仅来自命令行但没有 task.json/
   manifest 证明的 peer。

### Isolated validation

ownership proof 通过后：

- 创建临时本地 clone，只含 committed baseline；不联网；
- 复制 current task 的 exact allowlist files、删除状态以及自己的完整 artifact family；
- 不复制 peer source/test/task/evidence；
- 在 clone 中调用原
  `/Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate`，
  传入全部 required steps；
- 原样转发 stdout/stderr/exit code，finally 删除临时目录；
- 不 commit、push、reset、clean、stash 或改写主 worktree。

测试使用临时 git repo 和 stdlib mock/subprocess，不导入 backend conftest、不写
SQLite；覆盖无 peer 直通、合法两个 peer、manifest 缺失、allowlist 交叠、未知 dirt、
manifest ID/path 重复或不匹配、task.json/task-file allowlist 不等、目录 allowlist、
多重 owner、NUL-safe rename/copy、非法 glob、helper 非零 rc 传播和临时目录清理。

### Mandatory execution rule after G2

- G1 必须先 PASS；G2 单 lane 实现并用原 helper 或 wrapper 无-peer直通自验；
- G2 PASS 后，任何存在 post-init peer dirt 的 task 都必须使用本 wrapper，并提供一个
  同时包含 current/全部 peers 的 authoritative execution manifest；
- 一个 manifest 中 current+peer 的显式集合就是该次验证 wave。不同 manifest 的
  task 不得拼成 peer 集合；若确需混合，lead 必须先创建/批准一个共同 explicit batch
  manifest，而不是扩大 ignore；
- 没有 peer 的单 lane task 可继续直接调用原 helper，也可调用 wrapper 无-peer直通；
- delta-3 cumulative overlay 对并发执行全局覆盖旧 task file 中的 direct-helper
  command；这只改变证据验证入口，不削弱 task 自身 required steps、allowlist 或 gate。

显式 non-closure：不修改外部 skill、G1、evidence schema、release gate 或业务代码；
不允许并发共享 ownership。

## Dependency and serialization overrides

### Product graph

- P1 依赖 accepted contracts/register service；
- P2 依赖 accepted finalize seam；
- P1/P2 均以 G2 PASS 为 audit gate prerequisite；G1→G2→P1/P2 acceptance，G1/G2
  不进入产品 graph；
- RAW role task 直接依赖 P1 与 P2；
- `FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01` 增加 P2 为 shared-file 前置；
- `FPMS-V8-FILING-EXTERNAL-SUBMISSION-ADAPTER-20260712-01` 直接依赖 P2；
- `FPMS-V8-OA-EXTERNAL-SUBMISSION-EVIDENCE-20260712-01` 直接依赖 P2；
- attachment adapter 与 overlay contracts 继续通过 RAW role task 继承两个 guard；
- Foundation close 直接要求 delta-3 controller、P1、P2、G1、G2 的 task/evidence
  gates。G1/G2 是 audit gate，不是产品 graph 节点。

### Shared ownership order

`backend/app/modules/documents/evidence_service.py`：

```text
REGISTER_VERSION
→ REGISTER_DERIVATION
→ CURRENT_VERSION_RULE
→ REVIEW_SERVICE
→ RAW_ATTACHMENT_REGISTRATION_GUARD
→ COMPENSATION_PERIOD_ANNUITY
→ OPEN_LICENSE_ANNUITY
```

`backend/app/modules/documents/evidence_workflow_service.py`：

```text
FINALIZE_EXTERNAL_SUBMISSION_SEAM
→ EXTERNAL_SUBMISSION_ROLE_ALLOWLIST
→ PREPARE_OA_REPLY_SEAM
→ existing layout/patent-fee owners in their original relative order
```

`scripts/task_validate.sh` 仅 G1 拥有；`scripts/atomic_evidence_validate.py` 仅 G2
拥有。二者先 G1、后 G2，任何 shared-file verification 均串行。

所有 SQLite-writing test 继续进入 `GLOBAL_SQLITE_SERIAL_QUEUE`，最大并发写者 1。
G1/G2 的 stdlib 临时目录测试不占 SQLite queue，可与只读或其他无冲突工作并行。

## Effective counts and close propagation

delta-3 只新增 P1、P2 两个产品节点：

```text
effective product graph = 283 + 3 + 2 + 2 = 290
effective Foundation    = 197 + 3 + 2 + 2 = 204
deferred                = 86（不变）
```

G1、G2、三个 Ultra materialization controller 都是 audit-only governance gates，
不计入 290/204。原 197-row Foundation manifest 不改写。

- Foundation close：要求三个 controller、七个产品 external prerequisite（3+2+2）、
  G1/G2，以及其余原 Foundation task gates；
- Full activation：必须经有效 Foundation close，原 7 GLOBAL + 22 form decision gates
  不变；
- final item-to-slice ledger：列出 delta-1/2/3 overlays、七个产品 externals 与 G1/G2
  的 audit 证据，不把治理任务冒充产品 slice；
- final close：运行新的 cumulative delta-3 validator 与所有新增 task gates；原
  release gate 仍是 manifest-defined 最后一步，不提前、不重复、不削弱。

## Delta-3 materialization contract

后继 controller：
`FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01`。

它创建一个 explicit 15-row supplemental contract/execution manifest。每行只有一个
exact task-file path，同时记录 materialization wave 与后续 High execution wave；
controller PASS 前只授权 task-contract materialization，controller PASS 且用户手动
切回 High 后，High wave 列才授权按各 task contract 实施。该共同 manifest 也是 P1/P2
并发 atomic validation 的 authoritative manifest：

1. P1 registration guard；
2. P2 external-submission allowlist；
3. RAW role re-freeze；
4. prepare-OA shared-file dependency override；
5. filing external-submission adapter override；
6. OA external-submission adapter override；
7. G1 structured JSONL gate；
8. G2 concurrent validator；
9. Foundation close override；
10. Full activation override；
11. final item-to-slice ledger override；
12. final close override；
13. attachment adapter dependency/meaning audit override；
14. overlay contracts dependency/meaning audit override；
15. serialized delta-3 controller。

Rows 01–14 各由一个 task-file owner 物化，不实施产品；row 15 独占 manifest 与本
controller artifact family。

deterministic cumulative overlay 必须：

- hash-lock 四个 immutable baseline JSON、delta-1 manifest/overlay 与 delta-2
  spec/manifest/overlay 的原始 bytes，并额外 hash-lock delta-1 spec 原始 bytes；
- 组合 baseline、delta-1、delta-2、delta-3 graph，证明 290 nodes、0 unresolved、
  0 cycles、204 unique effective Foundation IDs；
- 先从 delta-1、delta-2 overlay 的 exact `task_sha256` 建立历史 trust anchor，后继
  overlay 对同一 task 以 latest-wins 覆盖旧 hash。对每个当前父 task，把首个
  `Status:` 行恢复成该父 overlay 冻结的 exact READY 文本后，必须重新得到旧
  `task_sha256`；只有这个证明通过后，才可生成 Status-sentinel normalized hash；
- RAW blocked task 是唯一明确 successor exception：先恢复 delta-2 READY Status，并
  精确移除 `## Blocked Review Outcome — 2026-07-14` section，必须重新得到 delta-2
  `task_sha256`；随后单独验证保留的 blocked section 与其独立 review evidence，最后
  才应用本轮 RAW override。任何其他 non-Status drift 均 fail closed；
- 保存已通过上述历史证明的父 task normalized SHA-256。后续合法执行态变化不构成
  contract drift，其他任何正文变化仍 fail closed；不得直接 hash 当前 task 并把未知
  drift 重新 canonize；
- 对本轮 14 个 task files 保存 exact closure、allowlist、dependencies 与 normalized
  task hash；
- 验证上述两个 shared source chain、G1→G2、SQLite queue、Foundation→Full→ledger
  →final→release 顺序；
- 不运行旧 delta validator 作为未来 close 的充分条件。旧 validator/evidence 保留
  历史只读；Foundation、Full、Final 后续使用 cumulative delta-3 validator。

## High execution handoff

Ultra materialization与两次独立复审 PASS 后，用户手动切回 High。执行顺序冻结为：

1. H3-0：G1 单 lane；
2. H3-1：G2 单 lane，完成共同 manifest/task/allowlist/isolated-clone regression；
3. H3-2：P1 与 P2 两个非冲突实现 lane；两者都使用本 delta-3 共同 execution
   manifest 和对方 peer ID 调用 G2 wrapper；两个 SQLite RED/GREEN 串行；
4. H3-3：两个 guard PASS 后，RAW role 单 lane重新执行；
5. 随后把 prepare-OA、filing/OA adapters 与其余 dependency-ready Foundation tasks
   交回 maximal-safe-wave scheduler；任何有 peer 的 validation 都执行 G2 mandatory
   rule。

G2 PASS 前 P1/P2 只允许只读 inspection，不得初始化或编辑。释放的 slot 立即用于
独立 review 或下一 dependency-ready、file-conflict-free task。

High 不得自行改变本 spec、role/state matrix、positive set、error surface、counts 或
close semantics。若实现证明这些合同无法同时成立，停止受影响 lane 并再次请求用户
手动切 Ultra；不扩张原任务。

## Acceptance

本 delta-3 只有在以下条件全部满足后可称为 Ultra-frozen：

- 四个独立实现任务合同完整，closure/non-closure/allowlist/TDD/evidence 均明确；
- RAW task 的两个 guard 依赖与真实成员回归测试明确；
- filing/OA/prepare-OA 和 close 传播无 bypass；
- effective graph 290、Foundation 204、deferred 86，G1/G2 不混入产品计数；
- parent bytes 不改写，normalized task hash 只忽略 Status 行；
- latest-parent exact hashes 与 RAW rejected-successor exception 均先通过历史 trust
  anchor，不能把当前非 Status drift 重新 canonize；
- G1→G2→并发产品验收，所有 declared-peer validation 都通过共同 manifest 锚定的
  repository wrapper；
- 两名独立 reviewer 分别批准 fail-closed/domain contract 与 tooling/graph contract；
- spec task 的 scoped lint/test/scope、task gate 和 atomic evidence validation PASS；
- 未运行产品 pytest、repo-wide Ruff、frontend build、Playwright、release gate，未
  commit/push/reset/clean/stash/discard。
