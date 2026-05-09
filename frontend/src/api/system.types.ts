/**
 * System API Types
 */

// Template Types
export interface TemplateListItem {
    id: string
    code: string
    name: string
    file_type: string
    description?: string
    file_path?: string
    enabled?: boolean
    created_at: string
    updated_at: string
}

export interface TemplateDetail {
    id: string
    code: string
    name: string
    file_type: string
    description?: string
    file_path?: string
    enabled?: boolean
    created_at: string
    updated_at: string
}

export interface TemplateListParams {
    page?: number
    page_size?: number
    code?: string
}

export interface TemplateUploadPayload {
    code: string
    name: string
    file_type?: string
    description?: string
    file: File
}

// System Param Types
export interface SystemParamListItem {
    key: string
    value: string
    value_type?: string
    description?: string
    is_secret?: boolean
    created_at?: string
    updated_at?: string
}

export interface SystemParamUpsertPayload {
    value: string
    value_type?: string
    description?: string
    is_secret?: boolean
}

// Letterhead Types
export interface LetterheadListItem {
    id: string | number
    name: string
    locale?: string | null
    logo_file_path?: string | null
    is_default: boolean
    header_text?: string | null
    footer_text?: string | null
    address_block?: string | null
    phone?: string | null
    email?: string | null
    website?: string | null
    created_at: string
    updated_at: string
}

export interface LetterheadCreatePayload {
    name: string
    locale?: string
    logo_file_path?: string
    is_default?: boolean
    header_text?: string
    footer_text?: string
    address_block?: string
    phone?: string
    email?: string
    website?: string
}
