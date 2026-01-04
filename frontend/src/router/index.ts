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
      { path: 'cases', name: 'cases', component: () => import('../modules/cases/pages/CaseList.vue') },
      { path: 'cases/:id', name: 'case_detail', component: () => import('../modules/cases/pages/CaseDetail.vue') },
      { path: 'documents', name: 'documents', component: () => import('../modules/documents/pages/DocumentList.vue') },
      { path: 'tasks', name: 'tasks', component: () => import('../modules/tasks/pages/TaskList.vue') },
      { path: 'fees/drafts', name: 'fee_drafts', component: () => import('../modules/fees/pages/FeeDraftList.vue') },
      { path: 'billing/bills', name: 'bills', component: () => import('../modules/billing/pages/BillList.vue') },
      { path: 'settings/clients', name: 'clients', component: () => import('../modules/settings/pages/ClientList.vue') },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
