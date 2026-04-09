import { http } from './http'
import type { Pagination } from './types'
import type {
    Department,
    DepartmentCreatePayload,
    DepartmentListParams,
    DepartmentUpdatePayload,
} from './departments.types'

interface BackendDepartment {
    id: string
    department_code: string
    name_cn: string
    is_active?: boolean | null
}

function mapDepartment(input: BackendDepartment): Department {
    return {
        id: input.id,
        department_code: input.department_code,
        name_cn: input.name_cn,
        is_active: input.is_active ?? true,
    }
}

export async function getDepartments(
    params: DepartmentListParams = {},
): Promise<Pagination<Department>> {
    const { page = 1, page_size = 20, q, is_active } = params
    const response = await http.get<Pagination<BackendDepartment>>('/departments', {
        params: {
            page,
            page_size,
            q: q?.trim() || undefined,
            is_active,
        },
    })

    return {
        ...response.data,
        items: response.data.items.map(mapDepartment),
    }
}

export async function createDepartment(data: DepartmentCreatePayload): Promise<Department> {
    const response = await http.post<BackendDepartment>('/departments', {
        department_code: data.department_code.trim(),
        name_cn: data.name_cn.trim(),
        is_active: data.is_active ?? true,
    })
    return mapDepartment(response.data)
}

export async function updateDepartment(
    id: string | number,
    data: DepartmentUpdatePayload,
): Promise<Department> {
    const payload: Record<string, unknown> = {}
    if (data.department_code !== undefined) payload.department_code = data.department_code.trim()
    if (data.name_cn !== undefined) payload.name_cn = data.name_cn.trim()
    if (data.is_active !== undefined) payload.is_active = data.is_active

    const response = await http.put<BackendDepartment>(`/departments/${id}`, payload)
    return mapDepartment(response.data)
}

export async function deactivateDepartment(id: string | number): Promise<void> {
    await http.put(`/departments/${id}/deactivate`)
}
