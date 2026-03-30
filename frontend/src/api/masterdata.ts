import { http } from './http'
import type { Pagination } from './types'
import type {
    Country,
    CountryCreatePayload,
    CountryListParams,
    CountryUpdatePayload,
} from './masterdata.types'

interface BackendCountry {
    id: string
    code: string
    name_cn: string
    name_en?: string | null
    is_active?: boolean | null
}

function mapCountry(input: BackendCountry): Country {
    return {
        id: input.id,
        code: input.code,
        name_cn: input.name_cn,
        name_en: input.name_en || undefined,
        is_active: input.is_active ?? true,
    }
}

function normalizeOptionalText(value?: string): string | undefined {
    const trimmed = value?.trim()
    return trimmed ? trimmed : undefined
}

function normalizeNullableText(value?: string): string | null {
    const trimmed = value?.trim()
    return trimmed ? trimmed : null
}

function toCreatePayload(data: CountryCreatePayload): Record<string, unknown> {
    return {
        code: data.code.trim(),
        name_cn: data.name_cn.trim(),
        name_en: normalizeOptionalText(data.name_en),
        is_active: data.is_active ?? true,
    }
}

function toUpdatePayload(data: CountryUpdatePayload): Record<string, unknown> {
    const payload: Record<string, unknown> = {}

    if (data.code !== undefined) payload.code = data.code.trim()
    if (data.name_cn !== undefined) payload.name_cn = data.name_cn.trim()
    if (data.name_en !== undefined) payload.name_en = normalizeNullableText(data.name_en)
    if (data.is_active !== undefined) payload.is_active = data.is_active

    return payload
}

export async function getCountries(params: CountryListParams = {}): Promise<Pagination<Country>> {
    const { page = 1, page_size = 20, q, is_active } = params
    const response = await http.get<Pagination<BackendCountry>>('/countries', {
        params: {
            page,
            page_size,
            q: q?.trim() || undefined,
            is_active,
        },
    })

    return {
        ...response.data,
        items: response.data.items.map(mapCountry),
    }
}

export async function createCountry(data: CountryCreatePayload): Promise<Country> {
    const response = await http.post<BackendCountry>('/countries', toCreatePayload(data))
    return mapCountry(response.data)
}

export async function updateCountry(id: string | number, data: CountryUpdatePayload): Promise<Country> {
    const response = await http.put<BackendCountry>(`/countries/${id}`, toUpdatePayload(data))
    return mapCountry(response.data)
}

export async function deactivateCountry(id: string | number): Promise<void> {
    await http.put(`/countries/${id}/deactivate`)
}
