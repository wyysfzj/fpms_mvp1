# FC3 Detailed Execution Plan — Fee Rate Dimensions Display

> Architect Agent | Created: 2026-02-27
> Status: COMPLETE — Ready for Implementation

---

## 1. Backend API Contract Summary (B4 — CONFIRMED COMPLETE)

### FeeRateOut (GET response / POST+PUT response)

| Field | Type | Nullable | Notes |
|-------|------|----------|-------|
| `id` | string | No | UUID |
| `fee_code` | string | No | |
| `fee_name` | string | No | |
| `fee_type` | FeeType | No | GOV \| SERVICE \| MISC |
| `currency` | string | No | |
| `default_amount` | Decimal \| null | Yes | |
| `enabled` | bool | No | |
| **`rate_group`** | string \| null | Yes | DOMESTIC / PCT / ANNUITY (convention, not enforced enum) |
| **`country_code`** | string \| null | Yes | Max 10 chars |
| **`case_type`** | string \| null | Yes | NORMAL / PCT_INTL / PCT_NATL / PRIORITY (from CaseType enum) |
| **`patent_category`** | string \| null | Yes | INV / UM / DES (from PatentCategory enum) |
| **`calc_mode`** | string \| null | Yes | FIXED / PER_CLAIM / PER_PAGE / TIER (CalcMode enum, default FIXED) |
| **`calc_params`** | string \| null | Yes | JSON text — **read-only display** |
| **`allow_reduction`** | bool \| null | Yes | Default false |
| **`effective_from`** | date \| null | Yes | ISO date string (YYYY-MM-DD) |
| **`effective_to`** | date \| null | Yes | ISO date string (YYYY-MM-DD) |

### FeeRateCreateIn (POST request body)

All 9 new fields are accepted, all optional (nullable).

### FeeRateUpdateIn (PUT request body)

All 9 new fields are accepted, all optional (nullable).

### Backend Enums (from `fees/enums.py` and `cases/enums.py`)

```python
class CalcMode(str, Enum):
    FIXED = "FIXED"
    PER_CLAIM = "PER_CLAIM"
    PER_PAGE = "PER_PAGE"
    TIER = "TIER"

class CaseType(str, Enum):
    NORMAL = "NORMAL"
    PCT_INTL = "PCT_INTL"
    PCT_NATL = "PCT_NATL"
    PRIORITY = "PRIORITY"

class PatentCategory(str, Enum):
    INV = "INV"
    UM = "UM"
    DES = "DES"
```

---

## 2. Chinese Label Mapping (所有新字段)

| Field | Chinese Label | Component | Options (Chinese) |
|-------|--------------|-----------|-------------------|
| `rate_group` | 费率组 | el-select | 国内(DOMESTIC), PCT(PCT), 年费(ANNUITY) |
| `country_code` | 国家/地区 | el-input | Free text, max 10 chars |
| `case_type` | 案件类型 | el-select | 普通(NORMAL), PCT国际(PCT_INTL), PCT国内(PCT_NATL), 优先权(PRIORITY) |
| `patent_category` | 专利类别 | el-select | 发明(INV), 实用新型(UM), 外观设计(DES) |
| `calc_mode` | 计算模式 | el-select | 固定(FIXED), 按权利要求(PER_CLAIM), 按页(PER_PAGE), 阶梯(TIER) |
| `calc_params` | 计算参数 | el-input (readonly) | Read-only textarea, JSON display |
| `allow_reduction` | 允许减缴 | el-switch | Boolean toggle |
| `effective_from` | 生效日期 | el-date-picker | Date |
| `effective_to` | 失效日期 | el-date-picker | Date |

---

## 3. File-by-File Change Specification

### 3.1 `frontend/src/api/fees.types.ts`

#### 3.1.1 Add union types (before FeeRate interface)

```typescript
export type CalcMode = 'FIXED' | 'PER_CLAIM' | 'PER_PAGE' | 'TIER'
export type RateGroup = 'DOMESTIC' | 'PCT' | 'ANNUITY'
```

#### 3.1.2 Add fields to `FeeRate` interface (after `enabled`)

```typescript
export interface FeeRate {
    id: string
    name: string
    rate: number
    currency?: string
    description?: string
    fee_code?: string
    fee_type?: string
    enabled?: boolean
    // B4 dimension fields
    rate_group?: string | null
    country_code?: string | null
    case_type?: string | null
    patent_category?: string | null
    calc_mode?: CalcMode | null
    calc_params?: string | null
    allow_reduction?: boolean | null
    effective_from?: string | null
    effective_to?: string | null
    created_at?: string
    updated_at?: string
}
```

#### 3.1.3 Add fields to `FeeRateCreatePayload` (after `fee_type`)

```typescript
export interface FeeRateCreatePayload {
    name: string
    rate: number
    currency?: string
    description?: string
    fee_code?: string
    fee_type?: string
    // B4 dimension fields
    rate_group?: string | null
    country_code?: string | null
    case_type?: string | null
    patent_category?: string | null
    calc_mode?: CalcMode | null
    calc_params?: string | null
    allow_reduction?: boolean | null
    effective_from?: string | null
    effective_to?: string | null
}
```

#### 3.1.4 Add fields to `FeeRateUpdatePayload` (after `enabled`)

```typescript
export interface FeeRateUpdatePayload {
    name?: string
    rate?: number
    currency?: string
    description?: string
    fee_type?: string
    enabled?: boolean
    // B4 dimension fields
    rate_group?: string | null
    country_code?: string | null
    case_type?: string | null
    patent_category?: string | null
    calc_mode?: CalcMode | null
    calc_params?: string | null
    allow_reduction?: boolean | null
    effective_from?: string | null
    effective_to?: string | null
}
```

---

### 3.2 `frontend/src/api/fees.ts` (⚠️ NOT in official allowlist — REQUIRED)

**Critical gap**: Without updating this file, dimension data from backend will be silently discarded by the mapper.

#### 3.2.1 Update `BackendFeeRate` interface (add after `enabled`)

```typescript
interface BackendFeeRate {
    id: string
    fee_code: string
    fee_name: string
    fee_type: string
    currency?: string | null
    default_amount?: string | number | null
    enabled?: boolean
    // B4 dimension fields
    rate_group?: string | null
    country_code?: string | null
    case_type?: string | null
    patent_category?: string | null
    calc_mode?: string | null
    calc_params?: string | null
    allow_reduction?: boolean | null
    effective_from?: string | null
    effective_to?: string | null
}
```

#### 3.2.2 Update `mapFeeRate()` function (add after `enabled`)

```typescript
function mapFeeRate(input: BackendFeeRate): FeeRate {
    return {
        id: input.id,
        name: input.fee_name || input.fee_code,
        rate: Number(input.default_amount || 0),
        currency: input.currency || 'CNY',
        fee_code: input.fee_code,
        fee_type: input.fee_type,
        enabled: input.enabled,
        // B4 dimension fields
        rate_group: input.rate_group ?? null,
        country_code: input.country_code ?? null,
        case_type: input.case_type ?? null,
        patent_category: input.patent_category ?? null,
        calc_mode: input.calc_mode ?? null,
        calc_params: input.calc_params ?? null,
        allow_reduction: input.allow_reduction ?? null,
        effective_from: input.effective_from ?? null,
        effective_to: input.effective_to ?? null,
    }
}
```

#### 3.2.3 Update `toFeeRateCreatePayload()` (add after `enabled`)

```typescript
function toFeeRateCreatePayload(data: FeeRateCreatePayload): Record<string, unknown> {
    return {
        fee_code: data.fee_code || buildFeeCode(data.name),
        fee_name: data.name,
        fee_type: data.fee_type || 'GOV',
        currency: data.currency || 'CNY',
        default_amount: data.rate,
        enabled: true,
        // B4 dimension fields (only include if provided)
        ...(data.rate_group !== undefined && { rate_group: data.rate_group }),
        ...(data.country_code !== undefined && { country_code: data.country_code }),
        ...(data.case_type !== undefined && { case_type: data.case_type }),
        ...(data.patent_category !== undefined && { patent_category: data.patent_category }),
        ...(data.calc_mode !== undefined && { calc_mode: data.calc_mode }),
        ...(data.calc_params !== undefined && { calc_params: data.calc_params }),
        ...(data.allow_reduction !== undefined && { allow_reduction: data.allow_reduction }),
        ...(data.effective_from !== undefined && { effective_from: data.effective_from }),
        ...(data.effective_to !== undefined && { effective_to: data.effective_to }),
    }
}
```

#### 3.2.4 Update `toFeeRateUpdatePayload()` (add after `enabled`)

```typescript
function toFeeRateUpdatePayload(data: FeeRateUpdatePayload): Record<string, unknown> {
    const payload: Record<string, unknown> = {}

    if (data.name !== undefined) payload.fee_name = data.name
    if (data.fee_type !== undefined) payload.fee_type = data.fee_type
    if (data.currency !== undefined) payload.currency = data.currency
    if (data.rate !== undefined) payload.default_amount = data.rate
    if (data.enabled !== undefined) payload.enabled = data.enabled
    // B4 dimension fields
    if (data.rate_group !== undefined) payload.rate_group = data.rate_group
    if (data.country_code !== undefined) payload.country_code = data.country_code
    if (data.case_type !== undefined) payload.case_type = data.case_type
    if (data.patent_category !== undefined) payload.patent_category = data.patent_category
    if (data.calc_mode !== undefined) payload.calc_mode = data.calc_mode
    if (data.calc_params !== undefined) payload.calc_params = data.calc_params
    if (data.allow_reduction !== undefined) payload.allow_reduction = data.allow_reduction
    if (data.effective_from !== undefined) payload.effective_from = data.effective_from
    if (data.effective_to !== undefined) payload.effective_to = data.effective_to

    return payload
}
```

---

### 3.3 `frontend/src/modules/fees/pages/FeeRates.vue`

#### 3.3.1 Add table columns (insert after the existing `currency` column, before `描述` column)

The table currently has: 编号 | 名称 | 费率 | 币种 | 描述 | 操作

New columns to add between 币种 and 描述:

```html
<el-table-column prop="fee_type" label="费用类型" width="100">
  <template #default="{ row }">
    {{ feeTypeLabel(row.fee_type) }}
  </template>
</el-table-column>
<el-table-column prop="rate_group" label="费率组" width="90">
  <template #default="{ row }">
    {{ rateGroupLabel(row.rate_group) }}
  </template>
</el-table-column>
<el-table-column prop="calc_mode" label="计算模式" width="110">
  <template #default="{ row }">
    {{ calcModeLabel(row.calc_mode) }}
  </template>
</el-table-column>
<el-table-column prop="case_type" label="案件类型" width="110">
  <template #default="{ row }">
    {{ caseTypeLabel(row.case_type) }}
  </template>
</el-table-column>
<el-table-column prop="patent_category" label="专利类别" width="100">
  <template #default="{ row }">
    {{ patentCategoryLabel(row.patent_category) }}
  </template>
</el-table-column>
<el-table-column prop="country_code" label="国家/地区" width="100" />
<el-table-column prop="allow_reduction" label="允许减缴" width="90">
  <template #default="{ row }">
    {{ row.allow_reduction ? '是' : '否' }}
  </template>
</el-table-column>
<el-table-column label="有效期" width="200">
  <template #default="{ row }">
    <span v-if="row.effective_from || row.effective_to">
      {{ row.effective_from || '—' }} ~ {{ row.effective_to || '—' }}
    </span>
    <span v-else>—</span>
  </template>
</el-table-column>
```

#### 3.3.2 Remove the existing `描述` column

The `description` field was a frontend-only concept mapped from nowhere meaningful in the backend `FeeRateOut`. The current `FeeRate.description` is never populated from the backend mapper (notice `mapFeeRate()` doesn't map it). Remove the description column. The new dimension columns provide far richer information.

#### 3.3.3 Add label helper functions in `<script setup>`

```typescript
function feeTypeLabel(v?: string | null): string {
  const map: Record<string, string> = { GOV: '官费', SERVICE: '服务费', MISC: '其他' }
  return v ? (map[v] ?? v) : '—'
}

function rateGroupLabel(v?: string | null): string {
  const map: Record<string, string> = { DOMESTIC: '国内', PCT: 'PCT', ANNUITY: '年费' }
  return v ? (map[v] ?? v) : '—'
}

function calcModeLabel(v?: string | null): string {
  const map: Record<string, string> = {
    FIXED: '固定', PER_CLAIM: '按权利要求', PER_PAGE: '按页', TIER: '阶梯'
  }
  return v ? (map[v] ?? v) : '—'
}

function caseTypeLabel(v?: string | null): string {
  const map: Record<string, string> = {
    NORMAL: '普通', PCT_INTL: 'PCT国际', PCT_NATL: 'PCT国内', PRIORITY: '优先权'
  }
  return v ? (map[v] ?? v) : '—'
}

function patentCategoryLabel(v?: string | null): string {
  const map: Record<string, string> = { INV: '发明', UM: '实用新型', DES: '外观设计' }
  return v ? (map[v] ?? v) : '—'
}
```

---

### 3.4 `frontend/src/modules/fees/components/FeeRateForm.vue`

#### 3.4.1 Widen dialog

Change `width="480px"` → `width="680px"` to accommodate the additional fields.

#### 3.4.2 Add form fields (after the existing `描述` textarea, before `</el-form>`)

Layout plan — use `el-row`/`el-col` for grouping:

```html
<!-- Dimension Fields Section -->
<el-divider content-position="left">维度设置</el-divider>

<el-row :gutter="16">
  <el-col :span="8">
    <el-form-item label="费率组" prop="rate_group">
      <el-select v-model="form.rate_group" placeholder="请选择" clearable style="width: 100%">
        <el-option label="国内" value="DOMESTIC" />
        <el-option label="PCT" value="PCT" />
        <el-option label="年费" value="ANNUITY" />
      </el-select>
    </el-form-item>
  </el-col>
  <el-col :span="8">
    <el-form-item label="计算模式" prop="calc_mode">
      <el-select v-model="form.calc_mode" placeholder="请选择" clearable style="width: 100%">
        <el-option label="固定" value="FIXED" />
        <el-option label="按权利要求" value="PER_CLAIM" />
        <el-option label="按页" value="PER_PAGE" />
        <el-option label="阶梯" value="TIER" />
      </el-select>
    </el-form-item>
  </el-col>
  <el-col :span="8">
    <el-form-item label="国家/地区" prop="country_code">
      <el-input v-model="form.country_code" placeholder="例如：CN" maxlength="10" />
    </el-form-item>
  </el-col>
</el-row>

<el-row :gutter="16">
  <el-col :span="8">
    <el-form-item label="案件类型" prop="case_type">
      <el-select v-model="form.case_type" placeholder="请选择" clearable style="width: 100%">
        <el-option label="普通" value="NORMAL" />
        <el-option label="PCT国际" value="PCT_INTL" />
        <el-option label="PCT国内" value="PCT_NATL" />
        <el-option label="优先权" value="PRIORITY" />
      </el-select>
    </el-form-item>
  </el-col>
  <el-col :span="8">
    <el-form-item label="专利类别" prop="patent_category">
      <el-select v-model="form.patent_category" placeholder="请选择" clearable style="width: 100%">
        <el-option label="发明" value="INV" />
        <el-option label="实用新型" value="UM" />
        <el-option label="外观设计" value="DES" />
      </el-select>
    </el-form-item>
  </el-col>
  <el-col :span="8">
    <el-form-item label="允许减缴">
      <el-switch v-model="form.allow_reduction" />
    </el-form-item>
  </el-col>
</el-row>

<el-row :gutter="16">
  <el-col :span="12">
    <el-form-item label="生效日期" prop="effective_from">
      <el-date-picker
        v-model="form.effective_from"
        type="date"
        placeholder="选择日期"
        value-format="YYYY-MM-DD"
        style="width: 100%"
      />
    </el-form-item>
  </el-col>
  <el-col :span="12">
    <el-form-item label="失效日期" prop="effective_to">
      <el-date-picker
        v-model="form.effective_to"
        type="date"
        placeholder="选择日期"
        value-format="YYYY-MM-DD"
        style="width: 100%"
      />
    </el-form-item>
  </el-col>
</el-row>

<el-form-item label="计算参数" prop="calc_params">
  <el-input
    v-model="form.calc_params"
    type="textarea"
    :rows="2"
    placeholder="JSON格式（可选）"
  />
</el-form-item>
```

#### 3.4.3 Update `form` reactive object type and default values

The `form` reactive is currently typed as `FeeRateCreatePayload`. Add the new fields:

```typescript
const form = reactive<FeeRateCreatePayload>({
  name: '',
  rate: 0,
  currency: 'CNY',
  description: '',
  // B4 dimension fields
  rate_group: null,
  country_code: null,
  case_type: null,
  patent_category: null,
  calc_mode: null,
  calc_params: null,
  allow_reduction: false,
  effective_from: null,
  effective_to: null,
})
```

#### 3.4.4 Update `resetForm()` function

Add clearing of all new fields:

```typescript
function resetForm() {
  form.name = ''
  form.rate = 0
  form.currency = 'CNY'
  form.description = ''
  form.rate_group = null
  form.country_code = null
  form.case_type = null
  form.patent_category = null
  form.calc_mode = null
  form.calc_params = null
  form.allow_reduction = false
  form.effective_from = null
  form.effective_to = null
  fieldErrors.value = new Map()
  error.value = null
}
```

#### 3.4.5 Update the `watch(() => props.rate, ...)` handler for edit mode

Add populating new fields when editing an existing rate:

```typescript
watch(() => props.rate, (rate) => {
  if (rate) {
    form.name = rate.name
    form.rate = rate.rate
    form.currency = rate.currency || 'CNY'
    form.description = rate.description || ''
    // B4 dimension fields
    form.rate_group = rate.rate_group ?? null
    form.country_code = rate.country_code ?? null
    form.case_type = rate.case_type ?? null
    form.patent_category = rate.patent_category ?? null
    form.calc_mode = rate.calc_mode ?? null
    form.calc_params = rate.calc_params ?? null
    form.allow_reduction = rate.allow_reduction ?? false
    form.effective_from = rate.effective_from ?? null
    form.effective_to = rate.effective_to ?? null
  } else {
    resetForm()
  }
}, { immediate: true })
```

#### 3.4.6 Update `handleSubmit()` payload

The submit payload currently only sends `name`, `rate`, `currency`, `description`. Add new fields:

```typescript
const payload: FeeRateCreatePayload | FeeRateUpdatePayload = {
  name: form.name,
  rate: form.rate,
  currency: form.currency || undefined,
  description: form.description || undefined,
  // B4 dimension fields
  rate_group: form.rate_group || undefined,
  country_code: form.country_code || undefined,
  case_type: form.case_type || undefined,
  patent_category: form.patent_category || undefined,
  calc_mode: form.calc_mode || undefined,
  calc_params: form.calc_params || undefined,
  allow_reduction: form.allow_reduction ?? undefined,
  effective_from: form.effective_from || undefined,
  effective_to: form.effective_to || undefined,
}
```

---

## 4. Risk Areas & Edge Cases

### 4.1 `fees.ts` not in allowlist
- **Risk**: Without updating `fees.ts`, all dimension data from the backend will be silently discarded by `mapFeeRate()`.
- **Mitigation**: Flag this to the user. The file MUST be updated or the feature is non-functional.

### 4.2 `calc_params` handling
- Backend stores as TEXT (JSON string). Frontend displays as read-only or editable textarea.
- **Decision**: Make it an editable textarea (not read-only) in the form, since `FeeRateCreateIn` and `FeeRateUpdateIn` accept it. The table does NOT show calc_params (too wide/noisy).
- **Edge case**: Invalid JSON — no frontend validation needed since backend stores as plain text.

### 4.3 `allow_reduction` null vs false
- Backend default is `server_default=text("0")` (false). Schema type is `bool | None`.
- **Decision**: Form uses `el-switch` with default `false`. Mapper uses `?? null` to distinguish unset from false.
- In the submit payload, use `?? undefined` so we only send it if explicitly set.

### 4.4 Date fields
- Backend uses `date` type (not datetime). Format: `YYYY-MM-DD`.
- `el-date-picker` with `value-format="YYYY-MM-DD"` ensures correct format.
- Both dates are optional. The table shows a combined "有效期" column with `from ~ to` format.

### 4.5 Table width
- Adding 8 new columns significantly widens the table. Using sensible widths and `show-overflow-tooltip` where needed. The table already uses `stripe` and `size="small"` which helps. Element Plus provides horizontal scrolling automatically.

### 4.6 Description field
- The `description` field in `FeeRate` type is a frontend-only concept. The backend `FeeRateOut` has no `description` field. The current `mapFeeRate()` doesn't map it. The table column shows it but it's always empty.
- **Decision**: Keep the `description` field in the type and form (for future use or notes), but remove the table column since it's always empty and the new columns provide better information.

---

## 5. Execution Order & Dependencies

```
T2: fees.types.ts   ──→  T3: fees.ts mapper  ──→  T4: FeeRates.vue  ──→  T6: Quality Gate
                                                ──→  T5: FeeRateForm.vue ─↗       ↓
                                                                              T7: Review
```

- T2 must complete first (types are imported everywhere)
- T3 depends on T2 (uses the types)
- T4 and T5 can run in parallel after T3 (independent UI components)
- T6 runs after T4+T5 complete
- T7 runs after T6 passes

---

## 6. Quality Gate Checklist

- [ ] `npm run lint` — no ESLint errors
- [ ] `npm run typecheck` — no TypeScript errors
- [ ] `npm run build` — production build succeeds
- [ ] All new fields render in FeeRates.vue table
- [ ] FeeRateForm.vue creates rate with dimension fields
- [ ] FeeRateForm.vue edits rate and pre-fills dimension fields
- [ ] Chinese labels used throughout (no English labels in UI)
- [ ] No `@/` import aliases used
- [ ] No inline hex colors (use CSS variables)
- [ ] All el-select components have `clearable` prop

---

## 7. Acceptance Criteria

1. **FeeRate type** includes all 9 B4 dimension fields
2. **API mapper** passes dimension fields from backend response to frontend type (no data loss)
3. **Create/Update payloads** send dimension fields to backend
4. **Table** displays: 费率组, 计算模式, 案件类型, 专利类别, 国家/地区, 允许减缴, 有效期
5. **Form** allows setting all dimension fields with appropriate input components
6. **Edit mode** pre-fills all dimension fields from existing rate data
7. **Quality gate** passes: lint + typecheck + build
8. **All labels in 简体中文**
