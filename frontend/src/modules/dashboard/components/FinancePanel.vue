<template>
  <div class="panel">
    <div class="panel-header">
      <span class="panel-title">{{ ZH.finance.title }}</span>
    </div>

    <el-skeleton v-if="loading" :rows="3" animated style="padding: 18px;" />

    <div v-else-if="items.length === 0" class="panel-empty">
      暂无财务数据
    </div>

    <template v-else>
      <FinanceRow v-for="item in items" :key="item.id" :item="item" />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ZH } from '../../../constants/labels.zh'
import FinanceRow from './FinanceRow.vue'
import type { FinanceItem } from './FinanceRow.vue'

defineProps<{
  items: FinanceItem[]
  loading: boolean
}>()
</script>
