# GPT53 Enhance 执行计划（先 MVP Gap，后 SPEC 2.0 Gap）

更新时间：2026-02-23  
适用仓库：`/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic`

## 1. 目标与边界

### 1.1 总目标（严格顺序）
1. 先弥补当前实现与 `docs/00_mvp1_scope.md` 的 GAP。  
2. 再弥补与 `docs/FPMS SPEC 2.0.md` 的 GAP。  
3. 文档生成功能因模板未齐全，先保留接口与错误语义（409），模板后补。

### 1.2 依据文档
- `docs/00_mvp1_scope.md`
- `docs/FPMS SPEC 2.0.md`
- `docs/mvp_story_gap.md`
- `docs/mvp1_gap.md`

### 1.3 执行纪律（强制）
- 每次只执行一个 task 文件（Atomic）。
- 先证据后结论：每个 task 都产出 `artifacts/<TASK-ID>/` 证据。
- 任何不在 MVP1 范围内的能力不提前实现（PCT、年费批量、提成、坏账、催款等）。

---

## 2. 总体策略（安全稳妥）

### 2.1 先“真值复核”再开发
先确认哪些 GAP 已被后续提交补齐，避免重复开发。  
复核维度：接口可调用、状态码正确、权限正确、链路可跑通。

### 2.2 风险优先级
- **P0（先做）**：影响 MVP 成功标准和主链路的缺口。
- **P1（后做）**：增强可用性，不阻断主链路。
- **P2（冻结）**：MVP1 明确排除项，仅登记不实施。

### 2.3 统一门禁
每个 task 完成后必须执行：
1. `ruff check --fix .`
2. `ruff format .`
3. `ruff check .`
4. `./scripts/task_validate.sh <TASK-ID>`
5. 关键波次结束执行 `./scripts/release_gate.sh`

---

## 3. 阶段 A：先补 MVP Scope GAP

## A0. 基线复核波（不改代码或只做最小修正）
目标：确认 MVP 成功标准 1/2/3/4 当前真实状态。  
输出：`artifacts/GPT53-A0-baseline/summary.md`（建议）记录每条标准是否通过与证据链接。

建议复核主链路：
1. 案件创建/检索/详情（成功标准 1）
2. OA 来文登记 + 附件 + 自动建任务（成功标准 2）
3. 费用草单 → 账单 → 收款/冲销（成功标准 3）
4. Word 账单输出（成功标准 4）

---

## A1. P0 主链路补齐（按 task 单文件顺序执行）

### A1-1 文档到时限任务自动联动（MVP 成功标准 2 核心）
1. `tasks/backend/business_logic/task_generation/BL-TASK-01_task_generation_service_from_document.md`
2. `tasks/backend/business_logic/task_generation/BL-TASK-02_wire_document_create_to_task_generation.md`

验收：
- 创建符合条件的来文后，任务自动生成；
- 失败时返回业务语义（如 409 配置缺失），不出现静默失败。

### A1-2 时限动作日志 + 今日提醒（worker/supervisor）
1. `tasks/backend/mvp1enhance/ENH-05-04.md`
2. `tasks/backend/mvp1enhance/ENH-05-13.md`

验收：
- close/reopen/cancel/assign 写入 TaskLog；
- `/tasks/today?as=worker|supervisor` 可用，权限与状态码正确。

### A1-3 文档多附件闭环（0..N）
1. `tasks/backend/mvp1enhance/ENH-04-07.md`
2. `tasks/backend/mvp1enhance/ENH-04-12.md`
3. `tasks/backend/mvp1enhance/ENH-04-13.md`

验收：
- 文档附件可上传/下载；
- 文件类型与路径安全校验生效；
- 权限 `Doc.Attach` 生效。

### A1-4 主数据与系统参数最小闭环
1. `tasks/backend/mvp1enhance/ENH-07-02.md`（客户地址/联系人 typed schema）
2. `tasks/backend/mvp1enhance/ENH-08-02.md`
3. `tasks/backend/mvp1enhance/ENH-08-05.md`
4. `tasks/backend/mvp1enhance/ENH-08-13.md`
5. `tasks/backend/mvp1enhance/ENH-08-14.md`

验收：
- `GET/PUT /system/params` 可用；
- secret 参数值对外掩码；
- 客户地址/联系人结构可在接口中正确表现。

---

## A2. P1 可用性增强（在 A1 全绿后）
1. 案件高级检索（按现有 task 拆分逐个执行）
2. 文档检索条件增强（模板/日期范围/方向/案件）
3. CaseReceipt 字段增强（在不破坏现有计费链路前提下）

说明：A2 仍需遵守“一个 task 一个文件”执行，不做跨模块大改。

---

## 4. 阶段 B：再补 FPMS SPEC 2.0 GAP（MVP 外扩）

前置条件：阶段 A 全部通过，且 `release_gate.sh` 通过。

## B1. Case 扩展（只做 NORMAL 相关必需字段）
目标：补齐 SPEC 第 2 章中 NORMAL 案型的关键字段与校验。  
不做：PCT/无效/诉讼完整流程（仍属后续）。

## B2. Documents 模板化联动引擎（先接口）
目标：建立 DocTemplate 驱动的状态/时限/费用联动骨架。  
策略：模板缺失时返回 `409`（`template_not_configured`），不做 UI 假成功。

## B3. Deadline 规则增强
目标：从最小模板提升到 BaseDate/InternalDeadline/Remind* 规则化计算。

## B4. 费用联动（非年费批量）
目标：支持文档事件触发 FeeDraft（最小可用），年费批量和宽限规则继续冻结。

## B5. 检索与报表增强
目标：先做操作性检索，后做统计性报表；财务复杂报表继续后置。

---

## 5. 文档生成能力（模板缺失场景）执行准则
1. 先实现渲染接口、context builder、权限与状态码。  
2. 模板存在：返回文件流；模板缺失：返回 `409`（可定位的 detail）。  
3. 不因模板未准备阻塞主业务链路（登记、任务、计费）。

---

## 6. 每次执行模板（Runbook）

1. 选定唯一 task 文件路径。  
2. 按 task allowlist 改动代码。  
3. 运行证据脚本：
   - `./scripts/evidence_run.sh <TASK-ID> lint ...`
   - `./scripts/evidence_run.sh <TASK-ID> fmt ...`
   - `./scripts/evidence_run.sh <TASK-ID> test ...`
   - `./scripts/evidence_finalize.sh <TASK-ID>`
   - `./scripts/task_validate.sh <TASK-ID>`
4. 输出三项结论（强制）：
   - 执行了哪个 task/runbook
   - 修改了哪些文件
   - 验证命令与预期状态码

---

## 7. 冻结清单（MVP1 不实施）
- PCT 国际/国家阶段自动化
- 年费批量/宽限/复杂通知
- 无效/诉讼完整工作流
- 催款/坏账/复杂财务报表
- 提成计算与结算
- 全文检索（ES）

以上仅登记在 backlog，不进入当前执行波次。
