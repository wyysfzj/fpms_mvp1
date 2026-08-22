import { createRouter, createWebHistory } from 'vue-router'
import Login from '../modules/auth/pages/Login.vue'
import MainLayout from '../layout/MainLayout.vue'

const routes = [
  { path: '/login', name: 'login', component: Login },
  {
    path: '/',
    component: MainLayout,
    children: [
      { path: 'dashboard', name: 'dashboard', component: () => import('../modules/dashboard/pages/Dashboard.vue') },
      { path: 'demo/inputs', name: 'demo_inputs', component: () => import('../modules/demo/pages/DemoInputs.vue') },
      { path: 'demo/abc', name: 'demo_abc', component: () => import('../modules/demo/pages/DemoAbc.vue') },

      // Cases
      { path: 'cases', name: 'cases', component: () => import('../modules/cases/pages/CaseList.vue') },
      { path: 'cases/batch-filing', name: 'case_batch_filing', component: () => import('../modules/cases/pages/CaseBatchFiling.vue') },
      { path: 'cases/new', name: 'case_new', component: () => import('../modules/cases/pages/CaseCreate.vue') },
      { path: 'cases/no/:caseNo/edit', name: 'case_edit_by_no', component: () => import('../modules/cases/pages/CaseEdit.vue') },
      { path: 'cases/:id/edit', name: 'case_edit', component: () => import('../modules/cases/pages/CaseEdit.vue') },
      { path: 'cases/no/:caseNo', name: 'case_detail_by_no', component: () => import('../modules/cases/pages/CaseDetail.vue') },
      { path: 'cases/:id', name: 'case_detail', component: () => import('../modules/cases/pages/CaseDetail.vue') },

      // Reports
      { path: 'reports', name: 'reports_home', component: () => import('../modules/reports/pages/ReportHome.vue') },
      { path: 'reports/cases', name: 'case_report', component: () => import('../modules/reports/pages/CaseReport.vue') },
      { path: 'reports/bills', name: 'bill_report', component: () => import('../modules/reports/pages/BillReport.vue') },
      { path: 'reports/fee-drafts', name: 'fee_draft_report', component: () => import('../modules/reports/pages/FeeDraftReport.vue') },
      { path: 'reports/annuity-tasks', name: 'annuity_report', component: () => import('../modules/reports/pages/AnnuityReport.vue') },
      { path: 'reports/expenses', name: 'expense_report', component: () => import('../modules/reports/pages/ExpenseReport.vue') },

      // Clients
      { path: 'clients', name: 'clients', component: () => import('../modules/clients/pages/ClientList.vue') },
      { path: 'clients/new', name: 'client_new', component: () => import('../modules/clients/pages/ClientForm.vue') },
      { path: 'clients/:id/edit', name: 'client_edit', component: () => import('../modules/clients/pages/ClientForm.vue') },
      { path: 'clients/:id', name: 'client_detail', component: () => import('../modules/clients/pages/ClientDetail.vue') },
      // Keep legacy entry to avoid breaking existing navigation.
      { path: 'settings/clients', name: 'settings_clients', component: () => import('../modules/settings/pages/ClientList.vue') },
      { path: 'settings/masterdata', name: 'settings_masterdata_home', component: () => import('../modules/settings/pages/MasterDataHome.vue') },
      {
        path: 'settings/masterdata/applicants',
        alias: '/settings/applicants',
        name: 'settings_masterdata_applicants',
        component: () => import('../modules/settings/pages/ApplicantList.vue'),
      },
      {
        path: 'settings/masterdata/countries',
        name: 'settings_masterdata_countries',
        component: () => import('../modules/settings/pages/CountryList.vue'),
      },
      {
        path: 'settings/masterdata/departments',
        name: 'settings_masterdata_departments',
        component: () => import('../modules/masterdata/departments/pages/DepartmentList.vue'),
      },

      // Documents
      { path: 'documents', name: 'documents', component: () => import('../modules/documents/pages/DocumentList.vue') },
      { path: 'documents/new', name: 'document_new', component: () => import('../modules/documents/pages/DocumentCreate.vue') },
      { path: 'documents/wizard', name: 'document_wizard', component: () => import('../modules/documents/pages/DocumentWizard.vue') },
      { path: 'documents/dispatch', name: 'document_dispatch', component: () => import('../modules/documents/pages/DocumentDispatch.vue') },
      { path: 'documents/:id/envelope', name: 'document_envelope_print', component: () => import('../modules/documents/pages/DocumentEnvelopePrint.vue') },
      { path: 'documents/:id/edit', name: 'document_edit', component: () => import('../modules/documents/pages/DocumentEdit.vue') },
      { path: 'documents/:id', name: 'document_detail', component: () => import('../modules/documents/pages/DocumentDetail.vue') },

      // Official Workflows
      {
        path: 'official-workflows/filing-preparation',
        name: 'official_work_filing_preparation',
        component: () => import('../modules/cases/pages/FilingPreparation.vue'),
      },
      {
        path: 'official-workflows/oa-reply',
        name: 'official_work_oa_reply',
        component: () => import('../modules/documents/pages/OAReplyPackage.vue'),
      },
      {
        path: 'official-workflows/fee-linkage',
        name: 'official_work_fee_linkage',
        component: () => import('../modules/officialWorkflows/pages/OfficialWorkflowPlaceholder.vue'),
        props: { title: '费用联动核对', description: '请选择具体费用工作包。' },
      },
      {
        path: 'official-workflows/receipt-archive',
        name: 'official_work_receipt_archive',
        component: () => import('../modules/officialWorkflows/pages/OfficialWorkflowPlaceholder.vue'),
        props: { title: '回执归档', description: '请选择具体回执归档工作包。' },
      },
      {
        path: 'official-workflows/letter-handoff',
        name: 'official_document_letter_handoff',
        component: () => import('../modules/officialWorkflows/pages/OfficialWorkflowPlaceholder.vue'),
        props: { title: '信函交接', description: '请选择具体信函交接工作包。' },
      },

      // Tasks
      { path: 'tasks', name: 'tasks', component: () => import('../modules/tasks/pages/TaskList.vue') },
      { path: 'tasks/new', name: 'task_new', component: () => import('../modules/tasks/pages/TaskCreate.vue') },
      { path: 'tasks/today', name: 'tasks_today', component: () => import('../modules/tasks/pages/TodayReminders.vue') },
      {
        path: 'tasks/special-search',
        name: 'task_special_search',
        component: () => import('../modules/tasks/pages/TaskSpecialSearch.vue'),
      },
      { path: 'tasks/:id', name: 'task_detail', component: () => import('../modules/tasks/pages/TaskDetail.vue') },

      // Annuity
      { path: 'annuity/tasks', name: 'annuity_tasks', component: () => import('../modules/annuity/pages/AnnuityTaskList.vue') },
      {
        path: 'annuity/pay-lists',
        alias: '/fee-management/pay-lists',
        name: 'annuity_pay_lists',
        component: () => import('../modules/annuity/pages/PayList.vue'),
      },
      {
        path: 'annuity/pay-lists/:id',
        alias: '/fee-management/pay-lists/:id',
        name: 'annuity_pay_list_detail',
        component: () => import('../modules/annuity/pages/PayListDetail.vue'),
      },
      {
        path: 'annuity/gov-payments/new',
        alias: '/fee-management/gov-payments/new',
        name: 'annuity_gov_payment_new',
        component: () => import('../modules/annuity/pages/GovPaymentCreate.vue'),
      },

      // Grant Fee
      {
        path: 'grant-fee/tasks',
        name: 'grant_fee_tasks',
        component: () => import('../modules/grantFees/pages/GrantFeeTaskList.vue'),
      },

      // Fees
      { path: 'fees/drafts', name: 'fee_drafts', component: () => import('../modules/fees/pages/FeeDraftList.vue') },
      { path: 'fees/drafts/new', name: 'fee_draft_new', component: () => import('../modules/fees/pages/FeeDraftCreate.vue') },
      { path: 'fees/drafts/:id', name: 'fee_draft_detail', component: () => import('../modules/fees/pages/FeeDraftDetail.vue') },
      { path: 'fees/rates', name: 'fee_rates', component: () => import('../modules/fees/pages/FeeRates.vue') },

      // Billing / Payments
      { path: 'billing/bills', name: 'bills', component: () => import('../modules/billing/pages/BillList.vue') },
      { path: 'billing/bills/new', name: 'bill_new', component: () => import('../modules/billing/pages/BillCreate.vue') },
      { path: 'billing/bills/:id', name: 'bill_detail', component: () => import('../modules/billing/pages/BillDetail.vue') },
      { path: 'billing/payments', name: 'payments', component: () => import('../modules/billing/pages/PaymentList.vue') },
      { path: 'billing/fee-unified-query', name: 'fee_unified_query', component: () => import('../modules/billing/pages/FeeUnifiedQuery.vue') },
      { path: 'billing/offsets', name: 'offsets', component: () => import('../modules/billing/pages/OffsetList.vue') },
      { path: 'billing/payments/new', name: 'payment_new', component: () => import('../modules/billing/pages/PaymentCreate.vue') },
      { path: 'billing/case-receipts', name: 'case_receipts', component: () => import('../modules/billing/pages/CaseReceiptList.vue') },

      // Collections
      { path: 'collections/dunning', name: 'dunning_list', component: () => import('../modules/collections/pages/DunningList.vue') },
      { path: 'collections/dunning/new', name: 'dunning_new', component: () => import('../modules/collections/pages/DunningCreate.vue') },
      { path: 'collections/dunning/:id', name: 'dunning_detail', component: () => import('../modules/collections/pages/DunningDetail.vue') },

      // Commission
      { path: 'commission/rules', name: 'commission_rules', component: () => import('../modules/commission/pages/CommissionRuleList.vue') },
      {
        path: 'commission',
        name: 'commission_records',
        alias: '/commission/records',
        component: () => import('../modules/commission/pages/CommissionList.vue'),
      },
      { path: 'commission/settlements', name: 'commission_settlements', component: () => import('../modules/commission/pages/CommissionSettlement.vue') },

      // Consulting
      { path: 'consulting/cases/new', name: 'consulting_case_new', component: () => import('../modules/consulting/pages/ConsultingCaseCreate.vue') },
      { path: 'consulting/fee-drafts/new', name: 'consulting_fee_draft_new', component: () => import('../modules/consulting/pages/ConsultingFeeDraftCreate.vue') },
      { path: 'consulting/profitability', name: 'consulting_profitability', component: () => import('../modules/consulting/pages/ConsultingProfitability.vue') },

      // Expenses
      { path: 'expenses', name: 'expenses', component: () => import('../modules/expenses/pages/ExpenseList.vue') },
      { path: 'expenses/new', name: 'expense_new', component: () => import('../modules/expenses/pages/ExpenseCreate.vue') },

      // System
      { path: 'system/params', name: 'system_params', component: () => import('../modules/system/pages/SystemParams.vue') },
      { path: 'system/templates', name: 'system_templates', component: () => import('../modules/system/pages/TemplateList.vue') },
      { path: 'system/task-templates', name: 'system_task_templates', component: () => import('../modules/system/pages/TaskTemplateList.vue') },
      { path: 'system/doc-templates', name: 'system_doc_templates', component: () => import('../modules/system/pages/DocTemplateList.vue') },
      { path: 'system/letterheads', name: 'system_letterheads', component: () => import('../modules/system/pages/LetterheadList.vue') },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
