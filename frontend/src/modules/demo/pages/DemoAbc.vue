<template>
  <section class="demo-page">
    <header class="hero">
      <div>
        <p class="eyebrow">LOCAL ABC E2E · DEMO_ONLY</p>
        <h1>客户账单、回款与核销演示</h1>
        <p>所有金额与模板均来自当前只读 runtime bundle；本页不代表生产费率或正式模板。</p>
      </div>
      <el-tag :type="bundle ? 'success' : 'warning'" size="large">
        {{ bundle ? '演示输入已校验' : '等待演示输入' }}
      </el-tag>
    </header>

    <el-alert v-if="errorMessage" :title="errorMessage" type="error" show-icon :closable="false" />

    <el-card class="step-card">
      <template #header><strong>1. Runtime bundle</strong></template>
      <el-button :loading="loading === 'bundle'" type="primary" @click="loadBundle">校验并读取输入</el-button>
      <dl v-if="bundle" class="facts">
        <div><dt>Bundle</dt><dd>{{ bundle.bundle_id }} / {{ bundle.bundle_version }}</dd></div>
        <div><dt>Manifest SHA-256</dt><dd class="hash">{{ bundle.manifest_sha256 }}</dd></div>
        <div><dt>模板</dt><dd>{{ bundle.template_code }}</dd></div>
        <div><dt>Template SHA-256</dt><dd class="hash">{{ bundle.template_sha256 }}</dd></div>
        <div><dt>服务费项目</dt><dd>{{ bundle.name_zh_cn }}（{{ money(bundle.amount) }} {{ bundle.currency }}）</dd></div>
        <div><dt>来源</dt><dd>{{ bundle.source_ref }} / {{ bundle.source_version }}</dd></div>
      </dl>
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
        <el-button data-testid="create-obligation" :disabled="!selectedCase || !bundle" :loading="loading === 'obligation'" @click="createObligation">生成服务费义务</el-button>
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
import { onMounted, reactive, ref } from 'vue'
import { getCaseByCaseNo } from '../../../api/cases'
import type { Case } from '../../../api/cases.types'
import {
  createDemoBankReceipt,
  createDemoBill,
  createDemoDraft,
  createDemoFullOffset,
  createDemoServiceObligation,
  lockDemoDraft,
  readDemoServiceItem,
  recordDemoPayInstruction,
} from '../demo.api'
import type {
  DemoBankReceiptResponse,
  DemoBillDetail,
  DemoDraft,
  DemoFeeObligationResponse,
  DemoOffsetResponse,
  DemoServiceItem,
} from '../demo.api'

const bundle = ref<DemoServiceItem>()
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

async function loadCase() {
  if (!caseNoInput.value) return
  await run('case', async () => { selectedCase.value = await getCaseByCaseNo(caseNoInput.value) })
}

async function createObligation() {
  if (!selectedCase.value || !bundle.value) return
  await run('obligation', async () => {
    obligation.value = await createDemoServiceObligation(
      selectedCase.value!.id,
      bundle.value!.item_code,
      idempotencyKeys.obligation,
    )
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
  })
}

onMounted(loadBundle)
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
</style>
