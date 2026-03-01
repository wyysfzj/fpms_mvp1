import { http } from './http'

interface AuthMeResponse {
    permissions?: unknown
}

function isStringArray(value: unknown): value is string[] {
    return Array.isArray(value) && value.every((item) => typeof item === 'string')
}

/**
 * Fetch current user's permissions from backend-authoritative endpoint.
 */
export async function getCurrentUserPermissions(): Promise<string[]> {
    const response = await http.get<AuthMeResponse>('/auth/me')
    const { permissions } = response.data

    if (!isStringArray(permissions)) {
        throw new Error('AUTH_ME_PERMISSIONS_INVALID')
    }

    return permissions
}
