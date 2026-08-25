# FPMS Demo V6 人工与 Codex UI 等价设计

状态：`DEC-DEMO-V6-UI-PARITY-20260826` 已批准设计边界；待独立零问题评审与用户书面规格批准
日期：2026-08-26
风险：`PROTECTED`（生命周期、证据、官费、服务费、账单、回款与核销）

## 1. 决策与问题

用户确认以下精确边界：主持人与另一 Codex 账号都必须从全新空业务库开始，在正常业务 UI
输入同一套业务值、点击同一类按钮并得到同一业务结果；禁止直接业务 API、直接数据库、隐藏
演示台或预造业务对象旁路。

现有 V6 自动化没有伪造数据，也没有绕过后端规则，但它是混合 E2E：第 02–10 阶段的若干
写操作由 Playwright `APIRequestContext` 直接调用，页面主要负责展示与断言。因此当前 PASS
证明真实后端链和结果页，不证明人工与 Codex 的 UI 输入等价。

本设计保留现有自动化作为 A 路径，并新增严格 UI-only 的 B 路径。两条路径共用既有 V6
业务规则、runtime bundle 和数据库模型，不复制业务实现。

## 2. 可观察结果

### A — 自动技术验收

- 保留现有 `TECHNICAL_REHEARSAL` 两轮 headless canonical runner。
- 它继续证明 11 阶段业务链、来源摘要、双轨费用、两次回款与核销、Network Error 0 和
  console error 0。
- 它是快速回归，不再被表述为人工 UI 可完成性的证据。

### B-HUMAN — 主持人人工演示

- 一个 setup-only 会话命令创建全新 run root、全新 SQLite、动态凭据并启动 8000/5173，
  只物化系统配置、身份、模板和 runtime 来源；客户、案件、文书、义务、草单、清单、账单、
  回款和核销的 preflight 计数必须全部为 0。
- 主持人先在独立输入页核对种子与事实边界，再从正常业务页面逐项输入和点击。
- 会话在主持人明确结束前保持服务、浏览器和数据库；失败时保留 artifact，旧 run 不作为
  新 run 的 reset 输入。

### B-CODEX — 另一账号 Codex 演示

- Codex 从同一 candidate commit 全新 clone，执行同一个 setup-only 命令并读取同一份 Runbook。
- Codex 只能使用浏览器填写与点击；不允许 curl、直接 HTTP client、SQL、内部 ID 抄写、
  `/demo/abc` 或从历史 artifact 复制对象。
- Codex 与人工使用同一输入分类和同一正常页面；只有 run suffix、UUID、数据库路径、动态
  凭据、幂等键和时间戳等 `APP_GENERATED` 值允许不同。

## 3. 数据与事实边界

现场 B 路径继续使用 `SYNTHETIC_TEST_ONLY`，只可表述为“客户在场的合成技术展示”，不得
改称 `CUSTOMER_AUTHORIZED`、`CUSTOMER_DEMO_PASS`、正式报价、正式官费来源激活、官方递交
或官方缴费成功。正常页面持续显示简体中文边界条：

> 合成演示数据｜仅用于技术展示，非客户、生产或官方事实

`DEC-DEMO-V6-UI-PARITY-20260826` 目前只授权设计与计划评审，不授权产品实施、客户现场展示
或 release。只有本规格独立零问题、用户明确批准书面规格、实施计划独立零问题并且每个原子
实现任务通过后，才可实施该透明合成路径。它不创造或替代外部客户 bundle、来源摘要或正式
客户授权决策；真正的 `CUSTOMER_DEMO` profile 仍由既有外部输入门禁控制。

输入分为三类：

| 类型 | 人工与 Codex 要求 | 例子 |
| --- | --- | --- |
| `EXPLICIT_INPUT` | 同一固定值或同一 `<run suffix>` 模板，必须在 UI 可见并由操作者输入 | 客户、案名、日期、1,200.00、调整原因 |
| `SOURCE_BOUND` | 两者都从当前 UI/来源读取，不允许重新手打或猜测 | digest、官费行、服务费单价、第二笔权威余额 |
| `APP_GENERATED` | 两次运行可不同，但必须唯一、可追溯且由系统生成 | UUID、对象 ID、幂等键、动态密码 |

### 3.1 单一可机读输入/输出合同

实施必须新增且只认一个 versioned 合同：`fpms.demo-v6-ui-parity/v1`。HUMAN、CODEX 和 strict
UI 技术验证都读取同一合同。每条字段固定：`stage`、`field_key`、`classification`、
`value_rule`、`ui_route`、`control`（role/label 或 testid）、`source_selector`、`normalization` 和
`required=true`。输出字段另固定 `observable`、`expected_rule` 和同一 UI 证据点。validator 对
缺项、多项、未知字段、重复字段、分类漂移、页面/控件漂移、非允许差异一律失败。

| 阶段 | 必填输入或来源绑定 | 必填可见输出 |
| --- | --- | --- |
| 01 | 客户名 `澄岳智造技术（苏州）有限公司`；编码 `CYZN-<run suffix>`；客户/联系人邮箱；周岚/知识产权经理；案号 `CYIP-CN-INV-<run suffix>`；固定案名；发明/中国国内/费减 0 | 唯一客户、联系人和案件；同案主联系人与第一申请人 |
| 02 | 当前案件；60 类目录为 `SOURCE_BOUND` | 同一 filing package；可执行/参考目录边界 |
| 03 | 人工递交 `2026-08-01 09:00:00`、备注“已完成人工递交”；回执号 `CNIPA-20260802-001`、接收 `2026-08-02 10:00:00`、接收人陈思远；已复核 filing/acceptance/preliminary/publication/substantive 证据均为 `SOURCE_BOUND` | 递交、回执、受理、初审开始/通过、公布和进入实审均绑定当前已复核证据 |
| 04 | OA 序号 1；通知 `2026-08-07 09:00:00`；期限 `2026-09-22`；答复输出角色和回执 `2026-08-08 10:00:00` 均来自当前 bundle | OA1 包、任务、答复绑定、回执和归档均唯一 |
| 05 | OA 序号 2；通知 `2026-08-09 09:00:00`；期限 `2026-10-23`；回执 `2026-08-10 10:00:00` | OA2 对象与 OA1 身份不同；两轮历史同时保留 |
| 06 | 原授权通知 `2026-08-11 09:00:00`/期限 `2026-11-23`；更正通知 `2026-08-12 09:00:00`/期限 `2026-11-24`；说明“依据更正通知更新办理登记手续期限”；当前任务 WAITING_CLIENT→PAY | 原任务被替代且 UI 不可写；当前任务 PAY 恰好一次；确认前无官费对象 |
| 07 | 当前任务；已复核更正证据；rate-book/book-row/preview digest 和逐行金额均为 `SOURCE_BOUND`；确认时间/key 为 `APP_GENERATED` | 900.00+50.00=950.00 CNY；唯一 GOV obligation/draft；GOV 行只读 |
| 08 | `FWSQDJ001`、`FWSQDJ002`；第二行数量 1→2；原因“客户确认增加一份附加文件处理” | GOV/SERVICE 各一张；SERVICE 1,500.00→1,800.00；一次 adjustment；两张 LOCKED |
| 09 | planned date `2026-08-25`；备注“授权登记官费清单”；金额/空凭证字段为 `SOURCE_BOUND` | 一张两行 PayList；每行一个 `REGISTERED_PENDING_OFFICIAL_EVIDENCE`，receipt/voucher/invoice 均为空 |
| 10 | 账单号 `AR-CYZN-<run suffix>`、账单日 `2026-08-25`、到期日 `2026-09-24`；第一笔 1,200.00/`2026-08-25`/BANK_TRANSFER/编号与 bank ref；第二笔读取刷新后余额 600.00，日期 `2026-08-26`；两次核销日期对应回款日 | UNSETTLED→PARTIALLY_SETTLED/600.00→SETTLED/0.00；恰好两笔 Payment 与两个有效 Offset |
| 11 | 无新输入 | 同案 GOV 待官方凭证、SERVICE 已结清；所有金额、身份与状态一致 |

合同顶层还必须绑定 exact candidate commit、bundle manifest/authority SHA-256、actor
`HUMAN|CODEX|STRICT_UI_TECHNICAL`、run ID、run root 和允许差异白名单。允许差异仅为 run suffix、
UUID/自增 ID、数据库/文件路径、动态凭据、幂等键和系统时间戳；所有业务日期、金额、原因、
来源摘要和状态不得差异。

## 4. 正常 UI 与禁止旁路

“正常 UI”是客户、案件、文书、递交准备、OA 答复、授权费用任务、案件费用、费用草单、官费
清单、官费登记、账单、回款、核销和案件详情页面。`/demo/inputs` 只用于演示前查看输入与空库
证据；`/demo/abc` 不得进入人工或 Codex 路径。

允许：浏览器填值或点击后，由前端正常发起 API 请求；Playwright 可用 `waitForResponse` 被动
观察该请求。禁止：`APIRequestContext` 或 `request` fixture、`request.fetch`、`page.request`、
Node/axios/fetch HTTP client、curl、直接 SQL/ORM/后端脚本、route mock、`page.evaluate`/动态代码
注入业务值、隐藏控制页写入、读取先前 ledger 取得业务对象 ID，或在 setup 阶段预建业务对象。

反旁路检查必须用 TypeScript AST 遍历 strict spec 的完整传递 import 闭包，不能只做单文件字符串
搜索。每个 POST/PUT/PATCH/DELETE 必须在 runtime mutation ledger 中关联唯一 `action_id`、可见
页面、role/label 或 testid、浏览器 request/response、method/path/status 和规范化 payload 摘要；
出现未关联可见控件动作的 mutation 即失败。

A 保留领域级负向 409/no-write。B 不给客户暴露诊断型错误操作，但每个新增 UI command client
必须有 focused 自动测试覆盖：commit 后响应丢失的 GET-first reconcile、exact replay 返回同一
对象、payload drift 409/no-write。B 页面只展示恢复后的权威结果或明确停止状态。

## 5. 十一阶段 UI 覆盖与最小缺口

| 阶段 | 当前 UI 状态 | 本设计的最小闭合 |
| --- | --- | --- |
| 01 客户与案件 | 已完整 | 直接复用客户、联系人和案件表单 |
| 02 文件与递交准备 | 基本完整 | 从案件详情进入递交准备；禁止 API resolve 旁路 |
| 03 受理与审查 | 部分 | 递交页增加“记录人工递交完成”；回执改为选择已上传附件；文书详情增加基于已复核证据的生命周期确认动作 |
| 04 第一轮 OA | 部分 | OA 通知确认、答复文书选择/绑定和回执附件选择均改为可见 UI |
| 05 第二轮 OA | 部分 | 复用阶段 04 的同一 UI seam，不复制第二套实现 |
| 06 授权登记准备 | 部分 | 已有更正通知与 PAY；补已复核授权通知确认和“标记等待客户”正常动作 |
| 07 生效官费预览 | 已完整 | runner 改为定位任务行、预览、核对并点击确认 |
| 08 双草单与服务费调整 | 缺一入口 | 案件费用页在 demo scope 下增加“生成服务费义务”；其余 PAY、建草单、调整和锁定复用现有 UI |
| 09 官费清单与登记 | 基本完整 | 逐行勾选生成清单并逐行登记；增加“返回当前清单/登记下一行”以防误选 |
| 10 两次回款与核销 | 部分 | 正常账单、回款、核销表单补齐 V6 显式字段和 command seam；第一笔后必须停留显示余额 600.00，第二笔后显示 0.00 |
| 11 同案双轨汇总 | 已完整 | 只从案件、清单、账单、回款和核销页面核对，不新增写入 |

文书生命周期确认可由一个职责单一的文书证据动作面板承载多个既有 endpoint；它不新增状态机、
不推断文书类型、不改变后端状态或证据规则。所有选项必须来自当前可见、已复核且同案的对象，
不得要求主持人抄内部 ID。

### 5.1 阶段 10 精确 command seam

三类正常页面动作只在当前 session 已通过 `/fees/demo-preflight`、schema 为 integrated V2、
classification 为 `SYNTHETIC_TEST_ONLY`、manifest/authority 与启动上下文精确一致时启用；否则
保持既有标准页面与标准 endpoint，不出现 V6 command 控件。

不得把现有 wrapper/parser 视为已支持分次结算，也不得复制一套平行 client。实施须窄幅扩展
现有 `createDemoBankReceipt`、`parseDemoBillDetail`、`parseDemoBankReceiptResponse` 和
`parseDemoOffsetResponse`：账单 parser 接受并校验 `UNSETTLED`、`PARTIALLY_SETTLED`、
`SETTLED` 各自的权威余额；回款 parser 校验本次可见输入金额而非强制等于账单总额；核销 parser
分别校验部分核销后的 600.00 和最终核销后的 0.00。原有 GET-first、exact replay、payload drift
和响应结构校验不得削弱。

- Bill：页面可见并提交 SERVICE draft、`bill_no`、`bill_date`、`due_date`；复用现有
  `createDemoBill` GET-first wrapper 和 `/bills/demo-from-draft`。草单选项必须明确显示 fee domain，
  不得把 GOV 当 SERVICE。
- Payment：页面可见并提交 bill、amount、`pay_no`、`pay_date`、CNY、`BANK_TRANSFER`、
  `bank_ref_no`、remark；窄幅扩展 `createDemoBankReceipt`，由它接收页面可见 amount 后调用
  `/payments/demo-bank-receipts`，不得继续使用 `bill.balance` 隐式覆盖输入。第一笔固定
  1,200.00；第一笔核销后刷新账单，第二笔只能绑定页面显示的权威余额 600.00。支付方式和
  bank ref 必须真实持久化。
- Offset：页面可见并提交 payment line、bill、amount、`offset_date`；复用
  `createDemoFullOffset` 和 `/offsets/demo-full`。登记回款不得改变账单余额；只有 Offset 成功才
  改变结清状态。

每次动作使用独立 `APP_GENERATED` idempotency key。响应丢失先按 key GET，找到 exact payload
则复用，未找到才允许一次原请求；同 key payload drift 必须 409/no-write。不得改变既有 endpoint、
transaction、状态机或标准非 V6 flow。

## 6. 运行结构

```text
fresh clone / accepted commit
        |
        +-- A: canonical runner -> 2 x headless -> technical receipts
        |
        +-- B: setup-only session
                -> new run root / empty business DB
                -> /demo/inputs preflight
                -> HUMAN or CODEX normal UI 01..11
                -> UI-only receipt and screenshots
                -> explicit close -> exact-root cleanup/archive
```

setup-only 会话复用 `run_local_demo_abc` 的 migration、系统 seed、runtime source 和服务生命周期。
只抽取一个共享的 run-context seam，避免复制环境变量、凭据和 cleanup 规则。A 的默认参数、300 秒
自动超时和两轮语义保持不变；B 没有自动业务写入，且只在显式关闭时结束。

## 7. UI 等价验收

新增独立 strict UI journey，不能 import 当前 hybrid journey。它必须：

1. 从 `/demo/inputs` 证明业务计数全 0、bundle 摘要匹配、分类为 `SYNTHETIC_TEST_ONLY`；
2. 只通过正常页面完成 01–11 的所有正向 mutation；
3. 按 `fpms.demo-v6-ui-parity/v1` 记录并校验每阶段页面、控件、显式输入、来源绑定值、截图、
   mutation 与可见结果；
4. 保存 `ui-input-ledger.json`、`ui-output-ledger.json`、`ui-mutation-ledger.json`、
   Network/console 数组和 pass receipt；
5. 通过传递 import AST 门禁和 runtime action 关联门禁；
6. 满足下面完整 07–11 权威矩阵。

下表每个分号分隔条件都必须成为 `fpms.demo-v6-ui-parity/v1` strict-receipt schema 的独立
`required=true` 字段；validator 不得用一个总布尔值、自由文本或“金额正确”等概括字段代替。

| 阶段 | strict receipt 必填条件 |
| --- | --- |
| 07 | `preview_line_count>=2`；`rate_book_digest`、逐个 `rate_row_digest`、`preview_digest` 精确；preview 前后在同一只读事务视图比较 `CaseActivityEvent`、demo command carrier、`FeeObligation`、`FeeObligationLine`、obligation draft/item links、`FeeDraft`、`FeeItem`、`PayList`、`GovPayment` 的 exact identities/counts，全部无新增或变更；确认后恰好一个 GOV obligation 和一张 GOV draft；900.00+50.00=950.00 |
| 08 | 同案恰好一张 GOV 和一张 SERVICE 且 domain 纯净；恰好一个 adjustment activity、一个 superseding PAY instruction、一个 superseding SERVICE obligation；原 header 精确为 `SUPERSEDED/PAY/NOT_CREATED/UNPAID/NOT_APPLICABLE`，新 header 精确为 `RECOGNIZED/PAY/CREATED/UNPAID/NOT_APPLICABLE`；`adjustment_before_snapshot/digest` 等于原 obligation 完整行集，`adjustment_after_snapshot/digest` 等于新 obligation 完整行集；原 obligation 无 current draft/item links，新 obligation 拥有全部 current links 且一一对应；1,500.00→1,800.00；两张草单锁定后只读 |
| 09 | 恰好一张 PayList、行数等于两条 GOV 行；每行恰好一个 `REGISTERED_PENDING_OFFICIAL_EVIDENCE` GovPayment，receipt/voucher/invoice 全为空；GOV draft 合计 = PayList 合计 = GovPayment 合计 = 950.00；重放 identities/counts 不变；SERVICE 行不进入 PayList |
| 10 | SERVICE superseding obligation payable 合计 = current linked FeeItem 合计 = SERVICE locked draft 合计 = Bill 合计 = 1,800.00；登记第一笔 Payment 不改变账单余额；第一笔 1,200.00 Offset 后 `PARTIALLY_SETTLED`/600.00；刷新页面读取权威 600.00 后登记第二笔；最终恰好两笔 Payment、两个有效 Offset、`SETTLED`/0.00；两笔 Payment 合计 = 两个有效 Offset 合计 = Bill 合计 = 1,800.00；GOV 金额不进入 Bill |
| 11 | 原 SERVICE obligation 仍为 `SUPERSEDED/PAY/NOT_CREATED/UNPAID/NOT_APPLICABLE` 且无 current links；新 SERVICE obligation 为 `RECOGNIZED/PAY/CREATED/UNPAID/NOT_APPLICABLE` 且拥有全部 current links；同案 GOV draft/PayList/GovPayment 身份与合计链完整；同案 SERVICE obligation/draft/Bill/Payment/Offset 身份与合计链完整；GOV 仍待官方凭证、SERVICE 已结清；Network/console 为空；阶段 11 无新写入 |

自动 strict UI run 只是额外技术验证，不能替代真实 actor。最终 UI parity 必须包含两个不同的
fresh run receipt：主持人按 Runbook 完成的 `actor=HUMAN`，以及另一 Codex 账号从远端 fresh
clone 完成的 `actor=CODEX`。两者必须绑定同一 candidate commit、同一合同版本和同一 bundle
摘要，规范化输入/输出完全相同；运行时 ID 只按允许差异规则比较。

## 8. 停止与恢复

出现以下任一项立即停止，不在客户共享屏幕调试：空库非零、输入页事实不符、缺少正常 UI
入口、需要内部 ID、页面首次加载 Network Error、console error、输入值漂移、意外 mutation、
来源/金额不一致、英文新增状态、需要直接 API/DB 或复用旧 run。

失败时停止共享屏幕，保留该 run 的 artifact 和数据库供诊断；修复后必须以新的 run root、run ID、
数据库和业务号重跑。cleanup 只能接受已经验证的 exact run root。

## 9. 变更边界

允许的产品变化仅限：setup-only run seam、透明合成边界条、已确认缺失的正常 UI 操作入口、
strict UI journey、静态反旁路门禁、Runbook/clone 交接。后端既有 endpoint、状态机、权限、事务、
来源、费用算法、schema、migration 和种子事实保持不变。

明确不做：重写 V6 runner、拆成 11 个可恢复子系统、Playwright Inspector、通用工作流设计器、
Docker V6 化、云部署、安全加固、正式客户 bundle、费率变更、相邻 UI 清理或全仓重构。

## 10. 实施顺序与发布条件

1. 独立一行任务对齐过期 migration-head 测试常量，不改 migration。
2. setup-only 会话与空库证据。
3. 阶段 02–06 最小 UI seam。
4. 阶段 08、10 最小 UI seam；07、09、11 只改 UI 驱动测试。
5. strict UI journey、反旁路静态门禁和人工 Runbook。
6. 现有 A 两轮回归、B strict UI、人工演练、另一 Codex 指令演练。
7. 独立 `PROTECTED` 评审 exact commit/range。
8. 从远端全新 clone 复跑后仍只保留 candidate；release ref 必须由独立 release task、明确授权、
   验收 owner、完整 release gate 和回滚合同另行关闭。主工作区清理与归档另行有界执行。

任何一条发布条件未满足，都只允许保留 candidate，不得宣称客户现场已准备完成。
