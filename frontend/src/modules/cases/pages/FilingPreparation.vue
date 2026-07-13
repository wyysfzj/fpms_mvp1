<template>
  <main class="page-container filing-preparation-page">
    <div class="page-header">
      <div>
        <h1>新申请递交准备</h1>
        <p class="page-subtitle">核对系统已维护信息、文件角色、官方页面清单和人工外部操作记录。</p>
      </div>
      <div class="page-actions">
        <el-button @click="goBack">返回</el-button>
        <el-button
          type="primary"
          :disabled="!packageId"
          :loading="refreshing"
          @click="handleRefresh"
        >
          刷新工作包
        </el-button>
      </div>
    </div>

    <div v-if="error" class="page-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <el-alert
      v-if="!packageId && !caseId && !loading"
      type="info"
      :closable="false"
      title="请选择具体工作包"
      description="请从案件详情、往来文件或任务入口进入新申请递交准备页。"
      show-icon
    />

    <div v-else-if="loading" class="page-loading">
      <el-skeleton :rows="10" animated />
    </div>

    <template v-else-if="filingPackage">
      <section class="case-header">
        <div class="case-header-main">
          <div class="case-meta">
            <el-tag :type="getPackageStatusTagType(filingPackage.package.status)" size="small">
              {{ getPackageStatusText(filingPackage.package.status) }}
            </el-tag>
            <span class="meta-divider">|</span>
            <span class="case-no">工作包 {{ filingPackage.package.id }}</span>
            <span class="meta-divider">|</span>
            <router-link class="entity-link" :to="`/cases/${filingPackage.package.case_id}`">
              查看案件
            </router-link>
          </div>
          <div class="case-title">
            <h2>递交准备总览</h2>
            <p>外部系统：{{ filingPackage.package.external_system || '待确认' }}</p>
          </div>
        </div>
      </section>

      <div class="summary-grid">
        <div class="summary-card">
          <span>字段完整性</span>
          <strong>{{ getPackageStatusText(filingPackage.official_field_summary.status) }}</strong>
          <small>缺失 {{ filingPackage.official_field_summary.missing_codes.length }} 项</small>
        </div>
        <div class="summary-card">
          <span>XML zip</span>
          <strong>{{ getStatusText(filingPackage.xml_zip.status) }}</strong>
          <small>{{ filingPackage.xml_zip.file_name || filingPackage.xml_zip.placeholder || '待引用' }}</small>
        </div>
        <div class="summary-card">
          <span>合并 PDF</span>
          <strong>{{ getStatusText(filingPackage.merged_pdf_archive_status) }}</strong>
          <small>官方提交完成后归档</small>
        </div>
        <div class="summary-card">
          <span>费用摘要</span>
          <strong>{{ filingPackage.fee_summary.draft_count }} 个草单 / {{ filingPackage.fee_summary.pay_list_count }} 个清单</strong>
          <small>{{ filingPackage.fee_summary.official_template_ready ? '官方模板已确认' : '官方模板待确认' }}</small>
        </div>
      </div>

      <div class="filing-layout">
        <div class="main-stack">
          <FilingPackageChecklist
            :case-id="filingPackage.package.case_id"
            :official-field-summary="filingPackage.official_field_summary"
            :official-page-checklist="filingPackage.official_page_checklist"
          />
          <FilingPackageManifest
            :technical-disclosure-gate="filingPackage.technical_disclosure_gate"
            :commission-instruction-gate="filingPackage.commission_instruction_gate"
            :filing-file-roles="filingPackage.filing_file_roles"
            :xml-zip="filingPackage.xml_zip"
            :merged-pdf-archive-status="filingPackage.merged_pdf_archive_status"
          />
          <ReceiptArchivePanel
            :package-id="filingPackage.package.id"
            :package-kind="filingPackage.package.package_kind"
            :package-status="filingPackage.package.status"
            :archive-status="filingPackage.merged_pdf_archive_status"
            :receipt-evidence-ready="isArchiveEvidenceReady(filingPackage.merged_pdf_archive_status)"
            receipt-gate-label="新申请电子申请回执 / 合并 PDF"
            @refresh-requested="fetchPackage"
            @error="error = $event"
          />
        </div>

        <aside class="side-stack">
          <section class="case-panel side-widget">
            <div class="widget-title">审核动作</div>
            <div class="review-actions">
              <el-button
                size="small"
                type="primary"
                :loading="reviewingCode === 'PREVIEW_CONFIRMED'"
                @click="handleChecklistDone('PREVIEW_CONFIRMED', '官方页面预览已人工确认')"
              >
                确认页面预览
              </el-button>
              <el-button
                size="small"
                :loading="reviewingCode === 'SIGNATURE_CONFIRMED'"
                @click="handleChecklistDone('SIGNATURE_CONFIRMED', '签名和递交责任已由人工确认')"
              >
                确认人工签名责任
              </el-button>
              <el-button
                size="small"
                :loading="recordingOperation"
                @click="handleRecordExternalOperation"
              >
                记录导入时间
              </el-button>
            </div>
          </section>

          <section class="case-panel side-widget">
            <div class="widget-title">外部操作时间</div>
            <div v-if="externalOperationItems.length" class="operation-list">
              <div v-for="item in externalOperationItems" :key="item.item_code" class="operation-item">
                <strong>{{ getChecklistItemLabel(item) }}</strong>
                <span>{{ formatEvidenceNote(item.evidence_note, '已记录', item.item_code) }}</span>
              </div>
            </div>
            <el-empty v-else description="尚未记录外部操作时间" :image-size="70" />
          </section>

          <section class="case-panel side-widget">
            <div class="widget-title">费用摘要</div>
            <div class="fee-summary-list">
              <span>费用草单：{{ filingPackage.fee_summary.draft_count }}</span>
              <span>官费清单：{{ filingPackage.fee_summary.pay_list_count }}</span>
              <span>官方模板：{{ filingPackage.fee_summary.official_template_ready ? '已确认' : '待确认' }}</span>
              <span>阻止项：{{ filingPackage.fee_summary.blocker_count }}</span>
            </div>
          </section>
        </aside>
      </div>
    </template>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  getFilingPreparationPackage,
  recordFilingPreparationExternalOperation,
  refreshFilingPreparationPackage,
  resolveFilingPreparationPackage,
  updateFilingPreparationChecklist,
} from '../../../api/officialWorkflows'
import type {
  FilingPreparationPackage,
  OfficialWorkPackageChecklist,
} from '../../../api/officialWorkflows.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import FilingPackageChecklist from '../components/FilingPackageChecklist.vue'
import FilingPackageManifest from '../components/FilingPackageManifest.vue'
import ReceiptArchivePanel from '../../officialWorkflows/components/ReceiptArchivePanel.vue'

const route = useRoute()
const router = useRouter()

const filingPackage = ref<FilingPreparationPackage | null>(null)
const loading = ref(false)
const refreshing = ref(false)
const recordingOperation = ref(false)
const reviewingCode = ref('')
const error = ref<ApiError | null>(null)

const packageId = computed(() => String(route.query.package_id || route.query.packageId || '').trim())
const caseId = computed(() => String(route.query.case_id || route.query.caseId || '').trim())

const externalOperationItems = computed(() =>
  (filingPackage.value?.official_page_checklist || []).filter((item) =>
    item.item_code.startsWith('CNIPA_')
    || item.item_code.includes('IMPORT')
    || Boolean(item.evidence_note?.includes('T'))
  )
)

watch(packageId, (nextPackageId) => {
  if (nextPackageId && nextPackageId === filingPackage.value?.package.id) return
  void fetchPackage()
})

onMounted(() => {
  void initializePackage()
})

async function initializePackage() {
  if (packageId.value) {
    await fetchPackage()
    return
  }
  if (!caseId.value) {
    filingPackage.value = null
    return
  }

  loading.value = true
  error.value = null
  try {
    const resolved = await resolveFilingPreparationPackage(caseId.value)
    filingPackage.value = resolved
    const query = { ...route.query }
    delete query.case_id
    delete query.caseId
    await router.replace({
      query: {
        ...query,
        package_id: resolved.package.id,
      },
    })
  } catch (err) {
    error.value = localizeResolveError(err)
  } finally {
    loading.value = false
  }
}

async function fetchPackage() {
  if (!packageId.value) {
    filingPackage.value = null
    return
  }

  loading.value = true
  error.value = null
  try {
    filingPackage.value = await getFilingPreparationPackage(packageId.value)
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

async function handleRefresh() {
  if (!packageId.value) return

  refreshing.value = true
  error.value = null
  try {
    filingPackage.value = await refreshFilingPreparationPackage(packageId.value)
    ElMessage.success('工作包已刷新')
  } catch (err) {
    error.value = err as ApiError
  } finally {
    refreshing.value = false
  }
}

async function handleChecklistDone(itemCode: string, evidenceNote: string) {
  if (!packageId.value) return

  reviewingCode.value = itemCode
  error.value = null
  try {
    const result = await updateFilingPreparationChecklist(packageId.value, itemCode, {
      status: 'DONE',
      evidence_note: evidenceNote,
    })
    replaceChecklistItem(result.checklist_item)
    ElMessage.success('审核动作已记录')
  } catch (err) {
    error.value = err as ApiError
  } finally {
    reviewingCode.value = ''
  }
}

async function handleRecordExternalOperation() {
  if (!packageId.value) return

  recordingOperation.value = true
  error.value = null
  const occurredAt = new Date().toISOString()
  try {
    const result = await recordFilingPreparationExternalOperation(packageId.value, {
      operation_code: 'CNIPA_IMPORT_STARTED',
      occurred_at: occurredAt,
      note: '专利业务办理系统导入请求类表格',
    })
    replaceChecklistItem(result.checklist_item)
    ElMessage.success('导入时间已记录')
  } catch (err) {
    error.value = err as ApiError
  } finally {
    recordingOperation.value = false
  }
}

function replaceChecklistItem(item: OfficialWorkPackageChecklist) {
  if (!filingPackage.value) return
  const items = [...filingPackage.value.official_page_checklist]
  const index = items.findIndex((current) => current.item_code === item.item_code)
  if (index >= 0) {
    items.splice(index, 1, item)
  } else {
    items.push(item)
  }
  filingPackage.value = {
    ...filingPackage.value,
    official_page_checklist: items.sort((a, b) => Number(a.sort_order || 0) - Number(b.sort_order || 0)),
  }
}

function goBack() {
  router.push('/cases')
}

function localizeResolveError(value: unknown): ApiError {
  const apiError = value as ApiError
  if (apiError.status === 404) {
    return { ...apiError, message: '未找到对应案件，无法进入新申请递交准备。' }
  }
  if (apiError.status === 409) {
    return { ...apiError, message: '当前案件状态或工作包配置不允许进入新申请递交准备。' }
  }
  if (apiError.status === 422) {
    return { ...apiError, message: '案件标识格式无效，请从案件详情重新进入。' }
  }
  return { ...apiError, message: '解析新申请递交工作包失败，请稍后重试。' }
}

function getPackageStatusText(status?: string | null): string {
  const normalized = String(status || '').toUpperCase()
  if (normalized === 'PREPARING') return '准备中'
  if (normalized === 'NEEDS_MAINTENANCE') return '需维护'
  if (normalized === 'NEEDS_CONFIRMATION') return '待确认'
  if (normalized === 'READY_FOR_EXTERNAL_SUBMIT') return '可人工递交'
  if (normalized === 'SUBMITTED') return '已人工递交'
  if (normalized === 'WAITING_RECEIPT') return '等待回执'
  if (normalized === 'ARCHIVED') return '已归档'
  if (normalized === 'EXCEPTION') return '异常'
  if (normalized === 'OVERRIDE') return '已例外处理'
  if (normalized === 'READY' || normalized === 'DONE' || normalized === 'PASS') return '已满足'
  return status || '待核对'
}

function getPackageStatusTagType(status?: string | null): 'success' | 'warning' | 'danger' | 'info' {
  const normalized = String(status || '').toUpperCase()
  if (normalized === 'READY_FOR_EXTERNAL_SUBMIT' || normalized === 'ARCHIVED' || normalized === 'READY' || normalized === 'DONE') {
    return 'success'
  }
  if (normalized === 'NEEDS_MAINTENANCE' || normalized === 'EXCEPTION') return 'danger'
  if (normalized === 'NEEDS_CONFIRMATION' || normalized === 'WAITING_RECEIPT' || normalized === 'PREPARING') return 'warning'
  return 'info'
}

function getStatusText(status?: string | null): string {
  const normalized = String(status || '').toUpperCase()
  if (normalized === 'PRESENT' || normalized === 'READY' || normalized === 'DONE') return '已满足'
  if (normalized === 'MISSING') return '待维护'
  return status || '待核对'
}

function isArchiveEvidenceReady(status?: string | null): boolean {
  return ['ARCHIVED', 'PRESENT', 'READY', 'DONE', 'PASS'].includes(String(status || '').toUpperCase())
}

function getChecklistItemLabel(item: OfficialWorkPackageChecklist): string {
  if (item.item_code === 'CNIPA_IMPORT_STARTED') return '接收类表格导入'
  return item.item_label || item.item_code
}

function formatEvidenceNote(value?: string | null, fallback = '待记录', itemCode?: string | null): string {
  const raw = String(value || '').trim()
  if (!raw) return fallback

  const occurredAt = raw.match(/(?:^|;\s*)occurred_at=([^;]+)/)?.[1]
  const note = raw.match(/(?:^|;\s*)note=([^;]+)/)?.[1]
  if (!occurredAt && !note) return raw

  const parts: string[] = []
  if (occurredAt) parts.push(`操作时间：${formatOperationTime(occurredAt)}`)
  if (note) {
    parts.push(`说明：${note}`)
  } else if (itemCode === 'CNIPA_IMPORT_STARTED') {
    parts.push('说明：专利业务办理系统导入请求类表格')
  }
  return parts.join('；')
}

function formatOperationTime(value: string): string {
  return value.trim().replace('T', ' ').replace(/\.\d+.*$/, '').replace(/Z$/, '')
}
</script>

<style scoped>
.filing-preparation-page {
  display: grid;
  gap: 18px;
}

.page-subtitle {
  margin: 6px 0 0;
  color: var(--text-sub);
  font-size: 14px;
}

.page-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.summary-card {
  display: grid;
  gap: 8px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: #f8fafc;
  padding: 14px;
}

.summary-card span,
.summary-card small {
  color: var(--text-sub);
  font-size: 12px;
}

.summary-card strong {
  color: var(--text-main);
  font-size: 17px;
}

.filing-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 16px;
  align-items: start;
}

.main-stack,
.side-stack {
  display: grid;
  gap: 16px;
}

.review-actions {
  display: grid;
  gap: 8px;
}

.operation-list,
.fee-summary-list {
  display: grid;
  gap: 10px;
}

.operation-item {
  display: grid;
  gap: 4px;
  border-bottom: 1px solid #edf2f7;
  padding-bottom: 10px;
}

.operation-item span,
.fee-summary-list span {
  color: var(--text-sub);
  font-size: 13px;
}

@media (max-width: 1180px) {
  .filing-layout {
    grid-template-columns: 1fr;
  }

  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>
