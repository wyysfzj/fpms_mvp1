<template>
  <section class="case-panel filing-manifest-panel">
    <h3 class="panel-heading">文件清单</h3>
    <div class="gate-cards">
      <div class="gate-card">
        <span>技术交底书</span>
        <el-tag :type="getStatusTagType(technicalDisclosureGate.status)" size="small">
          {{ getStatusText(technicalDisclosureGate.status) }}
        </el-tag>
        <strong>{{ technicalDisclosureGate.file_name || technicalDisclosureGate.attachment_id || '未匹配' }}</strong>
      </div>
      <div class="gate-card">
        <span>委托指示（如有）</span>
        <el-tag :type="getStatusTagType(commissionInstructionGate.status)" size="small">
          {{ getStatusText(commissionInstructionGate.status) }}
        </el-tag>
        <strong>{{ commissionInstructionGate.file_name || commissionInstructionGate.attachment_id || '未匹配' }}</strong>
      </div>
      <div class="gate-card">
        <span>XML zip</span>
        <el-tag :type="getStatusTagType(xmlZip.status)" size="small">{{ getStatusText(xmlZip.status) }}</el-tag>
        <strong>{{ xmlZip.file_name || xmlZip.attachment_id || xmlZip.placeholder || '未匹配' }}</strong>
      </div>
      <div class="gate-card">
        <span>合并 PDF</span>
        <el-tag :type="getStatusTagType(mergedPdfArchiveStatus)" size="small">
          {{ getStatusText(mergedPdfArchiveStatus) }}
        </el-tag>
        <strong>官方提交后归档</strong>
      </div>
    </div>

    <el-table :data="filingFileRoles" size="small" class="manifest-table">
      <el-table-column label="文件角色" min-width="160">
        <template #default="{ row }">{{ getRoleText(row.official_file_role) }}</template>
      </el-table-column>
      <el-table-column label="要求" width="90">
        <template #default="{ row }">
          <el-tag :type="row.required ? 'danger' : 'info'" size="small">
            {{ row.required ? '必需' : '可选' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="110">
        <template #default="{ row }">
          <el-tag :type="row.present ? 'success' : 'warning'" size="small">
            {{ row.present ? '已匹配' : '待匹配' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="附件" min-width="150">
        <template #default="{ row }">{{ row.attachment_id || '未关联' }}</template>
      </el-table-column>
      <el-table-column label="官方上传位置" min-width="160">
        <template #default="{ row }">{{ row.external_upload_position || '待确认' }}</template>
      </el-table-column>
      <el-table-column label="内容哈希" min-width="130">
        <template #default="{ row }">{{ formatHash(row.content_hash) }}</template>
      </el-table-column>
      <el-table-column prop="note" label="说明" min-width="190" />
    </el-table>
  </section>
</template>

<script setup lang="ts">
import type {
  FilingPackageGate,
  FilingPackageXmlZip,
  OfficialWorkPackageManifest,
} from '../../../api/officialWorkflows.types'

defineProps<{
  technicalDisclosureGate: FilingPackageGate
  commissionInstructionGate: FilingPackageGate
  filingFileRoles: OfficialWorkPackageManifest[]
  xmlZip: FilingPackageXmlZip
  mergedPdfArchiveStatus: string
}>()

const ROLE_TEXT: Record<string, string> = {
  TECHNICAL_DISCLOSURE: '技术交底书',
  COMMISSION_INSTRUCTION: '委托指示',
  FILING_XML_ZIP: 'XML压缩包',
  FILING_MERGED_PDF: '合并 PDF',
  FILING_DOCUMENT: '递交文件',
  FILING_CLAIMS: '权利要求书',
}

function getRoleText(role?: string | null): string {
  const normalized = String(role || '').trim().toUpperCase()
  if (!normalized) return '未标注'
  return ROLE_TEXT[normalized] || normalized
}

function getStatusText(status?: string | null): string {
  const normalized = String(status || '').toUpperCase()
  if (normalized === 'READY' || normalized === 'PRESENT' || normalized === 'DONE') return '已满足'
  if (normalized === 'MISSING') return '待维护'
  if (normalized === 'PENDING') return '待确认'
  return status || '待核对'
}

function getStatusTagType(status?: string | null): 'success' | 'warning' | 'danger' | 'info' {
  const normalized = String(status || '').toUpperCase()
  if (normalized === 'READY' || normalized === 'PRESENT' || normalized === 'DONE') return 'success'
  if (normalized === 'MISSING') return 'warning'
  return 'info'
}

function formatHash(value?: string | null): string {
  if (!value) return '未生成'
  return value.length > 14 ? `${value.slice(0, 14)}...` : value
}
</script>

<style scoped>
.filing-manifest-panel {
  display: grid;
  gap: 16px;
}

.gate-cards {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.gate-card {
  display: grid;
  gap: 8px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 12px;
  background: #f8fafc;
}

.gate-card span {
  color: var(--text-sub);
  font-size: 12px;
}

.gate-card strong {
  color: var(--text-main);
  font-size: 13px;
  overflow-wrap: anywhere;
}

.manifest-table {
  width: 100%;
}

@media (max-width: 1100px) {
  .gate-cards {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .gate-cards {
    grid-template-columns: 1fr;
  }
}
</style>
