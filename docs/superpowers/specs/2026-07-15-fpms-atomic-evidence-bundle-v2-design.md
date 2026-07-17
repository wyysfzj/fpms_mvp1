# FPMS Atomic Evidence Bundle V2 设计（2026-07-15）

## 1. Decision and supersession

本文冻结一个 repository-local、可版本化、fail-closed 的 Evidence Bundle V2 契约，
用于修复当前 evidence producer、artifact、consumer 和 gate 之间的系统性断裂。

本文是
`docs/superpowers/specs/2026-07-15-fpms-atomic-evidence-reconciliation-checkpoint-design.md`
的 superseding delta：旧文档保留为历史；其 exact worktree checkpoint、逐路径
reconciliation、quiescent close 和 status-only finalization 思路继续有效，但以下语义
被本文替代：

- external skill helper 不再是 FPMS 的最终 acceptance authority；
- 仅固定 `diff_sha256` 不再足够；
- G3 不再把未语义验证的 subject artifacts 复制给 external helper 后即接受；
- G4 必须绑定完整的 subject evidence bundle，而不是零散 source/test/diff/review hash。

批准的实现方向是 repository-local V2。不得在本项目任务中修改
`/Users/cfcc/.codex/skills/**`；修改全局 skill 会影响其他仓库、不可由本仓库版本化，
需要独立的全局授权，不属于本 Goal。

## 2. Proven failure and impact boundary

已实测：

- skill reference 要求 `git/diff.patch` scoped to task result；
- stock `finalize` 和 `scripts/evidence_finalize.sh` 都直接执行全仓 `git diff`，不读取
  allowlist，且漏掉 untracked additions；
- 当前设计任务由 stock finalize 生成的 patch 有 91 个路径，91 个均越出 allowlist，
  两个真实 untracked task/spec 路径均缺失；
- 该 patch 仍被 stock `validate` 和 `scripts/task_validate.sh` 接受；
- wrapper regression fixture 使用任意 `fixture\n` 作为 patch，证明现有测试只要求文件
  存在，没有验证语义。

只读启发式扫描发现 360 个既有 bundle 中有 101 个 patch 至少含一个 task.json
allowlist 外路径。该结果是风险发现，不是 retroactive invalidation verdict。当前
Foundation manifest 中已有 evidence 且标为 PASS 的 43 个任务，在“patch 路径越界”
这一项未发现问题；是否接受历史任务必须由独立的 legacy register 审计决定。

## 3. Story Shape Classification

- `shared_file_density`: high — V2 core、task gate、atomic wrapper 和 AGENTS 各有串行
  owner；旧 G3 之后还要再次串行拥有 atomic wrapper/test。
- `prereq_dependency_density`: high — core → legacy register → gate integrations →
  governance activation → checkpoint V2 → G4 严格有序。
- `be_fe_coupling`: none — 不改变产品、API、UI、法律、费用、文书或谱系语义。
- `evidence_cost`: high — producer、bundle、review、consumer、legacy activation 和
  checkpoint 均为 acceptance trust boundary。
- `chosen_runbook`: `P0-prereq-heavy-story`。

## 4. Alternatives

### 4.1 Approved — repository-local V2

新增一个标准库 Python evidence-bundle core。task gate、atomic wrapper 和后续
checkpoint 都使用它的同一 verifier；review projection 也由 core 内静态函数直接生成，
不再调用外部 Git/diff renderer。优点是可版本化、可 TDD、单一语义来源、不会影响其他
仓库；代价是要增加几个严格串行的 repository-governance prerequisite。

### 4.2 Rejected — patch installed global skill

代码改动可能较少，但修改不在仓库版本内，影响所有 workspace，无法由本 Goal 的
release gate 固定，也违反当前 task 的 authority boundary。

### 4.3 Rejected — continue per-task custom scope scripts

这些脚本保护了部分 Foundation PASS，但不同任务各自实现 patch、baseline、header 和
reverse-check 逻辑，容易遗漏 binary、untracked、status-only 或后续 artifact drift，
也无法让 task gate 自动 fail closed。

### 4.4 Rejected — hash existing artifacts without semantic validation

Hash 只能证明 byte 没变化，不能证明 full-repo patch、伪造 rc0 或缺失真实路径是正确
证据。V2 必须先验证 admissibility，再 seal integrity。

## 5. Trust model

1. `artifacts/<TASK-ID>/**` 在 candidate seal 前全部视为 implementer-controlled、可变、
   未受信输入。
2. 独立接受链固定的 V2 core 是 task-local evidence correctness 的唯一语义实现；atomic wrapper 只负责
   cross-task/worktree ownership；task gate 只消费 V2 acceptance。三者不得复制同一
   patch-validity 逻辑。
3. `changes.json` 和 content objects 是 baseline-subtracted change 的语义 authority；
   `git/diff.patch` 是由同一 core 内静态、in-process 函数生成并可重算的 review
   projection，不是外部 Git renderer 或 `git apply` 的 authority。
4. Candidate seal 固定实现、步骤、日志、summary candidate、task normalized content、
   producer version 和全部 task-local delta，但不包含自己的独立 review。
5. Lead/controller 在 candidate 后为每个 axis 生成 exact review-dispatch record；独立
   reviewer 的 JSON/Markdown/log 绑定 candidate 与 dispatch SHA-256。
6. Acceptance seal 绑定 candidate、全部 dispatch/reviews、最终 task/summary status-only
   transition 和 acceptance-producer hash，消除 review/self-hash 循环。
7. PASS 必须同时满足 V2 bundle verifier、repository task gate 和 atomic ownership
   validator。任一单独的 legacy helper PASS 不产生 FPMS acceptance。
8. 缺失、malformed、unresolved、hash drift、semantic drift、review drift 或 authority
   drift 一律非零；没有自动 legacy fallback。

Core/renderer 的 expected identity 不能由当前 `init` 对“它当时看到的文件或 executable”
自行宣告。唯一可信来源是：core bootstrap 的 task-frozen toolchain + 三轴独立接受记录；
activation 前由其 accepted bootstrap/register relation 延续；activation 后由 V2-accepted
activation policy 延续。`init` 只能核对 expected path/mode/hash/schema，不能选择、覆盖或
从 ambient `PATH` 推断 expected value。只记录 observed hash 可证明 continuity，不能证明
authority，因此不得单独作为信任根。

本设计不声称本地文件 hash 能证明真实人类/agent 身份或防御拥有 filesystem root 权限的
恶意操作者。Reviewer independence 是由 collaboration orchestrator/lead 的独立 dispatch、
agent allowlist 和 reviewer-authored output 在流程层执行；机器 verifier 只能证明 declared
implementer/reviewer ID 不同、dispatch/review byte graph 一致和之后没有漂移，不能把本地
role string 变成密码学身份证明。它保证的是：在本项目协作模型内，implementer 不能通过
遗漏路径、修改 ignored artifact、添加伪 rc0 或替换已 dispatch 的 review byte 而获得
机器 gate PASS；若缺少真实独立 dispatch，流程 gate 必须拒绝，不能把 machine rc0 描述
为“已证明独立作者身份”。

环境 TCB 明确止于 collaboration orchestrator、OS kernel/filesystem 和被 core bootstrap
独立固定的 exact Python runtime；filesystem-root 或 runtime-binary compromise 不在本地
bundle 能证明的范围。正常入口必须用该 absolute Python、`-I -S` 和 sanitized environment，
拒绝 `PYTHONPATH`、user/site startup、dynamic renderer import 和 repository/plugin helper。
Core 自身及 internal repository-reader identity 必须在使用前后做 no-follow、regular-file、
single-link、path-to-inode stability 和 expected-hash 核对；ambient loader/helper/PATH
substitution 不得进入 renderer 或 repository-state authority。

## 6. Component boundaries

### 6.1 Evidence Bundle V2 core

新增：

- `scripts/atomic_evidence_bundle.py`；
- `scripts/tests/test_atomic_evidence_bundle.py`。

它是一个 stdlib CLI service，公开六个 subcommand：

```bash
<TRUSTED_PYTHON_ABS> -I -S scripts/atomic_evidence_bundle.py init <TASK-ID> \
  --task-file <REPO-RELATIVE-TASK-FILE>

<TRUSTED_PYTHON_ABS> -I -S scripts/atomic_evidence_bundle.py run <TASK-ID> <STEP>

<TRUSTED_PYTHON_ABS> -I -S scripts/atomic_evidence_bundle.py seal-candidate <TASK-ID>

<TRUSTED_PYTHON_ABS> -I -S scripts/atomic_evidence_bundle.py reopen <TASK-ID>

<TRUSTED_PYTHON_ABS> -I -S scripts/atomic_evidence_bundle.py seal-acceptance <TASK-ID>

<TRUSTED_PYTHON_ABS> -I -S scripts/atomic_evidence_bundle.py verify <TASK-ID>
```

Allowlist、required step 的 exact argv/cwd/environment policy、review axes、candidate
hash、review paths 和 legacy policy 均从
task/candidate/activation contract 读取，不在 CLI 重复输入。这样既消除两个 authority，也
减少长命令转义和 JSON 兼容错误。CLI 不提供任意 `--legacy-register`、`--review` 或
`--allowlist` override；`run` 也不接受 caller-supplied command。

Core 不读取 manifest、不决定 concurrent peer ownership、不运行 task gate、不调用
atomic wrapper，也不修改 task/source/test。这样避免递归和职责耦合。

### 6.2 Atomic ownership wrapper

`scripts/atomic_evidence_validate.py` 继续负责：

- task/task.json/allowlist identity；
- manifest and peer identity；
- pairwise exact allowlist non-overlap；
- NUL-safe live dirty ownership；
- rename/copy/symlink/locality；
- isolated current-task projection；
- 后续 G3 checkpoint 和 G4 reconciliation authority。

V2 integration 后，它不再把 external helper 的返回值作为 acceptance，而是在 ownership
验证后调用同一 V2 `verify`。现有 no-peer/peer CLI 与 ownership fail-closed 行为保持；
acceptance backend 在 governance activation 时切换到 V2。

### 6.3 Repository task gate

`scripts/task_validate.sh` 只做入口和兼容错误输出，最终调用 V2 `verify`。它不得继续以
“summary/diff 文件存在 + 任意 lint/test rc0”作为 PASS。V2 core 不反向调用 task gate，
因此调用方向唯一：

```text
release/dependency gate -> task_validate.sh -> V2 verify
atomic ownership wrapper ------------------> V2 verify
```

### 6.4 Installed helper and local legacy scripts

以下 producer 可保留用于历史读取或 bootstrap comparison，但在 activation 后不能单独
授予 PASS：

- installed `evidence_gate.py`；
- `scripts/evidence_run.sh`；
- `scripts/evidence_finalize.sh`；
- task-local custom diff builders。

任何继续使用 legacy producer 的 task，最终也必须产生并通过 V2 acceptance，或由
exact legacy-pass register/G4 bridge 明确接受。

## 7. V2 storage and canonical encoding

V2 在现有 artifact root 下使用独立 namespace，不覆盖历史文件：

```text
artifacts/<TASK-ID>/bundle/v2/
  init.json
  init.sha256
  objects/<sha256>
  steps/000001.json
  steps/000001.log
  candidates/000001/changes.json
  candidates/000001/diff.patch
  candidates/000001/candidate.json
  candidates/000001/candidate.sha256
  reviews/000001/<axis>.dispatch.json
  reviews/000001/<axis>.json
  reviews/000001/<axis>.md
  reviews/000001/<axis>.log
  reopens/000001.json
  acceptance.json
  acceptance.sha256
```

所有 JSON 都必须是 UTF-8、sorted keys、紧凑 separators、`ensure_ascii=False`、
`allow_nan=False`、末尾单一 LF。SHA-256 按实际 bytes 计算并写为 64 位 lowercase hex
加 LF。JSON path 必须 repository-relative POSIX；禁止 absolute path、反斜杠、`.`、`..`、
NUL、ASCII control character、glob、directory authority 和 symlink traversal；普通空格
和合法 UTF-8 名称必须支持。

Content object 以 SHA-256 命名，只存 regular-file exact bytes；相同 bytes 去重。Missing
path 使用 tombstone，不创建 empty object。Object hash、文件 mode 和 manifest entry 必须
互相一致，object directory 必须恰好等于 init、all candidate changes 和 candidate artifact
snapshots 所引用的 object set，surplus object 也拒绝。

## 8. Init contract

### 8.1 Task contract

`init` 必须在 source/test edit 前运行，并验证：

- task ID 与 task-file stem 一致；
- task file 恰有一个 closure、non-closure、remaining follow-up、allowed-files、risk tier、
  runbook、`Required Evidence Commands` 和 `Required Review Axes`；
- `Required Evidence Commands` 是一个 canonical JSON block；每个 step 恰有一个 exact
  step ID、argv array、repository-relative cwd、fixed safe env map 和 hashed-inherited env
  name list；字符串 command、shell interpolation、重复 step 和 unknown key 拒绝；
- init 只从 task file 读取 allowlist/commands/axes，不接受重复 CLI value；
- 只有 own `artifacts/<TASK-ID>/**` 可使用 glob；其他 entries 必须是 exact file path；
- review axes 不重复且至少一个。HIGH evidence-governance design 可以要求多个正交轴。

V2 universal candidate steps 固定为 `lint`、`test`、`scope`；task 可在 exact block
追加 command 但不能删除或重复这三个。Independent review 不作为 implementer `run` step，
而由 review JSON 表达。Markdown parser 对 required heading/status/header 的零次或多次
出现一律拒绝，不能“取第一个看起来像的值”。

Init 将每个 argv[0] 解析为 absolute regular executable，固定 path/mode/SHA-256/version；
run 直接使用该 absolute path。子进程环境从固定最小 base 构造，不继承任意 ambient
environment：task-declared safe env 保存 exact value；确需继承且可能敏感的 value 只保存
name + SHA-256，运行时 hash 不同即拒绝且日志不输出明文。Cwd、argv、environment policy、
resolved executable 和 command-contract hash 全部进入 init/candidate。由此
`run <TASK> test -- true` 不存在合法 CLI，step-label substitution 必须 fail closed。

### 8.2 Exact initial state

`init.json` 至少固定：

- schema `fpms.atomic-evidence-bundle-init/v2`；
- task ID/path、risk tier、runbook、closure/non-closure hashes、exact allowlist；
- repository HEAD；
- V2 producer path/version/SHA-256、exact Python runtime identity 和
  `trusted_toolchain_anchor` relation；
- internal repository-reader Git 的 expected absolute path、regular mode、SHA-256、exact
  version output 和 sanitized argv/environment identity；这些 expected values 来自
  trusted toolchain anchor，不能由 init 选择或从 ambient `PATH` 推断；
- in-process review projection 的 schema/function ID、producer-source SHA-256 和 trust
  anchor；不存在 patch-renderer executable identity；
- 每个 non-evidence allowlist path 的 initial state：regular file 的 mode/hash/object，或
  missing tombstone；
- `git status --porcelain=v1 -z --untracked-files=all` 的 complete concrete dirty set；
- 每个 dirty entry 的 XY、kind、mode、worktree hash、index/HEAD OID 或 deletion tombstone；
- init ordinal `0` 和 canonical init hash。

未跟踪目录必须展开成 concrete descendants；不能保存 `scripts/tests/` 之类的 collapsed
authority。Rename/copy、symlink、目录 allowlist、无法读取的 mode/hash 或 malformed NUL
record 使 init 失败。

完整 dirty inventory 是 audit/ownership input，不表示 V2 bundle core 接受 external path；
cross-task owner 仍由 atomic wrapper 判断。

## 9. Run contract

每次 `run` 使用单调、零填充 ordinal；不得使用“秒级时间戳 + step name”作为唯一 log
identity。每个 step JSON 固定：

- schema `fpms.atomic-evidence-step/v2`；
- task ID、ordinal、step、task-frozen argv array、repository-relative cwd、sanitized-env
  policy/hash、resolved executable path/hash；
- previous-step SHA-256，形成 append-only hash chain；
- start/end timestamp 仅用于审计，不作为 authority ordering；
- exact rc、combined-output log path/hash/byte count；
- command runner path/hash；
- 执行前后 non-evidence allowlist state hash。

Ordinal 以 task-local exclusive lock 和 atomic temporary-file rename 保留；命令开始前写
pending record，正常结束才形成 hash-chain step。Crash 留下的 pending 不得当成功；下一次
运行只有在证明原 runner 已不存在后，才可把它封存为 immutable interrupted record，再
分配新 ordinal，不能删除或覆盖。若同一 step 最新记录 rc0、argv 完全相同且当前 allowlist
state 等于该记录 post-state，`run` 返回 sealed no-op，避免 reconnect 重跑；state 或 argv
不同则必须产生新 ordinal。

失败 step 永不删除。对每个 required step，candidate seal 要求其最后一条记录 rc 为 0、
command identity 与 init 完全相等；
早期成功后又出现失败时，旧成功不能继续满足 gate。Transport reconnect 读取最高完整
ordinal、验证 hash chain 后从第一个未完成 step 继续，不重复已经完成的 rc0 step。

Legacy `commands.jsonl`、`results.jsonl` 和 outputs 可继续作为兼容 mirror，但 V2 verifier
不以可编辑 JSONL 中一条孤立 rc0 作为 authority。

## 10. Candidate and semantic change contract

### 10.1 Candidate-local `changes.json` and `diff.patch`

Candidate seal 重新读取所有 non-evidence allowlist path，与 init objects 比较，并生成
sorted exact changes：

```json
{
  "schema": "fpms.atomic-evidence-changes/v2",
  "entries": [
    {
      "path": "exact/repository/file",
      "before": {"kind": "regular", "mode": "100644", "sha256": "..."},
      "after": {"kind": "regular", "mode": "100644", "sha256": "..."}
    }
  ]
}
```

`before` 或 `after` 可为 exact missing tombstone。Every changed path 必须在 exact
non-evidence allowlist；every current delta 必须出现；unchanged path 不得出现；own artifacts
不得出现在 changes。

Core 从 objects/changes 生成 deterministic、binary-capable candidate-local `diff.patch`。
唯一 renderer 是 `scripts/atomic_evidence_bundle.py` 内的静态 in-process function；固定
function/schema ID 为 `fpms.single-hunk-review-projection/v2`。它不得执行 subprocess、shell、
Git、`diff`、textconv、attributes、dynamic import、repository/plugin helper 或 caller callback。
Renderer source 与 producer 是同一 exact regular single-link file；expected source hash 必须
来自 `trusted_toolchain_anchor`，init/candidate/verify 都执行 no-follow stable-identity double
read，不能把 init 自己观察到的 hash 升格为 authority。

Projection byte grammar 固定如下：entry 按 path UTF-8 bytes 排序；每项写 fixed schema header、
canonical-JSON quoted path，以及 before/after 的 kind、mode、byte-count、SHA-256 和 content-
object reference。Strict UTF-8 且不含 NUL/ESC/除 TAB、LF、CR 外 C0 control 的内容按 exact
bytes 分行、不做 newline/Unicode normalization；renderer 取不重叠的 maximal common line
prefix/suffix，产生一个 deterministic hunk，包含全部 changed middle、前后最多三行 context
和 exact no-final-LF marker。Mode-only change 不伪造 content hunk。其余内容按 binary entry
输出 exact before/after object metadata，原始 bytes 只在 content objects 中。Structural
lines 固定 LF，路径/control data 只使用 canonical escaping。该文件是可读 review
projection，不承诺可被 `git apply`；semantic reconstruction 始终来自 changes + objects。

Candidate 固定 projection schema/source/trust-anchor identity；Verifier 从已验证 objects 和
changes 使用同一受信 source 重算 exact bytes，并要求：

- patch hash 和重算 bytes 相等；
- patch path set 与 changes path set 完全相等；
- full-repo/outside/duplicate/missing/surplus path 拒绝；
- placeholder、empty patch with non-empty changes、text/binary type confusion 拒绝；
- path with spaces 可正确处理；rename/copy 和 symlink 仍拒绝。

`changes.json` 是语义 authority；patch 不是靠 header-count 推断 authority。V2 canonical
scoped diff 永远是 accepted generation 内的 immutable `diff.patch`。AGENTS activation
必须把“scoped git/diff.patch”对 V2 明确为该 candidate-local path；legacy task 的 root
`artifacts/<TASK-ID>/git/diff.patch` 规则不变。

Init 另固定 `legacy_root_diff` profile：

- `missing-create-compat-mirror`：只供 activation 前的新治理任务显式选择；final acceptance
  可新增一个与 final candidate diff byte-for-byte 相同的 root compatibility mirror；
- `present-preserve-legacy`：root file 的 exact initial bytes/hash 作为 legacy context 永久
  保留，V2 不覆盖、移动、删除或把它称为 semantic authority；
- activation 后新任务默认 `no-root-mirror`，只使用 candidate-local diff。

Profile 与 initial state 不一致立即失败；任何 existing root diff 都只能选择 preserve。
Rejected generation 不创建/覆盖 root mirror，consumer 始终验证 candidate-local bytes。

### 10.2 Candidate schema

每次 `seal-candidate` 分配单调 generation；不得覆盖已有 generation。每个
`candidates/<GEN>/candidate.json` 至少固定：

- schema `fpms.atomic-evidence-candidate/v2`；
- init path/hash、changes path/hash、patch path/hash；
- producer path/version/hash；
- projection schema/function ID、producer source path/mode/hash 和
  `trusted_toolchain_anchor` identity；
- required steps 和全部 step record/log hash；
- one `verification_state_sha256`，并要求每个 required step 的 latest successful
  `post_state_sha256` 与它完全相等；
- task exact hash、status-normalized task hash、expected pre-review status；
- summary exact hash、status-normalized summary hash、expected candidate status；
- final state of every non-evidence allowlist path；
- task.json、baseline_allowlist、baseline_external、legacy commands/results 的存在状态与
  hash（存在即固定，缺失必须符合 V2/legacy profile）；
- explicitly referenced implementation/self-review evidence hashes；
- review axes required for acceptance。

Candidate 还必须内嵌本 generation seal 前 task artifact root 的 complete exact file inventory：
relative path、regular-file mode、byte count、SHA-256 和 content-object reference。Inventory
排除 `bundle/v2/objects/**`（由 object graph 单独 exact 验证）及本 generation candidate
自身 well-known outputs，但不能遗漏 legacy summary/results/commands/logs、task-local
validators、baseline、steps、prior candidates/reviews/reopens 或“未被引用”的文件。这样
旧 summary/JSONL/log byte 即使在合法 reopen 后变化仍可由 object 重放。Candidate 同时声明
review 后唯一允许新增
的 exact paths：本 generation 下每个 axis 固定一个 review dispatch、一个 review JSON、
一个 Markdown verdict、
一个 bounded combined verification log，以及一个 optional exact reopen record；最终
generation 仅在 init profile 为 `missing-create-compat-mirror` 时允许新增 root
`git/diff.patch` mirror，并允许 `acceptance.json`/`acceptance.sha256`。
不接受 review 目录 prefix、动态文件名或额外 attachment。

Candidate seal 前 summary 必须完整说明 closure、non-closure、modified files、commands、
result、dirty baseline 和 residual dependencies，状态为 `PASS-CANDIDATE` 或 task contract
指定的等价 exact value，不能声称 final PASS。

Seal 时重新计算 non-evidence allowlist state 作为 `verification_state_sha256`。若任何
required step 之后 source/test/task byte、mode、addition 或 deletion 改变，至少一个 latest
post-state 会不同，candidate 必须拒绝并要求对同一最终 state 重跑全部 required commands；
不能只重跑最后一个 scope step。

Candidate seal 成功后禁止再执行 `run`、重写既有 artifact 或生成新 implementer output。
若至少一个合法独立 review 对该 generation 给出 `CHANGES_REQUIRED`，且不存在 acceptance，
`reopen` 可生成一次 immutable reopen record，绑定 candidate/review/current artifact-tree
hash，并允许 task/summary 回到 exact in-progress status；之后才能继续 `run` 并 seal 下一
generation。没有 rejected review、覆盖旧 candidate、删除旧 finding 或 second reopen 全部
失败。Acceptance verifier 必须验证所有历史 generation/review/reopen chain，并证明最终
artifact tree 等于 final candidate inventory 加上述 exact future outputs；任何其他新增、
删除或漂移都失败。

## 11. Independent review and acceptance without circular trust

每个 required review axis 在 candidate generation 下写一个 canonical JSON：

```json
{
  "schema": "fpms.atomic-evidence-review/v2",
  "candidate_generation": 1,
  "axis": "producer|consumer-gate|adversarial-checkpoint|task-domain",
  "candidate_sha256": "<sha256>",
  "dispatch_path": "artifacts/.../bundle/v2/reviews/000001/<axis>.dispatch.json",
  "dispatch_sha256": "<sha256>",
  "verdict": "APPROVED",
  "reviewer_role": "independent ... reviewer",
  "implementer_role": "...",
  "p0": 0,
  "p1": 0,
  "p2": 0,
  "markdown_path": "artifacts/.../bundle/v2/reviews/000001/<axis>.md",
  "markdown_sha256": "<sha256>",
  "verification_log_path": "artifacts/.../bundle/v2/reviews/000001/<axis>.log",
  "verification_log_sha256": "<sha256>"
}
```

Reviewer 不能是 candidate implementer；缺失 identity separation、wrong candidate hash、
非 APPROVED、finding 非零或 markdown drift 全部拒绝。

Dispatch schema 固定 candidate generation/hash、axis、implementer ID、controller ID、
reviewer ID 和三个 exact reviewer-output paths；必须由非 implementer controller 在 candidate
seal 后、review output 前写入。Review JSON 必须逐字段回指 dispatch。Verifier 检查
declared ID separation 和 bytes/ordering；orchestrator/lead 负责证明实际 writer 对应 declared
reviewer，缺少该外部事实时不得声称 independent acceptance。

`CHANGES_REQUIRED` review 可以有 findings，但其 JSON/Markdown/log 仍必须 canonical、绑定
candidate 并进入 immutable history；它只授权 `reopen`，不能授权 acceptance。最终被
accept 的 generation 必须所有 required axes 均 `APPROVED` 且 P0/P1/P2 全为零。

Review 后只允许 task/summary 的 exact administrative status transition。Acceptance seal
要求 task 与 summary 各恰有一个 contract-defined `Status:` line；normalizer 只替换该行，
其他 byte 完全不变，且 status-normalized hash 与 candidate 相同。Acceptance 生成：

- schema `fpms.atomic-evidence-acceptance/v2`；
- final candidate generation/hash 和完整 prior generation/reopen chain hash；
- 每个 required axis dispatch/review JSON/Markdown/verification-log hash；
- final exact task/summary hash and allowed status transition；
- acceptance producer hash；
- legacy register or exact G4 bridge identity（如适用）；
- acceptance timestamp（audit only）。

Acceptance 不把自己的 hash 写入自身；`acceptance.sha256` 单独保存。Verifier 重算所有
关系，因此不存在“review 必须先绑定 acceptance，而 acceptance 又必须包含 review”的
循环。

`seal-acceptance` 使用 task-local exclusive lock：在 lock 内读取并验证 dispatch、review
JSON/Markdown/log、candidate、task、summary 和 complete artifact tree；构造 temporary
acceptance；再次读取并比对全部 input hash；fsync 后 atomic rename；再做一次 post-rename
re-read 才释放 lock。任何 in-flight substitution 都不产生 final acceptance。之后每次
task gate/atomic wrapper 仍重算所有 review bytes，acceptance 后替换也立即失效。该协议
关闭 filesystem TOCTOU，但不扩大前述 reviewer identity threat model。

## 12. V2 verification algorithm

`verify` 必须按以下顺序 fail closed：

1. repository/task/artifact locality and regular-file checks；
2. canonical JSON/hash/object graph；
3. V2 producer、acceptance-producer、exact Python runtime、internal repository reader 和
   in-process projection source/schema 的 independently anchored path/mode/hash/version；
4. init task contract、allowlist、risk/runbook/axes；
5. complete initial state and exact dirty inventory encoding；
6. step ordinal/hash chain、task-frozen command/env/executable、log hash、最后
   required-step rc0；
7. every latest required-step post-state equals candidate final verification-state；
8. changes semantic completeness and exact current non-evidence state；
9. deterministic candidate-local patch recomputation and legacy-root profile；
10. complete candidate artifact inventory and exact post-candidate output set；
11. all candidate generation/rejected-review/reopen history；
12. final candidate task/summary/status-normalized binding；
13. every required dispatch/review axis/bounded review log and declared identity separation；
14. acceptance status-only transition, double-read stability and final hashes；
15. if V2 is absent, activation-policy-anchored exact legacy-register or exact-four G4 bridge
    identity。

任何失败必须指出被拒绝的 relation/path/axis，且不得输出 `PASS`。Verifier 不运行产品
测试、不修改 evidence、不自动 seal、不自动使用 legacy helper。

## 13. Legacy activation and migration

### 13.1 Already-PASS tasks

切换 task gate 前建立 tracked：

`scripts/evidence_v2_legacy_pass_register.json`。

该 register 由独立 HIGH task 生成并审查，只能包含 activation 时已经 accepted、且属于
当前批准 V8 manifest/dependency closure 或 Evidence V2 bootstrap/dependency closure 的
exact task；不得为了“全仓看起来完整”审计全部 360 个历史 bundle。未登记的历史任务在
以后真正成为 dependency 时 fail closed 并进入独立 audit/remediation lane。每条固定
task ID/path/status/task hash、task.json、summary、diff、results、accepted review 和关键
log hashes，以及 legacy acceptance reason。任何 patch semantic unresolved 的任务不得
进入 register，必须进入 remediation lane。

Register 不接受 prefix、pattern、status inference 或“当前目录全部 PASS”。文件自身由
后续 activation policy 的 V2 acceptance 固定 path/hash。Activation 后不得追加旧任务。

### 13.2 READY / NOT STARTED tasks with legacy artifacts

不得把已有 stock-finalize patch 当 baseline，也不得删除或重写历史 artifacts。首次
执行时在 `bundle/v2/**` 新建 exact init；旧 artifacts 只作为 hashed legacy context。
当前发现的两个 not-started Foundation contaminated patches 属于此类。

### 13.3 Four blocked PASS-candidates

以下任务不能伪造新的 V2 init：

- `FPMS-V8-FO-PREVIEW-FE-ADAPTER-20260712-01`；
- `FPMS-V8-ANNUITY-PAYABLE-AMOUNT-RULE-20260712-01`；
- `FPMS-V8-DE-ATTACHMENT-EVIDENCE-ATOMIC-ADAPTER-20260712-01`；
- `FPMS-V8-LC-FILING-PREPARATION-STARTED-20260712-01`。

它们继续使用一次性 G4 legacy reconciliation bridge。G4 必须生成每任务完整 legacy
candidate：source/test/task normalized state、semantic changes/patch validation、task.json、
baseline、summary、results、commands、every referenced log、product review、producer/helper
version和 exact worktree checkpoint。逐路径 exception 仍按旧设计独立批准。

G4 bridge 是 task gate 的第三种、仅限这四个 ID 的 acceptance profile，不是假造 V2 init，
也不能塞入 legacy PASS register。Activation policy 必须预先固定：G4 task ID/path、四个
subject task ID/path、固定 status-close 顺序和 bridge schema/version。G4 自身使用普通 V2
acceptance；其 dependency contract 明确消费四个 frozen `PASS-CANDIDATE` 作为待审输入，
不得先调用或要求这四个 subject 的 normal task gate PASS，因此没有 bootstrap cycle。

G4 accepted candidate 为每个 subject 生成 immutable `bridge_candidate`，固定 pre-status
task/summary normalized bytes、完整 subject bundle、checkpoint/head、G3 rc0、exact allowed
status transition、exact allowed post-G4 artifact paths、required independent status-review
axis 和 predecessor subject acceptance（第一项指向 G4 acceptance）。G4 只能预授权关系，
不能替 subject 写最终 status、review 或 acceptance。

G4 V2 acceptance 后，四个 subject 按 policy 固定顺序串行恢复原 task；每个 agent 仍只拥有
自己的一个 task file，且只允许：contract-defined `Status:` transition、summary status-only
transition、candidate-local status diff、独立 status-review dispatch/JSON/Markdown/log 和
`legacy_bridge_acceptance.json`。该 bridge acceptance 绑定 G4 V2 acceptance、自己的
bridge candidate、previous subject acceptance、final task/summary/diff/review bytes；normal
verifier 逐关系重算。缺少前序、G4 尚未 V2 accepted、实现者自批、非 status-only drift 或
任一 live checkpoint drift全部拒绝。最后一个 subject acceptance 是四任务 bridge 的唯一
highest head；Foundation scheduler 只消费四个 normal gate 均 PASS 的结果。

### 13.4 Design-task bootstrap authority

V2 不能用尚未实现的 V2 来证明自己的 design/core 起点；这个 root-of-trust 必须显式、
最小、一次性并由独立 reviewer 承担，而不能隐藏在 stock helper 的 PASS 中。

本 design task 的 legacy init 把两个未跟踪目录折叠为：

- `frontend/src/api/contracts/`；
- `scripts/tests/`。

一次性 ledger
`artifacts/REPO-ATOMIC-EVIDENCE-BUNDLE-V2-DESIGN-20260715-01/analysis/bootstrap_reconciliation.json`
将它们展开为当时及当前完全相同的三个 concrete regular files。每个文件必须同时满足：

- current mode/hash 与 ledger 一致；
- mtime 早于 design init（只作附加审计，不单独构成 authority）；
- prior task.json 的 exact allowlist/identity/init 均匹配；
- 前端合同由先前 scoped new-file patch 的 exact post-image 证明，两个验证测试由先前
  independent review 中的 exact path/hash 证明；
- provenance artifact 自身 hash 与 ledger 固定值一致。

Task-local validator 还必须从保存的 task-before bytes 与 init 后创建的新 spec 生成唯一
canonical scoped patch；patch headers 和 post-image 只能是本 task 与本 spec。三个 Ultra
review axis 必须绑定同一个 final spec hash、ledger hash、scoped-patch hash 和 validator
结果。任何 descendant、provenance、hash 或 patch 漂移都使本 design task BLOCKED。

这是 design-review bootstrap only：it **does not grant V2 acceptance**、legacy PASS、产品
PASS、路径 owner 或可复用 reconciliation authority；stock task gate/atomic helper 的 rc0
仅是当前治理兼容信号，不是 scoped-diff 语义证明。明确 `no prefix`：ledger 中的目录名
只是指出旧记录的缺陷，绝不能被解释为目录前缀权限，任务结束即失效。

后续 written-plan 仍是非运行时文档任务，必须用同等 exact doc-only scope 证明。第一个
V2 core implementation task 是唯一的 implementation bootstrap root，必须严格串行且在
任何 source/test edit 前：保存 `git status --porcelain=v1 -z --untracked-files=all` 原始
bytes；展开全部 concrete dirty paths；固定 mode/hash/OID/tombstone；固定其 exact
allowlist 初态；并证明新的 core/test path 为 missing。该 capture 及其 validator 命令由
批准后的 plan/task contract 冻结，独立三轴 review 后才可把 core task 作为 exact legacy
bootstrap candidate 收入一次性 legacy register。Core bootstrap contract/review 还必须
固定 exact Python runtime、internal repository-reader Git 和 final core-source path/mode/hash，
并把 `fpms.single-hunk-review-projection/v2` 的 golden-vector bytes 纳入独立审查；该记录是
后续 `trusted_toolchain_anchor` 的起点，不得由 core init 自签。Core 不得伪造 retroactive V2 init，
也不得让其他 lane 与这个 bootstrap 并发。Core PASS 后，所有后续实现任务必须直接使用
V2；不得再创建第二个 implementation bootstrap exception。

## 14. Task-gate and atomic-wrapper activation

顺序固定：

1. serialized one-time core bootstrap independently approved，随后 V2 core PASS；
2. legacy PASS register PASS，并 exact 登记 core bootstrap candidate；
3. task gate integration PASS；
4. atomic wrapper V2 integration PASS；
5. checkpoint V2 implementation PASS，形成最终 wrapper bytes；
6. AGENTS + activation-policy governance closure PASS，pins final wrapper and prohibits
   legacy-only PASS；
7. G4 bridge and four status-only closures；
8. resume Foundation scheduler。

Task gate 接受且只接受：

- valid V2 acceptance；或
- exact task entry in the pinned legacy PASS register；或
- 对 activation policy 预先列出的四个 subject，valid G4 V2 acceptance + exact
  bridge-candidate + fixed-order independent status review + subject
  `legacy_bridge_acceptance`。

第三条不是 generic fallback：target ID 不在四项 exact list、G4 未独立 V2 accepted、G4
把 subject PASS 当 prerequisite、predecessor chain 不连续或 bridge byte/status/checkpoint
不匹配时立即非零。G4 implementer、subject closer 和 subject status reviewer 三个角色必须
分离；机器检查 declared dispatch/ID/byte graph，lead 按 §11 负责真实 writer independence。

Atomic wrapper 先验证 live ownership，再使用同一 acceptance rule。Release/foundation/full
close 继续调用 task gate，因此不会出现“dependency gate PASS，但 atomic validator FAIL”
的两套证据语义。

Legacy fallback 的 machine root 是
`scripts/evidence_v2_activation_policy.json`，不是 AGENTS prose、CLI path 或“当前文件”。
该 policy 由 `REPO-AGENTS-EVIDENCE-BUNDLE-V2-ACTIVATION-20260715-01` 与 AGENTS 同一
governance closure 创建，至少固定 activation task ID、register path/hash、V2 core
path/hash、exact Python/runtime and repository-reader toolchain identity、projection
schema、task-gate path/hash、atomic-wrapper path/hash、G4 task ID/path、四个 exact
subject ID/path 和 fixed bridge order/schema。正常 `verify` 发现目标没有 V2
acceptance 时，必须先用 internal V2-only mode 验证 activation task 自己的 V2 acceptance，
再证明 policy 是该 accepted changes 的 exact after-object，最后才可读取其中固定的
register 或 exact G4 bridge declaration。Internal V2-only mode 不允许 legacy recursion，
也不暴露为可绕过 policy 的用户 CLI flag。验证 G4 subject 时，internal mode 只验证 G4
task 自己的 V2 acceptance；不得递归调用 subject gate。

## 15. G3/G4 amended contract

旧 G3 设计保留以下内容：explicit opt-in、complete exact dirty set、HEAD/status/mode/hash/
OID/tombstone、path-specific authority、no prefix、no fallback、review binding、quiescent
window、newest-baseline-first 和 status-only finalization。

本文替代以下内容：

- G3 不调用 external helper 作为 acceptance；
- checkpoint subject anchor 必须是 V2 acceptance hash，或 G4 independently approved
  legacy-candidate hash；
- subject bundle 必须包含 results/commands/logs/summary/task/baseline/diff/review/tool
  versions，不只 source/test/diff/review；
- checkpoint reviewer 必须同时验证 semantic admissibility 与 byte integrity；
- G4 ignored artifact root 只允许新增 declared output ordinal；任何已 sealed
  checkpoint/review/candidate/log 漂移都失败；
- reconnect 根据 checkpoint hash、bundle ordinal 和 completed task-specific result
  恢复，不能仅凭可编辑 rc0 record 跳过命令。

G3/G4 所有 writable output 必须对每个 ancestor/leaf 使用 `lstat` no-follow validation，
resolved path 保持在 exact artifact root；leaf 创建使用 exclusive lock、`O_NOFOLLOW`、
`O_CREAT|O_EXCL`、same-directory temporary file、fsync 和 atomic rename。Existing symlink、
任一 symlink ancestor、non-regular leaf、`st_nlink != 1` regular file、hard-link alias 或
identity 在 pre/post check 间变化都失败；exact pathname 不是绕过 inode/target 检查的权限。

Checkpoint/runtime output 使用 append-only `heads/<ORDINAL>.json` chain。每个 head 固定
predecessor hash、checkpoint hash、ordinal、declared output hash 和 successor task/step；
在同一 lock 下以 compare-and-swap 要求 expected predecessor 正是当前 highest contiguous
head，再用 exclusive create 写唯一 successor。Verifier 枚举 exact numeric filenames，
拒绝 gap、fork、duplicate predecessor/successor、non-highest HEAD pointer 和 rollback；
reconnect 必须从重算出的唯一 highest head 恢复，不能由 caller 选择较旧但有效的 head。

G4 的四条 subject validation command 使用 explicit `legacy-pass-candidate-input` mode：
只验证 frozen bundle/checkpoint/原 implementation review，不调用 subject normal task gate。
G4 自己完成 V2 review/acceptance 后，其 head 不再变化。随后四个 subject status close 使用
activation policy 的 fixed order 建立跨 task bridge chain：ordinal 1 指向 G4 acceptance，
ordinal N 指向 ordinal N-1 subject acceptance；每个 ordinal 只存在于该 subject 自己的
exact artifact path，避免共享文件并发 ownership。Verifier 枚举 fixed four paths，拒绝
gap/fork/rollback；未轮到的 subject 不得提前 close。

G3 task ID 调整为：
`REPO-ATOMIC-EVIDENCE-RECONCILIATION-CHECKPOINT-V2-20260715-01`。旧未实施 G3 ID
保留历史，不执行。G4 task ID 可保持：
`REPO-V8-FOUR-TASK-WORKTREE-RECONCILIATION-AUTHORITY-20260715-01`，但必须依赖 V2
core/integrations/activation 和新 G3。

## 16. Required adversarial RED/GREEN coverage

### 16.1 Producer axis

- collapsed untracked directory expands to exact descendants；
- tracked dirty baseline、untracked addition、deletion、mode change、binary和带空格路径
  生成 exact objects/changes/patch；
- directory/symlink/rename/copy/malformed NUL record fails；
- repeated same-step within one second creates distinct ordinals/logs；
- crash/incomplete step never becomes a complete hash-chain member；
- changed file outside allowlist never enters task changes；
- `test` label substituted with `true`、argv/cwd/env/executable drift fails before execution；
- any source/task mutation after one required step forces all required steps to rerun on one
  identical final verification-state；
- existing legacy root diff is preserved byte-for-byte while candidate-local V2 diff remains
  semantic authority；
- pre-init ambient `PATH` Git/diff stub、`PYTHONPATH`/sitecustomize、dynamic renderer/helper
  injection 不得影响 projection；trusted Python/repository-reader/core source 的 path、
  inode、mode、byte/version drift 必须在 production/recomputation 前失败；
- fixed golden vectors 覆盖 text add/delete/edit、mode-only、binary、space/UTF-8 path、
  no-final-LF，且 projection 不执行任何 external renderer。

### 16.2 Consumer/gate axis

- `fixture\n` placeholder patch fails；
- full-repo patch fails with exact outside paths；
- patch omitting an untracked allowed change fails；
- missing/surplus/duplicate path, object/hash/mode drift and binary mismatch fail；
- forged results rc0, missing/tampered log, command drift and later failure after earlier
  success fail；
- wrong task/summary status transition and review/candidate hash drift fail；
- missing/forged dispatch、reviewer=implementer、review byte substitution during/after
  acceptance seal fail；
- task gate no longer passes on only lint/test/file existence；
- task gate and atomic wrapper return the same acceptance verdict；
- G4 normal V2 acceptance succeeds without subject normal PASS, while each exact subject stays
  blocked until its ordered bridge acceptance/status review is complete；any fifth subject or
  out-of-order/self-approved bridge fails。

### 16.3 Adversarial/checkpoint axis

- ignored artifact mutation after candidate/checkpoint seal fails；
- undeclared artifact、dynamic review attachment、review 后未 reopen 的 implementer log、
  same-generation overwrite 和无合法 reopen 的 next seal fail；
- rejected review 被删除/覆盖、无 rejected review 的 reopen、second reopen、旧 candidate
  漂移和 acceptance 非 final generation fail；
- results/summary/commands/log/helper/producer drift fails；
- review/self-hash circular construction is impossible；
- unregistered legacy task, register hash drift and post-activation register addition fail；
- forged/replaced activation policy、invalid activation V2 acceptance 和 legacy recursion
  fail；
- symlink ancestor/leaf、hard-link alias、multi-link writable output and target-swap race fail；
- checkpoint head gap/fork/duplicate successor/rollback/stale reconnect fail；
- prefix/blanket/mtime/latest-owner inference fails；
- G4 unresolved exception or incomplete subject bundle fails；
- reconnect never repeats a completed sealed command and never trusts an unsealed rc0。

所有 regressions 使用 temporary repositories，stdlib first；不得运行产品 pytest、SQLite、
frontend build、Playwright 或 release gate。

## 17. Atomic implementation decomposition

每个 follow-up agent 只拥有一个 task file：

1. `REPO-ATOMIC-EVIDENCE-BUNDLE-V2-CORE-20260715-01` — 在 13.4 的唯一 serialized
   implementation bootstrap 下新增 core CLI/service 与一个 regression module；不接线
   现有 gate，不伪造 retroactive V2 init。
2. `REPO-EVIDENCE-BUNDLE-V2-LEGACY-PASS-REGISTER-20260715-01` — 生成和独立审计一个
   exact tracked legacy register；不改 gate。
3. `REPO-TASK-GATE-EVIDENCE-BUNDLE-V2-INTEGRATION-20260715-01` — 只把 repository
   task gate 接到 V2 verifier，并更新其一个 regression module。
4. `REPO-ATOMIC-VALIDATOR-EVIDENCE-BUNDLE-V2-INTEGRATION-20260715-01` — 只把现有
   ownership wrapper 的 acceptance backend 接到 V2，并保留 ownership CLI。
5. `REPO-ATOMIC-EVIDENCE-RECONCILIATION-CHECKPOINT-V2-20260715-01` — 只实现 amended
   checkpoint mode；串行再次拥有 wrapper/test。
6. `REPO-AGENTS-EVIDENCE-BUNDLE-V2-ACTIVATION-20260715-01` — 一个 governance
   activation closure：在 checkpoint 后更新 authoritative AGENTS invocation/legacy rule，
   并创建固定 final wrapper bytes 的唯一 machine-readable activation policy；独立治理复审。
7. 四个 existing subject task 的 evidence-only overlay — 每个 agent 只拥有自己的 task
   file，冻结 bridge dependency/status-only contract 后暂停，不提前声称 PASS。
8. `REPO-V8-FOUR-TASK-WORKTREE-RECONCILIATION-AUTHORITY-20260715-01` — 只生成 G4
   authority/bridge candidates/checkpoint artifacts，以普通 V2 独立接受；不得把 subject
   normal PASS 作为 prerequisite。
9. G4 PASS 后，四个 existing subject task 按 policy 顺序分别继续同一个 atomic task，
   每个只生成自己的 status-review/bridge acceptance 并完成 normal gate；不得由 G4 agent
   或一个 controller 一次替四个 task 自批。

Implementation plan 才能冻结 exact allowlist、dependency edges、review commands 和 wave；
本 design 不实现任何 follow-up。

## 18. Orthogonal spec review

本 spec 必须由三个 non-authoring Ultra reviewer 对同一 spec SHA-256 并行审查：

- `producer`：init/run/objects/changes/candidate、binary/untracked/data-loss；
- `consumer-gate`：verify/task gate/wrapper/legacy register/activation/no recursion；
- `adversarial-checkpoint`：forgery、ignored artifacts、review cycle、G3/G4、reconnect。

本轮 design bootstrap 下，三个 verdict 还必须分别写入并绑定同一个
`bootstrap_reconciliation.json` SHA-256、canonical scoped patch SHA-256、task SHA-256
和 structural/bootstrap validator log SHA-256；只写 spec hash 的 verdict 不足以批准。

每个 reviewer 只写自己的 artifact file，分别给出 P0/P1/P2 和 APPROVED/CHANGES
REQUIRED。任一 finding 修改 spec 后，三个旧 verdict 均因 spec hash 变化失效；重新并行
审查，最多三轮，之后交用户决定。Agent `running` 且连续两次无 artifact/verification
进展时立即中止并复用槽位，不能把空跑算作 review。

R3 最终结果为 producer/consumer-gate `APPROVED`、adversarial-checkpoint 因
renderer self-anchor 返回一个 `P1`。用户于 2026-07-15 明确批准一次 R4 minimal
exception。R4 只允许：移除 external patch renderer、建立上述 independently anchored
in-process renderer/toolchain relation、刷新 task-local validator/summary/closure/evidence
hash，并让同一三轴复审同一 immutable subject。R4 出现任何新 P0/P1、或需要改变其他
closure 时，必须再次交用户决定；不得自动进入 R5。

## 19. Acceptance criteria

- producer → artifact → reviewer → consumer → dependency/release gate 的每个 boundary
  都有一个明确 owner、canonical input、semantic check 和 fail-closed output；
- task delta 的 authority 来自 exact init objects + current objects + changes，不来自全仓
  `git diff` 或 header guess；
- required step 从 task-frozen argv/cwd/env/executable 执行，且全部 latest rc0 post-state
  等于 candidate final verification-state；label substitution 和 test 后修改不可 seal；
- required steps/logs/reviews/status/tool versions 全部被 candidate/acceptance 绑定；
- candidate 封存 complete artifact inventory，review/acceptance 只能增加预先声明的 exact
  outputs；不存在 ignored artifact 漂移窗口；
- task gate 与 atomic wrapper 共用一个 V2 verifier；
- V2 canonical diff 永远 candidate-local；pre-existing legacy root diff 不覆盖，activation
  前 compatibility mirror 只可在 init 明确 missing 时新增；
- review projection 只由 independently anchored V2 core 内静态函数生成；不存在 external
  patch-renderer executable，init observed identity 不能自签 authority，ambient
  PATH/loader/helper 与 path-to-inode substitution 均 fail closed；
- legacy register 由 activation task 自身的 V2 acceptance 锚定，不接受可编辑 CLI path、
  mutable policy 或递归 fallback；
- already-PASS legacy tasks只有 exact reviewed register path；not-started 和四个 blocked
  tasks 不能静默 fallback；
- old G3/G4 的完整 worktree/path-specific/quiescent 铁律保留，partial artifact anchoring
  被完整 bundle anchoring 取代；
- exact four G4 subjects 有 policy-predeclared、G4-V2-anchored、fixed-order bridge gate；
  G4 不依赖 subject 先 PASS，且每个 subject 独立 status review/acceptance；
- review dispatch 和 atomic double-read acceptance 固定 review bytes；机器只证明 declared
  separation/byte graph，实际 reviewer authorship 仍由 orchestrator/lead 执行且不得夸大；
- no global skill edit、no existing baseline rewrite、no historical artifact overwrite、
  no commit/push/reset/clean/stash、no product or release behavior change；
- design bootstrap 逐文件、一次性、不可复用且 does not grant V2 acceptance；core 是
  唯一串行 implementation bootstrap root，之后没有第二个 exception；
- 三个正交 Ultra spec review 均绑定同一最终 spec hash 并 APPROVED，之后再请求用户审批
  written spec 和进入 writing-plans。
