import * as Perms from './perms'

/**
 * Menu item definition
 */
export interface MenuItem {
    key: string
    label: string
    icon: string
    route: string
    requiredPerms?: string[]
    /** If true, item is pushed to bottom with spacer */
    bottom?: boolean
}

/**
 * Menu group definition (for grouped sidebar rendering)
 */
export interface MenuGroup {
    key: string
    label: string
    children: MenuItem[]
}

/**
 * Grouped navigation menu — V3 layout:
 *   总览 / 业务实体 / 财务 / 系统设置
 */
export const MENU_GROUPS: MenuGroup[] = [
    {
        key: 'top',
        label: '',
        children: [
            { key: 'dashboard', label: '总览', icon: '📊', route: '/dashboard' },
        ],
    },
    {
        key: 'entity',
        label: '业务实体',
        children: [
            { key: 'clients', label: '客户管理', icon: '👥', route: '/clients', requiredPerms: [Perms.CLIENTS_READ] },
            { key: 'cases', label: '案件管理', icon: '📂', route: '/cases', requiredPerms: [Perms.CASES_READ] },
            { key: 'documents', label: '文书管理', icon: '📄', route: '/documents', requiredPerms: [Perms.DOCUMENTS_READ] },
            { key: 'tasks', label: '任务与期限', icon: '📅', route: '/tasks', requiredPerms: [Perms.TASKS_READ] },
            {
                key: 'task_special_search',
                label: '专项期限检索',
                icon: '🔎',
                route: '/tasks/special-search',
                requiredPerms: [Perms.TASKS_READ],
            },
            { key: 'annuity_tasks', label: '年费任务', icon: '⏰', route: '/annuity/tasks', requiredPerms: [Perms.TASKS_WRITE] },
            { key: 'dunning', label: '催款管理', icon: '📮', route: '/collections/dunning', requiredPerms: [Perms.BILLING_WRITE] },
            { key: 'consulting_case_new', label: '顾问项目立案', icon: '🧠', route: '/consulting/cases/new', requiredPerms: [Perms.CASES_WRITE] },
        ],
    },
    {
        key: 'reports',
        label: '统计报表',
        children: [
            {
                key: 'reports_home',
                label: '报表总览',
                icon: '📊',
                route: '/reports',
                requiredPerms: [
                    Perms.CASES_READ,
                    Perms.BILLING_READ,
                    Perms.FEES_READ,
                    Perms.PAY_LIST_READ,
                    Perms.COMMISSION_REPORT_READ,
                ],
            },
            { key: 'case_report', label: '案件统计', icon: '📈', route: '/reports/cases', requiredPerms: [Perms.CASES_READ] },
            { key: 'annuity_report', label: '年费任务统计', icon: '⏱️', route: '/reports/annuity-tasks', requiredPerms: [Perms.TASKS_WRITE] },
            { key: 'bill_report', label: '账单统计', icon: '🧾', route: '/reports/bills', requiredPerms: [Perms.BILLING_READ] },
            { key: 'report_payments', label: '预收款管理报表', icon: '💳', route: '/billing/payments', requiredPerms: [Perms.BILLING_READ] },
            { key: 'fee_draft_report', label: '费用草稿统计', icon: '💰', route: '/reports/fee-drafts', requiredPerms: [Perms.FEES_READ] },
            { key: 'expense_report', label: '支出统计', icon: '📉', route: '/reports/expenses', requiredPerms: [Perms.FEES_WRITE] },
            {
                key: 'report_fee_unified_query',
                label: '费用情况一览',
                icon: '🔍',
                route: '/billing/fee-unified-query',
                requiredPerms: [Perms.PAY_LIST_READ, 'CaseReceipt.Read'],
            },
            {
                key: 'report_commission_settlements',
                label: '提成结算报表',
                icon: '🧮',
                route: '/commission/settlements',
                requiredPerms: [Perms.COMMISSION_SETTLEMENT_CREATE, Perms.COMMISSION_REPORT_READ],
            },
            {
                key: 'report_consulting_profitability',
                label: '顾问收益视图',
                icon: '📉',
                route: '/consulting/profitability',
                requiredPerms: [Perms.BILLING_WRITE, Perms.FEES_WRITE],
            },
        ],
    },
    {
        key: 'finance',
        label: '财务',
        children: [
            { key: 'fees', label: '费用草稿', icon: '💰', route: '/fees/drafts', requiredPerms: [Perms.FEES_READ] },
            { key: 'fee_rates', label: '费率管理', icon: '💱', route: '/fees/rates', requiredPerms: [Perms.FEE_RATE_READ] },
            { key: 'grant_fee_tasks', label: '授权费任务', icon: '🧾', route: '/grant-fee/tasks', requiredPerms: ['GrantFeeTask.Read'] },
            { key: 'fee_management_pay_lists', label: '官费清单', icon: '📑', route: '/fee-management/pay-lists', requiredPerms: [Perms.PAY_LIST_READ] },
            { key: 'bills', label: '账单管理', icon: '🧾', route: '/billing/bills', requiredPerms: [Perms.BILLING_READ] },
            { key: 'payments', label: '回款与核销', icon: '💳', route: '/billing/payments', requiredPerms: [Perms.BILLING_READ] },
            {
                key: 'fee_unified_query',
                label: '费用情况一览',
                icon: '🔍',
                route: '/billing/fee-unified-query',
                requiredPerms: ['PayList.Read', 'CaseReceipt.Read'],
            },
            { key: 'offsets', label: '冲销管理', icon: '🔄', route: '/billing/offsets', requiredPerms: [Perms.BILLING_READ] },
            { key: 'case_receipts', label: '个案收款登记', icon: '📋', route: '/billing/case-receipts', requiredPerms: [Perms.BILLING_READ] },
            { key: 'expenses', label: '支出管理', icon: '📉', route: '/expenses', requiredPerms: [Perms.FEES_WRITE] },
            { key: 'commission_rules', label: '提成规则', icon: '🧮', route: '/commission/rules', requiredPerms: [Perms.COMMISSION_RULE_READ] },
            { key: 'commission_records', label: '提成记录', icon: '📚', route: '/commission', requiredPerms: [Perms.COMMISSION_READ] },
            {
                key: 'commission_settlements',
                label: '提成结算',
                icon: '📊',
                route: '/commission/settlements',
                requiredPerms: [Perms.COMMISSION_SETTLEMENT_CREATE, Perms.COMMISSION_REPORT_READ],
            },
            {
                key: 'consulting_profitability',
                label: '顾问收益视图',
                icon: '📈',
                route: '/consulting/profitability',
                requiredPerms: [Perms.BILLING_WRITE, Perms.FEES_WRITE],
            },
        ],
    },
    {
        key: 'settings',
        label: '系统设置',
        children: [
            { key: 'settings', label: '系统配置', icon: '⚙️', route: '/system/params', requiredPerms: [Perms.SETTINGS_READ] },
            {
                key: 'settings_masterdata_home',
                label: '主数据入口',
                icon: '🗂️',
                route: '/settings/masterdata',
                requiredPerms: [Perms.APPLICANT_READ, Perms.COUNTRY_READ, Perms.DEPARTMENT_READ],
            },
            {
                key: 'settings_masterdata_departments',
                label: '部门主数据',
                icon: '🏢',
                route: '/settings/masterdata/departments',
                requiredPerms: [Perms.DEPARTMENT_READ],
            },
            { key: 'task_templates', label: '任务模板', icon: '📋', route: '/system/task-templates', requiredPerms: [Perms.SETTINGS_READ] },
            { key: 'doc_templates', label: '文件模板', icon: '📄', route: '/system/doc-templates', requiredPerms: [Perms.SETTINGS_READ] },
            { key: 'system_templates', label: '模板文件源', icon: '🧾', route: '/system/templates', requiredPerms: [Perms.TEMPLATE_READ] },
            { key: 'letterheads', label: '信纸抬头', icon: '🏷️', route: '/system/letterheads', requiredPerms: [Perms.LETTERHEAD_READ] },
        ],
    },
]

/**
 * Flat menu items list (backward-compatible export)
 */
export const MENU_ITEMS: MenuItem[] = MENU_GROUPS.flatMap(g => g.children)
