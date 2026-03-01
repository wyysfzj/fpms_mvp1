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

      // Cases
      { path: 'cases', name: 'cases', component: () => import('../modules/cases/pages/CaseList.vue') },
      { path: 'cases/new', name: 'case_new', component: () => import('../modules/cases/pages/CaseCreate.vue') },
      { path: 'cases/:id/edit', name: 'case_edit', component: () => import('../modules/cases/pages/CaseEdit.vue') },
      { path: 'cases/:id', name: 'case_detail', component: () => import('../modules/cases/pages/CaseDetail.vue') },

      // Clients
      { path: 'clients', name: 'clients', component: () => import('../modules/clients/pages/ClientList.vue') },
      { path: 'clients/new', name: 'client_new', component: () => import('../modules/clients/pages/ClientForm.vue') },
      { path: 'clients/:id/edit', name: 'client_edit', component: () => import('../modules/clients/pages/ClientForm.vue') },
      // Keep legacy entry to avoid breaking existing navigation.
      { path: 'settings/clients', name: 'settings_clients', component: () => import('../modules/settings/pages/ClientList.vue') },

      // Documents
      { path: 'documents', name: 'documents', component: () => import('../modules/documents/pages/DocumentList.vue') },
      { path: 'documents/new', name: 'document_new', component: () => import('../modules/documents/pages/DocumentCreate.vue') },
      { path: 'documents/:id/edit', name: 'document_edit', component: () => import('../modules/documents/pages/DocumentEdit.vue') },
      { path: 'documents/:id', name: 'document_detail', component: () => import('../modules/documents/pages/DocumentDetail.vue') },

      // Tasks
      { path: 'tasks', name: 'tasks', component: () => import('../modules/tasks/pages/TaskList.vue') },
      { path: 'tasks/new', name: 'task_new', component: () => import('../modules/tasks/pages/TaskCreate.vue') },
      { path: 'tasks/today', name: 'tasks_today', component: () => import('../modules/tasks/pages/TodayReminders.vue') },
      { path: 'tasks/:id', name: 'task_detail', component: () => import('../modules/tasks/pages/TaskDetail.vue') },

      // Annuity
      { path: 'annuity/tasks', name: 'annuity_tasks', component: () => import('../modules/annuity/pages/AnnuityTaskList.vue') },
      { path: 'annuity/pay-lists', name: 'annuity_pay_lists', component: () => import('../modules/annuity/pages/PayList.vue') },
      { path: 'annuity/gov-payments/new', name: 'annuity_gov_payment_new', component: () => import('../modules/annuity/pages/GovPaymentCreate.vue') },

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
      { path: 'billing/payments/new', name: 'payment_new', component: () => import('../modules/billing/pages/PaymentCreate.vue') },

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
