/**
 * Client API Types
 */

export interface Client {
    id: string
    name: string
    name_cn?: string
    name_en?: string
    client_code?: string | null
    client_type?: string | null
    default_currency?: string | null
    email?: string
    is_active: boolean
    created_at?: string
    updated_at?: string
}

export interface ClientListParams {
    page?: number
    page_size?: number
}

export interface ClientCreatePayload {
    name: string
    name_en?: string
    client_code?: string
    client_type?: string
    default_currency?: string
    email?: string
}

export interface ClientUpdatePayload {
    name?: string
    name_en?: string
    client_code?: string
    client_type?: string
    default_currency?: string
    email?: string
}

// ── Address types ──────────────────────────────────

export interface ClientAddress {
    id: string
    client_id: string
    address_type: string
    address_line1: string | null
    address_line2: string | null
    city: string | null
    province: string | null
    postal_code: string | null
    country_code: string | null
    is_default: boolean
    created_at: string
    updated_at: string
}

export interface ClientAddressCreatePayload {
    address_type?: string
    address_line1?: string
    address_line2?: string
    city?: string
    province?: string
    postal_code?: string
    country_code?: string
    is_default?: boolean
}

export interface ClientAddressUpdatePayload {
    address_type?: string
    address_line1?: string
    address_line2?: string
    city?: string
    province?: string
    postal_code?: string
    country_code?: string
    is_default?: boolean
}

// ── Contact types ──────────────────────────────────

export interface ClientContact {
    id: string
    client_id: string
    contact_name: string
    title: string | null
    phone: string | null
    mobile: string | null
    email: string | null
    is_primary: boolean
    created_at: string
    updated_at: string
}

export interface ClientContactCreatePayload {
    contact_name: string
    title?: string
    phone?: string
    mobile?: string
    email?: string
    is_primary?: boolean
}

export interface ClientContactUpdatePayload {
    contact_name?: string
    title?: string
    phone?: string
    mobile?: string
    email?: string
    is_primary?: boolean
}
