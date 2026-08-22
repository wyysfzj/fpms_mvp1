# FPMS Governance Reset 设计

状态：`REVISION 4 / APPROVED / FROZEN / IMPLEMENTATION AUTHORIZED`

用户冻结批准：2026-07-17

日期：2026-07-16
范围：仓库治理与任务证据工具，不含任何产品功能
目标读者：仓库维护者、任务控制器、实施代理、独立复审代理

## 1. 决策摘要

采用一次有边界的 Governance Reset：把当前混合了宪法规则、领域规则、来源目录、
历史流程、运行手册和工具细节的 `AGENTS.md`，重构为薄治理内核；把按需加载的规范
移入 `docs/agents/**`；把初始化、证据记录、SQLite 串行、复审绑定、scope、门禁和
断线诊断收敛到一个深模块 `taskctl`。

本设计不是单文件大重写，也不是逐条补丁。它通过一个小而稳定的 interface 隐藏复杂
implementation，并保留旧脚本作为兼容 Adapter。治理激活必须经过三项串行 HIGH 任务、
双轴独立复审和 shadow validation；在最终激活前不得恢复产品 Goal。

## 2. 背景与已证实问题

当前 `AGENTS.md` 为 1,024 行、约 58 KB，同时承担至少六种职责：治理优先级、领域
安全、任务执行、证据协议、来源目录和历史运行规则。它造成全量上下文加载、重复规则、
冲突措辞和运行时细节污染。

2026-07-16 的优化已经解决正常路径下的 JSON 转义、caller cwd、backend venv、SQLite
命令期锁、canonical step 和自动 close，但复审仍确认以下缺口：

1. JSON 追加没有处理 short write；
2. review 解析不要求唯一最终 Verdict，也没有强制 reviewed patch hash 等于当前 scope；
3. `owner.json` 写入失败可能遗留自有锁；
4. 初始化仍暴露重复 `--allowlist` 参数，已发生实际误用；
5. scope 在 `.git` 创建临时索引，在当前沙箱中需要额外权限；
6. task/summary 的 `PASS` 必须先于最终 gates，形成状态循环和 hash-only 复审往返；
7. liveness 规则可以及时止损，但不能消除平台 transport 或工具级空跑；
8. 完整 AGENTS 模块化、SQLite 测试模板缓存和 FIFO 调度仍未实施。

## 3. 设计目标

### 3.1 必须达到

- `AGENTS.md` 不超过 300 行，目标 200–250 行，只保存不可妥协的治理内核和路由。
- 每项规范只有一个权威定义；其他位置只能通过稳定 rule ID 引用，不得复述。
- 代理通常只需学习一个外部 interface：`taskctl`。
- 新任务不再手写 allowlist 参数序列、JSON、锁、scope、review/gate 顺序或 PASS 状态。
- 法律、生命周期/状态/期限、官费/服务应收、文档/证据谱系、认证/授权/权限、安全、
  schema/migration/seed/不可逆变更、SQLite、API 状态/响应、简体中文 UI、客户决策和
  release-last 铁律逐项保持或更严格。
- 复审必须唯一、最终、零发现，并绑定当前 baseline-subtracted patch hash。
- 任一失败不得产生假 PASS、截断 JSON、遗留自有锁或覆盖历史证据。
- 历史 PASS 任务保持接受；未 PASS 的历史任务不得因迁移被重初始化或吸收脏基线。
- transport/tool stall 仍可能发生，但必须可诊断、限次恢复且不重复耐久步骤。

### 3.2 明确不做

- 不改变任何 FPMS 产品、法律、费用、状态机、文档谱系或客户决策语义。
- 不重新分析客户来源文档，不重写 V8 计划或 283-path 任务目录。
- 不尝试防御恶意 OS、Git、Python 或特权本地操作者。
- 不承诺由仓库代码消除 ChatGPT/Codex 网络断线或模型内部空跑。
- 不在 Governance Reset 中运行产品 full test、Playwright full scope 或 release gate。
- 不自动 commit、push、reset、clean、stash 或丢弃用户修改。

## 4. 治理架构

### 4.1 权威层级

从高到低：

1. system/developer/user 的当前明确指令；
2. 根目录 `AGENTS.md` 治理内核；
3. `docs/agents/manifest.json` 激活的规范模块；
4. 已批准的设计、计划和精确任务合同；
5. 非规范示例与运行手册。

低层不得削弱高层。缺少模块、manifest 不一致、rule ID 重复、治理 digest 改变或出现
无法解释的冲突时，受影响任务 fail closed；不受影响且无共享 owner 的任务可继续。

### 4.2 薄 `AGENTS.md`

根文件只保留：

- 指令优先级、最小改动、明确假设和 evidence-before-claim；
- 法律、生命周期/期限、官费/服务应收、文档/证据谱系、认证/授权/权限、安全、
  schema/migration/seed/不可逆变更、SQLite、客户决策和 release fail-closed 总则；
- 一个 active task owner、allowlist、dirty-baseline、独立复审和共享写串行铁律；
- risk 与 runtime capability 的分离；
- contract-frozen no-repeat fast path；
- API 状态/响应约束，以及新/改 UI 简体中文且不吸收无关 legacy 清理；
- `docs/agents/manifest.json` 与 taskctl 的强制入口；
- 断线先 reconcile、最多一次 replacement、不得重复耐久步骤；
- 模块路由表和冲突处理。

根文件不再保存来源明细、Phase 3 历史规则、命令清单、证据字段细节、长篇角色映射或
平台事件定义。

### 4.3 `docs/agents/**` 规范模块

| 文件 | 唯一职责 | 典型加载条件 |
| --- | --- | --- |
| `README.md` | 模块导航、权威层级、rule ID 约定 | 仅治理维护 |
| `manifest.json` | schema、activation task、active version、模块与 selector | taskctl 每次 start/close |
| `domain-safety.md` | 生命周期/期限、法律、费用/应收、谱系、认证/权限、安全、数据、API、SQLite、迁移、UI 铁律 | 相关风险任务 |
| `execution.md` | risk、atomic ownership、依赖/冲突、wave、liveness、transport recovery | 所有实施控制器 |
| `evidence.md` | 状态机、artifact schema、review 绑定、gate/release 语义 | 所有实现与复审 |
| `source-authority.md` | 来源优先级与现有 source index | review、法律/费用/流程任务 |
| `legacy-mvp1.md` | Phase 3、旧 router、历史过渡规则 | 仅匹配旧任务路径 |

每条不可妥协规则使用稳定 ID，例如 `GOV-SCOPE-001`、`GOV-LEGAL-001`。canonical
declaration 与 reference 是两种互斥语法：

```text
### Rule GOV-SCOPE-001 — Exact task ownership
```

```text
Rule-Ref: GOV-SCOPE-001
```

`### Rule` 只能在 manifest 声明的 owner module 中出现一次，且 declaration block 内不得
出现自身 `Rule-Ref`；其他文件只能 reference。根 kernel 可定义自己的高层 rule ID，但不得
复述 module rule 的详细条件。

新任务合同的首个 metadata block 必须各且仅各出现一次机器字段
`Risk-Tier`、`Closure-Tags` 和 `Task-Path`。`Risk-Tier` 只能是无 Markdown 装饰的
`LOW|MEDIUM|HIGH`；`Closure-Tags` 是单行 RFC 8259 JSON array，其元素必须是按
Unicode code point 升序、唯一的小写 `[a-z0-9-]+`；`Task-Path` 必须与当前任务
文件的规范化 repository-relative POSIX path 字节完全相等。任一字段缺失、
重复、带 backtick/错误大小写、array 未排序或 path 不相等，`taskctl start`
均 fail closed。manifest v2 selector schema 固定为：

```json
{
  "path": "docs/agents/domain-safety.md",
  "always": false,
  "selectors": [
    {
      "risk_any": ["HIGH"],
      "task_path_any": ["tasks/postdemo/**"],
      "closure_tag_any": ["legal", "fee", "lineage"]
    }
  ]
}
```

path/task path 必须是无 `..`、反斜杠或 symlink 的 POSIX repository-relative path；glob 只
允许 `*` 与 `**`。`always=true` 时 selectors 必须为空。否则一个 selector object 内各非空
field 按 AND，field 内按 OR；多个 selector objects 按 OR。多个 module 匹配时取 path 排序
后的 union，这是正常结果；同一 Rule ID 多 owner、已声明 required closure tag 没有 module、
或 task metadata 非法才 fail closed。start 将输入、逐 field match 和最终 module list 写入
`module_selection.json`，使零/多匹配结论可复核。

### 4.4 Governance digest

`scripts/governance_validate.py` 验证：

- 根文件行数上限、Markdown fence、内部链接和 manifest；
- rule ID 唯一性及定义/引用完整性；
- 模块列表没有未声明规范文件；
- 激活版本与兼容 Adapter 版本一致。

taskctl 对根文件和 manifest 中的规范模块计算一个稳定 digest，在 start 时写入任务 metadata，
close 时重新计算。digest mismatch 时 taskctl 只生成 `governance_change.json`：old/new
digest、改变的 rule IDs/modules、task closure 影响和原 baseline identity。只有与实施者
不同的治理 reviewer 写出绑定该 change hash 的 `governance_adoption.md: APPROVED`，任务
才能 adopt；无法机器确定影响时 fail closed，且任何 adopt 都不得重捕 dirty baseline。

### 4.5 铁律保全矩阵

GVR-1 必须从激活前 `AGENTS.md` 生成逐项 ledger；每个现行权威段落记录 current location、
disposition=`PRESERVE|MOVE|SUPERSEDE|REMOVE`、唯一 owner rule、selector、理由和 observable
activation check。`SUPERSEDE/REMOVE` 必须由本设计明确批准且由 GVR-3 治理轴逐项确认，不能
用“过程优化”概括删除。GVR-3 两个 reviewer 必须确认每个 family 已覆盖。

| Family | 必须保全的语义 | 目标 owner |
| --- | --- | --- |
| `GOV-LIFECYCLE` | 法律状态、案件生命周期、期限及 OA/grant/deadline | `domain-safety.md` |
| `GOV-FEE` | 官费、费率、减缓、缴费、服务应收及来源生效 | `domain-safety.md` |
| `GOV-LINEAGE` | 文档/证据 identity、derivation、review、provenance | `domain-safety.md` |
| `GOV-AUTH` | authentication、authorization、permission、安全边界 | `domain-safety.md` |
| `GOV-DATA` | schema、migration、seed、不可逆/破坏性操作 | `domain-safety.md` |
| `GOV-SQLITE` | 类型/default/SQL 兼容及写测试串行 | `domain-safety.md` |
| `GOV-API-UI` | HTTP 状态/响应、简体中文新改 UI、surgical scope | `domain-safety.md` |
| `GOV-CUSTOMER` | 客户决策、source activation、缺失权威 | kernel + `source-authority.md` |
| `GOV-SCOPE` | exact closure/non-closure/allowlist/dirty baseline/owner | kernel + `execution.md` |
| `GOV-EVIDENCE` | 独立 review、scope、task/atomic gates、latest logs | kernel + `evidence.md` |
| `GOV-RELEASE` | Foundation/Full/Final 和 release-last | kernel + `execution.md` |
| `GOV-BEHAVIOR` | think-first、simplicity、surgical scope、verification-before-claim | kernel |
| `GOV-SKILLS` | 最小相关 skill、仓库规则优先、冻结任务不重复 design/plan | kernel + `execution.md` |
| `GOV-RISK-RUNTIME` | LOW/MEDIUM/HIGH 与 runtime capability 分离、具体 blocker 才升级 | kernel + `execution.md` |
| `GOV-RUNBOOK` | Story Shape、runbook 选择、依赖/冲突/共享 owner | `execution.md` |
| `GOV-LIVENESS` | transport reconcile、30/90、one replacement、takeover | `execution.md` |
| `GOV-LEGACY` | Phase 3/3.1/3.5、router one-time 与历史过渡 | `legacy-mvp1.md` |
| `GOV-LINT` | scoped check-only、mutating format/fix 有意且限 allowlist | `execution.md` |
| `GOV-REPORT` | evidence-backed outcome、status、paths、blockers | `execution.md` |
| `GOV-MULTIAGENT` | 一 active task/agent、共享写串行、独立 reviewer、wave | `execution.md` |
| `GOV-SOURCE` | 原始来源优先、截图/渲染、有效版本、待确认 | `source-authority.md` |

任何当前铁律无法映射、映射到两个定义或缺少 activation check，均为 GVR-3 P1，manifest
不得生效。矩阵作为 GVR-3 evidence，不在激活后继续常驻根上下文。

## 5. 深模块：taskctl

### 5.1 Seam 与 interface

外部 interface 固定为：

```text
./scripts/taskctl <TASK-ID> start --task-file <path> [--bootstrap-kernel <candidate> --bootstrap-manifest <candidate>]
./scripts/taskctl <TASK-ID> record <step> -- <command...>
./scripts/taskctl <TASK-ID> backend-test red -- <pytest-args...>
./scripts/taskctl <TASK-ID> backend-test test -- <pytest-args...>
./scripts/taskctl <TASK-ID> prepare-review [--kernel <candidate> --manifest <candidate>]
./scripts/taskctl <TASK-ID> review lease <independent|governance|tooling> --reviewer <id>
./scripts/taskctl <TASK-ID> review submit <independent|governance|tooling> --report <path>
./scripts/taskctl <TASK-ID> governance-adopt --approval <path>
./scripts/taskctl <TASK-ID> activate --kernel <candidate> --manifest <candidate>
./scripts/taskctl <TASK-ID> close
./scripts/taskctl <TASK-ID> doctor
```

`start` 自动解析任务合同中的 Allowed Files；调用者不再重复传递 allowlist。
普通任务禁止 bootstrap 参数。只有 manifest 声明的 exact GVR-3 task ID，在 active
v2 manifest 尚未安装且 Evidence 1.1 bundle 已 init/录入 RED 后，必须同时传入
`--bootstrap-kernel` 与 `--bootstrap-manifest`。taskctl 必须验证：两个 path 位于
已接受 GVR-1 artifact；bytes/hash 等于 GVR-1 耐久记录；manifest schema/
selectors 有效且 `activation_task` 等于当前 GVR-3；task path/metadata/allowlist 与
v1 `task.json` 一致；两个 GVR 依赖已 PASS。然后它以第 10 节的 pre-v2
non-PASS 规则原子 adopt 当前 bundle，保全 RED/v1 prefix 字节、不重捕
baseline，建立 v2 `IMPLEMENTING` state 并记录 bootstrap hashes/module selection。任一
验证失败均不改状态；重复相同调用幂等，参数/bytes 改变则拒绝。

`doctor` 只读，用于断线或 stall 后报告 agent/process、diff、artifact、lock 和第一个
未完成步骤，不自动删除锁或重跑命令。

`record` 保存 caller cwd、argv boundaries 和命令分类。明显的 backend pytest、migration
或 taskctl 内部 close command 不得通过 generic record 绕过专用 lease/gate；命令无法
分类时记录为 `UNKNOWN` 并 fail closed，而不是猜测为 non-SQLite。可信工作区模型不尝试
解析任意 shell 程序，但 review/gate 会拒绝以 shell 包装器隐藏受控命令的任务证据。
GVR-3 的 canonical scope argv 只能是 `python3 scripts/evidence_scope.py finalize <GVR-3>`；
canonical frozen-v1 argv 只能是该物化合同中冻结的
`python3 scripts/frozen_v1_acceptance.py ...`。taskctl 对这两个 exact argv 分类并验证
step/task/path，任何 wrapper、替代 runner 或参数变化都 fail closed。

普通任务的 `prepare-review` 不接受 candidate 参数；它在 final lint/test/scope 成功后
冻结 pre-review candidate manifest 并以 CAS 从 `IMPLEMENTING` 转为
`READY_FOR_REVIEW`。只有 manifest 冻结的 GVR-3 task ID 必须同时传入
`--kernel` 与 `--manifest`；两个 path 都必须位于 GVR-1 已接受且 digest
冻结的 candidate artifact。taskctl 以这两个 bytes 虚拟替换实际根路径，生成
与未来安装后完全相同的 scoped patch，并将 kernel hash、manifest hash、patch
hash 和 governance digest 原子纳入 candidate fingerprint。GVR-3 缺一参数、传空
参数、超出冻结 artifact 或在其他任务传入参数都 fail closed。

`review lease` 只能由 controller ownership
record 中的 lead 调用，为当前 candidate/axis/reviewer 写一次性 lease。`review submit` 读取
该 lease，拒绝
implementer ID、错误 axis、过期 fingerprint 或 GVR-3 两轴复用同一 ID；它计算并写入
candidate/patch/governance hashes，调用者只提供正文与终态 counts。这里的 lease 是可信工作区
内的职责/时序约束，不声称是抵御恶意本地操作者的加密身份协议。

`governance-adopt` 只接受第 4.4 节独立治理 approval，CAS 前置状态必须是
`BLOCKED/GOVERNANCE_DIGEST_MISMATCH`；成功后更新 digest、使旧 candidate/review/gates
失效并回到 `IMPLEMENTING`，不重捕 baseline。`close` 只对已安装耐久 result
的成功 ordinal，或明确返回非零 result 的失败 ordinal 做幂等继续；相同
action-request digest 不单独构成可重放授权。`doctor` 永不改变 state。

`activate` 只允许 manifest 中冻结的 GVR-3 task ID 调用，且输入 bytes 必须匹配两个 review
绑定的 candidate fingerprint/hash/digest；其他任务或未审批 candidate 一律拒绝。其安装
顺序与 crash semantics 见第 10 节，不能被 generic record 代替。

### 5.2 兼容 Adapter

- `evidence_init.sh` 变为 `taskctl start` Adapter；
- `evidence_run.sh` 变为 `taskctl record` Adapter；
- `evidence_task.py` 保留原 CLI，并委托 taskctl implementation；
- 旧脚本在一个完整产品 pilot 通过前不删除。

Adapter 不拥有业务逻辑，不手写 JSON、锁、scope 或 gates。删除 taskctl 后复杂度会重新
散落到多个 Adapter，因而该 module 具有实际 depth。

`prepare-review` 冻结的 candidate fingerprint 只包含 pre-review inputs：task contract、
allowlist、governance digest、baseline identity、当前 scoped patch、summary，以及 task
contract 要求的 final result+log hashes。普通任务的必需集合为 lint/test/scope；
GVR-3 还必须包含 `frozen_v1`。因 `scripts/frozen_v1_acceptance.py` 是 GVR-3
allowlisted source，它的 bytes 同时已在 scoped patch 中。之后新增的 review/task-gate/atomic
receipts 不属于 candidate，不能使它自我失效。

close 使用独立 chain，action key 为 `(task ID, candidate fingerprint, ordinal,
action-request-digest)`；request digest 包含 command argv、cwd、step、axis 和 required-step
set。同一 key 已成功的 ordinal 不重跑；任何 pre-review input 改变才使 candidate 及全部
review/gate receipts 失效。doctor 指向第一个缺失或失败的 ordinal。

## 6. 证据与状态模型

### 6.1 权威状态机

```text
READY → IMPLEMENTING → READY_FOR_REVIEW → REVIEW_APPROVED
      → CLOSING → PASS
```

任一阶段可进入 `FAIL`；需要外部决定时进入 `BLOCKED`。任务 Markdown 的 Status 是人类
可读阶段，不再单独构成接受事实。终态由 task-local `state.json`、append-only results 和
消费者共同决定。

close 的顺序固定为：

1. 获取 task-local controller lease，以 compare-and-swap 要求 state=`READY_FOR_REVIEW`、
   candidate fingerprint 未变、latest lint/test/scope 为 rc 0；
2. 重新生成 baseline-subtracted scope，并重新计算 fingerprint；
3. 严格验证唯一最终 review 与当前 patch hash/digest；
4. 原子转为 `REVIEW_APPROVED`，记录并执行 `independent_review`；
5. 原子转为 `CLOSING`，依次记录并执行 `task_gate`、`atomic_evidence`；
6. 仅在前述步骤均为 rc 0 时，以 temp+fsync+rename 原子写入 `state.json: PASS` 和 terminal
   ordinal。

close 失败时不得留下 PASS；任务/summary/review/产品文件不得由 close 改写。release gate
只接受 `state.json: PASS` 且所有 required result/log 最新有效的 v2 任务。

已安装非零 result 的 stage 失败时 state 进入 `FAIL`，记录 fingerprint、
failed ordinal 和 `resume_from`；相同 fingerprint 可以从该已知失败 ordinal 重试。
缺 result 的情形不属于此分支，必须按第 6.2 节的 `OUTCOME_UNKNOWN`/
replay-safe 规则处理。任何 source/test/task/summary/review bytes 改变都会回到
`IMPLEMENTING` 或 `READY_FOR_REVIEW`，使旧 review 与之后的 ordinals 失效。这样无需
在 gate 前写假 PASS，也无需 status-only hash confirmation。

### 6.2 原子 event store 与 JSONL compatibility view

v2 的权威记录不是直接追加 JSONL，而是 task-local `events/`：

```text
events/<ordinal>.command.json
events/<ordinal>.result.json
```

每个 event 先写同目录随机 temp、完成全部 bytes、fsync file，再以 exclusive rename 安装并
fsync directory。task-local FD lock/CAS state 为 action-request-digest 预留唯一 ordinal；两个
writer 不能获得同一 ordinal。SIGKILL 发生在 rename 前只留下可清理 temp，发生在 rename 后
event 已完整耐久，不会出现半个 JSON object。

command event 已安装而 result event 缺失时状态为 `COMMAND_WITHOUT_RESULT`，state 不前进。
对 generic/opaque external command，原进程结束后必须转为
`BLOCKED/OUTCOME_UNKNOWN`：不得自动重放、不得伪造 result，即使 argv/cwd/digest
相同也不例外。只有 taskctl 内部 action 在命令分类表中预先声明
`replay_safe=true`，且其 effect verifier 能区分“未生效”与“已耐久生效”时，
doctor 才可在同一 ordinal 上继续：已生效则从耐久事实安装 result，未生效
则重执行；无法证明时仍 `OUTCOME_UNKNOWN`。SIGKILL、short-write、EINTR、ENOSPC、
file/dir fsync failure、rename failure、ordinal reservation crash、opaque-command
post-effect/pre-result crash、内部 replay-safe action 的 effect-verifier 两分支和两个 writer
竞争必须逐 fault point 测试。

`commands.jsonl`/`results.jsonl` 保留为 compatibility view，而不是 acceptance authority。
view 从完整 events 以 temp+fsync+rename 原子生成；若 crash，旧 view 保持完整，doctor 可从
events 重建。新 v2 task 的 view 每行必须有效 JSON。adopted task 的原 v1 prefix bytes 保持
逐字相同并记录 length/hash，view 只在该 prefix 后投影 v2 events；v2 consumer 读取 events，
不把可能 malformed 的 legacy prefix 当作 v2 evidence。

### 6.3 SQLite lease

使用 OS 自动释放的 FD `LockLease` implementation：对固定 regular lock file 获取
`flock(LOCK_EX|LOCK_NB)`；只有成功持有 FD 才能运行 pytest，FD close 或进程退出会由内核
释放权威锁。contention 立即 fail closed，不等待、不删除 foreign state。

owner sidecar 仅用于诊断，通过 temp+fsync+rename 写入，不构成锁权威；owner 写入失败时
pytest 不启动并关闭 FD。pytest 启动失败、信号终止、FD close/sidecar cleanup failure都有
独立非零结果。即使 sidecar unlink/rmdir 类清理永久失败，也不能阻塞下一 holder；下一进程
只相信 flock，并在成功持锁后更新诊断 sidecar。tests 必须覆盖进程 SIGKILL 后下一 holder
立即可获得 lease，以及 sidecar 永久失败不形成假 contention。

SQLite 模板缓存和 FIFO 是 performance Adapter，可在 Foundation 后加入，不改变 LockLease
interface；Governance Reset 只为其保留 seam，不提前实现。

### 6.4 独立复审绑定

普通任务的 `review/independent_review.md` 必须包含且只能包含一组终态字段：

```text
Reviewed-Candidate-Fingerprint: <64 lowercase hex>
Reviewed-Patch-SHA256: <64 lowercase hex>
Reviewed-Governance-Digest: <64 lowercase hex>
Reviewer-ID: <durable agent/session identity>
Verdict: APPROVED
P0: 0
P1: 0
P2: 0
```

禁止同一文件出现 `CHANGES_REQUESTED`、第二个 Verdict、`none`、非数字 counts，或与当前
candidate/scope/governance 不一致的 hash。review file hash 在验证后进入 close state；后续
任何 byte 改变都会使 review ordinal 失效。实现者不得写 review；可信工作区模型下不增加
加密身份协议。

GVR-3 激活不是普通单轴任务，必须有两个文件：`review/governance_axis.md` 与
`review/tooling_axis.md`。两者均包含上述字段；两个 reviewer identity 必须互不相同，且均
不同于 implementer。
taskctl 的 canonical `independent_review` step 同时验证两个文件并生成机器 summary，不能由
实施者或其中一个 reviewer 替另一个轴批准。任一轴缺失、hash/digest 不同或非零 finding，
activation fail closed。

GVR-3 validation 对 `(candidate fingerprint, patch SHA-256, governance digest)` 三元组执行：
governance axis == tooling axis == close 当前重新计算值。三个维度分别 mismatch 的 fixtures
都必须 fail closed；只比较 patch/digest 或只比较两轴彼此均不充分。

## 7. Scope 与沙箱兼容

临时 Git index 改到仓库可写的 task-local temporary directory，或 OS temp 中由 repo digest
隔离的目录，并通过 `GIT_INDEX_FILE` 指向它。创建、使用和清理全部在一次 scope command
内完成；不得触碰真实 index，不需要 `.git` 写权限，不与另一任务共享临时 index。
temporary directory 必须 0700、拒绝 symlink、使用随机文件名和 exclusive create；无论
Git 成功、失败或进程收到可处理信号，finally 都清理本 task 创建的 index，绝不删除 foreign
path。无法确认 ownership 时保留现场并 fail closed。

测试必须覆盖 clean/dirty、tracked/untracked、非 ASCII 路径、删除、失败清理和两个串行
任务。任何 outside-allowlist 新变化仍 fail closed。

## 8. Liveness 与 transport

Governance Reset 不声称消除平台故障。它改变的是恢复成本：

- 每个 taskctl action 写入开始/结束和 durable ordinal；
- doctor 依据进程、lock、ordinal、diff 与 artifact 给出唯一 live-state；
- transport failure 先 reconcile，不重复已完成 ordinal；
- TRUE_STALL 仍使用 30/90 秒判定，最多一次 replacement；
- replacement 仍 stall 时由无其他实施任务的 lead 接管同一 exact task，或仅暂停该 lane。

AGENTS 只保存上述不变量；平台事件字段和诊断细节位于 `execution.md`。

## 9. 三项串行实施任务

三个槽位在计划阶段物化为三个精确 task path；以下 closure/non-closure/dependency 是上限，
不是允许实施者自行合并新工作。

Revision 4 已将三个合同物化为 `DRAFT / NOT IMPLEMENTATION READY` 文件。每个文件枚举
规范机器 metadata、exact Allowed Files、chosen runbook、在 repository root 执行的精确
argv/预期 rc、evidence path 和 remaining follow-ups；设计双轴必须同时审查这些
task bytes。只有设计最终批准并把三份状态转为
`CONTRACT FROZEN / READY` 后才可初始化任何 implementation evidence。

### GVR-1：规范模块与治理验证器

- Task path：`tasks/repo/REPO-GOVERNANCE-RESET-MODULES-20260716-01.md`。
- Exact closure：创建第 4.3 节六个模块、rule declaration/reference/selector schema、
  `governance_validate.py` 与结构测试；在本任务 artifact 中产出 kernel/manifest candidate、
  铁律保全 ledger 和 digest。
- Exact Allowed Files：以该已物化 task file 为准，包括六个命名的 `docs/agents/*.md`、
  `scripts/governance_validate.py`、`scripts/tests/test_governance_validate.py`、own artifacts。
- Non-closure：不修改根 `AGENTS.md`、任何 active manifest、evidence consumer/Adapter 或产品。
- Dependency：当前设计最终批准；完成后必须独立治理 review 和 task gates PASS。

### GVR-2：taskctl 与 Evidence v2 implementation

- Task path：`tasks/repo/REPO-GOVERNANCE-RESET-TASKCTL-20260716-01.md`。
- Exact closure：实现 `scripts/taskctl` 的 start/record/backend-test/close/doctor、状态机、
  rollback append、LockLease、strict review/hash、legacy-prefix adopt 与 scope temporary index；
  提供 fault-injection、concurrency、idempotence 和 close-order tests。
- Exact Allowed Files：以该已物化 task file 为准，包括 `scripts/taskctl`、`scripts/evidence_scope.py`、
  `scripts/tests/test_taskctl.py`、`scripts/tests/test_evidence_scope_v2.py`、own artifacts。
  GVR-1 candidate 是只读依赖。
- Non-closure：不修改根 AGENTS、active manifest、旧 Adapter、现有 task/atomic/release
  consumer 或产品；不实现 SQLite template cache/FIFO。
- Dependency：GVR-1 independently accepted PASS。

### GVR-3：兼容、shadow validation 与有效激活

- Task path：`tasks/repo/REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01.md`。
- Exact closure：把现有 evidence init/run/task 入口变为 Adapter；更新 task/atomic/release
  consumers 的互斥 v1-ledger/v2-state 路径；生成 legacy PASS ledger；执行 shadow fixtures；
  将 reviewed candidate 内容写入根 AGENTS 和 `docs/agents/manifest.json`；由两个独立轴
  审批同一 patch/digest，最后通过 taskctl close 写入 GVR-3 state PASS。
- Exact Allowed Files：以该已物化 task file 为准，包括根 AGENTS、active manifest、legacy PASS ledger、现有
  evidence Adapter/三个 consumer/release gate、受审查的 `scripts/frozen_v1_acceptance.py`、
  精确兼容测试、own artifacts。
- Non-closure：不改 module/taskctl implementation、任何历史 task artifact、产品代码、V8
  catalog/plan 或 release 状态。
- Dependency：GVR-1 与 GVR-2 independently accepted PASS，且没有 active product owner、
  SQLite/migration/shared verification。

三项任务严格串行，符合最多三项 governance prerequisite 的上限。只有落在某 task 已批准
exact closure 内的 defect 才能在同一 task 修复；hidden prerequisite、第二 closure、allowlist
扩展或第四 prerequisite 必须停下并回到用户批准，绝不能为守住“三项”而吸收。

GVR-1/GVR-2 仍由激活前 Evidence 1.1 close 接受。为满足现行 consumer 的明确
precondition，实施者必须在最终 lint/test 后、独立 review 前：①仅把该 task 首个
Status 行置为 `Status: PASS / IMPLEMENTATION COMPLETE / PENDING EVIDENCE 1.1 CLOSE`；
②用各 task 合同冻结的字段完成 `summary.md`，其 Status 必须为同一字符串；
③重新 finalize baseline-subtracted scope/生成 patch 并记录 task、summary、patch hashes。
该 `PASS / ... PENDING` 只是 Evidence 1.1 的 bootstrap 内容 precondition，不是任务终态、
不能激活 v2 或恢复产品 Goal。reviewer 必须在此后审查该 final task/
summary/patch bytes 并在 report 写入三个 SHA-256；review 后这三者不得再改。
同一 reviewer 还必须写入三行标准 `shasum -a 256` checksum file，并在 close 前由
合同冻结的 `shasum -a 256 -c` argv 返回 0。然后才能调用现行
`evidence_task.py close`。由于 close 的第一 child 会重新 finalize patch，close 返回 0 后
必须立即以同一 argv/checksum file 再记录一次最新 `review_binding: rc=0`，再运行
要求 `review_binding` 的最终 atomic validation。任一 hash 变化需要重新
finalize 和独立 review，不得用旧 report 关闭。

## 10. 激活与兼容策略

- 激活期间暂停全部产品实施 lane 和 shared verification；只读审查可以继续。
- GVR-1 的 kernel/manifest candidate 始终位于 task artifact，绝不提前占用根路径。
- GVR-3 先用 Evidence 1.1 入口 init 并记录一次真实 RED，在修改任何
  Adapter/consumer 前调用精确 bootstrap `taskctl <GVR-3> start --task-file <task>
  --bootstrap-kernel <GVR-1-kernel> --bootstrap-manifest <GVR-1-manifest>`。它必须按
  第 5.1 节 adopt 旧 bundle 而不重捕 baseline；之后所有 GREEN/lint/scope/
  `frozen_v1`/review/gate 事实只由 v2 events 产生。
- GVR-3 在 own artifact 构造包含最终 source changes、根 AGENTS 和 manifest 的 candidate
  tree/patch；通过精确入口 `taskctl <GVR-3> prepare-review --kernel <GVR-1-kernel>
  --manifest <GVR-1-manifest>` 将两个虚拟替换 bytes 与当前 scoped patch 原子绑定。
  两个轴审批该虚拟 candidate，不要求根文件提前生效。candidate 根 AGENTS 必须
  包含 bootstrap：manifest 指向该 exact GVR-3，
  但只有 `artifacts/<GVR-3>/state.json == PASS` 时 v2 才有效；否则仓库处于
  `GOVERNANCE_STAGED`，只允许 GVR-3 close/remediation，产品 Goal 必须 blocked。
- GVR-3 是唯一 dual-mode bootstrap task。start 时把 pre-change legacy consumer bytes/hash
  复制到 own artifact。只有 allowlisted、Ruff/compile/test 通过且位于 candidate scoped
  patch 的 `scripts/frozen_v1_acceptance.py` 可以核验并在隔离 fixture 执行这些冻结
  bytes；不允许 artifact 内的可写 runner 或当前已修改 consumer 充当 gate。
  `frozen_v1` result/log hash 必须进入 prepare-review candidate。reviewers 审批最终
  patch 与 `PASS / GOVERNANCE_STAGED` 候选后，再用 candidate v2 taskctl close；两套结果
  都必须为零。
- 两个轴审批 virtual candidate 后，`taskctl activate` 只接受 prepare-review 已绑定的
  同两个 path/bytes，获取独占 activation FD lease，并按
  固定顺序安装：① root temp 完整写入+fsync，`os.replace(AGENTS.md)`，fsync repository root；
  ② 验证新 root 对 missing/old/mismatch manifest 一律 STAGED/fail-closed；③ manifest temp
  完整写入+fsync，replace `docs/agents/manifest.json`，fsync `docs/agents`；④ 重新计算 actual
  candidate triple，必须与两轴完全相同；`activate` 在此返回 0 并保持
  `GOVERNANCE_STAGED`；⑤唯一外部 close 入口 `taskctl <GVR-3> close` 运行 gates；
  ⑥ state PASS 最后写入。
  禁止 manifest-first。root 的 atomic replace 不存在 missing-root 窗口；root-first 后任何
  crash 都由 bootstrap 阻断产品，manifest 安装后也继续阻断直到 PASS receipt。
- tests 在 root write/fsync/replace/dir-fsync、manifest write/fsync/replace/dir-fsync、actual
  hash verification 和 PASS receipt 前后逐点注入 crash；每个恢复状态必须是 old-root 且
  controller pause 仍有效，或 new-root `GOVERNANCE_STAGED`，绝不能进入 active product。
- 历史 PASS 任务由 GVR-3 生成不可变 `legacy-pass-ledger.json`：task ID、接受时间、task
  file hash，以及整个 artifact tree（包含 task.json、baseline_allowlist、external dirt、
  commands、results、summary、diff、review、logs、status/其他既有文件）的规范化相对路径、
  file mode、byte length、SHA-256；按 path byte-order 计算总 root digest。symlink/非 regular
  file 拒绝。release consumer 对无 v2 state 的任务只接受该 ledger 中完整 path set 和 root
  digest 均未变的条目；新增、删除或修改任一 byte 都拒绝，不能靠 Markdown PASS 通过。
- pre-v2 未 PASS bundle 由 `start` 自动 adopt：逐一保全 task.json、baseline files、external
  dirt、commands、results、summary、diff、review、logs 的 byte length/hash，新增 governance
  digest、state 和 legacy prefix offset/hash，不重写历史 bytes、不重新 capture baseline；
  重复 adopt 必须幂等。
- adopted v1 prefix 只证明历史完整性，绝不能满足 v2 的 lint/test/scope/review/task/atomic
  required steps。所有 pre-v2 未 PASS task 必须在 adopt 后以 v2 events 重新产生 task contract
  要求的 canonical acceptance；只有 historical PASS ledger 分支可以复用冻结 v1 acceptance。
- task contract、allowlist 或 governance digest 无法确定时，仅该任务 fail closed。
- 激活后新任务必须走 taskctl；直接调用底层 helper 视为 gate failure。
- release consumer 使用互斥分支：`v2 state PASS` 或 `legacy ledger exact digest`；同时满足、
  两者均不满足或 bytes 改变都 fail closed。

## 11. 验收标准

### 治理

- 根 `AGENTS.md` ≤ 300 行；全部 fence、链接、manifest 和 rule ID 验证通过。
- 任一规则只有一个定义；source index 与 legacy rules 不再常驻根上下文。
- 第 4.5 节每个 family 都有 current-rule inventory、唯一 owner ID、required selector 和
  activation check；生命周期/期限、法律、官费/应收、谱系、认证/授权/权限、安全、
  schema/migration/seed/不可逆变更、SQLite、API/UI、客户决策和 release-last 无删除。
- digest mismatch 无独立 `governance_adoption.md` 时不能 close；adopt 不改变 baseline bytes。

### 工具

- event write/fsync/rename/dir-fsync 及 SIGKILL 任一失败点不安装半个 event；JSONL view 始终
  是旧完整版本或新完整版本，能从 events 重建；legacy prefix bytes/hash 不变。
- FD lease 在正常、pytest failure、signal 和 SIGKILL 后均由内核释放；owner sidecar 任一
  failure 不形成权威 contention。
- stale hash、两个 Verdict、`none`、非零 counts、缺失 review 全部被 close 拒绝。
- GVR-3 缺任一 axis、reviewer identity 重合，或两个轴/当前 close 的
  fingerprint/patch/digest 三元组任一不相等全部被拒绝。
- close 失败不产生 PASS；成功只需一次 command，无人工 status/hash-only 往返。
- start 不再接受手写 allowlist 列表；scope 不需要 `.git` 写权限。
- commands/results、logs、scope、review、task gate 和 atomic gate 全部由共享消费者验证。
- 相同 fingerprint 的 close retry 只能复用已耐久成功 result，或从已耐久
  非零 result 的 ordinal 继续；opaque command 的 `COMMAND_WITHOUT_RESULT` 一律
  `OUTCOME_UNKNOWN`/BLOCKED，不得自动重放。fingerprint 变化使旧 review/gates
  失效，不能复用。

### 兼容与性能

- legacy ledger fixtures 结果不变；digest 被改即拒绝；pre-v2 active bundle adopt 对全部
  artifact bytes 幂等保全且不重捕 baseline。
- v2 对 shadow fixtures 的结论必须与 v1 相同或更严格，不能更宽松。
- STAGED root/manifest、任意 activation crash point 和任一 GVR-3 gate failure均不能让产品
  task start；只有 GVR-3 state PASS 后 v2 有效。
- 第一个 2–4 个非冲突产品任务作为 pilot：JSON/cwd/step/gate-order 错误为 0，每任务一次
  canonical close，重复 full-file acceptance test 不超过 task contract 要求。
- pilot 只测量实际 wall-clock、active command time、review cycles 和 stall recovery；不预设
  虚构的加速百分比。

## 12. 复审与完成条件

设计冻结需要两个独立轴：

1. Governance/standards：权威层级、领域铁律、atomicity、migration 与 activation；
2. Evidence/tooling：状态机、JSON、lock、scope、review hash、compatibility 与 failure paths。

实施完成后 GVR-3 再执行同样双轴 final audit。只有两个轴均为 `APPROVED`、零 P0/P1/P2，
三项任务 evidence/gates 全部 PASS，manifest v2 才能激活。随后才恢复产品 Goal。

## 13. 预期效果与限制

该设计把复杂度从每个代理的记忆和手工命令中移入一个可测试的深 module，预计显著减少
规划重复、JSON/cwd/label 错误、人工 gate 往返和断线后的返工，同时保持独立复审和所有
高风险铁律。

它不能保证模型永不空跑或网络永不断开；它保证的是这些故障不会隐式改变任务状态，且
恢复从第一个未完成 ordinal 开始。端到端显著提速必须由激活后的真实 pilot 数据确认。
