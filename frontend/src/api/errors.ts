import type { AxiosError } from 'axios'
import type { ApiError, ErrorEnvelope } from './types'

/**
 * Normalize axios errors to a consistent ApiError format
 */
export function normalizeApiError(error: AxiosError<ErrorEnvelope>): ApiError {
    const status = error.response?.status ?? 0
    const requestId = error.response?.headers?.['x-request-id'] as string | undefined

    // Try to extract from backend error envelope
    const envelope = error.response?.data?.error
    if (envelope) {
        return {
            status,
            code: envelope.code,
            message: envelope.message,
            details: envelope.details,
            requestId,
        }
    }

    // Fallback for network errors or non-envelope responses
    return {
        status,
        code: 'UNKNOWN_ERROR',
        message: error.message || 'An unexpected error occurred',
        requestId,
    }
}

/**
 * Field error structure
 */
export interface FieldError {
    field: string
    messages: string[]
}

/**
 * Map backend 422 details to field-level errors
 * Backend may return details as:
 * - { "field_name": "error message" }
 * - { "field_name": ["error1", "error2"] }
 * - { "errors": [{ "loc": ["body", "field"], "msg": "..." }] } (Pydantic style)
 */
export function mapFieldErrors(details?: Record<string, unknown>): Map<string, string[]> {
    const fieldErrors = new Map<string, string[]>()

    if (!details) return fieldErrors

    // Handle Pydantic validation errors
    if (Array.isArray(details.errors)) {
        for (const err of details.errors) {
            if (typeof err === 'object' && err !== null) {
                const loc = (err as { loc?: unknown[] }).loc
                const msg = (err as { msg?: string }).msg
                if (Array.isArray(loc) && typeof msg === 'string') {
                    // Take last element of loc as field name
                    const field = String(loc[loc.length - 1])
                    const existing = fieldErrors.get(field) || []
                    existing.push(msg)
                    fieldErrors.set(field, existing)
                }
            }
        }
        return fieldErrors
    }

    // Handle simple key-value or key-array format
    for (const [key, value] of Object.entries(details)) {
        if (key === 'required_perm') continue // Skip special keys

        if (typeof value === 'string') {
            fieldErrors.set(key, [value])
        } else if (Array.isArray(value)) {
            fieldErrors.set(key, value.filter(v => typeof v === 'string') as string[])
        }
    }

    return fieldErrors
}
