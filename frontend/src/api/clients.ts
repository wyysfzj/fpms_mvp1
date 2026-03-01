import { http } from './http'
import type { Pagination } from './types'
import type {
    Client, ClientCreatePayload, ClientListParams, ClientUpdatePayload,
    ClientAddress, ClientAddressCreatePayload, ClientAddressUpdatePayload,
    ClientContact, ClientContactCreatePayload, ClientContactUpdatePayload,
} from './clients.types'

interface BackendClient {
    id: string
    client_code?: string | null
    name_cn?: string | null
    name_en?: string | null
    email?: string | null
    client_type?: string | null
    default_currency?: string | null
    is_active?: boolean | null
    created_at?: string
    updated_at?: string
}

function mapClient(input: BackendClient): Client {
    return {
        id: input.id,
        name: input.name_cn || input.name_en || '',
        name_cn: input.name_cn || undefined,
        name_en: input.name_en || undefined,
        client_code: input.client_code,
        client_type: input.client_type,
        default_currency: input.default_currency,
        email: input.email || undefined,
        is_active: input.is_active ?? true,
        created_at: input.created_at,
        updated_at: input.updated_at,
    }
}

function toCreatePayload(data: ClientCreatePayload): Record<string, unknown> {
    return {
        client_code: data.client_code || undefined,
        name_cn: data.name,
        name_en: data.name_en || undefined,
        client_type: data.client_type || undefined,
        default_currency: data.default_currency || 'CNY',
        email: data.email || undefined,
        is_active: true,
    }
}

function toUpdatePayload(data: ClientUpdatePayload): Record<string, unknown> {
    const payload: Record<string, unknown> = {}

    if (data.client_code !== undefined) payload.client_code = data.client_code || null
    if (data.name !== undefined) payload.name_cn = data.name || null
    if (data.name_en !== undefined) payload.name_en = data.name_en || null
    if (data.client_type !== undefined) payload.client_type = data.client_type || null
    if (data.default_currency !== undefined) payload.default_currency = data.default_currency || null
    if (data.email !== undefined) payload.email = data.email || null

    return payload
}

/**
 * Get paginated list of clients
 */
export async function getClients(params: ClientListParams = {}): Promise<Pagination<Client>> {
    const { page = 1, page_size = 20 } = params
    const response = await http.get<Pagination<BackendClient>>('/clients', {
        params: { page, page_size }
    })

    return {
        ...response.data,
        items: response.data.items.map(mapClient),
    }
}

/**
 * Get a single client by ID
 */
export async function getClient(id: string | number): Promise<Client> {
    const response = await http.get<BackendClient>(`/clients/${id}`)
    return mapClient(response.data)
}

/**
 * Create a new client
 */
export async function createClient(data: ClientCreatePayload): Promise<Client> {
    const response = await http.post<BackendClient>('/clients', toCreatePayload(data))
    return mapClient(response.data)
}

/**
 * Update an existing client
 */
export async function updateClient(id: string | number, data: ClientUpdatePayload): Promise<Client> {
    const response = await http.put<BackendClient>(`/clients/${id}`, toUpdatePayload(data))
    return mapClient(response.data)
}

/**
 * Deactivate a client
 */
export async function deactivateClient(id: string | number): Promise<Client> {
    const response = await http.put<BackendClient>(`/clients/${id}/deactivate`)
    return mapClient(response.data)
}

// ── Address CRUD ──────────────────────────────────

export async function getClientAddresses(clientId: string): Promise<ClientAddress[]> {
    const response = await http.get<ClientAddress[]>(`/clients/${clientId}/addresses`)
    return response.data
}

export async function createClientAddress(
    clientId: string,
    data: ClientAddressCreatePayload
): Promise<ClientAddress> {
    const response = await http.post<ClientAddress>(`/clients/${clientId}/addresses`, data)
    return response.data
}

export async function updateClientAddress(
    clientId: string,
    addressId: string,
    data: ClientAddressUpdatePayload
): Promise<ClientAddress> {
    const response = await http.put<ClientAddress>(
        `/clients/${clientId}/addresses/${addressId}`, data
    )
    return response.data
}

export async function deleteClientAddress(clientId: string, addressId: string): Promise<void> {
    await http.delete(`/clients/${clientId}/addresses/${addressId}`)
}

// ── Contact CRUD ──────────────────────────────────

export async function getClientContacts(clientId: string): Promise<ClientContact[]> {
    const response = await http.get<ClientContact[]>(`/clients/${clientId}/contacts`)
    return response.data
}

export async function createClientContact(
    clientId: string,
    data: ClientContactCreatePayload
): Promise<ClientContact> {
    const response = await http.post<ClientContact>(`/clients/${clientId}/contacts`, data)
    return response.data
}

export async function updateClientContact(
    clientId: string,
    contactId: string,
    data: ClientContactUpdatePayload
): Promise<ClientContact> {
    const response = await http.put<ClientContact>(
        `/clients/${clientId}/contacts/${contactId}`, data
    )
    return response.data
}

export async function deleteClientContact(clientId: string, contactId: string): Promise<void> {
    await http.delete(`/clients/${clientId}/contacts/${contactId}`)
}
