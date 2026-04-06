# FPMS SPEC 2.0 Final Audit Ledger

Date: 2026-04-06  
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

The repo is close to full `SPEC 2.0` coverage, but excluding document generation itself, there are still a small number of real residual gaps.

Current high-confidence residuals:
1. Document specific search is missing `has_attachment` filtering.
2. Task list / task special search lack the list-level export/print closure required by `4.9 / FR-DL-09`.
3. Expense management statistics do not yet reach the `5.10.2` aggregation scope.
4. Commission settlement report exists, but export closure for `FR-COM-07` is not present.

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

Status: `Partially Implemented`

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

Residual gap:
- `3.8.1` requires `是否有附件` search filtering.
- Current implementation has no `has_attachment` filter in frontend or backend query contract.

Gap evidence:
- [DocumentList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentList.vue)
- [api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/api.py)
- [test_document_specific_search_api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/tests/test_document_specific_search_api.py)

Excluded by scope:
- wizard attachment generation and generated document output
- printable/Word/PDF dispatch artifacts as document-generation closures

### 3.3 Module 3: Deadline & Docket

Status: `Partially Implemented`

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

Residual gap:
- `4.9 / FR-DL-09` requires list-level export/print for:
  - my tasks
  - supervisor tasks
  - apply-fee special search results
  - exam-request special search results
- Current implementation only exposes single-task print.

Gap evidence:
- [api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/tasks/api.py)
- [schemas.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/tasks/schemas.py)
- [TaskList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/tasks/pages/TaskList.vue)
- [TaskSpecialSearch.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/tasks/pages/TaskSpecialSearch.vue)

Excluded by scope:
- task sheet document generation itself

### 3.4 Module 4: Fee Management

Status: `Partially Implemented`

Closed slices:
- fee rate maintenance
- fee drafts
- grant fee management
- annuity management
- case receipt registration
- expense creation/listing
- fee reports already implemented in current workspace

Evidence:
- [FeeRates.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/fees/pages/FeeRates.vue)
- [FeeDraftCreate.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/fees/pages/FeeDraftCreate.vue)
- [FeeDraftList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/fees/pages/FeeDraftList.vue)
- [GrantFeeTaskList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue)
- [AnnuityTaskList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/annuity/pages/AnnuityTaskList.vue)
- [ExpenseCreate.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/expenses/pages/ExpenseCreate.vue)
- [ExpenseList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/expenses/pages/ExpenseList.vue)
- [api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/fees/api.py)
- [api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/annuity/api.py)
- [api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/grant_fees/api.py)
- [api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/expenses/api.py)

Residual gap A:
- `5.10.2` requires:
  - per-case expense total
  - per-client / per-department expense totals
  - profitability-ready aggregation
- Current expense stats only cover:
  - total count
  - total amount
  - counts and sums by category

Gap evidence:
- [ExpenseList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/expenses/pages/ExpenseList.vue)
- [service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/expenses/service.py)

Residual gap B:
- `5.11` dual-pane fee overview is now closed in current workspace-state:
  - upper pane `T_GovPayment`
  - lower pane `T_CaseReceipt`
  - truthful upper-pane `fee_type` filter

Close evidence:
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

Status: `Partially Implemented`

Closed slices:
- commission rule maintenance
- commission generation and update
- multi-agent split
- wait-pay and force-settle semantics
- settlement batch creation
- settlement report query and grouped totals

Evidence:
- [CommissionRuleList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/commission/pages/CommissionRuleList.vue)
- [CommissionList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/commission/pages/CommissionList.vue)
- [CommissionSettlement.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/commission/pages/CommissionSettlement.vue)
- [api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/commission/api.py)
- [service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/commission/service.py)
- [test_commission_e2e.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/tests/test_commission_e2e.py)
- [test_commission_report.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/tests/test_commission_report.py)

Residual gap:
- `FR-COM-07` requires report export.
- Current implementation exposes report query/statistics, but no export API or export UI path was found.

Gap evidence:
- [CommissionSettlement.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/commission/pages/CommissionSettlement.vue)
- [api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/commission/api.py)
- [service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/commission/service.py)

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

Status: `Partially Implemented`

Reason:
- The module-level residuals are inherited from the still-open search/report slices above.

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

Residuals carried from other modules:
- document search missing `has_attachment`
- task list / special-search export-print
- expense statistics depth gap
- fee overview structural gap
- commission report export gap

## 4. Remaining Gap List (excluding document generation)

High-confidence real residuals:
1. Document search lacks `是否有附件` filter.
2. Deadline/task list and special-search list export/print closure is missing.
3. Expense statistics do not yet provide per-case / per-client / per-department aggregation.
4. Fee overview does not yet match the spec’s double-pane GovPayment + CaseReceipt structure.
5. Commission settlement report lacks export closure.

## 5. Excluded by Scope

Excluded because they are document-generation-only closures:
- generated document outputs from templates
- wizard attachment generation output
- dispatch sheet Word/PDF output
- other printable artifact generation whose core closure is docx/pdf production

## 6. Needs Reclassification

None currently identified.

## 7. Final Judgment

The workspace is close to full `SPEC 2.0` parity, but excluding document generation itself, it is not yet honest to claim “everything else is fully complete”.

The remaining non-document-generation gaps are concentrated in:
- search semantics
- report/export completeness
- statistics depth
