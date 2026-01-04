<template>
  <div style="display:flex; min-height: 100vh;">
    <aside style="width: 220px; border-right: 1px solid #ddd; padding: 12px;">
      <div style="font-weight: 600; margin-bottom: 12px;">FPMS MVP1</div>
      <nav style="display:flex; flex-direction: column; gap: 8px;">
        <router-link to="/dashboard">Dashboard</router-link>
        <router-link to="/cases">Cases</router-link>
        <router-link to="/documents">Documents</router-link>
        <router-link to="/tasks">Tasks</router-link>
        <router-link to="/fees/drafts">Fees</router-link>
        <router-link to="/billing/bills">Billing</router-link>
        <router-link to="/settings/clients">Settings</router-link>
      </nav>
    </aside>
    <main style="flex:1; padding: 16px;">
      <router-view />
    </main>
  </div>
</template>
