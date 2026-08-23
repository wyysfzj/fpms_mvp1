# FPMS 客户 Demo V6：授权登记双轨费用增强设计

日期：2026-08-23
状态：用户已批准书面规格，独立规格审查零发现
前序：`docs/postdemo/demo-lifecycle-customer-v5.html` 及其完整 runbook
风险：HIGH（官费、服务应收、回款、核销与来源激活）

## 1. 设计结论

V6 保留 V5 阶段 01–06 的同一客户、同一案件和授权登记主线，只替换并扩展费用尾段。
新尾段采用两条严格分离的费用链：

- 官费：`已批准并激活的 CNIPA OfficialRateBook/FeeRate -> 授权登记只读预览 ->
  授权人员人工确认 -> GOV FeeObligation/Line -> GOV FeeDraft/FeeItem -> PayList -> GovPayment`；
- 服务费：`客户授权 demo bundle -> 多行 SERVICE FeeObligation/Line -> SERVICE
  FeeDraft/FeeItem -> Bill -> Payment -> Offset`。

官费与服务费可以在同一案件中并列展示，但不得合并草单、混入对方的下游对象，
也不得使用一个笼统的“已支付”状态替代官方缴费、客户回款和核销三个不同事实。

本设计的目标是让客户看到真实、可解释的费用变化，而不是增加费用类型或扩展为费用规则平台。

## 2. 当前 V5 审查结论

V5 的费用闭环可靠但过于线性：

- 只有一个合成 SERVICE 项目；
- 只有一张立即锁定的服务费草单；
- 只有一张客户账单；
- 只有一次等额回款和一次全额核销；
- 官费保持未配置和 no-write。

V5 已正确建立来源校验、控制页隐藏、幂等重放、网络结果对账和客户应收闭环。
V6 必须复用这些成果，不能重新设计案件生命周期、证据链或财务基础模型。

## 3. 目标与成功标准

### 3.1 目标

1. 在授权登记阶段使用已配置、已激活且可追溯的官费 runtime input。
2. 展示多行官费预览，并明确预览 no-write。
3. 展示一张只含 GOV 的官费草单和一张只含 SERVICE 的服务费草单。
4. 展示服务费草单在 OPEN 状态的一次可解释调整，以及锁定后的只读状态。
5. 展示官费清单和人工缴费登记，但不虚构官方提交或外部支付成功。
6. 展示服务费账单先部分结清、再完全结清的两次回款与两次核销。
7. 每次 Demo 前新建隔离 run 和全新 SQLite 数据库，只初始化种子数据，并完成来源、API 和
   首次加载预检。

### 3.2 成功标准

- 同一案件中两条费用链均可从来源追溯到最终状态；
- GOV 与 SERVICE 在草单、清单、账单和汇总层均不串线；
- 所有 mutation 可按幂等键对账和安全重放；
- 连续两次执行“新建隔离 run -> 完整 Demo”均通过且无首次加载 `Network Error`；
- 费用事实、范围和证据获得独立零发现审查。

## 4. 明确不做

本轮 non-closure 为：

- 不演示或实现官费费减；
- 不加入年费、滞纳金、坏账、撤销核销或多币种；
- 不增加多案件费用矩阵；
- 不新建费用类型、费用表或规则引擎；
- 不把官方费用变成客户服务费应收；
- 不宣称生成的内部清单是官方缴费模板；
- 不宣称 `GovPayment` 记录本身证明已经向官方成功提交或支付；
- 不激活生产费率，不把 Demo runtime 值写成代码默认；
- 不改动 V5 阶段 01–06 的案件、文书、OA、证据和授权登记故事。

## 5. Demo 编排

V5 阶段 01–06 保持不变。费用尾段调整为：

### 阶段 07：官费配置与预览

授权登记节点按 runtime bundle 中的 exact fee-code selector 读取已经 `APPROVED/ACTIVE` 的
CNIPA `OfficialRateBook/FeeRate`，生成不少于两行的授权登记官费候选预览。页面显示费项、
数量、单价或计算方式、候选金额、来源版本和生效日期。

本阶段不扩展当前只支持 `FILING_ACCEPTED/REEXAM_REQUESTED` 的通用 preview trigger，也不把
候选金额自动接受为义务。授权登记使用一个只读的 grant-specific preview adapter；它只能读取
已激活费率和已归档授权通知上下文，不能创建 activity、command carrier、`FeeObligation/Line`、
draft/link/item、`PayList` 或 `GovPayment`。

### 阶段 08：双轨草单审核

分别生成：

- 一张仅包含 GOV 明细的官费草单；
- 一张包含至少两个 SERVICE 明细的服务费草单。

授权人员必须逐行提交明确的确认金额，并绑定授权通知证据、preview digest、actor、确认时间和
幂等键。确认动作复用现有授权官费人工复核原则，在一个事务内创建多行 GOV obligation；
它不取代或弱化人工确认，也不允许从费率候选自动生成已接受义务。随后由该 obligation 生成
GOV 草单。

GOV 明细即使在 OPEN 草单中也只读。SERVICE 草单在 OPEN 状态对一个可调整项目执行一次
数量修改，并填写调整原因；页面重新计算服务费合计。调整动作保留原 obligation 及其 lines
不可变，另写一条绑定 before/after、actor、时间、原因和幂等键的 `CaseActivityEvent`，创建一个
包含完整修订行集的 superseding SERVICE obligation，并在同一事务内把现有 OPEN 草单的 items
和 links 切换到 superseding lines。这是一条 Demo 所需的可追溯调整记录，不扩展为通用价格审计
模型。随后两张草单分别锁定，锁定后明细均只读。

### 阶段 09：官费清单与缴费登记

从锁定 GOV 草单创建一张 `PayList`，清单只接收 GOV 明细。canonical Demo 对每条官费明细
登记一个 `GovPayment`，但明确不提供 `official_receipt_no`、voucher 或 invoice evidence；
页面固定表达“已登记，待官方凭证核验”，不能表达“官方缴费成功”。带官方凭证及其核验是
本轮 non-closure。

### 阶段 10：客户账单与分次回款

从锁定 SERVICE 草单生成唯一客户账单。第一次回款金额小于账单总额；回款创建后账单仍
未结清，第一次核销后账单进入部分结清。第二次回款使用剩余金额，第二次核销后账单结清。

### 阶段 11：同案财务汇总

案件财务汇总分别显示：

- 官费应缴、官费清单和缴费登记状态；
- 服务费应收、已回款、已核销和未结清余额。

页面不得把两条链合并为一个“已支付”状态。

## 6. Runtime input 合同

### 6.1 官费输入

runtime bundle 的授权登记 selector 至少选择两条适用的激活费率行。每行必须能够绑定：

- 官费代码和中文名称；
- 数量、单价或既有支持的计算模式；
- 币种，本 Demo 固定为 CNY；
- CNIPA 来源引用、来源版本、生效起止日期和 source snapshot SHA-256；
- `enabled=true`、`OfficialRateBook.approval_status=APPROVED` 和
  `activation_status=ACTIVE`；
- 计算前金额和本次应缴金额；
- 是否允许费减的来源属性，但本轮案件不应用费减。

官费金额的权威载体是已批准并激活的 `OfficialRateBook/FeeRate`，runtime bundle 只选择并
digest-bind exact book/version/rate rows，不另带一套可覆盖数据库金额的真值。少于两条适用行、
来源哈希不匹配、版本冲突、未激活、币种错误或金额非正时，preflight 必须失败。系统不得添加
无来源的“占位官费”来满足行数。

### 6.2 服务费输入

服务费配置至少包含两个 SERVICE 项目。每项提供：

- 项目代码、中文名称、单价和初始数量；
- 来源引用、来源版本和内容 SHA-256；
- 固定或可调整标志。

至少一个项目固定，至少一个项目可调整。validated bundle provider 把被选项目的代码、中文名称、
单价、初始数量、可调整标志、source digest 和 manifest digest 作为一个 canonical source
activity snapshot 持久化；一次识别动作从该 snapshot 创建一个多行 SERVICE obligation，
`prepare_draft` 再从同一 obligation 生成一张多行草单。不得通过多次单行 obligation 后再合并草单。

具体名称、金额和最终数量均由 runtime input 提供，不写入代码默认值，不冒充客户正式报价。
`DEMO_ONLY` 或 bundle 私有价格不得写入正式 `ServicePriceBook`。

### 6.3 分次回款输入

runtime bundle 提供第一次回款金额，并满足：

`0 < 第一次回款 < 锁定 SERVICE 草单合计`

第二次回款金额由账单权威剩余金额计算，不由前端缓存或重复配置决定。

### 6.4 来源分类、决策与 readiness

本设计沿用 V5 的 authority boundary，不允许 loader 自行提升来源等级：

- `SYNTHETIC_TEST_ONLY` 只能达到 `TECHNICAL_REHEARSAL_PASS`，必须使用明显的测试身份和
  免责声明，结构上不得达到客户 `DEMO_READY`；
- 客户演示的 SERVICE 配置必须为 exact-digest-pinned `CUSTOMER_AUTHORIZED` bundle，并在
  source registry 中记录 actor、批准时间、decision version、raw manifest digest 及每个
  service source digest；
- 客户演示的 GOV 行必须来自 `source_authority=CNIPA`、`APPROVED/ACTIVE` 的官方费率簿，
  同时由 `CUSTOMER_AUTHORIZED` bundle 精确选择 fee codes 和版本；
- bundle decision、启动配置、manifest digest、官方 rate-book digest 和 service source
  digests 必须完全一致；
- 本轮 Demo 不执行新的官方费率审批或激活动作，只消费事先存在且通过上述门禁的本地激活版本，
  也不改变生产环境状态。

里程碑分级固定为：`IMPLEMENTED`（代码闭合）、`TECHNICAL_REHEARSAL_PASS`（可使用合成输入）和
`DEMO_READY`（同时具备 CNIPA 已激活官费来源和客户授权 SERVICE bundle）。缺少最后一组输入时，
只能报告 `DEMO_INPUT_REQUIRED`，不得面对客户演示金额。

## 7. 领域与权限规则

### 7.1 双轨隔离

- GOV obligation 只能生成 GOV 草单和 GOV 明细；
- SERVICE obligation 只能生成 SERVICE 草单和 SERVICE 明细；
- `PayList` 只接收 GOV 明细；
- 客户 `Bill` 只接收本轮 SERVICE 草单；
- 类型不匹配返回业务冲突，不能静默过滤后继续；
- 每条 obligation、draft、pay list、bill、payment 和 offset 都有独立幂等身份。

### 7.2 草单编辑

- GOV 明细来自激活费率候选和授权人员逐行人工确认结果，不允许在草单中手改；
- 官费错误必须返回配置/预览环节修正后重新生成；
- SERVICE 明细只在 OPEN 状态通过绑定来源 snapshot 的专用调整命令编辑；只允许 bundle 中
  标记为可调整的项目，且必须记录原因、before/after、actor、时间和幂等键；
- LOCKED 状态拒绝新增、修改或删除明细；
- 本轮不新增完整的价格调整审计模型，不把 `updated_at` 解释为审计轨迹。

### 7.3 事实边界

- 官费预览不是已接受的缴费义务；
- 人工确认不是外部官方确认；
- `PayList` 是内部官费清单，不自动等于官方模板；
- `GovPayment` 是系统登记事实；没有官方凭证时不证明官方受理或支付成功；
- 客户回款登记不等于核销；只有有效 `Offset` 改变账单结清状态。

## 8. 最小技术落点

### 8.1 复用对象

设计复用现有 `OfficialRateBook`、`FeeRate`、授权官费人工复核原则、`FeeObligation`、`FeeObligationLine`、
`FeeDraft`、`FeeItem`、obligation/draft/item 关联、`PayList`、`GovPayment`、`Bill`、
`Payment`、`PaymentLine`、`Offset` 和 `CaseReceipt`。

不建立 Demo 专用财务存储，不复制 provenance 到备注字段。授权登记候选预览使用一个只读
grant-specific adapter，而不是扩展现有通用 preview trigger。SERVICE bundle snapshot 和一次
草单调整事件使用现有 `CaseActivityEvent`；不新增表。现有模型已经支持多行 obligation/item、
部分核销、账单余额和多笔回款；实现应补齐编排、门禁、查询和 UI，而不是替换模型。

### 8.1.1 SERVICE 调整 reconciliation

专用调整命令只允许执行一次，并必须在一个事务内完成。前置条件固定为：

- 当前 obligation 为 SERVICE，且没有现存 superseding child；
- 当前草单为 OPEN、尚未生成 Bill/PayList，且其每个 item 与当前 obligation line 一对一链接；
- 当前 draft/item/link identities、金额和 source snapshot digest 与命令中的 expected values 一致；
- 被修改的项目在 bundle snapshot 中明确标记为可调整；
- 命令包含非空中文调整原因、actor、时间和幂等键。

事务顺序固定为：

1. 写入唯一 adjustment activity，payload 保存完整 before/after line snapshot 和 digest；
2. 调用现有 obligation recognition 创建完整行集的 superseding SERVICE obligation，
   `supersedes_obligation_id` 指向原 obligation；
3. 通过现有 instruction service 为 superseding obligation 写入一条 PAY 指示活动；该活动显式绑定
   原 PAY instruction 和 adjustment activity，表示延续已经确认的服务收费意图，不新增客户可见的
   “客户决策”面板；
4. 对现有 OPEN 草单的对应 `FeeItem` 原子更新 quantity/unit price/amount；
5. 将每条 `FeeObligationDraftItemLink` 从原 line 重新绑定到 exact superseding line；
6. 使用 compare-and-swap 原子迁移两个 header 的草单状态：
   - 原 header 必须是 `SUPERSEDED/PAY/CREATED/UNPAID/NOT_APPLICABLE`，迁移为
     `SUPERSEDED/PAY/NOT_CREATED/UNPAID/NOT_APPLICABLE`；
   - superseding header 必须是 `RECOGNIZED/PAY/NOT_CREATED/UNPAID/NOT_APPLICABLE`，迁移为
     `RECOGNIZED/PAY/CREATED/UNPAID/NOT_APPLICABLE`；
7. 重算草单合计，并在提交前分别运行原 obligation、superseding obligation 和当前草单的既有
   reader 校验。

禁止修改原 obligation/lines 的金额和来源事实，禁止保留 item 同时链接新旧两条 line，禁止创建
第二张草单，也禁止为支持调整而放宽全局 obligation 读取不变量。唯一允许修改的原 header 字段是
上述 CAS 控制的 `draft_status: CREATED -> NOT_CREATED`；`obligation_status=SUPERSEDED` 和历史
`client_instruction_status=PAY` 保持不变。事务完成后，既有 reader 仍按当前 links 要求每个 item
金额等于 superseding line 的 `payable_amount`；读取原 obligation 时返回 `SUPERSEDED` 且不报告
当前草单，读取 superseding obligation 时返回 `RECOGNIZED/PAY/CREATED` 和该草单。

exact replay 返回同一个 adjustment activity、superseding PAY instruction、superseding obligation、
draft 和 items；payload drift、第二次调整、任一 header CAS miss、并发版本变化或任一 relink
不完整均返回 409 并整笔回滚。重放必须验证两个 header 已处于上述最终状态，不得再次迁移状态。

### 8.2 用户页面

共享屏幕只展示正常业务页面：

- 案件费用节点；
- 官费预览；
- GOV 与 SERVICE 草单详情；
- 官费清单和缴费登记；
- 客户账单、回款和核销；
- 案件财务汇总。

`ABC 演示台`、runtime 加载、清理和确定性控制命令仅供主持人使用，不进入客户导航或共享屏幕。

### 8.3 来源展示

正常费用页面增加只读“计算与来源”区域，通过现有 obligation/draft/item 关联展示：

- 费用代码、来源版本和生效日期；
- 数量、单价、计算方式和应缴金额；
- 来源引用、内容校验与激活状态。

### 8.4 API 与恢复

保持现有 HTTP 状态、响应 envelope 和权限语义。新增或调整的用户文案全部为简体中文。
Demo 控制动作可以用于确定性建立输入和执行分次回款，但必须调用或复用正常领域服务，
不得绕过类型门禁、金额校验或幂等控制。

每次 mutation 使用独立幂等键。出现传输失败时先按幂等键读取持久状态；已完成则恢复原对象，
未完成才允许重试。重放不得产生新业务对象。

### 8.5 Canonical GovPayment 命令合同

现有 `/gov-payments` 不提供客户端幂等键，不能直接承担 canonical Demo 的 commit-then-drop
恢复。本轮采用隐藏的 demo command wrapper，复用现有 `DemoFinanceCommand` carrier 和正常
`register_gov_payment` 领域服务，不新增表：

- operation 固定为 `GOV_PAYMENT`，每个 GOV `fee_item_id` 使用一个独立 idempotency key；
- canonical payload 固定包含 `pay_list_id`、`fee_item_id`、`paid_date`、exact `paid_amount`、
  `official_receipt_no=null`、`voucher_no=null`、`invoice_no=null` 及中文待核验备注；
- wrapper 写入前核对 fee item 属于该 PayList、类型为 GOV、金额等于该行应缴金额；
- exact same key/payload 返回同一个 `GovPayment`，并标记 `reused=true`；
- same key/payload drift 返回 409 且零写入；
- commit 后响应丢失时，`GET /gov-payments/idempotency/{key}` 从 command snapshot 与
  `PayList` 权威明细恢复同一个结果；
- customer UI 只读取正常 PayList/GovPayment 页面，不展示 wrapper。

## 9. Demo 前清理与 preflight

每次 Demo 不在旧数据库中逐行删除，而是建立一个新的隔离 run root 和全新 SQLite 数据库：

1. 生成新的不可复用 Demo run ID 和 run root；
2. 写入只含 run ID、数据库绝对路径、bundle digest 和创建时间的 `run.json`；
3. preflight 要求目标数据库及 `-wal/-shm` companion 均不存在；
4. 在该隔离数据库执行 migration 和幂等种子初始化；
5. 验证目标案件以外不存在非种子业务对象，目标案件的草单、清单、缴费、账单、回款和核销
   均为初始计数；
6. 校验官费和服务费 runtime bundle、来源哈希、authority decision 和激活状态；
7. 预热案件详情、草单、官费清单、账单和回款 API；
8. 任一检查失败则关闭该 run，不复用该数据库，并禁止开始 Demo。

旧 run 不作为新 Demo 的 reset 输入，也不在 preflight 中删除。演示结束后只能按已验证的 exact
run root 执行独立 cleanup/归档流程。不得使用全表 truncate、业务前缀匹配或宽泛目录删除。

## 10. 可观察验收矩阵

| 阶段 | 必须满足 |
| --- | --- |
| 07 | 官费预览行数与激活配置一致且不少于 2；来源可见；事务级 before/after 证明所有费用 mutation 表零写入 |
| 08 | 恰好 1 张 GOV 草单和 1 张 SERVICE 草单；各自类型纯净；恰好 1 条 SERVICE adjustment activity、1 条 superseding PAY instruction 和 1 个 superseding obligation；原 header 为 `SUPERSEDED/PAY/NOT_CREATED`，新 header 为 `RECOGNIZED/PAY/CREATED`；当前 links 全部指向 superseding lines；调整后合计正确；锁定后只读 |
| 09 | 恰好 1 张 PayList；清单行数等于 GOV 行数；每行恰好一个“已登记、待核验”的无凭证 GovPayment；合计等于清单合计；重放计数不变 |
| 10A | 第一次回款创建后账单未结清；第一次核销后账单为 `PARTIALLY_SETTLED` 且余额正确 |
| 10B | 第二次回款和核销后账单为 `SETTLED`、余额为 0；恰好 2 笔回款和 2 条有效核销 |
| 11 | 官费与服务费分栏；页面中文状态一致；所有权威读取返回相同金额与状态 |

最终必须满足：

- GOV 草单合计 = PayList 合计 = GovPayment 合计；
- adjustment before snapshot/digest = 原 SERVICE obligation 完整行集；
- adjustment after snapshot/digest = superseding SERVICE obligation 完整行集；
- superseding SERVICE obligation payable 合计 = 当前 linked FeeItem 合计 = SERVICE 锁定草单合计；
- 原 SERVICE obligation 读取为 `SUPERSEDED/PAY/NOT_CREATED` 且没有当前 draft links；
- superseding SERVICE obligation 读取为 `RECOGNIZED/PAY/CREATED` 且拥有全部当前 draft links；
- SERVICE 锁定草单合计 = Bill 合计；
- 两笔 Payment 合计 = 两条有效 Offset 合计 = Bill 合计；
- 官费金额不进入客户服务费账单；
- SERVICE 明细不进入 PayList。

## 11. 验证策略

1. 后端目标测试：runtime 门禁、预览 no-write、双轨隔离、GOV 只读、SERVICE superseding
   adjustment/relink、草单锁定、PayList 纯度、部分核销、幂等和传输恢复。
2. 前端目标测试：GOV 明细无编辑入口、SERVICE OPEN 可编辑、LOCKED 只读、中文状态、
   来源面板和首次加载恢复。
3. 一条 canonical live-backend E2E，从新建隔离 run 开始完整执行阶段 01–11，并在 mutation 后刷新
   正常业务页读取权威状态。
4. 连续两次执行“新建隔离 run -> 完整 Demo”均通过，浏览器控制台和网络日志无首次加载错误。
5. HIGH 费用事实独立审查必须为零发现，且绑定最终规格/任务/实现证据的当前哈希。

阶段 07 的 no-write 测试必须覆盖至少：`CaseActivityEvent`、demo command carrier、
`FeeObligation`、`FeeObligationLine`、obligation draft/item links、`FeeDraft`、`FeeItem`、
`PayList` 和 `GovPayment`。测试比较调用前后的 exact identities/counts，并在同一只读事务视图中
断言无新增或变更；只检查草单/清单/缴费三个表不足以证明 no-write。

广泛产品测试、repo-wide lint 和 release gate 只在后续明确的最终关闭点运行，不在每个原子任务中重复。

## 12. 停止条件

出现以下任一情况必须停止受影响阶段：

- 官费来源未激活、哈希不匹配、版本冲突或适用行少于两条；
- GOV 与 SERVICE 混入同一草单或进入错误的下游对象；
- GOV 明细可手改，或锁定草单仍可修改；
- 预览产生写入；
- 回款未经核销即改变账单结清状态；
- 金额等式不成立；
- 幂等重放增加对象数量；
- 正常业务页首次加载出现 `Network Error`；
- `GovPayment` 被展示为无凭证的官方缴费成功；
- 新 run 的数据库已存在，或 run root/数据库/bundle 绑定不唯一；
- 客户演示只达到 `TECHNICAL_REHEARSAL_PASS`，未达到 `DEMO_READY`。

## 13. 防止 over-engineering 的实现护栏

- 一个案件、一种授权登记官费场景、一个币种；
- 两条费用链，各一张草单；
- 官费至少两行、服务费至少两行；
- 服务费只有一次草单调整；
- 客户回款固定两次、核销固定两次；
- 不吸收费减、年费、逾期、撤销、坏账、多案件或生产发布；
- 优先复用现有对象和标准页面，只有缺失的 grant-specific 只读预览、门禁、编排、来源展示与
  确定性验证可以改动；不得扩展通用 fee preview trigger；
- 任何新增抽象必须证明现有模型不能满足本规格中的一条可观察验收，否则不得引入。

## 14. 实施前置条件

实施计划和产品改动开始前必须同时满足：

1. 本规格获得独立零发现审查；
2. 用户复核并批准书面规格；
3. 官费与服务费 runtime 输入已提供，或实施任务明确只实现输入合同而不激活金额；客户
   `DEMO_READY` 还要求 exact CNIPA `APPROVED/ACTIVE` rate-book binding 和
   `CUSTOMER_AUTHORIZED` SERVICE bundle decision；
4. 仓库治理 manifest 与其命名激活任务的 terminal PASS 回执重新可验证；
5. 后续实施拆成最小、可独立验收的 HIGH 原子任务，并由非实现者审查。

当前工作树执行
`./scripts/taskctl REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01 doctor`
返回 `task artifact authority root is missing`。这不改变本设计，但在恢复并验证治理回执前，
不得开始产品实现。

## 15. 原子执行分类

以下分类只约束后续实施编排，不改变本设计的业务语义：

- `shared_file_density: HIGH`：费用、授权、账单、前端 API 与 canonical E2E 存在共享路由和模型；
- `prereq_dependency_density: HIGH`：治理 PASS、来源激活、runtime bundle 和前序状态严格串行；
- `be_fe_coupling: HIGH`：新增可见状态与控制动作必须由后端权威状态驱动；
- `evidence_cost: HIGH`：费用事实、幂等恢复、双轨隔离及连续两次新 run 均需要持久化证据；
- `chosen_runbook: P0-prereq-heavy-story`：按 Gate 0 与依赖顺序串行实施，禁止共享 SQLite 写入并行，
  禁止在原子任务中重复 repo-wide 验证。
