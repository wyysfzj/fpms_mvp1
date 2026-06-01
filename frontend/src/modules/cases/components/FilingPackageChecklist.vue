<template>
  <section class="case-panel filing-checklist-panel">
    <div class="panel-toolbar">
      <div>
        <h3 class="panel-heading">字段完整性</h3>
        <p class="checklist-subtitle">缺失的稳定数据应回到案件、申请人或发明人维护位置处理。</p>
      </div>
      <el-tag :type="fieldSummaryTagType" size="small">{{ getStatusText(officialFieldSummary.status) }}</el-tag>
    </div>

    <div v-if="officialFieldSummary.items.length" class="field-check-grid">
      <div
        v-for="item in officialFieldSummary.items"
        :key="item.code"
        class="field-check-item"
      >
        <div>
          <strong>{{ item.label }}</strong>
          <span v-if="item.message">{{ item.message }}</span>
        </div>
        <div class="field-check-actions">
          <el-tag :type="getStatusTagType(item.status)" size="small">{{ getStatusText(item.status) }}</el-tag>
          <router-link
            v-if="isMissing(item.status)"
            class="maintenance-link"
            :to="`/cases/${caseId}/edit`"
          >
            到案件页维护
          </router-link>
        </div>
      </div>
    </div>
    <el-empty v-else description="暂无字段核对数据" :image-size="72" />

    <h4 class="subsection-title">官方页面字段清单</h4>
    <el-table :data="pageSectionRows" size="small" class="checklist-table">
      <el-table-column prop="label" label="官方页面字段" min-width="170" />
      <el-table-column prop="source" label="系统维护位置" min-width="170" />
      <el-table-column label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="getStatusTagType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="note" label="说明" min-width="220" />
    </el-table>

    <h4 class="subsection-title">官方页面审核动作</h4>
    <el-table :data="officialPageChecklist" size="small" class="checklist-table">
      <el-table-column prop="item_label" label="动作" min-width="180" />
      <el-table-column label="要求" width="90">
        <template #default="{ row }">
          <el-tag :type="row.required ? 'danger' : 'info'" size="small">
            {{ row.required ? '必做' : '可选' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="110">
        <template #default="{ row }">
          <el-tag :type="getStatusTagType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="evidence_note" label="证据 / 时间" min-width="220">
        <template #default="{ row }">{{ row.evidence_note || '待记录' }}</template>
      </el-table-column>
    </el-table>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type {
  OfficialFieldSummary,
  OfficialWorkPackageChecklist,
} from '../../../api/officialWorkflows.types'

const props = defineProps<{
  caseId: string
  officialFieldSummary: OfficialFieldSummary
  officialPageChecklist: OfficialWorkPackageChecklist[]
}>()

const fieldSummaryTagType = computed(() => getStatusTagType(props.officialFieldSummary.status))

const STANDARD_PAGE_SECTIONS = [
  { code: 'INTERNAL_NUMBER', label: '内部编号', source: '案件主数据' },
  { code: 'TITLE', label: '发明名称', source: '案件主数据' },
  { code: 'INVENTOR', label: '发明人', source: '案件发明人信息' },
  { code: 'APPLICANT', label: '申请人', source: '案件申请人信息' },
  { code: 'CONTACT', label: '联系人', source: '客户联系人' },
  { code: 'AGENCY', label: '代理机构 / 代理人', source: '代理人档案' },
  { code: 'DIVISION', label: '分案信息', source: '案件主数据' },
  { code: 'SEQUENCE_LISTING', label: '序列表', source: '申请文件角色' },
  { code: 'PRIORITY', label: '优先权', source: '案件优先权信息' },
  { code: 'EARLY_PUBLICATION', label: '提前公开', source: '案件递交选项' },
  { code: 'SUBSTANTIVE_EXAMINATION', label: '实质审查', source: '案件递交选项' },
  { code: 'ABSTRACT_DRAWING', label: '摘要附图', source: '申请文件角色' },
  { code: 'CONFIDENTIALITY_REVIEW', label: '保密审查', source: '案件递交选项' },
  { code: 'ADDITIONAL_FILES', label: '附加文件', source: '附件文件角色' },
  { code: 'ASSOCIATED_BUSINESS', label: '关联业务', source: '案件关联信息' },
  { code: 'PROOF_FILING', label: '证明文件备案', source: '附件文件角色' },
]

const pageSectionRows = computed(() =>
  STANDARD_PAGE_SECTIONS.map((section) => {
    const checklist = props.officialPageChecklist.find((item) => item.item_code === section.code)
    const fieldItem = props.officialFieldSummary.items.find((item) => item.code.includes(section.code))
    return {
      ...section,
      status: checklist?.status || fieldItem?.status || 'PENDING',
      note: checklist?.evidence_note || fieldItem?.message || '按现有系统数据核对，不设置长期提交前维护区。',
    }
  })
)

function isMissing(status?: string | null): boolean {
  return ['MISSING', 'NEEDS_MAINTENANCE', 'BLOCKED'].includes(String(status || '').toUpperCase())
}

function getStatusText(status?: string | null): string {
  const normalized = String(status || '').toUpperCase()
  if (normalized === 'READY' || normalized === 'DONE' || normalized === 'PASS') return '已满足'
  if (normalized === 'PRESENT') return '已提供'
  if (normalized === 'MISSING' || normalized === 'NEEDS_MAINTENANCE') return '需维护'
  if (normalized === 'NEEDS_CONFIRMATION' || normalized === 'PENDING') return '待确认'
  if (normalized === 'BLOCKED') return '阻止'
  return status || '待核对'
}

function getStatusTagType(status?: string | null): 'success' | 'warning' | 'danger' | 'info' {
  const normalized = String(status || '').toUpperCase()
  if (normalized === 'READY' || normalized === 'DONE' || normalized === 'PASS' || normalized === 'PRESENT') return 'success'
  if (normalized === 'MISSING' || normalized === 'NEEDS_MAINTENANCE' || normalized === 'BLOCKED') return 'danger'
  if (normalized === 'NEEDS_CONFIRMATION' || normalized === 'PENDING') return 'warning'
  return 'info'
}
</script>

<style scoped>
.filing-checklist-panel {
  display: grid;
  gap: 16px;
}

.checklist-subtitle {
  margin: -6px 0 0;
  color: var(--text-sub);
  font-size: 13px;
}

.field-check-grid {
  display: grid;
  gap: 10px;
}

.field-check-item {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 12px;
}

.field-check-item div {
  display: grid;
  gap: 4px;
}

.field-check-item span {
  color: var(--text-sub);
  font-size: 12px;
}

.field-check-actions {
  justify-items: end;
  min-width: 110px;
}

.maintenance-link {
  color: var(--color-primary);
  font-size: 12px;
  text-decoration: none;
}

.subsection-title {
  margin: 6px 0 0;
  color: var(--text-main);
  font-size: 15px;
}

.checklist-table {
  width: 100%;
}
</style>
