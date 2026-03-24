# FB2 Architect Plan — Client Detail + Address/Contact UI

## 1. Dependency Verification

### Backend A2 APIs — CONFIRMED COMPLETE

| Endpoint | Method | Response | Permission |
|---|---|---|---|
| `/clients/{client_id}/addresses` | GET | `list[ClientAddressOut]` | Client.Read |
| `/clients/{client_id}/addresses` | POST | `ClientAddressOut` (201) | Client.Edit |
| `/clients/{client_id}/addresses/{address_id}` | PUT | `ClientAddressOut` | Client.Edit |
| `/clients/{client_id}/addresses/{address_id}` | DELETE | 204 No Content | Client.Edit |
| `/clients/{client_id}/contacts` | GET | `list[ClientContactOut]` | Client.Read |
| `/clients/{client_id}/contacts` | POST | `ClientContactOut` (201) | Client.Edit |
| `/clients/{client_id}/contacts/{contact_id}` | PUT | `ClientContactOut` | Client.Edit |
| `/clients/{client_id}/contacts/{contact_id}` | DELETE | 204 No Content | Client.Edit |

### Backend Schema Fields (from `schemas.py` — verified):

**ClientAddressOut**: `id, client_id, address_type, address_line1, address_line2, city, province, postal_code, country_code, is_default, created_at, updated_at`

**ClientAddressCreateIn**: `address_type="GENERAL", address_line1?, address_line2?, city?, province?, postal_code?, country_code="CN", is_default=false`

**ClientAddressUpdateIn**: all fields optional

**ClientContactOut**: `id, client_id, contact_name, title?, phone?, mobile?, email?, is_primary, created_at, updated_at`

**ClientContactCreateIn**: `contact_name (required), title?, phone?, mobile?, email?, is_primary=false`

**ClientContactUpdateIn**: all fields optional

---

## 2. File-by-File Change Specification

### File 1: `frontend/src/api/clients.types.ts` (modify)

**What to add** — 6 new interfaces after the existing ones:

```typescript
// ── Address types ──────────────────────────────────

export interface ClientAddress {
    id: string
    client_id: string
    address_type: string
    address_line1: string | null
    address_line2: string | null
    city: string | null
    province: string | null
    postal_code: string | null
    country_code: string | null
    is_default: boolean
    created_at: string
    updated_at: string
}

export interface ClientAddressCreatePayload {
    address_type?: string       // default "GENERAL"
    address_line1?: string
    address_line2?: string
    city?: string
    province?: string
    postal_code?: string
    country_code?: string       // default "CN"
    is_default?: boolean        // default false
}

export interface ClientAddressUpdatePayload {
    address_type?: string
    address_line1?: string
    address_line2?: string
    city?: string
    province?: string
    postal_code?: string
    country_code?: string
    is_default?: boolean
}

// ── Contact types ──────────────────────────────────

export interface ClientContact {
    id: string
    client_id: string
    contact_name: string
    title: string | null
    phone: string | null
    mobile: string | null
    email: string | null
    is_primary: boolean
    created_at: string
    updated_at: string
}

export interface ClientContactCreatePayload {
    contact_name: string        // required
    title?: string
    phone?: string
    mobile?: string
    email?: string
    is_primary?: boolean        // default false
}

export interface ClientContactUpdatePayload {
    contact_name?: string
    title?: string
    phone?: string
    mobile?: string
    email?: string
    is_primary?: boolean
}
```

**No mapping needed** — field names match backend 1:1 (no snake→camel conversion required, consistent with how other modules work).

---

### File 2: `frontend/src/api/clients.ts` (modify)

**What to add** — 8 new exported functions at the bottom of the file.

Import additions at top:
```typescript
import type {
    Client, ClientCreatePayload, ClientListParams, ClientUpdatePayload,
    ClientAddress, ClientAddressCreatePayload, ClientAddressUpdatePayload,
    ClientContact, ClientContactCreatePayload, ClientContactUpdatePayload,
} from './clients.types'
```

New functions (after existing `deactivateClient`):

```typescript
// ── Address CRUD ──────────────────────────────────

export async function getClientAddresses(clientId: string): Promise<ClientAddress[]> {
    const response = await http.get<ClientAddress[]>(`/clients/${clientId}/addresses`)
    return response.data
}

export async function createClientAddress(
    clientId: string,
    data: ClientAddressCreatePayload
): Promise<ClientAddress> {
    const response = await http.post<ClientAddress>(`/clients/${clientId}/addresses`, data)
    return response.data
}

export async function updateClientAddress(
    clientId: string,
    addressId: string,
    data: ClientAddressUpdatePayload
): Promise<ClientAddress> {
    const response = await http.put<ClientAddress>(
        `/clients/${clientId}/addresses/${addressId}`, data
    )
    return response.data
}

export async function deleteClientAddress(clientId: string, addressId: string): Promise<void> {
    await http.delete(`/clients/${clientId}/addresses/${addressId}`)
}

// ── Contact CRUD ──────────────────────────────────

export async function getClientContacts(clientId: string): Promise<ClientContact[]> {
    const response = await http.get<ClientContact[]>(`/clients/${clientId}/contacts`)
    return response.data
}

export async function createClientContact(
    clientId: string,
    data: ClientContactCreatePayload
): Promise<ClientContact> {
    const response = await http.post<ClientContact>(`/clients/${clientId}/contacts`, data)
    return response.data
}

export async function updateClientContact(
    clientId: string,
    contactId: string,
    data: ClientContactUpdatePayload
): Promise<ClientContact> {
    const response = await http.put<ClientContact>(
        `/clients/${clientId}/contacts/${contactId}`, data
    )
    return response.data
}

export async function deleteClientContact(clientId: string, contactId: string): Promise<void> {
    await http.delete(`/clients/${clientId}/contacts/${contactId}`)
}
```

**No backend mapper needed** — response fields match frontend types directly (unlike the `BackendClient` → `Client` mapper for the main entity).

---

### File 3: `frontend/src/modules/clients/components/AddressTable.vue` (new)

**Props**: `clientId: string`

**Events**: none (self-contained CRUD)

**Component structure**:

```
<template>
  <div class="case-panel">
    <div class="panel-toolbar">
      <h3 class="panel-heading">地址列表</h3>
      <el-button type="primary" size="small" @click="openCreate">新增地址</el-button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="muted">加载中...</div>

    <!-- Empty -->
    <div v-else-if="items.length === 0" class="placeholder-content">
      <p>暂无地址</p>
    </div>

    <!-- Table -->
    <el-table v-else :data="items" stripe size="small">
      <el-table-column prop="address_type" label="类型" width="100">
        <template #default="{ row }">
          <el-tag size="small">{{ addressTypeLabel(row.address_type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="address_line1" label="地址行1" min-width="180" />
      <el-table-column prop="city" label="城市" width="100" />
      <el-table-column prop="province" label="省份" width="100" />
      <el-table-column prop="postal_code" label="邮编" width="90" />
      <el-table-column prop="country_code" label="国家" width="80" />
      <el-table-column label="默认" width="70">
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
    </el-table>

    <!-- Create/Edit Dialog -->
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑地址' : '新增地址'" width="560px">
      <el-form :model="form" label-position="top">
        <el-form-item label="地址类型">
          <el-select v-model="form.address_type" style="width: 100%">
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
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="城市">
              <el-input v-model="form.city" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="省份">
              <el-input v-model="form.province" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="邮编">
              <el-input v-model="form.postal_code" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="国家代码">
              <el-input v-model="form.country_code" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="默认地址">
              <el-switch v-model="form.is_default" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
// Props
defineProps<{ clientId: string }>()

// State
// items: ref<ClientAddress[]>
// loading, saving: ref<boolean>
// dialogVisible: ref<boolean>
// editingId: ref<string | null>
// form: reactive<ClientAddressCreatePayload>  (reused for edit)

// Functions
// fetchAddresses()        → getClientAddresses(props.clientId)
// openCreate()            → reset form, dialogVisible = true
// openEdit(row)           → populate form from row, editingId = row.id
// handleSave()            → create or update based on editingId
// handleDelete(addressId) → deleteClientAddress, refresh
// addressTypeLabel(type)  → { GENERAL: '通用', BILLING: '账单', MAILING: '邮寄' }

// Lifecycle
// onMounted → fetchAddresses()
</script>
```

**Imports** (all relative, no `@/`):
```typescript
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getClientAddresses, createClientAddress, updateClientAddress, deleteClientAddress } from '../../../api/clients'
import type { ClientAddress, ClientAddressCreatePayload } from '../../../api/clients.types'
```

---

### File 4: `frontend/src/modules/clients/components/ContactTable.vue` (new)

**Props**: `clientId: string`

**Component structure** — mirrors AddressTable pattern:

```
<template>
  <div class="case-panel">
    <div class="panel-toolbar">
      <h3 class="panel-heading">联系人列表</h3>
      <el-button type="primary" size="small" @click="openCreate">新增联系人</el-button>
    </div>

    <!-- Loading / Empty / Table -->
    <el-table v-else :data="items" stripe size="small">
      <el-table-column prop="contact_name" label="姓名" min-width="120" />
      <el-table-column prop="title" label="职务" width="100" />
      <el-table-column prop="phone" label="电话" width="130" />
      <el-table-column prop="mobile" label="手机" width="130" />
      <el-table-column prop="email" label="邮箱" min-width="160" />
      <el-table-column label="主联系人" width="90">
        <template #default="{ row }">
          <el-tag v-if="row.is_primary" type="success" size="small">是</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120" fixed="right">
        <!-- edit + popconfirm delete -->
      </el-table-column>
    </el-table>

    <!-- Create/Edit Dialog -->
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑联系人' : '新增联系人'" width="500px">
      <el-form :model="form" label-position="top">
        <el-form-item label="姓名" required>
          <el-input v-model="form.contact_name" />
        </el-form-item>
        <el-form-item label="职务">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="电话">
              <el-input v-model="form.phone" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="手机">
              <el-input v-model="form.mobile" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="主联系人">
          <el-switch v-model="form.is_primary" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
// Same pattern as AddressTable
// Props: { clientId: string }
// API: getClientContacts, createClientContact, updateClientContact, deleteClientContact
// Types: ClientContact, ClientContactCreatePayload
</script>
```

**Imports** (all relative):
```typescript
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getClientContacts, createClientContact, updateClientContact, deleteClientContact } from '../../../api/clients'
import type { ClientContact, ClientContactCreatePayload } from '../../../api/clients.types'
```

---

### File 5: `frontend/src/modules/clients/pages/ClientDetail.vue` (new)

**Layout**: Follows `CaseDetail.vue` pattern with `el-tabs`.

**Structure**:

```
<template>
  <div class="page-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="page-header-left">
        <el-button text @click="goBack">
          <span class="back-icon">←</span> 返回
        </el-button>
      </div>
      <div class="page-header-right">
        <el-button type="primary" @click="handleEdit">编辑客户</el-button>
      </div>
    </div>

    <!-- Error Banner -->
    <div v-if="error" class="page-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <!-- Loading -->
    <div v-if="loading" class="page-loading">
      <el-skeleton :rows="10" animated />
    </div>

    <!-- Content -->
    <template v-else-if="client">
      <!-- Client Header -->
      <div class="client-header">
        <h1>{{ client.name }}</h1>
        <div class="client-meta">
          <span v-if="client.client_code">{{ client.client_code }}</span>
          <el-tag v-if="!client.is_active" type="warning">已停用</el-tag>
        </div>
      </div>

      <!-- Tabs -->
      <el-tabs v-model="activeTab">
        <el-tab-pane label="基本信息" name="info">
          <!-- read-only info grid: name, code, type, currency, email -->
          <div class="case-panel">
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">客户名称</span>
                <span class="info-value">{{ client.name }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">客户代码</span>
                <span class="info-value">{{ client.client_code || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">客户类型</span>
                <span class="info-value">{{ client.client_type || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">默认币种</span>
                <span class="info-value">{{ client.default_currency || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">邮箱</span>
                <span class="info-value">{{ client.email || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">状态</span>
                <span class="info-value">
                  <el-tag :type="client.is_active ? 'success' : 'warning'" size="small">
                    {{ client.is_active ? '活跃' : '已停用' }}
                  </el-tag>
                </span>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="地址" name="addresses">
          <AddressTable :client-id="clientId" />
        </el-tab-pane>

        <el-tab-pane label="联系人" name="contacts">
          <ContactTable :client-id="clientId" />
        </el-tab-pane>

        <el-tab-pane label="关联案件" name="cases">
          <!-- Inline case list filtered by client_id -->
          <!-- Uses getCases({client_id, page, page_size}) -->
          <!-- Simple el-table with case_no, title, status, filing_date -->
        </el-tab-pane>
      </el-tabs>
    </template>

    <!-- Not Found -->
    <div v-else-if="!loading && !error" class="page-empty">
      <div class="empty-state">
        <span class="empty-icon">📋</span>
        <h3 class="empty-title">未找到客户</h3>
        <p class="empty-message">请求的客户不存在。</p>
        <el-button type="primary" @click="goBack">返回</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Imports
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getClient } from '../../../api/clients'
import type { Client } from '../../../api/clients.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import AddressTable from '../components/AddressTable.vue'
import ContactTable from '../components/ContactTable.vue'

// State
const route = useRoute()
const router = useRouter()

const clientId = computed(() => String(route.params.id || ''))
const client = ref<Client | null>(null)
const loading = ref(false)
const error = ref<ApiError | null>(null)
const activeTab = ref('info')

// Related cases state (Tab 4)
// relatedCases: ref<Case[]>([])
// casesLoading: ref(false)
// Uses: import { getCases } from '../../../api/cases'
// Note: CaseListParams lacks client_id — pass raw params to http.get

// Functions
// fetchClient() → getClient(clientId.value)
// fetchRelatedCases() → getCases with client_id param (workaround)
// goBack() → router.push('/clients')
// handleEdit() → router.push(`/clients/${clientId.value}/edit`)
</script>
```

**Related Cases Tab Implementation Note**:
The existing `getCases` function only destructures `page` and `page_size` from params — it does NOT pass `client_id`. Two options:
1. **Workaround**: Call `http.get('/cases', { params: { client_id, page, page_size } })` directly in `ClientDetail.vue`.
2. **Proper fix**: Modify `cases.types.ts` to add `client_id` to `CaseListParams` and update `getCases` to pass it through — but `cases.types.ts` and `cases.ts` are NOT in the allowlist.

**Decision**: Use option 1 (direct http call) within `ClientDetail.vue` to stay within allowlist. Add to findings as tech debt.

---

### File 6: `frontend/src/router/index.ts` (modify)

**What to add**: One new route entry for `/clients/:id`, inserted between the existing `clients/new` and `clients/:id/edit` routes.

```typescript
// Add this between client_new and client_edit:
{
    path: 'clients/:id',
    name: 'client_detail',
    component: () => import('../modules/clients/pages/ClientDetail.vue'),
    meta: { requiredPerms: [Perms.CLIENTS_READ] }
},
```

**Position**: After line 162 (after the `client_new` route), before line 163 (the `client_edit` route).

**IMPORTANT**: The `:id` route MUST come after the `/new` literal route to avoid Vue Router matching "new" as an id.

Current order (lines 152–168):
```
clients        → ClientList
clients/new    → ClientForm
clients/:id/edit → ClientForm
```

New order:
```
clients        → ClientList
clients/new    → ClientForm
clients/:id    → ClientDetail    ← NEW
clients/:id/edit → ClientForm
```

---

## 3. Data Flow Diagram

```
ClientDetail.vue
├── onMounted → getClient(id) → client ref
├── Tab "基本信息" → read-only display from client ref
├── Tab "地址"
│   └── AddressTable.vue (prop: clientId)
│       ├── onMounted → getClientAddresses(clientId) → items ref
│       ├── openCreate → dialog → createClientAddress → refresh items
│       ├── openEdit → dialog → updateClientAddress → refresh items
│       └── handleDelete → deleteClientAddress → refresh items
├── Tab "联系人"
│   └── ContactTable.vue (prop: clientId)
│       ├── onMounted → getClientContacts(clientId) → items ref
│       ├── openCreate → dialog → createClientContact → refresh items
│       ├── openEdit → dialog → updateClientContact → refresh items
│       └── handleDelete → deleteClientContact → refresh items
└── Tab "关联案件"
    └── inline implementation
        └── onMounted/watch(activeTab) → http.get('/cases', {client_id}) → cases ref
```

**Key point**: AddressTable and ContactTable are self-contained — they fetch their own data and manage their own CRUD dialogs. ClientDetail just passes `clientId` as a prop.

---

## 4. API Contract Table

| Frontend Function | HTTP Method | Backend Endpoint | Request Body | Response |
|---|---|---|---|---|
| `getClient(id)` | GET | `/clients/{id}` | — | `BackendClient` |
| `getClientAddresses(clientId)` | GET | `/clients/{client_id}/addresses` | — | `ClientAddress[]` |
| `createClientAddress(clientId, data)` | POST | `/clients/{client_id}/addresses` | `ClientAddressCreatePayload` | `ClientAddress` |
| `updateClientAddress(clientId, addrId, data)` | PUT | `/clients/{client_id}/addresses/{address_id}` | `ClientAddressUpdatePayload` | `ClientAddress` |
| `deleteClientAddress(clientId, addrId)` | DELETE | `/clients/{client_id}/addresses/{address_id}` | — | void (204) |
| `getClientContacts(clientId)` | GET | `/clients/{client_id}/contacts` | — | `ClientContact[]` |
| `createClientContact(clientId, data)` | POST | `/clients/{client_id}/contacts` | `ClientContactCreatePayload` | `ClientContact` |
| `updateClientContact(clientId, contactId, data)` | PUT | `/clients/{client_id}/contacts/{contact_id}` | `ClientContactUpdatePayload` | `ClientContact` |
| `deleteClientContact(clientId, contactId)` | DELETE | `/clients/{client_id}/contacts/{contact_id}` | — | void (204) |
| (inline) `http.get('/cases', { params: { client_id } })` | GET | `/cases?client_id={id}` | — | `Pagination<Case>` |

---

## 5. Acceptance Criteria Checklist

- [ ] **AC-1**: `clients.types.ts` exports `ClientAddress`, `ClientAddressCreatePayload`, `ClientAddressUpdatePayload`, `ClientContact`, `ClientContactCreatePayload`, `ClientContactUpdatePayload`
- [ ] **AC-2**: `clients.ts` exports 8 new functions: `getClientAddresses`, `createClientAddress`, `updateClientAddress`, `deleteClientAddress`, `getClientContacts`, `createClientContact`, `updateClientContact`, `deleteClientContact`
- [ ] **AC-3**: `AddressTable.vue` renders a table of addresses with columns: type, line1, city, province, postal_code, country, is_default, actions
- [ ] **AC-4**: `AddressTable.vue` supports create/edit via `el-dialog` with fields: address_type (el-select: GENERAL/BILLING/MAILING), address_line1, address_line2, city, province, postal_code, country_code, is_default (el-switch)
- [ ] **AC-5**: `AddressTable.vue` supports delete with `el-popconfirm` ("确定删除？")
- [ ] **AC-6**: `ContactTable.vue` renders a table of contacts with columns: name, title, phone, mobile, email, is_primary, actions
- [ ] **AC-7**: `ContactTable.vue` supports create/edit via `el-dialog` with fields: contact_name (required), title, phone, mobile, email, is_primary (el-switch)
- [ ] **AC-8**: `ContactTable.vue` supports delete with `el-popconfirm` ("确定删除？")
- [ ] **AC-9**: `ClientDetail.vue` has 4 tabs: 基本信息, 地址, 联系人, 关联案件
- [ ] **AC-10**: `ClientDetail.vue` "基本信息" tab shows: name, client_code, client_type, default_currency, email, is_active
- [ ] **AC-11**: `ClientDetail.vue` "关联案件" tab fetches and displays cases filtered by `client_id`
- [ ] **AC-12**: `ClientDetail.vue` header has back button (→ `/clients`) and edit button (→ `/clients/:id/edit`)
- [ ] **AC-13**: Router has `clients/:id` route pointing to `ClientDetail.vue` with perm `CLIENTS_READ`
- [ ] **AC-14**: All UI labels are in Chinese
- [ ] **AC-15**: All imports use relative paths (no `@/`)
- [ ] **AC-16**: Quality gate passes: `npm run lint && npm run typecheck && npm run build`

---

## 6. Risk / Issues Log

| # | Issue | Severity | Impact | Mitigation |
|---|---|---|---|---|
| R1 | **No `GET /clients/{client_id}` endpoint** — backend `api.py` has no individual GET route. The frontend `getClient()` calls `GET /clients/{id}` which would fail. However, `ClientForm.vue` already uses this function in edit mode — so either the endpoint exists elsewhere or this is a pre-existing bug. | HIGH | ClientDetail.vue depends on `getClient()` to load client data. | Use `getClient()` as-is (consistent with `ClientForm.vue`). If it fails at runtime, a backend fix is needed (add `GET /clients/{client_id}` endpoint). This is outside FB2's allowlist. |
| R2 | **`ClientList.vue` handleView still routes to `/clients/${id}/edit`** — after FB2 adds the detail page, `handleView` should route to `/clients/${id}` instead. But `ClientList.vue` is NOT in the FB2 allowlist. | MEDIUM | "查看" action in client list goes to edit form, not detail page. | Log as tech debt — fix in a future batch. |
| R3 | **`getCases` doesn't pass `client_id` param** — the function destructures only `page` and `page_size`. The "Related Cases" tab needs `client_id` filter. | MEDIUM | Cannot use `getCases()` with client_id filter. | Use `http.get('/cases', { params: { client_id, page, page_size } })` directly in ClientDetail. `cases.ts` / `cases.types.ts` not in allowlist. |
| R4 | **List endpoint returns `ClientListItemOut`** (id, client_code, name_cn, name_en only) — not full `ClientOut`. If `getClient()` falls through to the list endpoint, detail fields will be missing. | LOW | Only relevant if R1 causes a fallback behavior. | Same mitigation as R1. |

---

## 7. Task Assignments (mapping to team tasks)

| Task ID | File(s) | Agent | Dependency |
|---|---|---|---|
| T1 (#2) | `clients.types.ts` | Impl-1 | none |
| T2 (#3) | `clients.ts` | Impl-1 | T1 |
| T3 (#4) | `AddressTable.vue` | Impl-1 | T1, T2 |
| T4 (#5) | `ContactTable.vue` | Impl-1 | T1, T2 |
| T5 (#6) | `ClientDetail.vue` | Impl-1 | T1, T2, T3, T4 |
| T6 (#7) | `router/index.ts` | Impl-1 | T5 |
| QG (#8) | — | Impl-1 | T6 |
| Review (#9) | all 6 files | Review Agent | QG |

**Recommended execution order**: T1 → T2 → T3 + T4 (parallel) → T5 → T6 → QG → Review

---

## 8. Implementation Notes

### CSS Classes to Reuse
From `CaseDetail.vue` and other pages:
- `.page-container`, `.page-header`, `.page-header-left`, `.page-header-right`
- `.page-error`, `.page-loading`, `.page-empty`
- `.case-panel`, `.panel-toolbar`, `.panel-heading`
- `.info-grid`, `.info-item`, `.info-label`, `.info-value`
- `.empty-state`, `.empty-icon`, `.empty-title`, `.empty-message`
- `.back-icon`
- `.compact-table`
- `.placeholder-content`
- `.muted`

### Element Plus Components Used
- `el-tabs`, `el-tab-pane`
- `el-table`, `el-table-column`
- `el-dialog`
- `el-form`, `el-form-item`
- `el-input`
- `el-select`, `el-option`
- `el-switch`
- `el-button`
- `el-tag`
- `el-popconfirm`
- `el-skeleton`
- `el-row`, `el-col`
- `ElMessage` (from `element-plus`)

### Error Handling Pattern
Follow `CaseDocumentsTab.vue` pattern — `try/catch` with silent fail on fetch, `ElMessage.error()` on CUD operations.
