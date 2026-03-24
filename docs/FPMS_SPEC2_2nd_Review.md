# FPMS SPEC 2.0 Implementation Review Report (2nd Review)

**Review Date**: 2026-03-23
**Scope**: All SPEC 2.0 functional modules EXCEPT Document Generation
**Baseline**: Commit `a44d2d8` (master branch, clean worktree)
**Quality Gates**: Backend 183 tests PASS | Frontend lint PASS | typecheck PASS | build PASS

---

## Executive Summary

Overall implementation completeness: **~44%** (excluding Document Generation)

| Module | Completion | Status |
|--------|-----------|--------|
| Module 1: Case Maintenance (案卷维护) | ~70% | Core CRUD complete, missing ~15 fields, batch filing, PCT frontend tabs |
| Module 2: Documents & Correspondence (中间文件) | ~35% | Basic CRUD exists, 5-step wizard / 4 DocTypes / mailing completely missing |
| Module 3: Deadline & Docket (时限管理) | ~40% | Basic task CRUD exists, template missing key fields, special search missing |
| Module 4: Fee Management (费用管理) | ~30% | Draft/rate complete, gov payment/grant fee/annuity API/case receipt all missing |
| Module 5: Billing & Receivables (账单收款催款) | ~55% | Bill/payment/offset core complete, bad debt/prepayment/reverse offset UI missing |
| Module 6: Commission (提成管理) | ~40% | Rule/generation/settlement exists, multi-agent split/WaitPay calc/reports missing |
| Module 7: Consulting & Search (顾问检索) | ~45% | Case creation/fee draft complete, extension fields/expense UI/profitability missing |
| Module 8: Settings & Reports (设置报表) | ~40% | Master data/params complete, **all statistical reports** missing |

---

## Module 1: Case Maintenance (案卷维护) — ~70%

### User Story / FR Audit

| US/FR ID | Description | Backend | Frontend | Gap |
|----------|-------------|---------|----------|-----|
| US-CM-01 | 新案建立：录入基本信息、参与方、日期、控制标记并保存 | DONE | PARTIAL | Missing: recv_date, draw_pages, claim_pages, manuscript_words, discount_rate, no_power, no_prio_text, require_hk; Limited address field support |
| US-CM-02 | 扩展信息维护：优先权、菌种保藏、PCT、无效案字段 | DONE | PARTIAL | Backend supports all; Frontend needs PCT tabs for PCT cases and full invalidation case UI |
| US-CM-03 | 参与方管理：选择/新增客户、申请人、外方代理、地址 | DONE | PARTIAL | Missing: DocAddressID, BillAddressID (doc/bill mailing addresses); No address selection UI from master data |
| US-CM-04 | 限制修改视图：代理人补充少量字段 | DONE | PARTIAL | Backend endpoint /cases/{id}/limited-edit exists; Frontend component exists but limited to title/spec fields only; Missing: spec_pages, claim_count exposure |
| **US-CM-05** | **批件递交批处理：批量设置递交日期和实审请求** | **MISSING** | **MISSING** | No backend endpoint; No UI page; Deferred to non-MVP (case_future.md) |
| FR-CM-01 | 根据案件类型、专利类别、申请方向创建新案，案卷号全局唯一 | DONE | DONE | Complete |
| FR-CM-02 | 保存时校验必填字段及组合规则 | PARTIAL | PARTIAL | Missing: ToCountry field; Missing: ApplicantKind↔IsLegalEntity consistency check |
| FR-CM-03 | 支持从主数据中选择客户/申请人/外方代理，允许新增并回填 | DONE | PARTIAL | Frontend has client selection but lacks applicant master data pulldown |
| FR-CM-04 | 维护完整法律状态枚举，支持由中间文件/流程自动更新 | DONE | DONE | Complete |
| FR-CM-05 | 支持优先权、菌种保藏、PCT信息、无效案专属字段 | DONE | PARTIAL | Backend: T_Priority, T_BioDeposit models complete; Frontend: needs PCT/invalidation case UI tabs |
| FR-CM-06 | 提供限制修改视图，只能编辑白名单字段 | PARTIAL | PARTIAL | Backend: /limited-edit only allows title/spec; Frontend: LimitedEditDialog minimal |
| **FR-CM-07** | **提供案件递交批处理（按条件筛选、批量设置状态）** | **MISSING** | **MISSING** | Deferred to non-MVP |

### Key Missing Fields in Database Model

- `recv_date` (present but not exposed in schema forms)
- `draw_pages`, `claim_pages`, `manuscript_words` (missing)
- `discount_rate`, `no_power`, `no_prio_text`, `require_hk` (missing)
- `to_country` (missing - required for spec 2.4.2)
- `doc_address_id`, `bill_address_id` (missing - required for spec 2.4.3)
- `issue_date`, `cert_no`, `first_annuity_year` (missing)

---

## Module 2: Documents & Correspondence (中间文件) — ~35%

### User Story / FR Audit

| US/FR ID | Description | Backend | Frontend | Gap |
|----------|-------------|---------|----------|-----|
| US-WD-01 | 来文批量录入中间文件 | PARTIAL | PARTIAL | DocType only IN/OUT (spec requires OFFICIAL_IN/OUT, CLIENT_IN/OUT); Missing: DispatchDate, ReceiveDate, ForwardDate, IncomingRegNo, OutgoingRegNo, NotifyAgent; No batch wizard |
| US-WD-02 | 发文登记与自动核销 | PARTIAL | PARTIAL | Reply chain (reply_to_id) implemented; Task auto-writeoff works; Missing: Frontend reply chain management UI |
| US-WD-03 | 期限联动（自动生成时限任务） | PARTIAL | MISSING | Backend has deadline_template_code in DocTemplate; Missing: Document.Deadline field; Missing: Step 3 UI |
| US-WD-04 | 费用联动（自动生成费用草单） | PARTIAL | MISSING | Backend fee_linking_service.py exists; Missing: FeeRate lookup/reduction logic; Missing: Step 4 UI |
| US-WD-05 | 电子档案存档（0..N附件） | DONE | PARTIAL | Backend DocAttachment CRUD complete; Missing: Language field (CN/EN/OTHER) |
| US-WD-06 | 查询与清单输出 | PARTIAL | PARTIAL | Basic filters work; Missing: TemplateCode/DocName search, "HasAttachment" filter |
| **US-WD-07** | **邮寄信息登记、文件交接单、信封打印** | **MISSING** | **MISSING** | No T_DocDispatch/T_DocDispatchLine tables; No endpoints; No UI |
| **FR-WD-02** | **批量录入向导 (Step 1-2)** | **MISSING** | **MISSING** | No wizard architecture; Only single-doc create form |
| FR-WD-03 | 模板自动填充默认值 | PARTIAL | MISSING | Backend applies template defaults; No frontend integration |
| FR-WD-04 | 需回复文件自动生成时限任务 | PARTIAL | MISSING | TaskGenerationService exists; Missing: Document.Deadline field; No Step 3 UI |
| FR-WD-05 | 自动生成费用草单 | PARTIAL | MISSING | Basic FeeDraft creation exists; Missing: FeeRate lookup, reduction logic |
| **FR-WD-08** | **邮寄信息登记 (OutgoingRegNo)** | **MISSING** | **MISSING** | No endpoint for batch OutgoingRegNo/ForwardDate updates |
| **FR-WD-09** | **文件交接单 (T_DocDispatch/Line)** | **MISSING** | **MISSING** | No tables, no endpoints, no UI |
| **FR-WD-10** | **信封打印** | **MISSING** | **MISSING** | No address selection or printing logic |

### Critical Gaps

1. **Wizard Architecture**: Entire 5-step wizard (spec §3.4) missing — only single-doc create form exists
2. **Field Completeness**: Document model missing 11+ spec fields
3. **DocType Categories**: Cannot distinguish OFFICIAL vs CLIENT documents (only IN/OUT)
4. **Compliance Features**: Mailing registration, dispatch slips, envelope printing completely unimplemented

---

## Module 3: Deadline & Docket (时限管理) — ~40%

### User Story / FR Audit

| US/FR ID | Description | Backend | Frontend | Gap |
|----------|-------------|---------|----------|-----|
| US-DL-01 / FR-DL-01 | 时限模板配置 | PARTIAL | PARTIAL | Missing: add_years, deadline_base enum, remind_1/2/3_offset_days, remind_base, daily_remind, default_supervisor_id |
| US-DL-02 / FR-DL-02 | 自动创建时限任务（从中间文件/案件事件） | PARTIAL | N/A | TaskGenerationService exists; Missing: DeadlineBase enum branching, remind calculation, daily remind logic |
| US-DL-03 / FR-DL-04 | 日常提醒 – 作业人视角 | PARTIAL | PARTIAL | Missing: date range filtering, remind_base selection, overtime detection |
| US-DL-05 / FR-DL-05 | 日常提醒 – 监督人视角 | PARTIAL | PARTIAL | Missing: supervisor operations (re-assign, bulk change, remarks) |
| US-DL-06 / FR-DL-06 | 手工维护时限任务 | DONE | PARTIAL | Backend CRUD complete; Frontend missing update/edit form (read-only detail only) |
| **US-DL-07 / FR-DL-07** | **专项检索（申请费 & 实审请求时限）** | **MISSING** | **MISSING** | No endpoints for APPLY_FEE_LIMIT / EXAM_REQUEST_LIMIT template search |
| US-DL-08 / FR-DL-08 | 登录提醒与清单打印 | PARTIAL | PARTIAL | Today endpoint exists; Missing: remind1/2/3 matching, daily remind range |
| FR-DL-09 | 清单导出/打印 | PARTIAL | MISSING | Backend has single-task print; No bulk export endpoint; No frontend export UI |
| FR-DL-10 | 操作日志 | PARTIAL | DONE | Missing: UPDATE/RESTORE actions, OldValue/NewValue JSON snapshots |

### Critical Missing Fields

**T_TaskTemplate**: `add_years`, `deadline_base` enum, `remind_base` enum, `r1/r2/r3_offset_days`, `daily_remind`, `default_supervisor_id`

**T_Task**: `remind1`, `remind2`, `remind3` dates, `daily_remind_from`, `daily_remind`, `remark`, `is_written_off`

---

## Module 4: Fee Management (费用管理) — ~30%

### User Story / FR Audit

| US/FR ID | Description | Backend | Frontend | Gap |
|----------|-------------|---------|----------|-----|
| US-FE-01 | 费用草单生成与维护 | DONE | DONE | Complete — FeeDraft CRUD, items, lock/unlock |
| US-FE-02 / FR-FE-01 | 标准费率与费减/折扣计算 | PARTIAL | PARTIAL | CalcMode only FIXED/PER_CLAIM (spec requires BY_YEAR/BY_PAGES/COMPOSITE); No discount UI |
| **US-FE-03 / FR-FE-04** | **官费清单与缴费** | **MISSING** | **MISSING** | T_PayList/T_GovPayment models exist but no API; No UI |
| **US-FE-04 / FR-FE-05** | **授权费/年登印费管理** | **MISSING** | **MISSING** | No T_GrantFeeTask model; No endpoints; No UI |
| US-FE-05 / FR-FE-06 | 年费管理（多年度） | PARTIAL | MISSING | T_AnnuityTask model exists; No API endpoints; No UI |
| US-FE-06 / FR-FE-07 | 个案收款登记 | PARTIAL | MISSING | CaseReceipt model exists; No API endpoints; No UI |
| US-FE-07 / FR-FE-08 | 支出费用管理 | PARTIAL | MISSING | Expense model exists (minimal); No API; No UI |
| **US-FE-08 / FR-FE-09** | **费用情况查询一览** | **MISSING** | **MISSING** | No dual-table query endpoints; No comprehensive UI |
| FR-FE-03 | 自动金额计算 | PARTIAL | MISSING | Only FIXED/PER_CLAIM; Missing BY_YEAR/BY_PAGES/COMPOSITE |

### Key Gaps

- **Official Payment System** (T_PayList/T_GovPayment): Models exist but no API/UI
- **Grant Fee Management**: No model at all
- **Annuity Management**: Model exists, no service/API/UI
- **Case Receipt**: Model exists, no API/UI
- **Fee Calculation Modes**: Only 2 of 5 CalcModes implemented

---

## Module 5: Billing, Receivables, Dunning & Bad Debt (账单收款催款) — ~55%

### User Story / FR Audit

| US/FR ID | Description | Backend | Frontend | Gap |
|----------|-------------|---------|----------|-----|
| US-BL-01 / FR-BL-02 | 从费用草单生成账单 | DONE | DONE | Complete |
| US-BL-02 / FR-BL-03 | 手工创建账单 (AR/AP) | DONE | DONE | Missing: DiscountRate field; Adjustment bill not explicit |
| US-BL-03 / FR-BL-04 | 账单打印/导出 | PARTIAL | MISSING | Backend renderer exists; No frontend print button |
| US-BL-04 / FR-BL-05 | 收款登记与冲销 | DONE | DONE | Missing: exchange rate field for currency conversion |
| US-BL-05 / FR-BL-06 | 冲销反转 | DONE | **MISSING** | Backend reverse_offset_service() exists; No frontend UI |
| US-BL-06 / FR-BL-07 | 坏账标记与恢复 | PARTIAL | **MISSING** | Backend: status change only; Missing: IsBadDebt, BadDebtDate, BadDebtReason fields; No UI |
| US-BL-06 / FR-BL-08 | 催款生成与催款函 | PARTIAL | PARTIAL | Dunning tables exist; Missing: dunning letter generation; Frontend: basic list only |
| US-BL-07 / FR-BL-09 | 预收款管理 | PARTIAL | **MISSING** | PaymentLine supports prepay; No dedicated tracking/report UI |

### Key Missing Fields

- **Bill model**: `DiscountRate`, `ExchangeRate`, `IsBadDebt`, `BadDebtDate`, `BadDebtReason`
- **BillItem model**: `Quantity`, `UnitPrice`, `Currency`, `LocalAmount`, `TaxRate`, `TaxAmount`
- **Payment model**: `PayMethod`, `BankRefNo`, `ExchangeRate`

---

## Module 6: Agent Commission (提成管理) — ~40%

### User Story / FR Audit

| US/FR ID | Description | Backend | Frontend | Gap |
|----------|-------------|---------|----------|-----|
| US-COM-01 / FR-COM-01 | 提成规则配置 | DONE | DONE | Missing: BaseMode enum, ServiceFeeFactor, ClientGroup fields |
| US-COM-02 / FR-COM-02 | 账单生成时自动生成提成 | PARTIAL | MISSING | Backend hook exists; No dedicated UI for viewing |
| **US-COM-03 / FR-COM-03** | **多代理人提成分成** | **MISSING** | **MISSING** | Commission model has single agent_id; No allocation table or ratio logic |
| US-COM-04 / FR-COM-04 | WaitPay（款到后结算） | PARTIAL | MISSING | Flag exists; Missing PaidRatio calculation logic; No UI |
| US-COM-05 / FR-COM-05 | ForceSettle（强制可结算） | PARTIAL | MISSING | Flag exists; No UI to set flag; No permission control |
| US-COM-06 / FR-COM-06 | 结算批次生成 | PARTIAL | PARTIAL | CommissionSettlement tables exist; Frontend limited functionality |
| US-COM-07 / FR-COM-07 | 提成报表与导出 | PARTIAL | MISSING | No dedicated report endpoints; No aggregation/export |

### Critical Gap

**FR-COM-03 (Multi-Agent Split)**: Commission model designed for single agent only — no allocation table, no share ratio, no SecondAgentID support in T_Case.

---

## Module 7: Consulting & Search (顾问/检索) — ~45%

### User Story / FR Audit

| US/FR ID | Description | Backend | Frontend | Gap |
|----------|-------------|---------|----------|-----|
| US-CS-01 / FR-CS-01 | 顾问/检索项目立案 | DONE | DONE | Missing extension fields: ConsultingScope, DeliverableType, FixedFee, EstimatedHours, StartDate, EndDate |
| US-CS-02 / FR-CS-02 | 内部任务管理 | DONE | PARTIAL | Reuses generic task module; No consulting-specific templates |
| US-CS-03 / FR-CS-03 | 支出记录追踪 | DONE | MISSING | Expense model exists; No dedicated consulting expense UI |
| US-CS-04 / FR-CS-04 | 费用草单生成 (fixed/hourly) | DONE | DONE | Complete |
| US-CS-05 / FR-CS-05 | 账单与收款 | DONE | MISSING | Reuses billing module; No dedicated consulting bill UI |
| US-CS-06 / FR-CS-06 | 提成 | PARTIAL | MISSING | Commission triggers on bill; No dedicated consulting commission UI |

---

## Module 8: Settings, Search & Reports (设置/报表) — ~40%

### Feature Audit

| Feature Area | Backend | Frontend | Gap |
|--------------|---------|----------|-----|
| **SETTINGS** | | | |
| Master Data: Clients (CRUD + Address + Contact) | DONE | DONE | Complete |
| Master Data: Applicants | MISSING | MISSING | No applicant management endpoints or UI |
| Master Data: Countries | MISSING | MISSING | No country maintenance |
| Master Data: Bio Deposit Units | MISSING | MISSING | No bio deposit unit management |
| Business Parameters: Fee Rates | DONE | DONE | Complete |
| Business Parameters: Task Templates | DONE | DONE | Complete |
| Business Parameters: System Parameters | DONE | DONE | Complete |
| Document Templates (T_Template) | DONE | DONE | Complete |
| Letterheads (T_LetterHead) | DONE | DONE | Complete |
| **SEARCH & QUERIES** | | | |
| Advanced Case Search | PARTIAL | PARTIAL | Missing: applicant_id, secondary_agent_id, fee status filters, patent_no |
| Intermediate Document Search | MISSING | MISSING | No document-specific search endpoint (spec 9.3.2) |
| Fee Status Query | PARTIAL | MISSING | Endpoints exist but no combined query UI |
| Deadline Search | PARTIAL | PARTIAL | TodayReminders only; No dedicated deadline search UI |
| **REPORTS** | | | |
| Case Statistics Report | MISSING | MISSING | By client/country/agent/year-month trends |
| Fee & Income Statistics Report | MISSING | MISSING | Service fee by client/case type, fee income trends |
| Annuity Statistics Report | MISSING | MISSING | Annuity payment status by country/client/year |
| Bill/AR/Overdue/Bad Debt Report | MISSING | MISSING | Aging, overdue, bad debt tracking |
| Commission Statistics Report | PARTIAL | PARTIAL | Limited to settlement; Missing agent/case type breakdown |

---

## Priority-Ranked MISSING Features

### P0 — Core Business Flow Gaps (blocks end-to-end closure)

| # | Feature | Module | Notes |
|---|---------|--------|-------|
| 1 | 官费清单与缴费 (FR-FE-04) | Fees | Model exists, need API + UI |
| 2 | 个案收款登记端点 (FR-FE-07) | Fees | Model exists, need API + UI |
| 3 | 年费管理 API/UI (FR-FE-06) | Fees | Model exists, need API + UI |
| 4 | 冲销反转前端 | Billing | Backend service exists, need UI |

### P1 — Important Functional Gaps

| # | Feature | Module | Notes |
|---|---------|--------|-------|
| 5 | 多代理人提成分成 (FR-COM-03) | Commission | Model redesign needed (single → multi agent) |
| 6 | 坏账完整流程 | Billing | Need fields (IsBadDebt/Date/Reason) + recovery UI |
| 7 | 预收款管理报表 | Billing | Logic supports prepay, need dedicated report |
| 8 | 中间文件5步向导 | Documents | Major UI architecture work |
| 9 | 时限模板关键字段补全 | Tasks | 3-level reminders, deadline_base, daily_remind |
| 10 | 案卷缺失字段补全 (~15 fields) | Cases | draw_pages, claim_pages, to_country, etc. |

### P2 — Enhancement Features

| # | Feature | Module | Notes |
|---|---------|--------|-------|
| 11 | 批件递交 (US-CM-05) | Cases | Batch filing workflow |
| 12 | 邮寄/交接单/信封 (FR-WD-08~10) | Documents | T_DocDispatch tables + UI |
| 13 | 所有统计报表 | Reports | Case/Fee/Annuity/Billing/Commission reports |
| 14 | 申请人/国家主数据 | Settings | Applicant + Country CRUD |
| 15 | 授权费管理 (US-FE-04) | Fees | T_GrantFeeTask model + full workflow |
| 16 | 费用综合查询 (US-FE-08) | Fees | Dual-table query (payment + receipt) |
| 17 | 专项检索 (US-DL-07) | Tasks | APPLY_FEE_LIMIT / EXAM_REQUEST_LIMIT search |
| 18 | 高级案件查询增强 | Settings | applicant_id, patent_no, fee status filters |
| 19 | 中间文件专项查询 (spec 9.3.2) | Settings | Document-specific search endpoint |
| 20 | 账单打印前端按钮 | Billing | Backend renderer exists, need frontend button |

---

## Document Version

- **Version**: 2.0
- **Review Date**: 2026-03-23
- **Reviewer**: Claude Code (automated audit)
- **Baseline Commit**: `a44d2d8` on master
- **Previous Review**: `docs/FPMS_Code_Review_Report_SPEC_2.0_20260227.md`
