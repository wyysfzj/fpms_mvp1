# FPMS Demo V6 runtime 官费来源最小架构整改

日期：2026-08-25
状态：待独立审查与用户书面确认
风险：HIGH（官费来源、runtime input、fresh-run 数据物化）

## 1. 结论

V6 的 `official_fee_selector` 只能选择并校验数据库中已经存在的官费行；全新 Demo 数据库却不含
`OfficialRateBook/FeeRate`。因此阶段 07 在正确地失败关闭，而不是金额算法出错。

最小整改是在现有 V6 manifest 内新增一个 `official_fee_source` 对象，携带 exactly one 完整费率簿
快照及 selector 选中的 exact fee rows。manifest、authority decision 和既有 expected digest 门禁
继续绑定整个输入。loader 在启动前验证来源对象及其摘要；fresh-run runner 只把已验证快照原样写入
现有表；之后仍由既有 grant preview 读取并计算。没有第二套费率真值或计算路径。

## 2. 已选择的合同

### 2.1 `official_fee_source.rate_book`

必须完整提供现有 `OfficialRateBook` 所需的来源事实：

- `book_code`、`version_code`、`source_authority`；
- `source_reference`、`source_version`、`source_published_on`；
- `source_snapshot` 与其 SHA-256 `source_snapshot_hash`；
- `effective_from`、可空 `effective_to`。

runtime 合同不接受 `approval_status`、`activation_status`、actor ID 或时间作为可覆盖输入。
loader 通过全部 authority 门禁后，fresh-run 先以 `PENDING/INACTIVE` 创建 candidate，再调用现有
`activate_official_rate_book` 完成系统内审批和激活，不直接写 active tuple。`approved_at` 使用
authority record 已绑定的 aware 时间转换为 Asia/Shanghai naive wall time；启动时钟早于该时间则
失败。`activated_at` 是实际 bootstrap action 的 Asia/Shanghai naive wall time；existing service
负责 actor 有效性、可信 CNIPA URL、canonical snapshot、区间冲突和
`current_identity_key=CNIPA|book_code`。

本地 reviewer 用户只是系统内 approval/activation FK actor，不被描述为外部官方发布者。来源权威
仍由 `source_authority/source_reference/source_snapshot` 表达。本设计按用户 2026-08-25 的明确批准，
仅在 isolated local Demo bootstrap 内窄幅替代 V6 §6.4“只消费事先存在的激活版本”；不改变生产或
共享数据库的审批/激活规则，也不允许绕过 existing activation service。

### 2.2 `official_fee_source.rows`

每一行完整携带既有 `FPMS_DEMO_RATE_ROW_DIGEST_V1` 所覆盖的字段：

- `fee_code`、`fee_name`、`fee_type=GOV`、`currency=CNY`、`default_amount`、`enabled=true`；
- 可空分类字段、`calc_mode`、`calc_params`、`allow_reduction`；
- `effective_from/effective_to`；
- `source_doc/source_url/source_policy/source_version/source_status=ACTIVE`。

只允许 selector 中列出的 exact rows，不允许额外费率行。row digest 继续使用既有 canonical payload；
loader 和 preview 必须调用同一个公开的 digest helper，避免两套摘要实现。

### 2.3 selector 交叉绑定

loader 必须在任何数据库写入之前验证：

- source authority、book version、snapshot hash 分别等于 selector 的 authority、version、book digest；
- selector fee-code 集合与 source rows 集合完全相等，顺序按 selector 固定；
- 每行 canonical digest 等于 selector 对应的 row digest；
- 金额严格为正、币种为 CNY；
- 行与簿必须覆盖 bundle 中 canonical replacement grant notice 的 `official_due_date`；loader
  同时固定该日期，后续授权任务的 `due_date` 必须精确相等，不能改用 Demo local date；
- 行的 source version/reference 与费率簿一致，不存在未知字段或重复 code；
- authority 文件中的既有 source-digest ledger 与上述 book/rows 一致。

任一不一致抛出 bundle preflight error；不得启动服务、建案件或写入部分费率事实。

## 3. Fresh-run 物化

迁移、既有 60 行通知目录、OA 模板和两个 Demo 身份初始化后，在同一 fresh database bootstrap
事务内执行一次专用物化函数：

1. 读取 loader 已冻结的 immutable snapshot，不重新解析原文件；
2. 使用 snapshot 中的 exact source fields 创建一条 `PENDING/INACTIVE` `OfficialRateBook`
   candidate；
3. 使用 exact row fields 创建所选 `FeeRate`，并绑定新 book ID；
4. 使用配置的 reviewer 用户和已定义时间调用现有 `activate_official_rate_book`；
5. flush 后验证 active tuple/current identity，重新计算 book snapshot hash 与每个 row digest；任一
   不一致回滚整个 bootstrap 事务；
6. 创建授权任务时必须断言 task `due_date` 等于 loader 绑定的 replacement grant notice
   `official_due_date`；
7. 提交后阶段 07 继续调用现有只读 preview，不接受 runner 传入金额。

这是 isolated Demo run 的 runtime materialization，不是全局种子或生产激活。全新数据库以外如出现
同 identity 的既有簿/行或任何冲突，立即失败，不做 upsert、覆盖或静默复用。

## 4. 来源与客户边界

- `SYNTHETIC_TEST_ONLY` 只表示 bundle decision、服务价格和案件证据可为合成。其官费 source 仍须
  满足 existing activation service 的可信 CNIPA URL 与 canonical snapshot 合同。自动化测试可以
  使用 structurally valid local fixture 验证门禁，但该 fixture 不证明内容真实、不得进入
  `CUSTOMER_DEMO` profile、不得用于面对客户的 headed 画面，也不得得到 `DEMO_READY`。
- `CUSTOMER_AUTHORIZED` bundle 必须按现有 decision contract 绑定 exact manifest、book digest 和
  row digests；缺 decision 或 digest 不一致时保持 `DEMO_INPUT_REQUIRED`。
- 本整改不会自动生成 customer-authorized bundle，也不会把技术测试 fixture 升格为客户输入。
- 客户 Demo 的具体模板、费用及来源仍是之后的 runtime input；没有获批输入就不演示金额。

## 5. 失败和停止条件

下列任一条件在服务启动前停止：缺 source、未知/缺失字段、snapshot hash 错误、selector/source 不等、
row digest 错误、非 GOV、非 CNY、金额非正、未覆盖 canonical task due date、来源版本冲突、
authority decision 不匹配、approved time 在未来。

物化时若 actor 缺失、数据库非 fresh、唯一键冲突、写后摘要不同或事务异常，回滚并停止。不得降级到
占位费率、硬编码金额、测试内隐式 seed、网络抓取、直接写 active tuple 或跳过阶段 07。

## 6. 最小实现边界

后续实现任务只允许按需修改：

- `backend/app/core/demo_bundle.py`：immutable source 类型、严格解析、低层纯 row-digest helper 和
  digest/official-due-date 交叉校验；
- `backend/app/modules/grant_fees/demo_official_fee.py`：只改为导入 core 的 row-digest helper，preview
  语义不变；core 不得反向导入 grant/fee module；
- `backend/scripts/run_local_demo_abc.py`：fresh-run 专用物化；
- `backend/tests/test_demo_abc_runtime_bundle.py`：完整 synthetic source fixture 与负例；
- `backend/tests/test_demo_abc_local_runner.py`：fresh DB 物化、actor、摘要和冲突回滚；
- `backend/tests/test_demo_v6_grant_official_fee.py`：仅把受新 loader 合同影响的私有 source fixture
  改成同一 canonical source shape；保留其 preview 私有数据库 seed 和业务测试职责。

不新增数据库表/迁移、runtime bundle 文件、API、页面或通用导入模块。
`backend/tests/test_demo_integrated_a_runner.py` 和现有 preview/activation suites 只运行验证，不在写入
allowlist。

## 7. 验收

实现必须 test-first，并依次证明：

1. bundle loader 正例和上述失败关闭负例；
2. fresh-run 只物化一簿两行，字段与摘要完全相等；
3. 既有 grant preview 与 activation suites 继续通过，且 runtime loader/runner 测试证明
   materialized source 可被现有 preview 消费；
4. scoped Ruff 与 exact diff check；
5. canonical V6 rehearsal 从阶段 01 到 11 单次通过；
6. 同一冻结 candidate 再执行一次 fresh run，两个 run/DB/业务 identity 不同而 source digests 相同；
7. 独立 HIGH review 对费用事实、来源边界和 exact diff 报告 P0/P1/P2 = 0/0/0。

失败 evidence 保留为诊断记录，不改写为 PASS。通过前不得声称 Demo ready。

## 8. 被拒绝的扩展

- 独立 JSON rate-book asset：manifest 内联对象已经被 manifest digest 完整绑定，额外文件只增加同步面。
- 通用 importer/service：当前只有 fresh local Demo 的一簿两行闭环，没有第二消费者。
- runner 硬编码或测试 seed：会绕过 runtime authority，正是本次缺陷。
- 让 preview 直接读取 manifest 金额：会形成第二计算路径并绕过现有 activated-rate-book 规则。
