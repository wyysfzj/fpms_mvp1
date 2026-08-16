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
    shortLabel?: string
    activePatterns?: string[]
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

export type NavMode = 'work' | 'module'

export interface ProductMenuGroup extends MenuGroup {
    mode: NavMode
    description?: string
    pinnedBottom?: boolean
}

const dashboardItem: MenuItem = {
    key: 'dashboard',
    label: '工作台',
    shortLabel: '台',
    icon: '📊',
    route: '/dashboard',
}

const demoAbcItem: MenuItem = {
    key: 'demo_abc',
    label: 'ABC 演示台',
    shortLabel: '演',
    icon: '▶️',
    route: '/demo/abc',
}

const todayRemindersItem: MenuItem = {
    key: 'tasks_today',
    label: '今日提醒',
    shortLabel: '今',
    icon: '🔔',
    route: '/tasks/today',
    requiredPerms: [Perms.TASKS_READ],
}

const tasksItem: MenuItem = {
    key: 'tasks',
    label: '任务与期限',
    shortLabel: '任',
    icon: '📅',
    route: '/tasks',
    activePatterns: ['/tasks/*'],
    requiredPerms: [Perms.TASKS_READ],
}

const taskSpecialSearchItem: MenuItem = {
    key: 'task_special_search',
    label: '专项期限检索',
    shortLabel: '检',
    icon: '🔎',
    route: '/tasks/special-search',
    requiredPerms: [Perms.TASKS_READ],
}

const clientsItem: MenuItem = {
    key: 'clients',
    label: '客户管理',
    shortLabel: '客',
    icon: '👥',
    route: '/clients',
    activePatterns: ['/clients/*'],
    requiredPerms: [Perms.CLIENTS_READ],
}

const casesItem: MenuItem = {
    key: 'cases',
    label: '案件列表',
    shortLabel: '案',
    icon: '📂',
    route: '/cases',
    activePatterns: ['/cases/*'],
    requiredPerms: [Perms.CASES_READ],
}

const caseNewItem: MenuItem = {
    key: 'case_new',
    label: '新建案件',
    shortLabel: '新',
    icon: '➕',
    route: '/cases/new',
    requiredPerms: [Perms.CASES_READ, Perms.CASES_WRITE],
}

const caseBatchFilingItem: MenuItem = {
    key: 'case_batch_filing_menu',
    label: '案件批量递交',
    shortLabel: '递',
    icon: '📤',
    route: '/cases/batch-filing',
    requiredPerms: [Perms.CASES_READ, Perms.CASES_WRITE],
}

const officialFilingPreparationItem: MenuItem = {
    key: 'official_work_filing_preparation',
    label: '新申请递交准备',
    shortLabel: '准',
    icon: '🧭',
    route: '/official-workflows/filing-preparation',
    requiredPerms: [Perms.CASES_READ, Perms.DOCUMENTS_READ],
}

const officialOAReplyItem: MenuItem = {
    key: 'official_work_oa_reply',
    label: 'OA答复工作包',
    shortLabel: 'OA',
    icon: '📝',
    route: '/official-workflows/oa-reply',
    requiredPerms: [Perms.DOCUMENTS_READ],
}

const officialFeeLinkageItem: MenuItem = {
    key: 'official_work_fee_linkage',
    label: '费用联动核对',
    shortLabel: '核',
    icon: '🔗',
    route: '/official-workflows/fee-linkage',
    requiredPerms: [Perms.FEES_READ, Perms.PAY_LIST_READ],
}

const officialReceiptArchiveItem: MenuItem = {
    key: 'official_work_receipt_archive',
    label: '回执归档',
    shortLabel: '执',
    icon: '🗄️',
    route: '/official-workflows/receipt-archive',
    requiredPerms: [Perms.DOCUMENTS_READ],
}

const officialLetterHandoffItem: MenuItem = {
    key: 'official_document_letter_handoff',
    label: '信函交接',
    shortLabel: '函',
    icon: '✉️',
    route: '/official-workflows/letter-handoff',
    requiredPerms: [Perms.DOCUMENTS_READ],
}

const documentsItem: MenuItem = {
    key: 'documents',
    label: '往来文件',
    shortLabel: '文',
    icon: '📄',
    route: '/documents',
    activePatterns: ['/documents/*'],
    requiredPerms: [Perms.DOCUMENTS_READ],
}

const feesItem: MenuItem = {
    key: 'fees',
    label: '费用草稿',
    shortLabel: '费',
    icon: '💰',
    route: '/fees/drafts',
    activePatterns: ['/fees/drafts/*'],
    requiredPerms: [Perms.FEES_READ],
}

const feeRatesItem: MenuItem = {
    key: 'fee_rates',
    label: '费率管理',
    shortLabel: '率',
    icon: '💱',
    route: '/fees/rates',
    requiredPerms: [Perms.FEE_RATE_READ],
}

const grantFeeTasksItem: MenuItem = {
    key: 'grant_fee_tasks',
    label: '授权费任务',
    shortLabel: '授',
    icon: '🧾',
    route: '/grant-fee/tasks',
    requiredPerms: ['GrantFeeTask.Read'],
}

const payListsItem: MenuItem = {
    key: 'fee_management_pay_lists',
    label: '官费清单',
    shortLabel: '清',
    icon: '📑',
    route: '/fee-management/pay-lists',
    activePatterns: ['/annuity/pay-lists', '/annuity/pay-lists/*', '/fee-management/pay-lists/*'],
    requiredPerms: [Perms.PAY_LIST_READ],
}

const billsItem: MenuItem = {
    key: 'bills',
    label: '账单管理',
    shortLabel: '账',
    icon: '🧾',
    route: '/billing/bills',
    activePatterns: ['/billing/bills/*'],
    requiredPerms: [Perms.BILLING_READ],
}

const paymentsItem: MenuItem = {
    key: 'payments',
    label: '回款与核销',
    shortLabel: '款',
    icon: '💳',
    route: '/billing/payments',
    activePatterns: ['/billing/payments/*'],
    requiredPerms: [Perms.BILLING_READ],
}

const feeUnifiedQueryItem: MenuItem = {
    key: 'fee_unified_query',
    label: '费用情况一览',
    shortLabel: '览',
    icon: '🔍',
    route: '/billing/fee-unified-query',
    requiredPerms: ['PayList.Read', 'CaseReceipt.Read'],
}

const offsetsItem: MenuItem = {
    key: 'offsets',
    label: '冲销管理',
    shortLabel: '冲',
    icon: '🔄',
    route: '/billing/offsets',
    requiredPerms: [Perms.BILLING_READ],
}

const caseReceiptsItem: MenuItem = {
    key: 'case_receipts',
    label: '个案收款登记',
    shortLabel: '收',
    icon: '📋',
    route: '/billing/case-receipts',
    requiredPerms: [Perms.BILLING_READ],
}

const expensesItem: MenuItem = {
    key: 'expenses',
    label: '支出管理',
    shortLabel: '支',
    icon: '📉',
    route: '/expenses',
    activePatterns: ['/expenses/*'],
    requiredPerms: [Perms.FEES_WRITE],
}

const annuityTasksItem: MenuItem = {
    key: 'annuity_tasks',
    label: '年费任务',
    shortLabel: '年',
    icon: '⏰',
    route: '/annuity/tasks',
    requiredPerms: [Perms.TASKS_WRITE],
}

const dunningItem: MenuItem = {
    key: 'dunning',
    label: '催款管理',
    shortLabel: '催',
    icon: '📮',
    route: '/collections/dunning',
    activePatterns: ['/collections/dunning/*'],
    requiredPerms: [Perms.BILLING_WRITE],
}

const commissionRulesItem: MenuItem = {
    key: 'commission_rules',
    label: '提成规则',
    shortLabel: '规',
    icon: '🧮',
    route: '/commission/rules',
    requiredPerms: [Perms.COMMISSION_RULE_READ],
}

const commissionRecordsItem: MenuItem = {
    key: 'commission_records',
    label: '提成记录',
    shortLabel: '提',
    icon: '📚',
    route: '/commission',
    requiredPerms: [Perms.COMMISSION_READ],
}

const commissionSettlementsItem: MenuItem = {
    key: 'commission_settlements',
    label: '提成结算',
    shortLabel: '结',
    icon: '📊',
    route: '/commission/settlements',
    requiredPerms: [Perms.COMMISSION_SETTLEMENT_CREATE, Perms.COMMISSION_REPORT_READ],
}

const consultingCaseNewItem: MenuItem = {
    key: 'consulting_case_new',
    label: '顾问项目立案',
    shortLabel: '顾',
    icon: '🧠',
    route: '/consulting/cases/new',
    requiredPerms: [Perms.CASES_WRITE],
}

const consultingProfitabilityItem: MenuItem = {
    key: 'consulting_profitability',
    label: '顾问收益视图',
    shortLabel: '益',
    icon: '📈',
    route: '/consulting/profitability',
    requiredPerms: [Perms.BILLING_WRITE, Perms.FEES_WRITE],
}

const reportsHomeItem: MenuItem = {
    key: 'reports_home',
    label: '报表总览',
    shortLabel: '报',
    icon: '📊',
    route: '/reports',
    requiredPerms: [
        Perms.CASES_READ,
        Perms.BILLING_READ,
        Perms.FEES_READ,
        Perms.PAY_LIST_READ,
        Perms.COMMISSION_REPORT_READ,
    ],
}

const caseReportItem: MenuItem = {
    key: 'case_report',
    label: '案件统计',
    shortLabel: '案',
    icon: '📈',
    route: '/reports/cases',
    requiredPerms: [Perms.CASES_READ],
}

const annuityReportItem: MenuItem = {
    key: 'annuity_report',
    label: '年费任务统计',
    shortLabel: '年',
    icon: '⏱️',
    route: '/reports/annuity-tasks',
    requiredPerms: [Perms.TASKS_WRITE],
}

const billReportItem: MenuItem = {
    key: 'bill_report',
    label: '账单统计',
    shortLabel: '账',
    icon: '🧾',
    route: '/reports/bills',
    requiredPerms: [Perms.BILLING_READ],
}

const feeDraftReportItem: MenuItem = {
    key: 'fee_draft_report',
    label: '费用草稿统计',
    shortLabel: '费',
    icon: '💰',
    route: '/reports/fee-drafts',
    requiredPerms: [Perms.FEES_READ],
}

const expenseReportItem: MenuItem = {
    key: 'expense_report',
    label: '支出统计',
    shortLabel: '支',
    icon: '📉',
    route: '/reports/expenses',
    requiredPerms: [Perms.FEES_WRITE],
}

const reportPaymentsItem: MenuItem = {
    key: 'report_payments',
    label: '预收款管理报表',
    shortLabel: '款',
    icon: '💳',
    route: '/billing/payments',
    requiredPerms: [Perms.BILLING_READ],
}

const reportFeeUnifiedQueryItem: MenuItem = {
    key: 'report_fee_unified_query',
    label: '费用情况一览',
    shortLabel: '览',
    icon: '🔍',
    route: '/billing/fee-unified-query',
    requiredPerms: [Perms.PAY_LIST_READ, 'CaseReceipt.Read'],
}

const reportCommissionSettlementsItem: MenuItem = {
    key: 'report_commission_settlements',
    label: '提成结算报表',
    shortLabel: '结',
    icon: '🧮',
    route: '/commission/settlements',
    requiredPerms: [Perms.COMMISSION_SETTLEMENT_CREATE, Perms.COMMISSION_REPORT_READ],
}

const reportConsultingProfitabilityItem: MenuItem = {
    key: 'report_consulting_profitability',
    label: '顾问收益视图',
    shortLabel: '益',
    icon: '📉',
    route: '/consulting/profitability',
    requiredPerms: [Perms.BILLING_WRITE, Perms.FEES_WRITE],
}

const settingsItem: MenuItem = {
    key: 'settings',
    label: '系统配置',
    shortLabel: '配',
    icon: '⚙️',
    route: '/system/params',
    requiredPerms: [Perms.SETTINGS_READ],
}

const settingsMasterdataHomeItem: MenuItem = {
    key: 'settings_masterdata_home',
    label: '主数据入口',
    shortLabel: '数',
    icon: '🗂️',
    route: '/settings/masterdata',
    requiredPerms: [Perms.APPLICANT_READ, Perms.COUNTRY_READ, Perms.DEPARTMENT_READ],
}

const settingsMasterdataDepartmentsItem: MenuItem = {
    key: 'settings_masterdata_departments',
    label: '部门主数据',
    shortLabel: '部',
    icon: '🏢',
    route: '/settings/masterdata/departments',
    requiredPerms: [Perms.DEPARTMENT_READ],
}

const taskTemplatesItem: MenuItem = {
    key: 'task_templates',
    label: '任务模板',
    shortLabel: '任',
    icon: '📋',
    route: '/system/task-templates',
    requiredPerms: [Perms.SETTINGS_READ],
}

const docTemplatesItem: MenuItem = {
    key: 'doc_templates',
    label: '文件模板',
    shortLabel: '文',
    icon: '📄',
    route: '/system/doc-templates',
    requiredPerms: [Perms.SETTINGS_READ],
}

const systemTemplatesItem: MenuItem = {
    key: 'system_templates',
    label: '模板文件源',
    shortLabel: '源',
    icon: '🧾',
    route: '/system/templates',
    requiredPerms: [Perms.TEMPLATE_READ],
}

const letterheadsItem: MenuItem = {
    key: 'letterheads',
    label: '信纸抬头',
    shortLabel: '信',
    icon: '🏷️',
    route: '/system/letterheads',
    requiredPerms: [Perms.LETTERHEAD_READ],
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
            {
                key: 'case_batch_filing_menu',
                label: '案件批量递交',
                icon: '📤',
                route: '/cases/batch-filing',
                requiredPerms: [Perms.CASES_READ, Perms.CASES_WRITE],
            },
            {
                key: 'official_work_filing_preparation',
                label: '新申请递交准备',
                icon: '🧭',
                route: '/official-workflows/filing-preparation',
                requiredPerms: [Perms.CASES_READ, Perms.DOCUMENTS_READ],
            },
            {
                key: 'official_work_oa_reply',
                label: 'OA答复工作包',
                icon: '📝',
                route: '/official-workflows/oa-reply',
                requiredPerms: [Perms.DOCUMENTS_READ],
            },
            {
                key: 'official_work_receipt_archive',
                label: '回执归档',
                icon: '🗄️',
                route: '/official-workflows/receipt-archive',
                requiredPerms: [Perms.DOCUMENTS_READ],
            },
            {
                key: 'grant_fee_tasks_case_lifecycle',
                label: '授权费任务',
                icon: '🧾',
                route: '/grant-fee/tasks',
                requiredPerms: ['GrantFeeTask.Read'],
            },
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
            {
                key: 'official_work_fee_linkage',
                label: '费用联动核对',
                icon: '🔗',
                route: '/official-workflows/fee-linkage',
                requiredPerms: [Perms.FEES_READ, Perms.PAY_LIST_READ],
            },
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
            {
                key: 'official_document_letter_handoff',
                label: '信函交接',
                icon: '✉️',
                route: '/official-workflows/letter-handoff',
                requiredPerms: [Perms.DOCUMENTS_READ],
            },
        ],
    },
]

/**
 * Flat menu items list (backward-compatible export)
 */
export const MENU_ITEMS: MenuItem[] = MENU_GROUPS.flatMap(g => g.children)

export const PRODUCT_NAV_GROUPS: ProductMenuGroup[] = [
    {
        mode: 'work',
        key: 'my-work',
        label: '我的工作',
        description: '日常入口',
        children: [demoAbcItem, dashboardItem, todayRemindersItem, tasksItem, taskSpecialSearchItem],
    },
    {
        mode: 'work',
        key: 'case-lifecycle',
        label: '案件生命周期',
        description: '主流程',
        children: [casesItem, caseNewItem, documentsItem, caseBatchFilingItem],
    },
    {
        mode: 'work',
        key: 'official-workflow',
        label: '官方工作包',
        description: '递交与答复',
        children: [
            officialFilingPreparationItem,
            officialOAReplyItem,
            officialReceiptArchiveItem,
            officialFeeLinkageItem,
            officialLetterHandoffItem,
        ],
    },
    {
        mode: 'work',
        key: 'finance-flow',
        label: '费用到回款',
        description: '财务链路',
        children: [grantFeeTasksItem, feesItem, payListsItem, billsItem, paymentsItem, caseReceiptsItem],
    },
    {
        mode: 'work',
        key: 'post-grant',
        label: '授权后运营',
        description: '维护',
        children: [annuityTasksItem, dunningItem, commissionRecordsItem, commissionSettlementsItem],
    },
    {
        mode: 'work',
        key: 'work-support',
        label: '管理入口',
        pinnedBottom: true,
        children: [clientsItem, reportsHomeItem, settingsItem],
    },
    {
        mode: 'module',
        key: 'module-work',
        label: '我的工作',
        children: [demoAbcItem, dashboardItem, todayRemindersItem, tasksItem, taskSpecialSearchItem],
    },
    {
        mode: 'module',
        key: 'clients-cases',
        label: '客户与案件',
        children: [clientsItem, casesItem, caseNewItem, caseBatchFilingItem, consultingCaseNewItem],
    },
    {
        mode: 'module',
        key: 'documents-tasks',
        label: '文件与任务',
        children: [documentsItem, officialOAReplyItem, officialReceiptArchiveItem, officialLetterHandoffItem],
    },
    {
        mode: 'module',
        key: 'official-workflow',
        label: '官方工作包',
        children: [officialFilingPreparationItem, officialOAReplyItem, officialFeeLinkageItem, officialReceiptArchiveItem],
    },
    {
        mode: 'module',
        key: 'fees-billing',
        label: '费用与账单',
        children: [
            feesItem,
            feeRatesItem,
            grantFeeTasksItem,
            payListsItem,
            billsItem,
            paymentsItem,
            feeUnifiedQueryItem,
            offsetsItem,
            caseReceiptsItem,
            expensesItem,
        ],
    },
    {
        mode: 'module',
        key: 'post-grant-commission',
        label: '授权后与提成',
        children: [
            annuityTasksItem,
            dunningItem,
            commissionRulesItem,
            commissionRecordsItem,
            commissionSettlementsItem,
            consultingProfitabilityItem,
        ],
    },
    {
        mode: 'module',
        key: 'reports',
        label: '报表分析',
        children: [
            reportsHomeItem,
            caseReportItem,
            annuityReportItem,
            billReportItem,
            reportPaymentsItem,
            feeDraftReportItem,
            expenseReportItem,
            reportFeeUnifiedQueryItem,
            reportCommissionSettlementsItem,
            reportConsultingProfitabilityItem,
        ],
    },
    {
        mode: 'module',
        key: 'settings',
        label: '系统设置',
        children: [
            settingsItem,
            settingsMasterdataHomeItem,
            settingsMasterdataDepartmentsItem,
            taskTemplatesItem,
            docTemplatesItem,
            systemTemplatesItem,
            letterheadsItem,
        ],
    },
]
