import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import 'element-plus/dist/index.css'

// Global styles
import './styles/variables.css'
import './styles/base.css'
import './styles/layout.css'
import './styles/demo-themes.css'
import './styles/dashboard.css'
import './styles/pipeline.css'
import './styles/relations.css'
import './styles/workflow.css'
import './styles/stepper.css'

import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(ElementPlus, { locale: zhCn })

// Initialize UI store to restore mode and apply body class
import { useUIStore } from './stores/ui'
// Store is auto-initialized when accessed, which applies body class

// Listen for unauthorized events and redirect to login
window.addEventListener('fpms:unauthorized', () => {
    const currentRoute = router.currentRoute.value
    if (currentRoute.name !== 'login') {
        router.push({ name: 'login' })
    }
})

// Listen for forbidden events and redirect to /forbidden
interface ForbiddenEventDetail {
    requiredPerm?: string
    message?: string
    requestId?: string
}

window.addEventListener('fpms:forbidden', ((event: CustomEvent<ForbiddenEventDetail>) => {
    const currentRoute = router.currentRoute.value
    // Avoid redirect loop
    if (currentRoute.name !== 'forbidden') {
        const query: Record<string, string> = {}
        if (event.detail?.requiredPerm) {
            query.perm = event.detail.requiredPerm
        }
        if (event.detail?.requestId) {
            query.rid = event.detail.requestId
        }
        router.push({ name: 'forbidden', query })
    }
}) as EventListener)

async function bootstrap(): Promise<void> {
    // Re-hydrate auth state on refresh and fetch permissions so menu visibility is stable.
    const authStore = useAuthStore()
    authStore.syncFromStorage()
    if (authStore.token) {
        try {
            await authStore.loadPermissions()
        } catch {
            // Keep app boot resilient; downstream API guards will handle auth errors.
        }
    }

    app.mount('#app')

    // Initialize UI store after mount to ensure body class is applied
    useUIStore()
}

void bootstrap()
