# FPMS SPEC 2.0 Final Audit Ledger

Date: 2026-04-06  
Truth Refresh: 2026-04-09  
Scope rule: exclude document-generation capability itself

## 1. Audit Method Freeze

This audit uses `docs/FPMS SPEC 2.0.md` as the only requirements baseline.

Judgment is based only on current real product behavior:
- backend API / service / model / state machine
- frontend page / route / user path
- query / list / detail / edit / batch / linkage behavior
- current tests

The following do not count as implementation evidence:
- docs / plans / task files
- placeholder or disabled UI
- representative slice extrapolation
- historic review conclusions

Status rubric:
- `Closed`: real page/API/user path exists and is materially equivalent to the spec item
- `Partially Implemented`: real behavior exists, but only covers part of the required slice
- `Missing`: no real product closure found
- `Excluded by Scope (document-generation only)`: item is fundamentally document generation and was intentionally excluded
- `Needs Reclassification`: current scope cannot honestly classify the item

`document-generation excluded` means:
- template rendering
- docx/pdf output generation
- generated attachment artifacts
- Word/PDF printable document output as the core closure itself

Adjacent but independently verifiable business behavior is still in scope:
- search
- list/detail/edit
- state changes
- batch actions
- billing/task linkage
- visibility/query/report semantics

## 2. Overall Conclusion

The repo now reaches full `SPEC 2.0` coverage except for document-generation-only closures that were intentionally excluded from this ledger.

Current high-confidence residuals:
- None.

No additional item currently requires `Needs Reclassification`.

## 3. Final Audit Ledger

### 3.1 Module 1: Case Maintenance

Status: `Closed`

Evidence:
- [CaseCreate.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/cases/pages/CaseCreate.vue)
- [CaseEdit.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/cases/pages/CaseEdit.vue)
- [CaseDetail.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/cases/pages/CaseDetail.vue)
- [CaseBatchFiling.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/cases/pages/CaseBatchFiling.vue)
- [api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/cases/api.py)
- [service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/cases/service.py)
- [test_case_batch_filing_action.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/tests/test_case_batch_filing_action.py)
- [test_case_report.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/tests/test_case_report.py)

Notes:
- Case CRUD, limited edit, batch filing, search, reports, applicant split, and linked case views all have real product paths.

### 3.2 Module 2: Documents & Correspondence

Status: `Closed`

Closed slices:
- document wizard main flow
- document CRUD/detail
- attachment upload/download
- mailing registration
- dispatch sheet creation/detail
- envelope preview
- document-specific search main query path

Evidence:
- [DocumentWizard.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentWizard.vue)
- [DocumentCreate.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentCreate.vue)
- [DocumentEdit.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentEdit.vue)
- [DocumentDetail.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentDetail.vue)
- [DocumentDispatch.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentDispatch.vue)
- [DocumentEnvelopePrint.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentEnvelopePrint.vue)
- [DocumentList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentList.vue)
- [api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/api.py)
- [service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/service.py)
- [test_document_specific_search_api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/tests/test_document_specific_search_api.py)
- [test_doc_dispatch_handoff.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/tests/test_doc_dispatch_handoff.py)
- [test_doc_dispatch_envelope.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/tests/test_doc_dispatch_envelope.py)

Additional close evidence:
- [documents.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/documents.ts)
- [documents.types.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/documents.types.ts)

Notes:
- `3.8.1` 的 `是否有附件` 查询条件现在已具备真实闭环：
  - backend `GET /api/v1/documents?...&has_attachment=true|false`
  - frontend `中间文件专项查询` 页面附件状态筛选
  - targeted tests 覆盖 `true / false / omitted`

Excluded by scope:
- wizard attachment generation and generated document output
- printable/Word/PDF dispatch artifacts as document-generation closures

### 3.3 Module 3: Deadline & Docket

Status: `Closed`

Closed slices:
- task template maintenance
- task CRUD / action flow
- my tasks / supervisor tasks / today reminders
- special searches for application fee and exam request deadlines

Evidence:
- [TaskList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/tasks/pages/TaskList.vue)
- [TaskDetail.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/tasks/pages/TaskDetail.vue)
- [TaskSpecialSearch.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/tasks/pages/TaskSpecialSearch.vue)
- [TodayReminders.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/tasks/pages/TodayReminders.vue)
- [api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/tasks/api.py)
- [service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/tasks/service.py)
- [test_task_special_search_api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/tests/test_task_special_search_api.py)

Additional close evidence:
- [tasks.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/tasks.ts)
- [test_task_list_export_api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/tests/test_task_list_export_api.py)
- [test_task_list_print_api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/tests/test_task_list_print_api.py)
- [test_task_special_search_exportprint_api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/tests/test_task_special_search_exportprint_api.py)

Notes:
- `4.9 / FR-DL-09` 现在已具备真实列表级导出/打印闭环：
  - `GET /api/v1/tasks/export`
  - `GET /api/v1/tasks/print`
  - `GET /api/v1/tasks/special/search/export`
  - `GET /api/v1/tasks/special/search/print`
  - frontend 我的任务 / 监督任务 / 专项检索结果真实入口

Excluded by scope:
- task sheet document generation itself

### 3.4 Module 4: Fee Management

Status: `Closed`

Closed slices:
- fee rate maintenance
- fee drafts
- grant fee management
- annuity management
- case receipt registration
- expense creation/listing
- expense statistics:
  - per-case totals
  - per-client totals
  - per-department totals
  - worker-level filtering
  - first-round case-level same-currency gross-profit aggregation
- fee reports already implemented in current workspace

Evidence:
- [FeeRates.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/fees/pages/FeeRates.vue)
- [FeeDraftCreate.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/fees/pages/FeeDraftCreate.vue)
- [FeeDraftList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/fees/pages/FeeDraftList.vue)
- [GrantFeeTaskList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue)
- [AnnuityTaskList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/annuity/pages/AnnuityTaskList.vue)
- [ExpenseCreate.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/expenses/pages/ExpenseCreate.vue)
- [ExpenseList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/expenses/pages/ExpenseList.vue)
- [departments/api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/masterdata/departments/api.py)
- [DepartmentList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/masterdata/departments/pages/DepartmentList.vue)
- [api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/fees/api.py)
- [api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/annuity/api.py)
- [api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/grant_fees/api.py)
- [api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/expenses/api.py)
- [service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/expenses/service.py)
- [expenses.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/expenses.ts)
- [expenses.types.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/expenses.types.ts)
- [test_expense_stats_api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/tests/test_expense_stats_api.py)
- [test_department_master_api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/tests/test_department_master_api.py)

Additional close evidence for `5.11` dual-pane fee overview:
- [FeeUnifiedQuery.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/billing/pages/FeeUnifiedQuery.vue)
- [billing.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/billing.ts)
- [billing.types.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/billing.types.ts)
- [api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/billing/api.py)
- [service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/billing/service.py)
- [schemas.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/billing/schemas.py)
- [test_fee_overview_upper_api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/tests/test_fee_overview_upper_api.py)
- [test_fee_overview_lower_api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/tests/test_fee_overview_lower_api.py)

### 3.5 Module 5: Billing, Receivables, Dunning & Bad Debt

Status: `Closed`

Evidence:
- [BillList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/billing/pages/BillList.vue)
- [BillDetail.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/billing/pages/BillDetail.vue)
- [PaymentList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/billing/pages/PaymentList.vue)
- [CaseReceiptList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/billing/pages/CaseReceiptList.vue)
- [OffsetList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/billing/pages/OffsetList.vue)
- [DunningList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/collections/pages/DunningList.vue)
- [BadDebtPanel.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/billing/components/BadDebtPanel.vue)
- [api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/billing/api.py)
- [api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/collections/api.py)
- [test_collections_e2e.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/tests/test_collections_e2e.py)
- [test_billing_bad_debt_reporting.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/tests/test_billing_bad_debt_reporting.py)
- [test_prepayment_reporting_api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/tests/test_prepayment_reporting_api.py)

### 3.6 Module 6: Commission Management

Status: `Closed`

Closed slices:
- commission rule maintenance
- commission generation and update
- multi-agent split
- wait-pay and force-settle semantics
- settlement batch creation
- settlement report query and grouped totals
- settlement report export closure

Evidence:
- [CommissionRuleList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/commission/pages/CommissionRuleList.vue)
- [CommissionList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/commission/pages/CommissionList.vue)
- [CommissionSettlement.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/commission/pages/CommissionSettlement.vue)
- [commission.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/commission.ts)
- [api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/commission/api.py)
- [service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/commission/service.py)
- [export_excel.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/commission/export_excel.py)
- [test_commission_e2e.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/tests/test_commission_e2e.py)
- [test_commission_report.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/tests/test_commission_report.py)

Notes:
- `FR-COM-07` 现在已具备真实导出闭环：
  - backend `GET /api/v1/commission/reports/settlement/export`
  - frontend `导出报表` 用户路径
  - targeted export tests

### 3.7 Module 7: Consulting / Search Projects

Status: `Closed`

Evidence:
- [ConsultingCaseCreate.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/consulting/pages/ConsultingCaseCreate.vue)
- [ConsultingFeeDraftCreate.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/consulting/pages/ConsultingFeeDraftCreate.vue)
- [ConsultingProfitability.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/consulting/pages/ConsultingProfitability.vue)
- [api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/consulting/api.py)
- [service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/consulting/service.py)
- [test_consulting_e2e.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/tests/test_consulting_e2e.py)

### 3.8 Module 8: Settings, Search & Reports Overview

Status: `Closed`

Closed slices:
- master data pages
- document template settings
- task template settings
- system params
- first-round search/report pages across modules

Evidence:
- [MasterDataHome.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/settings/pages/MasterDataHome.vue)
- [DocTemplateList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/system/pages/DocTemplateList.vue)
- [TaskTemplateList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/system/pages/TaskTemplateList.vue)
- [SystemParams.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/system/pages/SystemParams.vue)
- [DepartmentList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/masterdata/departments/pages/DepartmentList.vue)
- [departments/api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/masterdata/departments/api.py)

## 4. Remaining Gap List (excluding document generation)

High-confidence real residuals:
- None.

## 5. Excluded by Scope

Excluded because they are document-generation-only closures:
- generated document outputs from templates
- wizard attachment generation output
- dispatch sheet Word/PDF output
- other printable artifact generation whose core closure is docx/pdf production

## 6. Needs Reclassification

None currently identified.

## 7. Final Judgment

Excluding document-generation-only closures, it is now honest to claim the workspace has reached full `SPEC 2.0` parity.
