<template>
  <div>
    <div style="display: flex; justify-content: flex-end; margin-bottom: 12px;">
      <el-button type="primary" size="small" @click="openCreate">新增联系人</el-button>
    </div>

    <el-table
      v-loading="loading"
      :data="contacts"
      stripe
      size="small"
      class="compact-table"
    >
      <el-table-column prop="contact_name" label="姓名" min-width="120" />
      <el-table-column prop="title" label="职务" width="100" />
      <el-table-column prop="phone" label="电话" width="140" />
      <el-table-column prop="mobile" label="手机" width="140" />
      <el-table-column prop="email" label="邮箱" min-width="160" />
      <el-table-column label="主联系人" width="90" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.is_primary" type="success" size="small">是</el-tag>
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
        <span>暂无联系人</span>
      </template>
    </el-table>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑联系人' : '新增联系人'"
      width="520px"
      destroy-on-close
    >
      <el-form :model="form" label-width="80px" label-position="right">
        <el-form-item label="姓名" required>
          <el-input v-model="form.contact_name" />
        </el-form-item>
        <el-form-item label="职务">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="手机">
          <el-input v-model="form.mobile" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="主联系人">
          <el-switch v-model="form.is_primary" />
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
    getClientContacts,
    createClientContact,
    updateClientContact,
    deleteClientContact,
} from '../../../api/clients'
import type { ClientContact, ClientContactCreatePayload } from '../../../api/clients.types'

const props = defineProps<{
    clientId: string
}>()

const contacts = ref<ClientContact[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEditing = ref(false)
const editingId = ref('')
const submitting = ref(false)

const defaultForm = (): ClientContactCreatePayload & { is_primary: boolean } => ({
    contact_name: '',
    title: '',
    phone: '',
    mobile: '',
    email: '',
    is_primary: false,
})

const form = ref(defaultForm())

async function fetchData() {
    loading.value = true
    try {
        contacts.value = await getClientContacts(props.clientId)
    } catch {
        ElMessage.error('加载联系人失败')
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

function openEdit(row: ClientContact) {
    isEditing.value = true
    editingId.value = row.id
    form.value = {
        contact_name: row.contact_name || '',
        title: row.title || '',
        phone: row.phone || '',
        mobile: row.mobile || '',
        email: row.email || '',
        is_primary: row.is_primary,
    }
    dialogVisible.value = true
}

async function handleSubmit() {
    if (!form.value.contact_name?.trim()) {
        ElMessage.warning('请输入联系人姓名')
        return
    }
    submitting.value = true
    try {
        if (isEditing.value) {
            await updateClientContact(props.clientId, editingId.value, form.value)
            ElMessage.success('联系人已更新')
        } else {
            await createClientContact(props.clientId, form.value)
            ElMessage.success('联系人已创建')
        }
        dialogVisible.value = false
        await fetchData()
    } catch {
        ElMessage.error(isEditing.value ? '更新联系人失败' : '创建联系人失败')
    } finally {
        submitting.value = false
    }
}

async function handleDelete(contactId: string) {
    try {
        await deleteClientContact(props.clientId, contactId)
        ElMessage.success('联系人已删除')
        await fetchData()
    } catch {
        ElMessage.error('删除联系人失败')
    }
}

onMounted(() => {
    fetchData()
})
</script>
