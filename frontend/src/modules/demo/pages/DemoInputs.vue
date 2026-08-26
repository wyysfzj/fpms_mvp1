<template>
  <section class="demo-inputs-page" data-testid="demo-inputs-page">
    <header class="hero">
      <div>
        <p class="eyebrow">主持人预检 · 只读</p>
        <h1>演示输入与空业务库</h1>
        <p>本页仅用于客户操作前核对本地合成演示输入，不会创建或修改任何业务对象。</p>
      </div>
      <el-button
        data-testid="demo-inputs-preflight"
        type="primary"
        :loading="loading"
        @click="loadPreflight"
      >
        校验演示输入与空业务库
      </el-button>
      <el-button
        data-testid="demo-inputs-finalize"
        type="warning"
        :loading="exporting"
        :disabled="!sessionActive"
        @click="finalizeEvidence"
      >
        完成并导出本轮证据
      </el-button>
    </header>

    <ApiErrorBanner v-if="error" :error="error" :dismissable="false" />
    <el-alert
      v-if="sessionMessage"
      :title="sessionMessage"
      :type="sessionMessageType"
      :closable="false"
    />

    <template v-if="preflight">
      <el-alert
        data-testid="demo-inputs-boundary"
        title="当前输入属于合成测试范围；未经客户授权，不得作为正式模板或费率启用。"
        type="warning"
        :closable="false"
        show-icon
      />

      <el-card class="input-card" data-testid="demo-inputs-provenance">
        <template #header><strong>输入校验与来源</strong></template>
        <dl class="facts">
          <div><dt>就绪状态</dt><dd data-testid="input-readiness">{{ preflight.readiness }}</dd></div>
          <div><dt>授权分类</dt><dd data-testid="input-classification">{{ preflight.authority_classification }}</dd></div>
          <div><dt>允许客户激活</dt><dd data-testid="input-customer-activation">{{ preflight.customer_activation_eligible ? '是' : '否' }}</dd></div>
          <div><dt>Bundle ID / 版本</dt><dd>{{ preflight.bundle_id }} / {{ preflight.bundle_version }}</dd></div>
          <div><dt>Manifest SHA-256</dt><dd class="hash">{{ preflight.manifest_sha256 }}</dd></div>
          <div><dt>模板代码</dt><dd>{{ preflight.template_code }}</dd></div>
          <div><dt>模板文件 SHA-256</dt><dd class="hash">{{ preflight.template_sha256 }}</dd></div>
          <div><dt>费率项目代码</dt><dd>{{ preflight.item_code }} · {{ preflight.name_zh_cn }}</dd></div>
          <div><dt>费率来源</dt><dd>{{ preflight.source_ref }}</dd></div>
          <div><dt>费率来源版本</dt><dd>{{ preflight.source_version }}</dd></div>
          <div><dt>费率来源 SHA-256</dt><dd class="hash">{{ preflight.source_sha256 }}</dd></div>
          <div><dt>服务费</dt><dd>{{ preflight.amount }} {{ preflight.currency }}</dd></div>
          <div><dt>官方费用</dt><dd>官方费用：未配置（不计入总额）</dd></div>
        </dl>
        <el-alert
          data-testid="demo-inputs-disclaimer"
          :title="preflight.disclaimer_zh_cn"
          type="warning"
          :closable="false"
          class="disclaimer"
        />
      </el-card>

      <el-card class="input-card" data-testid="demo-business-counts">
        <template #header><strong>本轮业务对象计数</strong></template>
        <p class="count-note">开始演示前，以下完整业务表计数应全部为 0。</p>
        <div class="count-grid">
          <div v-for="item in businessCountItems" :key="item.key" class="count-item">
            <span>{{ item.label }}</span>
            <strong :data-testid="`business-count-${item.key}`">
              {{ businessCount(item.key) }}
            </strong>
          </div>
        </div>
      </el-card>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import { DEMO_BUSINESS_COUNT_KEYS } from '../demo.contract'
import { readDemoPreflight } from '../demo.api'
import type { DemoPreflight } from '../demo.api'
import {
  activateDemoUiSession,
  DEMO_UI_SESSION_CHANGE_EVENT,
  finalizeDemoUiSessionEvidence,
  isDemoUiSessionActive,
  stopDemoUiSession,
} from '../demoUiSession'

type BusinessCountKey = (typeof DEMO_BUSINESS_COUNT_KEYS)[number]

const businessCountItems: ReadonlyArray<{ key: BusinessCountKey; label: string }> =
  DEMO_BUSINESS_COUNT_KEYS.map((key) => ({ key, label: key }))

const preflight = ref<DemoPreflight | null>(null)
const error = ref<ApiError | null>(null)
const loading = ref(false)
const exporting = ref(false)
const sessionActive = ref(isDemoUiSessionActive())
const sessionMessage = ref<string | null>(null)
const sessionMessageType = computed(() => sessionActive.value ? 'success' : 'warning')

function syncDemoSession(): void {
  sessionActive.value = isDemoUiSessionActive()
}

function businessCount(key: BusinessCountKey): number {
  return preflight.value?.business_counts[key] ?? 0
}

async function loadPreflight(): Promise<void> {
  loading.value = true
  error.value = null
  preflight.value = null
  sessionMessage.value = null
  try {
    preflight.value = await readDemoPreflight()
    if (await activateDemoUiSession(preflight.value)) {
      sessionMessage.value = '合成演示会话已通过当前预检绑定。'
    } else {
      sessionMessage.value = '预检绑定与当前会话不一致，已停止本轮演示。'
    }
  } catch (caught) {
    error.value = caught as ApiError
    stopDemoUiSession('PREFLIGHT_FAILED')
  } finally {
    loading.value = false
  }
}

async function finalizeEvidence(): Promise<void> {
  if (!sessionActive.value) return
  exporting.value = true
  sessionMessage.value = null
  try {
    await finalizeDemoUiSessionEvidence()
    sessionMessage.value = '本轮观察证据已导出。'
  } catch {
    sessionMessage.value = '观察证据导出失败，本轮演示已停止。'
  } finally {
    exporting.value = false
  }
}

onMounted(() => window.addEventListener(DEMO_UI_SESSION_CHANGE_EVENT, syncDemoSession))
onBeforeUnmount(() => window.removeEventListener(DEMO_UI_SESSION_CHANGE_EVENT, syncDemoSession))
</script>

<style scoped>
.demo-inputs-page {
  display: grid;
  gap: 20px;
  max-width: 1120px;
  margin: 0 auto;
  padding: 28px;
}

.hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

.hero h1,
.hero p {
  margin: 0;
}

.eyebrow {
  margin-bottom: 6px !important;
  color: var(--el-color-primary);
  font-size: 12px;
  font-weight: 700;
}

.input-card {
  border-radius: 14px;
}

.facts {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px 24px;
  margin: 0;
}

.facts div {
  min-width: 0;
}

.facts dt {
  color: var(--text-secondary);
  font-size: 12px;
}

.facts dd {
  margin: 4px 0 0;
  overflow-wrap: anywhere;
}

.hash {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 12px;
}

.disclaimer {
  margin-top: 18px;
}

.count-note {
  margin: 0 0 14px;
  color: var(--text-secondary);
}

.count-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12px;
}

.count-item {
  display: grid;
  gap: 5px;
  padding: 12px;
  border: 1px solid var(--color-border);
  border-radius: 10px;
}

.count-item strong {
  font-size: 24px;
}

@media (max-width: 800px) {
  .hero {
    align-items: flex-start;
    flex-direction: column;
  }

  .facts,
  .count-grid {
    grid-template-columns: 1fr;
  }
}
</style>
