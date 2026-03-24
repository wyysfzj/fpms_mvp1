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
            { key: 'tasks', label: '任务与期限', icon: '📅', route: '/tasks', requiredPerms: [Perms.TASKS_READ] },
            { key: 'annuity_tasks', label: '年费任务', icon: '⏰', route: '/annuity/tasks', requiredPerms: [Perms.TASKS_WRITE] },
            { key: 'dunning', label: '催款管理', icon: '📮', route: '/collections/dunning', requiredPerms: [Perms.BILLING_WRITE] },
            { key: 'consulting_case_new', label: '顾问项目立案', icon: '🧠', route: '/consulting/cases/new', requiredPerms: [Perms.CASES_WRITE] },
        ],
    },
    {
        key: 'finance',
        label: '财务',
        children: [
            { key: 'fees', label: '费用草稿', icon: '💰', route: '/fees/drafts', requiredPerms: [Perms.FEES_READ] },
            { key: 'fee_management_pay_lists', label: '官费清单', icon: '📑', route: '/fee-management/pay-lists', requiredPerms: [Perms.BILLING_WRITE] },
            { key: 'bills', label: '账单管理', icon: '🧾', route: '/billing/bills', requiredPerms: [Perms.BILLING_READ] },
            { key: 'payments', label: '回款与核销', icon: '💳', route: '/billing/payments', requiredPerms: [Perms.BILLING_READ] },
            { key: 'expenses', label: '支出管理', icon: '📉', route: '/expenses', requiredPerms: [Perms.FEES_WRITE] },
            { key: 'commission_rules', label: '提成规则', icon: '🧮', route: '/commission/rules', requiredPerms: [Perms.FEES_WRITE] },
            { key: 'commission_records', label: '提成记录', icon: '📚', route: '/commission', requiredPerms: [Perms.FEES_WRITE] },
            {
                key: 'commission_settlements',
                label: '提成结算',
                icon: '📊',
                route: '/commission/settlements',
                requiredPerms: [Perms.BILLING_WRITE],
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
            { key: 'task_templates', label: '任务模板', icon: '📋', route: '/system/task-templates', requiredPerms: [Perms.SETTINGS_READ] },
            { key: 'doc_templates', label: '文件模板', icon: '📄', route: '/system/doc-templates', requiredPerms: [Perms.SETTINGS_READ] },
        ],
    },
]

/**
 * Flat menu items list (backward-compatible export)
 */
export const MENU_ITEMS: MenuItem[] = MENU_GROUPS.flatMap(g => g.children)
