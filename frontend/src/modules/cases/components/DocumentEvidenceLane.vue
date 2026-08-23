<template>
  <section class="document-evidence-lane" data-testid="document-evidence-lane">
    <header class="lane-header">
      <p class="lane-kicker">左侧证据线</p>
      <h2>文件驱动</h2>
    </header>

    <p v-if="documentMilestones.length === 0" class="empty-state">暂无文件证据事实</p>
    <article
      v-for="milestone in documentMilestones"
      :key="milestone.activityId"
      class="document-milestone"
    >
      <p>活动类型：{{ activityTypeLabel(milestone.activityType) }}</p>
      <p>活动时间：{{ milestone.effectiveAt }}</p>

      <div
        v-for="evidence in milestone.documentEvidence"
        :key="evidence.version.evidenceVersionId"
        class="fact-card"
      >
        <h3>文件版本</h3>
        <p>角色：{{ evidence.version.role }}</p>
        <p>版本：{{ evidence.version.versionNumber }}</p>
        <p>版本状态：{{ evidence.version.state }}</p>
        <p>复核状态：{{ evidence.version.reviewState }}</p>
        <p>文书编号：{{ evidence.version.documentId }}</p>
        <p>附件编号：{{ evidence.version.attachmentId }}</p>
        <p>谱系键：{{ evidence.version.lineageKey }}</p>
        <p>内容哈希：{{ evidence.version.contentHash }}</p>
        <p>最终递交时间：{{ displayValue(evidence.version.finalSubmittedAt) }}</p>

        <div
          v-for="derivation in evidence.derivations"
          :key="derivation.evidenceDerivationId"
          class="nested-fact"
        >
          <h4>派生关系</h4>
          <p>派生类型：{{ derivation.derivationType }}</p>
          <p>父版本：{{ derivation.parentEvidenceVersionId }}</p>
          <p>子版本：{{ derivation.childEvidenceVersionId }}</p>
          <p>来源快照：{{ derivation.sourceSnapshot }}</p>
        </div>
      </div>

      <div v-for="workPackage in milestone.workPackages" :key="workPackage.packageId" class="fact-card">
        <h3>工作包与递交</h3>
        <p>工作包编号：{{ workPackage.packageId }}</p>
        <p>工作包类型：{{ workPackage.packageKind }}</p>
        <p>工作包状态：{{ workPackage.status }}</p>
        <p>来源文书：{{ displayValue(workPackage.sourceDocumentId) }}</p>
        <p>答复文书：{{ displayValue(workPackage.replyDocumentId) }}</p>
        <p>缺失门禁：{{ displayList(workPackage.missingGateCodes) }}</p>

        <div v-for="receipt in workPackage.receipts" :key="receipt.receiptId" class="nested-fact">
          <h4>官方回执</h4>
          <p>回执类型：{{ receipt.receiptKind }}</p>
          <p>回执附件：{{ displayValue(receipt.receiptAttachmentId) }}</p>
          <p>受理案号：{{ displayValue(receipt.receivingCaseNo) }}</p>
          <p>收到时间：{{ displayValue(receipt.receivedAt) }}</p>
          <p>归档状态：{{ receipt.archiveStatus }}</p>
        </div>
      </div>

      <div v-for="task in milestone.tasks" :key="task.taskId" class="fact-card">
        <h3>关联任务</h3>
        <p>任务标题：{{ displayValue(task.title) }}</p>
        <p>任务状态：{{ task.status }}</p>
        <p>法定期限：{{ displayValue(task.dueDate) }}</p>
        <p>内部期限：{{ displayValue(task.internalDueDate) }}</p>
        <p>完成时间：{{ displayValue(task.doneAt) }}</p>
      </div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { OverlayMilestone } from '../../../api/lifecycleOverlay.types'

const ACTIVITY_TYPE_LABELS: Readonly<Record<string, string>> = {
  FILING_PREPARATION_STARTED: '申请文件准备已开始',
  DOCUMENT_EVIDENCE_VERSION_REGISTERED: '文件证据版本已登记',
  DOCUMENT_EVIDENCE_REVIEW_DECIDED: '文件证据复核结论已记录',
  DOCUMENT_EVIDENCE_EXTERNAL_SUBMISSION_FINALIZED: '外部递交文件已定稿',
  FILING_EXTERNAL_SUBMISSION_RECORDED: '申请文件已递交',
  FILING_RECEIPT_ARCHIVED: '申请回执已归档',
  ACCEPTANCE_NOTICE_RECORDED: '受理通知已登记',
  PRELIMINARY_EXAMINATION_STARTED: '初步审查已开始',
  PRELIMINARY_EXAMINATION_PASSED: '初步审查已通过',
  PUBLICATION_NOTICE_RECORDED: '公布通知已登记',
  SUBSTANTIVE_EXAMINATION_STARTED: '实质审查已开始',
  OA_NOTICE_RECORDED: '审查意见通知已登记',
  OA_EXTERNAL_SUBMISSION_RECORDED: '审查意见答复已递交',
  OA_RECEIPT_ARCHIVED: '审查意见答复回执已归档',
}

const props = defineProps<{
  milestones: readonly OverlayMilestone[]
}>()

const documentMilestones = computed(() =>
  props.milestones.filter(
    (milestone) =>
      milestone.documentEvidence.length > 0 ||
      milestone.workPackages.length > 0 ||
      milestone.tasks.length > 0,
  ),
)

function displayValue(value: string | null): string {
  return value ?? '-'
}

function activityTypeLabel(activityType: string): string {
  return ACTIVITY_TYPE_LABELS[activityType] ?? '活动类型待确认'
}

function displayList(values: readonly string[]): string {
  return values.length > 0 ? values.join('、') : '-'
}
</script>

<style scoped>
.document-evidence-lane {
  min-width: 0;
  padding: 18px;
  border: 1px solid var(--color-border);
  border-radius: 14px;
  background: var(--bg-card);
}

.lane-header h2,
.fact-card h3,
.nested-fact h4 {
  margin: 0;
}

.lane-kicker {
  margin: 0 0 4px;
  color: var(--el-color-info);
  font-size: 12px;
  font-weight: 600;
}

.document-milestone,
.fact-card,
.nested-fact {
  display: grid;
  gap: 6px;
}

.document-milestone {
  margin-top: 16px;
}

.fact-card {
  padding: 12px;
  border: 1px solid var(--color-border);
  border-radius: 10px;
}

.nested-fact {
  margin-top: 4px;
  padding: 10px;
  background: var(--bg-page);
}

.document-milestone p,
.fact-card p,
.nested-fact p,
.empty-state {
  margin: 0;
  overflow-wrap: anywhere;
}

.empty-state {
  margin-top: 16px;
  color: var(--text-secondary);
}
</style>
