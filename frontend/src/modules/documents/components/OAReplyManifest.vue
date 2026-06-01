<template>
  <section class="case-panel oa-manifest-panel">
    <div class="panel-toolbar">
      <div>
        <h3 class="panel-heading">OA答复文件清单</h3>
        <p class="manifest-subtitle">文件角色直接服务官方页面上传位置和回执收到文件核对。</p>
      </div>
      <el-tag :type="experimentDataSubmitted ? 'warning' : 'info'" size="small">
        补交实验数据：{{ experimentDataSubmitted ? '是' : '否' }}
      </el-tag>
    </div>

    <div class="attachment-grid">
      <div class="attachment-card">
        <span>意见陈述 Word</span>
        <el-tag :type="getAttachmentTagType(statementWord.status)" size="small">
          {{ getAttachmentStatusText(statementWord.status) }}
        </el-tag>
        <strong>{{ getAttachmentName(statementWord) }}</strong>
        <small>{{ statementWord.external_upload_position || '页面字段 / 待确认上传位置' }}</small>
      </div>
      <div class="attachment-card">
        <span>PDF保真附件</span>
        <el-tag :type="getAttachmentTagType(statementPdf.status)" size="small">
          {{ getAttachmentStatusText(statementPdf.status) }}
        </el-tag>
        <strong>{{ getAttachmentName(statementPdf) }}</strong>
        <small>{{ statementPdf.external_upload_position || '附加文件类别待确认' }}</small>
      </div>
      <div class="attachment-card">
        <span>修改对照页</span>
        <el-tag :type="getAttachmentTagType(comparisonPage.status)" size="small">
          {{ getAttachmentStatusText(comparisonPage.status) }}
        </el-tag>
        <strong>{{ getAttachmentName(comparisonPage) }}</strong>
        <small>{{ comparisonPage.external_upload_position || '附加文件 / 待确认' }}</small>
      </div>
      <div class="attachment-card">
        <span>其他证明文件</span>
        <el-tag :type="proofFiles.length ? 'success' : 'info'" size="small">
          {{ proofFiles.length ? `${proofFiles.length} 个` : '无' }}
        </el-tag>
        <strong>{{ proofFiles.length ? proofFiles.map(getAttachmentName).join('、') : '按需提供' }}</strong>
        <small>实验数据、证明材料或其他附加文件</small>
      </div>
    </div>

    <h4 class="subsection-title">修改后的权利要求书</h4>
    <el-table :data="modifiedClaimFiles" size="small" class="manifest-table">
      <el-table-column label="文件" min-width="180">
        <template #default="{ row }">{{ getAttachmentName(row) }}</template>
      </el-table-column>
      <el-table-column label="状态" width="110">
        <template #default="{ row }">
          <el-tag :type="getAttachmentTagType(row.status)" size="small">
            {{ getAttachmentStatusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="官方上传位置" min-width="180">
        <template #default="{ row }">{{ row.external_upload_position || '待确认' }}</template>
      </el-table-column>
    </el-table>

    <h4 class="subsection-title">工作包文件角色</h4>
    <el-table :data="oaFileRoles" size="small" class="manifest-table">
      <el-table-column label="文件角色" min-width="170">
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
      <el-table-column label="官方上传位置" min-width="180">
        <template #default="{ row }">{{ row.external_upload_position || '待确认' }}</template>
      </el-table-column>
      <el-table-column label="说明" min-width="190">
        <template #default="{ row }">{{ row.note || row.source_role_alias || '按文件角色核对' }}</template>
      </el-table-column>
    </el-table>
  </section>
</template>

<script setup lang="ts">
import type {
  OaReplyAttachment,
  OfficialWorkPackageManifest,
} from '../../../api/officialWorkflows.types'

defineProps<{
  statementWord: OaReplyAttachment
  statementPdf: OaReplyAttachment
  modifiedClaimFiles: OaReplyAttachment[]
  comparisonPage: OaReplyAttachment
  proofFiles: OaReplyAttachment[]
  experimentDataSubmitted: boolean
  oaFileRoles: OfficialWorkPackageManifest[]
}>()

const ROLE_TEXT: Record<string, string> = {
  OA_STATEMENT_WORD: '意见陈述 Word',
  OA_STATEMENT_PDF: 'PDF保真附件',
  OA_MODIFIED_CLAIMS: '修改后的权利要求书',
  OA_AMENDMENT_COMPARISON: '修改对照页',
  OA_OTHER_PROOF: '其他证明文件',
  OA_ADDITIONAL_FILE: '附加文件',
  RECEIPT_PDF: '电子申请回执',
  MERGED_PDF: '合并 PDF',
}

function getRoleText(role?: string | null): string {
  const normalized = String(role || '').trim().toUpperCase()
  if (!normalized) return '未标注'
  return ROLE_TEXT[normalized] || normalized
}

function getAttachmentName(attachment: OaReplyAttachment): string {
  return attachment.file_name || attachment.attachment_id || '未匹配'
}

function getAttachmentStatusText(status?: string | null): string {
  const normalized = String(status || '').toUpperCase()
  if (normalized === 'READY' || normalized === 'PRESENT' || normalized === 'DONE') return '已满足'
  if (normalized === 'MISSING') return '待维护'
  if (normalized === 'PENDING') return '待确认'
  return status || '待核对'
}

function getAttachmentTagType(status?: string | null): 'success' | 'warning' | 'danger' | 'info' {
  const normalized = String(status || '').toUpperCase()
  if (normalized === 'READY' || normalized === 'PRESENT' || normalized === 'DONE') return 'success'
  if (normalized === 'MISSING') return 'warning'
  if (normalized === 'BLOCKED' || normalized === 'EXCEPTION') return 'danger'
  return 'info'
}
</script>

<style scoped>
.oa-manifest-panel {
  display: grid;
  gap: 16px;
}

.manifest-subtitle {
  margin: -6px 0 0;
  color: var(--text-sub);
  font-size: 13px;
}

.attachment-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.attachment-card {
  display: grid;
  gap: 8px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 12px;
  background: #f8fafc;
}

.attachment-card span {
  color: var(--text-sub);
  font-size: 12px;
}

.attachment-card strong {
  color: var(--text-main);
  font-size: 13px;
  overflow-wrap: anywhere;
}

.attachment-card small {
  color: var(--text-sub);
  font-size: 12px;
}

.subsection-title {
  margin: 2px 0 0;
  color: var(--text-main);
  font-size: 15px;
}

.manifest-table {
  width: 100%;
}

@media (max-width: 1180px) {
  .attachment-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .attachment-grid {
    grid-template-columns: 1fr;
  }
}
</style>
