<template>
  <div class="state-pagination-bar">
    <el-pagination
      :current-page="page"
      :page-size="pageSize"
      :page-sizes="pageSizes"
      :total="total"
      layout="total, sizes, prev, pager, next"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    />
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  page: number
  pageSize: number
  total: number
  pageSizes?: number[]
}>(), {
  pageSizes: () => [10, 20, 50, 100],
})

const emit = defineEmits<{
  'update:page': [value: number]
  'update:pageSize': [value: number]
}>()

function handleCurrentChange(nextPage: number) {
  emit('update:page', nextPage)
}

function handleSizeChange(nextSize: number) {
  emit('update:pageSize', nextSize)
  emit('update:page', 1)
}
</script>
