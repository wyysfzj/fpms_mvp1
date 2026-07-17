# FPMS Atomic Evidence 精确对账检查点设计（2026-07-15）

## 1. Purpose

本文定义一个窄范围、显式启用、fail-closed 的 atomic-evidence 恢复机制，用于关闭
四个产品实现和独立复审均已完成、但被长寿命 dirty worktree ownership 冲突阻断的
V8 Foundation 任务：

1. `FPMS-V8-FO-PREVIEW-FE-ADAPTER-20260712-01`；
2. `FPMS-V8-ANNUITY-PAYABLE-AMOUNT-RULE-20260712-01`；
3. `FPMS-V8-DE-ATTACHMENT-EVIDENCE-ATOMIC-ADAPTER-20260712-01`；
4. `FPMS-V8-LC-FILING-PREPARATION-STARTED-20260712-01`。

本文不改变任何产品、法律、费用、文书或谱系语义。它只为 atomic evidence 增加一个
新的精确状态 authority；没有该 authority 时，现有 validator 继续按原规则拒绝。

## 2. Authority and observed blocker

权威顺序：

1. `AGENTS.md`；
2. `REPO-CONCURRENT-WAVE-ATOMIC-EVIDENCE-VALIDATION-20260714-01`（G2）；
3. `REPO-DELTA3-PATH-ONLY-TABLE-MANIFEST-COMPATIBILITY-20260714-01`；
4. 本文仅追加 checkpoint mode 与一次四任务 reconciliation authority。

已复现事实：

- 外部 evidence init 使用默认 `git status --porcelain`，可能把未跟踪目录折叠成
  `scripts/tests/`；它没有保存具体 descendant、状态、mode 或内容 hash；
- G2 使用 `git status --porcelain=v1 -z --untracked-files=all`，按具体路径和 exact
  baseline membership 校验，因此正确拒绝 collapsed marker；
- 当前审计观察到 205 个 dirty path；四任务 unknown union 为 64，其中 34 个没有
  collision-free 的合格 owner；
- G2 与后续 path-only compatibility 任务必须同时解释各自 dirty task/tool history，
  但它们又共同声明 wrapper 与 wrapper test，不能组成无冲突 active-peer 集合；
- collapsed-directory prefix 方案已经独立 Ultra review 后拒绝，因为它无法区分
  init-time descendant 与 post-init descendant。

因此，现有 exact-peer 模式没有合法 peer set；省略 peer、改写 baseline、目录前缀
放行或构造 umbrella owner 均不是可接受修复。

## 3. Story Shape Classification

- `shared_file_density`: high — G3 串行拥有 repository wrapper/test；四个产品 task
  contract 需要各自独立 ownership；G4 是全 worktree 的只读 authority。
- `prereq_dependency_density`: high — G1/G2/path-only compatibility、G3、四个 contract
  overlay、G4 和四个最终状态收口严格有序。
- `be_fe_coupling`: none — 不改变产品运行时或前后端接口。
- `evidence_cost`: high — checkpoint 必须覆盖完整精确状态、逐路径 authority、独立
  review、四个 validator 结果和状态-only finalization。
- `chosen_runbook`: `P0-prereq-heavy-story`。

## 4. Approved approach

采用两层设计：

- **G3 — checkpoint validation mechanism**：为 repository wrapper 增加 opt-in、
  content-addressed、exact-state checkpoint mode；原 no-peer/peer mode 不变。
- **G4 — four-task reconciliation authority**：在静默窗口生成一个精确 checkpoint，
  独立审查每一条历史 reconciliation，随后只读运行四个 atomic validator。

四个产品 task file 各自接受一个 evidence-only contract overlay，只增加 G3/G4 依赖、
checkpoint close 命令和 status-only finalization 规则；不得更改其 closure、non-closure、
产品 source/test 或已批准 review history。

未采用：

- collapsed directory prefix：会授权无法观察的后加 descendant；
- task.json/owner graph 全量修复：当前 metadata 和 shared-file history 不能形成唯一、
  无冲突 owner graph；
- integration commit：当前 Goal 明确禁止 commit，且 worktree 含尚未最终关闭的任务；
- replay scoped patch 后直接调用外部 helper：无法检测当前任务的越权写入；
- snapshot timestamp/mtime/latest-owner inference：没有可信时间或签名 authority。

## 5. Universal invariants

1. 原 `task.json`、`baseline_allowlist.diff`、`baseline_external_files.txt` 永不重写、
   append 或重新初始化。
2. checkpoint 记录 concrete path；目录、prefix、glob、模糊 owner 均不产生 authority。
3. checkpoint 固定一个 exact Git HEAD 和完整 NUL-safe dirty path set。
4. 每条 path 固定 porcelain `XY`、kind、mode、worktree SHA-256，以及适用的 index/HEAD
   OID 或 deletion tombstone。
5. rename、copy、symlink、非规范路径、缺失/新增 path、状态或 byte drift 全部拒绝。
6. 每条 path 必须有一种显式 authority：已接受 task lineage 的唯一 terminal custodian，
   或 G4 对 exact byte 的逐路径 reconciliation exception。后者不声明历史作者或编辑权。
7. reconciliation exception 必须证明该 path 不在四个 subject allowlist 和 subject
   baseline-subtracted patch 中，给出 evidence references/reason code，并被独立 reviewer
   单独接受；任何 unresolved entry 阻断 G4。
8. 四个 subject 的 task、allowlist、source/test bytes、baseline、diff 和独立复审均由
   checkpoint anchor 固定。只允许后续 `Status:` 行变化，并由独立 status review 验证。
9. checkpoint seal 后进入 quiescent close window；除 G4 自身 ignored artifact outputs
   外，禁止任何 worktree mutation。任何 drift 使全部未执行 validator 失效。
10. G3 仍在临时 clone 中只复制当前 task 的 exact allowlist 与 artifact family，并调用
    未修改的外部 helper；checkpoint 不把外部 dirt 复制进 isolated clone。

## 6. G3 — reconciliation checkpoint mode

### 6.1 Atomic task

Task ID：
`REPO-ATOMIC-EVIDENCE-RECONCILIATION-CHECKPOINT-MODE-20260715-01`。

唯一 closure：在 `scripts/atomic_evidence_validate.py` 增加一个 opt-in checkpoint
validation mode，并在现有 stdlib regression module 中冻结其公开行为。

允许文件：

- G3 task file；
- `scripts/atomic_evidence_validate.py`；
- `scripts/tests/test_atomic_evidence_validate.py`；
- `artifacts/<G3-TASK-ID>/**`。

### 6.2 Public CLI

```bash
python3 scripts/atomic_evidence_validate.py <TASK-ID> \
  --required-step lint \
  --required-step test \
  --required-step independent_review \
  --required-step scope \
  --reconciliation-checkpoint <REPO-LOCAL-CHECKPOINT-JSON> \
  --checkpoint-review <REPO-LOCAL-REVIEW-JSON> \
  --checkpoint-sha256 <LOWERCASE-SHA256>
```

规则：

- 三个 checkpoint 参数必须一起出现；
- checkpoint mode 与 `--manifest`、`--concurrent-task` 互斥；
- 未提供 checkpoint 参数时，现有 no-peer/peer CLI、错误、delegation 和 return code
  保持兼容；
- 没有从 peer failure 到 checkpoint 的自动 fallback；
- checkpoint/review 必须是 repository-local regular file，禁止 symlink/escape。

### 6.3 Canonical checkpoint schema

```json
{
  "schema": "fpms.atomic-worktree-reconciliation/v1",
  "authority_task_id": "REPO-V8-FOUR-TASK-WORKTREE-RECONCILIATION-AUTHORITY-20260715-01",
  "repo_head": "<40-hex-commit>",
  "subjects": [
    {
      "task_id": "<TASK-ID>",
      "task_file": "tasks/.../<TASK-ID>.md",
      "status_normalized_task_sha256": "<sha256>",
      "task_json_sha256": "<sha256>",
      "allowlist_sha256": "<sha256>",
      "baseline_files": [{"path": "artifacts/...", "sha256": "<sha256>"}],
      "non_evidence_allowlist_state": [
        {"path": "exact/file", "kind": "regular", "mode": "100644", "sha256": "<sha256>"}
      ],
      "diff_sha256": "<sha256>",
      "review_path": "artifacts/.../review/independent_rereview.md",
      "review_sha256": "<sha256>"
    }
  ],
  "dirty_entries": [
    {
      "path": "exact/repository/path",
      "xy": "??",
      "kind": "regular",
      "mode": "100644",
      "worktree_sha256": "<sha256>",
      "index_oid": null,
      "head_oid": null,
      "authority": {
        "kind": "task_lineage",
        "terminal_task_id": "<TASK-ID>",
        "anchors": [{"path": "artifacts/...", "sha256": "<sha256>"}]
      }
    }
  ],
  "ignored_authority_artifact_root": "artifacts/REPO-V8-FOUR-TASK-WORKTREE-RECONCILIATION-AUTHORITY-20260715-01"
}
```

`authority.kind` 只允许：

- `task_lineage`：有唯一 terminal custodian；serialized predecessor 只作为历史 lineage，
  不成为 active owner；
- `reconciliation_exception`：由 G4 对该 exact byte 提供 path-specific reason、subject
  exclusion proof、evidence references 和独立批准，不授予目录或未来 byte authority。

checkpoint canonical JSON 使用 UTF-8、sorted keys、紧凑 separators 和末尾 LF；CLI
给出的 SHA-256 必须与 bytes 完全一致。

### 6.4 Independent checkpoint review

`--checkpoint-review` JSON 至少包含：

```json
{
  "schema": "fpms.atomic-worktree-reconciliation-review/v1",
  "checkpoint_sha256": "<sha256>",
  "verdict": "APPROVED",
  "reviewer_role": "independent Ultra repository-governance reviewer",
  "p0": 0,
  "p1": 0,
  "p2": 0,
  "review_markdown_path": "artifacts/.../review/checkpoint_review.md",
  "review_markdown_sha256": "<sha256>"
}
```

缺失、非 APPROVED、finding 非零、checkpoint hash 不一致、review markdown 漂移均拒绝。

### 6.5 Validation algorithm

1. 校验 CLI 组合和 checkpoint/review locality；
2. 校验 canonical bytes、expected hash、review binding 和 pinned HEAD；
3. 复用 G2 的 task metadata、allowlist、path normalization、symlink、rename/copy 检查；
4. 重算四个 subject anchor，任何 source/test/task non-status/diff/review/baseline 漂移拒绝；
5. NUL-safe 读取完整 live dirty set，与 `dirty_entries` 做 exact set/status/mode/hash/OID
   equality；
6. 校验每条 authority，禁止 unresolved、duplicate terminal custodian 或 prefix authority；
7. 仅忽略 G4 自身 artifact root 的新增 output；checkpoint 与 review 文件仍须 hash 相同；
8. 创建 pinned-HEAD 临时 clone，只复制当前 task allowlist/artifacts，调用未修改 helper；
9. 透传 stdout/stderr/return code，并无条件删除 clone。

### 6.6 Required RED/GREEN coverage

- valid exact checkpoint + approved bound review 成功 delegation；
- collapsed `scripts/tests/` 本身不授权 descendant；只有 checkpoint 中同名 concrete
  path、exact hash 和 authority 才可通过；
- new/missing/surplus path、content/status/mode/OID drift、later descendant 全部失败；
- malformed path、directory/glob/prefix、symlink、rename/copy 全部失败；
- wrong task/HEAD/checkpoint hash、baseline/task metadata/source/test/diff/review anchor
  全部失败；
- missing/unordered/tampered lineage、unresolved exception、two terminal owners 全部失败；
- checkpoint/peer 参数混用失败；
- isolated clone、cleanup、return-code propagation 与全部既有 wrapper regressions 保持
  GREEN。

### 6.7 G3 non-closure

不修改 external helper、G1/G2 历史、task gate、AGENTS、manifest、existing baseline、
产品文件或 release gate；不建立通用 checkpoint chain，不实现 prefix compatibility，
不生成当前四任务 checkpoint。

## 7. Four evidence-only task contract overlays

四个现有 task file 分别由一个独立 owner 更新，只允许：

- 保留已批准产品 closure/non-closure、source/test bytes 和 review history；
- 增加 G3 与 G4 audit dependency；
- 把最终 atomic validation 指向 G4 checkpoint/controller evidence；
- 冻结 G4 后只允许 `Status:` 行变化和 task-local summary/diff/status-review 更新；
- 禁止重跑产品测试，除非 status reviewer 发现产品 byte drift。

四个 overlay 不增加产品 graph node，不改变 Foundation 204 count。任何 source/test、
allowlist、风险、runbook 或产品 acceptance 变化必须另行 replan。

## 8. G4 — four-task worktree reconciliation authority

### 8.1 Atomic task

Task ID：
`REPO-V8-FOUR-TASK-WORKTREE-RECONCILIATION-AUTHORITY-20260715-01`。

唯一 closure：在一个 quiescent close window 内，对 seal 时的完整 dirty worktree 生成
一个 canonical checkpoint 和独立 review，并使用 G3 对四个 subject 执行只读 atomic
validation，记录逐任务结果。

允许文件：

- G4 task file；
- `artifacts/<G4-TASK-ID>/**`。

G4 不编辑 wrapper、产品 task/source/test、baseline、manifest 或 Git state。

### 8.2 Reconciliation authority

G4 必须对 seal 时的完整 concrete dirty set 逐路径分类。设计审计中的 `205` 只是发现
快照，不是未来固定数量；G4 以 seal 时实际 NUL-safe inventory 为准。

对无法由有效 task lineage 唯一解释的 path，G4 可使用
`reconciliation_exception`，但必须逐路径提供：

- exact path/status/mode/hash/OID；
- 该 path 不属于四个 subject allowlist 的结构证明；
- 该 path 不出现在四个 subject baseline-subtracted patch 的证明；
- 可用的历史 controller/review/hash evidence；
- 无可靠历史 owner 时使用 `LEGACY_METADATA_INCOMPLETE` reason，并明确“不声明作者”；
- independent reviewer 对该 exact byte 的接受结论。

没有 evidence 或 reviewer 不接受时，G4 必须 `BLOCKED`；不得用一个 blanket exception
覆盖多条 path。

shared-file lineage 允许按已批准序列列出 predecessor，但只保留一个 terminal
custodian。例如 wrapper/test lineage 为 G2 → path-only compatibility，terminal custodian
是后者；两者不得同时成为 active owner。

### 8.3 Quiescent close sequence

1. G3 PASS；四个 evidence-only overlay 独立批准；四个产品 source/test/review 不变；
2. 暂停所有其他 implementation、formatter、test 和 artifact-finalization lane；
3. G4 生成 checkpoint，写入 canonical hash；
4. 独立 Ultra reviewer 审核 checkpoint 和每个 reconciliation exception；
5. checkpoint/review 均冻结后，按 newest baseline first 只读执行：FO Preview FE →
   Annuity Payable → DE Attachment Adapter → LC Filing Preparation；
6. 四个 G3 command 的 stdout/stderr/rc 仅写入 G4 ignored artifact outputs；Git-visible
   path 不得变化；
7. 任一 validator 非零或 live-state drift：停止剩余命令，G4 为 BLOCKED；
8. 四个 rc0 后，G4 完成 independent close review、task gate 和自身 atomic evidence；
9. G4 PASS 后，四个产品 task 分别执行 status-only finalization 和独立 status review。

G4 不替产品 task 自批。产品最终 PASS 必须同时引用：原产品 implementation review、
G4 对应 rc0 log、G4 PASS、status-only diff 和独立 status-review verdict。

## 9. Error and safety semantics

- 所有 checkpoint contract failure 返回非零并给出被拒绝的关系/path；不调用 helper；
- helper 被调用后，其 return code 原样返回；
- temporary clone 创建/复制/delegation 任一步失败均清理 clone；
- checkpoint authority 不改变 endpoint 或 HTTP status；
- 本设计没有 SQLite command；G4 期间仍禁止并发 SQLite writer；
- transport reconnect 先核对 checkpoint hash、live status 和已完成 command log，不重复
  已成功 validator。

## 10. Dependency and capability boundary

顺序：

1. 本 Ultra design task 独立批准；
2. Ultra 计划和 task materialization 冻结 G3、四个 overlay、G4；
3. High 实现 G3（stdlib TDD、独立 High review、task gates）；
4. Ultra 执行/审计 G4 的 path-specific authority；
5. High 执行四个 mechanical status-only close；
6. 恢复 Foundation dependency scheduler。

High 不得自行接受 unresolved reconciliation exception、改变 checkpoint trust boundary
或切换到 commit/prefix/owner inference。发现该类问题时只暂停 G4 lane 并请求 Ultra。

## 11. Acceptance criteria

- G3/G4 是两个独立原子 closure；
- 现有 no-peer/peer behavior 和外部 helper 保持不变；
- checkpoint exact-state、review binding、path authority、drift 和 clone isolation 均有
  public regression；
- G4 inventory unknown/unresolved 为零，或 fail closed 为 BLOCKED；
- 四个产品 source/test byte 与已批准 review 保持一致；
- 四个 validator 都有 G4 task-local rc0 log；
- 每个产品 task 有独立 status-only review 后才成为 PASS；
- 无 commit/push/reset/clean/stash/baseline rewrite/prefix trust/peer omission；
- 后续 Foundation/Full/Final/Release gate 顺序不变。
