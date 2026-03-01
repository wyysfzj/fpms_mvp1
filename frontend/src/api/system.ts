import { http } from './http'
import type { Pagination } from './types'
import type {
    LetterheadCreatePayload,
    LetterheadListItem,
    SystemParamListItem,
    SystemParamUpsertPayload,
    TemplateDetail,
    TemplateListItem,
    TemplateListParams,
    TemplateUploadPayload,
} from './system.types'

interface BackendTemplate {
    id: string
    name: string
    group?: string | null
    language?: string | null
    file_path: string
    enabled: boolean
    created_at: string
}

interface SystemParamBackendListItem {
    param_key: string
    param_value: string
    value_type?: string
    is_secret?: boolean
}

function inferFileType(filePath: string, language?: string | null): string {
    if (language) return language

    const ext = filePath.split('.').pop()?.toLowerCase()
    if (!ext) return 'file'
    return ext
}

function mapTemplate(input: BackendTemplate): TemplateListItem {
    const fileType = inferFileType(input.file_path, input.language)

    return {
        id: input.id,
        code: input.group || '',
        name: input.name,
        file_type: fileType,
        description: undefined,
        file_path: input.file_path,
        enabled: input.enabled,
        created_at: input.created_at,
        updated_at: input.created_at,
    }
}

// ============ Templates ============

/**
 * Get paginated list of templates
 */
export async function getTemplates(params: TemplateListParams = {}): Promise<Pagination<TemplateListItem>> {
    const { page = 1, page_size = 20, code } = params
    const response = await http.get<Pagination<BackendTemplate>>('/templates', {
        params: { page, page_size, group: code }
    })

    return {
        ...response.data,
        items: response.data.items.map(mapTemplate),
    }
}

/**
 * Get a single template by ID
 */
export async function getTemplate(id: string): Promise<TemplateDetail> {
    const response = await http.get<BackendTemplate>(`/templates/${id}`)
    return mapTemplate(response.data)
}

/**
 * Upload a new template
 */
export async function uploadTemplate(payload: TemplateUploadPayload): Promise<TemplateDetail> {
    const filePath = `uploads/templates/${payload.file.name}`
    const response = await http.post<BackendTemplate>('/templates', {
        name: payload.name,
        group: payload.code || null,
        language: payload.file_type || null,
        file_path: filePath,
        enabled: true,
    })
    return mapTemplate(response.data)
}

/**
 * Disable a template (soft-delete via update)
 */
export async function deleteTemplate(id: string): Promise<void> {
    await http.put(`/templates/${id}`, { enabled: false })
}

// ============ System Params ============

/**
 * Get all system params
 */
export async function getSystemParams(): Promise<SystemParamListItem[]> {
    const response = await http.get<SystemParamBackendListItem[]>('/system/params')
    return response.data.map((item) => ({
        key: item.param_key,
        value: item.param_value,
    }))
}

/**
 * Upsert a system param by key
 */
export async function upsertSystemParam(key: string, payload: SystemParamUpsertPayload): Promise<void> {
    await http.put(`/system/params/${key}`, {
        param_value: payload.value,
        value_type: payload.value_type || 'string',
        description: payload.description,
    })
}

// ============ Letterheads ============

/**
 * Get all letterheads
 */
export async function getLetterheads(): Promise<LetterheadListItem[]> {
    const response = await http.get<LetterheadListItem[]>('/letterheads')
    return response.data
}

/**
 * Create a new letterhead
 */
export async function createLetterhead(payload: LetterheadCreatePayload): Promise<LetterheadListItem> {
    const response = await http.post<LetterheadListItem>('/letterheads', {
        name: payload.name,
        locale: payload.locale || null,
        logo_file_path: payload.logo_file_path || null,
        header_text: payload.header_text || null,
        footer_text: payload.footer_text || null,
        address_block: payload.address_block || null,
        phone: payload.phone || null,
        email: payload.email || null,
        website: payload.website || null,
        is_default: payload.is_default || false,
    })
    return response.data
}

/**
 * Delete letterhead is not exposed by backend.
 */
export async function deleteLetterhead(): Promise<void> {
    throw {
        status: 405,
        code: 'METHOD_NOT_ALLOWED',
        message: 'Delete letterhead endpoint is not available in backend API.',
    }
}
