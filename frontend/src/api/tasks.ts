import { http } from './http'
import type { Pagination } from './types'
import type { Task, TaskCreatePayload, TaskListParams, TaskLog, TaskTemplate, TaskTemplateCreatePayload, TaskTemplateUpdatePayload } from './tasks.types'

interface BackendTask {
    id: string
    title: string
    case_id?: string | null
    case_no?: string | null
    client_name?: string | null
    document_id?: string | null
    task_template_id?: string | null
    due_date?: string | null
    internal_due_date?: string | null
    base_date?: string | null
    worker_id?: string | null
    supervisor_id?: string | null
    remark?: string | null
    status?: string | null
    done_at?: string | null
    created_at?: string
    updated_at?: string
}

function mapTask(input: BackendTask): Task {
    return {
        id: input.id,
        title: input.title,
        description: input.remark || undefined,
        case_id: input.case_id || undefined,
        case_no: input.case_no || undefined,
        client_name: input.client_name || undefined,
        document_id: input.document_id || undefined,
        task_template_id: input.task_template_id || undefined,
        status: input.status || 'OPEN',
        due_date: input.due_date || undefined,
        internal_due: input.internal_due_date || undefined,
        base_date: input.base_date || undefined,
        assigned_to: input.worker_id || input.supervisor_id || undefined,
        worker_id: input.worker_id || undefined,
        supervisor_id: input.supervisor_id || undefined,
        remark: input.remark || undefined,
        done_at: input.done_at || undefined,
        created_at: input.created_at,
        updated_at: input.updated_at,
    }
}

function toCreatePayload(data: TaskCreatePayload): Record<string, unknown> {
    let remark = data.description?.trim() || ''
    if (data.priority) {
        const priorityTag = `[priority:${data.priority}]`
        remark = remark ? `${remark}\n${priorityTag}` : priorityTag
    }

    return {
        case_id: String(data.case_id),
        title: data.title,
        due_date: data.due_date,
        worker_id: data.assigned_to || undefined,
        remark: remark || undefined,
    }
}

/**
 * Get a single task by ID
 */
export async function getTask(id: string): Promise<Task> {
    const response = await http.get<BackendTask>(`/tasks/${id}`)
    return mapTask(response.data)
}

/**
 * Get task audit logs
 */
export async function getTaskLogs(taskId: string): Promise<TaskLog[]> {
    const response = await http.get<TaskLog[]>(`/tasks/${taskId}/logs`)
    return response.data
}

/**
 * Get paginated list of tasks
 */
export async function getTasks(params: TaskListParams = {}): Promise<Pagination<Task>> {
    const { page = 1, page_size = 20, status, case_id, client_id, as } = params
    const response = await http.get<Pagination<BackendTask>>('/tasks', {
        params: {
            page,
            page_size,
            ...(status ? { status } : {}),
            ...(case_id ? { case_id } : {}),
            ...(client_id ? { client_id } : {}),
            ...(as ? { as } : {}),
        }
    })

    return {
        ...response.data,
        items: response.data.items.map(mapTask),
    }
}

/**
 * Create a new task
 */
export async function createTask(data: TaskCreatePayload): Promise<Task> {
    const response = await http.post<BackendTask>('/tasks', toCreatePayload(data))
    return mapTask(response.data)
}

/**
 * Close a task
 */
export async function closeTask(id: string | number): Promise<void> {
    await http.post(`/tasks/${id}/close`, {})
}

/**
 * Reopen a task
 */
export async function reopenTask(id: string | number): Promise<void> {
    await http.post(`/tasks/${id}/reopen`, {})
}

/**
 * Cancel a task
 */
export async function cancelTask(id: string | number): Promise<void> {
    await http.post(`/tasks/${id}/cancel`, {})
}

/**
 * Delete a manually maintained task
 */
export async function deleteTask(id: string | number): Promise<void> {
    await http.delete(`/tasks/${id}`)
}

/**
 * Get today's reminders for worker or supervisor
 */
export async function getTodayReminders(mode: 'worker' | 'supervisor'): Promise<Pagination<Task>> {
    const response = await http.get<Pagination<BackendTask>>('/tasks/today', {
        params: { as: mode }
    })

    return {
        ...response.data,
        items: response.data.items.map(mapTask),
    }
}

// ── Task Template CRUD ─────────────────────────────

export async function getTaskTemplates(enabledOnly?: boolean): Promise<TaskTemplate[]> {
    const response = await http.get<TaskTemplate[]>('/task-templates', {
        params: enabledOnly != null ? { enabled_only: enabledOnly } : undefined,
    })
    return response.data
}

export async function createTaskTemplate(data: TaskTemplateCreatePayload): Promise<TaskTemplate> {
    const response = await http.post<TaskTemplate>('/task-templates', data)
    return response.data
}

export async function updateTaskTemplate(id: string, data: TaskTemplateUpdatePayload): Promise<TaskTemplate> {
    const response = await http.put<TaskTemplate>(`/task-templates/${id}`, data)
    return response.data
}
