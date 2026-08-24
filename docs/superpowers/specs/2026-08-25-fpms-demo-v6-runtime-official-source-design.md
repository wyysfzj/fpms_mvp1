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
通过所有 authority 门禁后，fresh-run 才以固定 `APPROVED/ACTIVE` 状态物化；本地 reviewer 用户仅是
系统内审批/激活动作的 FK actor，不被描述为外部官方发布者。来源权威仍由
`source_authority/source_reference/source_snapshot` 表达。

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
- 金额严格为正、币种为 CNY、行与簿在 Demo local date 生效；
- 行的 source version/reference 与费率簿一致，不存在未知字段或重复 code；
- authority 文件中的既有 source-digest ledger 与上述 book/rows 一致。

任一不一致抛出 bundle preflight error；不得启动服务、建案件或写入部分费率事实。

## 3. Fresh-run 物化

迁移、既有 60 行通知目录、OA 模板和两个 Demo 身份初始化后，在同一 fresh database bootstrap
事务内执行一次专用物化函数：

1. 读取 loader 已冻结的 immutable snapshot，不重新解析原文件；
2. 使用 snapshot 中的 exact source fields 创建一条 `OfficialRateBook`；
3. 使用 exact row fields 创建所选 `FeeRate`，并绑定新 book ID；
4. 使用配置的 reviewer 用户作为本地 approval/activation actor；
5. flush 后重新计算 book snapshot hash 与每个 row digest；任一不一致回滚整个事务；
6. 提交后阶段 07 继续调用现有只读 preview，不接受 runner 传入金额。

这是 isolated Demo run 的 runtime materialization，不是全局种子或生产激活。全新数据库以外如出现
同 identity 的既有簿/行或任何冲突，立即失败，不做 upsert、覆盖或静默复用。

## 4. 来源与客户边界

- `SYNTHETIC_TEST_ONLY` bundle 可携带明显合成的完整 source，只能得到
  `TECHNICAL_REHEARSAL_PASS`；测试不得把其 URL、日期或金额描述为真实 CNIPA 事实。
- `CUSTOMER_AUTHORIZED` bundle 必须按现有 decision contract 绑定 exact manifest、book digest 和
  row digests；缺 decision 或 digest 不一致时保持 `DEMO_INPUT_REQUIRED`。
- 本整改不会自动生成 customer-authorized bundle，也不会把技术测试 fixture 升格为客户输入。
- 客户 Demo 的具体模板、费用及来源仍是之后的 runtime input；没有获批输入就不演示金额。

## 5. 失败和停止条件

下列任一条件在服务启动前停止：缺 source、未知/缺失字段、snapshot hash 错误、selector/source 不等、
row digest 错误、非 GOV、非 CNY、金额非正、未生效/已过期、来源版本冲突、authority decision 不匹配。

物化时若 actor 缺失、数据库非 fresh、唯一键冲突、写后摘要不同或事务异常，回滚并停止。不得降级到
占位费率、硬编码金额、测试内隐式 seed、网络抓取或跳过阶段 07。

## 6. 最小实现边界

后续实现任务只允许按需修改：

- `backend/app/core/demo_bundle.py`：immutable source 类型、严格解析和 digest 交叉校验；
- `backend/app/modules/grant_fees/demo_official_fee.py`：将既有 row digest helper 提升为可复用契约，
  preview 语义不变；
- `backend/scripts/run_local_demo_abc.py`：fresh-run 专用物化；
- `backend/tests/test_demo_abc_runtime_bundle.py`：完整 synthetic source fixture 与负例；
- `backend/tests/test_demo_abc_local_runner.py`：fresh DB 物化、actor、摘要和冲突回滚；
- `backend/tests/test_demo_v6_grant_official_fee.py`：删除测试私有的重复费率 seed，证明 preview 使用
  runtime materialized facts；
- 必要时更新 `backend/tests/test_demo_integrated_a_runner.py` 的 bundle shape 断言，不改 stage contract。

不新增数据库表/迁移、runtime bundle 文件、API、页面或通用导入模块。

## 7. 验收

实现必须 test-first，并依次证明：

1. bundle loader 正例和上述失败关闭负例；
2. fresh-run 只物化一簿两行，字段与摘要完全相等；
3. grant preview 测试不再私自 seed 官费；
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
