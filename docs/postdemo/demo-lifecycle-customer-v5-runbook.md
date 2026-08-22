# FPMS 客户全流程演示 V5 Runbook

**用途：** 面向客户，从零演示同一客户、同一案件的证据、OA、授权登记准备、服务费、账单、回款与核销闭环。  
**配套说明页：** `docs/postdemo/demo-lifecycle-customer-v5.html`  
**验证路径：** `scripts/run_demo_integrated_a_rehearsal.py`  
**适用范围：** 本地、虚构数据、`SYNTHETIC_TEST_ONLY` 技术演示。  
**不代表：** 客户正式输入已激活、法定官费已确认、生产部署、产品发布或安全整改完成。

---

## 1. 演示目标与完成标准

本次演示只讲一条主线：

> 从零创建客户和案件，用已复核文件推动案件，完成两轮独立 OA，进入授权登记处理，
> 再从一笔有来源的 SERVICE 服务费生成唯一账单、登记客户回款并完成核销。

演示完成时必须同时看到：

- 同一动态客户 ID、案件 ID 贯穿全部业务对象；
- 12 份演示证据各有独立文件哈希、复核版本和消费结果；
- 第一轮与第二轮 OA 的通知、期限、任务、答复包和回执身份互不复用；
- 案件最终四维状态为：
  `GRANT_REGISTRATION_IN_PROGRESS / GRANT_REGISTRATION / APPLICATION_PENDING / CONFIRMED`；
- 服务费草单为 `LOCKED`，且只包含已配置的 SERVICE 金额；
- AR 账单为 `SETTLED`，余额为 `0.00 CNY`；
- 客户回款为 `FULLY_ALLOCATED`，未核销金额为 `0.00 CNY`；
- 官费、年费和正式客户模板仍显示为“待配置”，没有伪造金额或完成状态；
- 本轮临时数据库和 storage 在演示后已删除，证据目录保留。

建议客户讲解时间为 35–45 分钟。Canonical headed 技术排练本身约 2–3 分钟，
主持人可先用 V5 页面逐阶段讲解，再运行技术排练并展示最终证据。

---

## 2. 必须先讲清楚的事实边界

| 现场看到的内容 | 正确解释 | 不得宣称 |
| --- | --- | --- |
| 递交准备工作包 | 内部递交准备已经建立 | 已向官方系统提交 |
| `APPLICATION_PENDING` | 申请仍处于在途状态 | 已获得生效专利权 |
| 授权登记处理中 | 已复核授权登记来源推动了内部流程 | 专利已经授权并生效 |
| 官费对象数量为 0 | 本轮没有写入任何官费对象 | 官费金额为 0 |
| `官方费用：未配置` | 缺少已激活的正式官费输入 | 官费已缴或无需缴费 |
| 示例服务费 `1,200.00 CNY` | 合成测试输入，有版本、来源和哈希 | 客户正式报价或通用价格 |
| 客户回款 `UNALLOCATED` | 银行回款已登记但尚未核销 | 账单已经结清 |
| 有效 Offset | 回款与账单的实际核销关系 | Payment 创建时即已核销 |
| 最终 `SETTLED / FULLY_ALLOCATED` | 本地技术演示的财务闭环成立 | 产品、生产或发布已批准 |

现场统一使用这句话标注模板和服务费：

> 合成测试输入（SYNTHETIC_TEST_ONLY，非客户授权）

### 当前操作面边界

Canonical 排练使用可见 UI 完成登录、客户/联系人、案件、文书向导、证据上传复核和结果展示；
生命周期命令及部分财务命令使用已经受审的正式 public API owner。它证明真实后端、数据库和
UI 可观测结果，不等于所有命令都已经具备完整的人工客户操作页。演示时不得用“全程纯手工 UI”
描述当前能力。

---

## 3. 每场演示前的数据清空规则

### 3.1 唯一允许的方式：Fresh Run

每场演示都创建新的：

- `FPMS_DEMO_RUN_ID`；
- 独立 SQLite 数据库；
- 独立 storage 目录；
- 独立 synthetic runtime bundle 临时目录；
- 独立演示证据目录。

不得在共享数据库中逐表删除，不得使用通配符、最近创建时间或名称模糊匹配做 cleanup。
Fresh Run 比“删除旧演示行”更安全，也能证明演示确实从零开始。

### 3.2 允许保留/重建的种子数据

Fresh Run 启动时只允许出现：

- 演示管理员和独立证据复核账号；
- 60 条精确官方文书目录种子；
- 演示任务模板；
- 1 条 `OA_OUT` 答复模板；
- 启动时加载的不可变 synthetic runtime bundle：模板、SERVICE 费率和 12 份演示证据。

Runtime bundle 是带哈希的演示输入，不是客户、案件或财务业务对象。

### 3.3 IA-00 必须为零的业务对象

进入客户主线前，下列计数必须全部为 `0`：

| 对象 | 期待计数 |
| --- | ---: |
| 客户 `client` | 0 |
| 联系人 `contact` | 0 |
| 案件 `case` | 0 |
| 工作包 `package` | 0 |
| 任务 `task` | 0 |
| 费用义务 `obligation` | 0 |
| 草单 `draft` | 0 |
| 账单 `bill` | 0 |
| 回款 `payment` | 0 |
| 核销 `offset` | 0 |

任何一个非零都表示本轮不是 fresh run：立即停止，不通过删除记录“修成零”。

### 3.4 启动前检查

在隔离 demo worktree 根目录执行：

```bash
git status --porcelain=v1 -uall
lsof -nP -iTCP:8000 -sTCP:LISTEN
lsof -nP -iTCP:5173 -sTCP:LISTEN
test -x backend/.venv/bin/python
test -x frontend/node_modules/.bin/vite
```

期待结果：

- Git 输出为空；
- 8000 和 5173 没有 listener；
- Python 与 Vite 检查 rc=0。

为本次演示选择一个尚不存在的证据目录，例如：

```bash
DEMO_ARTIFACT=/tmp/fpms-customer-v5-20260822-150000
test ! -e "$DEMO_ARTIFACT"
```

然后启动一次 headed fresh rehearsal：

```bash
PYTHONPATH=backend backend/.venv/bin/python \
  scripts/run_demo_integrated_a_rehearsal.py \
  --artifact "$DEMO_ARTIFACT" \
  --runs 1
```

不要加 `--headless`。演示命令会生成随机本地账号密码，不应打印或保存密码值。

---

## 4. 主持人开场（2 分钟）

打开 `demo-lifecycle-customer-v5.html`，先讲：

> 今天只看一位虚构客户、一个虚构案件。我们从零创建业务对象，随后每一次状态变化都能追溯
> 到已复核文件；最后把一笔有明确来源的服务费走到账单、客户回款和核销。官费、年费和正式
> 客户模板没有获得运行时授权，所以系统会明确显示待配置，不会用硬编码数据代替事实。

屏幕期待：

- 标题为“从案件建立，到证据闭环，再到客户回款”；
- 可见“本地技术演示”“虚构演示数据”“官费未配置不写入”；
- 九阶段顺序完整；
- “最近几周，客户真正能感知的变化”对比表可见。

---

## 5. 逐步演示

## 5.0 零号预检：输入来源与空业务库

**主持人说明**

> 系统先验证本轮输入包，再验证业务库为空。模板和服务费不能只靠名称识别，必须显示版本、
> 来源和 SHA-256。这个输入包只用于本地合成测试，不能自动升级为客户正式配置。

**现场操作**

1. 登录演示管理员账号。
2. 打开 `/demo/abc`。
3. 查看演示输入、模板来源、费率来源和官费状态。

**屏幕输出**

- `演示输入已校验`；
- readiness：`READY`；
- classification：`SYNTHETIC_TEST_ONLY`；
- `customer_activation_eligible=false`；
- bundle ID、bundle version、manifest SHA-256；
- template code、template file SHA-256；
- rate item code、source ref、source version、source SHA-256；
- `官方费用：未配置（不计入总额）`。

**期待与验证**

- 上述 provenance 字段与 bundle manifest 逐项相等；
- 10 类业务对象计数全部为 0；
- 缺少、失效或哈希不一致的 bundle 必须拒绝 readiness，不允许继续写业务对象。

**最近新增**

- 模板和费率由版本、来源、哈希共同识别；
- 客户授权边界与 synthetic 技术演示明确分离。

---

## 5.1 阶段 01：客户、主联系人与案件

**主持人说明**

> 现在开始产生本轮第一个业务对象。后续文件、任务、费用和回款都必须回到这一位客户和这一个
> 案件，不能靠固定 fixture 或旧运行数据拼接。

**现场操作**

1. 打开 `/clients/new`。
2. 创建名称以“虚构集成演示客户”开头的客户，使用本轮唯一客户代码。
3. 进入客户详情的“联系人”页签，新增“虚构主联系人”，设为主联系人。
4. 打开 `/cases/new`，创建本轮唯一案号，关联刚创建的客户并从客户主数据回填申请人。
5. 打开案件详情，再查看账单、回款和核销列表为空。

**输入**

- 客户名称、唯一客户代码、测试邮箱；
- 主联系人姓名、职务、测试邮箱；
- 唯一案号、虚构案件标题、关联客户；
- 费用减缓选择“不减免（0）”。这里的 0 是明确选择的减缓比例，不是未知官费金额。

**屏幕输出**

- 客户详情显示主联系人；
- 案件详情显示同一客户；
- 案件初始 legacy display：`NOT_FILED`；
- 四维投影：`NEW_CASE / NOT_SUBMITTED / NOT_ESTABLISHED / CONFIRMED`；
- package、task、draft、bill、payment、offset 均为 0。

**期待与验证**

- 客户与联系人各恰好 1 条；
- `primary_contact.client_id == client.id`；
- 案件动态 ID 非空，`case.client_id == client.id`；
- 后续步骤必须复用当前 client ID 和 case ID。

**最近新增**

- 每次演示真正从零创建业务对象；
- 动态 ID 成为跨案件、证据和财务页面的唯一关联。

---

## 5.2 阶段 02：文书目录与递交准备

**主持人说明**

> 先验证哪些官方文书可以驱动流程，再建立内部递交准备工作包。准备完成不等于已经向官方提交。

**现场操作**

1. 打开 `/documents/wizard`。
2. 选择“收文”，展开文书模板选项。
3. 展示 60 条 `OFFICIAL_NOTICE_001…060` 目录。
4. 对比一个“可执行”条目与一个“仅供参考”条目。
5. 对当前案件执行递交准备 resolve，再执行一次相同 resolve。
6. 返回案件页查看递交准备工作包。

**屏幕输出**

- 目录恰好 60 行；
- 可执行条目可选择；
- 仅供参考条目禁用；
- 两次 resolve 返回同一个 package ID；
- package kind：`FILING_PREP`；
- 四维投影：`FILING_PREPARATION / NOT_SUBMITTED / NOT_ESTABLISHED / CONFIRMED`。

**期待与验证**

- 模板列表请求不出现 422；
- 重复操作不新增第二个工作包；
- 法律状态仍为 `NOT_SUBMITTED`。

**最近新增**

- 60 类官文目录具有精确身份；
- “可执行”和“仅参考”不再由主持人口头区分；
- 递交准备 resolve 具备已有对象复用语义。

**事实边界**

> 递交准备不等于官方递交。本阶段没有宣称外部提交成功。

---

## 5.3 阶段 03：递交回执、受理与审查证据

**主持人说明**

> 案件不会因为主持人说“已经受理”就改变状态。每一次推进都需要上传文件、形成不可变内容哈希，
> 由另一个复核账号确认，并让生命周期消费这个确切的证据版本。

**现场操作**

按顺序通过文书/附件 UI 上传并复核：

1. `FILING_FINAL_SUBMISSION`；
2. `FILING_RECEIPT`；
3. `ACCEPTANCE_NOTICE`；
4. `PRELIMINARY_EXAMINATION_SOURCE`；
5. `PUBLICATION_NOTICE`；
6. `SUBSTANTIVE_EXAMINATION_SOURCE`。

每份文件都展示：附件 ID、evidence version ID、内容 SHA-256、复核状态和消费结果 ID。

**屏幕输出**

- 递交回执后的四维投影：
  `PROSECUTION_MANAGEMENT / SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE / APPLICATION_PENDING / CONFIRMED`；
- 文件 lineage 保留，不用生成物替换原始证据；
- 进入实审管理后，案件仍保持 `APPLICATION_PENDING`。

**期待与验证**

- 六个角色的附件、版本、哈希和消费结果均非空且互不混用；
- 未复核证据不能推动对应状态；
- UI 显示的案件状态与生命周期权威投影一致。

**最近新增**

- 文件、证据版本、复核结果与生命周期活动形成可追踪链；
- 状态由已复核事实推动，不靠旧 fixture 或口头补状态。

---

## 5.4 阶段 04：第一轮 OA 完整闭环

**主持人说明**

> 第一轮 OA 有自己的通知、完整期限三元组、任务、答复包和回执。创建答复文件不会提前关闭任务；
> 只有正确来源的回执归档后，目标任务才关闭。

**输入**

- 证据角色：`OA_NOTICE_1`；
- synthetic due date：`2026-09-22`；
- source：`MANUAL_OFFICIAL_NOTICE`；
- status：`CONFIRMED`；
- OA 输出：修改后权利要求书、意见陈述 PDF、意见陈述 Word。

该日期只是本轮合成测试输入，不是通用法定期限。

**现场操作与输出**

1. 上传并复核第一轮 OA 通知。
   - 创建、读取、编辑、影响预览和向导回显同一期限三元组。
2. 对 OA 工作包 resolve 两次。
   - 两次得到同一 package ID 和同一 task ID；任务数量为 1。
3. 创建关联 OA_OUT。
   - 只形成 1 条 source/package/reply 关联；package 为 `WAITING_RECEIPT`；task 仍为 `OPEN`。
4. 负向验证：提交错案件回执和同案错来源回执。
   - 两次均返回 4xx；目标 package、task、receipt 前后快照完全一致。
5. 上传正确回执并归档。
   - package 变为 `ARCHIVED`；只关闭第一轮 OA 的 task；案件 legacy display 为 `SUB_EXAM`。

**期待与验证**

- 缺期限三元组或试图改动已确认期限时 fail closed，且 package/task 无新增或变化；
- OA_OUT 创建后任务不关闭；
- 错案、错来源回执不产生业务写入；
- 正确回执只关闭一个目标任务。

**最近新增**

- 五个期限表面保持同一确切事实；
- 错误回执从“难解释”变为可证明的 4xx + no-write；
- OA_OUT 与唯一工作包原子关联。

---

## 5.5 阶段 05：第二轮 OA 独立闭环

**主持人说明**

> 第二轮不是把第一轮对象改个名称。它必须拥有自己的通知、期限、答复包、任务和回执，且第一轮
> 历史在第二轮完成后保持不变。

**输入**

- 证据角色：`OA_NOTICE_2`、`OA_RECEIPT_2`；
- OA sequence：`2`；
- synthetic due date：`2026-10-23`；
- source：`MANUAL_OFFICIAL_NOTICE`；
- status：`CONFIRMED`。

**现场操作**

1. 上传并复核第二轮 OA 通知；
2. 创建第二轮工作包、任务和 OA_OUT；
3. 上传并归档第二轮正确回执；
4. 回看第一轮历史。

**屏幕输出**

- OA2 的 source/package/task/OA_OUT/receipt ID 均与 OA1 不同；
- OA2 task 被关闭；
- OA1 历史前后相等；
- 案件回到 `SUB_EXAM`，四维投影保持
  `PROSECUTION_MANAGEMENT / SUBSTANTIVE_EXAMINATION / APPLICATION_PENDING / CONFIRMED`。

**期待与验证**

- 禁止用 OA sequence 1 的来源重放第二轮；
- 不完整期限三元组不写入；
- 两轮证据链、任务和回执完全隔离。

**最近新增**

- 从单轮 OA 示例扩展为两轮可重复、可追踪、互不污染的闭环。

---

## 5.6 阶段 06：授权登记来源替换与任务门禁

**主持人说明**

> 授权登记通知也必须先成为已复核来源。若收到更新版本，新来源显式替换旧来源；旧任务失效后
> 不能继续生成草单、批量指示、通知或改变等待状态。

**输入**

- 原始角色：`GRANT_NOTICE_ORIGINAL`，synthetic deadline `2026-11-23`；
- 替换角色：`GRANT_NOTICE_REPLACEMENT`，synthetic deadline `2026-11-24`；
- source：`IMPORTED_OFFICIAL_NOTICE`；
- status：`CONFIRMED`；
- replacement metadata：`supersedes_role=GRANT_NOTICE_ORIGINAL`。

**现场操作与输出**

1. 上传、复核并消费原始授权登记通知。
   - 产生一个可操作任务；案件进入
     `GRANT_REGISTRATION_IN_PROGRESS / GRANT_REGISTRATION / APPLICATION_PENDING / CONFIRMED`。
2. 上传并复核替换通知。
   - 新 document/evidence/activity/task ID 与旧对象不同；
   - `supersedes_activity_id` 指向原 activity；只有替换任务可操作。
3. 对旧任务尝试四类修改：生成草单、批量指示、生成通知、标记等待客户。
   - 四次均为 409；每次 before/after 快照相同。
4. 在当前任务记录一次 `PAY`。
   - instruction count 为 1；没有创建官费 item、obligation、draft 或 payable。
5. 尝试在缺少正式官费 authority 时生成官费。
   - 返回 409 / `DEMO_OFFICIAL_FEE_CONFIG_REQUIRED`；业务对象不变化。

**期待与验证**

- 只有替换后的当前任务可修改；
- 来源替换关系和 predecessor task 均可追踪；
- 当前授权任务的 `PAY` 只是客户指示，不产生官费金额或草单；
- 官费 carrier 数量为 0，UI 显示“未配置”，不得解释为官费金额 0。

**最近新增**

- 授权来源替换具有 durable lineage；
- 旧任务四类写操作均 fail closed；
- 客户指示与费用生成解耦。

---

## 5.7 阶段 07：SERVICE 服务费义务与锁定草单

**主持人说明**

> 授权任务的 PAY 不会自动生成费用。现在单独选择有来源的 SERVICE 项目，在服务费义务上记录
> PAY，再生成并锁定草单。官费继续保持未配置。

**现场操作**

1. 打开 `/demo/abc`，查看 SERVICE rate provenance；
2. 创建唯一 SERVICE obligation；
3. 在该 obligation 记录 `PAY`；
4. 生成一张关联草单并锁定；
5. 刷新页面查看草单 ID、金额、币种、状态和来源。

**屏幕输出**

- obligation count：1；
- draft count：1；
- draft status：`LOCKED`；
- service amount：`1,200.00 CNY`；
- official fee display：`未配置`；
- official fee 不计入 total；
- bundle、template、rate 的版本/来源/哈希仍可见。

**期待与验证**

- 草单金额严格等于 bundle 中的 SERVICE amount；
- 只包含 SERVICE line；
- 缺少或损坏费率时不得生成 0 元草单；
- 重试不增加第二个 obligation 或 draft。

**最近新增**

- SERVICE 价格具有 item code、source ref、source version、source SHA-256；
- 未知官费不再被 adapter 或业务逻辑转换成合法的 0；
- 草单锁定后成为唯一账单来源。

---

## 5.8 阶段 08：唯一 AR 账单、客户回款与核销

**主持人说明**

> 这里要区分三个事实：账单是应收，回款是收到钱，核销才是把这笔钱分配到账单。系统不会因为
> 创建 Payment 时填写了目标账单，就提前说账单已经结清。

### 5.8.1 从锁定草单创建唯一账单

**操作与输出**

- 从唯一 `LOCKED` draft 创建 AR bill；
- 首次结果：`UNSETTLED / 1,200.00 CNY`；
- balance：`1,200.00`；
- source draft 只有当前 draft；
- 重放相同 intent 返回同一 bill ID；
- bill count 始终为 1，草单被标记为已消费来源。

**期待结果**

- OPEN 草单、已消费草单或第二个不同 intent 都不能重复开账；
- BillItem 与 draft identity 一致；
- 金额和币种来自锁定草单，不由账单页面重新猜测。

### 5.8.2 登记客户银行回款

**操作与输出**

- 创建 1 笔 `1,200.00 CNY` 银行回款；
- 创建 1 条 PaymentLine；
- 初始 payment status：`UNALLOCATED`；
- unapplied：`1,200.00`；
- `applied_bill_ids=[]`；
- suggested bill 只作为核对上下文，不是已核销事实；
- 重放相同 intent 返回同一 payment ID。

**期待结果**

- 回款登记后账单仍未结清；
- pay_no/idempotency 防止重复回款；
- 回款、line、金额、币种与权威响应一致。

### 5.8.3 执行一次全额核销

**操作与输出**

- 将当前 PaymentLine 的 `1,200.00 CNY` 核销到当前 bill；
- active offset count：1；
- bill：`SETTLED / balance 0.00 CNY`；
- payment：`FULLY_ALLOCATED / unapplied 0.00 CNY`；
- CaseReceipt received：`1,200.00 CNY`。

**期待结果**

- 只存在 1 条有效 offset；
- Bill balance、PaymentLine balance 和 CaseReceipt 投影在同一事务后保持一致；
- 重试不重复扣减或增加第二条有效核销。

### 5.8.4 刷新并跨页面复核

打开或刷新：

- 案件详情；
- 草单详情；
- 账单详情；
- 回款列表；
- 核销列表。

期待各页面 ID 与权威响应一致：

| 页面 | 期待状态 | 期待金额 |
| --- | --- | ---: |
| 案件 | 授权登记处理中 | 客户已收金额 1,200.00 CNY |
| 草单 | `LOCKED` | 1,200.00 CNY |
| 账单 | `SETTLED` | balance 0.00 CNY |
| 回款 | `FULLY_ALLOCATED` | unapplied 0.00 CNY |
| 核销 | active=true | 1,200.00 CNY |

**最近新增**

- 锁定草单只生成一张账单；
- 回款与核销事实分开；
- bill/payment/offset mutation 支持安全重放；
- 页面刷新后继续显示权威状态、金额、币种和对象 ID。

---

## 5.9 阶段 09：正式 runtime input 与后续边界

**主持人说明**

> 当前演示已经完成案件、证据、两轮 OA、授权登记处理和客户服务费财务闭环。正式客户模板、
> 法定官费和年费不会由代码默认值或历史表格自动启用；客户提供并确认后，系统才会验证版本、
> 来源和哈希，再进入对应功能。

**本次不执行**

- 正式客户模板激活；
- 官方申请费、授权登记费或其他官费计算；
- 年费计算、缴费清单或官方支付；
- 外部官方系统直接提交；
- 生产部署、公开 URL、安全或发布验收。

**期待输出**

- UI 显示“待配置”或 `CONFIG_REQUIRED`；
- 不产生官费、年费、PayList 或官方完成状态；
- 不把 synthetic bundle 解释为客户授权输入。

**最近新增**

- runtime input readiness 取代硬编码模板和费率；
- 未配置输入 fail closed，并保持 no-write。

---

## 6. 最近几周成果：客户讲解版

| 之前的演示重点 | 最近几周后的可见成果 | 本次证明方式 |
| --- | --- | --- |
| 页面和宽泛流程阶段 | 文件版本、期限、任务、工作包和活动形成链路 | 12 份 evidence binding 与消费结果 |
| 主要展示一轮 OA | 两轮 OA 保持独立通知、期限、任务、答复包和回执 | OA1/OA2 ID 全部不同，第一轮历史不变 |
| 错误操作难说明 | 错案件/错来源回执 4xx 且目标状态零变化 | 两组独立 before/after 快照 |
| 授权来源更新容易覆盖旧事实 | 原始来源、替换来源和 supersession edge 可追踪 | original/replacement evidence/activity/task lineage |
| 旧任务仍可能被误操作 | 四类过期任务修改全部 409/no-write | 每个操作独立前后快照 |
| 费用示例像固定真值 | SERVICE 来源可见，未知官费保持未配置 | rate provenance + official fee no-write |
| 财务流程停在草单 | LOCKED draft → 唯一 AR bill → bank payment → offset | 最终 SETTLED/FULLY_ALLOCATED/0.00 CNY |
| 重试可能产生重复业务对象 | 账单、回款、核销重放保持同一结果 | 相同 intent 返回同一对象，计数保持 1 |
| 页面状态可能与后端漂移 | 刷新后 ID、状态、金额和币种与权威结果一致 | IA-17 visible surfaces 对账 |

不要把这些成果描述成“大规模重构已经完成”或“生产问题全部解决”。客户价值在于：

- 事实更可追踪；
- 错误输入更安全；
- 两轮 OA 不再串线；
- 费用来源更诚实；
- 客户应收、回款与核销真正闭环。

---

## 7. 现场停止条件与恢复

出现以下任一情况立即停止，不要口头绕过：

| 情况 | 处理 |
| --- | --- |
| IA-00 任一业务计数非零 | 停止；换全新 RUN_ID，不删除共享数据 |
| bundle 不是 `READY/SYNTHETIC_TEST_ONLY` | 停止；核对 manifest/authority/file hashes |
| 8000 或 5173 已被其他进程占用 | 查明精确 PID；只停止已确认的旧 demo 进程 |
| 日志显示 `PermissionError: Operation not permitted` 且 lsof 无 listener | 这是本地端口权限问题，不是“端口已占用”；在正常本地权限下重跑 |
| 非预期 401/403/4xx/5xx | 停止；保留本轮 artifact 和日志，不补数据库 |
| 期待的负向 4xx 后快照变化 | 记录缺陷并停止，不继续正向演示 |
| OA1/OA2 任一身份重复 | 停止；不得把它解释为复用优化 |
| 官费显示数字、已缴或已完成 | 停止；本轮只允许“未配置” |
| bill/payment/offset 计数大于 1 | 停止；保留证据，不手工删重复对象 |
| 页面刷新后 ID、状态、金额或币种不一致 | 停止；以权威响应和数据库事实为准 |

恢复原则：使用新的 RUN_ID 和全新证据目录从 IA-00 重新开始。不要复用失败运行的数据库或
storage，不要在共享工作区执行 `git clean`、`reset` 或数据库通配删除。

---

## 8. 演示结束、清理与证据核验

Canonical runner 无论成功或失败都会在 `finally` 中：

1. 向本轮 local runner 发送终止信号；
2. 等待并终止本轮 8000/5173 子进程；
3. 校验 cleanup target 位于系统临时目录且名称以
   `fpms-demo-abc-integrated-r` 开头；
4. 删除本轮 SQLite、`-wal/-shm`、storage 和临时运行目录；
5. 写入 `run1/cleanup.json`。

结束后执行：

```bash
test "$(jq -r '.run_root_removed' "$DEMO_ARTIFACT/run1/cleanup.json")" = "true"
lsof -nP -iTCP:8000 -sTCP:LISTEN
lsof -nP -iTCP:5173 -sTCP:LISTEN
(cd "$DEMO_ARTIFACT" && shasum -a 256 -c checksums.sha256)
```

期待结果：

- `run_root_removed=true`；
- 8000/5173 没有 listener；
- `checksums.sha256` 全部 `OK`。

保留以下非敏感证据：

- `candidate.json`；
- `summary.json`；
- `run1/task9-checkpoints.json`；
- `run1/evidence-role-map.json`；
- `run1/integrated-final.png`；
- `run1/playwright.log`、`runner.log`；
- `run1/cleanup.json`；
- `checksums.sha256`。

不要保存 token、密码、Authorization header 或完整 HAR。

---

## 9. 成功判定

只有同时满足以下条件，本次才可称为：

> LOCAL SYNTHETIC INTEGRATED TECHNICAL DEMO PASS

- [ ] IA-00…IA-18 各出现且只出现一次；
- [ ] checkpoint count = 19；
- [ ] evidence binding count = 12；
- [ ] 9 个核心业务 ID 全部非空且互不重复；
- [ ] OA1/OA2 身份独立；
- [ ] 授权原始/替换来源和 supersession 关系完整；
- [ ] 官费相关对象没有写入，UI 为“未配置”；
- [ ] draft = `LOCKED`；
- [ ] bill = `SETTLED / 0.00 CNY`；
- [ ] payment = `FULLY_ALLOCATED / 0.00 CNY`；
- [ ] active offset count = 1；
- [ ] final screenshot 非空并目视一致；
- [ ] cleanup = true；
- [ ] artifact checksums 全部通过；
- [ ] 工作区仍为 clean；
- [ ] 8000/5173 已释放。

该结论仍不得缩写为 `PRODUCT_READY`、`PRODUCTION_READY` 或 `RELEASE_PASS`。

---

## 10. 本 Runbook 的验证记录

本节在 runbook 生成后使用同一现有 runner 做一次 fresh headed rehearsal，并记录实际结果。
验证只覆盖本文档描述的本地 synthetic demo，不扩展到产品、生产或发布。

| 字段 | 本轮结果 |
| --- | --- |
| 验证日期 | 待执行 |
| Candidate commit/tree | 待执行 |
| Artifact | 待执行 |
| RUN_ID | 待执行 |
| Playwright | 待执行 |
| Checkpoints | 待执行 |
| Evidence bindings | 待执行 |
| Final lifecycle | 待执行 |
| Final bill/payment | 待执行 |
| Cleanup | 待执行 |
| Checksums | 待执行 |
| Verdict | 待执行 |

---

## 11. 一页主持人速查

1. **边界：** 本地、虚构、synthetic；官费未配置不写入。  
2. **从零：** 业务计数 10 项全部为 0。  
3. **客户案件：** 动态客户/联系人/案件 ID 贯穿全程。  
4. **递交准备：** 60 类官文，可执行与参考分开；准备不等于提交。  
5. **证据审查：** 状态只由已复核版本推动。  
6. **两轮 OA：** 各自通知、期限、任务、答复包、回执；错误回执 no-write。  
7. **授权登记：** 来源可替换，旧任务不可写；PAY 不自动生成官费。  
8. **服务费：** 来源可见；1,200.00 CNY 是 synthetic；官费仍未配置。  
9. **客户财务：** LOCKED 草单 → 唯一账单 → 银行回款 → 唯一核销。  
10. **收口：** SETTLED / FULLY_ALLOCATED / 0.00 CNY；清理临时 DB/storage。  
11. **最后一句：** 今天证明的是可追踪、可拒绝错误、可安全重试的客户旅程，不是生产发布。
