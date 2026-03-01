<template>
  <div :class="['drawer-backdrop', { open: visible }]" @click.self="close">
    <div class="drawer-panel">
      <div class="drawer-header">{{ ZH.drawer.title }}</div>
      <div class="drawer-body">
        <div class="form-group">
          <label class="form-label">{{ ZH.drawer.client }}</label>
          <el-select
            v-model="form.client_id"
            filterable
            remote
            :remote-method="searchClients"
            :placeholder="ZH.drawer.clientPlaceholder"
            :loading="clientsLoading"
            style="width: 100%;"
          >
            <el-option
              v-for="c in clientOptions"
              :key="c.id"
              :label="c.name"
              :value="c.id"
            />
          </el-select>
        </div>

        <div class="form-group">
          <label class="form-label">{{ ZH.drawer.caseType }}</label>
          <el-select v-model="form.patent_category" style="width: 100%;">
            <el-option label="发明专利" value="INV" />
            <el-option label="实用新型" value="UTL" />
            <el-option label="外观设计" value="DES" />
          </el-select>
        </div>

        <div class="form-group">
          <label class="form-label">{{ ZH.drawer.caseTitle }}</label>
          <el-input
            v-model="form.title_cn"
            type="textarea"
            :rows="3"
            :placeholder="ZH.drawer.titlePlaceholder"
          />
        </div>
      </div>
      <div class="drawer-footer">
        <el-button @click="close">{{ ZH.drawer.cancel }}</el-button>
        <el-button type="primary" :loading="submitting" @click="submit">
          {{ ZH.drawer.create }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { ZH } from '../../../constants/labels.zh'
import { getClients } from '../../../api/clients'
import { createCase } from '../../../api/cases'
import type { Client } from '../../../api/clients.types'

const props = defineProps<{
  visible: boolean
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  created: [caseId: string]
}>()

const form = reactive({
  client_id: '' as string,
  patent_category: 'INV' as string,
  title_cn: '' as string,
})

const submitting = ref(false)
const clientsLoading = ref(false)
const clientOptions = ref<Client[]>([])

// Load initial clients when drawer opens
watch(() => props.visible, async (val) => {
  if (val) {
    await searchClients('')
  }
})

// Handle ESC key
function onEscKey(e: KeyboardEvent) {
  if (e.key === 'Escape' && props.visible) close()
}
onMounted(() => document.addEventListener('keydown', onEscKey))
onUnmounted(() => document.removeEventListener('keydown', onEscKey))

async function searchClients(query: string) {
  clientsLoading.value = true
  try {
    const res = await getClients({ page: 1, page_size: 50 })
    if (query) {
      clientOptions.value = res.items.filter(c =>
        c.name.toLowerCase().includes(query.toLowerCase()) ||
        (c.name_cn && c.name_cn.includes(query)) ||
        (c.name_en && c.name_en.toLowerCase().includes(query.toLowerCase()))
      )
    } else {
      clientOptions.value = res.items
    }
  } catch {
    clientOptions.value = []
  } finally {
    clientsLoading.value = false
  }
}

function close() {
  emit('update:visible', false)
}

function resetForm() {
  form.client_id = ''
  form.patent_category = 'INV'
  form.title_cn = ''
}

async function submit() {
  if (!form.client_id) {
    ElMessage.warning('请选择客户')
    return
  }
  if (!form.title_cn.trim()) {
    ElMessage.warning('请输入案件标题')
    return
  }

  submitting.value = true
  try {
    // Generate a case_no (required by backend)
    const ts = Date.now().toString(36).toUpperCase()
    const caseNo = `P${new Date().getFullYear().toString().slice(-2)}-${ts.slice(-6)}`

    const result = await createCase({
      case_no: caseNo,
      client_id: form.client_id,
      title: form.title_cn.trim(),
      patent_category: form.patent_category,
    })
    ElMessage.success('案件创建成功')
    resetForm()
    close()
    emit('created', result.id)
  } catch {
    ElMessage.error('创建失败，请重试')
  } finally {
    submitting.value = false
  }
}
</script>
