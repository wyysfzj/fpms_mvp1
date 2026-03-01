import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export type UIMode = 'work' | 'immersive'

const STORAGE_KEY = 'fpms_ui_mode'
const DEMO_UI = import.meta.env.VITE_DEMO_UI === '1'

/**
 * UI store for app-wide UI state
 */
export const useUIStore = defineStore('ui', () => {
    // State: restore from localStorage
    const savedMode = localStorage.getItem(STORAGE_KEY) as UIMode | null
    const mode = ref<UIMode>(savedMode === 'immersive' ? 'immersive' : 'work')

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
        isImmersive,
        demoUI,
        setMode,
        toggleMode,
    }
})
