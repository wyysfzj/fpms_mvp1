/**
 * Task API Types
 */

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
}

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
    add_days: number | null
    add_months: number | null
    inner_offset_days: number | null
    default_worker_role: string | null
    enabled: boolean
    description: string | null
    created_at: string
    updated_at: string
}

export interface TaskTemplateCreatePayload {
    code: string
    name: string
    add_days?: number | null
    add_months?: number | null
    inner_offset_days?: number | null
    default_worker_role?: string | null
    description?: string | null
}

export interface TaskTemplateUpdatePayload {
    name?: string | null
    add_days?: number | null
    add_months?: number | null
    inner_offset_days?: number | null
    default_worker_role?: string | null
    enabled?: boolean | null
    description?: string | null
}
