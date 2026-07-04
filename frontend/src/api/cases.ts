import { http } from './http'
import type { Pagination } from './types'
import type {
    Case,
    CaseBatchFilingActionPayload,
    CaseBatchFilingActionResult,
    CaseBatchFilingCandidate,
    CaseBatchFilingQueryParams,
    CaseCreatePayload,
    CaseDocumentGatePreview,
    CaseIntakeDocumentGateParams,
    CaseLimitedEditPayload,
    CaseListResponse,
    CaseListParams,
    CaseUpdatePayload,
} from './cases.types'

interface BackendCase {
    id: string
    case_no: string
    case_type?: string
    patent_category?: string
    flow_dir?: string
    client_id?: string | null
    client_name?: string | null
    foreign_agent_id?: string | null
    foreign_agent_name?: string | null
    foreign_ref?: string | null
    from_country?: string | null
    to_country?: string | null
    doc_address_id?: string | null
    bill_address_id?: string | null
    title_cn?: string | null
    title_en?: string | null
    status?: string | null
    filing_date?: string | null
    recv_date?: string | null
    issue_date?: string | null
    app_no?: string | null
    cert_no?: string | null
    draw_pages?: number | null
    claim_pages?: number | null
    manuscript_words?: number | null
    discount_rate?: string | null
    no_power?: boolean | null
    no_prio_text?: boolean | null
    require_hk?: boolean | null
    first_annuity_year?: number | null
    app_date?: string | null
    applicants?: Array<{
        seq: number
        is_first?: boolean
        name_cn?: string
        name_en?: string
        address_cn?: string
        address_en?: string
        nationality?: string | null
        certificate_type?: string | null
        certificate_no?: string | null
        official_postcode?: string | null
        official_applicant_kind?: string | null
    }>
    inventors?: Array<{
        seq: number
        name_cn?: string
        name_en?: string
        nationality?: string | null
        china_id_no?: string | null
    }>
    priorities?: Array<{ seq: number; country_code?: string | null; prio_no?: string | null; prio_date?: string | null }>
    bio_deposits?: Array<{ seq: number; deposit_no?: string | null; deposit_unit_name?: string | null; deposit_date?: string | null; name?: string | null }>
    agent_splits?: Array<{ agent_id: string; role?: string | null; share_ratio?: string | number | null }>
    ro?: string | null
    isa?: string | null
    ipea?: string | null
    intl_app_no?: string | null
    intl_app_date?: string | null
    intl_pub_no?: string | null
    intl_pub_date?: string | null
    intl_pub_lang?: string | null
    need_iper?: boolean | null
    iper_date?: string | null
    pct_national_entry_date?: string | null
    original_case_id?: string | null
    invalid_client_id?: string | null
    invalid_client_name?: string | null
    invalid_patentee?: string | null
    invalid_requester?: string | null
    invalid_role?: string | null
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

interface BackendCaseListResponse {
    items: BackendCase[]
    page: number
    page_size: number
    total: number
    summary: {
        total_case_count?: number
        status_counts?: Array<{ key: string; count: number }>
        case_type_counts?: Array<{ key: string; count: number }>
        client_counts?: Array<{
            key: string
            label: string
            count: number
            case_type_counts?: Array<{ key: string; count: number }>
        }>
        country_counts?: Array<{ key: string; count: number }>
        agent_counts?: Array<{ key: string; count: number }>
        year_trends?: Array<{
            key: string
            label: string
            new_case_count: number
            granted_count: number
            terminated_count: number
            invalidated_count: number
            withdrawn_count: number
            abandoned_count: number
        }>
        month_trends?: Array<{
            key: string
            label: string
            new_case_count: number
            granted_count: number
            terminated_count: number
            invalidated_count: number
            withdrawn_count: number
            abandoned_count: number
        }>
        granted_count?: number
        grant_rate?: number | null
        terminated_count?: number
        invalidated_count?: number
        in_prosecution_count?: number
    }
}

interface BackendCaseBatchFilingCandidate {
    id: string
    case_no: string
    title_cn?: string | null
    client_name?: string | null
    case_type: string
    patent_category: string
    flow_dir: string
    recv_date?: string | null
    status: string
    has_exam_request?: boolean | null
    final_material_gate?: CaseBatchFilingCandidate['final_material_gate'] | null
}

function mapCase(input: BackendCase): Case {
    return {
        id: input.id,
        case_no: input.case_no,
        case_type: input.case_type || undefined,
        patent_category: input.patent_category || undefined,
        flow_dir: input.flow_dir || undefined,
        title: input.title_cn || input.title_en || undefined,
        client_id: input.client_id || '',
        client_name: input.client_name || undefined,
        foreign_agent_id: input.foreign_agent_id || undefined,
        foreign_agent_name: input.foreign_agent_name || undefined,
        foreign_ref: input.foreign_ref || undefined,
        from_country: input.from_country || undefined,
        to_country: input.to_country || undefined,
        doc_address_id: input.doc_address_id || undefined,
        bill_address_id: input.bill_address_id || undefined,
        status: input.status || undefined,
        filing_date: input.filing_date || undefined,
        recv_date: input.recv_date || undefined,
        issue_date: input.issue_date || undefined,
        app_no: input.app_no || undefined,
        cert_no: input.cert_no || undefined,
        draw_pages: input.draw_pages ?? undefined,
        claim_pages: input.claim_pages ?? undefined,
        manuscript_words: input.manuscript_words ?? undefined,
        discount_rate: input.discount_rate || undefined,
        no_power: input.no_power ?? undefined,
        no_prio_text: input.no_prio_text ?? undefined,
        require_hk: input.require_hk ?? undefined,
        first_annuity_year: input.first_annuity_year ?? undefined,
        app_date: input.app_date || undefined,
        applicants: (input.applicants || []).map((applicant) => ({
            seq: applicant.seq,
            is_first: applicant.is_first,
            name_cn: applicant.name_cn || undefined,
            name_en: applicant.name_en || undefined,
            address_cn: applicant.address_cn || undefined,
            address_en: applicant.address_en || undefined,
            nationality: applicant.nationality || undefined,
            certificate_type: applicant.certificate_type || undefined,
            certificate_no: applicant.certificate_no || undefined,
            official_postcode: applicant.official_postcode || undefined,
            official_applicant_kind: applicant.official_applicant_kind || undefined,
        })),
        inventors: (input.inventors || []).map((inventor) => ({
            seq: inventor.seq,
            name_cn: inventor.name_cn || undefined,
            name_en: inventor.name_en || undefined,
            nationality: inventor.nationality || undefined,
            china_id_no: inventor.china_id_no || undefined,
        })),
        priorities: (input.priorities || []).map((priority) => ({
            seq: priority.seq,
            country_code: priority.country_code || undefined,
            prio_no: priority.prio_no || undefined,
            prio_date: priority.prio_date || undefined,
        })),
        bio_deposits: (input.bio_deposits || []).map((bioDeposit) => ({
            seq: bioDeposit.seq,
            deposit_no: bioDeposit.deposit_no || undefined,
            deposit_unit_name: bioDeposit.deposit_unit_name || undefined,
            deposit_date: bioDeposit.deposit_date || undefined,
            name: bioDeposit.name || undefined,
        })),
        agent_splits: (input.agent_splits || []).map((agentSplit) => ({
            agent_id: agentSplit.agent_id,
            role: agentSplit.role || undefined,
            share_ratio: agentSplit.share_ratio !== undefined && agentSplit.share_ratio !== null
                ? Number(agentSplit.share_ratio)
                : null,
        })),
        ro: input.ro || undefined,
        isa: input.isa || undefined,
        ipea: input.ipea || undefined,
        intl_app_no: input.intl_app_no || undefined,
        intl_app_date: input.intl_app_date || undefined,
        intl_pub_no: input.intl_pub_no || undefined,
        intl_pub_date: input.intl_pub_date || undefined,
        intl_pub_lang: input.intl_pub_lang || undefined,
        need_iper: input.need_iper ?? undefined,
        iper_date: input.iper_date || undefined,
        pct_national_entry_date: input.pct_national_entry_date || undefined,
        original_case_id: input.original_case_id || undefined,
        invalid_client_id: input.invalid_client_id || undefined,
        invalid_client_name: input.invalid_client_name || undefined,
        invalid_patentee: input.invalid_patentee || undefined,
        invalid_requester: input.invalid_requester || undefined,
        invalid_role: input.invalid_role || undefined,
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

function trimToUndefined(value: string | null | undefined): string | undefined {
    if (typeof value !== 'string') return value ?? undefined
    const normalized = value.trim()
    return normalized ? normalized : undefined
}

function trimToNull(value: string | null | undefined): string | null | undefined {
    if (value === undefined) return undefined
    if (value === null) return null
    const normalized = value.trim()
    return normalized ? normalized : null
}

function mapBatchFilingCandidate(input: BackendCaseBatchFilingCandidate): CaseBatchFilingCandidate {
    return {
        id: input.id,
        case_no: input.case_no,
        title_cn: input.title_cn || undefined,
        client_name: input.client_name || undefined,
        case_type: input.case_type,
        patent_category: input.patent_category,
        flow_dir: input.flow_dir,
        recv_date: input.recv_date || undefined,
        status: input.status,
        has_exam_request: input.has_exam_request ?? undefined,
        final_material_gate: input.final_material_gate || undefined,
    }
}

function toUpdatePayload(data: CaseUpdatePayload): Record<string, unknown> {
    const payload: Record<string, unknown> = {}

    if (data.title !== undefined) payload.title = trimToNull(data.title)
    if (data.status !== undefined) payload.status = trimToNull(data.status)
    if (data.filing_date !== undefined) payload.filing_date = trimToNull(data.filing_date)
    if (data.recv_date !== undefined) payload.recv_date = trimToNull(data.recv_date)
    if (data.foreign_agent_id !== undefined) payload.foreign_agent_id = trimToNull(data.foreign_agent_id)
    if (data.foreign_ref !== undefined) payload.foreign_ref = trimToNull(data.foreign_ref)
    if (data.from_country !== undefined) payload.from_country = trimToNull(data.from_country)
    if (data.to_country !== undefined) payload.to_country = trimToNull(data.to_country)
    if (data.doc_address_id !== undefined) payload.doc_address_id = trimToNull(data.doc_address_id)
    if (data.bill_address_id !== undefined) payload.bill_address_id = trimToNull(data.bill_address_id)
    if (data.app_no !== undefined) payload.app_no = trimToNull(data.app_no)
    if (data.issue_date !== undefined) payload.issue_date = trimToNull(data.issue_date)
    if (data.cert_no !== undefined) payload.cert_no = trimToNull(data.cert_no)
    if (data.draw_pages !== undefined) payload.draw_pages = data.draw_pages
    if (data.claim_pages !== undefined) payload.claim_pages = data.claim_pages
    if (data.manuscript_words !== undefined) payload.manuscript_words = data.manuscript_words
    if (data.discount_rate !== undefined) payload.discount_rate = trimToNull(data.discount_rate)
    if (data.no_power !== undefined) payload.no_power = data.no_power
    if (data.no_prio_text !== undefined) payload.no_prio_text = data.no_prio_text
    if (data.require_hk !== undefined) payload.require_hk = data.require_hk
    if (data.first_annuity_year !== undefined) payload.first_annuity_year = data.first_annuity_year
    if (data.case_type !== undefined) payload.case_type = trimToNull(data.case_type)
    if (data.patent_category !== undefined) payload.patent_category = trimToNull(data.patent_category)
    if (data.flow_dir !== undefined) payload.flow_dir = trimToNull(data.flow_dir)
    if (data.applicants !== undefined) payload.applicants = data.applicants
        ?.map((applicant) => ({
            seq: applicant.seq,
            is_first: applicant.is_first ?? false,
            name_cn: trimToNull(applicant.name_cn),
            name_en: trimToNull(applicant.name_en),
            address_cn: trimToNull(applicant.address_cn),
            address_en: trimToNull(applicant.address_en),
            nationality: trimToNull(applicant.nationality),
            certificate_type: trimToNull(applicant.certificate_type),
            certificate_no: trimToNull(applicant.certificate_no),
            official_postcode: trimToNull(applicant.official_postcode),
            official_applicant_kind: trimToNull(applicant.official_applicant_kind),
        }))
        .filter((applicant) =>
            [
                applicant.name_cn,
                applicant.name_en,
                applicant.address_cn,
                applicant.address_en,
                applicant.nationality,
                applicant.certificate_type,
                applicant.certificate_no,
                applicant.official_postcode,
                applicant.official_applicant_kind,
            ].some((value) => value !== null)
        )
    if (data.inventors !== undefined) payload.inventors = data.inventors
        ?.map((inventor) => ({
            seq: inventor.seq,
            name_cn: trimToNull(inventor.name_cn),
            name_en: trimToNull(inventor.name_en),
            nationality: trimToNull(inventor.nationality),
            china_id_no: trimToNull(inventor.china_id_no),
        }))
        .filter((inventor) =>
            [
                inventor.name_cn,
                inventor.name_en,
                inventor.nationality,
                inventor.china_id_no,
            ].some((value) => value !== null)
        )
    if (data.priorities !== undefined) payload.priorities = data.priorities
        ?.map((priority) => ({
            seq: priority.seq,
            country_code: trimToNull(priority.country_code),
            prio_no: trimToNull(priority.prio_no),
            prio_date: trimToNull(priority.prio_date),
        }))
    if (data.bio_deposits !== undefined) payload.bio_deposits = data.bio_deposits
        ?.map((bioDeposit) => ({
            seq: bioDeposit.seq,
            deposit_no: trimToNull(bioDeposit.deposit_no),
            deposit_unit_name: trimToNull(bioDeposit.deposit_unit_name),
            deposit_date: trimToNull(bioDeposit.deposit_date),
            name: trimToNull(bioDeposit.name),
        }))
        .filter((bioDeposit) =>
            [bioDeposit.deposit_no, bioDeposit.deposit_unit_name, bioDeposit.deposit_date, bioDeposit.name].some((value) => value !== null)
        )
    if (data.agent_splits !== undefined) payload.agent_splits = data.agent_splits
        ?.map((agentSplit) => ({
            agent_id: trimToNull(agentSplit.agent_id),
            role: trimToNull(agentSplit.role),
            share_ratio: agentSplit.share_ratio === null || agentSplit.share_ratio === undefined
                ? null
                : agentSplit.share_ratio,
        }))
        .filter((agentSplit) =>
            [agentSplit.agent_id, agentSplit.role, agentSplit.share_ratio].some((value) => value !== null)
        )
    if (data.ro !== undefined) payload.ro = trimToNull(data.ro)
    if (data.isa !== undefined) payload.isa = trimToNull(data.isa)
    if (data.ipea !== undefined) payload.ipea = trimToNull(data.ipea)
    if (data.intl_app_no !== undefined) payload.intl_app_no = trimToNull(data.intl_app_no)
    if (data.intl_app_date !== undefined) payload.intl_app_date = trimToNull(data.intl_app_date)
    if (data.intl_pub_no !== undefined) payload.intl_pub_no = trimToNull(data.intl_pub_no)
    if (data.intl_pub_date !== undefined) payload.intl_pub_date = trimToNull(data.intl_pub_date)
    if (data.intl_pub_lang !== undefined) payload.intl_pub_lang = trimToNull(data.intl_pub_lang)
    if (data.need_iper !== undefined) payload.need_iper = data.need_iper
    if (data.iper_date !== undefined) payload.iper_date = trimToNull(data.iper_date)
    if (data.pct_national_entry_date !== undefined) {
        payload.pct_national_entry_date = trimToNull(data.pct_national_entry_date)
    }
    if (data.original_case_id !== undefined) payload.original_case_id = trimToNull(data.original_case_id)
    if (data.invalid_client_id !== undefined) payload.invalid_client_id = trimToNull(data.invalid_client_id)
    if (data.invalid_patentee !== undefined) payload.invalid_patentee = trimToNull(data.invalid_patentee)
    if (data.invalid_requester !== undefined) payload.invalid_requester = trimToNull(data.invalid_requester)
    if (data.invalid_role !== undefined) payload.invalid_role = trimToNull(data.invalid_role)
    if (data.pub_date !== undefined) payload.pub_date = trimToNull(data.pub_date)
    if (data.pub_no !== undefined) payload.pub_no = trimToNull(data.pub_no)
    if (data.grant_date !== undefined) payload.grant_date = trimToNull(data.grant_date)
    if (data.grant_no !== undefined) payload.grant_no = trimToNull(data.grant_no)
    if (data.patent_no !== undefined) payload.patent_no = trimToNull(data.patent_no)
    if (data.valid_until !== undefined) payload.valid_until = trimToNull(data.valid_until)
    if (data.spec_pages !== undefined) payload.spec_pages = data.spec_pages
    if (data.claim_count !== undefined) payload.claim_count = data.claim_count
    if (data.has_exam_request !== undefined) payload.has_exam_request = data.has_exam_request
    if (data.primary_agent_id !== undefined) {
        payload.primary_agent_id = trimToNull(data.primary_agent_id)
    }
    if (data.second_agent_id !== undefined) {
        payload.second_agent_id = trimToNull(data.second_agent_id)
    }
    if (data.draftor_id !== undefined) payload.draftor_id = trimToNull(data.draftor_id)
    if (data.is_fee_monitor !== undefined) payload.is_fee_monitor = data.is_fee_monitor
    if (data.fee_reduction !== undefined) payload.fee_reduction = trimToNull(data.fee_reduction)
    if (data.applicant_kind !== undefined) payload.applicant_kind = trimToNull(data.applicant_kind)

    return payload
}

/**
 * Get paginated list of cases
 */
export async function getCases(params: CaseListParams = {}): Promise<CaseListResponse> {
    const { page = 1, page_size = 20, ...filters } = params
    // Build clean params — only include non-empty filter values
    const queryParams: Record<string, string | number> = { page, page_size }
    for (const [key, value] of Object.entries(filters)) {
        if (typeof value === 'string') {
            const normalized = value.trim()
            if (normalized) {
                queryParams[key] = normalized
            }
            continue
        }
        if (value !== undefined && value !== null && value !== '') {
            queryParams[key] = String(value)
        }
    }
    const response = await http.get<BackendCaseListResponse>('/cases', {
        params: queryParams
    })

    return {
        page: response.data.page,
        page_size: response.data.page_size,
        total: response.data.total,
        items: response.data.items.map(mapCase),
        summary: {
            total_case_count: response.data.summary?.total_case_count || 0,
            status_counts: response.data.summary?.status_counts || [],
            case_type_counts: response.data.summary?.case_type_counts || [],
            client_counts: (response.data.summary?.client_counts || []).map(item => ({
                key: item.key,
                label: item.label,
                count: item.count,
                case_type_counts: item.case_type_counts || [],
            })),
            country_counts: response.data.summary?.country_counts || [],
            agent_counts: response.data.summary?.agent_counts || [],
            year_trends: response.data.summary?.year_trends || [],
            month_trends: response.data.summary?.month_trends || [],
            granted_count: response.data.summary?.granted_count || 0,
            grant_rate: response.data.summary?.grant_rate ?? null,
            terminated_count: response.data.summary?.terminated_count || 0,
            invalidated_count: response.data.summary?.invalidated_count || 0,
            in_prosecution_count: response.data.summary?.in_prosecution_count || 0,
        },
    }
}

/**
 * Get a single case by ID
 */
export async function getCase(id: string | number): Promise<Case> {
    const response = await http.get<BackendCase>(`/cases/${id}`)
    return mapCase(response.data)
}

export async function getCaseByCaseNo(caseNo: string): Promise<Case> {
    const normalizedCaseNo = caseNo.trim()
    const result = await getCases({ case_no: normalizedCaseNo, page: 1, page_size: 1 })
    const found = result.items.find(item => item.case_no === normalizedCaseNo)
    if (!found) {
        throw new Error('未找到对应案件')
    }
    return getCase(found.id)
}

export async function getCaseIntakeDocumentGate(
    params: CaseIntakeDocumentGateParams
): Promise<CaseDocumentGatePreview> {
    const query = new URLSearchParams()
    query.set('case_type', params.case_type)
    query.set('patent_category', params.patent_category)
    query.set('flow_dir', params.flow_dir)
    if (params.has_exam_request !== undefined) {
        query.set('has_exam_request', String(params.has_exam_request))
    }
    if (params.no_power !== undefined) {
        query.set('no_power', String(params.no_power))
    }
    if (params.has_priority !== undefined) {
        query.set('has_priority', String(params.has_priority))
    }
    for (const documentId of params.source_document_ids || []) {
        query.append('source_document_ids', documentId)
    }

    const response = await http.get<CaseDocumentGatePreview>(
        '/cases/document-gate/intake-preview',
        { params: query }
    )
    return response.data
}

export async function getCaseDocumentGate(caseId: string | number): Promise<CaseDocumentGatePreview> {
    const response = await http.get<CaseDocumentGatePreview>(`/cases/${caseId}/document-gate`)
    return response.data
}

/**
 * Create a new case
 */
export async function createCase(data: CaseCreatePayload): Promise<Case> {
    // Backend expects title_cn (not title) and patent_category
    const payload: Record<string, unknown> = {
        case_no: data.case_no,
        case_type: trimToUndefined(data.case_type) || 'NORMAL',
        client_id: data.client_id,
        title_cn: trimToUndefined(data.title),
        patent_category: trimToUndefined(data.patent_category),
        flow_dir: trimToUndefined(data.flow_dir) || 'CN_DOMESTIC',
        foreign_agent_id: trimToUndefined(data.foreign_agent_id),
        foreign_ref: trimToUndefined(data.foreign_ref),
        from_country: trimToUndefined(data.from_country),
        to_country: trimToUndefined(data.to_country),
        doc_address_id: trimToUndefined(data.doc_address_id),
        bill_address_id: trimToUndefined(data.bill_address_id),
        app_no: trimToUndefined(data.app_no),
        recv_date: trimToUndefined(data.recv_date),
        issue_date: trimToUndefined(data.issue_date),
        cert_no: trimToUndefined(data.cert_no),
        draw_pages: data.draw_pages ?? undefined,
        claim_pages: data.claim_pages ?? undefined,
        manuscript_words: data.manuscript_words ?? undefined,
        discount_rate: trimToUndefined(data.discount_rate),
        no_power: data.no_power ?? undefined,
        no_prio_text: data.no_prio_text ?? undefined,
        require_hk: data.require_hk ?? undefined,
        first_annuity_year: data.first_annuity_year ?? undefined,
        applicants: data.applicants
            ?.map((applicant) => ({
                seq: applicant.seq,
                is_first: applicant.is_first ?? false,
                name_cn: trimToUndefined(applicant.name_cn),
                name_en: trimToUndefined(applicant.name_en),
                address_cn: trimToUndefined(applicant.address_cn),
                address_en: trimToUndefined(applicant.address_en),
                nationality: trimToUndefined(applicant.nationality),
                certificate_type: trimToUndefined(applicant.certificate_type),
                certificate_no: trimToUndefined(applicant.certificate_no),
                official_postcode: trimToUndefined(applicant.official_postcode),
                official_applicant_kind: trimToUndefined(applicant.official_applicant_kind),
            }))
            .filter((applicant) =>
                [
                    applicant.name_cn,
                    applicant.name_en,
                    applicant.address_cn,
                    applicant.address_en,
                    applicant.nationality,
                    applicant.certificate_type,
                    applicant.certificate_no,
                    applicant.official_postcode,
                    applicant.official_applicant_kind,
                ].some((value) => value !== undefined)
            ),
        inventors: data.inventors
            ?.map((inventor) => ({
                seq: inventor.seq,
                name_cn: trimToUndefined(inventor.name_cn),
                name_en: trimToUndefined(inventor.name_en),
                nationality: trimToUndefined(inventor.nationality),
                china_id_no: trimToUndefined(inventor.china_id_no),
            }))
            .filter((inventor) =>
                [
                    inventor.name_cn,
                    inventor.name_en,
                    inventor.nationality,
                    inventor.china_id_no,
                ].some((value) => value !== undefined)
            ),
        priorities: data.priorities?.map((priority) => ({
            seq: priority.seq,
            country_code: trimToUndefined(priority.country_code),
            prio_no: trimToUndefined(priority.prio_no),
            prio_date: trimToUndefined(priority.prio_date),
        })),
        agent_splits: data.agent_splits?.map((agentSplit) => ({
            agent_id: trimToUndefined(agentSplit.agent_id),
            role: trimToUndefined(agentSplit.role),
            share_ratio: agentSplit.share_ratio === null || agentSplit.share_ratio === undefined
                ? null
                : agentSplit.share_ratio,
        })),
        bio_deposits: data.bio_deposits
            ?.map((bioDeposit) => ({
                seq: bioDeposit.seq,
                deposit_no: trimToUndefined(bioDeposit.deposit_no),
                deposit_unit_name: trimToUndefined(bioDeposit.deposit_unit_name),
                deposit_date: trimToUndefined(bioDeposit.deposit_date),
                name: trimToUndefined(bioDeposit.name),
            }))
            .filter((bioDeposit) =>
                [bioDeposit.deposit_no, bioDeposit.deposit_unit_name, bioDeposit.deposit_date, bioDeposit.name].some((value) => value !== undefined)
            ),
        ro: trimToUndefined(data.ro),
        isa: trimToUndefined(data.isa),
        ipea: trimToUndefined(data.ipea),
        intl_app_no: trimToUndefined(data.intl_app_no),
        intl_app_date: trimToUndefined(data.intl_app_date),
        intl_pub_no: trimToUndefined(data.intl_pub_no),
        intl_pub_date: trimToUndefined(data.intl_pub_date),
        intl_pub_lang: trimToUndefined(data.intl_pub_lang),
        need_iper: data.need_iper ?? undefined,
        iper_date: trimToUndefined(data.iper_date),
        pct_national_entry_date: trimToUndefined(data.pct_national_entry_date),
        original_case_id: trimToUndefined(data.original_case_id),
        invalid_client_id: trimToUndefined(data.invalid_client_id),
        invalid_patentee: trimToUndefined(data.invalid_patentee),
        invalid_requester: trimToUndefined(data.invalid_requester),
        invalid_role: trimToUndefined(data.invalid_role),
        // A3 fields
        pub_date: trimToUndefined(data.pub_date),
        pub_no: trimToUndefined(data.pub_no),
        grant_date: trimToUndefined(data.grant_date),
        grant_no: trimToUndefined(data.grant_no),
        patent_no: trimToUndefined(data.patent_no),
        valid_until: trimToUndefined(data.valid_until),
        spec_pages: data.spec_pages ?? undefined,
        claim_count: data.claim_count ?? undefined,
        has_exam_request: data.has_exam_request ?? undefined,
        primary_agent_id: trimToUndefined(data.primary_agent_id),
        second_agent_id: trimToUndefined(data.second_agent_id),
        draftor_id: trimToUndefined(data.draftor_id),
        is_fee_monitor: data.is_fee_monitor ?? undefined,
        fee_reduction: trimToUndefined(data.fee_reduction),
        applicant_kind: trimToUndefined(data.applicant_kind),
    }
    const response = await http.post<BackendCase>('/cases', payload)
    return mapCase(response.data)
}

/**
 * Update an existing case
 */
export async function updateCase(id: string | number, data: CaseUpdatePayload): Promise<Case> {
    const response = await http.put<BackendCase>(`/cases/${id}`, toUpdatePayload(data))
    return mapCase(response.data)
}

/**
 * Limited edit for a case (restricted fields)
 */
export async function limitedEditCase(id: string | number, data: CaseLimitedEditPayload): Promise<Case> {
    const response = await http.post<BackendCase>(`/cases/${id}/limited-edit`, data)
    return mapCase(response.data)
}

export async function getBatchFilingCandidates(
    params: CaseBatchFilingQueryParams = {}
): Promise<Pagination<CaseBatchFilingCandidate>> {
    const queryParams: Record<string, string | number> = {
        page: params.page ?? 1,
        page_size: params.page_size ?? 20,
        status: params.status ?? 'NOT_FILED',
    }
    for (const [key, value] of Object.entries(params)) {
        if (value !== undefined && value !== null && value !== '') {
            queryParams[key] = value
        }
    }
    const response = await http.get<Pagination<BackendCaseBatchFilingCandidate>>(
        '/cases/batch-filing/candidates',
        { params: queryParams }
    )
    return {
        ...response.data,
        items: response.data.items.map(mapBatchFilingCandidate),
    }
}

export async function submitBatchFiling(
    payload: CaseBatchFilingActionPayload
): Promise<CaseBatchFilingActionResult> {
    const response = await http.post<CaseBatchFilingActionResult>(
        '/cases/batch-filing/submit',
        payload
    )
    return response.data
}
