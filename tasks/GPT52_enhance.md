# FPMS 安全增强计划（先补齐 MVP1 Scope GAP，再逐步对齐 SPEC 2.0）

> 生成日期：2026-02-23  
> 依据输入：`00_mvp1_scope.md`、`mvp1_gap.md`、`mvp_story_gap.md`、`FPMS SPEC 2.0.md`（仅用于核对优先级与术语一致性）

---

## 0. 目标与边界

### 0.1 总目标（两阶段）
1) **先补齐「现有实现」与「MVP1 Scope」之间的差距**：确保 MVP1 的“可演示、可落地、可回归”的核心业务闭环成立。  
2) **在 MVP1 稳定后，再分批补齐与 FPMS SPEC 2.0 的差距**：按业务价值与风险分层推进，避免一次性引入大范围数据模型/自动化引擎变更。

### 0.2 MVP1 主线闭环（作为验收主线）
MVP1 的操作主线为：  
**Case → Documents → Deadline Tasks → Fee Draft → Bill → Payment/Offset → Case Receipt**

> 注：该闭环中的“文档→时限联动（自动创建任务）”是目前 MVP1 成功标准里唯一缺口；计划将它作为 **MVP1 GAP 补齐的 P0** 来做（先实现最小可用版本，再演进为 SPEC 的可配置引擎）。

### 0.3 明确暂缓（不在本计划前半段做）
按 `mvp1_gap.md` 的「P2 — Future」清单：PCT、年费批处理、无效/诉讼、催款/坏账、提成、咨询/检索项目、全文检索 ES、多币种汇率表、复杂报表等——均属于 **Spec 2.0 的后续阶段**，不作为 MVP1 GAP 补齐的阻塞项。

### 0.4 文档生成（模板缺失的处理策略）
由于缺少具体模板文件，本计划对“文档生成/模板输出”采取：
- **先做接口与错误契约**（可下载则下载，缺模板则返回明确错误码/信息，并在前端友好提示）；
- **模板管理保持文件型上传/选择**（不做在线模板编辑器 UI）；
- 对新增的输出类型（如任务清单/交接单/信封等）先留出 `template_code`/`template_type` 的挂载点。

---

## 1. 执行原则（安全与稳妥）

### 1.1 变更策略
- **优先“增量兼容”**：先新增表/字段/接口，不破坏现有 API shape；必要的破坏性变更放在单独迁移阶段并提供双写/兼容期。
- **先补“数据结构缺口”再补“自动化引擎”**：数据模型不到位时，自动化只能堆特殊逻辑，维护成本高。
- **每一步都是可回滚的 PR 级别变更**：严格切分任务，避免跨越式“全做完再测”。

### 1.2 Gate（每个原子任务的硬门槛）
每个任务必须包含：
- DB 迁移（如涉及模型）可重复执行、可回滚（至少在 dev 环境）
- 单元/集成测试或最小 smoke 流程（至少 curl/Playwright 之一）
- 前后端合同校验（接口返回 shape、错误 envelope、分页 shape）
- 证据日志（命令 + 关键输出）

---

## 2. 阶段 A：先补齐 MVP1 Scope GAP（推荐 6–10 个原子里程碑）

> 本阶段目标：让 MVP1 在“真实业务可跑 + 客户演示可信”层面闭环；并确保后续对齐 SPEC 2.0 时不会推倒重来。

### A0 — 基线与回归护栏（强烈建议先做）
**目的**：防止后续增量改动破坏既有可用功能。

- A0-01：整理一份 *E2E Smoke 主线脚本*（curl + UI 手工步骤）
  - 覆盖：登录 → 客户 → 案件 → 文档（含附件）→ 任务 → 草单 → 账单 → 收款/冲销 → 账单模板导出
- A0-02：最小自动化 smoke（建议 Playwright 2–3 条主线 + API smoke ）
- A0-03：数据库种子与演示数据（保证演示环境“一键可复现”）

**验收**：任意分支拉起后端+前端，30 分钟内可跑通演示脚本并产出证据。

---

### A1 — Client：补齐“地址/联系人”主数据能力（MVP1 P0）
对应 GAP：`mvp1_gap.md` P0-3。

**交付内容**
- 新增 `T_ClientAddress`、`T_ClientContact`（或等价结构），支持 0..N 地址/联系人
- 标记用途：账单地址/邮寄地址/默认联系人（至少能表达 billing vs mailing）
- API：客户详情返回 addresses/contacts；提供增删改接口
- 前端：客户详情页增加「地址/联系人」区块与编辑能力

**验收**
- 一个客户可维护 ≥2 个地址（含用途）与 ≥2 个联系人
- 账单生成时（如需要）可选择 billing address 展示字段（若当前账单模板暂不改，可先保证数据可取）

---

### A2 — Documents：多附件（MVP1 P0）
对应 GAP：`mvp1_gap.md` P0-4；`mvp_story_gap.md` US-WD-05。

**交付内容**
- 新增 `T_DocAttachment`（seq、filename、filepath、size、mime、uploaded_at…）
- 兼容：保留 `T_Document.file_path`（若存在）并作为 attachment[0] 的回填/兼容读取
- API：上传多个附件、列出附件、下载附件
- 前端：文档创建/编辑支持多文件上传；详情页展示附件清单（下载为主）

**验收**
- 同一文档可上传 ≥2 个附件；刷新后仍可下载
- 缺附件时显示空状态，不报错

---

### A3 — Deadline：任务模板（T_TaskTemplate）+ 基础计算（MVP1 P0）
对应 GAP：`mvp1_gap.md` P0-1；`mvp_story_gap.md` US-DL-01。

**交付内容**
- 新增 `T_TaskTemplate`（最小字段集）：
  - template_code/name
  - base_date_source（如：DOC_DATE / DEADLINE_DATE / CASE_FILING_DATE）
  - add_days（或 add_months/add_days）
  - 默认责任人规则（可先为 role-based 或 manual）
- API：模板 CRUD；创建任务时可选 template_code 自动计算 due_date
- 前端：设置页增加「任务模板」管理（管理员）；任务创建页支持选择模板

**验收**
- 管理员可新增/编辑模板
- 选择模板创建任务时 due_date 能按规则计算并保存

---

### A4 — Deadline：任务操作日志（T_TaskLog）（MVP1 P0）
对应 GAP：`mvp1_gap.md` P0-2；`mvp_story_gap.md` US-DL-05（log maintained）。

**交付内容**
- 新增 `T_TaskLog`：记录 create/update/status/assign/reopen/cancel 等动作
- API：按 task_id 查询 log
- 前端：任务详情显示日志时间线（最少：动作、操作者、时间、备注）

**验收**
- 任意任务状态变更后，log 可查询且 UI 展示

---

### A5 — MVP1 成功标准 #2：文档→任务自动联动（最小可用）（MVP1 P0）
对应 GAP：`mvp_story_gap.md` US-WD-03 + US-DL-02（目前缺失）。

**关键决策（安全实现路线）**
- **先做“最小自动联动 v0”**：仅覆盖 1–2 个高价值场景（例如 OA 来文登记后自动生成“答复 OA”任务）。
- **先不做完整 SPEC 的 DocTemplate 自动化引擎**（那是后续阶段 B 的工作）；但要在数据结构上预留可演进路径（例如：将规则抽象为 config 表或在 `T_DocTemplate` 的最小子集落地）。

**交付内容**
- 文档创建时（满足条件）自动创建任务：
  - 条件：doc_type=OFFICIAL_IN（或其他定义的触发类型）、NeedReply=true（如当前没有字段，可先以 doc_type 代替）
  - due_date：优先用 document.deadline_date；无则由模板计算
- 关联：任务记录 doc_id（或通过关系表）
- 幂等：同一文档重复保存不会重复创建任务（可用 unique constraint/业务键）
- 前端：文档详情可看到“联动生成的任务”；任务详情可回跳到源文档

**验收**
- 登记一份 OA 来文（含附件）后，系统自动生成一条关联任务，并可在“今日提醒/任务列表”看到

---

### A6 — Settings：系统参数（T_SystemParam）（MVP1 P1/必要）
对应 GAP：`mvp1_gap.md` P1-5；Scope H。

**交付内容**
- 新增 `T_SystemParam`（key/value、scope、updated_at、updated_by）
- API：list/upsert
- 前端：系统参数页（管理员）
- 用例：编号前缀/默认币种/默认期限偏移等（先放最小集合）

**验收**
- 参数可被写入、读取；前端展示与编辑可用

---

### A7 — Case：NORMAL 案件字段扩展（受控增量）（MVP1 P0/P1）
对应 GAP：`mvp1_gap.md` P0-5；`mvp_story_gap.md` US-CM-01 补全。

**交付内容（建议分两小步）**
- A7-1（低风险）：补齐 “日常必用字段”
  - PubDate/PubNo、GrantDate/GrantNo/PatentNo、SpecPages/ClaimCount、HasExamRequest 等
- A7-2（中风险）：控制标记与角色指派字段
  - IsFeeMonitor、FeeReduction、PrimaryAgentID/SecondAgentID/DraftorID、FromCountry/ToCountry 等（仅 NORMAL 必要子集）

**验收**
- 新增字段可在创建/编辑/详情中读写；不破坏已有数据与接口

---

### A8 — Search：MVP1 级别的“可用检索面板”（MVP1 P1）
对应 GAP：`mvp1_gap.md` P1-1。

**交付内容**
- Case 列表过滤：client_id、status、date range（filing/recv）、case_type（仍以 NORMAL 为主）
- Documents 列表过滤：case_id、doc_type、date range
- 前端：高级筛选 UI（可折叠）

**验收**
- 至少 3 个关键筛选条件可用，且分页/排序稳定

---

## 3. 阶段 B：在 MVP1 稳定后，逐步对齐 FPMS SPEC 2.0（分层推进）

> 本阶段目标：把 MVP1 从“可跑闭环”演进到“可配置自动化 + 专业字段完备”的 SPEC 级系统。每一层都应独立可验收。

### B1 — 自动化引擎基础：DocTemplate 配置表（SPEC 核心）
对应 `mvp1_gap.md` Module 2、Cross-cutting “Document event → cascading actions”。

**交付内容（先落最小子集）**
- `T_DocTemplate`：template_code、doc_type、status_effect、deadline_template_code、fee_draft_type、fee_item_list（JSON）、input_fields（JSON）等
- 文档登记改为“选择模板→填字段→保存”
- 先支持 2–3 个模板（OA 来文、OA 答复、授权通知）——模板文件可缺，但配置要跑通

**验收**
- 新建文档可绑定 DocTemplate；保存后可触发后续动作（下一步 B2/B3）

---

### B2 — 文档回复链 + 自动核销任务（SPEC 核心）
对应 `mvp_story_gap.md` US-WD-02/03；`mvp1_gap.md` Documents fields.

**交付内容**
- Document 增加 ReplyToID/NeedReply/ReplyDate；支持 OUT 文档指向 IN 文档
- 当登记 OUT 回复文档时：自动将关联任务置为 DONE（并写入 TaskLog）
- UI：文档详情显示“回复链”（来文 ↔ 去文）

**验收**
- 在 OA 场景中：登记来文→自动任务→登记去文→任务自动核销

---

### B3 — 文档→费用草单联动（增强自动化闭环）
对应 `mvp_story_gap.md` US-WD-04。

**交付内容**
- 在 DocTemplate 中配置 fee_draft_type 与默认 fee items
- 文档保存后可生成 FeeDraft（可提示用户确认/可撤销）
- UI：从文档入口可跳转到生成的草单

**验收**
- 授权通知文档可一键生成授权相关草单（模板缺失不影响草单生成）

---

### B4 — Deadline 引擎升级：内部限/多级提醒/监督视角
对应 `mvp_story_gap.md` US-DL-03/04；`mvp1_gap.md` Task fields.

**交付内容**
- Task 增加 InnerDeadline、Remind1/2/3、Worker/Supervisor 区分
- Today reminders 支持 Worker/Supervisor 两种视角
- 权限控制 + UI 分组呈现

**验收**
- 同一任务可看到官方绝限+内部限；监督人可以查看组内任务并重分配

---

### B5 — 金融增强：账单分项、折扣、反冲销、预收款（按需分批）
对应 `mvp_story_gap.md` US-BL-05/07 等（其中部分在 MVP1 排除，但 Spec 对齐时需要）。

**交付内容（拆分为多个小任务）**
- Bill 增加 TotalGov/TotalService/TotalMisc、DiscountRate、Direction(AR/AP)
- Offset reversal（反冲销）
- PaymentLine（分配行）支持预收款余额

**验收**
- 可回滚冲销并恢复余额；可管理预收款余额

---

### B6 — 主数据规范化：Applicant/Inventor/Priority 拆表（高风险，后置）
**这是典型“大手术”**：当前 JSON 内嵌结构改为规范化表，建议放在较后阶段，并提供迁移脚本与兼容读写期。

---

### B7 — 报表与高级检索（后置）
在数据模型稳定后再做：统计、钻取、导出、审计等。

---

## 4. 推荐的执行顺序（最稳妥的“跑道”）

1) **A0（回归护栏）**  
2) **A1/A2（客户主数据 + 文档多附件）**  
3) **A3/A4（任务模板 + 任务日志）**  
4) **A5（文档→任务最小联动，补齐 MVP1 成功标准 #2）**  
5) **A6/A7/A8（系统参数 + NORMAL 字段扩展 + 搜索面板）**  
6) **B1/B2/B3（DocTemplate + 回复链 + 自动核销 + 费用联动）**  
7) **B4/B5（期限引擎升级 + 金融增强）**  
8) **B6/B7（规范化拆表 + 报表）**

---

## 5. 附录：任务拆分建议（原子任务颗粒度示例）

> 以下仅示例如何切分；实际 allowlist 与命令以 repo 当前结构为准。

- 原子任务示例：`A2-Documents-MultiAttachment`
  - 允许改动：document 模型 + migration + storage + document API + document 前端表单/详情
  - Gate：迁移可回滚；上传 2 个附件；下载成功；接口 envelope 兼容；FE build 通过
  - Evidence：迁移日志、curl 上传/下载、UI 截图或 Playwright log

---

