import axios from 'axios'
import type { AxiosError } from 'axios'
import { normalizeApiError } from './errors'
import type { ErrorEnvelope } from './types'
import { installDemoUiObserver } from '../modules/demo/demoUiSession'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

export const http = axios.create({
  baseURL,
})

installDemoUiObserver(http)

// Request interceptor: inject Authorization header
http.interceptors.request.use((config) => {
  const token = localStorage.getItem('fpms_token')
  if (token) {
    config.headers = config.headers || {}
    config.headers['Authorization'] = `Bearer ${token}`
  }
  return config
})

// Response interceptor: normalize errors and handle 401/403
http.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ErrorEnvelope>) => {
    const normalized = normalizeApiError(error)

    // On 401, clear token and dispatch unauthorized event
    if (normalized.status === 401) {
      localStorage.removeItem('fpms_token')
      window.dispatchEvent(new CustomEvent('fpms:unauthorized'))
    }

    // On 403, dispatch forbidden event with details
    if (normalized.status === 403) {
      const requiredPerm = normalized.details?.required_perm as string | undefined
      window.dispatchEvent(new CustomEvent('fpms:forbidden', {
        detail: {
          requiredPerm,
          message: normalized.message,
          requestId: normalized.requestId,
        }
      }))
    }

    return Promise.reject(normalized)
  }
)
