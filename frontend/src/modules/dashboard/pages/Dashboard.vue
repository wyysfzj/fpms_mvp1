<template>
  <div class="dashboard-page">
    <!-- Header: title + date -->
    <div class="dashboard-header">
      <h1 class="dashboard-title">{{ ZH.dashboard.title }}</h1>
      <span class="dashboard-date">{{ todayDate }}</span>
    </div>

    <!-- Error banner -->
    <el-alert
      v-if="error"
      :title="error"
      type="error"
      show-icon
      :closable="false"
      style="margin-bottom: 16px;"
    />

    <!-- Pipeline Cards -->
    <div class="dashboard-only">
      <div class="pipeline-grid">
        <el-skeleton v-if="pipeLoading" :rows="2" animated style="height: 140px;" />
        <el-skeleton v-if="pipeLoading" :rows="2" animated style="height: 140px;" />
        <el-skeleton v-if="pipeLoading" :rows="2" animated style="height: 140px;" />
        <el-skeleton v-if="pipeLoading" :rows="2" animated style="height: 140px;" />
        <template v-if="!pipeLoading">
          <PipeCard
            :bar-color="'var(--color-primary)'"
            :value="pipe.newCasesCount"
            :label="ZH.pipeline.newCases"
            hint="+ 新建案件"
            @click="showDrawer = true"
          />
          <PipeCard
            :bar-color="'var(--color-warning)'"
            :value="pipe.pendingTasksCount"
            :label="ZH.pipeline.pendingTasks"
            :badge="pipe.urgentTasksCount > 0
              ? { text: pipe.urgentTasksCount + ' ' + ZH.pipeline.urgentSuffix, class: 'urgent' }
              : undefined"
            @click="$router.push('/tasks')"
          />
          <PipeCard
            :bar-color="'var(--color-purple)'"
            :value="formatMoney(pipe.unbilledDraftsAmount)"
            :label="ZH.pipeline.unbilledDrafts"
            @click="$router.push('/fees/drafts')"
          />
          <PipeCard
            :bar-color="'var(--color-success)'"
            :value="formatMoney(pipe.unallocatedPaymentsAmount)"
            :label="ZH.pipeline.unallocated"
            @click="$router.push('/billing/payments')"
          />
        </template>
      </div>

      <!-- Workflow Overview (V3) -->
      <el-skeleton v-if="wfLoading" :rows="3" animated style="margin-bottom: 16px;" />
      <WorkflowOverview
        v-if="!wfLoading"
        :steps="wfStats.steps"
        :total="wfStats.total"
        :selected-step="selectedStep"
        @select="onSelectStep"
        @clear="onClearStep"
      />

      <!-- Split Grid: Case Table + Finance Panel -->
      <div class="split-grid">
        <WorkflowCaseTable
          v-if="!wfLoading"
          :cases="filteredCases"
          :selected-step="selectedStep"
        />
        <FinancePanel :items="financeItems" :loading="financeLoading" />
      </div>

      <div style="margin-top: 16px;">
        <TodoTable :tasks="todayTasks" :loading="todayLoading" />
      </div>

      <!-- Action Center (below split grid) -->
      <div style="margin-top: 16px;">
        <ActionCenter :tasks="enrichedTasks" :loading="tasksLoading" />
      </div>
    </div>

    <!-- New Case Drawer -->
    <NewCaseDrawer
      :visible="showDrawer"
      @update:visible="showDrawer = $event"
      @created="onCaseCreated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ZH } from '../../../constants/labels.zh'
import PipeCard from '../components/PipeCard.vue'
import ActionCenter from '../components/ActionCenter.vue'
import FinancePanel from '../components/FinancePanel.vue'
import NewCaseDrawer from '../components/NewCaseDrawer.vue'
import WorkflowOverview from '../components/WorkflowOverview.vue'
import WorkflowCaseTable from '../components/WorkflowCaseTable.vue'
import TodoTable from '../components/TodoTable.vue'
import { getTodayReminders } from '../../../api/tasks'
import {
  fetchPipelineKpi,
  fetchEnrichedTasks,
  fetchFinanceData,
  fetchWorkflowStats,
  filterCasesByStep,
} from '../dashboard.api'
import type { PipelineKpi, WorkflowStats } from '../dashboard.api'
import type { EnrichedTask } from '../components/ActionCenter.vue'
import type { FinanceItem } from '../components/FinanceRow.vue'
import type { Task } from '../../../api/tasks.types'

const router = useRouter()

// --- State ---
const pipeLoading = ref(true)
const tasksLoading = ref(true)
const todayLoading = ref(true)
const financeLoading = ref(true)
const wfLoading = ref(true)
const error = ref<string | null>(null)
const showDrawer = ref(false)
const selectedStep = ref<string | null>(null)

const pipe = ref<PipelineKpi>({
  newCasesCount: 0,
  pendingTasksCount: 0,
  urgentTasksCount: 0,
  unbilledDraftsAmount: 0,
  unallocatedPaymentsAmount: 0,
})

const wfStats = ref<WorkflowStats>({
  steps: [],
  total: 0,
  cases: [],
})

const enrichedTasks = ref<EnrichedTask[]>([])
const todayTasks = ref<Task[]>([])
const financeItems = ref<FinanceItem[]>([])

const filteredCases = computed(() =>
  filterCasesByStep(wfStats.value.cases, selectedStep.value)
)

const todayDate = new Date().toLocaleDateString('zh-CN', {
  year: 'numeric',
  month: 'long',
  day: 'numeric',
  weekday: 'long',
})

// --- Helpers ---
function formatMoney(amount: number): string {
  return '¥' + amount.toLocaleString('zh-CN', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  })
}

function onCaseCreated(caseId: string) {
  router.push(`/cases/${caseId}`)
}

function onSelectStep(stepKey: string) {
  selectedStep.value = stepKey
}

function onClearStep() {
  selectedStep.value = null
}

// --- Data loading ---
onMounted(async () => {
  const pipePromise = fetchPipelineKpi()
    .then(data => { pipe.value = data })
    .catch(err => { error.value = err?.message || '加载流程指标失败' })
    .finally(() => { pipeLoading.value = false })

  const tasksPromise = fetchEnrichedTasks()
    .then(data => { enrichedTasks.value = data })
    .catch(err => { error.value = err?.message || '加载待办任务失败' })
    .finally(() => { tasksLoading.value = false })

  const todayPromise = getTodayReminders('worker')
    .then(data => { todayTasks.value = data.items.slice(0, 10) })
    .catch(err => { error.value = err?.message || '加载今日提醒失败' })
    .finally(() => { todayLoading.value = false })

  const financePromise = fetchFinanceData()
    .then(data => { financeItems.value = data })
    .catch(err => { error.value = err?.message || '加载财务数据失败' })
    .finally(() => { financeLoading.value = false })

  const wfPromise = fetchWorkflowStats()
    .then(data => { wfStats.value = data })
    .catch(err => { error.value = err?.message || '加载工作流失败' })
    .finally(() => { wfLoading.value = false })

  await Promise.all([pipePromise, tasksPromise, todayPromise, financePromise, wfPromise])
})
</script>
