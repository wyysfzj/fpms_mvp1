import { http } from './http'
import type { Pagination } from './types'
import type {
    CalcMode,
    ApplyFeeDraftGeneratePayload,
    FeeDraftCreatePayload,
    FeeDraftDetail,
    FeeDraftListItem,
    FeeDraftListResponse,
    FeeDraftListParams,
    FeeDraftReportSummary,
    FeeDraftUpdatePayload,
    FeeItem,
    FeeItemCreatePayload,
    FeeItemUpdatePayload,
    FeeRate,
    FeeRateCreatePayload,
    FeeRateListParams,
    FeeRateUpdatePayload,
} from './fees.types'

interface BackendFeeRate {
    id: string
    fee_code: string
    fee_name: string
    fee_type: string
    currency?: string | null
    default_amount?: string | number | null
    enabled?: boolean
    rate_group?: string | null
    country_code?: string | null
    case_type?: string | null
    patent_category?: string | null
    calc_mode?: string | null
    calc_params?: string | null
    allow_reduction?: boolean | null
    effective_from?: string | null
    effective_to?: string | null
}

interface BackendFeeItem {
    id: string
    draft_id: string
    case_id?: string | null
    rate_id: string
    fee_code?: string | null
    fee_name?: string | null
    fee_type?: string | null
    quantity?: string | number | null
    unit_price?: string | number | null
    amount?: string | number | null
    remark?: string | null
}

interface BackendFeeDraftListItem {
    id: string
    case_id: string
    case_no?: string | null
    client_id?: string | null
    client_name?: string | null
    currency: string
    status: 'OPEN' | 'LOCKED'
    amount: string | number
}

interface BackendFeeDraftReportSummary {
    total_draft_count: number
    service_fee_amount: string | number
    government_fee_amount: string | number
    income_amount: string | number
    billed_amount?: string | number
    received_amount?: string | number
    unpaid_balance_amount?: string | number
    partially_received_bill_count?: number
    client_amounts?: BackendFeeDraftGroupedAmount[]
    case_type_amounts?: BackendFeeDraftGroupedAmount[]
    country_amounts?: BackendFeeDraftGroupedAmount[]
    agent_service_amounts?: BackendFeeDraftAgentServiceAmount[]
    year_amounts?: BackendFeeDraftTrendAmount[]
    month_amounts?: BackendFeeDraftTrendAmount[]
}

interface BackendFeeDraftGroupedAmount {
    key: string
    label: string
    draft_count: number
    service_fee_amount: string | number
    government_fee_amount: string | number
    income_amount: string | number
}

interface BackendFeeDraftAgentServiceAmount {
    key: string
    label: string
    draft_count: number
    service_fee_amount: string | number
}

interface BackendFeeDraftTrendAmount {
    key: string
    label: string
    draft_count: number
    service_fee_amount: string | number
    government_fee_amount: string | number
    income_amount: string | number
    draft_type_amounts?: BackendFeeDraftGroupedAmount[]
}

interface BackendFeeDraftListResponse extends Pagination<BackendFeeDraftListItem> {
    summary: BackendFeeDraftReportSummary
}

interface BackendFeeDraftDetail {
    id: string
    case_id: string
    case_no?: string | null
    client_id?: string | null
    client_name?: string | null
    draft_type: string
    currency: string
    status: 'OPEN' | 'LOCKED'
    total_gov?: string | number
    total_service?: string | number
    total_misc?: string | number
    amount?: string | number
    created_at?: string
    updated_at?: string
}

function mapFeeRate(input: BackendFeeRate): FeeRate {
    return {
        id: input.id,
        name: input.fee_name || input.fee_code,
        rate: Number(input.default_amount || 0),
        currency: input.currency || 'CNY',
        fee_code: input.fee_code,
        fee_type: input.fee_type,
        enabled: input.enabled,
        rate_group: input.rate_group ?? null,
        country_code: input.country_code ?? null,
        case_type: input.case_type ?? null,
        patent_category: input.patent_category ?? null,
        calc_mode: (input.calc_mode as CalcMode) ?? null,
        calc_params: input.calc_params ?? null,
        allow_reduction: input.allow_reduction ?? null,
        effective_from: input.effective_from ?? null,
        effective_to: input.effective_to ?? null,
    }
}

function mapFeeItem(input: BackendFeeItem): FeeItem {
    return {
        id: input.id,
        draft_id: input.draft_id,
        case_id: input.case_id ?? null,
        rate_id: input.rate_id,
        fee_code: input.fee_code ?? null,
        fee_name: input.fee_name ?? null,
        fee_type: input.fee_type ?? null,
        description: input.remark || input.fee_name || input.fee_code || '',
        quantity: Number(input.quantity || 0),
        unit_price: Number(input.unit_price || 0),
        amount: Number(input.amount || 0),
    }
}

function mapFeeDraftListItem(input: BackendFeeDraftListItem): FeeDraftListItem {
    return {
        id: input.id,
        case_id: input.case_id,
        case_no: input.case_no ?? null,
        client_id: input.client_id ?? null,
        client_name: input.client_name ?? null,
        currency: input.currency,
        status: input.status,
        amount: Number(input.amount || 0),
    }
}

function mapFeeDraftDetail(input: BackendFeeDraftDetail): FeeDraftDetail {
    return {
        id: input.id,
        case_id: input.case_id,
        case_no: input.case_no ?? null,
        client_id: input.client_id ?? null,
        client_name: input.client_name ?? null,
        draft_type: input.draft_type,
        currency: input.currency,
        status: input.status,
        total_gov: input.total_gov != null ? Number(input.total_gov) : undefined,
        total_service: input.total_service != null ? Number(input.total_service) : undefined,
        total_misc: input.total_misc != null ? Number(input.total_misc) : undefined,
        amount: input.amount != null ? Number(input.amount) : undefined,
        created_at: input.created_at,
        updated_at: input.updated_at,
    }
}

function mapFeeDraftReportSummary(input: BackendFeeDraftReportSummary): FeeDraftReportSummary {
    return {
        total_draft_count: Number(input.total_draft_count || 0),
        service_fee_amount: Number(input.service_fee_amount || 0),
        government_fee_amount: Number(input.government_fee_amount || 0),
        income_amount: Number(input.income_amount || 0),
        billed_amount: Number(input.billed_amount || 0),
        received_amount: Number(input.received_amount || 0),
        unpaid_balance_amount: Number(input.unpaid_balance_amount || 0),
        partially_received_bill_count: Number(input.partially_received_bill_count || 0),
        client_amounts: (input.client_amounts || []).map(mapFeeDraftGroupedAmount),
        case_type_amounts: (input.case_type_amounts || []).map(mapFeeDraftGroupedAmount),
        country_amounts: (input.country_amounts || []).map(mapFeeDraftGroupedAmount),
        agent_service_amounts: (input.agent_service_amounts || []).map(mapFeeDraftAgentServiceAmount),
        year_amounts: (input.year_amounts || []).map(mapFeeDraftTrendAmount),
        month_amounts: (input.month_amounts || []).map(mapFeeDraftTrendAmount),
    }
}

function mapFeeDraftGroupedAmount(input: BackendFeeDraftGroupedAmount) {
    return {
        key: input.key,
        label: input.label,
        draft_count: Number(input.draft_count || 0),
        service_fee_amount: Number(input.service_fee_amount || 0),
        government_fee_amount: Number(input.government_fee_amount || 0),
        income_amount: Number(input.income_amount || 0),
    }
}

function mapFeeDraftAgentServiceAmount(input: BackendFeeDraftAgentServiceAmount) {
    return {
        key: input.key,
        label: input.label,
        draft_count: Number(input.draft_count || 0),
        service_fee_amount: Number(input.service_fee_amount || 0),
    }
}

function mapFeeDraftTrendAmount(input: BackendFeeDraftTrendAmount) {
    return {
        key: input.key,
        label: input.label,
        draft_count: Number(input.draft_count || 0),
        service_fee_amount: Number(input.service_fee_amount || 0),
        government_fee_amount: Number(input.government_fee_amount || 0),
        income_amount: Number(input.income_amount || 0),
        draft_type_amounts: (input.draft_type_amounts || []).map(mapFeeDraftGroupedAmount),
    }
}

function buildFeeCode(name: string): string {
    const base = name
        .trim()
        .toUpperCase()
        .replace(/[^A-Z0-9]+/g, '_')
        .replace(/^_+|_+$/g, '')
        .slice(0, 24)

    const suffix = String(Date.now()).slice(-6)
    return `${base || 'RATE'}_${suffix}`
}

function toFeeRateCreatePayload(data: FeeRateCreatePayload): Record<string, unknown> {
    return {
        fee_code: data.fee_code || buildFeeCode(data.name),
        fee_name: data.name,
        fee_type: data.fee_type || 'GOV',
        currency: data.currency || 'CNY',
        default_amount: data.rate,
        enabled: true,
        ...(data.rate_group !== undefined && { rate_group: data.rate_group }),
        ...(data.country_code !== undefined && { country_code: data.country_code }),
        ...(data.case_type !== undefined && { case_type: data.case_type }),
        ...(data.patent_category !== undefined && { patent_category: data.patent_category }),
        ...(data.calc_mode !== undefined && { calc_mode: data.calc_mode }),
        ...(data.calc_params !== undefined && { calc_params: data.calc_params }),
        ...(data.allow_reduction !== undefined && { allow_reduction: data.allow_reduction }),
        ...(data.effective_from !== undefined && { effective_from: data.effective_from }),
        ...(data.effective_to !== undefined && { effective_to: data.effective_to }),
    }
}

function toFeeRateUpdatePayload(data: FeeRateUpdatePayload): Record<string, unknown> {
    const payload: Record<string, unknown> = {}

    if (data.name !== undefined) payload.fee_name = data.name
    if (data.fee_type !== undefined) payload.fee_type = data.fee_type
    if (data.currency !== undefined) payload.currency = data.currency
    if (data.rate !== undefined) payload.default_amount = data.rate
    if (data.enabled !== undefined) payload.enabled = data.enabled
    if (data.rate_group !== undefined) payload.rate_group = data.rate_group
    if (data.country_code !== undefined) payload.country_code = data.country_code
    if (data.case_type !== undefined) payload.case_type = data.case_type
    if (data.patent_category !== undefined) payload.patent_category = data.patent_category
    if (data.calc_mode !== undefined) payload.calc_mode = data.calc_mode
    if (data.calc_params !== undefined) payload.calc_params = data.calc_params
    if (data.allow_reduction !== undefined) payload.allow_reduction = data.allow_reduction
    if (data.effective_from !== undefined) payload.effective_from = data.effective_from
    if (data.effective_to !== undefined) payload.effective_to = data.effective_to

    return payload
}

/**
 * Get paginated list of fee rates
 */
export async function getFeeRates(params: FeeRateListParams = {}): Promise<Pagination<FeeRate>> {
    const { page = 1, page_size = 50 } = params
    const response = await http.get<Pagination<BackendFeeRate>>('/fees/rates', {
        params: { page, page_size }
    })

    return {
        ...response.data,
        items: response.data.items.map(mapFeeRate),
    }
}

/**
 * Create a new fee rate
 */
export async function createFeeRate(data: FeeRateCreatePayload): Promise<FeeRate> {
    const response = await http.post<BackendFeeRate>('/fees/rates', toFeeRateCreatePayload(data))
    return mapFeeRate(response.data)
}

/**
 * Update an existing fee rate
 */
export async function updateFeeRate(id: string, data: FeeRateUpdatePayload): Promise<FeeRate> {
    const response = await http.put<BackendFeeRate>(`/fees/rates/${id}`, toFeeRateUpdatePayload(data))
    return mapFeeRate(response.data)
}

// Fee Draft Functions

/**
 * Get paginated list of fee drafts
 */
export async function getFeeDrafts(
    params: FeeDraftListParams = {},
): Promise<FeeDraftListResponse> {
    const {
        page = 1,
        page_size = 20,
        case_id,
        client_id,
        status,
        draft_status,
        fee_type,
        currency,
        date_from,
        date_to,
        bill_status,
    } = params
    const response = await http.get<BackendFeeDraftListResponse>('/fees/drafts', {
        params: {
            page,
            page_size,
            case_id,
            client_id,
            status,
            draft_status,
            fee_type,
            currency,
            date_from,
            date_to,
            bill_status,
        }
    })
    return {
        ...response.data,
        items: response.data.items.map(mapFeeDraftListItem),
        summary: mapFeeDraftReportSummary(response.data.summary),
    }
}

/**
 * Get a single fee draft by ID
 */
export async function getFeeDraft(id: string): Promise<FeeDraftDetail> {
    const response = await http.get<BackendFeeDraftDetail>(`/fees/drafts/${id}`)
    return mapFeeDraftDetail(response.data)
}

/**
 * Create a new fee draft
 */
export async function createFeeDraft(data: FeeDraftCreatePayload): Promise<FeeDraftDetail> {
    const response = await http.post<BackendFeeDraftDetail>('/fees/drafts', data)
    return mapFeeDraftDetail(response.data)
}

/**
 * Generate an application fee draft from case data and configured fee rates.
 */
export async function generateApplyFeeDraft(data: ApplyFeeDraftGeneratePayload): Promise<FeeDraftDetail> {
    const response = await http.post<BackendFeeDraftDetail>('/fees/drafts/apply-fee/generate', {
        case_id: data.case_id,
        currency: data.currency || 'CNY',
        discount_rate: data.discount_rate ?? undefined,
    })
    return mapFeeDraftDetail(response.data)
}

/**
 * Update an existing fee draft
 */
export async function updateFeeDraft(id: string, data: FeeDraftUpdatePayload): Promise<FeeDraftDetail> {
    const response = await http.put<BackendFeeDraftDetail>(`/fees/drafts/${id}`, data)
    return mapFeeDraftDetail(response.data)
}

// Fee Item Functions

/**
 * Get items for a fee draft
 */
export async function getFeeDraftItems(draftId: string): Promise<FeeItem[]> {
    const response = await http.get<BackendFeeItem[]>(`/fees/drafts/${draftId}/items`)
    return response.data.map(mapFeeItem)
}

/**
 * Create a new fee item in a draft
 */
export async function createFeeItem(draftId: string, data: FeeItemCreatePayload): Promise<FeeItem> {
    let rateId = data.rate_id
    if (!rateId) {
        const rates = await getFeeRates({ page: 1, page_size: 1 })
        rateId = rates.items[0]?.id
    }
    if (!rateId) {
        throw {
            status: 409,
            code: 'MISSING_CONFIGURATION',
            message: 'No fee rate available. Create a fee rate before adding draft items.',
        }
    }

    const response = await http.post<BackendFeeItem>(`/fees/drafts/${draftId}/items`, {
        rate_id: rateId,
        quantity: data.quantity,
        unit_price: data.unit_price,
        remark: data.description || undefined,
    })
    return mapFeeItem(response.data)
}

/**
 * Update an existing fee item
 */
export async function updateFeeItem(draftId: string, itemId: string, data: FeeItemUpdatePayload): Promise<FeeItem> {
    const response = await http.put<BackendFeeItem>(`/fees/drafts/${draftId}/items/${itemId}`, {
        quantity: data.quantity,
        unit_price: data.unit_price,
        remark: data.description || undefined,
    })
    return mapFeeItem(response.data)
}

/**
 * Delete a fee item
 */
export async function deleteFeeItem(itemId: string): Promise<void> {
    await http.delete(`/fees/items/${itemId}`)
}

// Fee Draft Lock/Unlock

/**
 * Lock a fee draft (prevents editing)
 */
export async function lockFeeDraft(draftId: string): Promise<FeeDraftDetail> {
    const response = await http.post<FeeDraftDetail>(`/fees/drafts/${draftId}/lock`)
    return response.data
}

/**
 * Unlock a fee draft (allows editing)
 */
export async function unlockFeeDraft(draftId: string): Promise<FeeDraftDetail> {
    const response = await http.post<FeeDraftDetail>(`/fees/drafts/${draftId}/unlock`)
    return response.data
}
