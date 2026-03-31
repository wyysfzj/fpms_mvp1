/**
 * Task API Types
 */

import type { Pagination } from './types'

export type TaskDeadlineBase =
    | 'FILING_DATE'
    | 'RECEIVE_DATE'
    | 'DISPATCH_DATE'
    | 'PUB_DATE'
    | 'GRANT_DATE'
    | 'CASE_EVENT'
    | 'CUSTOM'

export type TaskRemindBase = 'INNER' | 'DEADLINE'

export interface Task {
    id: string
    title: string
    description?: string
    case_id?: string
    case_no?: string
    client_name?: string
    document_id?: string
    task_template_id?: string
    status: string
    priority?: string
    due_date?: string
    internal_due?: string
    base_date?: string
    assigned_to?: string
    worker_id?: string
    supervisor_id?: string
    remark?: string
    done_at?: string
    created_at?: string
    updated_at?: string
}

export interface TaskLog {
    id: string
    task_id: string
    action: string
    from_status?: string
    to_status?: string
    remark?: string
    created_at: string
}

export interface TaskListParams {
    page?: number
    page_size?: number
    status?: string
    case_id?: string
    client_id?: string
    as?: 'worker' | 'supervisor'
}

export interface TaskSpecialSearchItem {
    task_code: string
    task_id: string
    case_id: string
    case_no?: string | null
    client_name?: string | null
    title: string
    status: string
    due_date?: string | null
    is_overdue: boolean
    remark?: string | null
}

export interface TaskSpecialSearchParams {
    page?: number
    page_size?: number
    task_code?: string
    status?: string
    case_no?: string
    client_name?: string
    due_date_from?: string
    due_date_to?: string
    is_overdue?: boolean
}

export type TaskSpecialSearchResponse = Pagination<TaskSpecialSearchItem>

export interface TaskCreatePayload {
    title: string
    description?: string
    case_id: string
    priority?: string
    due_date: string
    assigned_to?: string
}

export interface TaskTemplate {
    id: string
    code: string
    name: string
    deadline_base?: TaskDeadlineBase | null
    add_days: number | null
    add_months: number | null
    inner_offset_days: number | null
    remind_base?: TaskRemindBase | null
    remind_1_offset_days?: number | null
    remind_2_offset_days?: number | null
    remind_3_offset_days?: number | null
    daily_remind: boolean
    default_supervisor_id?: string | null
    default_worker_role: string | null
    enabled: boolean
    description: string | null
    created_at: string
    updated_at: string
}

export interface TaskTemplateCreatePayload {
    code: string
    name: string
    deadline_base?: TaskDeadlineBase | null
    add_days?: number | null
    add_months?: number | null
    inner_offset_days?: number | null
    remind_base?: TaskRemindBase | null
    remind_1_offset_days?: number | null
    remind_2_offset_days?: number | null
    remind_3_offset_days?: number | null
    daily_remind?: boolean
    default_supervisor_id?: string | null
    default_worker_role?: string | null
    description?: string | null
}

export interface TaskTemplateUpdatePayload {
    name?: string | null
    deadline_base?: TaskDeadlineBase | null
    add_days?: number | null
    add_months?: number | null
    inner_offset_days?: number | null
    remind_base?: TaskRemindBase | null
    remind_1_offset_days?: number | null
    remind_2_offset_days?: number | null
    remind_3_offset_days?: number | null
    daily_remind?: boolean
    default_supervisor_id?: string | null
    default_worker_role?: string | null
    enabled?: boolean | null
    description?: string | null
}
