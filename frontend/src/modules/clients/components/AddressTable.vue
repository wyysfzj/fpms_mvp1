<template>
  <div>
    <div style="display: flex; justify-content: flex-end; margin-bottom: 12px;">
      <el-button type="primary" size="small" @click="openCreate">新增地址</el-button>
    </div>

    <el-table
      v-loading="loading"
      :data="addresses"
      stripe
      size="small"
      class="compact-table"
    >
      <el-table-column label="类型" width="100">
        <template #default="{ row }">
          <el-tag size="small">{{ addressTypeLabel(row.address_type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="address_line1" label="地址行1" min-width="160" />
      <el-table-column prop="city" label="城市" width="100" />
      <el-table-column prop="province" label="省份" width="100" />
      <el-table-column prop="postal_code" label="邮编" width="90" />
      <el-table-column prop="country_code" label="国家" width="80" />
      <el-table-column label="默认" width="70" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.is_default" type="success" size="small">是</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{ row }">
          <el-button text size="small" @click="openEdit(row)">编辑</el-button>
          <el-popconfirm title="确定删除？" @confirm="handleDelete(row.id)">
            <template #reference>
              <el-button text size="small" type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
      <template #empty>
        <span>暂无地址</span>
      </template>
    </el-table>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑地址' : '新增地址'"
      width="520px"
      destroy-on-close
    >
      <el-form :model="form" label-width="80px" label-position="right">
        <el-form-item label="类型">
          <el-select v-model="form.address_type" placeholder="请选择">
            <el-option label="通用" value="GENERAL" />
            <el-option label="账单" value="BILLING" />
            <el-option label="邮寄" value="MAILING" />
          </el-select>
        </el-form-item>
        <el-form-item label="地址行1">
          <el-input v-model="form.address_line1" />
        </el-form-item>
        <el-form-item label="地址行2">
          <el-input v-model="form.address_line2" />
        </el-form-item>
        <el-form-item label="城市">
          <el-input v-model="form.city" />
        </el-form-item>
        <el-form-item label="省份">
          <el-input v-model="form.province" />
        </el-form-item>
        <el-form-item label="邮编">
          <el-input v-model="form.postal_code" />
        </el-form-item>
        <el-form-item label="国家">
          <el-input v-model="form.country_code" />
        </el-form-item>
        <el-form-item label="默认">
          <el-switch v-model="form.is_default" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
    getClientAddresses,
    createClientAddress,
    updateClientAddress,
    deleteClientAddress,
} from '../../../api/clients'
import type { ClientAddress, ClientAddressCreatePayload } from '../../../api/clients.types'

const props = defineProps<{
    clientId: string
}>()

const addresses = ref<ClientAddress[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEditing = ref(false)
const editingId = ref('')
const submitting = ref(false)

const defaultForm = (): ClientAddressCreatePayload & { is_default: boolean } => ({
    address_type: 'GENERAL',
    address_line1: '',
    address_line2: '',
    city: '',
    province: '',
    postal_code: '',
    country_code: '',
    is_default: false,
})

const form = ref(defaultForm())

const ADDRESS_TYPE_MAP: Record<string, string> = {
    GENERAL: '通用',
    BILLING: '账单',
    MAILING: '邮寄',
}

function addressTypeLabel(type: string): string {
    return ADDRESS_TYPE_MAP[type] || type
}

async function fetchData() {
    loading.value = true
    try {
        addresses.value = await getClientAddresses(props.clientId)
    } catch {
        ElMessage.error('加载地址失败')
    } finally {
        loading.value = false
    }
}

function openCreate() {
    isEditing.value = false
    editingId.value = ''
    form.value = defaultForm()
    dialogVisible.value = true
}

function openEdit(row: ClientAddress) {
    isEditing.value = true
    editingId.value = row.id
    form.value = {
        address_type: row.address_type || 'GENERAL',
        address_line1: row.address_line1 || '',
        address_line2: row.address_line2 || '',
        city: row.city || '',
        province: row.province || '',
        postal_code: row.postal_code || '',
        country_code: row.country_code || '',
        is_default: row.is_default,
    }
    dialogVisible.value = true
}

async function handleSubmit() {
    submitting.value = true
    try {
        if (isEditing.value) {
            await updateClientAddress(props.clientId, editingId.value, form.value)
            ElMessage.success('地址已更新')
        } else {
            await createClientAddress(props.clientId, form.value)
            ElMessage.success('地址已创建')
        }
        dialogVisible.value = false
        await fetchData()
    } catch {
        ElMessage.error(isEditing.value ? '更新地址失败' : '创建地址失败')
    } finally {
        submitting.value = false
    }
}

async function handleDelete(addressId: string) {
    try {
        await deleteClientAddress(props.clientId, addressId)
        ElMessage.success('地址已删除')
        await fetchData()
    } catch {
        ElMessage.error('删除地址失败')
    }
}

onMounted(() => {
    fetchData()
})
</script>
