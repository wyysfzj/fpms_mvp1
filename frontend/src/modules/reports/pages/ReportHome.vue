<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">统计报表</h1>
        <span class="page-count">独立分析入口</span>
      </div>
    </div>

    <div class="report-entry-grid">
      <router-link
        v-for="entry in reportEntries"
        :key="entry.route"
        class="report-entry"
        :to="entry.route"
      >
        <span class="entry-icon">{{ entry.icon }}</span>
        <span class="entry-title">{{ entry.title }}</span>
        <span class="entry-desc">{{ entry.desc }}</span>
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
const reportEntries = [
  {
    title: '案件统计',
    desc: '案件总量、状态分布、客户/国别/代理人分布与年度趋势。',
    route: '/reports/cases',
    icon: '📊',
  },
  {
    title: '账单统计',
    desc: '应收、逾期、账龄与坏账回收统计。',
    route: '/reports/bills',
    icon: '🧾',
  },
  {
    title: '预收款管理报表',
    desc: '预收款、核销金额与剩余预收余额。',
    route: '/billing/payments',
    icon: '💳',
  },
  {
    title: '费用草稿统计',
    desc: '草稿收入、服务费、官费与多维度汇总。',
    route: '/reports/fee-drafts',
    icon: '💰',
  },
  {
    title: '年费任务统计',
    desc: '任务状态、缴费状态、客户/国家/年度金额汇总。',
    route: '/reports/annuity-tasks',
    icon: '⏱️',
  },
  {
    title: '支出统计',
    desc: '支出总额、分类、案件、客户、部门与毛利分析。',
    route: '/reports/expenses',
    icon: '📉',
  },
  {
    title: '费用情况一览',
    desc: '官费缴费情况与个案收款情况综合查询。',
    route: '/billing/fee-unified-query',
    icon: '🔍',
  },
  {
    title: '提成结算报表',
    desc: '提成结算批次、明细、代理人与案件维度统计。',
    route: '/commission/settlements',
    icon: '🧮',
  },
  {
    title: '顾问收益视图',
    desc: '顾问项目收入、支出与毛利分析。',
    route: '/consulting/profitability',
    icon: '📈',
  },
]
</script>

<style scoped>
.report-entry-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
}

.report-entry {
  display: grid;
  grid-template-columns: auto 1fr;
  grid-template-areas:
    "icon title"
    "icon desc";
  column-gap: 12px;
  row-gap: 6px;
  min-height: 96px;
  padding: 18px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  color: inherit;
  background: var(--el-bg-color);
  text-decoration: none;
}

.report-entry:hover {
  border-color: var(--color-primary);
}

.entry-icon {
  grid-area: icon;
  font-size: 24px;
  line-height: 1;
}

.entry-title {
  grid-area: title;
  font-size: 16px;
  font-weight: 600;
}

.entry-desc {
  grid-area: desc;
  color: var(--text-sub);
  font-size: 13px;
  line-height: 1.5;
}
</style>
