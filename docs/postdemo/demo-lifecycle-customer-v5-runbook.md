# FPMS 客户全流程演示 V5 Runbook

- **用途：** 面向客户，从零演示同一客户、同一案件的证据、OA、授权登记准备、服务费、账单、回款与核销闭环。
- **配套说明页：** `docs/postdemo/demo-lifecycle-customer-v5.html`
- **验证路径：** `scripts/run_demo_integrated_a_rehearsal.py`
- **适用范围：** 本地、合成测试数据、`SYNTHETIC_TEST_ONLY` 技术演示。
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
- 案件最终在客户屏幕显示“授权登记中 / 授权登记 / 申请审理中 / 已确认”；
- 技术/API 验收四维值为：
  `GRANT_REGISTRATION_IN_PROGRESS / GRANT_REGISTRATION / APPLICATION_PENDING / CONFIRMED`；
- 服务费草单为 `LOCKED`，且只包含已配置的 SERVICE 金额；
- AR 账单为 `SETTLED`，余额为 `0.00 CNY`；
- 客户回款为 `FULLY_ALLOCATED`，未核销金额为 `0.00 CNY`；
- 官费、年费和正式客户模板仍显示为“待配置”，没有伪造金额或完成状态；
- 本轮临时数据库和 storage 在演示后已删除，证据目录保留。

建议客户讲解时间为 35–45 分钟。Canonical headed 技术排练本身约 2–3 分钟，
主持人可先用 V5 页面逐阶段讲解，再运行技术排练并展示最终证据。

本轮普通业务字段固定为同一组真实形态值；合成测试属性在表外统一标注，不写入客户名、联系人名或文书标题：

| 业务字段 | 本轮值 |
| --- | --- |
| 客户 / 客户代码 | 澄岳智造技术（苏州）有限公司 / `CYZN-<run suffix>` |
| 主联系人 | 周岚 / 知识产权经理 / `zhou.lan@chengyue-ip.example` |
| 案号 / 案名 | `CYIP-CN-INV-<run suffix>` / 一种柔性制造产线中视觉检测工位的自适应标定方法 |
| 服务项目 | 授权登记阶段代理服务费 / `1,200.00 CNY` |
| 财务业务号 | `AR-CYZN-<run suffix>` / `RCPT-CYZN-<run suffix>` / `BTR-CYZN-<run suffix>` |
| 递交与审查文书 | 发明专利请求书及申请文件；发明专利申请递交回执；发明专利申请受理通知书；发明专利申请初步审查合格通知书；发明专利申请公布通知书；发明专利申请进入实质审查阶段通知书 |
| 两轮 OA | 第一次审查意见通知书；第一次审查意见答复递交回执；第二次审查意见通知书；第二次审查意见答复递交回执 |
| 授权登记来源 | 办理登记手续通知书（原始版本）；办理登记手续通知书（更新版本） |

整组场景边界：`SYNTHETIC_TEST_ONLY`、customer activation false、非客户授权、非生产输入。

---

## 2. 必须先讲清楚的事实边界

| 现场看到的内容 | 正确解释 | 不得宣称 |
| --- | --- | --- |
| 递交准备工作包 | 内部递交准备已经建立 | 已向官方系统提交 |
| 申请审理中（技术值 `APPLICATION_PENDING`） | 申请仍处于在途状态 | 已获得生效专利权 |
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
INTEGRATED_DEPS=/private/tmp/fpms-integrated-deps.HRGhrj
test -d "$INTEGRATED_DEPS"
PYTHONPATH="$INTEGRATED_DEPS:backend" python3 -c 'import pytest, openpyxl, pypdf'
test -x frontend/node_modules/.bin/vite
```

期待结果：

- Git 输出为空；
- 8000 和 5173 没有 listener；
- Integrated A 测试依赖根与 Vite 检查 rc=0。

不要只使用 `backend/.venv/bin/python` 启动本 runner：该环境是产品运行依赖，未必包含 runner
构造 synthetic bundle 时使用的 test-only `pytest`。演示机必须使用已经验证的
`INTEGRATED_DEPS`；如果该目录不存在，停止并恢复已接受的演示依赖环境，不要现场安装未知版本。

为本次演示选择一个尚不存在的证据目录，例如：

```bash
DEMO_ARTIFACT=/tmp/fpms-customer-v5-20260822-150000
test ! -e "$DEMO_ARTIFACT"
```

然后启动一次 headed fresh rehearsal：

```bash
PYTHONPATH="$INTEGRATED_DEPS:backend" python3 \
  scripts/run_demo_integrated_a_rehearsal.py \
  --artifact "$DEMO_ARTIFACT" \
  --runs 1
```

不要加 `--headless`。演示命令会生成随机本地账号密码，不应打印或保存密码值。

---

## 4. 主持人开场（2 分钟）

打开 `demo-lifecycle-customer-v5.html`，先讲：

> 今天只看一套合成测试场景中的一位客户、一个案件。我们从零创建业务对象，随后每一次状态变化都能追溯
> 到已复核文件；最后把一笔有明确来源的服务费走到账单、客户回款和核销。官费、年费和正式
> 客户模板没有获得运行时授权，所以系统会明确显示待配置，不会用硬编码数据代替事实。

屏幕期待：

- 标题为“从案件建立，到证据闭环，再到客户回款”；
- 可见“本地技术演示”“合成测试数据”“官费未配置不写入”；
- 九阶段顺序完整；
- “最近几周，客户真正能感知的变化”对比表可见。

---

## 5. 逐步演示

## 5.0 后台预检（不计入 01–09 客户阶段）

**主持人说明**

> 系统先验证本轮输入包，再验证业务库为空。模板和服务费不能只靠名称识别，必须显示版本、
> 来源和 SHA-256。这个输入包只用于本地合成测试，不能自动升级为客户正式配置。

**现场操作**

1. 登录演示管理员账号。
2. 在客户操作开始前，由主持人打开未加入产品菜单的只读页面 `/demo/inputs`。
3. 点击“校验演示输入与空业务库”，查看输入来源、费率来源、官费状态和十类业务对象计数。
4. 校验成功后，在同一浏览器会话中保留一个不共享的 `/demo/abc` 标签页，点击“校验全新演示环境”；确认该控制页显示“演示输入已校验”后保持标签页打开，直到阶段 07 再使用。

> `/demo/inputs` 是主持人可选择展示的只读输入页；`/demo/abc` 始终留在不共享标签页。两次
> 读取发生在业务对象仍为零时，不会产生客户、案件或财务写入，也不得在阶段 07 重新 preflight。

**屏幕输出**

- 只读页显示“就绪状态：`READY`”；
- classification：`SYNTHETIC_TEST_ONLY`；
- `customer_activation_eligible=false`；
- bundle ID、bundle version、manifest SHA-256；
- template code、template file SHA-256；
- rate item code、source ref、source version、source SHA-256；
- `官方费用：未配置（不计入总额）`。

不共享的控制标签页另显示“演示输入已校验”；该行不是客户业务页面输出。

**期待与验证**

- 上述 provenance 字段与 bundle manifest 逐项相等；
- 10 类业务对象计数全部为 0；
- 缺少、失效或哈希不一致的 bundle 必须拒绝 readiness，不允许继续写业务对象。

**最近新增**

- 模板和费率由版本、来源、哈希共同识别；
- 客户授权边界与 synthetic 技术演示明确分离。

---

## 5.1 阶段 01：客户、主联系人与案件

**主持人话术**

> 现在从澄岳智造技术（苏州）有限公司、主联系人周岚和同一件发明申请开始。后续文件、任务、
> 费用和回款都必须回到这一位客户和这一个案件。

**界面/动作**

1. 打开 `/clients/new`。
2. 创建“澄岳智造技术（苏州）有限公司”，使用本轮唯一客户代码。
3. 进入客户详情的“联系人”页签，新增“周岚”，设为主联系人。
4. 打开 `/cases/new`，创建本轮唯一案号，关联刚创建的客户并从客户主数据回填申请人。
5. 打开案件详情，再查看账单、回款和核销列表为空。

**输入**

- 客户名称“澄岳智造技术（苏州）有限公司”、客户代码 `CYZN-<run suffix>`；
- 主联系人“周岚”、职务“知识产权经理”、保留邮箱 `zhou.lan@chengyue-ip.example`；
- 案号 `CYIP-CN-INV-<run suffix>`、案名“一种柔性制造产线中视觉检测工位的自适应标定方法”、关联客户；
- 费用减缓选择“不减免（0）”。这里的 0 是明确选择的减缓比例，不是未知官费金额。

**屏幕输出**

- 客户详情显示主联系人；
- 案件详情显示同一客户；
- 案件页显示“未递交”；
- 中央主线显示“新建案件 / 尚未递交 / 权利尚未成立 / 已确认”；
- package、task、draft、bill、payment、offset 均为 0。

**预期结果**

- 客户、联系人、案件各恰好 1 条；
- 同一客户和案件贯穿后续所有对象。

**验证**

- 客户与联系人各恰好 1 条；
- `primary_contact.client_id == client.id`；
- 案件内部技术 ID 非空，`case.client_id == client.id`；客户讲解以客户代码和案号为业务含义；
- 技术/API 四维值为 `NEW_CASE / NOT_SUBMITTED / NOT_ESTABLISHED / CONFIRMED`；
- 后续步骤必须复用当前 client ID 和 case ID。

**事实边界**

普通业务字段不带“演示/虚构”占位词；整组数据仍受 `SYNTHETIC_TEST_ONLY` 边界约束。

**本阶段停止条件**

业务库不为空、出现重复对象、联系人或案件关联不一致、客户代码/案号不符合本轮前缀时立即停止。

**最近新增**

- 每次演示真正从零创建业务对象；
- 真实业务形态的动态代码与内部技术身份共同贯穿证据和财务链路。

---

## 5.2 阶段 02：文书目录与递交准备

**主持人话术**

> 本阶段验证模板来源、目录行为与递交准备工作包复用；不声称运行时模板预览。

**界面/动作**

1. 引用后台预检已校验的 template code 与 file SHA-256，不打开模板预览。
2. 打开 `/documents/wizard`，选择“收文”，展示 60 条 `OFFICIAL_NOTICE_001…060`。
3. 对比一个“可执行”条目与一个“仅供参考”条目。
4. 对 `CYIP-CN-INV-<run suffix>` 执行递交准备 resolve，再执行一次相同 resolve。
5. 返回案件页查看递交准备工作包。

**输入**

- 后台已校验的 template code 与 template file SHA-256；
- 60 条精确文书目录；
- 当前案号 `CYIP-CN-INV-<run suffix>`。

**屏幕输出**

- 目录恰好 60 行；
- 可执行条目可选择；
- 仅供参考条目禁用；
- 两次 resolve 返回同一个 package ID；
- 工作包类型显示“递交准备”；
- 中央主线显示“递交准备 / 尚未递交 / 权利尚未成立 / 已确认”。

**预期结果**

- 可执行/仅参考行为与目录配置一致；
- 重复 resolve 复用同一工作包。

**验证**

- 模板列表请求不出现 422；
- 重复操作不新增第二个工作包；
- 技术/API 工作包类型为 `FILING_PREP`，四维值为
  `FILING_PREPARATION / NOT_SUBMITTED / NOT_ESTABLISHED / CONFIRMED`；
- 官方程序阶段仍为 `NOT_SUBMITTED`，法律状态仍为 `NOT_ESTABLISHED`。

**最近新增**

- 60 类官文目录具有精确身份；
- “可执行”和“仅参考”不再由主持人口头区分；
- 递交准备 resolve 具备已有对象复用语义。

**事实边界**

> 递交准备不等于官方递交。本阶段没有运行时模板预览，也没有宣称外部提交成功。

**本阶段停止条件**

模板 provenance 不一致、目录不是 60 行、可执行/仅参考行为错误，或重复 resolve 产生第二个工作包时停止。

---

## 5.3 阶段 03：递交回执、受理与审查证据

**主持人话术**

> 案件不会因为主持人说“已经受理”就改变状态。每一次推进都需要上传文件、形成不可变内容哈希，
> 由另一个复核账号确认，并让生命周期消费这个确切的证据版本。

**界面/动作**

按顺序通过文书/附件 UI 上传并复核：

1. `FILING_FINAL_SUBMISSION` — 发明专利请求书及申请文件；
2. `FILING_RECEIPT` — 发明专利申请递交回执；
3. `ACCEPTANCE_NOTICE` — 发明专利申请受理通知书；
4. `PRELIMINARY_EXAMINATION_SOURCE` — 发明专利申请初步审查合格通知书；
5. `PUBLICATION_NOTICE` — 发明专利申请公布通知书；
6. `SUBSTANTIVE_EXAMINATION_SOURCE` — 发明专利申请进入实质审查阶段通知书。

每份文件都展示：附件 ID、evidence version ID、内容 SHA-256、复核状态和消费结果 ID。

**输入**

上述六份自然中文标题的合成证据文件；技术角色保持 `FILING_*`、`ACCEPTANCE_NOTICE`、
`PRELIMINARY_EXAMINATION_SOURCE`、`PUBLICATION_NOTICE`、`SUBSTANTIVE_EXAMINATION_SOURCE`。

**屏幕输出**

- 递交回执后中央主线显示“流程管理 / 递交已确认，等待受理 / 申请审理中 / 已确认”；
- 文件 lineage 保留，不用生成物替换原始证据；
- 进入实审管理后，案件仍显示“申请审理中”。

**预期结果**

- 六份文件各自形成已复核证据版本并由对应生命周期动作消费；
- 案件由等待受理推进到实质审查，原始证据链保留。

**验证**

- 六个角色的附件、版本、哈希和消费结果均非空且互不混用；
- 未复核证据不能推动对应状态；
- 递交回执后的技术/API 四维值为
  `PROSECUTION_MANAGEMENT / SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE / APPLICATION_PENDING / CONFIRMED`；
- UI 显示的案件状态与生命周期权威投影一致。

**事实边界**

内部记录外部操作不等于 FPMS 直接连接官方系统完成提交；未复核证据不得推动状态。

**本阶段停止条件**

任何证据未复核、身份/哈希复用、消费结果缺失，或页面状态与权威投影不一致时停止。

**最近新增**

- 文件、证据版本、复核结果与生命周期活动形成可追踪链；
- 状态由已复核事实推动，不靠旧 fixture 或口头补状态。

---

## 5.4 阶段 04：第一轮 OA 完整闭环

**主持人话术**

> 第一轮 OA 有自己的通知、完整期限三元组、任务、答复包和回执。创建答复文件不会提前关闭任务；
> 只有正确来源的回执归档后，目标任务才关闭。

**输入**

- `OA_NOTICE_1`：第一次审查意见通知书；
- `OA_RECEIPT_1`：第一次审查意见答复递交回执；
- synthetic due date：`2026-09-22`；
- source：`MANUAL_OFFICIAL_NOTICE`；
- status：`CONFIRMED`；
- OA 输出：修改后权利要求书、意见陈述 PDF、意见陈述 Word。

该日期只是本轮合成测试输入，不是通用法定期限。

**界面/动作**

1. 上传并复核第一轮 OA 通知。
   - 创建、读取、编辑、影响预览和向导回显同一期限三元组。
2. 对 OA 工作包 resolve 两次。
   - 两次得到同一 package ID 和同一 task ID；任务数量为 1。
3. 创建关联 OA_OUT。
   - 只形成 1 条 source/package/reply 关联；package 为 `WAITING_RECEIPT`；task 仍为 `OPEN`。
4. 负向验证：提交错案件回执和同案错来源回执。
   - 两次均返回 4xx；目标 package、task、receipt 前后快照完全一致。
5. 上传正确回执并归档。
   - package 变为 `ARCHIVED`；只关闭第一轮 OA 的 task；案件页显示“实质审查”。

**屏幕输出**

- 五个期限表面显示同一确认日期、来源与状态；
- OA_OUT 后任务仍开放；正确回执后工作包归档并只关闭目标任务；
- 两个错误回执均为 4xx，前后快照相同。

**预期结果**

- 第一轮通知、答复包、任务、答复文件与回执形成唯一闭环；
- 错案/错来源输入不产生业务写入。

**验证**

- 缺期限三元组或试图改动已确认期限时 fail closed，且 package/task 无新增或变化；
- OA_OUT 创建后任务不关闭；
- 错案、错来源回执不产生业务写入；
- 正确回执只关闭一个目标任务。

**事实边界**

确认日期是本轮合成测试输入，不是通用法定期限；OA_OUT 创建本身不代表官方回执已归档。

**本阶段停止条件**

期限三元组缺失或漂移、错误回执改变快照、OA_OUT 提前关闭任务或关闭非目标任务时停止。

**最近新增**

- 五个期限表面保持同一确切事实；
- 错误回执从“难解释”变为可证明的 4xx + no-write；
- OA_OUT 与唯一工作包原子关联。

---

## 5.5 阶段 05：第二轮 OA 独立闭环

**主持人话术**

> 第二轮不是把第一轮对象改个名称。它必须拥有自己的通知、期限、答复包、任务和回执，且第一轮
> 历史在第二轮完成后保持不变。

**输入**

- `OA_NOTICE_2`：第二次审查意见通知书；
- `OA_RECEIPT_2`：第二次审查意见答复递交回执；
- OA sequence：`2`；
- synthetic due date：`2026-10-23`；
- source：`MANUAL_OFFICIAL_NOTICE`；
- status：`CONFIRMED`。

**界面/动作**

1. 上传并复核第二轮 OA 通知；
2. 创建第二轮工作包、任务和 OA_OUT；
3. 上传并归档第二轮正确回执；
4. 回看第一轮历史。

**屏幕输出**

- OA2 的 source/package/task/OA_OUT/receipt ID 均与 OA1 不同；
- OA2 task 被关闭；
- OA1 历史前后相等；
- 案件页回到“实质审查”，中央主线保持“流程管理 / 实质审查 / 申请审理中 / 已确认”。

**预期结果**

- 第二轮 source/package/task/OA_OUT/receipt 与第一轮全部不同；
- 第二轮关闭后第一轮历史保持不变。

**验证**

- 禁止用 OA sequence 1 的来源重放第二轮；
- 不完整期限三元组不写入；
- 技术/API 四维值保持
  `PROSECUTION_MANAGEMENT / SUBSTANTIVE_EXAMINATION / APPLICATION_PENDING / CONFIRMED`；
- 两轮证据链、任务和回执完全隔离。

**事实边界**

第二轮不得复用第一轮证据、期限或任务；确认日期仍是本轮合成测试输入。

**本阶段停止条件**

任一身份重复、第一轮历史变化、不完整期限被接受或错误任务被关闭时停止。

**最近新增**

- 从单轮 OA 示例扩展为两轮可重复、可追踪、互不污染的闭环。

---

## 5.6 阶段 06：授权登记来源替换与任务门禁

**主持人话术**

> 授权登记通知也必须先成为已复核来源。若收到更新版本，新来源显式替换旧来源；旧任务失效后
> 不能继续生成草单、批量指示、通知或改变等待状态。

**输入**

- 原始角色 `GRANT_NOTICE_ORIGINAL`：办理登记手续通知书（原始版本），synthetic deadline `2026-11-23`；
- 替换角色 `GRANT_NOTICE_REPLACEMENT`：办理登记手续通知书（更新版本），synthetic deadline `2026-11-24`；
- source：`IMPORTED_OFFICIAL_NOTICE`；
- status：`CONFIRMED`；
- replacement metadata：`supersedes_role=GRANT_NOTICE_ORIGINAL`。

**界面/动作**

1. 上传、复核并消费原始授权登记通知。
   - 产生一个可操作任务；案件中央主线显示“授权登记中 / 授权登记 / 申请审理中 / 已确认”。
2. 上传并复核替换通知。
   - 新 document/evidence/activity/task ID 与旧对象不同；
   - `supersedes_activity_id` 指向原 activity；只有替换任务可操作。
3. 对旧任务尝试四类修改：生成草单、批量指示、生成通知、标记等待客户。
   - 四次均为 409；每次 before/after 快照相同。
4. 在当前任务记录一次 `PAY`。
   - instruction count 为 1；没有创建官费 item、obligation、draft 或 payable。
5. 尝试在缺少正式官费 authority 时生成官费。
   - 返回 409 / `DEMO_OFFICIAL_FEE_CONFIG_REQUIRED`；业务对象不变化。

**屏幕输出**

- 案件显示“授权登记中 / 授权登记 / 申请审理中 / 已确认”；
- 更新来源指向原 activity，只有更新任务可操作；
- 当前 PAY 恰好一条，官费 carrier 数量为 0。

**预期结果**

- 来源替换关系可追踪；
- 旧任务四类写入全部 409/no-write；当前 PAY 不生成官费。

**验证**

- 只有替换后的当前任务可修改；
- 来源替换关系和 predecessor task 均可追踪；
- 技术/API 四维值为
  `GRANT_REGISTRATION_IN_PROGRESS / GRANT_REGISTRATION / APPLICATION_PENDING / CONFIRMED`；
- 当前授权任务的 `PAY` 只是客户指示，不产生官费金额或草单；
- 官费 carrier 数量为 0，UI 显示“未配置”，不得解释为官费金额 0。

**事实边界**

授权登记处理中不表示专利已生效；当前任务 PAY 不生成官费金额、义务或草单。

**本阶段停止条件**

替换边缺失、旧任务可写、PAY 重复、出现任何官费对象/金额或页面投影不一致时停止。

**最近新增**

- 授权来源替换具有 durable lineage；
- 旧任务四类写操作均 fail closed；
- 客户指示与费用生成解耦。

---

## 5.7 阶段 07：SERVICE 服务费义务与锁定草单

**主持人话术**

> 授权任务的 PAY 不会自动生成费用。现在单独选择“授权登记阶段代理服务费”，在服务费义务上
> 记录 PAY，再生成并锁定草单。官费继续保持未配置。

**界面/动作**

1. 主持人不共享控制页：在 `/demo/abc` 复核 SERVICE rate provenance，并仅创建唯一 SERVICE obligation；
2. 客户共享费用页与草单页：立即切回正常案件详情“费用”页签，查看刚创建的服务费义务；
3. 在正常费用页签点击“记录支付指示”，确认该 obligation 的客户指示变为 `PAY`；
4. 从“创建关联费用草稿”进入正常草单页面，创建并锁定唯一草单；
5. 在案件费用页签和草单详情页刷新，复核草单 ID、金额、币种、状态和来源。

> `/demo/abc` 只承担合成演示数据的主持人控制，不加入任何产品菜单，也不投放到客户共享屏幕。

**输入**

- 服务项目：授权登记阶段代理服务费；
- 业务费项代码：`SVC_GRANT_REGISTRATION_CN`；
- 金额：`1,200.00 CNY`，保持 active synthetic bundle 的精确值；
- rate item code、source ref、source version、source SHA-256。

**屏幕输出**

- obligation count：1；
- draft count：1；
- draft status：`LOCKED`；
- service amount：`1,200.00 CNY`；
- official fee display：`未配置`；
- official fee 不计入 total；
- bundle、template、rate 的版本/来源/哈希仍可见。

**预期结果**

- 唯一 SERVICE obligation 与唯一 `LOCKED` 草单；
- 草单只含 SERVICE line，官费继续未配置。

**验证**

- 草单金额严格等于 bundle 中的 SERVICE amount；
- 只包含 SERVICE line；
- 缺少或损坏费率时不得生成 0 元草单；
- 重试不增加第二个 obligation 或 draft。

**事实边界**

`1,200.00 CNY` 是 `SYNTHETIC_TEST_ONLY` 输入，不是官方费用或客户报价；未知官费不写成 0。

**本阶段停止条件**

控制页进入共享屏幕、服务费名称/来源不匹配、草单未锁定或重复、出现官费金额时停止。

**最近新增**

- SERVICE 价格具有 item code、source ref、source version、source SHA-256；
- 未知官费不再被 adapter 或业务逻辑转换成合法的 0；
- 草单锁定后成为唯一账单来源。

---

## 5.8 阶段 08：唯一 AR 账单、客户回款与核销

**主持人话术**

> 这里要区分三个事实：账单是应收，回款是收到钱，核销才是把这笔钱分配到账单。系统不会因为
> 创建 Payment 时填写了目标账单，就提前说账单已经结清。

> 主持人不共享控制页：账单、回款和核销命令只在 `/demo/abc` 触发；客户共享账单、回款、核销与案件权威读页，
> 并在每次动作后刷新复核。

**界面/动作**

依次触发唯一 AR 账单、银行回款和一次全额核销；每个命令后切回正常权威读页核对结果。

**输入**

- 账单号 `AR-CYZN-<run suffix>`；
- 回款号 `RCPT-CYZN-<run suffix>`；
- 银行参考号 `BTR-CYZN-<run suffix>`；
- 金额 `1,200.00 CNY`，来源为唯一锁定草单。

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

**屏幕输出**

客户共享权威读页先显示 `UNSETTLED / UNALLOCATED`，核销后显示
`SETTLED / FULLY_ALLOCATED / 0.00 CNY / 0.00 CNY`，并显示上述真实形态业务号。

**预期结果**

- bill、payment、offset 各恰好 1 个有效对象；
- 重放返回同一业务对象；
- 账单、回款、核销与案件收款投影一致。

**验证**

Canonical IA-14 至 IA-18 从正常账单、回款、核销和案件页面核对业务号、状态、金额、余额、币种与最终截图。

**事实边界**

回款登记不等于已经核销；只有有效 offset 才建立账单关联并使账单结清。

**本阶段停止条件**

控制页进入共享屏幕、业务号前缀错误、任一计数大于 1、回款创建即结清或权威读页不一致时停止。

**最近新增**

- 锁定草单只生成一张账单；
- 回款与核销事实分开；
- bill/payment/offset mutation 支持安全重放；
- 页面刷新后继续显示权威状态、金额、币种和对象 ID。

---

## 5.9 阶段 09：正式 runtime input 与后续边界

**主持人话术**

> 这是口头说明与配置边界：当前演示已经完成案件、证据、两轮 OA、授权登记处理和客户服务费财务闭环。正式客户模板、
> 法定官费和年费不会由代码默认值或历史表格自动启用；客户提供并确认后，系统才会验证版本、
> 来源和哈希，再进入对应功能。

**界面/动作**

本阶段不操作产品页面；主持人回到 V5 说明页，口头列出未执行和待配置事项。

**输入**

无本轮运行时输入。正式客户模板、官费与年费 bundle 均未提供或激活。

**本次不执行**

- 正式客户模板激活；
- 官方申请费、授权登记费或其他官费计算；
- 年费计算、缴费清单或官方支付；
- 外部官方系统直接提交；
- 生产部署、公开 URL、安全或发布验收。

**屏幕输出**

- 无新增产品 UI 观察；仅展示本说明页的配置边界文字；
- 前序权威读取仍证明未产生官费对象或官方完成状态。

**预期结果**

主持人明确列出未执行事项，不把未来能力或配置入口讲成当前已观察页面。

**验证**

本阶段验证的是话术/配置边界。Canonical 只以官费 no-write 与本轮最终状态支持边界，
不证明正式模板激活、年费计算或缴费 UI。

**事实边界**

不声称已观察正式模板、官费、年费、PayList 或官方支付页面；不把 synthetic bundle 解释为客户授权输入。

**本阶段停止条件**

任何人把待配置事项描述为已实现、已观察、已激活或已完成时立即停止并纠正。

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

## 10. 本 Runbook 的历史基线验证记录

本节仅保留 runbook 生成时使用同一现有 runner 完成的历史基线 headed rehearsal。它不是
当前任务或当前 candidate 的自证；当前候选必须由 task-local evidence 和独立 High review 另行
绑定。该历史记录只覆盖本文档描述的本地 synthetic demo，不扩展到产品、生产或发布。

| 字段 | 历史基线结果 |
| --- | --- |
| 验证日期 | 2026-08-22（Asia/Shanghai） |
| Candidate commit/tree | `06b5813dab1d4a027ec989b5f3c1edff2c997998` / `bd257fca30ec2eab0595040b62f205be37d83305` |
| Artifact | `/tmp/fpms-customer-v5-runbook-06b5813-01` |
| RUN_ID | `integrated-r1-7f37c5c5aaca` |
| Playwright | headed Chromium，`1 passed (2.1m)` |
| Checkpoints | IA-00…IA-18，19/19，各一次 |
| Evidence bindings | 12/12 |
| Final lifecycle（技术/API） | `GRANT_REGISTRATION_IN_PROGRESS / GRANT_REGISTRATION / APPLICATION_PENDING / CONFIRMED` |
| Final bill/payment | `SETTLED / FULLY_ALLOCATED / 0.00 CNY / 0.00 CNY` |
| Cleanup | `run_root_removed=true`；8000/5173 已释放 |
| Checksums | 20/20 `OK` |
| Verdict | `LOCAL SYNTHETIC INTEGRATED TECHNICAL DEMO PASS` |

历史基线验证前的命令灵敏度检查曾用 `backend/.venv/bin/python` 启动 runner，并在 bundle 构建前因
缺少 test-only `pytest` 明确失败；当时没有启动服务或写入业务数据。Runbook 已将入口修正为
既有 `INTEGRATED_DEPS`，随后使用全新 artifact/RUN_ID 完成上述 PASS。该失败证明依赖预检能够
阻止“环境不完整但继续演示”的假成功。

---

## 11. 一页主持人速查

1. **边界：** 本地、合成测试、synthetic；官费未配置不写入。
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
