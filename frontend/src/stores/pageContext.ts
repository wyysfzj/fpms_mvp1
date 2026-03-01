import { defineStore } from 'pinia'
import { ref } from 'vue'

/**
 * Page context store for breadcrumb and title management (DEMO-UI-03)
 * Used by detail pages to set contextual breadcrumbs in TopHeader
 */
export const usePageContext = defineStore('pageContext', () => {
    const breadcrumb = ref<string[]>([])
    const title = ref('')

    function setBreadcrumb(items: string[]) {
        breadcrumb.value = items
    }

    function setTitle(t: string) {
        title.value = t
    }

    function clear() {
        breadcrumb.value = []
        title.value = ''
    }

    return { breadcrumb, title, setBreadcrumb, setTitle, clear }
})
