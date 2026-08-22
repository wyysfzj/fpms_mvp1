<template>
  <section class="demo-page">
    <header class="hero">
      <div>
        <p class="eyebrow">LOCAL ABC E2E · DEMO_ONLY</p>
        <h1>客户账单、回款与核销演示</h1>
        <p>所有金额与模板均来自当前只读 runtime bundle；本页不代表生产费率或正式模板。</p>
      </div>
      <el-tag :type="demoReady ? 'success' : bundle ? 'info' : 'warning'" size="large">
        {{ demoReady
          ? `演示输入已校验 · ${preflight?.authority_classification}`
          : bundle ? '演示输入已加载，尚未通过全新环境校验' : '等待演示输入' }}
      </el-tag>
    </header>

    <el-alert v-if="errorMessage" :title="errorMessage" type="error" show-icon :closable="false" />

    <el-card class="step-card">
      <template #header><strong>1. Runtime bundle</strong></template>
      <div class="actions">
        <el-button data-testid="demo-preflight" :loading="loading === 'preflight'" type="primary" @click="validatePreflight">校验全新演示环境</el-button>
        <el-button :loading="loading === 'bundle'" @click="loadBundle">读取输入</el-button>
      </div>
      <dl v-if="bundle" class="facts">
        <div><dt>Bundle ID / 版本</dt><dd><span data-testid="bundle-id">{{ bundle.bundle_id }}</span> / <span data-testid="bundle-version">{{ bundle.bundle_version }}</span></dd></div>
        <div><dt>Manifest SHA-256</dt><dd data-testid="manifest-sha256" class="hash">{{ bundle.manifest_sha256 }}</dd></div>
        <div><dt>模板代码</dt><dd data-testid="template-code">{{ bundle.template_code }}</dd></div>
        <div><dt>模板文件 SHA-256</dt><dd data-testid="template-sha256" class="hash">{{ bundle.template_sha256 }}</dd></div>
        <div><dt>费率项目代码</dt><dd><span data-testid="rate-item-code">{{ bundle.item_code }}</span> · {{ bundle.name_zh_cn }}</dd></div>
        <div><dt>费率来源</dt><dd data-testid="rate-source-ref">{{ bundle.source_ref }}</dd></div>
        <div><dt>费率来源版本</dt><dd data-testid="rate-source-version">{{ bundle.source_version }}</dd></div>
        <div><dt>费率来源 SHA-256</dt><dd data-testid="rate-source-sha256" class="hash">{{ bundle.source_sha256 }}</dd></div>
        <div><dt>服务费</dt><dd>{{ money(bundle.amount) }} {{ bundle.currency }}</dd></div>
        <div><dt>官方费用</dt><dd>官方费用：未配置（不计入总额）</dd></div>
      </dl>
      <el-alert v-if="bundle" data-testid="demo-disclaimer" :title="bundle.disclaimer_zh_cn" type="warning" :closable="false" class="disclaimer" />
    </el-card>

    <el-card class="step-card">
      <template #header><strong>2. 选择已创建案件</strong></template>
      <p class="hint">
        先通过 <router-link to="/clients/new">客户管理</router-link> 和
        <router-link to="/cases/new">案件管理</router-link> 创建虚构演示数据，再输入页面可见的案号。
      </p>
      <el-form inline @submit.prevent="loadCase">
        <el-form-item label="案号">
          <el-input v-model.trim="caseNoInput" data-testid="demo-case-no" placeholder="例如：DEMO-CASE-001" style="width: 360px" />
        </el-form-item>
        <el-button type="primary" :loading="loading === 'case'" @click="loadCase">加载案件</el-button>
      </el-form>
      <p v-if="selectedCase" class="success-line">
        已选择 {{ selectedCase.case_no }} · 客户 {{ selectedCase.client_id }}
      </p>
    </el-card>

    <el-card class="step-card">
      <template #header><strong>3. 服务费义务 → PAY → 锁定草单</strong></template>
      <div class="actions">
        <el-button data-testid="create-obligation" :disabled="!selectedCase || !demoReady" :loading="loading === 'obligation'" @click="createObligation">生成服务费义务</el-button>
        <el-button data-testid="create-draft" :disabled="!obligation" :loading="loading === 'draft'" @click="confirmPayAndLock">确认 PAY 并锁定草单</el-button>
      </div>
      <p v-if="obligation" class="success-line">义务 {{ obligation.obligation.id }} · {{ money(obligation.amount) }} CNY</p>
      <p v-if="draft" class="success-line">草单 {{ draft.id }} · {{ draft.status }} · {{ money(draft.amount) }} CNY</p>
    </el-card>

    <el-card class="step-card">
      <template #header><strong>4. 唯一客户 AR 账单</strong></template>
      <el-button data-testid="create-bill" type="primary" :disabled="draft?.status !== 'LOCKED'" :loading="loading === 'bill'" @click="createBill">生成账单</el-button>
      <dl v-if="bill" class="facts">
        <div><dt>账单</dt><dd>{{ bill.bill_no }} / {{ bill.status }}</dd></div>
        <div><dt>应收</dt><dd>{{ money(bill.amount) }} CNY</dd></div>
        <div><dt>余额</dt><dd>{{ money(bill.balance) }} CNY</dd></div>
      </dl>
    </el-card>

    <el-card class="step-card">
      <template #header><strong>5. 等额客户银行回款</strong></template>
      <el-button data-testid="create-payment" :disabled="!bill || bill.status !== 'UNSETTLED'" :loading="loading === 'payment'" @click="createPayment">登记回款</el-button>
      <dl v-if="payment" class="facts">
        <div><dt>回款</dt><dd>{{ payment.payment.pay_no }} / {{ payment.payment.pay_method }}</dd></div>
        <div><dt>银行参考号</dt><dd>{{ payment.payment.bank_ref_no }}</dd></div>
        <div><dt>待核销</dt><dd>{{ money(payment.line.balance_amt) }} CNY · {{ payment.line.status }}</dd></div>
      </dl>
    </el-card>

    <el-card class="step-card">
      <template #header><strong>6. 全额核销与案件收款闭环</strong></template>
      <el-button data-testid="create-offset" type="success" :disabled="!payment || payment.line.status !== 'UNALLOCATED'" :loading="loading === 'offset'" @click="createOffset">核销并结清</el-button>
      <dl v-if="offset" class="facts final-state">
        <div><dt>账单状态</dt><dd>{{ offset.bill.status }} / 余额 {{ money(offset.bill.balance) }} CNY</dd></div>
        <div><dt>回款状态</dt><dd>{{ offset.line.status }} / 余额 {{ money(offset.line.balance_amt) }} CNY</dd></div>
        <div><dt>案件收款</dt><dd>{{ money(offset.case_receipt.received_amt) }} / {{ money(offset.case_receipt.receivable_amt) }} CNY</dd></div>
      </dl>
    </el-card>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { getCaseByCaseNo } from '../../../api/cases'
import type { Case } from '../../../api/cases.types'
import {
  createDemoBankReceipt,
  createDemoBill,
  createDemoDraft,
  createDemoFullOffset,
  createDemoServiceObligation,
  lockDemoDraft,
  readDemoBillCommand,
  readDemoDraft,
  readDemoOffsetCommand,
  readDemoPaymentCommand,
  readDemoServiceObligation,
  readDemoServiceItem,
  readDemoPreflight,
  recordDemoPayInstruction,
} from '../demo.api'
import type {
  DemoBankReceiptResponse,
  DemoBillDetail,
  DemoDraft,
  DemoFeeObligationResponse,
  DemoOffsetResponse,
  DemoPreflight,
  DemoServiceItem,
} from '../demo.api'
import { parseDemoPreflight } from '../demo.contract'

const bundle = ref<DemoServiceItem>()
const preflight = ref<DemoPreflight>()
const demoReady = computed(() => preflight.value?.readiness === 'READY')
const selectedCase = ref<Case>()
const caseNoInput = ref('')
const obligation = ref<DemoFeeObligationResponse>()
const draft = ref<DemoDraft>()
const bill = ref<DemoBillDetail>()
const payment = ref<DemoBankReceiptResponse>()
const offset = ref<DemoOffsetResponse>()
const loading = ref('')
const errorMessage = ref('')

const idempotencyKeys = reactive({
  obligation: crypto.randomUUID(),
  instruction: crypto.randomUUID(),
  bill: crypto.randomUUID(),
  payment: crypto.randomUUID(),
  offset: crypto.randomUUID(),
})

const today = new Date().toISOString().slice(0, 10)
const due = new Date(Date.now() + 15 * 86_400_000).toISOString().slice(0, 10)
const suffix = crypto.randomUUID().slice(0, 8).toUpperCase()
const DEMO_SESSION_KEY = 'fpms_demo_abc_session_v1'

interface StoredDemoSession {
  preflight: DemoPreflight
  case_no?: string
  obligation_id?: string
  draft_id?: string
  idempotency_keys: typeof idempotencyKeys
}

function sameProvenance(saved: DemoPreflight, currentBundle: DemoServiceItem): boolean {
  return saved.bundle_id === currentBundle.bundle_id
    && saved.bundle_version === currentBundle.bundle_version
    && saved.manifest_sha256 === currentBundle.manifest_sha256
    && saved.template_code === currentBundle.template_code
    && saved.template_sha256 === currentBundle.template_sha256
    && saved.item_code === currentBundle.item_code
    && saved.source_ref === currentBundle.source_ref
    && saved.source_version === currentBundle.source_version
    && saved.source_sha256 === currentBundle.source_sha256
}

function persistSession() {
  if (!preflight.value) return
  const state: StoredDemoSession = {
    preflight: preflight.value,
    case_no: selectedCase.value?.case_no,
    obligation_id: obligation.value?.obligation.id,
    draft_id: draft.value?.id,
    idempotency_keys: { ...idempotencyKeys },
  }
  sessionStorage.setItem(DEMO_SESSION_KEY, JSON.stringify(state))
}

function readStoredSession(currentBundle: DemoServiceItem): StoredDemoSession | undefined {
  const raw = sessionStorage.getItem(DEMO_SESSION_KEY)
  if (!raw) return undefined
  try {
    const value = JSON.parse(raw) as Partial<StoredDemoSession>
    const saved = { ...value, preflight: parseDemoPreflight(value.preflight) }
    if (saved.preflight.manifest_sha256 !== currentBundle.manifest_sha256
      || !sameProvenance(saved.preflight, currentBundle)
      || !saved.idempotency_keys) {
      sessionStorage.removeItem(DEMO_SESSION_KEY)
      return undefined
    }
    return saved as StoredDemoSession
  } catch {
    sessionStorage.removeItem(DEMO_SESSION_KEY)
    return undefined
  }
}

function money(value: string): string {
  if (!/^(?:0|[1-9]\d*)\.\d{2}$/.test(value)) return '数据异常'
  return value
}

function messageOf(error: unknown): string {
  if (typeof error === 'object' && error !== null && 'message' in error) {
    return String((error as { message: unknown }).message)
  }
  return '操作失败，请核对当前步骤后重试。'
}

async function run(step: string, action: () => Promise<void>) {
  loading.value = step
  errorMessage.value = ''
  try {
    await action()
  } catch (error) {
    errorMessage.value = messageOf(error)
  } finally {
    loading.value = ''
  }
}

async function loadBundle() {
  await run('bundle', async () => { bundle.value = await readDemoServiceItem() })
}

async function validatePreflight() {
  preflight.value = undefined
  await run('preflight', async () => {
    const result = await readDemoPreflight()
    preflight.value = result
    bundle.value = result
    persistSession()
  })
}

async function loadCase() {
  if (!caseNoInput.value) return
  await run('case', async () => {
    selectedCase.value = await getCaseByCaseNo(caseNoInput.value)
    persistSession()
  })
}

async function createObligation() {
  if (!selectedCase.value || !bundle.value || !demoReady.value) return
  await run('obligation', async () => {
    obligation.value = await createDemoServiceObligation(
      selectedCase.value!.id,
      bundle.value!.item_code,
      idempotencyKeys.obligation,
    )
    persistSession()
  })
}

async function confirmPayAndLock() {
  if (!selectedCase.value?.client_id || !obligation.value) return
  await run('draft', async () => {
    await recordDemoPayInstruction(obligation.value!.obligation.id, idempotencyKeys.instruction)
    const created = await createDemoDraft(
      selectedCase.value!.id,
      String(selectedCase.value!.client_id),
      obligation.value!.obligation.id,
    )
    draft.value = await lockDemoDraft(created.id)
    persistSession()
  })
}

async function createBill() {
  if (!draft.value) return
  await run('bill', async () => {
    const result = await createDemoBill(
      draft.value!.id,
      `DEMO-AR-${suffix}`,
      today,
      due,
      idempotencyKeys.bill,
    )
    bill.value = result.bill
    persistSession()
  })
}

async function createPayment() {
  if (!bill.value) return
  await run('payment', async () => {
    payment.value = await createDemoBankReceipt(
      bill.value!,
      `DEMO-PAY-${suffix}`,
      `DEMO-BANK-${suffix}`,
      today,
      idempotencyKeys.payment,
    )
    persistSession()
  })
}

async function createOffset() {
  if (!payment.value || !bill.value) return
  await run('offset', async () => {
    offset.value = await createDemoFullOffset(
      payment.value!.line,
      bill.value!,
      today,
      idempotencyKeys.offset,
    )
    bill.value = offset.value.bill
    payment.value = { ...payment.value!, line: offset.value.line, bill: offset.value.bill }
    persistSession()
  })
}

async function restoreSession() {
  await run('bundle', async () => {
    const currentBundle = await readDemoServiceItem()
    bundle.value = currentBundle
    const saved = readStoredSession(currentBundle)
    if (!saved) return

    preflight.value = saved.preflight
    Object.assign(idempotencyKeys, saved.idempotency_keys)
    if (saved.case_no) {
      selectedCase.value = await getCaseByCaseNo(saved.case_no)
      caseNoInput.value = saved.case_no
    }
    if (saved.obligation_id && selectedCase.value) {
      obligation.value = await readDemoServiceObligation(
        saved.obligation_id,
        selectedCase.value.id,
        currentBundle,
        idempotencyKeys.obligation,
      )
    }
    if (saved.draft_id) {
      const restoredDraft = await readDemoDraft(saved.draft_id)
      if (restoredDraft.case_id !== selectedCase.value?.id) throw new Error('演示草单与当前案件不一致')
      draft.value = restoredDraft
    }
    const billResult = await readDemoBillCommand(idempotencyKeys.bill)
    if (billResult) bill.value = billResult.bill
    const paymentResult = await readDemoPaymentCommand(idempotencyKeys.payment)
    if (paymentResult) payment.value = paymentResult
    const offsetResult = await readDemoOffsetCommand(idempotencyKeys.offset)
    if (offsetResult) {
      if (offsetResult.bill.case_id !== selectedCase.value?.id) throw new Error('演示核销与当前案件不一致')
      offset.value = offsetResult
      bill.value = offsetResult.bill
      if (payment.value) {
        payment.value = { ...payment.value, line: offsetResult.line, bill: offsetResult.bill }
      }
    }
  })
}

onMounted(restoreSession)
</script>

<style scoped>
.demo-page { max-width: 1080px; margin: 0 auto; padding: 24px; }
.hero { display: flex; justify-content: space-between; gap: 24px; align-items: flex-start; margin-bottom: 20px; }
.hero h1 { margin: 4px 0 8px; }
.eyebrow { color: #2563eb; font-weight: 700; letter-spacing: .08em; }
.step-card { margin-top: 16px; }
.hint { color: #64748b; }
.actions { display: flex; gap: 12px; }
.success-line { color: #15803d; font-weight: 600; }
.facts { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px 24px; margin-top: 18px; }
.facts div { min-width: 0; }
.facts dt { color: #64748b; font-size: 13px; }
.facts dd { margin: 4px 0 0; font-weight: 600; }
.hash { overflow-wrap: anywhere; font-family: ui-monospace, monospace; font-size: 12px; }
.final-state { border-left: 4px solid #16a34a; padding-left: 16px; }
.disclaimer { margin-top: 16px; }
</style>
