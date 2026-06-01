<template>
  <section class="case-panel oa-checklist-panel">
    <div class="panel-toolbar">
      <div>
        <h3 class="panel-heading">官方页面审核清单</h3>
        <p class="checklist-subtitle">按客户截图中的人工页面动作核对，不替代签名、扫码或正式提交。</p>
      </div>
      <el-tag :type="overallTagType" size="small">{{ overallStatusText }}</el-tag>
    </div>

    <div class="standard-step-grid">
      <div v-for="step in standardStepRows" :key="step.code" class="standard-step">
        <div class="step-title-row">
          <strong>{{ step.label }}</strong>
          <el-tag :type="getStatusTagType(step.status)" size="small">
            {{ getStatusText(step.status) }}
          </el-tag>
        </div>
        <span>{{ step.note }}</span>
        <small>{{ step.evidence_note || '待记录人工核对证据' }}</small>
      </div>
    </div>

    <el-table :data="officialPageChecklist" size="small" class="checklist-table">
      <el-table-column prop="item_label" label="页面动作 / 字段" min-width="190" />
      <el-table-column label="要求" width="90">
        <template #default="{ row }">
          <el-tag :type="row.required ? 'danger' : 'info'" size="small">
            {{ row.required ? '必做' : '可选' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="110">
        <template #default="{ row }">
          <el-tag :type="getStatusTagType(row.status)" size="small">
            {{ getStatusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="证据 / 备注" min-width="220">
        <template #default="{ row }">{{ row.evidence_note || '待记录' }}</template>
      </el-table-column>
    </el-table>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { OfficialWorkPackageChecklist } from '../../../api/officialWorkflows.types'

const props = defineProps<{
  officialPageChecklist: OfficialWorkPackageChecklist[]
}>()

const STANDARD_STEPS = [
  {
    code: 'CLOUD_SECOND_DOWNLOAD_CONFIRMED',
    label: '云端二次下载',
    note: '确认需答复官文已二次下载或已明确该场景无需执行。',
  },
  {
    code: 'QUERY_RESULT_CONFIRMED',
    label: '查询结果',
    note: '核对申请号、官文名称、官文代码、发文日和期限。',
  },
  {
    code: 'BUSINESS_HANDLING_CONFIRMED',
    label: '业务办理',
    note: '核对已进入正确的答复办理事项和页面入口。',
  },
  {
    code: 'PREVIEW_TABS_CONFIRMED',
    label: '预览标签页',
    note: '核对陈述意见、修改文件和附加文件预览内容。',
  },
  {
    code: 'SIGNATURE_CONFIRMED',
    label: '签名确认',
    note: '签名责任由工作人员人工确认并留痕。',
  },
  {
    code: 'SUBMISSION_CONFIRMED',
    label: '提交确认',
    note: '正式提交由工作人员人工完成并记录结果。',
  },
  {
    code: 'RECEIPT_CONFIRMED',
    label: '回执归档',
    note: '以电子申请回执或归档状态作为关闭依据。',
  },
]

const standardStepRows = computed(() =>
  STANDARD_STEPS.map((step) => {
    const item = props.officialPageChecklist.find((check) => check.item_code === step.code)
    return {
      ...step,
      status: item?.status || 'PENDING',
      evidence_note: item?.evidence_note || '',
    }
  })
)

const overallTagType = computed(() => {
  if (!props.officialPageChecklist.length) return 'info'
  if (props.officialPageChecklist.some((item) => isBlocked(item.status))) return 'danger'
  if (props.officialPageChecklist.some((item) => item.required && !isDone(item.status))) return 'warning'
  return 'success'
})

const overallStatusText = computed(() => {
  if (!props.officialPageChecklist.length) return '待生成'
  if (props.officialPageChecklist.some((item) => isBlocked(item.status))) return '存在阻止项'
  if (props.officialPageChecklist.some((item) => item.required && !isDone(item.status))) return '待确认'
  return '已满足'
})

function isDone(status?: string | null): boolean {
  return ['DONE', 'READY', 'PASS', 'PRESENT'].includes(String(status || '').toUpperCase())
}

function isBlocked(status?: string | null): boolean {
  return ['BLOCKED', 'MISSING', 'NEEDS_MAINTENANCE', 'EXCEPTION'].includes(String(status || '').toUpperCase())
}

function getStatusText(status?: string | null): string {
  const normalized = String(status || '').toUpperCase()
  if (normalized === 'DONE' || normalized === 'READY' || normalized === 'PASS') return '已确认'
  if (normalized === 'PRESENT') return '已提供'
  if (normalized === 'MISSING' || normalized === 'NEEDS_MAINTENANCE') return '需维护'
  if (normalized === 'BLOCKED' || normalized === 'EXCEPTION') return '阻止'
  if (normalized === 'PENDING' || normalized === 'NEEDS_CONFIRMATION') return '待确认'
  return status || '待核对'
}

function getStatusTagType(status?: string | null): 'success' | 'warning' | 'danger' | 'info' {
  const normalized = String(status || '').toUpperCase()
  if (normalized === 'DONE' || normalized === 'READY' || normalized === 'PASS' || normalized === 'PRESENT') return 'success'
  if (normalized === 'MISSING' || normalized === 'NEEDS_MAINTENANCE' || normalized === 'BLOCKED' || normalized === 'EXCEPTION') return 'danger'
  if (normalized === 'PENDING' || normalized === 'NEEDS_CONFIRMATION') return 'warning'
  return 'info'
}
</script>

<style scoped>
.oa-checklist-panel {
  display: grid;
  gap: 16px;
}

.checklist-subtitle {
  margin: -6px 0 0;
  color: var(--text-sub);
  font-size: 13px;
}

.standard-step-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.standard-step {
  display: grid;
  gap: 8px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 12px;
  background: #f8fafc;
}

.step-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.standard-step span,
.standard-step small {
  color: var(--text-sub);
  font-size: 12px;
}

.checklist-table {
  width: 100%;
}

@media (max-width: 860px) {
  .standard-step-grid {
    grid-template-columns: 1fr;
  }
}
</style>
