<template>
  <aside class="sidebar product-sidebar" :class="{ 'sidebar-collapsed': uiStore.sidebarCollapsed }">
    <div class="sidebar-header">
      <router-link to="/dashboard" class="sidebar-logo" title="法务流程">
        <span class="logo-icon">⚖️</span>
        <span class="logo-copy">
          <span class="logo-accent">法务流程</span>
          <span class="logo-subtitle">知识产权管理系统</span>
        </span>
      </router-link>
      <button
        class="sidebar-collapse-button"
        type="button"
        :aria-label="uiStore.sidebarCollapsed ? '展开侧栏' : '收起侧栏'"
        :title="uiStore.sidebarCollapsed ? '展开侧栏' : '收起侧栏'"
        @click="uiStore.toggleSidebarCollapsed()"
      >
        {{ uiStore.sidebarCollapsed ? '›' : '‹' }}
      </button>
    </div>

    <div v-if="!uiStore.sidebarCollapsed" class="nav-mode-switch" role="tablist" aria-label="导航模式">
      <button
        v-for="mode in navModes"
        :key="mode.key"
        type="button"
        class="nav-mode-button"
        :class="{ active: uiStore.navMode === mode.key }"
        role="tab"
        :aria-selected="uiStore.navMode === mode.key"
        @click="setNavMode(mode.key)"
      >
        {{ mode.label }}
      </button>
    </div>

    <nav class="sidebar-nav" aria-label="主导航">
      <section
        v-for="group in mainGroups"
        :key="group.key"
        class="nav-section"
        :class="{
          'nav-section-collapsed': isGroupCollapsed(group),
          'nav-section-active': activeGroupKey === group.key,
        }"
      >
        <button
          v-if="group.label && !uiStore.sidebarCollapsed"
          class="nav-group-button"
          :class="{ 'nav-group-button-locked': activeGroupKey === group.key }"
          type="button"
          :aria-expanded="!isGroupCollapsed(group)"
          :aria-disabled="activeGroupKey === group.key"
          :title="activeGroupKey === group.key ? '当前分组保持展开' : group.label"
          @click="toggleGroup(group)"
        >
          <span class="nav-group-title">
            <span>{{ group.label }}</span>
            <small v-if="group.description">{{ group.description }}</small>
          </span>
          <span class="nav-group-meta">
            <span class="nav-group-count">{{ group.items.length }}</span>
            <span class="nav-group-chevron" aria-hidden="true">⌄</span>
          </span>
        </button>
        <div v-show="!isGroupCollapsed(group) || uiStore.sidebarCollapsed" class="nav-group-items">
          <router-link
            v-for="item in group.items"
            :key="item.key"
            :to="item.route"
            class="nav-item"
            :class="{ active: activeItemKey === item.key }"
            :title="item.label"
            :aria-label="item.label"
          >
            <span class="nav-icon" aria-hidden="true">{{ item.icon }}</span>
            <span class="nav-label">{{ item.label }}</span>
          </router-link>
        </div>
      </section>
    </nav>

    <div v-if="bottomGroups.length > 0" class="sidebar-bottom-nav">
      <section
        v-for="group in bottomGroups"
        :key="group.key"
        class="nav-section nav-section-bottom"
        :class="{
          'nav-section-collapsed': isGroupCollapsed(group),
          'nav-section-active': activeGroupKey === group.key,
        }"
      >
        <button
          v-if="group.label && !uiStore.sidebarCollapsed"
          class="nav-group-button nav-group-button-bottom"
          :class="{ 'nav-group-button-locked': activeGroupKey === group.key }"
          type="button"
          :aria-expanded="!isGroupCollapsed(group)"
          :aria-disabled="activeGroupKey === group.key"
          :title="activeGroupKey === group.key ? '当前分组保持展开' : group.label"
          @click="toggleGroup(group)"
        >
          <span class="nav-group-title">
            <span>{{ group.label }}</span>
          </span>
          <span class="nav-group-meta">
            <span class="nav-group-count">{{ group.items.length }}</span>
            <span class="nav-group-chevron" aria-hidden="true">⌄</span>
          </span>
        </button>
        <div v-show="!isGroupCollapsed(group) || uiStore.sidebarCollapsed" class="nav-group-items">
          <router-link
            v-for="item in group.items"
            :key="item.key"
            :to="item.route"
            class="nav-item"
            :class="{ active: activeItemKey === item.key }"
            :title="item.label"
            :aria-label="item.label"
          >
            <span class="nav-icon" aria-hidden="true">{{ item.icon }}</span>
            <span class="nav-label">{{ item.label }}</span>
          </router-link>
        </div>
      </section>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { PRODUCT_NAV_GROUPS } from '../../constants/menu'
import type { MenuItem, NavMode } from '../../constants/menu'
import { useAuthStore } from '../../stores/auth'
import { useUIStore } from '../../stores/ui'

type VisibleGroup = {
  key: string
  label: string
  mode: NavMode
  description?: string
  pinnedBottom?: boolean
  items: MenuItem[]
}

const navModes: { key: NavMode; label: string }[] = [
  { key: 'work', label: '工作导航' },
  { key: 'module', label: '模块导航' },
]

const route = useRoute()
const authStore = useAuthStore()
const uiStore = useUIStore()

function canShowMenuItem(requiredPerms?: string[]): boolean {
  if (!requiredPerms || requiredPerms.length === 0) return true
  return authStore.hasAnyPermission(requiredPerms)
}

function setNavMode(mode: NavMode): void {
  uiStore.setNavMode(mode)
}

const visibleGroups = computed<VisibleGroup[]>(() =>
  PRODUCT_NAV_GROUPS
    .filter(group => group.mode === uiStore.navMode)
    .map(group => ({
      key: group.key,
      label: group.label,
      mode: group.mode,
      description: group.description,
      pinnedBottom: group.pinnedBottom,
      items: group.children.filter(item => canShowMenuItem(item.requiredPerms)),
    }))
    .filter(group => group.items.length > 0)
)

const mainGroups = computed(() => visibleGroups.value.filter(group => !group.pinnedBottom))
const bottomGroups = computed(() => visibleGroups.value.filter(group => group.pinnedBottom))

function scorePattern(pattern: string, currentPath: string): number {
  if (pattern.endsWith('/*')) {
    const prefix = pattern.slice(0, -1)
    return currentPath.startsWith(prefix) ? 5000 + prefix.length : -1
  }
  if (currentPath === pattern) return 9000 + pattern.length
  return currentPath.startsWith(`${pattern}/`) ? 5000 + pattern.length : -1
}

function scoreItem(item: MenuItem): number {
  const currentPath = route.path
  const candidates = [item.route, ...(item.activePatterns ?? [])]
  let score = -1
  for (const pattern of candidates) {
    score = Math.max(score, scorePattern(pattern, currentPath))
  }
  return score
}

const activeItemKey = computed(() => {
  const items = visibleGroups.value.flatMap(group => group.items)
  let bestKey = ''
  let bestScore = -1
  for (const item of items) {
    const score = scoreItem(item)
    if (score > bestScore) {
      bestScore = score
      bestKey = item.key
    }
  }
  return bestKey
})

const activeGroupKey = computed(() => {
  for (const group of visibleGroups.value) {
    if (group.items.some(item => item.key === activeItemKey.value)) {
      return group.key
    }
  }
  return ''
})

function defaultGroupCollapsed(group: VisibleGroup): boolean {
  if (group.mode === 'work') return false
  return group.key !== 'module-work'
}

function isGroupCollapsed(group: VisibleGroup): boolean {
  if (uiStore.sidebarCollapsed) return false
  if (activeGroupKey.value === group.key) return false

  const savedState = uiStore.isSidebarGroupCollapsed(group.mode, group.key)
  return savedState ?? defaultGroupCollapsed(group)
}

function toggleGroup(group: VisibleGroup): void {
  if (activeGroupKey.value === group.key) return
  uiStore.setSidebarGroupCollapsed(group.mode, group.key, !isGroupCollapsed(group))
}
</script>
