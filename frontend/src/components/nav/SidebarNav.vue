<template>
  <aside class="sidebar">
    <div class="sidebar-logo">
      <span class="logo-icon">⚖️</span>
      <span class="logo-accent">法务流程</span>
    </div>
    <nav class="sidebar-nav">
      <template v-for="group in visibleGroups" :key="group.key">
        <div v-if="group.label" class="nav-group-label">{{ group.label }}</div>
        <router-link
          v-for="item in group.items"
          :key="item.key"
          :to="item.route"
          class="nav-item"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-label">{{ item.label }}</span>
        </router-link>
      </template>
    </nav>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { MENU_GROUPS } from '../../constants/menu'
import { useAuthStore } from '../../stores/auth'

const authStore = useAuthStore()

/**
 * Filter menu items based on permissions (best-effort)
 * If perms are unknown, show all items
 */
function canShowMenuItem(requiredPerms?: string[]): boolean {
  if (!requiredPerms || requiredPerms.length === 0) return true
  return authStore.hasAnyPermission(requiredPerms)
}

const visibleGroups = computed(() =>
  MENU_GROUPS
    .map(group => ({
      key: group.key,
      label: group.label,
      items: group.children.filter(item => canShowMenuItem(item.requiredPerms)),
    }))
    .filter(group => group.items.length > 0)
)
</script>

<style scoped>
.nav-group-label {
  font-size: 11px;
  color: var(--text-sub, #94A3B8);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 16px 15px 4px;
  font-weight: 600;
}
</style>
