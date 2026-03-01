import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { http } from '../api/http'
import { getCurrentUserPermissions } from '../api/auth'
import type { AuthResponse } from '../api/types'

const TOKEN_KEY = 'fpms_token'

export const useAuthStore = defineStore('auth', () => {
    // State: hydrate from localStorage
    const token = ref<string | null>(localStorage.getItem(TOKEN_KEY))

    // Permissions: null means not loaded yet, empty array means no perms
    const perms = ref<string[] | null>(null)
    const permissionsLoaded = ref(false)
    const permissionsSource = ref<'backend' | 'fallback' | null>(null)

    // Getters
    const isAuthenticated = computed(() => !!token.value)

    /**
     * Check if user has a specific permission
     * Fail closed until permissions are loaded.
     */
    function hasPermission(perm: string): boolean {
        if (!permissionsLoaded.value || perms.value === null) return false
        return perms.value.includes(perm)
    }

    /**
     * Check if user has any of the required permissions
     * Empty requirement remains public; non-empty requirement fails closed
     * until permissions are loaded.
     */
    function hasAnyPermission(requiredPerms: string[]): boolean {
        if (!requiredPerms || requiredPerms.length === 0) return true
        if (!permissionsLoaded.value || perms.value === null) return false
        const currentPerms = perms.value
        return requiredPerms.some((p) => currentPerms.includes(p))
    }

    /**
     * Pull permissions from backend-authoritative source.
     * If unavailable (e.g., endpoint missing), fall back to explicit deny-all.
     */
    async function loadPermissions(): Promise<void> {
        permissionsLoaded.value = false
        perms.value = null
        permissionsSource.value = null

        try {
            const backendPerms = await getCurrentUserPermissions()
            perms.value = Array.from(new Set(backendPerms))
            permissionsSource.value = 'backend'
        } catch {
            // Explicit non-permissive fallback.
            perms.value = []
            permissionsSource.value = 'fallback'
        } finally {
            permissionsLoaded.value = true
        }
    }

    // Actions
    async function login(username: string, password: string): Promise<void> {
        const { data } = await http.post<AuthResponse>('/auth/login', { username, password })
        token.value = data.access_token
        localStorage.setItem(TOKEN_KEY, data.access_token)
        await loadPermissions()
    }

    function logout(): void {
        token.value = null
        perms.value = null
        permissionsLoaded.value = false
        permissionsSource.value = null
        localStorage.removeItem(TOKEN_KEY)
    }

    // Allow external sync (e.g., after 401 clears localStorage)
    function syncFromStorage(): void {
        token.value = localStorage.getItem(TOKEN_KEY)
        if (!token.value) {
            perms.value = null
            permissionsLoaded.value = false
            permissionsSource.value = null
        }
    }

    // Allow setting perms from outside (e.g., from /me endpoint)
    function setPerms(newPerms: string[]): void {
        perms.value = Array.from(new Set(newPerms))
        permissionsLoaded.value = true
        permissionsSource.value = 'backend'
    }

    return {
        token,
        perms,
        permissionsLoaded,
        permissionsSource,
        isAuthenticated,
        hasPermission,
        hasAnyPermission,
        loadPermissions,
        login,
        logout,
        syncFromStorage,
        setPerms,
    }
})
