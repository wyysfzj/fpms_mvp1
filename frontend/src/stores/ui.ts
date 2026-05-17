import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { NavMode } from '../constants/menu'

export type UIMode = 'work' | 'immersive'
export type SidebarGroupCollapseState = Record<string, boolean>

const STORAGE_KEY = 'fpms_ui_mode'
const NAV_MODE_STORAGE_KEY = 'fpms_nav_mode'
const SIDEBAR_COLLAPSED_STORAGE_KEY = 'fpms_sidebar_collapsed'
const SIDEBAR_GROUP_COLLAPSED_STORAGE_KEY = 'fpms_sidebar_group_collapsed'
const DEMO_UI = import.meta.env.VITE_DEMO_UI === '1'

function readSidebarGroupCollapsed(): SidebarGroupCollapseState {
    const raw = localStorage.getItem(SIDEBAR_GROUP_COLLAPSED_STORAGE_KEY)
    if (!raw) return {}

    try {
        const parsed = JSON.parse(raw)
        if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) return {}

        return Object.fromEntries(
            Object.entries(parsed).filter((entry): entry is [string, boolean] => typeof entry[1] === 'boolean')
        )
    } catch {
        return {}
    }
}

function sidebarGroupStateKey(navMode: NavMode, groupKey: string): string {
    return `${navMode}:${groupKey}`
}

/**
 * UI store for app-wide UI state
 */
export const useUIStore = defineStore('ui', () => {
    // State: restore from localStorage
    const savedMode = localStorage.getItem(STORAGE_KEY) as UIMode | null
    const savedNavMode = localStorage.getItem(NAV_MODE_STORAGE_KEY) as NavMode | null
    const savedSidebarCollapsed = localStorage.getItem(SIDEBAR_COLLAPSED_STORAGE_KEY)
    const mode = ref<UIMode>(savedMode === 'immersive' ? 'immersive' : 'work')
    const navMode = ref<NavMode>(savedNavMode === 'module' ? 'module' : 'work')
    const sidebarCollapsed = ref(savedSidebarCollapsed === '1')
    const sidebarGroupCollapsed = ref<SidebarGroupCollapseState>(readSidebarGroupCollapsed())

    // Getters
    const isImmersive = computed(() => mode.value === 'immersive')
    const demoUI = computed(() => DEMO_UI)

    // Actions
    function setMode(newMode: UIMode): void {
        mode.value = newMode
        localStorage.setItem(STORAGE_KEY, newMode)
        applyBodyClass(newMode)
    }

    function toggleMode(): void {
        setMode(mode.value === 'work' ? 'immersive' : 'work')
    }

    function setNavMode(newMode: NavMode): void {
        navMode.value = newMode
        localStorage.setItem(NAV_MODE_STORAGE_KEY, newMode)
    }

    function setSidebarCollapsed(collapsed: boolean): void {
        sidebarCollapsed.value = collapsed
        localStorage.setItem(SIDEBAR_COLLAPSED_STORAGE_KEY, collapsed ? '1' : '0')
    }

    function toggleSidebarCollapsed(): void {
        setSidebarCollapsed(!sidebarCollapsed.value)
    }

    function persistSidebarGroupCollapsed(): void {
        localStorage.setItem(SIDEBAR_GROUP_COLLAPSED_STORAGE_KEY, JSON.stringify(sidebarGroupCollapsed.value))
    }

    function isSidebarGroupCollapsed(groupNavMode: NavMode, groupKey: string): boolean | undefined {
        return sidebarGroupCollapsed.value[sidebarGroupStateKey(groupNavMode, groupKey)]
    }

    function setSidebarGroupCollapsed(groupNavMode: NavMode, groupKey: string, collapsed: boolean): void {
        sidebarGroupCollapsed.value = {
            ...sidebarGroupCollapsed.value,
            [sidebarGroupStateKey(groupNavMode, groupKey)]: collapsed,
        }
        persistSidebarGroupCollapsed()
    }

    function toggleSidebarGroupCollapsed(groupNavMode: NavMode, groupKey: string): void {
        setSidebarGroupCollapsed(groupNavMode, groupKey, !isSidebarGroupCollapsed(groupNavMode, groupKey))
    }

    // Apply body class based on mode
    function applyBodyClass(m: UIMode): void {
        if (m === 'immersive') {
            document.body.classList.add('mode-immersive')
        } else {
            document.body.classList.remove('mode-immersive')
        }
    }

    // Apply demo theme (style-b) when VITE_DEMO_UI=1
    function applyDemoTheme(): void {
        if (DEMO_UI) {
            document.body.classList.add('style-b')
        } else {
            document.body.classList.remove('style-b')
        }
    }

    // Initialize on store creation
    applyBodyClass(mode.value)
    applyDemoTheme()

    return {
        mode,
        navMode,
        sidebarCollapsed,
        sidebarGroupCollapsed,
        isImmersive,
        demoUI,
        setMode,
        toggleMode,
        setNavMode,
        setSidebarCollapsed,
        toggleSidebarCollapsed,
        isSidebarGroupCollapsed,
        setSidebarGroupCollapsed,
        toggleSidebarGroupCollapsed,
    }
})
