# FPMS MVP1 Comprehensive GAP Analysis

> **Author**: Senior Architect & BA
> **Date**: 2026-02-23
> **Scope**: Two-way GAP analysis between (1) Current Implementation vs FPMS SPEC 2.0, and (2) FPMS SPEC 2.0 vs MVP1 Scope

---

## Part 1: Current Implementation vs FPMS SPEC 2.0 — Detailed GAP Analysis

### Module 1: Case Maintenance (SPEC Ch.2)

#### 1.1 Data Model GAPs

| SPEC 2.0 Field/Table | Current Status | GAP Detail |
|---|---|---|
| `T_Case` — 50+ fields (RO, ISA, IPEA, IntlAppNo, IntlAppDate, IntlPubNo, IntlPubDate, NeedIPER, IPERDate, PubDate, PubNo, GrantDate, GrantNo, PatentNo, ValidUntil, FirstAnnuityYear, IsFeeMonitor, ApplicantKind, FeeReduction, NoPower, NoPrioText, HasExamRequest, SpecPages, ClaimCount, FromCountry, ToCountry, ForeignAgentID, PrimaryAgentID, SecondAgentID, DraftorID, etc.) | **Partial** — `models.py` has ~15 fields: id, case_no, case_type, patent_category, flow_dir, client_id, title_cn, title_en, app_no, status, filing_date, recv_date, notes, applicants/inventors/priorities as JSON | **MAJOR GAP**: ~35+ fields missing. No PCT extension fields, no agent assignment fields, no control flags (IsFeeMonitor, FeeReduction, NoPower, etc.), no grant/pub dates, no spec pages/claim count |
| `T_CaseApplicant` (separate table with seq, IsPrimary, ApplicantID FK) | applicants stored as JSON list of dicts in T_Case | **GAP**: No separate normalized table; no FK to T_Applicant master; no IsPrimary flag; no address fields |
| `T_CaseInventor` (separate table with seq, name_cn, name_en) | inventors stored as JSON list of dicts | **GAP**: No separate normalized table; current impl stores as embedded JSON |
| `T_Priority` (separate table with seq, country_code, prio_no, prio_date) | priorities stored as JSON list of dicts | **GAP**: No separate normalized table; no PrioDate→Case.PrioDate aggregation |
| `T_BioDeposit` (biological deposit records) | Not implemented | **GAP**: Entire sub-model missing |
| `CaseType` enum: NORMAL, PCT_INTL, PCT_NATIONAL, INVALIDATION, LITIGATION, CONSULTING, SEARCH | Only NORMAL enum value used | **GAP**: 6 of 7 case types not supported |
| `CaseStatus` enum: 13 legal states (NOT_FILED → WAITING_RECEIPT → ACCEPTED → PRELIM → PUBLISHED → SUB_EXAM → OA1 → OA2 → GRANT_PENDING → GRANTED → TERMINATED → INVALIDATED → LITIGATION_*) | Status field exists with same 13 values (V3 Stepper recently added) | **OK** — V3 work added full status support |
| Batch filing (NOT_FILED → WAITING_RECEIPT for multiple cases) | Not implemented | **GAP**: No batch filing UI or API |
| Case limited edit view (Agent role whitelist) | `CaseUpdateLimited` schema exists with title_cn, title_en, inventors | **Partial** — Schema exists but limited compared to SPEC's full whitelist |
| Case export (Excel/CSV) | Backend `export_cases` endpoint exists | **OK** |

#### 1.2 API GAPs

| SPEC Feature | Current API | GAP |
|---|---|---|
| POST /cases (full field set) | `POST /api/v1/cases` — CaseCreate schema has case_no, case_type, patent_category, flow_dir, client_id, title_cn, title_en, app_no, applicants, inventors, priorities | **Partial** — Missing 30+ fields from SPEC |
| PUT /cases/:id (full update) | `PUT /api/v1/cases/:id` — CaseUpdateFull with title_cn, title_en, app_no, status, applicants, inventors, priorities | **Partial** — Missing many updateable fields |
| PATCH /cases/:id (limited edit) | `PATCH /api/v1/cases/:id` — CaseUpdateLimited | **OK** conceptually |
| GET /cases (advanced search with 20+ filter dimensions) | `GET /api/v1/cases` supports q, page, page_size, status | **MAJOR GAP**: Only basic search. Missing: client_id filter, case_type, patent_category, flow_dir, date ranges, agent filters, control flag filters |
| Batch status update (filing batch) | Not implemented | **GAP** |

#### 1.3 Frontend GAPs

| SPEC Feature | Current Status | GAP |
|---|---|---|
| Case create form (full field set) | `CaseCreate.vue` — basic fields only | **GAP**: Missing PCT fields, agent assignment, control flags, spec pages/claims |
| Case detail page (all tabs) | `CaseDetail.vue` — overview, claims (placeholder), docs (placeholder), fees (placeholder), billing (receipts summary), tasks (placeholder) | **Partial** — Most tabs are placeholders |
| Case list with advanced filters | `CaseList.vue` — basic list with V3 workflow step filter | **GAP**: No advanced filter panel |
| Case stepper (V3 workflow) | `CaseStepper.vue` — 5-step workflow display | **OK** — Recently implemented |

---

### Module 2: Documents & Correspondence (SPEC Ch.3)

#### 2.1 Data Model GAPs

| SPEC 2.0 Feature | Current Status | GAP |
|---|---|---|
| `T_DocTemplate` — template registry with StatusEffect, StatusRestore, DeadlineTemplateCode, FeeDraftType, FeeItemList, InputFieldList, ReplyToTemplateCode, NeedNotifyAgent, PlainTemplateID_CN/EN | Not implemented | **MAJOR GAP**: Entire document template configuration table missing. This is the core engine for automated workflow (status changes, task generation, fee draft generation from document events) |
| `T_Document` — 20+ fields (CaseID, DocType, TemplateCode, DocName, Direction, DispatchDate, ReceiveDate, InputDate, ForwardDate, IncomingRegNo, OutgoingRegNo, PostRegNo, NeedReply, ReplyDate, ReplyToID, NotifyAgent, Summary, ExtraData, StatusEffect) | `T_Document` exists with: id, case_id, doc_type, title, direction, doc_date, deadline_date, template_code, notes, status, file_path | **Partial** — Has basic fields but missing: DispatchDate vs ReceiveDate distinction, NeedReply/ReplyDate/ReplyToID chain, NotifyAgent, IncomingRegNo/OutgoingRegNo, ForwardDate, StatusEffect, ExtraData |
| `T_DocAttachment` — multiple attachments per document (FileName, FilePath, FileSize, MimeType, seq) | Single file_path on T_Document | **GAP**: No multi-attachment support |
| `T_DocDispatch` — envelope/mailing tracking (DispatchType, PostRegNo, PostDate, TrackingURL, DeliveryConfirmed, Recipient) | Not implemented | **GAP**: Entire mailing tracking missing |
| 5-step document wizard (Step1: case+template, Step2: details, Step3: auto-task, Step4: auto-fee-draft, Step5: attachments) | Simple CRUD form for documents | **MAJOR GAP**: No wizard workflow; no auto-generation of tasks or fee drafts from document events |
| Document→Task linkage (auto-create deadline task from document template) | Not implemented | **GAP**: Documents and tasks are independent |
| Document→FeeDraft linkage (auto-create fee draft from document template) | Not implemented | **GAP** |
| Document→Case status change (StatusEffect/StatusRestore) | Not implemented | **GAP**: Document creation doesn't update case status |

#### 2.2 Frontend GAPs

| SPEC Feature | Current Status | GAP |
|---|---|---|
| Document register wizard (5 steps) | `DocumentCreate.vue` — simple form | **GAP** |
| Document list with advanced search (DocType, Template, Case, date ranges) | `DocumentList.vue` — basic list | **Partial** |
| Document detail with attachments, dispatch tracking | `DocumentDetail.vue` — basic detail | **GAP** |

---

### Module 3: Deadline & Docket (SPEC Ch.4)

#### 3.1 Data Model GAPs

| SPEC 2.0 Feature | Current Status | GAP |
|---|---|---|
| `T_TaskTemplate` — full template with DeadlineBase, AddYears/Months/Days, InnerOffsetDays, RemindBase, R1/R2/R3_OffsetDays, DailyRemind, DailyRemindFrom, DefaultWorkerRole, DefaultSupervisorID, LinkedDocTemplate, FeeGroup | Not implemented as a table; task creation is manual | **MAJOR GAP**: No task template table. All deadline calculation rules should be config-driven but are currently non-existent |
| `T_Task` — 15+ time fields (BaseDate, Deadline, InnerDeadline, Remind1/2/3, DailyRemindFrom, DoneDate, IsWrittenOff) + DocID FK | `T_Task` has: id, case_id, title, description, task_type, priority, status, due_date, assigned_to, assigned_by, notes | **Partial** — Has basic fields but missing: BaseDate, InnerDeadline, Remind1/2/3, DailyRemindFrom, DocID linkage, TemplateCode, WorkerID/SupervisorID distinction, IsWrittenOff |
| `T_TaskLog` — audit trail (TaskID, Action, ActionBy, ActionAt, OldValue, NewValue, Comment) | Not implemented | **GAP**: No task action history/audit trail |
| Auto-task creation from document events | Not implemented | **GAP** |
| Worker vs Supervisor views (different dashboards) | Single task list | **GAP** |
| Task status: OPEN → DONE / CANCELLED / REOPEN with full state machine | Status: OPEN, IN_PROGRESS, COMPLETED, CANCELLED | **Partial** — Similar but no REOPEN, no IsWrittenOff |
| Specialized searches (application fee deadline search, exam request search) | Not implemented | **GAP** |
| Today's reminder page (tasks due today/overdue grouped by worker/supervisor) | `TodayReminders.vue` exists | **Partial** — Basic implementation exists |

---

### Module 4: Fee Management (SPEC Ch.5)

#### 4.1 Data Model GAPs

| SPEC 2.0 Feature | Current Status | GAP |
|---|---|---|
| `T_FeeRate` — full fee rate table with Group, CountryCode, CaseType, PatentCategory, FeeCode, FeeName, FeeType (GOV/SERVICE/MISC), CalcMode (FIXED/PER_CLAIM/PER_PAGE/TIER/FORMULA), CalcParams JSON, DefaultCurrency, AllowReduction, IsActive, EffectiveFrom/To | `T_FeeRate` exists with: id, fee_code, fee_name, fee_type, unit_price, currency, category, is_active, notes | **Partial** — Missing: Group, CountryCode, CaseType, PatentCategory dimensions; CalcMode/CalcParams calculation engine; AllowReduction; effective date range |
| `T_FeeDraft` — draft header with Type enum (APPLY_FEE, OA_FEE, GRANT_FEE, ANNUITY_FEE, INVALIDATION_FEE, LITIGATION_FEE, CONSULT_FEE, SEARCH_FEE, INTERMEDIATE_FEE), Currency, TotalGov/TotalService/TotalMisc/TotalAmt, Status | `T_FeeDraft` exists with: id, case_id, draft_no, title, draft_type, currency, total_amount, status, notes | **Partial** — Missing: TotalGov/TotalService/TotalMisc breakdown; Type enum only has basic types |
| `T_FeeItem` — draft line items with RateID FK, FeeCode, FeeName, YearNo, FeeType, Quantity, UnitPrice, Amount, Currency, ExchangeRate, LocalAmount, IsAuto, IsReduced, IsDiscounted, DiscountRate | `T_FeeItem` exists with: id, draft_id, fee_code, fee_name, fee_type, quantity, unit_price, amount, currency, notes | **Partial** — Missing: RateID FK, YearNo, ExchangeRate/LocalAmount, IsAuto/IsReduced/IsDiscounted flags |
| `T_PayList` — government fee payment list (Type, ListNo, FlowDir, PlannedPayDate, ActualPayDate, Currency, TotalAmt, InvoiceNoFrom/To, Status) | Not implemented | **MAJOR GAP**: Entire gov fee payment tracking missing |
| `T_GovPayment` — individual gov fee payment records (PayListID, CaseID, ItemID, FeeCode, YearNo, PlannedAmt/Date, PaidAmt/Date, VoucherNo, InvoiceNo) | Not implemented | **MAJOR GAP** |
| `T_GrantFeeTask` — grant fee specific task table | Not implemented | **GAP** |
| `T_AnnuityTask` — annual fee task table (CaseID, YearNo, DueDate, GraceDueDate, ClientInstruction, NotifyDate, IsOverdue, GovFeeAmt, ServiceFeeAmt) | Not implemented | **MAJOR GAP**: Entire annual fee management missing |
| `T_CaseReceipt` — per-case receivable/received tracking (CaseID, FeeCode, YearNo, FeeType, ReceivableAmt, ReceivedAmt, ReceiptDate, IsArrears, InvoiceNo, IsCommissionable) | `T_CaseReceipt` exists with: id, case_id, bill_id, fee_type, receivable_amt, received_amt | **Partial** — Missing: FeeCode, YearNo, ReceiptDate, IsArrears, InvoiceNo, IsCommissionable |
| `T_Expense` — project expense tracking (CaseID, AgentID, ItemName, Category, WorkerID, Date, Quantity, UnitPrice, Total, Currency) | Not implemented | **GAP** |
| Fee draft auto-generation from document template events | Not implemented | **GAP** |
| Fee draft → Bill generation pipeline (batch, multi-draft to single bill) | Implemented: POST /api/v1/billing/bills/from-drafts | **OK** |

---

### Module 5: Billing, Receivables, Dunning & Bad Debt (SPEC Ch.6)

#### 5.1 Data Model GAPs

| SPEC 2.0 Feature | Current Status | GAP |
|---|---|---|
| `T_Bill` — full bill with Direction (AR/AP), BillNo, ClientID, BillDate, DueDate, Currency, ExchangeRate, DiscountRate, TotalGov/TotalService/TotalMisc, Amount, Balance, Status (UNSETTLED/PARTIALLY_SETTLED/SETTLED/BAD_DEBT), IsBadDebt, BadDebtDate, BadDebtReason | `T_Bill` exists with: id, bill_no, client_id, bill_date, due_date, currency, total_amount, paid_amount, balance, status, notes | **Partial** — Missing: Direction (AR/AP), TotalGov/TotalService/TotalMisc breakdown, DiscountRate, ExchangeRate, IsBadDebt/BadDebtDate/BadDebtReason |
| `T_BillItem` — bill line items with CaseID, DraftID, FeeItemID, FeeCode, FeeName, YearNo, FeeType, Quantity, UnitPrice, Amount, Currency, LocalAmount | `T_BillItem` exists with basic fields | **Partial** — Missing some FK tracing fields |
| `T_Payment` — payment record with ClientID, PayNo, PayDate, Currency, Amount, PayMethod, BankRefNo | `T_Payment` exists with similar fields | **OK** |
| `T_PaymentLine` — payment allocation line (RawAmount, AllocatedAmt, BalanceAmt, CaseID) | Not implemented as separate table | **GAP**: Payment splitting/allocation not supported |
| `T_Offset` — offset/reconciliation record (PaymentLineID, BillID, OffsetAmt, OffsetDate, IsReversed, ReversedAt, ReversedBy) | `T_Offset` exists with basic fields | **Partial** — Missing: IsReversed/ReversedAt/ReversedBy (no reverse offset support) |
| `T_Dunning` — dunning notice header (DunningNo, ClientID, ToDate, Currency, TotalAmt, Status, SentDate) | Not implemented | **GAP** — explicitly excluded from MVP1 |
| `T_DunningLine` — dunning line items (BillID, BillNo, OutstandingAmt) | Not implemented | **GAP** |
| Manual bill creation (hand-keyed, no fee draft) | POST /api/v1/billing/bills exists | **Partial** — Basic manual creation exists |
| Bill template rendering (docxtpl → Word) | `doc_render_bill_context.py` exists, template rendering works | **OK** |
| Prepayment management (PaymentLine with BalanceAmt>0, no bill yet) | Not fully supported | **GAP** |
| Offset reversal (un-offset) | Not implemented | **GAP** |
| Bad debt marking (IsBadDebt, Status=BAD_DEBT) | Not implemented | **GAP** — explicitly excluded from MVP1 |

---

### Module 6: Agent Commission Management (SPEC Ch.7)

| SPEC 2.0 Feature | Current Status | GAP |
|---|---|---|
| `T_CommissionRule` — commission rule table (CaseType, FlowDir, PatentCategory, ClientGroup, Stage1Rate, Stage2Rate, BaseMode, BaseFixedAmt) | Not implemented | **ENTIRE MODULE MISSING** — explicitly excluded from MVP1 |
| `T_Commission` — commission record (CaseID, AgentID, RuleID, BaseFee, S1_Rate/Amt/Done, S2_Rate/Amt/Done, WaitPay, ForceSettle) | Not implemented | **GAP** |
| `T_CommissionSettlement` / `T_CommissionSettleLine` — settlement batch | Not implemented | **GAP** |
| Commission auto-calculation on bill generation | Not implemented | **GAP** |
| Multi-agent commission splitting | Not implemented | **GAP** |
| WaitPay / ForceSettle logic | Not implemented | **GAP** |

---

### Module 7: Consulting & Search Projects (SPEC Ch.8)

| SPEC 2.0 Feature | Current Status | GAP |
|---|---|---|
| CaseType=CONSULTING/SEARCH with extended fields (ConsultingScope, DeliverableType, FixedFee, EstimatedHours, StartDate, EndDate) | Not implemented | **ENTIRE MODULE MISSING** — explicitly excluded from MVP1 |
| Internal task management for projects | Not implemented | **GAP** |
| Project expense tracking (T_Expense) | Not implemented | **GAP** |
| Consulting-specific fee draft types (CONSULT_FEE, SEARCH_FEE) | Not implemented | **GAP** |

---

### Module 8: Settings, Search & Reports (SPEC Ch.9)

#### 8.1 Settings GAPs

| SPEC Feature | Current Status | GAP |
|---|---|---|
| Client master data (T_Client with T_ClientAddress, T_ClientContact) | `T_Client` exists with: id, client_no, name_cn, name_en, country, contact_person, phone, email, address, notes | **Partial** — Single address inline; no T_ClientAddress multi-address; no T_ClientContact |
| Applicant master data (T_Applicant with nationality, IsJobInvention, IsLegalEntity, HasGeneralPower) | Not implemented as master data | **GAP** — Applicants are free-text in case JSON |
| Country/Region master data (T_Country) | Not implemented | **GAP** |
| Bio deposit unit master data (T_BioDepositUnit) | Not implemented | **GAP** |
| Task templates configuration UI | Not implemented | **GAP** |
| Fee rate management UI (import/export, effective dates) | `FeeRates.vue` exists for basic fee rate CRUD | **Partial** |
| Document template management (T_Template with template file upload/management) | `T_Template` exists with basic fields, templates served from filesystem | **Partial** |
| Letterhead configuration (T_LetterHead) | Not implemented | **GAP** |
| Global system parameters (T_SystemParam) | `system/api.py` has basic healthz and system info | **GAP**: No configurable system parameters |

#### 8.2 Search GAPs

| SPEC Feature | Current Status | GAP |
|---|---|---|
| Advanced case search (20+ filter dimensions) | Basic keyword search only | **MAJOR GAP** |
| Document search (by DocType, Template, date ranges) | Basic document list | **GAP** |
| Fee inquiry double-table (gov fee payments + case receipts) | Not implemented | **GAP** |
| Deadline search (application fee, exam request timelines) | Not implemented | **GAP** |

#### 8.3 Reports GAPs

| SPEC Feature | Current Status | GAP |
|---|---|---|
| Case statistics (by client/country/agent/type/time) | Dashboard has basic KPI cards | **GAP**: No drill-down reports |
| Fee & revenue statistics | Not implemented | **GAP** |
| Annual fee statistics | Not implemented | **GAP** |
| AR/aging/bad debt/dunning reports | Not implemented | **GAP** |
| Commission reports | Not implemented | **GAP** |

---

### Cross-Cutting / Infrastructure GAPs

| SPEC Feature | Current Status | GAP |
|---|---|---|
| T_Case.ParentCaseID (for PCT_NATIONAL → PCT_INTL linkage) | Not implemented | **GAP** |
| T_PCTNationalPlan (bridge table for PCT national entry planning) | Not implemented | **GAP** |
| Auto-numbering for CaseNo, BillNo, PayNo, etc. (configurable patterns) | Some auto-numbering exists | **Partial** |
| Multi-currency support with exchange rates | Currency field exists on several tables but no exchange rate table or conversion | **GAP** |
| Batch operations (batch filing, batch fee draft generation, batch annuity processing) | Not implemented | **GAP** |
| Document event → cascading actions (status change + task creation + fee draft) | Not implemented | **MAJOR GAP**: This is the core automation engine described in SPEC |

---

## Part 2: FPMS SPEC 2.0 vs MVP1 Scope — What's in SPEC but Explicitly Out of MVP1

### Explicitly Excluded by `00_mvp1_scope.md`

| Feature | SPEC Reference | MVP1 Scope Statement |
|---|---|---|
| PCT international + national plan; national entry automation | Ch.2 (CaseType=PCT_INTL/PCT_NATIONAL), Ch.12 (E2E Scenario C), T_PCTNationalPlan | "PCT international + national plan; national entry automation" — explicitly parked |
| Annual fee/renewal batch, grace rules, complex notifications | Ch.5.8 (T_AnnuityTask), Ch.13 (E2E Scenario D), Ch.5.9 (grace rules) | "Annual fee/renewal batch, grace rules, complex notifications" — explicitly parked |
| Invalidation / litigation full workflows | Ch.2 (CaseType=INVALIDATION/LITIGATION), related E2E scenario E | "Invalidation / litigation full workflows" — explicitly parked |
| Dunning, bad debt, complex finance reports | Ch.6.8 (T_Dunning, T_DunningLine, bad debt marking), Ch.9.4 (reports) | "Dunning, bad debt, complex finance reports" — explicitly parked |
| Commission calculation & settlement | Ch.7 (entire Module 6: T_CommissionRule, T_Commission, T_CommissionSettlement, T_CommissionSettleLine) | "Commission calculation & settlement" — explicitly parked |
| Full "template builder UI" | Ch.9.2.3 (template management) | "Full template builder UI (keep as file-based template upload)" — explicitly parked |
| Full-text search / Elasticsearch | Ch.9.3 (advanced search) | "Full-text search / Elasticsearch" — explicitly parked |

### Features In MVP1 Scope but NOT Fully Implemented

These are features that `00_mvp1_scope.md` says should be in MVP1 but are currently incomplete or missing:

| MVP1 Scope Item | Expected per Scope | Current Status | GAP |
|---|---|---|---|
| **A. Auth & RBAC** | Login/logout, role-based menu, permission enforcement | Fully implemented: JWT auth, 4 roles, 50+ permissions, role-based menu | **OK** |
| **B. Master data — Client** | Client with addresses & contacts | T_Client exists but single-address only, no T_ClientContact | **Partial** — Missing multi-address and contacts |
| **B. Master data — Applicant** | "optional in MVP1; can be free text" | Applicants are JSON in case — free text approach taken | **OK** per scope caveat |
| **B. Master data — Users** | Admin only | User management via admin endpoints | **OK** |
| **C. Case — Create** | Create case (NORMAL only) | Case CRUD works for NORMAL type | **OK** |
| **C. Case — List/search + export** | Case list/search + export | List with basic search + export endpoint | **Partial** — Search very basic |
| **C. Case — Detail edit by Formalities** | Full edit by Formalities role | CaseUpdateFull schema exists but limited fields | **Partial** — Many SPEC fields not in schema |
| **C. Case — Limited edit for Agent** | White list fields only | CaseUpdateLimited schema (title_cn, title_en, inventors) | **OK** |
| **D. Documents — Register** | IN/OUT direction, doc type, dates, attachments | Document CRUD with direction, type, dates, single file | **Partial** — Missing multi-attachment |
| **D. Documents — Link to Case** | Link document to a Case | case_id FK exists on T_Document | **OK** |
| **D. Documents — Template rendering** | Server-side docxtpl → docx download | Template rendering endpoint exists, bill template works | **OK** |
| **E. Task templates** | Minimal set | No T_TaskTemplate table; manual task creation only | **GAP** — Template-driven task creation not implemented |
| **E. Task CRUD** | Assign worker + supervisor | Task CRUD works, assigned_to field | **Partial** — No worker vs supervisor distinction |
| **E. Mark done/cancel/reopen** | Log maintained | Status changes work, but no T_TaskLog audit trail | **GAP** — No task log |
| **E. Today reminder page** | By worker/supervisor | TodayReminders.vue exists | **Partial** — No worker/supervisor split view |
| **F. Fee rates** | Minimal: service fee items as configurable | T_FeeRate with basic CRUD, FeeRates.vue | **OK** for MVP scope |
| **F. Fee draft CRUD** | Manual or from simple doc template trigger | Fee draft and fee item CRUD works | **Partial** — No doc template trigger |
| **G. Generate bill from fee draft** | Single client + currency constraint | Bill generation from drafts endpoint | **OK** |
| **G. Manual bill create** | Optional | Bill CRUD exists | **OK** |
| **G. Payment register** | Payment registration | Payment CRUD works | **OK** |
| **G. Offset payment to bills** | Update balance/status | Offset endpoint works, bill balance/status updated | **OK** |
| **G. Case receipt summary** | By case & fee type | CaseReceiptsSummary component, API endpoint | **OK** |
| **H. System parameters** | Only those needed by MVP1 | Basic system info endpoint | **GAP** — No configurable parameters |
| **H. Templates & letterhead metadata** | Store file path, language, group | T_Template exists with basic metadata | **Partial** — No letterhead (T_LetterHead) |

---

## Summary: Priority GAP Matrix

### P0 — Critical for MVP1 Completeness (in MVP1 scope but missing/incomplete)

| # | GAP | Module | Impact | Estimated Effort |
|---|---|---|---|---|
| P0-1 | Task Template table (T_TaskTemplate) for config-driven deadline creation | Deadline (E) | Core MVP1 requirement per scope "Task templates (minimal set)" | Medium |
| P0-2 | Task audit log (T_TaskLog) | Deadline (E) | MVP1 scope says "log maintained" for mark done/cancel/reopen | Small |
| P0-3 | Multi-address for Client (T_ClientAddress) | Master data (B) | MVP1 scope says "Client with addresses & contacts" | Small |
| P0-4 | Multi-attachment for Documents (T_DocAttachment) | Documents (D) | MVP1 scope says "attachments" (plural) | Small |
| P0-5 | Case detail schema expansion (filing_date, recv_date, app_no, and all NORMAL-type fields from SPEC) | Cases (C) | Many fields in SPEC for NORMAL case type not in model | Medium |

### P1 — Important Enhancements (MVP1 scope partially met)

| # | GAP | Module | Impact |
|---|---|---|---|
| P1-1 | Advanced case search (status, client_id, case_type, date ranges, agent filters) | Cases (C) | MVP1 scope says "Case list/search" |
| P1-2 | Worker vs Supervisor distinction on Tasks | Deadline (E) | MVP1 scope implies both roles |
| P1-3 | CaseReceipt enrichment (FeeCode, YearNo, ReceiptDate, IsArrears) | Billing (G) | Needed for proper case-level financial view |
| P1-4 | Fee rate dimensions (Group, CountryCode, CaseType, PatentCategory) | Fees (F) | Needed for any fee automation |
| P1-5 | Configurable system parameters (T_SystemParam) | Settings (H) | MVP1 scope mentions "system parameters" |

### P2 — Future (Explicitly Excluded from MVP1)

| # | GAP | Module | Scope Decision |
|---|---|---|---|
| P2-1 | PCT workflows (T_PCTNationalPlan, PCT_INTL/PCT_NATIONAL case types) | Cases | Parked |
| P2-2 | Annual fee management (T_AnnuityTask, batch processing, grace rules) | Fees | Parked |
| P2-3 | Invalidation/Litigation workflows | Cases | Parked |
| P2-4 | Dunning & bad debt (T_Dunning, T_DunningLine, IsBadDebt) | Billing | Parked |
| P2-5 | Commission system (T_CommissionRule, T_Commission, settlement batches) | New module | Parked |
| P2-6 | Consulting/Search project management | Cases | Parked |
| P2-7 | Document event automation engine (status change + task + fee draft cascade) | Documents | Parked (most complex single feature) |
| P2-8 | Gov fee payment tracking (T_PayList, T_GovPayment) | Fees | Parked |
| P2-9 | Offset reversal (IsReversed, reverse offset flow) | Billing | Parked |
| P2-10 | Prepayment management | Billing | Parked |
| P2-11 | Advanced reports (case statistics, fee/revenue, AR aging) | Reports | Parked |
| P2-12 | Full-text search / Elasticsearch | Search | Parked |
| P2-13 | Letterhead management (T_LetterHead) | Settings | Parked |
| P2-14 | Project expenses (T_Expense) | Fees | Parked |
| P2-15 | Multi-currency with exchange rate table | Cross-cutting | Parked |
| P2-16 | Batch operations (filing, fee draft gen, annuity processing) | Cross-cutting | Parked |

---

## Appendix: Module-by-Module Table Count Comparison

| SPEC 2.0 Table | In Current Impl? | Notes |
|---|---|---|
| T_User | Yes | Auth module |
| T_Role | Yes | RBAC module |
| T_Permission / T_RolePerm | Yes | RBAC module |
| T_Case | Yes (partial fields) | ~15 of 50+ fields |
| T_CaseApplicant | No (JSON in T_Case) | Should be separate table per SPEC |
| T_CaseInventor | No (JSON in T_Case) | Should be separate table per SPEC |
| T_Priority | No (JSON in T_Case) | Should be separate table per SPEC |
| T_BioDeposit | No | SPEC only |
| T_PCTNationalPlan | No | Future (PCT) |
| T_Client | Yes (partial) | Missing multi-address/contact |
| T_ClientAddress | No | MVP1 gap |
| T_ClientContact | No | MVP1 gap |
| T_Applicant | No | Free text per MVP1 decision |
| T_Country | No | Future |
| T_BioDepositUnit | No | Future |
| T_DocTemplate | No | **Key missing table** |
| T_Document | Yes (partial) | Missing several fields |
| T_DocAttachment | No | MVP1 gap |
| T_DocDispatch | No | Future |
| T_TaskTemplate | No | **MVP1 gap** |
| T_Task | Yes (partial) | Missing time calculation fields |
| T_TaskLog | No | **MVP1 gap** |
| T_FeeRate | Yes (partial) | Missing dimensions |
| T_FeeDraft | Yes (partial) | Missing breakdowns |
| T_FeeItem | Yes (partial) | Missing flags |
| T_PayList | No | Future |
| T_GovPayment | No | Future |
| T_GrantFeeTask | No | Future |
| T_AnnuityTask | No | Future |
| T_CaseReceipt | Yes (partial) | Missing enrichment |
| T_Expense | No | Future |
| T_Bill | Yes (partial) | Missing Direction, breakdowns |
| T_BillItem | Yes (partial) | Missing some FKs |
| T_Payment | Yes | OK |
| T_PaymentLine | No | Future |
| T_Offset | Yes (partial) | Missing reverse support |
| T_Dunning | No | Future |
| T_DunningLine | No | Future |
| T_CommissionRule | No | Future |
| T_Commission | No | Future |
| T_CommissionSettlement | No | Future |
| T_CommissionSettleLine | No | Future |
| T_Template | Yes (partial) | OK for MVP |
| T_LetterHead | No | Future |
| T_SystemParam | No | MVP1 gap |

**Total SPEC tables**: ~40+
**Currently implemented**: ~15 (partial)
**MVP1 Gaps (should be in MVP1)**: ~5 tables (T_TaskTemplate, T_TaskLog, T_DocAttachment, T_ClientAddress, T_SystemParam)
**Future (post-MVP1)**: ~20+ tables
