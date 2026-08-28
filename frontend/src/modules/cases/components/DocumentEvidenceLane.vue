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
      <p>活动时间：{{ overlayDateText(milestone.effectiveAt) }}</p>
      <details class="audit-details">
        <summary>审计信息</summary>
        <p>活动编号：{{ milestone.activityId }}</p>
        <p>原始活动类型：{{ milestone.activityType }}</p>
        <p>来源活动编号：{{ displayValue(milestone.sourceActivityId) }}</p>
      </details>

      <div
        v-for="evidence in milestone.documentEvidence"
        :key="evidence.version.evidenceVersionId"
        class="fact-card"
      >
        <h3>文件版本</h3>
        <p>角色：{{ evidenceRoleText(evidence.version.role) }}</p>
        <p>版本：{{ evidence.version.versionNumber }}</p>
        <p>版本状态：{{ evidenceStateText(evidence.version.state) }}</p>
        <p>复核状态：{{ evidenceReviewText(evidence.version.reviewState) }}</p>
        <p>复核时间：{{ overlayDateText(evidence.version.reviewedAt) }}</p>
        <p>最终递交时间：{{ overlayDateText(evidence.version.finalSubmittedAt) }}</p>

        <div
          v-for="derivation in evidence.derivations"
          :key="derivation.evidenceDerivationId"
          class="nested-fact"
        >
          <h4>派生关系</h4>
          <p>派生类型：{{ derivationTypeText(derivation.derivationType) }}</p>
          <p>派生时间：{{ overlayDateText(derivation.derivedAt) }}</p>
        </div>

        <details class="audit-details">
          <summary>审计信息</summary>
          <p>证据版本编号：{{ evidence.version.evidenceVersionId }}</p>
          <p>文书编号：{{ evidence.version.documentId }}</p>
          <p>附件编号：{{ evidence.version.attachmentId }}</p>
          <p>谱系键：{{ evidence.version.lineageKey }}</p>
          <p>内容哈希：{{ evidence.version.contentHash }}</p>
          <p>创建人编号：{{ evidence.version.creatorId }}</p>
          <p>复核人编号：{{ displayValue(evidence.version.reviewerId) }}</p>
          <p>原始角色：{{ evidence.version.role }}</p>
          <p>原始版本状态：{{ evidence.version.state }}</p>
          <p>原始复核状态：{{ evidence.version.reviewState }}</p>
          <template v-for="derivation in evidence.derivations" :key="`audit-${derivation.evidenceDerivationId}`">
            <p>派生关系编号：{{ derivation.evidenceDerivationId }}</p>
            <p>父版本：{{ derivation.parentEvidenceVersionId }}</p>
            <p>子版本：{{ derivation.childEvidenceVersionId }}</p>
            <p>来源快照：{{ derivation.sourceSnapshot }}</p>
            <p>执行人编号：{{ derivation.actorId }}</p>
            <p>原始派生类型：{{ derivation.derivationType }}</p>
          </template>
        </details>
      </div>

      <div v-for="workPackage in milestone.workPackages" :key="workPackage.packageId" class="fact-card">
        <h3>工作包与递交</h3>
        <p>工作包类型：{{ workPackageKindText(workPackage.packageKind) }}</p>
        <p>工作包状态：{{ workPackageStatusText(workPackage.status) }}</p>
        <div class="missing-gates">
          <span>缺失门禁：</span>
          <span v-if="workPackage.missingGateCodes.length === 0">暂无</span>
          <span
            v-for="label in missingGateLabels(workPackage.missingGateCodes)"
            :key="label"
          >
            {{ label }}
          </span>
        </div>

        <div v-for="receipt in workPackage.receipts" :key="receipt.receiptId" class="nested-fact">
          <h4>官方回执</h4>
          <p>回执类型：{{ receiptKindText(receipt.receiptKind) }}</p>
          <p>受理案号：{{ displayValue(receipt.receivingCaseNo) }}</p>
          <p>收到时间：{{ overlayDateText(receipt.receivedAt) }}</p>
          <p>归档状态：{{ receiptArchiveStatusText(receipt.archiveStatus) }}</p>
        </div>

        <details class="audit-details">
          <summary>审计信息</summary>
          <p>工作包编号：{{ workPackage.packageId }}</p>
          <p>原始工作包类型：{{ workPackage.packageKind }}</p>
          <p>原始工作包状态：{{ workPackage.status }}</p>
          <p>来源文书：{{ displayValue(workPackage.sourceDocumentId) }}</p>
          <p>答复文书：{{ displayValue(workPackage.replyDocumentId) }}</p>
          <p>清单证据版本：{{ displayList(workPackage.manifestEvidenceVersionIds) }}</p>
          <p>原始缺失门禁：{{ displayList(uniqueCodes(workPackage.missingGateCodes)) }}</p>
          <template v-for="receipt in workPackage.receipts" :key="`audit-${receipt.receiptId}`">
            <p>回执编号：{{ receipt.receiptId }}</p>
            <p>回执附件：{{ displayValue(receipt.receiptAttachmentId) }}</p>
            <p>提交人：{{ displayValue(receipt.submitter) }}</p>
            <p>原始回执类型：{{ receipt.receiptKind }}</p>
            <p>原始归档状态：{{ receipt.archiveStatus }}</p>
          </template>
        </details>
      </div>

      <div v-for="task in milestone.tasks" :key="task.taskId" class="fact-card">
        <h3>关联任务</h3>
        <p>任务标题：{{ displayValue(task.title) }}</p>
        <p>任务状态：{{ taskStatusText(task.status) }}</p>
        <p>法定期限：{{ displayValue(task.dueDate) }}</p>
        <p>内部期限：{{ displayValue(task.internalDueDate) }}</p>
        <p>完成时间：{{ overlayDateText(task.doneAt) }}</p>
        <details class="audit-details">
          <summary>审计信息</summary>
          <p>任务编号：{{ task.taskId }}</p>
          <p>关联文书编号：{{ displayValue(task.documentId) }}</p>
          <p>任务模板编号：{{ displayValue(task.taskTemplateId) }}</p>
          <p>原始任务状态：{{ task.status }}</p>
        </details>
      </div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { OverlayMilestone } from '../../../api/lifecycleOverlay.types'
import {
  activityTypeText,
  derivationTypeText,
  evidenceReviewText,
  evidenceRoleText,
  evidenceStateText,
  missingGateText,
  overlayDateText,
  receiptArchiveStatusText,
  receiptKindText,
  taskStatusText,
  uniqueCodes,
  workPackageKindText,
  workPackageStatusText,
} from './lifecycleOverlayDisplay'

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
  return value || '暂无'
}

function activityTypeLabel(activityType: string): string {
  return activityTypeText(activityType)
}

function displayList(values: readonly string[]): string {
  return values.length > 0 ? values.join('、') : '暂无'
}

function missingGateLabels(values: readonly string[]): readonly string[] {
  return uniqueCodes(values).map((value) => missingGateText(value))
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
.missing-gates,
.empty-state {
  margin: 0;
  overflow-wrap: anywhere;
}

.missing-gates {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.audit-details {
  margin-top: 6px;
  padding-top: 6px;
  border-top: 1px dashed var(--color-border);
}

.audit-details summary {
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 13px;
}

.empty-state {
  margin-top: 16px;
  color: var(--text-secondary);
}
</style>
