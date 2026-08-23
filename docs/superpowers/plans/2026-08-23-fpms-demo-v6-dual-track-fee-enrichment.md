# FPMS Demo V6 Dual-Track Fee Enrichment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在不改变 V5 阶段 01–06 的前提下，把授权登记后的费用尾段升级为可面对客户演示的 GOV/SERVICE 双轨、多行草单、一次服务费调整、官费登记待核验及两次回款核销闭环。

**Architecture:** 复用现有 FeeObligation、FeeDraft、PayList、GovPayment、Bill、Payment、Offset 与 CaseActivityEvent；只增加 grant-specific 只读预览、runtime 多项目 bundle 编排、一次 superseding SERVICE 调整和可恢复的 demo command wrapper。所有任务按 `P0-prereq-heavy-story` 串行执行，共享 SQLite 写入和共享路由文件不并行。

**Tech Stack:** Python 3.11、FastAPI、SQLAlchemy、SQLite、Pydantic、Vue 3、TypeScript、Playwright、pytest、Ruff、ESLint。

## 2026-08-23 Lean 5.6 执行覆盖（仅替换流程，不改变产品闭包）

当前 Demo 分支已由提交 `ee73aa1` 切换到 Lean 5.6。该分支根 `AGENTS.md` 明确将
`scripts/taskctl`、canonical scope 和旧 evidence machinery 设为只读历史。因此，本计划后文所有
`taskctl`、task materialization、artifact evidence、prepare-review/close/doctor 指令均不执行；它们
不再是产品 Gate，也不得为恢复它们而修改旧治理代码。

产品规格、Task 01→07 顺序、每个 Task 的 Closure/Non-closure/Files、targeted RED/GREEN、共享文件
串行、fresh SQLite、双轮验收和独立 High review 全部保持不变。执行机械映射固定为：

- `backend-test red/test` → 使用当前后端虚拟环境直接运行同一 focused pytest argv；
- `record lint` / frontend checks → 直接运行同一 scoped check-only argv；
- `scope/prepare-review/close/doctor` → 用候选 commit SHA/range、focused checks 和独立 High reviewer
  的零发现结论完成 story 验收；
- 每个 story 只提交其声明的产品/测试/文档路径，不创建旧格式 task/evidence 文件。

本覆盖来自对当前分支治理字节的实际核验，只纠正已退役执行机制，不重新设计或扩大 V6。

---

## 0. 权威规格与不可变边界

实现必须逐条服从：

- `docs/superpowers/specs/2026-08-23-fpms-demo-v6-dual-track-fee-enrichment-design.md`
- 规格 SHA-256：`3ea6455b53fd87523dd086f0569c6f6492d0031baf80286ef85576d8d42e803b`
- V5 基线：`docs/postdemo/demo-lifecycle-customer-v5.html`
- V5 runbook：`docs/postdemo/demo-lifecycle-customer-v5-runbook.md`

以下内容不是实现自由度：

- V5 阶段 01–06 原样保留；
- 官费 preview no-write，且不扩展通用 preview trigger；
- GOV 与 SERVICE 不得进入同一草单或对方下游对象；
- GOV 草单行不可编辑；SERVICE 只有一次专用、可追溯的数量调整；
- 无官方凭证的 GovPayment 只能显示“已登记，待官方凭证核验”；
- 两次回款和两次核销后才结清客户账单；
- 每次演示必须使用新 run root 和新 SQLite 数据库；
- `SYNTHETIC_TEST_ONLY` 只能达到 `TECHNICAL_REHEARSAL_PASS`；
- 不实现费减、年费、滞纳金、坏账、撤销、多币种、规则引擎或生产发布。

若规格哈希变化，停止当前任务，重新完成规格审查和计划差异审查，不自行吸收变化。

## 1. Gate 0：任何产品改动前的硬门禁

Gate 0 是外部前置，不是本计划的产品任务，也不得被实现者顺手修复。

- [ ] 在当前 worktree 执行：

```bash
./scripts/taskctl REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01 doctor
```

预期：terminal PASS，且 manifest、激活任务和治理 bytes 绑定一致。当前已知输出为
`task artifact authority root is missing`；该输出下禁止创建产品 task、修改产品文件或运行产品测试。

- [ ] 确认后端测试工具存在：

```bash
test -x backend/.venv/bin/pytest
test -x /Users/cfcc/Library/Python/3.11/bin/ruff
```

若 pytest 缺失，只在 Gate 0 恢复后按 `backend/pyproject.toml` 建立开发环境：

```bash
uv pip install --python backend/.venv/bin/python -e 'backend[dev]'
```

不得把虚拟环境文件加入 git。

- [ ] 获得并校验 customer demo 的两个 exact runtime 输入：
  - `CNIPA`、`APPROVED/ACTIVE` 的 OfficialRateBook/FeeRate，至少两行；
  - exact-digest-pinned `CUSTOMER_AUTHORIZED` SERVICE bundle，至少两个项目。

缺少 customer-authorized 输入时，可以实施和完成 `TECHNICAL_REHEARSAL_PASS`，但最终状态必须为
`DEMO_INPUT_REQUIRED`，不得报告 `DEMO_READY`。

## 2. 原子编排分类

- `shared_file_density: HIGH`
- `prereq_dependency_density: HIGH`
- `be_fe_coupling: HIGH`
- `evidence_cost: HIGH`
- `chosen_runbook: P0-prereq-heavy-story`

执行规则：

1. 七个任务严格按 01 → 07 串行；同一时间只有一个 task owner。
2. 每个任务开始前 materialize exact task file，建立独立 evidence root，并运行 `taskctl start`。
3. 每个行为变更先提交 focused RED，再写最小 GREEN；不得先写实现后补测试。
4. 每个任务只运行列出的 focused checks；repo-wide checks 只在 Task 07。
5. HIGH 任务的实现者不能批准自己的工作；每个任务 close 前必须有独立零发现审查。
6. 共享文件在后继任务中以最新已接受任务为 baseline，禁止把前序 diff 重算进当前任务。
7. 一个任务发生阻塞时停止受影响 lane；不得以重构共享基础设施绕开阻塞。

## 3. 批次清单与依赖

| 序号 | Task ID / task path | Closure | Evidence root | 依赖 |
| --- | --- | --- | --- | --- |
| 01 | `FPMS-DEMO-V6-RUNTIME-CONTRACT-20260823-01` / `tasks/postdemo/FPMS-DEMO-V6-RUNTIME-CONTRACT-20260823-01.md` | runtime 多项目合同、新 run preflight、readiness | `artifacts/FPMS-DEMO-V6-RUNTIME-CONTRACT-20260823-01/` | Gate 0 |
| 02 | `FPMS-DEMO-V6-GOV-OFFICIAL-FEE-20260823-02` / `tasks/postdemo/FPMS-DEMO-V6-GOV-OFFICIAL-FEE-20260823-02.md` | grant preview、人工确认、多行 GOV 草单 | `artifacts/FPMS-DEMO-V6-GOV-OFFICIAL-FEE-20260823-02/` | 01 |
| 03 | `FPMS-DEMO-V6-SERVICE-ADJUSTMENT-20260823-03` / `tasks/postdemo/FPMS-DEMO-V6-SERVICE-ADJUSTMENT-20260823-03.md` | 多行 SERVICE obligation、一次 superseding adjustment、双轨来源只读模型 | `artifacts/FPMS-DEMO-V6-SERVICE-ADJUSTMENT-20260823-03/` | 01, 02 |
| 04 | `FPMS-DEMO-V6-FINANCE-20260823-04` / `tasks/postdemo/FPMS-DEMO-V6-FINANCE-20260823-04.md` | PayList/GovPayment 恢复、两次回款核销 | `artifacts/FPMS-DEMO-V6-FINANCE-20260823-04/` | 02, 03 |
| 05 | `FPMS-DEMO-V6-CUSTOMER-UI-20260823-05` / `tasks/postdemo/FPMS-DEMO-V6-CUSTOMER-UI-20260823-05.md` | 正常业务页的双轨客户展示 | `artifacts/FPMS-DEMO-V6-CUSTOMER-UI-20260823-05/` | 04 |
| 06 | `FPMS-DEMO-V6-CANONICAL-E2E-20260823-06` / `tasks/postdemo/FPMS-DEMO-V6-CANONICAL-E2E-20260823-06.md` | V6 runner、live E2E、lifecycle、runbook | `artifacts/FPMS-DEMO-V6-CANONICAL-E2E-20260823-06/` | 05 |
| 07 | `FPMS-DEMO-V6-CUSTOMER-ACCEPTANCE-20260823-07` / `tasks/postdemo/FPMS-DEMO-V6-CUSTOMER-ACCEPTANCE-20260823-07.md` | 两次全新 run、最终独立验收 | `artifacts/FPMS-DEMO-V6-CUSTOMER-ACCEPTANCE-20260823-07/` | 06 + DEMO_READY 输入 |

这张表是 planning-only manifest。用户批准本计划且 Gate 0 PASS 后，才创建 task files 和批次控制文件。

## 4. 共享文件冲突图

| 共享面 | 首次 owner | 后继 owner | 规则 |
| --- | --- | --- | --- |
| `backend/app/core/demo_bundle.py` | 01 | 03 只消费，不再改合同 | 03 如需改合同必须退回 01 重新验收 |
| `scripts/run_demo_integrated_a_rehearsal.py` | 01 | 06 | 01 只做输入/新 run；06 只编排阶段 07–11 |
| `backend/app/modules/grant_fees/api.py` | 02 | 无 | 05 仅改前端，不回改 API |
| `backend/app/modules/fees/api.py` | 03 | 无 | SERVICE 路由一次闭合 |
| `backend/app/modules/billing/api.py` | 04 | 无 | finance wrapper 一次闭合 |
| 前端 API clients / pages | 05 | 06 只由 E2E 消费 | 06 不改客户 UI，发现缺口则退回 05 |
| live E2E / V6 docs | 06 | 07 只读取 | 07 不修产品，只报告或退回 owner |

## 5. 冻结的 API、权限与 HTTP 契约

所有端点沿用相邻 API 的 Bearer JWT、BusinessError envelope 和 FastAPI validation envelope，
不得新增权限码或自定义错误 envelope：

| Endpoint | Permission | Success/replay | Failure semantics |
| --- | --- | --- | --- |
| `GET /grant-fee-tasks/{task_id}/official-fee-preview` | `GrantFeeTask.Read` | 200 / N/A | 401 未登录；403 缺权限；404 task/evidence 不存在；409 来源、状态、digest 或 stored lineage 冲突；422 path validation |
| `POST /grant-fee-tasks/{task_id}/official-fee-confirmation` | `GrantFeeTask.Write` | 201 首次；200 exact replay | 401；403；404 task/evidence 不存在；409 preview drift、重复确认、金额/类型/状态冲突；422 payload validation |
| `POST /fees/drafts/{draft_id}/demo-service-adjustment` | `Fee.Draft.Edit` | 201 首次；200 exact replay | 401；403；404 draft/item 不存在；409 source/quantity/CAS/relink/second-adjustment/drift；422 payload validation |
| `GET /fees/drafts/{draft_id}/source-facts` | `Fee.Draft.Read` | 200 / N/A | 401；403；404 draft 不存在；409 stored lineage invalid；422 path validation |
| `POST /gov-payments/demo-command` | `GovPayment.Create` | 201 首次；200 exact replay；202 已保留但尚未完成 | 401；403；404 PayList/item 不存在；409 type/amount/payload/stored-state drift；422 payload validation |
| `GET /gov-payments/idempotency/{key}` | `GovPayment.Create`（与相邻登记动作相同，不新增 `Read` 权限） | 200 完成；202 pending | 401；403；404 command 不存在；409 stored-state drift；422 path validation |

每个新增 API 的 focused test 必须覆盖允许权限、无 token 401、缺 exact permission 403、404、409、422，
以及首次/replay 状态码；不得用管理员全权限用例代替 permission boundary。
response models 分别固定为 `GrantOfficialFeePreviewOut`、`GrantOfficialFeeConfirmationOut`、
`DemoServiceAdjustmentOut`、`DemoV6DraftSourceFactsOut` 和 `DemoGovPaymentCommandOut`；均像相邻 endpoints
直接返回 response model，不套新的 success envelope。错误继续使用全局 BusinessError/validation envelope。

## 6. 每个 HIGH task 的标准证据关闭协议

Task-specific 步骤中的 RED/GREEN/lint 命令必须通过 `taskctl` 记录。GREEN 后顺序固定为：

1. 运行 scoped `git diff --check` 诊断并确认空输出；
2. `git add -- <exact allowlist>`，按 task 中的 commit message 冻结 candidate commit；
3. 记录 canonical scope：

```bash
./scripts/taskctl TASK_ID record scope -- python3 scripts/evidence_scope.py finalize TASK_ID
```

4. 执行 `prepare-review`，此后禁止 candidate-affecting edit；
5. 租约给非实现者，review report 必须绑定 candidate commit/tree、patch SHA-256、task/summary hashes；
6. 提交唯一 `Verdict: APPROVED / P0: 0 / P1: 0 / P2: 0` 的报告；
7. `close` 后立即 `doctor`，两者均为 terminal PASS 才能开始下一 task。

每个 task 将 `TASK_ID` 替换为批次表中的 literal task ID；task materialization 时不得保留占位符。
reviewer IDs 固定为 `<task-id-lowercase>-independent-r1`，报告固定为
`artifacts/<TASK_ID>/review/independent.md`。例如 Task 01 的完整尾段是：

```bash
git add -- backend/app/core/demo_bundle.py backend/tests/test_demo_abc_runtime_bundle.py scripts/run_demo_integrated_a_rehearsal.py backend/tests/test_demo_integrated_a_runner.py
git commit -m "feat(demo): define v6 runtime input contract"
./scripts/taskctl FPMS-DEMO-V6-RUNTIME-CONTRACT-20260823-01 record scope -- python3 scripts/evidence_scope.py finalize FPMS-DEMO-V6-RUNTIME-CONTRACT-20260823-01
./scripts/taskctl FPMS-DEMO-V6-RUNTIME-CONTRACT-20260823-01 prepare-review
./scripts/taskctl FPMS-DEMO-V6-RUNTIME-CONTRACT-20260823-01 review lease independent --reviewer fpms-demo-v6-runtime-contract-20260823-01-independent-r1
./scripts/taskctl FPMS-DEMO-V6-RUNTIME-CONTRACT-20260823-01 review submit independent --report artifacts/FPMS-DEMO-V6-RUNTIME-CONTRACT-20260823-01/review/independent.md
./scripts/taskctl FPMS-DEMO-V6-RUNTIME-CONTRACT-20260823-01 close
./scripts/taskctl FPMS-DEMO-V6-RUNTIME-CONTRACT-20260823-01 doctor
```

Tasks 02–07 使用完全相同的 expanded sequence；materialized task file 必须逐条写出命令，不能保留
`TASK_ID`。literal review binding 如下：

| Task | Reviewer ID | Report |
| --- | --- | --- |
| 02 | `fpms-demo-v6-gov-official-fee-20260823-02-independent-r1` | `artifacts/FPMS-DEMO-V6-GOV-OFFICIAL-FEE-20260823-02/review/independent.md` |
| 03 | `fpms-demo-v6-service-adjustment-20260823-03-independent-r1` | `artifacts/FPMS-DEMO-V6-SERVICE-ADJUSTMENT-20260823-03/review/independent.md` |
| 04 | `fpms-demo-v6-finance-20260823-04-independent-r1` | `artifacts/FPMS-DEMO-V6-FINANCE-20260823-04/review/independent.md` |
| 05 | `fpms-demo-v6-customer-ui-20260823-05-independent-r1` | `artifacts/FPMS-DEMO-V6-CUSTOMER-UI-20260823-05/review/independent.md` |
| 06 | `fpms-demo-v6-canonical-e2e-20260823-06-independent-r1` | `artifacts/FPMS-DEMO-V6-CANONICAL-E2E-20260823-06/review/independent.md` |
| 07 | `fpms-demo-v6-customer-acceptance-20260823-07-independent-r1` | `artifacts/FPMS-DEMO-V6-CUSTOMER-ACCEPTANCE-20260823-07/review/independent.md` |

任何 review finding 只退回本 task 的受影响步骤；修改后重新记录 GREEN/lint/scope、重新 freeze
candidate、重新 review，不复用旧报告。

## Task 01：Runtime 多项目合同与隔离 run preflight

**Closure:** bundle 由单个 SERVICE rate 升级为至少两个项目，绑定官方 fee selectors、首笔回款金额和 readiness；runner 只接受 exact bundle，并持续保证全新 run root/SQLite。

**Files:**

- Modify: `backend/app/core/demo_bundle.py`
- Modify: `backend/tests/test_demo_abc_runtime_bundle.py`
- Modify: `scripts/run_demo_integrated_a_rehearsal.py`
- Modify: `backend/tests/test_demo_integrated_a_runner.py`

**Non-closure:** 不创建业务 obligation/draft/payment，不写默认金额，不改变正式 ServicePriceBook。

- [ ] **Step 1: materialize task contract and capture baseline**

Task allowlist 只能包含上述四个文件和 task/evidence 元数据。运行 `taskctl start`，保存规格哈希、HEAD、
dirty baseline、依赖工具版本和 exact bundle 输入路径；SQLite lease 只在 focused pytest 时持有。

- [ ] **Step 2: write RED bundle contract tests**

在 `test_demo_abc_runtime_bundle.py` 增加最小用例：

```python
assert len(snapshot.service_rates) >= 2
assert {row.adjustable for row in snapshot.service_rates} == {False, True}
targets = [row for row in snapshot.service_rates if row.final_quantity != row.initial_quantity]
assert len(targets) == 1 and targets[0].adjustable
assert snapshot.first_receipt_amount > 0
assert snapshot.official_fee_selector.fee_codes == expected_fee_codes
```

同时覆盖：exact digest drift、重复 item code、少于两项、没有固定项、没有可调整项、非 CNY、
final quantity 未绑定 exact adjustable item、`final_quantity <= 0`、`first_receipt_amount <= 0`、
官方 selector 少于两行、customer profile 使用 synthetic authority 均 fail closed。

运行 RED：

```bash
./scripts/taskctl FPMS-DEMO-V6-RUNTIME-CONTRACT-20260823-01 backend-test red -- -q backend/tests/test_demo_abc_runtime_bundle.py -k 'v6'
```

预期：仅因 `service_rates`、官方 selector 或 receipt 合同尚不存在而失败；基础设施错误不算 RED。

- [ ] **Step 3: implement the smallest immutable snapshot**

将单数 `service_rate` 改为 `service_rates: tuple[DemoServiceRate, ...]`，只增加规格要求的字段：

```python
@dataclass(frozen=True, slots=True)
class DemoServiceRate:
    item_code: str
    name_zh_cn: str
    unit_price: str
    initial_quantity: int
    final_quantity: int
    adjustable: bool
    currency: str
    source_ref: str
    source_version: str
    source_sha256: str

@dataclass(frozen=True, slots=True)
class DemoOfficialFeeSelector:
    source_authority: str
    rate_book_version: str
    rate_book_sha256: str
    fee_codes: tuple[str, ...]
```

固定项要求 `final_quantity == initial_quantity`；唯一可调整目标要求 digest-bound
`final_quantity != initial_quantity`。adjustment 命令虽接收 UI 的 `new_quantity`，但后端必须要求它与
bundle target/final quantity 完全一致，不能让 UI 或 runner 发明价格影响事实。

`CUSTOMER_DEMO` 要求 customer-authorized decision 与 exact digests；`TECHNICAL_REHEARSAL`
允许明显 synthetic fixture，但 readiness 必须不同。不得兼容旧的单行隐式默认；旧 fixture 由测试显式迁移。

为保持已批准的 V5 演示在 Task 03 tuple orchestration 落地前可回归，Task 01 暂时保留既有 V1 schema
解析和 `service_rate`/`amount` 只读适配；它们不参与 V2 runtime contract，也不得为 V2 补默认行、金额
或数量。Task 03 按其 Step 2 删除该适配并迁移既有 V5 consumer。该过渡只解决任务依赖顺序，不扩大产品
行为或保留旧控制页。

- [ ] **Step 4: write RED fresh-run/readiness runner tests, then implement**

在 runner tests 断言：

- CLI 固定新增 `--profile {TECHNICAL_REHEARSAL,CUSTOMER_DEMO}`、`--bundle <absolute-path>`、
  `--expected-manifest-sha256` 和 `--expected-authority-sha256`；customer run 四项均必填，且不能回退
  到测试 helper；
- run root、DB、`-wal`、`-shm` 任一已存在即停止；
- `run.json` 只绑定 run ID、DB absolute path、bundle digest、created_at；
- runner 不逐表删除、不按前缀删除目录；
- synthetic 输入结果为 `TECHNICAL_REHEARSAL_PASS`，customer-authorized 输入才可能 `DEMO_READY`。

先运行针对 runner 的 RED，再只补 preflight 与 CLI contract。保留既有 exact-root guarded cleanup。

- [ ] **Step 5: focused GREEN and lint**

```bash
./scripts/taskctl FPMS-DEMO-V6-RUNTIME-CONTRACT-20260823-01 backend-test test -- -q backend/tests/test_demo_abc_runtime_bundle.py backend/tests/test_demo_integrated_a_runner.py
./scripts/taskctl FPMS-DEMO-V6-RUNTIME-CONTRACT-20260823-01 record lint -- ruff check backend/app/core/demo_bundle.py backend/tests/test_demo_abc_runtime_bundle.py scripts/run_demo_integrated_a_rehearsal.py backend/tests/test_demo_integrated_a_runner.py
git diff --check -- backend/app/core/demo_bundle.py backend/tests/test_demo_abc_runtime_bundle.py scripts/run_demo_integrated_a_rehearsal.py backend/tests/test_demo_integrated_a_runner.py
```

预期：focused tests PASS、Ruff PASS、diff check 空输出。

- [ ] **Step 6: freeze candidate, independent HIGH review, close**

先按标准证据关闭协议冻结以下 commit，再由独立审查者检查：无默认金额、无 production activation、
fresh-run fail closed、readiness 不越权、无宽泛删除。P0/P1/P2 均为 0 后 close：

```bash
git commit -m "feat(demo): define v6 runtime input contract"
```

## Task 02：授权登记官费预览、人工确认与多行 GOV 草单

**Closure:** grant-specific adapter 从 active CNIPA rate book 读取不少于两行候选；preview no-write；一次确认命令原子创建/确认多行 GOV obligation，并准备一张 GOV-only draft。

**Files:**

- Create: `backend/app/modules/grant_fees/demo_official_fee.py`
- Modify: `backend/app/modules/grant_fees/schemas.py`
- Modify: `backend/app/modules/grant_fees/api.py`
- Create: `backend/tests/test_demo_v6_grant_official_fee.py`

**Non-closure:** 不改 `_PROVIDER_SUPPORTED_TRIGGERS`，不改 rate book 审批/激活，不实现费减，不生成 PayList/GovPayment。

- [ ] **Step 1: RED preview tests**

测试 GET preview 只接受目标 grant task、归档授权通知证据、bundle exact selectors 和
`CNIPA/APPROVED/ACTIVE` rate rows。对调用前后 exact identities/counts 比较：
`CaseActivityEvent`、`DemoFinanceCommand`、`FeeObligation`、`FeeObligationLine`、draft links、
`FeeDraft`、`FeeItem`、`PayList`、`GovPayment` 均无新增/变更。
API contract 同时覆盖 `GrantFeeTask.Read` 的 200/401/403、task/evidence 404、source/digest 409 和
path 422；响应必须由声明的 response model 过滤。

```bash
./scripts/taskctl FPMS-DEMO-V6-GOV-OFFICIAL-FEE-20260823-02 backend-test red -- -q backend/tests/test_demo_v6_grant_official_fee.py -k 'preview'
```

- [ ] **Step 2: implement read-only grant adapter**

新增 GET：`/grant-fee-tasks/{task_id}/official-fee-preview`。响应只返回：fee code/name、quantity、
unit price/calculation mode、candidate/full/payable amount、currency、book version/effective dates、
source refs/digests、`preview_digest`。使用查询和 canonical digest，不 flush、不 append activity。

无 active book、selector drift、少于两行、非 CNY、非正金额、证据未归档均返回 409。不得调用或修改
通用 `preview_obligation` provider。

- [ ] **Step 3: RED confirmation/draft tests**

POST confirmation payload 固定为：

```json
{
  "preview_digest": "sha256:...",
  "reviewed_evidence_version_id": "...",
  "expected_content_hash": "sha256:...",
  "confirmed_at": "2026-08-23T10:00:00",
  "idempotency_key": "v6-gov-confirm-01",
  "lines": [
    {"fee_code": "...", "quantity": 1, "confirmed_payable_amount": "..."}
  ]
}
```

测试：exact line set、金额与 preview 一致、人工 actor/evidence、一个多行 GOV obligation、一个 GOV draft、
GOV-only links、首次 201、same replay 200 且返回同对象、`GrantFeeTask.Write` 的 401/403、404、422，
以及 payload drift/重复确认/金额变化 409 且整笔回滚。

- [ ] **Step 4: implement one composite confirmation transaction**

新增 POST：`/grant-fee-tasks/{task_id}/official-fee-confirmation`。在一个事务内：

1. 重算并核对 preview digest；
2. 用现有 `recognize_obligation` 创建完整 GOV line set；
3. 复用现有 grant PAY instruction 与官费人工复核不变量记录人工确认；
4. 调用现有 `prepare_draft` 生成一张 GOV-only draft；
5. 返回 obligation、review activity、draft 及 `reused`。

新模块只编排现有领域服务。若现有服务无法完成规格可观察状态，停止 Task 02 并报告 exact blocker；
未经计划差异审查和用户批准不得扩大 allowlist，尤其不能直接改巨大 `grant_fees/service.py`。

- [ ] **Step 5: focused verification**

```bash
./scripts/taskctl FPMS-DEMO-V6-GOV-OFFICIAL-FEE-20260823-02 backend-test test -- -q backend/tests/test_demo_v6_grant_official_fee.py backend/tests/test_v8_grant_official_fee_manual_review.py backend/tests/test_v8_fee_obligation_prepare_draft.py
./scripts/taskctl FPMS-DEMO-V6-GOV-OFFICIAL-FEE-20260823-02 record lint -- ruff check backend/app/modules/grant_fees/demo_official_fee.py backend/app/modules/grant_fees/schemas.py backend/app/modules/grant_fees/api.py backend/tests/test_demo_v6_grant_official_fee.py
git diff --check -- backend/app/modules/grant_fees/demo_official_fee.py backend/app/modules/grant_fees/schemas.py backend/app/modules/grant_fees/api.py backend/tests/test_demo_v6_grant_official_fee.py
```

- [ ] **Step 6: freeze candidate, independent HIGH review, close**

先冻结下列 candidate；审查者再确认 preview 全表 no-write 证明、人工确认没有被自动计算替代、
GOV 纯度、通用 trigger 未变。

```bash
git add -- backend/app/modules/grant_fees/demo_official_fee.py backend/app/modules/grant_fees/schemas.py backend/app/modules/grant_fees/api.py backend/tests/test_demo_v6_grant_official_fee.py
git commit -m "feat(fees): add grant official fee preview flow"
```

## Task 03：多行 SERVICE obligation 与一次 superseding adjustment

**Closure:** customer-authorized bundle 一次创建多行 SERVICE obligation/draft；OPEN 草单按 bundle final quantity 执行一次专用数量调整并满足 header CAS、relink、replay、rollback；一个正常只读 endpoint 为双轨草单页面提供权威来源事实。

**Files:**

- Modify: `backend/app/modules/fees/demo_service.py`
- Create: `backend/app/modules/fees/demo_v6_source_facts.py`
- Modify: `backend/app/modules/fees/demo_service_schemas.py`
- Modify: `backend/app/modules/fees/api.py`
- Modify: `backend/tests/test_demo_abc_runtime_service_draft.py`
- Create: `backend/tests/test_demo_v6_service_adjustment.py`
- Create: `backend/tests/test_demo_v6_source_facts.py`

**Non-closure:** 不改 FeeObligation/FeeDraft schema，不建立通用价格审计模型，不放宽既有 readers，不允许第二次调整。

- [ ] **Step 1: RED multi-line source snapshot/obligation tests**

单个 source activity snapshot 必须含全部 service rows、manifest/source digests、unit price、quantity、
adjustable flag；单个 recognition 创建一个多行 obligation；单个 prepare 创建一个多行 SERVICE draft。
测试拒绝多次单行 obligation 合并、DEMO_ONLY 写入 ServicePriceBook、bundle drift 和 item mix。

先创建 adjustment/source-facts test files 的最小 contract skeleton，然后一次记录完整 RED tranche：

```bash
./scripts/taskctl FPMS-DEMO-V6-SERVICE-ADJUSTMENT-20260823-03 backend-test red -- -q backend/tests/test_demo_abc_runtime_service_draft.py backend/tests/test_demo_v6_service_adjustment.py backend/tests/test_demo_v6_source_facts.py
```

预期：仅因多行 provider、adjustment 和 source-facts seam 尚不存在而失败。

- [ ] **Step 2: implement tuple-based service orchestration**

把 `DemoServiceItem`/result 改为 item tuple 与 total，不为兼容旧控制页保留隐式 first item。source payload
使用 canonical complete row set；每行 payable = unit price × quantity；一次调用 `recognize_obligation`。

- [ ] **Step 3: RED adjustment transaction tests**

用例必须覆盖：

- fixed item 拒绝；adjustable item 成功且要求中文非空原因；
- 原 obligation/lines 金额不可变；恰好一条 adjustment activity；
- 恰好一个 superseding obligation 和一条 superseding PAY instruction；
- 当前 FeeItems/links 全部切到 superseding lines；
- 原 header 为 `SUPERSEDED/PAY/NOT_CREATED/UNPAID/NOT_APPLICABLE`；
- 新 header 为 `RECOGNIZED/PAY/CREATED/UNPAID/NOT_APPLICABLE`；
- original/superseding/draft 既有 readers 全部通过；
- exact replay identities 不变；payload drift、第二次调整、CAS miss、部分 relink、并发变化返回 409 且零部分写入。
- API 首次 201、replay 200，并覆盖 `Fee.Draft.Edit` 的 401/403、404、409、422。

```bash
./scripts/taskctl FPMS-DEMO-V6-SERVICE-ADJUSTMENT-20260823-03 backend-test red -- -q backend/tests/test_demo_v6_service_adjustment.py
```

- [ ] **Step 4: implement the exact seven-step adjustment**

新增 POST：`/fees/drafts/{draft_id}/demo-service-adjustment`，payload 只含
`item_id`、`expected_quantity`、`new_quantity`、`reason`、`idempotency_key`。actor 取当前用户，source rows
从持久化 snapshot 读取，不从前端接受 unit price/source truth；`new_quantity` 必须等于 exact
digest-bound bundle target 的 `final_quantity`，否则 409。

严格按规格 8.1.1 顺序在一个事务内执行 activity → superseding obligation → PAY instruction →
item update → exact relink → two header CAS → existing reader validation。不要抽出新通用框架。

- [ ] **Step 5: add the minimal authoritative normal-page read seam**

先在 `test_demo_v6_source_facts.py` 写 RED，再新增
`GET /fees/drafts/{draft_id}/source-facts`。response model 固定为：draft id/status/domain；每行 current
item/obligation-line IDs、fee code/name、quantity、unit price、amount；source authority/ref/version/
effective date/digest/activation；`adjustable`；以及可选 adjustment activity id/reason/before digest/after
digest。GOV 信息从 active rate binding + confirmed obligation lineage 读取；SERVICE 信息从持久化 bundle
source activity + current superseding links 读取。不得从 request、前端缓存或 hidden command response 补真值。

测试 GOV/SERVICE、OPEN/LOCKED、调整前后、original/superseding links、404、stored-lineage 409，以及
`Fee.Draft.Read` 的 401/403。该 endpoint 是正常业务 read model，不执行 mutation。

- [ ] **Step 6: focused verification**

```bash
./scripts/taskctl FPMS-DEMO-V6-SERVICE-ADJUSTMENT-20260823-03 backend-test test -- -q backend/tests/test_demo_abc_runtime_service_draft.py backend/tests/test_demo_v6_service_adjustment.py backend/tests/test_demo_v6_source_facts.py backend/tests/test_v8_service_receivable_obligation.py backend/tests/test_v8_fee_obligation_prepare_draft.py
./scripts/taskctl FPMS-DEMO-V6-SERVICE-ADJUSTMENT-20260823-03 record lint -- ruff check backend/app/modules/fees/demo_service.py backend/app/modules/fees/demo_v6_source_facts.py backend/app/modules/fees/demo_service_schemas.py backend/app/modules/fees/api.py backend/tests/test_demo_abc_runtime_service_draft.py backend/tests/test_demo_v6_service_adjustment.py backend/tests/test_demo_v6_source_facts.py
git diff --check -- backend/app/modules/fees/demo_service.py backend/app/modules/fees/demo_v6_source_facts.py backend/app/modules/fees/demo_service_schemas.py backend/app/modules/fees/api.py backend/tests/test_demo_abc_runtime_service_draft.py backend/tests/test_demo_v6_service_adjustment.py backend/tests/test_demo_v6_source_facts.py
```

- [ ] **Step 7: freeze candidate, independent HIGH review, close**

先冻结下列 candidate；审查重点是事务原子性、immutable history、exact relink、header CAS、
权威 source-facts 和无全局 reader relaxation。

```bash
git add -- backend/app/modules/fees/demo_service.py backend/app/modules/fees/demo_v6_source_facts.py backend/app/modules/fees/demo_service_schemas.py backend/app/modules/fees/api.py backend/tests/test_demo_abc_runtime_service_draft.py backend/tests/test_demo_v6_service_adjustment.py backend/tests/test_demo_v6_source_facts.py
git commit -m "feat(fees): add traceable service draft adjustment"
```

## Task 04：GovPayment 可恢复登记与两次回款核销

**Closure:** GOV draft → PayList 后，每行 GovPayment 有幂等 command carrier 和待凭证核验表达；SERVICE bill 支持两笔回款、两次对应核销，从 UNSETTLED → PARTIALLY_SETTLED → SETTLED。

**Files:**

- Modify: `backend/app/modules/billing/schemas.py`
- Modify: `backend/app/modules/billing/service.py`
- Modify: `backend/app/modules/billing/api.py`
- Modify: `backend/tests/test_demo_abc_payment_offset.py`
- Create: `backend/tests/test_demo_v6_gov_payment.py`

**Non-closure:** 不改 GovPayment 数据表，不增加官方凭证，不实现真实支付、撤销核销或坏账。

- [ ] **Step 1: RED GovPayment wrapper tests**

operation 固定为 `GOV_PAYMENT`。测试每个 GOV fee item 一个 key；payload 包含 exact
pay_list/fee_item/date/amount 和所有官方凭证字段为 null；same replay 返回同 GovPayment；drift 409；
commit-then-drop 后 GET `/gov-payments/idempotency/{key}` 恢复；SERVICE item/错误 PayList/金额不等均拒绝。
POST 固定为 `/gov-payments/demo-command`，POST/GET 均复用 `GovPayment.Create`，不得新增权限码；覆盖
首次 201、replay 200、pending 202、无 token 401、缺权限 403、缺对象/command 404、drift 409、validation 422。

在两个 finance test files 写完 contract 后记录一次完整 RED：

```bash
./scripts/taskctl FPMS-DEMO-V6-FINANCE-20260823-04 backend-test red -- -q backend/tests/test_demo_v6_gov_payment.py backend/tests/test_demo_abc_payment_offset.py
```

预期：仅因 GovPayment wrapper 和两次 partial allocation 尚未实现而失败。

- [ ] **Step 2: implement thin command wrapper**

在 billing 层复用 `DemoFinanceCommand` 与正常 `register_gov_payment`，不复制 official payment 领域逻辑，
不新增表。响应增加 `reused` 和固定事实状态 `REGISTERED_PENDING_OFFICIAL_EVIDENCE`；不得返回
`OFFICIAL_PAYMENT_SUCCEEDED`。

- [ ] **Step 3: RED partial receipt/offset tests**

将既有单笔全额测试改成规格闭环：

```python
assert Decimal("0") < first_amount < bill.total_amount
assert bill_after_first_receipt.status == "UNSETTLED"
assert bill_after_first_offset.status == "PARTIALLY_SETTLED"
assert second_amount == bill_after_first_offset.balance_amount
assert bill_after_second_offset.status == "SETTLED"
assert bill_after_second_offset.balance_amount == Decimal("0.00")
```

断言恰好 2 Payments、2 active Offsets；每笔回款 fully allocated；多 item bill 分配正确；exact replay 不增计数；
first amount 非法、second 缓存金额 drift、第三笔回款、跨 bill/item 均 fail closed。

- [ ] **Step 4: minimally generalize demo wrappers using existing finance semantics**

保留现有请求中的 explicit amount/offset amount。移除“恰好一 BillItem、必须一次全额”的 demo-only 限制，
改为调用既有部分核销分配逻辑和权威 bill balance；第一次完成后 PARTIALLY_SETTLED，第二次金额只从服务端
剩余余额计算。不要改 generic finance behavior。

- [ ] **Step 5: focused verification**

```bash
./scripts/taskctl FPMS-DEMO-V6-FINANCE-20260823-04 backend-test test -- -q backend/tests/test_demo_v6_gov_payment.py backend/tests/test_demo_abc_payment_offset.py backend/tests/test_payment_offset_case_receipt_readiness.py backend/tests/test_v8_gov_payment_activity_adapter.py
./scripts/taskctl FPMS-DEMO-V6-FINANCE-20260823-04 record lint -- ruff check backend/app/modules/billing/schemas.py backend/app/modules/billing/service.py backend/app/modules/billing/api.py backend/tests/test_demo_v6_gov_payment.py backend/tests/test_demo_abc_payment_offset.py
git diff --check -- backend/app/modules/billing/schemas.py backend/app/modules/billing/service.py backend/app/modules/billing/api.py backend/tests/test_demo_v6_gov_payment.py backend/tests/test_demo_abc_payment_offset.py
```

- [ ] **Step 6: freeze candidate, independent HIGH review, close**

先冻结下列 candidate；审查者再核对 Payment ≠ Offset、无凭证 GovPayment 的事实文案、
两次金额等式及幂等恢复。

```bash
git add -- backend/app/modules/billing/schemas.py backend/app/modules/billing/service.py backend/app/modules/billing/api.py backend/tests/test_demo_abc_payment_offset.py backend/tests/test_demo_v6_gov_payment.py
git commit -m "feat(demo): support recoverable dual-track settlement"
```

## Task 05：客户可见正常业务页面

**Closure:** 客户只在正常业务页面看到官费来源与只读行、SERVICE 一次调整、待凭证核验、部分/完全结清和同案双轨汇总；ABC 控制页仍隐藏。

**Files:**

- Modify: `frontend/src/api/grantFees.ts`
- Modify: `frontend/src/api/grantFees.types.ts`
- Modify: `frontend/src/api/fees.ts`
- Modify: `frontend/src/api/fees.types.ts`
- Modify: `frontend/src/api/govPayments.ts`
- Modify: `frontend/src/api/govPayments.types.ts`
- Modify: `frontend/src/api/billing.ts`
- Modify: `frontend/src/api/billing.types.ts`
- Modify: `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`
- Modify: `frontend/src/modules/fees/pages/FeeDraftDetail.vue`
- Modify: `frontend/src/modules/fees/components/FeeDraftItemsTable.vue`
- Modify: `frontend/src/modules/annuity/pages/PayListDetail.vue`
- Modify: `frontend/src/modules/annuity/pages/GovPaymentCreate.vue`
- Modify: `frontend/src/modules/billing/pages/BillDetail.vue`
- Modify: `frontend/src/modules/billing/pages/PaymentList.vue`
- Modify: `frontend/src/modules/billing/pages/OffsetList.vue`
- Modify: `frontend/src/modules/cases/components/FeeObligationLane.vue`
- Modify: `frontend/src/modules/demo/demo.api.ts`
- Modify: `frontend/src/modules/demo/command-reconcile.ts`
- Create: `backend/tests/test_demo_v6_fee_ui_contract.py`

**Non-closure:** 不增加“客户决策”面板，不把 ABC 控制页加入导航，不清理未触及页面的遗留英文。

- [ ] **Step 1: write and record the exact UI contract RED**

冻结前端只消费后端权威字段：preview/source digest、fee domain、adjustable、adjustment state、
GovPayment evidence state、bill balance/settlement status。禁止在前端推导第二笔金额或把未知状态映射为成功。
新增 `backend/tests/test_demo_v6_fee_ui_contract.py`，以只读 source/static contract 断言：GOV 无编辑 action；SERVICE
adjustment 只能发 exact item/new quantity/reason/key；所有来源字段来自 `/source-facts` mapper；pending evidence、
PARTIALLY_SETTLED、SETTLED 均有中文映射；客户页面/导航不含 ABC 或“客户决策”。

```bash
./scripts/taskctl FPMS-DEMO-V6-CUSTOMER-UI-20260823-05 backend-test red -- -q backend/tests/test_demo_v6_fee_ui_contract.py
```

预期：仅因 V6 mapper/actions/labels 尚未存在而非零；基础设施/语法错误不算 RED。

- [ ] **Step 2: grant preview and draft source panel**

授权费用页显示不少于两行只读 preview 和“候选预览，尚未形成缴费义务”。确认提交逐行金额后导航正常 GOV
草单。草单“计算与来源”区域显示 code/version/effective date/ref/digest/activation。

- [ ] **Step 3: enforce GOV/SERVICE edit boundary**

`FeeDraftItemsTable.vue` 根据权威 domain 和 draft status：

- GOV：OPEN/LOCKED 都不显示编辑/删除；
- SERVICE OPEN：只有 adjustable item 显示“调整数量”；要求中文原因；成功刷新整个 draft；
- SERVICE LOCKED：全部只读；
- 不使用 generic item update 伪造 audit trail。

- [ ] **Step 4: finance facts and same-case summary**

PayList/GovPayment 页显示“已登记，待官方凭证核验”；Bill 页面先显示“部分结清”和余额，再显示“已结清”；
Payment/Offset 保持不同对象和状态。案件费用 lane 分栏显示 GOV 应缴/清单/登记与 SERVICE 应收/回款/核销/余额。
所有新增文案为简体中文，中央主线不出现新英文状态。

- [ ] **Step 5: preserve hidden command reconciliation**

`demo.api.ts` 只作为主持人控制客户端，调用正常领域 endpoints；每次 transport failure 先 GET idempotency 状态，
已完成则恢复同一对象，未完成才重试。不要将 ABC 控制页链接加入客户导航或 runbook 客户共享屏幕。

- [ ] **Step 6: focused frontend verification**

```bash
npm --prefix frontend run typecheck
npm --prefix frontend exec -- eslint --config frontend/eslint.config.js frontend/src/api/grantFees.ts frontend/src/api/grantFees.types.ts frontend/src/api/fees.ts frontend/src/api/fees.types.ts frontend/src/api/govPayments.ts frontend/src/api/govPayments.types.ts frontend/src/api/billing.ts frontend/src/api/billing.types.ts frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue frontend/src/modules/fees/pages/FeeDraftDetail.vue frontend/src/modules/fees/components/FeeDraftItemsTable.vue frontend/src/modules/annuity/pages/PayListDetail.vue frontend/src/modules/annuity/pages/GovPaymentCreate.vue frontend/src/modules/billing/pages/BillDetail.vue frontend/src/modules/billing/pages/PaymentList.vue frontend/src/modules/billing/pages/OffsetList.vue frontend/src/modules/cases/components/FeeObligationLane.vue frontend/src/modules/demo/demo.api.ts frontend/src/modules/demo/command-reconcile.ts
./scripts/taskctl FPMS-DEMO-V6-CUSTOMER-UI-20260823-05 backend-test test -- -q backend/tests/test_demo_v6_fee_ui_contract.py
./scripts/taskctl FPMS-DEMO-V6-CUSTOMER-UI-20260823-05 record lint -- ruff check backend/tests/test_demo_v6_fee_ui_contract.py
git diff --check -- frontend/src backend/tests/test_demo_v6_fee_ui_contract.py
```

预期：typecheck PASS、exact ESLint PASS、diff check 空输出。

- [ ] **Step 7: freeze candidate, independent UI/fact-boundary review, close**

先冻结下列 candidate；审查者再以客户共享屏幕逐页确认：ABC 不可见、无“客户决策”、
无 GOV 编辑入口、无英文新增状态、无支付事实夸大。

```bash
git add -- frontend/src/api/grantFees.ts frontend/src/api/grantFees.types.ts frontend/src/api/fees.ts frontend/src/api/fees.types.ts frontend/src/api/govPayments.ts frontend/src/api/govPayments.types.ts frontend/src/api/billing.ts frontend/src/api/billing.types.ts frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue frontend/src/modules/fees/pages/FeeDraftDetail.vue frontend/src/modules/fees/components/FeeDraftItemsTable.vue frontend/src/modules/annuity/pages/PayListDetail.vue frontend/src/modules/annuity/pages/GovPaymentCreate.vue frontend/src/modules/billing/pages/BillDetail.vue frontend/src/modules/billing/pages/PaymentList.vue frontend/src/modules/billing/pages/OffsetList.vue frontend/src/modules/cases/components/FeeObligationLane.vue frontend/src/modules/demo/demo.api.ts frontend/src/modules/demo/command-reconcile.ts backend/tests/test_demo_v6_fee_ui_contract.py
git commit -m "feat(ui): present v6 dual-track fee lifecycle"
```

## Task 06：Canonical live E2E、V6 lifecycle 与完整 runbook

**Closure:** runner 从阶段 01 执行到 11；live-backend E2E 通过正常页面验证每一阶段；V6 lifecycle 和 runbook 与实际编排逐项一致并突出最近数周成果。

**Files:**

- Modify: `scripts/run_demo_integrated_a_rehearsal.py`
- Modify: `backend/tests/test_demo_integrated_a_runner.py`
- Create: `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-v6.live-backend.spec.ts`
- Create: `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-v6-static-contract.mjs`
- Create: `scripts/check_customer_demo_lifecycle_v6.py`
- Create: `docs/postdemo/demo-lifecycle-customer-v6.html`
- Create: `docs/postdemo/demo-lifecycle-customer-v6-runbook.md`

**Non-closure:** 不重写 V5，不将 Playwright 变成通用测试框架，不把 synthetic fixture 描述为客户数据。

- [ ] **Step 1: write static RED orchestration contract**

static contract 固定阶段 01–06 与 V5 一致，并要求阶段 07–11 精确为：

1. active official fee preview；
2. GOV/SERVICE 草单、一次 SERVICE adjustment、两草单锁定；
3. PayList + per-line GovPayment pending evidence；
4. SERVICE Bill + first receipt/offset + second receipt/offset；
5. same-case dual-track summary。

```bash
./scripts/taskctl FPMS-DEMO-V6-CANONICAL-E2E-20260823-06 backend-test red -- -q backend/tests/test_demo_integrated_a_runner.py -k 'v6_contract'
```

预期：仅因 V6 stage table/runner/docs 尚不存在而失败。

- [ ] **Step 2: extend runner only with the new tail**

runner 的每个 mutation 使用独立 idempotency key，commit 后按 key 读取持久状态。第二笔回款金额在第一笔核销后读取
bill authoritative balance。输出 `run.json`、阶段结果、object identities/counts、amount equations、readiness 和 stop reason。
V5 01–06 function calls不重构。

- [ ] **Step 3: write live E2E with normal-page assertions**

E2E 从新的 isolated run 开始；控制 API 只在非共享 setup/advance 中使用。每阶段在正常业务页刷新并断言：

- URL 与页面标题是客户业务页；
- 输入、屏幕输出与权威 GET 一致；
- GOV/SERVICE 纯度、数量、金额、状态和来源；
- first-load network/console 无错误；
- replay 前后 identities/counts 不变；
- 最终所有规格金额等式成立。

同一 runner test file 还要新增 `test_v6_customer_acceptance_receipts`：只读
`FPMS_DEMO_V6_CUSTOMER_EVIDENCE_DIR` 指向的完成 evidence，校验 `--runs 2` 的不同 run IDs/DBs、相同 input
digests、两个 PASS receipts、network/console 与金额等式。缺 env、缺文件或任一 receipt 不完整必须失败；
该测试不启动或重跑 demo。

- [ ] **Step 4: author lifecycle and runbook from the same stage table**

V6 HTML 与 Markdown runbook 每一步都包含：演示话术、UI/操作、输入、屏幕输出、期待结果、验证方法、事实边界、
停止条件。用“最近新增”标记：runtime 来源门禁、官费多行预览、GOV/SERVICE 双草单、一次可追溯调整、
GovPayment 待核验、两次回款核销、同案汇总、fresh-run 与 network preflight。

不要使用 `DEMO-CASE-xxx`；测试身份模拟真实客户/案件格式，并在技术 fixture 中保留合成数据免责声明。

- [ ] **Step 5: focused verification**

```bash
./scripts/taskctl FPMS-DEMO-V6-CANONICAL-E2E-20260823-06 backend-test test -- -q backend/tests/test_demo_integrated_a_runner.py
./scripts/taskctl FPMS-DEMO-V6-CANONICAL-E2E-20260823-06 record lint -- ruff check scripts/run_demo_integrated_a_rehearsal.py scripts/check_customer_demo_lifecycle_v6.py backend/tests/test_demo_integrated_a_runner.py
backend/.venv/bin/python scripts/check_customer_demo_lifecycle_v6.py
python3 FPMS_Automation_Skeleton_Pack/scripts/validate_assets.py
node FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-v6-static-contract.mjs
backend/.venv/bin/python scripts/run_demo_integrated_a_rehearsal.py --profile TECHNICAL_REHEARSAL --runs 1 --headless --artifact artifacts/FPMS-DEMO-V6-CANONICAL-E2E-20260823-06/rehearsal
git diff --check -- scripts/run_demo_integrated_a_rehearsal.py backend/tests/test_demo_integrated_a_runner.py FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-v6.live-backend.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-v6-static-contract.mjs scripts/check_customer_demo_lifecycle_v6.py docs/postdemo/demo-lifecycle-customer-v6.html docs/postdemo/demo-lifecycle-customer-v6-runbook.md
```

预期：受控 focused pytest/lint 和必需诊断 doc checker、asset validation、static contract、单条 live E2E
全部 PASS。raw diagnostics 不替代 canonical `test`/`lint` evidence。

- [ ] **Step 6: freeze candidate, independent runbook/E2E review, close**

先冻结下列 candidate；独立审查再逐阶段核对 runbook、HTML、runner 与 E2E 的同一顺序和事实边界，
确认没有隐藏控制页出现在客户路线。

```bash
git add -- scripts/run_demo_integrated_a_rehearsal.py backend/tests/test_demo_integrated_a_runner.py FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-v6.live-backend.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-v6-static-contract.mjs scripts/check_customer_demo_lifecycle_v6.py docs/postdemo/demo-lifecycle-customer-v6.html docs/postdemo/demo-lifecycle-customer-v6-runbook.md
git commit -m "test(demo): add canonical v6 customer rehearsal"
```

## Task 07：连续两次新 run 与客户 readiness 最终验收

**Closure:** 使用 customer-authorized runtime 输入连续两次执行完整 V6；两个不同 run root/DB 均通过；独立 reviewer 对最终费用事实和证据给出零发现。

**Files:**

- Create: `docs/postdemo/demo-v6-customer-readiness-report.md`
- Evidence-only outputs under: `artifacts/FPMS-DEMO-V6-CUSTOMER-ACCEPTANCE-20260823-07/`

**Non-closure:** 本任务不修产品代码、不部署、不发布；任何失败退回原 owner/task，不在验收任务内热修。

- [ ] **Step 1: bind final inputs and clean starting state**

记录 HEAD、spec/plan/bundle/authority/rate-book/service-source digests。验证两个 planned run IDs 不存在对应 DB、WAL、SHM、
run root。不得删除旧业务 DB 来制造干净状态。

Task 07 只有在 task file 中写入并审查以下 literal（无 shell placeholder）后才能 `taskctl start`：

- customer bundle absolute path；
- expected manifest SHA-256；
- expected authority-decision SHA-256；
- evidence artifact absolute/仓库相对 path。

任一 literal 未提供时保持 `DEMO_INPUT_REQUIRED`，不 materialize 本 task。

- [ ] **Step 2: run customer rehearsal #1**

使用 runner 的 customer profile 和 task file 中的 exact literals 执行 `--runs 2` 的第一 ordinal。runner
内部 single-worker 执行 canonical live E2E，并保存 backend/frontend logs、network、console、screenshots、
object IDs/counts、amount equations、readiness 和 run root manifest。

- [ ] **Step 3: run customer rehearsal #2 from another fresh root**

同一个 `--runs 2` invocation 必须为第二 ordinal 自动生成不同 run ID/run root/SQLite，其他 approved inputs
digest 完全一致；不复用第一轮数据库或业务对象。Task file 中冻结的 canonical command shape 为：

```bash
backend/.venv/bin/python scripts/run_demo_integrated_a_rehearsal.py --profile CUSTOMER_DEMO --bundle LITERAL_APPROVED_ABSOLUTE_BUNDLE_PATH --expected-manifest-sha256 LITERAL_64_HEX_MANIFEST --expected-authority-sha256 LITERAL_64_HEX_AUTHORITY --runs 2 --headless --artifact artifacts/FPMS-DEMO-V6-CUSTOMER-ACCEPTANCE-20260823-07/runs
FPMS_DEMO_V6_CUSTOMER_EVIDENCE_DIR=artifacts/FPMS-DEMO-V6-CUSTOMER-ACCEPTANCE-20260823-07/runs ./scripts/taskctl FPMS-DEMO-V6-CUSTOMER-ACCEPTANCE-20260823-07 backend-test test -- -q backend/tests/test_demo_integrated_a_runner.py -k 'v6_customer_acceptance_receipts'
```

`LITERAL_*` 仅用于本计划表示 materialization slot；实际 task file/command 必须替换为获批 literal，且
`rg 'LITERAL_' <task-file>` 零结果后才允许 start。

- [ ] **Step 4: compare two receipts**

两次均必须满足：

- 无首次加载 `Network Error`、console error 或失败请求；
- 阶段 01–11 顺序相同，业务 identities 不同；
- source/input digests 相同；
- GOV total = PayList total = GovPayment total；
- SERVICE superseding total = draft total = Bill total；
- 2 Payments = 2 active Offsets = Bill total，最终 balance = 0；
- 官费不进入 Bill，服务费不进入 PayList；
- 客户页面无 ABC、无“客户决策”、无新增英文状态。

- [ ] **Step 5: exact final close-point checks**

只有在两次 rehearsal 均通过后运行以下 exact checks；当前 manifest 没有另列 product-full 或 release 命令，
因此不发明 repo-wide backend pytest、broad Playwright 或 release gate：

```bash
git diff --check
npm --prefix frontend run typecheck
npm --prefix frontend run lint
python3 FPMS_Automation_Skeleton_Pack/scripts/validate_assets.py
node FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-v6-static-contract.mjs
./scripts/taskctl FPMS-DEMO-V6-CUSTOMER-ACCEPTANCE-20260823-07 record lint -- git diff --check -- docs/postdemo/demo-v6-customer-readiness-report.md
```

- [ ] **Step 6: freeze readiness report, independent final review, close**

最终 reviewer 绑定 current hashes 与两个 run receipts，必须 P0/P1/P2 = 0。报告只能给出以下之一：

- `DEMO_READY`：customer-authorized SERVICE + active CNIPA GOV inputs 且两次通过；
- `TECHNICAL_REHEARSAL_PASS / DEMO_INPUT_REQUIRED`：实现与 synthetic rehearsal 通过但 customer inputs 缺失；
- `NOT_READY`：任一事实、网络、幂等、隔离或证据门禁失败。

先写 readiness report 并冻结以下 candidate，再执行标准 review/close；reviewer 直接检查两个 run receipts，
不能只相信报告摘要：

```bash
git add -- docs/postdemo/demo-v6-customer-readiness-report.md
git commit -m "docs(demo): record v6 customer readiness"
```

## 7. 失败恢复与停止协议

任一 task 出现 transport failure：先 GET idempotency state 和权威对象；已完成则恢复同一 object IDs，未完成才重试一次。
不得重复已持久化步骤，不得换 key 逃避 conflict。

立即停止受影响任务的条件：

- Gate 0 不再 PASS、manifest/digest 变化或 task allowlist 不准确；
- runtime source 未授权/未激活、digest drift、金额或币种不合法；
- preview 产生任一 mutation；
- GOV/SERVICE 串线或 locked draft 可编辑；
- SERVICE adjustment 出现部分写入、第二次调整或 reader relaxation；
- Payment 未核销却改变 settlement，或金额等式不成立；
- GovPayment 被表达为官方支付成功；
- first-load `Network Error`；
- 新 run DB/root 已存在；
- 实现需要触碰 non-closure 文件或引入新 schema/table/general rule engine。

恢复从第一个未完成 ordinal 开始；已完成 task 只作为 accepted dependency，不重做 brainstorm、设计或 broad verification。

## 8. Definition of Done

只有同时满足以下条件，才可向用户报告本轮“全部完成”：

- Tasks 01–07 全部按当前治理协议 close；
- 每个 HIGH task 有非实现者零发现审查；
- final spec、plan、task、code、runtime input 和两次 run evidence hashes 完整绑定；
- 两次 customer-authorized fresh-run canonical demo 全部通过；
- 正常客户页面完成阶段 01–11，且 runbook/HTML/E2E 编排一致；
- 无首次加载网络错误；所有双轨纯度、幂等、来源和金额等式成立；
- 最终 readiness 明确为 `DEMO_READY`；
- deploy、push、release 不在本计划 closure 内，需用户另行授权并且 release 永远最后。
