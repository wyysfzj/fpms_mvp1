/**
 * Country masterdata API types
 */

export interface Country {
    id: string
    code: string
    name_cn: string
    name_en?: string
    is_active: boolean
}

export interface CountryListParams {
    page?: number
    page_size?: number
    q?: string
    is_active?: boolean
}

export interface CountryCreatePayload {
    code: string
    name_cn: string
    name_en?: string
    is_active?: boolean
}

export interface CountryUpdatePayload {
    code?: string
    name_cn?: string
    name_en?: string
    is_active?: boolean
}
