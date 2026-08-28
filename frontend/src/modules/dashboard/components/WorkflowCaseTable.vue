<template>
  <div class="panel">
    <div class="panel-header">
      <div class="panel-title">{{ panelTitle }}</div>
      <button class="wf-fulllist-btn" @click="goFullList">
        {{ ZH.workflow.enterFullList }}
      </button>
    </div>
    <div class="wf-table-wrap">
      <table class="wf-data-table">
        <thead>
          <tr>
            <th>{{ ZH.workflow.colCaseNo }}</th>
            <th>{{ ZH.workflow.colClient }}</th>
            <th>{{ ZH.workflow.colTitle }}</th>
            <th>{{ ZH.workflow.colStep }}</th>
            <th>{{ ZH.workflow.colStatus }}</th>
            <th>{{ ZH.workflow.colAction }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!displayCases.length">
            <td colspan="6" class="muted" style="padding: 16px;">
              {{ ZH.workflow.noData }}
            </td>
          </tr>
          <tr
            v-for="c in displayCases"
            :key="c.id"
            class="clickable"
            @click="goDetail(c.id)"
          >
            <td style="font-family: monospace;">{{ c.case_no }}</td>
            <td>{{ c.client_name || '-' }}</td>
            <td>{{ c.title || '-' }}</td>
            <td>{{ getFlow(c).stepNoText }} · {{ getFlow(c).stepLabel }}</td>
            <td>
              <span class="tag" :class="getTagClass(c)">
                {{ getFlow(c).rule.legalText }}
              </span>
            </td>
            <td>
              <button class="wf-detail-btn" @click.stop="goDetail(c.id)">
                {{ ZH.workflow.viewDetail }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="totalPages > 1" class="wf-pager">
      <button class="wf-page-btn" :disabled="currentPage === 1" @click="prevPage">
        上一页
      </button>
      <span class="wf-page-text">第 {{ currentPage }} / {{ totalPages }} 页，共 {{ props.cases.length }} 条</span>
      <button class="wf-page-btn" :disabled="currentPage === totalPages" @click="nextPage">
        下一页
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import type { Case } from '../../../api/cases.types'
import { getCaseWorkflow, getStatusTagClass, WORKFLOW_STEPS } from '../../../constants/workflow'
import { ZH } from '../../../constants/labels.zh'

const props = defineProps<{
  cases: Case[]
  selectedStep: string | null
}>()

const router = useRouter()
const pageSize = 6
const currentPage = ref(1)

const panelTitle = computed(() => {
  if (props.selectedStep) {
    const step = WORKFLOW_STEPS.find(s => s.key === props.selectedStep)
    const name = step?.label || props.selectedStep
    return ZH.workflow.stageTitleFiltered.replace('{name}', name)
  }
  return ZH.workflow.stageTitleAll
})

const totalPages = computed(() => Math.max(1, Math.ceil(props.cases.length / pageSize)))

const displayCases = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return props.cases.slice(start, start + pageSize)
})

watch(
  () => [props.selectedStep, props.cases.length],
  () => {
    currentPage.value = 1
  }
)

function getWorkflowStatus(c: Case) {
  return c.workflow_status || c.status
}

function getFlow(c: Case) {
  const status = getWorkflowStatus(c)
  if (!status) {
    return {
      rule: { legalText: ZH.workflow.unknownStatus },
      stepIndex: -1,
      stepLabel: ZH.workflow.unknownStatus,
      stepNoText: ZH.workflow.stagePending,
    }
  }
  const flow = getCaseWorkflow(status)
  return {
    ...flow,
    stepLabel: flow.rule.stepText,
    stepNoText: `第${flow.stepIndex + 1}阶段/5`,
  }
}

function getTagClass(c: Case) {
  return getStatusTagClass(getWorkflowStatus(c) || '')
}

function goDetail(id: string) {
  router.push(`/cases/${id}`)
}

function goFullList() {
  if (props.selectedStep) {
    router.push({ path: '/cases', query: { step: props.selectedStep } })
  } else {
    router.push('/cases')
  }
}

function prevPage() {
  if (currentPage.value > 1) {
    currentPage.value -= 1
  }
}

function nextPage() {
  if (currentPage.value < totalPages.value) {
    currentPage.value += 1
  }
}
</script>

<style scoped>
.wf-fulllist-btn,
.wf-detail-btn {
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid var(--border, #e2e8f0);
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  background: white;
  color: var(--text-main, #0f172a);
}
.wf-fulllist-btn {
  background: var(--primary, #2563eb);
  border-color: var(--primary, #2563eb);
  color: white;
}
.wf-fulllist-btn:hover {
  filter: brightness(0.95);
}
.wf-detail-btn:hover {
  border-color: #cbd5e1;
}

.wf-pager {
  margin-top: 12px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
}

.wf-page-btn {
  padding: 6px 10px;
  border-radius: 6px;
  border: 1px solid var(--border, #e2e8f0);
  background: white;
  color: var(--text-main, #0f172a);
  font-size: 12px;
  cursor: pointer;
}

.wf-page-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.wf-page-text {
  font-size: 12px;
  color: var(--text-sub, #64748b);
}
</style>
