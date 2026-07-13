# FPMS 实现与文档差距分析报告（Gap Analysis Report）

日期：2026-07-08
任务：分析当前代码实现与 `docs/` 下设计文档、用户手册、用户反馈的差距，输出差距清单并修复可闭环项。

## 1. 分析范围与方法

对照来源：

- 设计文档：`docs/postdemo/postdemo_p1_functional_spec_20260531.md`（P1 FS + 验收标准 AC-01..AC-18）、`docs/postdemo/postdemo_fee_scenario_integration_design_20260704.md`、`docs/postdemo/postdemo_fee_followup_trigger_design_20260705.md`
- 审计与用户反馈：`docs/reviews/fpms_functional_correctness_audit_20260705.md`（FG-01..FG-12、IC-01..IC-10）、`docs/reviews/fpms_audit_remediation_design_20260705.md`、`docs/postdemo/postdemo_fee_scenario_gap_review_20260705.md`（GAP-FEE/CALC/UI/TEST 系列）
- 演示运行记录（用户实际操作反馈）：`docs/postdemo/postdemo_p1_v4/v5/v6_ui_e2e_success_runbook_20260705.md` 的 Residual Risks 段
- 当前实现：`backend/app/modules/*`、`frontend/src/*`（HEAD `ff3d58b`），后端全量 pytest、前端 lint/typecheck 基线

## 2. 结论总览

| 类别 | 数量 | 处理 |
|---|---:|---|
| A. 回归测试与实现漂移（测试断言未跟上已定稿的新行为） | 17 个失败测试（3 组） | 本轮修复 |
| B. 前后端不一致 / 文档承诺未落地的可闭环差距 | 5 项 | 本轮修复 |
| C. 已在文档中明确"待客户确认/后续阶段"的差距 | 若干 | 保持 open，见 §6 |

后端基线：`pytest` 612 passed / **17 failed**；前端基线：`lint`、`typecheck` 通过。

## 3. A 类：测试与实现漂移（本轮修复）

### A-1. 年费草单金额语义变更后旧 E2E 测试未更新（6 个失败）

- 失败：`tests/test_annuity_e2e.py` 中 6 个用例（generate-drafts、pay-list from-fee-items、query、detail、export、currency normalize）。
- 根因：提交 `6df9060` 按《收费后续触发规则设计》§6.6/§6.7（"年费金额由 `AnnuityTask` 承载，不重算"）将 `generate_fee_drafts_from_annuity_tasks` 从 `_rate_amount(db, ...)` 全局费率取数改为 `task.gov_fee_amt`（`backend/app/modules/annuity/service.py:1035`），且服务费不再并入草单。新测试 `tests/test_annuity_generate.py:279` 已断言 `service_fee_amt == 0.00`，但旧 E2E 测试仍直插 `AnnuityTask` 时不设 `gov_fee_amt`，并期望 `100+20=120`。
- 判定：实现行为正确（有设计依据 + 新测试），旧测试期望过期。
- 修复：旧测试直插任务时补 `gov_fee_amt`，金额期望改为任务承载金额（仅官费）。

### A-2. 授权费任务响应新增 deadline-preview 字段后冻结断言未更新（6 个失败）

- 失败：`tests/test_grant_fee_state_machine_api.py`（3 个）、`tests/test_grant_fee_worklist_api.py`（3 个）。
- 根因：按《收费后续触发规则设计》§6.8（授权/年费 deadline preview 输出 trigger/deadline/fee_basis/节点解释），提交 `6df9060` 给授权费任务响应新增 `trigger_rule / deadline_rule / fee_basis / fee_node_explanation`（`backend/app/modules/grant_fees/service.py:65`）。旧测试用"字段集合全等"断言，未包含新字段。
- 判定：实现正确，测试过期。修复：把 4 个新字段并入期望集合。

### A-3. 申请人主数据新增总委托书备案编号后冻结 schema 断言未更新（5 个失败）

- 失败：`tests/test_applicant_data_model.py`（2 个）、`tests/test_masterdata_prereq_schema.py`（2 个）、`tests/test_masterdata_prereq_contract.py`（1 个）。
- 根因：按 P1 FS AC-17（总委托书备案编号按申请人级维护），`total_power_of_attorney_no` 已加入 `Applicant` 模型/API（`backend/app/modules/masterdata/applicants/models.py:16`），审计报告也确认其为已实现项。旧"冻结最小列集"测试未包含该列。
- 判定：实现正确，测试过期。修复：期望列集/字段集加入 `total_power_of_attorney_no`。

## 4. B 类：可闭环实现差距（本轮修复）

### B-1. 前端来源状态不识别 `PENDING_CONFIRMATION`（GAP-UI-003）

- 现状：`frontend/src/modules/cases/components/CaseFeesTab.vue:233` 的 `formatSourceStatus` 只识别 `CONFIRMED/PENDING/DISABLED`；seed 实际写入 `PENDING_CONFIRMATION`（`backend/scripts/seed_dev.py:47`），UI 显示"来源状态：未标记"。
- 修复：识别 `PENDING_CONFIRMATION` 显示"待确认"。

### B-2. 前端 `FeeRate` 类型与费率参数页缺来源审计字段（GAP-FEE-007 / GAP-UI-004）

- 现状：后端 `FeeRateOut` 已输出 `source_doc/source_url/source_policy/source_version/source_status`（`backend/app/modules/fees/schemas.py:290`），前端 `frontend/src/api/fees.types.ts:8` 的 `FeeRate` 接口全部缺失，`FeeRates.vue` 不展示，用户无法审计费率来源。
- 修复：补类型字段；费率参数页增加来源状态/来源版本展示。

### B-3. 待确认费率缺硬性启用门禁（GAP-AUDIT-006 / 差距评审 P0-3）

- 现状：`PENDING_CONFIRMATION` 条目仅靠 seed 里 `enabled=False` 的约定被排除；若被误启用，`_enabled_fee_rates_by_code`（`backend/app/modules/fees/service.py:647`）仍会选中并自动生成草单。差距评审 P0 结论要求"待确认条目不得自动生成草单"。
- 修复：官费费率选择器排除 `source_status ∈ {PENDING_CONFIRMATION, DISABLED}` 的条目（`NULL`/`CONFIRMED` 不受影响），并补回归测试。

### B-4. 官费清单明细不展示案号（V6 runbook Residual Risk 1）

- 现状：pay-list 详情 API 的 `gov_payments` 载荷只有 `case_id`（`backend/app/modules/annuity/service.py:1614`），前端 `PayListDetail.vue:445` 只能显示"已关联案件"。V6 演示明确记录该增强诉求。
- 修复：详情载荷补 `case_no`（join `T_Case`），前端明细列直接显示案号。

### B-5. 费用草单明细缺"费用项目"名称列（V5 runbook Residual Risk 1）

- 现状：`FeeDraftItemsTable.vue` 只有 类型/描述/数量/单价/金额 列；`FeeItemOut.fee_name` 已存在（`backend/app/modules/fees/schemas.py:168`）但未展示，用户只能靠备注辨认"申请费/公布印刷费/实审费"。
- 修复：前端明细表增加"费用项目"列（`fee_name`，空值回退描述）。

### B-6. UM/DES 申请费草单无测试覆盖（GAP-TEST-001，部分）

- 现状：`CN_UM_APPLICATION_FEE / CN_DES_APPLICATION_FEE` 服务代码已支持（`backend/app/modules/fees/service.py:42`），但 `tests/test_apply_fee_draft_rule.py` 只测 INV。
- 修复：补 UM/DES 申请费草单生成测试。

## 5. 与文档核对后确认"已实现、无差距"的项

- 费减语义 `0.85 → 应缴 15%`：`_official_payable_ratio_from_customer_reduction`（`fees/service.py:631`）+ 参数化测试（`test_pd_p1_fee_reduction_conversion.py`）。AC-18 满足。
- Live demo seed 发明申请费已为 900（`pdP1LiveSeed.py:116`），与官方/客户口径一致（GAP-FEE-002/GAP-CALC-002 已闭环）。
- 费率生效期选择（IC-05）：`fee_rate_effective_on_conditions` 已被 fees/annuity/grant_fees 三处选择器使用，含测试。
- GRANTED 就绪门禁统一（IC-01）：三模块共用 `has_required_granted_status_fields`（`cases/service.py:684`），含 `pub_no/pub_date`。
- 附件角色级扩展名/MIME 校验（IC-09/FG-03）：10 个官方文件角色已校验（`documents/service.py:184`）。
- 官方清单多文件角色（IC-04）：`OA_OTHER_PROOF / OA_ADDITIONAL_FILE` 支持多行（`official_workflows/service.py:72`）。
- 复审触发预览（P1.5 任务 1）：`REEXAM_REQUESTED` 已支持并返回期限/费减字段（`fees/service.py:917`），含测试。
- 授权/年费 deadline preview（P1.5 任务 2）：字段已输出（见 A-2）。

## 6. C 类：保持 open 的差距（文档已明确依赖客户决策或后续阶段）

| 差距 | 来源 | 保持 open 的依据 |
|---|---|---|
| IC-02 回执元数据完整性硬门禁 | 审计 | 修复设计明确 skip："回执清单人工录入还是系统解析未决"（`fpms_audit_remediation_design_20260705.md`） |
| IC-03 归档 override 独立权限 | 审计 | 依赖客户角色/审批策略确认 |
| IC-06 pay-list 导出状态拆分（EXPORTED≠官方接受） | 审计 | P1 手动流程边界；官方模板未验证（FG-05 同源） |
| IC-07 全量法律状态迁移矩阵 | 审计 | 修复设计列为 Deferred，需更大状态机设计 |
| IC-08 授权费任务显式状态机 | 审计 | Deferred，同上 |
| IC-10/FG-09 最新官文 resolver | 审计/FS §11.1-5 | tie-break 规则待客户确认 |
| FG-01 代理人资格证号档案 | 审计/FS §11.2-2 | 维护对象归属待客户确认 |
| FG-02 文书版本沿革（version/supersedes） | 审计 | 建议独立任务 `FPMS-DOCUMENT-VERSION-LINEAGE`，涉及迁移 |
| FG-05 官方缴费 Excel 模板兼容 | 审计/FS AC-08 | 需官方空表+成功样例；当前 UI 已按 AC-08 显示"待确认"边界 |
| FG-07 产品级审计导出 | 审计 | P1/P2 候选任务 |
| FG-11 持久化费用触发规则表 | 审计/触发设计 §3 | 设计推荐先服务层注册表，字段稳定后再落表 |
| FG-12 / GAP-TRIGGER-011..015 PCT/海牙/IC 自动触发 | 审计/触发设计 §7-9 | 设计明确冻结至 P2/P3，需客户样例 |
| GAP-CALC-003/004 说明书附加费、优先权费计费 | 差距评审 | 页数口径、优先权计项待客户确认（评审 §15-3/4） |
| GAP-DEADLINE-008 年费滞纳金区间计算 | 差距评审 | 是否系统自动判定待确认（评审 §15-6） |
| 前端 REEXAM 触发入口（UI 仍只调 FILING_ACCEPTED） | 触发设计 §5 | 复审预览需先有"客户决定复审"动作对象（§5.8 待确认 2/3）；后端 API 已就绪 |
| review_mode 字段未输出 | 触发设计 §6.8 | 规则层落表时一并冻结 |

## 7. 本轮修复清单（执行顺序）

1. A-1/A-2/A-3：更新 17 个过期测试断言（不改产品行为）。
2. B-3：官费费率选择器增加 `source_status` 启用门禁 + 回归测试。
3. B-4：pay-list 详情载荷补 `case_no` + 前端案号列。
4. B-1/B-2/B-5：前端来源状态映射、FeeRate 来源字段与展示、草单"费用项目"列。
5. B-6：补 UM/DES 申请费测试。
6. 验证：后端全量 `pytest`、`ruff check`；前端 `lint + typecheck + build`。

## 8. 验证结果

### 8.1 静态基线

- 后端：`pytest` 全量 **632 passed / 0 failed**（修复前 612 passed / 17 failed）。
- 后端：`ruff check` 变更文件全部通过。
- 前端：`npm run typecheck`、`npm run lint`（--max-warnings 0）、`npm run build` 全部通过。
- 全新数据库：`alembic upgrade head` + `python scripts/seed_dev.py` 在空库上成功（53 条官费费率入库）。

### 8.2 端到端实测（uvicorn 实例 + 全新 SQLite）

| 步骤 | 结果 |
|---|---|
| 登录 admin，创建客户/申请人（含总委托书备案编号）/案件（费减 0.85、12 项权利要求、请求实审） | 通过 |
| `官费预览 FILING_ACCEPTED`：申请费 900→135、附加费 300（不可减）、印刷费 50、实审费 2500→375，合计 860，含期限规则 | 通过（AC-18 语义正确） |
| `官费预览 REEXAM_REQUESTED`：seed 中复审费待确认未启用 → 正确返回 `OFFICIAL_FEE_PREVIEW_RATE_MISSING`，不产生金额 | 通过 |
| 启用门禁：新建 `enabled=true` 但 `source_status=PENDING_CONFIRMATION` 的 9999 元发明申请费，预览仍选 900 元 CONFIRMED 费率 | 通过（B-3 新门禁生效） |
| 申请费草单生成 → 官费清单（备注保留）→ 清单详情 `gov_payments` 直接返回 `case_no=E2E-GAP-CASE-01` | 通过（B-4/V5 备注问题实测未复现，后端已持久化） |
| GRANTED 门禁：缺 `pub_no/pub_date` 保存 `GRANTED` → `CASE_GRANTED_FIELDS_REQUIRED`；补齐后成功 | 通过（IC-01 修复保持） |
| 年费任务生成（20 条，第 2/3 年 900、第 4 年 1200 按阶梯费率）+ deadline preview 字段（触发/期限/依据） | 通过 |
| 年费草单（金额取任务承载值 900）→ 官费清单 → xlsx 导出（有效 OOXML）→ 缴费登记（gov payment PAID） | 通过 |
| 费率参数 API 返回 `source_doc/source_status` 等来源审计字段 | 通过（B-2 前端类型/展示同步补齐） |

## 9. 修复文件清单

后端：

- `backend/app/modules/fees/service.py` — 新增 `fee_rate_source_enabled_condition` 启用门禁并接入 `_enabled_fee_rates_by_code`
- `backend/app/modules/annuity/service.py` — 年费/授权费费率选择接入启用门禁；pay-list 详情 `gov_payments` 增加 `case_no`
- `backend/app/modules/grant_fees/service.py` — 费率选择接入启用门禁
- `backend/tests/test_annuity_e2e.py` — 对齐年费草单"任务承载金额"语义（含 `gov_fee_amt`、SERVICE 项手工插入、`case_no` 字段断言）
- `backend/tests/test_grant_fee_state_machine_api.py` / `test_grant_fee_worklist_api.py` — 字段集合加入 deadline preview 4 字段
- `backend/tests/test_applicant_data_model.py` / `test_masterdata_prereq_schema.py` / `test_masterdata_prereq_contract.py` — 冻结列集加入 `total_power_of_attorney_no`
- `backend/tests/test_official_fee_preview_api.py` — 新增 PENDING_CONFIRMATION 启用门禁回归测试
- `backend/tests/test_apply_fee_draft_rule.py` — 新增 UM/DES 申请费草单测试

前端：

- `frontend/src/api/fees.types.ts` / `fees.ts` — `FeeRate` 增加 `source_doc/source_url/source_policy/source_version/source_status`
- `frontend/src/api/govPayments.types.ts` / `govPayments.ts` — `GovPaymentInfo` 增加 `case_no`
- `frontend/src/modules/fees/pages/FeeRates.vue` — 费率参数表增加"来源状态/来源"列
- `frontend/src/modules/fees/components/FeeDraftItemsTable.vue` — 草单明细增加"费用项目"列
- `frontend/src/modules/cases/components/CaseFeesTab.vue` — `formatSourceStatus` 识别 `PENDING_CONFIRMATION`
- `frontend/src/modules/annuity/pages/PayListDetail.vue` — 清单明细直接展示案号
