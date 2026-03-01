import { http } from './http'
import type { Pagination } from './types'
import type { Case, CaseListParams, CaseCreatePayload, CaseUpdatePayload, CaseLimitedEditPayload } from './cases.types'

/** FB5: Server-side filter parameters for case list */
interface CaseFilterParams extends CaseListParams {
  client_id?: string
  case_type?: string
  patent_category?: string
  flow_dir?: string
  status?: string
  filing_date_from?: string   // YYYY-MM-DD
  filing_date_to?: string     // YYYY-MM-DD
  primary_agent_id?: string
}

interface BackendCase {
    id: string
    case_no: string
    case_type?: string
    patent_category?: string
    client_id?: string | null
    client_name?: string | null
    title_cn?: string | null
    title_en?: string | null
    status?: string | null
    filing_date?: string | null
    recv_date?: string | null
    app_no?: string | null
    app_date?: string | null
    applicants?: Array<{ seq: number; is_first?: boolean; name_cn?: string; name_en?: string; address_cn?: string; address_en?: string }>
    inventors?: Array<{ seq: number; name_cn?: string; name_en?: string }>
    // A3: Publication & Grant
    pub_date?: string | null
    pub_no?: string | null
    grant_date?: string | null
    grant_no?: string | null
    patent_no?: string | null
    valid_until?: string | null
    // A3: Specification
    spec_pages?: number | null
    claim_count?: number | null
    has_exam_request?: boolean | null
    // A3: Agent Assignment
    primary_agent_id?: string | null
    second_agent_id?: string | null
    draftor_id?: string | null
    // A3: Control Flags
    is_fee_monitor?: boolean | null
    fee_reduction?: string | null
    applicant_kind?: string | null
    created_at?: string
    updated_at?: string
}

function mapCase(input: BackendCase): Case {
    return {
        id: input.id,
        case_no: input.case_no,
        title: input.title_cn || input.title_en || undefined,
        client_id: input.client_id || '',
        client_name: input.client_name || undefined,
        status: input.status || undefined,
        filing_date: input.filing_date || undefined,
        recv_date: input.recv_date || undefined,
        app_no: input.app_no || undefined,
        app_date: input.app_date || undefined,
        applicants: input.applicants || [],
        inventors: input.inventors || [],
        // Publication & Grant
        pub_date: input.pub_date || undefined,
        pub_no: input.pub_no || undefined,
        grant_date: input.grant_date || undefined,
        grant_no: input.grant_no || undefined,
        patent_no: input.patent_no || undefined,
        valid_until: input.valid_until || undefined,
        // Specification
        spec_pages: input.spec_pages ?? undefined,
        claim_count: input.claim_count ?? undefined,
        has_exam_request: input.has_exam_request ?? undefined,
        // Agent Assignment
        primary_agent_id: input.primary_agent_id || undefined,
        second_agent_id: input.second_agent_id || undefined,
        draftor_id: input.draftor_id || undefined,
        // Control Flags
        is_fee_monitor: input.is_fee_monitor ?? undefined,
        fee_reduction: input.fee_reduction || undefined,
        applicant_kind: input.applicant_kind || undefined,
        created_at: input.created_at || '',
        updated_at: input.updated_at || '',
    }
}

/**
 * Get paginated list of cases
 */
export async function getCases(params: CaseFilterParams = {}): Promise<Pagination<Case>> {
    const { page = 1, page_size = 20, ...filters } = params
    // Build clean params — only include non-empty filter values
    const queryParams: Record<string, string | number> = { page, page_size }
    for (const [key, value] of Object.entries(filters)) {
        if (value !== undefined && value !== null && value !== '') {
            queryParams[key] = value
        }
    }
    const response = await http.get<Pagination<BackendCase>>('/cases', {
        params: queryParams
    })

    return {
        ...response.data,
        items: response.data.items.map(mapCase),
    }
}

/**
 * Get a single case by ID
 */
export async function getCase(id: string | number): Promise<Case> {
    const response = await http.get<BackendCase>(`/cases/${id}`)
    return mapCase(response.data)
}

/**
 * Create a new case
 */
export async function createCase(data: CaseCreatePayload): Promise<Case> {
    // Backend expects title_cn (not title) and patent_category
    const payload: Record<string, unknown> = {
        case_no: data.case_no,
        client_id: data.client_id,
        title_cn: data.title || undefined,
        patent_category: data.patent_category || undefined,
        // A3 fields
        pub_date: data.pub_date || undefined,
        pub_no: data.pub_no || undefined,
        grant_date: data.grant_date || undefined,
        grant_no: data.grant_no || undefined,
        patent_no: data.patent_no || undefined,
        valid_until: data.valid_until || undefined,
        spec_pages: data.spec_pages ?? undefined,
        claim_count: data.claim_count ?? undefined,
        has_exam_request: data.has_exam_request ?? undefined,
        primary_agent_id: data.primary_agent_id || undefined,
        second_agent_id: data.second_agent_id || undefined,
        draftor_id: data.draftor_id || undefined,
        is_fee_monitor: data.is_fee_monitor ?? undefined,
        fee_reduction: data.fee_reduction || undefined,
        applicant_kind: data.applicant_kind || undefined,
    }
    const response = await http.post<BackendCase>('/cases', payload)
    return mapCase(response.data)
}

/**
 * Update an existing case
 */
export async function updateCase(id: string | number, data: CaseUpdatePayload): Promise<Case> {
    const response = await http.put<BackendCase>(`/cases/${id}`, data)
    return mapCase(response.data)
}

/**
 * Limited edit for a case (restricted fields)
 */
export async function limitedEditCase(id: string | number, data: CaseLimitedEditPayload): Promise<Case> {
    const response = await http.post<BackendCase>(`/cases/${id}/limited-edit`, data)
    return mapCase(response.data)
}
