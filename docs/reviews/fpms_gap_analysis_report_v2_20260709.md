# FPMS 实现与文档差距分析报告 V2（Gap Analysis Report v2）

日期：2026-07-09
范围：按 `AGENTS.md §0.3 Source Document Index for Reviews and Audits` 全量文档索引，对照当前实现（HEAD `ff3d58b` + 第一轮修复工作区）进行第二轮差距分析。
前序报告：`docs/reviews/fpms_gap_analysis_report_20260708.md`（第一轮，17 个漂移测试 + 6 项可闭环差距已修复，后端 632 passed）。

## 1. 分析范围与方法

按索引分四组核对，全部结论都以当前代码 file:line 证据为准（多数文档写于 2026 Q1-Q2，代码在 2026-05..07 已大幅推进，逐条验证后再定 verdict）：

1. **SPEC 2.0 基线与审计族**：`FPMS_SPEC2_Final_Audit_Excluding_Document_Generation_20260406.md`、`FPMS_SPEC2_2nd_Review_REFRESH.md`、`FRMS_SPEC2_2nd_POST.md`、`spec20_tech_mitigate.md`、`2026-04-09-spec20-process-follow-test-cases.md`
2. **历史差距文档**：`gap.md`、`mvp1_gap.md`、`mvp_story_gap.md` + `MVP2_GAP_Decision_Matrix_and_Phased_Recommendation_20260315.md`（判定 DEFERRED）
3. **Post-demo 客户源文档与台账**：`postdemo_enhancement_analysis_20260530.md`、answer_ledger、full-scope delta/close ledgers、`相关流程操作-20260526.txt`、`OA答复流程.txt`、`信函生成操作.txt` 提取件、P1 FS §5.2/§6
4. **第一轮已核对文档**（fee scenario、audit remediation、V4-V6 runbooks）不重复展开，仅引用其残留项。

## 2. 结论总览

- SPEC 2.0 核心（案件/文书/时限/账单/提成/顾问/坏账/预收/冲销反转）已实质闭环；两份审计台账声称"无残留"，但 `FRMS_SPEC2_2nd_POST.md` 登记的 **5 项 FR-FE-04 blocked follow-up 至今全部未落地**，这是本轮最大的结构性差距。
- 历史 gap 文档中约 30 个 ❌/🟡/🚫 项，**22 项已闭环**；仍开放的为少量 UX/导出类差距。
- 客户源文档中，**信函生成的 8 行"官文→格式函"映射表和 22 行"致函官方"清单从未 seed 入库**，导致格式函自动匹配在生产上永远不命中——这是客户明确给出、可直接转写的数据。
- 60 行官方通知目录与客户表逐行一致（第一轮агент所称"66 行"经复核为误报，实际 60=60）。

## 3. 差距清单

### 3.1 A 类：本轮修复（可执行、无需客户决策）

| ID | 差距 | 来源 | 证据 |
|---|---|---|---|
| **V2-01** | `T_PayList` 缺 `list_type / flow_dir / invoice_no_from / invoice_no_to`（FRFE04-BLOCK-01） | `FRMS_SPEC2_2nd_POST.md` 已批准 follow-up | `annuity/models.py:12` PayList 无这些列 |
| **V2-02** | `T_GovPayment` 缺 `fee_code / year_no / planned_amt / planned_currency / paid_currency / voucher_no / invoice_no`（FRFE04-BLOCK-02） | 同上 | `annuity/models.py:42` 仅 currency/paid_date/paid_amount/official_receipt_no |
| **V2-03** | 依赖上述字段的增强查询（FRFE04-BLOCK-03） | 同上 | `annuity/api.py` 列表无对应过滤 |
| **V2-04** | 格式函映射表 0 行 seed；客户 8 行"官文→格式函"表（信函生成 TABLE 001）未装载，自动匹配永不命中 | `信函生成操作.docx` P0007 | `grep FormatLetterMapping scripts/seed_dev.py` = 0；匹配引擎在 `official_workflows/service.py:1476` |
| **V2-05** | 信函默认文件名规则不符客户口径：客户为 `{案号}-给{申请人}的邮件.docx`，实现默认 `{case_no}-格式函.docx` 且占位符不含申请人 | `信函生成操作.docx` P0004 | `official_workflows/service.py:1589-1607` 仅 case_no/app_no/document_title |
| **V2-06** | 22 行"致函官方"文件清单（相关流程操作 TABLE 002）未作为 OUT 方向目录 seed | `相关流程操作-20260526.docx` P0102 | `grep 补正答复\|费用减缓请求书` 非测试代码 = 0 |
| **V2-07** | V4 demo cleanup 删除 `FormatLetterMapping` 前未清理动态创建的、引用该映射的 `LetterHandoff` 行 → 外键失败（V6 runbook Residual 4 实测记录） | `postdemo_p1_v6_ui_e2e_success_runbook_20260705.md` §5 | `pdP1LiveSeed.py:496` 直接删映射；`clear_fixture` 仅按 V4 文档 ID 删 handoff，漏掉 V5/V6 动态 handoff 的 `format_letter_mapping_id` 引用 |
| **V2-08** | `calculate_fee_amount` 只支持 FIXED/PER_CLAIM；`calc_mode=PER_PAGE` 已在模型/seed 中存在但不能算（US-FE-02 残留、GAP-CALC-003 前置） | `mvp_story_gap.md` US-FE-02；fee gap review | `fees/service.py:1670-1676`；`case.spec_pages` 已存在 |
| **V2-09** | 今日提醒清单无打印（US-DL-07，🟡 唯一残留的时限故事项） | `mvp_story_gap.md` | `TodayReminders.vue` 无 print/export |
| **V2-10** | 文书列表有完整高级筛选但无导出清单（US-WD-06 残留半项） | `mvp_story_gap.md` | `DocumentList.vue` 无导出按钮/后端无对应 endpoint |

### 3.2 B 类：保持 open（需客户决策/样例，或已批准延期）

| 差距 | 来源 | Open 依据 |
|---|---|---|
| FRFE04-BLOCK-04 XML/文本多格式官方导出 | POST ledger | 官方导出格式需官方样例；本轮仅 Excel |
| FRFE04-BLOCK-05 已缴记录高权限修改+审计 | POST ledger | "需要独立权限/审计设计"，与 IC-03 同类客户策略项 |
| 客户≠官方申请人时总委号映射位置 | P1 FS §18.3 | 客户明确待答 |
| 官方缴费 Excel 模板兼容（FG-05） | P1 FS AC-08 | 需官方空表+成功样例 |
| 官费标准费率表（P0103，EMF 图片） | close_ledger AC-14 | 源不可机读，待客户提供可读版 |
| IC-02/03/06/07/08/10、FG-01/02/07/11 | 第一轮报告 §6 | 依据不变 |
| PCT 国家阶段、无效/诉讼、全文检索、统一工作台、模板中心、词库 | MVP2 决策矩阵 20260315 | DEFERRED-MVP2 |
| 附件在线预览（US-WD-05 残留半项） | mvp_story_gap | 预览交互形态未定（浏览器内嵌 vs 新窗口），且涉及文件安全头配置；建议独立任务 |
| 案件费用页 REEXAM 触发入口 | 第一轮报告 | 需"客户决定复审"动作对象（触发设计 §5.8） |

### 3.3 已核实"文档过期、实际已闭环"的代表项（不修复，仅记录）

- 时限模板/自动生成/监督人/TaskLog/专项检索（US-DL-01..06）→ `tasks/` 模块全量落地
- 发文自动核销、期限联动、费用联动、邮寄交接（US-WD-02/03/04/07）→ `documents/` + `LetterHandoff/DocDispatch`
- 年费/授权费/官费清单/支出/提成/顾问/预收/冲销反转/坏账 → 对应模块全部存在
- 60 行官方通知目录与客户 TABLE 001 逐行一致（60=60）
- 费减 0/0.7/0.85 转换 + 前端展示（FeeLinkagePanel 已接 `fee_reduction_conversion_status`）
- 发明人中国籍必填身份证号校验已在 readiness 中（`official_workflows/service.py:359-363`）
- 费用综合查询"双表对照"已有 `FeeUnifiedQuery.vue`（上半官费/下半个案收款）
- 重复案号硬阻断、受限编辑白名单（TC-CM-001/002）

## 4. 修复执行顺序

1. V2-01/02/03：PayList + GovPayment 结构列（一个迁移）→ schemas → service 写入/读出 → 列表过滤 → 测试
2. V2-04/05：格式函映射 seed（8 行）+ `{applicant_name}` 占位符 + 客户命名规则
3. V2-06：致函官方 22 行 OUT 目录 seed
4. V2-07：demo cleanup 外键修复
5. V2-08：PER_PAGE 计算模式
6. V2-09/10：今日提醒打印 + 文书列表导出
7. 全量验证：后端 pytest、ruff、前端 lint/typecheck/build、fresh-DB 迁移+seed、live API E2E

## 5. 验证结果

### 5.1 静态基线

- 后端：`pytest` 全量 **638 passed / 0 failed**（第一轮修复后为 632；本轮新增 6 个测试）。
- 后端：`ruff check` 全部变更文件通过。
- 前端：`npm run typecheck`、`npm run lint`（--max-warnings 0）、`npm run build` 全部通过。
- 全新数据库：`alembic upgrade head`（含新迁移 `frfe04_block_struct_cols_01`）+ `python scripts/seed_dev.py` 成功；seed 幂等（重跑无重复）。

### 5.2 修复实测（uvicorn 实例 + 全新 SQLite）

| 差距 | 实测 | 结果 |
|---|---|---|
| V2-01/02 结构列 | 创建清单带 `list_type=ANNUITY / flow_dir / invoice_no_from/to`；手工明细带 `fee_code / year_no / paid_currency / voucher_no / invoice_no`，全部写入并在响应/详情中回读 | 通过 |
| V2-03 增强查询 | `GET /pay-lists?list_type=ANNUITY&voucher_no=VCH-V2-01` 精确命中 1 条；无匹配时 0 条 | 通过 |
| V2-04 映射 seed | 8 行映射 + 8 个 FORMAT_LETTER 模板文件落库/落盘；上传"第一次审查意见通知书"官文后 preview 自动命中 `FORMAT_LETTER_007`，`template_status=READY` | 通过 |
| V2-05 命名规则 | 生成路径为 `V2-E2E-CASE-01-给V2差距验证申请人的邮件.docx`，符合客户 P0004 口径 | 通过 |
| V2-06 致函官方目录 | 22 行 OUT 目录 seed，`/doc-templates` API 可查（total=22） | 通过 |
| V2-07 cleanup FK | 构造"非 demo 文书的动态 handoff 引用 demo 映射"场景后重跑 V4 seed（含 clear_fixture 删映射）——不再外键失败 | 通过 |
| V2-08 PER_PAGE | 单元测试覆盖 31-300/301+ 双档、跨档、不足 31 页三种情形（40 页=500 元；320 页=13500+2000 元；25 页=0 元） | 通过 |
| V2-09 今日提醒打印 | 前端"打印清单"按钮接 `/tasks/print?as=&due_from=&due_to=`（当天），后端返回可打印 HTML（实测 200 + 标题"我的时限任务清单"） | 通过 |
| V2-10 文书清单导出 | `GET /documents/export?case_id=...` 返回有效 xlsx（标题/文书名/案号在 sheet 中）；带方向过滤只导出 IN；前端"导出清单"按钮沿用当前筛选条件 | 通过 |
| 回归 | 第一轮修复（费减 0.85→135、pay-list 备注/case_no、启用门禁）全部保持 | 通过 |

## 6. 修复文件清单

后端：

- `backend/alembic/versions/frfe04_paylist_govpayment_struct.py` — 新迁移（幂等、batch_alter_table、SQLite 兼容）
- `backend/app/modules/annuity/models.py` — PayList +4 列、GovPayment +7 列
- `backend/app/modules/annuity/api.py` — 输入 schema、endpoint 透传、列表查询参数与序列化
- `backend/app/modules/annuity/service.py` — 创建/登记/手工补录写入新字段、列表过滤、详情输出
- `backend/app/modules/official_workflows/service.py` — 信函文件名规则（`{applicant_name}` 占位符 + 客户默认命名）
- `backend/app/modules/documents/official_notice_catalog.py` — 新增 22 行致函官方目录 seed
- `backend/app/modules/documents/export_excel.py`（新文件）+ `documents/api.py` — 文书清单 Excel 导出端点
- `backend/app/modules/fees/service.py` — `calculate_fee_amount` 支持 `PER_PAGE`
- `backend/scripts/seed_dev.py` — 格式函映射/模板 seed（8 行）+ 目录接线
- `backend/tests/test_format_letter_mapping_seed.py`、`test_document_list_export_api.py`（新）；`test_annuity_e2e.py`（结构字段 round-trip/filter 测试 + PER_PAGE 测试 + 字段集更新）

前端：

- `frontend/src/modules/documents/pages/DocumentList.vue` + `api/documents.ts` — 导出清单按钮与 API
- `frontend/src/modules/tasks/pages/TodayReminders.vue` + `api/tasks.types.ts` — 打印清单按钮（复用 `/tasks/print`）

Demo 基础设施：

- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/pdP1LiveSeed.py` — clear_fixture 删除映射/模板前先解除动态 handoff 引用（V6 Residual 4 闭环）
