/**
 * API Types for FPMS Frontend
 */

/**
 * Backend error envelope format
 */
export interface ErrorEnvelope {
    error: {
        code: string
        message: string
        details?: Record<string, unknown>
    }
}

/**
 * Pagination response format
 */
export interface Pagination<T> {
    items: T[]
    page: number
    page_size: number
    total: number
}

/**
 * Normalized API error for frontend consumption
 */
export interface ApiError {
    status: number
    code: string
    message: string
    details?: Record<string, unknown>
    requestId?: string
}

/**
 * Auth response from login endpoint
 */
export interface AuthResponse {
    access_token: string
    token_type: string
}
