export interface Department {
    id: string
    department_code: string
    name_cn: string
    is_active: boolean
}

export interface DepartmentListParams {
    page?: number
    page_size?: number
    q?: string
    is_active?: boolean
}

export interface DepartmentCreatePayload {
    department_code: string
    name_cn: string
    is_active?: boolean
}

export interface DepartmentUpdatePayload {
    department_code?: string
    name_cn?: string
    is_active?: boolean
}
