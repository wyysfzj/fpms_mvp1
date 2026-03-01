import { getClients } from '../../api/clients'
import { getCases } from '../../api/cases'
import { getTasks } from '../../api/tasks'
import { getBills, getPayments } from '../../api/billing'
import { getFeeDrafts } from '../../api/fees'
import type { Case } from '../../api/cases.types'
import type { Task } from '../../api/tasks.types'
import type { Pagination } from '../../api/types'
import type { EnrichedTask } from './components/ActionCenter.vue'
import type { FinanceItem } from './components/FinanceRow.vue'
import { WORKFLOW_STEPS, getStatusRule, getStepIndex } from '../../constants/workflow'

// ---- Legacy KPI (kept for backward compat) ----

export interface DashboardKpi {
    clientsTotal: number
    casesTotal: number
    tasksTotal: number
    tasksPendingTotal: number
    billsTotal: number
}

export async function fetchDashboardKpi(): Promise<DashboardKpi> {
    const [clients, cases, tasks, pendingTasks, bills] = await Promise.all([
        getClients({ page: 1, page_size: 1 }),
        getCases({ page: 1, page_size: 1 }),
        getTasks({ page: 1, page_size: 1 }),
        getTasks({ page: 1, page_size: 1, status: 'OPEN' }),
        getBills({ page: 1, page_size: 1 }),
    ])

    return {
        clientsTotal: clients.total,
        casesTotal: cases.total,
        tasksTotal: tasks.total,
        tasksPendingTotal: pendingTasks.total,
        billsTotal: bills.total,
    }
}

export async function fetchTodoTasks(): Promise<Pagination<Task>> {
    return getTasks({
        page: 1,
        page_size: 10,
        status: 'OPEN',
    })
}

// ---- Pipeline KPI ----

export interface PipelineKpi {
    newCasesCount: number
    pendingTasksCount: number
    urgentTasksCount: number
    unbilledDraftsAmount: number
    unallocatedPaymentsAmount: number
}

export async function fetchPipelineKpi(): Promise<PipelineKpi> {
    // MVP限制: 客户端聚合，page_size 按后端接口上限控制为 100。
    // 生产环境应替换为服务端聚合接口 (如 GET /api/v1/dashboard/kpi)
    const [cases, pendingTasks, drafts, payments] = await Promise.all([
        getCases({ page: 1, page_size: 1 }),
        getTasks({ page: 1, page_size: 100, status: 'OPEN' }),
        getFeeDrafts({ status: 'OPEN', page: 1, page_size: 100 }),
        getPayments({ page: 1, page_size: 100 }),
    ])

    // Count urgent tasks (due within 3 days)
    const now = new Date()
    const urgentCount = pendingTasks.items.filter(t => {
        if (!t.due_date) return false
        const due = new Date(t.due_date)
        const diffDays = (due.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)
        return diffDays >= 0 && diffDays <= 3
    }).length

    // Sum unbilled draft amounts
    const unbilledSum = drafts.items.reduce((sum, d) => sum + Number(d.amount || 0), 0)

    // MVP限制: 付款总额包含所有付款记录，非仅未核销部分。
    // 系统暂无 offset 状态字段可用于过滤真正未分配的付款。
    const paymentSum = payments.items.reduce((sum, p) => sum + p.amount, 0)

    return {
        newCasesCount: cases.total,
        pendingTasksCount: pendingTasks.total,
        urgentTasksCount: urgentCount,
        unbilledDraftsAmount: unbilledSum,
        unallocatedPaymentsAmount: paymentSum,
    }
}

// ---- Enriched Tasks (Action Center) ----

function computeDeadline(dueDate?: string): { text: string; class: string } {
    if (!dueDate) return { text: '', class: 'normal' }
    const due = new Date(dueDate)
    const now = new Date()
    const diffDays = Math.ceil((due.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))

    if (diffDays < 0) {
        return { text: `已逾期${Math.abs(diffDays)}天`, class: 'urgent' }
    }
    if (diffDays <= 3) {
        return { text: `绝限: 剩${diffDays}天`, class: 'urgent' }
    }
    if (diffDays <= 7) {
        return { text: `剩${diffDays}天`, class: 'warn' }
    }
    return { text: `剩${diffDays}天`, class: 'normal' }
}

export async function fetchEnrichedTasks(): Promise<EnrichedTask[]> {
    const tasksRes = await getTasks({ page: 1, page_size: 10, status: 'OPEN' })

    return tasksRes.items.map(task => {
        const deadline = computeDeadline(task.due_date)
        return {
            id: task.id,
            title: task.title,
            case_id: task.case_id,
            case_no: task.case_no,
            client_name: task.client_name,
            has_document: !!task.document_id,
            has_fee: false,
            deadline_text: deadline.text,
            deadline_class: deadline.class,
        }
    })
}

// ---- Finance Data ----

export async function fetchFinanceData(): Promise<FinanceItem[]> {
    const [billsRes, paymentsRes] = await Promise.all([
        getBills({ page: 1, page_size: 50 }),
        getPayments({ page: 1, page_size: 20 }),
    ])

    const items: FinanceItem[] = []
    const now = new Date()

    // Recent payments → "待核销"
    for (const p of paymentsRes.items.slice(0, 3)) {
        items.push({
            type: 'payment',
            id: `pay-${p.id}`,
            label: p.reference || `回款#${p.id.slice(0, 8)}`,
            amount: p.amount,
            currency: p.currency,
            badge_text: '待核销',
            badge_class: 'normal',
            date: p.payment_date,
            highlight: true,
        })
    }

    // Overdue bills
    const overdueBills = billsRes.items.filter(b => {
        if (b.status !== 'UNSETTLED') return false
        if (!b.due_date) return false
        return new Date(b.due_date) < now
    })

    for (const b of overdueBills.slice(0, 3)) {
        const dueDiff = Math.ceil((now.getTime() - new Date(b.due_date!).getTime()) / (1000 * 60 * 60 * 24))
        items.push({
            type: 'overdue_bill',
            id: `bill-${b.id}`,
            label: b.bill_no,
            amount: b.amount,
            currency: b.currency,
            badge_text: `已逾期${dueDiff}天`,
            badge_class: 'urgent',
            date: b.due_date,
            highlight: false,
        })
    }

    // Pending bills (not overdue)
    const pendingBills = billsRes.items.filter(b => {
        if (b.status !== 'UNSETTLED') return false
        if (!b.due_date) return true // no due_date = pending
        return new Date(b.due_date) >= now
    })

    for (const b of pendingBills.slice(0, 3)) {
        items.push({
            type: 'pending_bill',
            id: `bill-${b.id}`,
            label: b.bill_no,
            amount: b.amount,
            currency: b.currency,
            badge_text: '待付款',
            badge_class: 'warn',
            date: b.due_date,
            highlight: false,
        })
    }

    // Cap at 5 items total, keeping the order: payments → overdue → pending
    return items.slice(0, 5)
}

// ---- Workflow Stats (client-side aggregation) ----

export interface WorkflowStepStat {
    key: string
    label: string
    color: string
    count: number
    percent: number
}

export interface WorkflowStats {
    steps: WorkflowStepStat[]
    total: number
    cases: Case[]
}

export async function fetchWorkflowStats(): Promise<WorkflowStats> {
    // MVP: fetch all cases client-side and group by workflow step
    const res = await getCases({ page: 1, page_size: 100 })
    const allCases = res.items

    const stepCounts = new Map<string, number>()
    for (const step of WORKFLOW_STEPS) {
        stepCounts.set(step.key, 0)
    }

    for (const c of allCases) {
        const rule = getStatusRule(c.status)
        const current = stepCounts.get(rule.stepKey) || 0
        stepCounts.set(rule.stepKey, current + 1)
    }

    const total = allCases.length
    const steps: WorkflowStepStat[] = WORKFLOW_STEPS.map(step => ({
        key: step.key,
        label: step.label,
        color: step.color,
        count: stepCounts.get(step.key) || 0,
        percent: total ? Math.round(((stepCounts.get(step.key) || 0) / total) * 100) : 0,
    }))

    return { steps, total, cases: allCases }
}

export function filterCasesByStep(cases: Case[], stepKey: string | null): Case[] {
    if (!stepKey) return cases
    return cases.filter(c => {
        const rule = getStatusRule(c.status)
        return rule.stepKey === stepKey
    })
}

export { getStepIndex }
