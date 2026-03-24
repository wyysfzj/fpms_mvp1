# FB3 Architect Plan — Case Form Field Expansion

> Generated: 2026-02-27 | Architect Agent | Batch FB3

---

## 1. Scope Summary

Add the 15 new case fields (from backend migration A3) to the frontend Case module.
Organize them in **4 collapsible sections** within CaseCreate, CaseEdit, and CaseDetail pages.

### File Allowlist

| # | File | Action |
|---|------|--------|
| 1 | `frontend/src/api/cases.types.ts` | modify |
| 2 | `frontend/src/modules/cases/pages/CaseCreate.vue` | modify |
| 3 | `frontend/src/modules/cases/pages/CaseEdit.vue` | modify |
| 4 | `frontend/src/modules/cases/pages/CaseDetail.vue` | modify |

---

## 2. CRITICAL ISSUE: `mapCase()` Data Loss in `cases.ts`

### Problem

`frontend/src/api/cases.ts` contains:

```typescript
interface BackendCase { /* only existing fields */ }

function mapCase(input: BackendCase): Case {
    return { /* explicitly constructs object — new fields DROPPED */ }
}

export async function createCase(data: CaseCreatePayload): Promise<Case> {
    const payload = { case_no, client_id, title_cn, patent_category } // manual build
    ...
}
```

Three blockers if `cases.ts` is NOT modified:

1. **`getCase()` / `getCases()`** → `mapCase()` strips all 15 new fields → **CaseDetail and CaseEdit cannot display them**
2. **`createCase()`** manually builds payload with only 4 fields → **new fields never sent to backend on create**
3. **`updateCase()`** sends `data` directly (no manual build) → this one works IF `CaseUpdatePayload` includes new fields, but the returned response still gets stripped by `mapCase()`

### Recommendation: **Option A — Add `cases.ts` to the allowlist** (STRONGLY RECOMMENDED)

**Rationale:**
- Without this change, fields appear in forms but are **never populated from API responses** and **never sent on create**. This makes the entire FB3 batch cosmetic-only — forms exist but don't work.
- The change to `cases.ts` is mechanical (add fields to `BackendCase`, add lines to `mapCase()`, add fields to `createCase()` payload) — low risk, no architectural deviation.
- `updateCase()` already passes `data` directly via PUT, so only `BackendCase` + `mapCase()` + `createCase()` need updating.

**Scope of change in `cases.ts`:**
1. Add 15 fields to `BackendCase` interface
2. Add 15 field mappings to `mapCase()` function
3. Add 15 fields to `createCase()` payload builder

**If Option A is rejected**, the fallback is:
- **Option C**: Document as known limitation. Forms render with empty fields. Users can type values in create/edit, `updateCase()` sends them (if `CaseUpdatePayload` is updated), but on page reload they appear blank because `mapCase()` strips them from the response. This is a **degraded UX**.

> **ACTION REQUIRED**: Team lead must approve adding `cases.ts` to the FB3 allowlist before implementation begins. Tasks T1-T4 below are written assuming Option A is approved.

---

## 3. Field Catalog (15 fields, 4 groups)

### Group 1 — 公告与授权 (Publication & Grant) — 6 fields

| Field | Backend Type | TS Type | Form Widget | Label |
|-------|-------------|---------|-------------|-------|
| `pub_date` | date \| None | `string \| undefined` | `el-date-picker` | 公告日 |
| `pub_no` | str \| None | `string \| undefined` | `el-input` | 公告号 |
| `grant_date` | date \| None | `string \| undefined` | `el-date-picker` | 授权日 |
| `grant_no` | str \| None | `string \| undefined` | `el-input` | 授权号 |
| `patent_no` | str \| None | `string \| undefined` | `el-input` | 专利号 |
| `valid_until` | date \| None | `string \| undefined` | `el-date-picker` | 有效期至 |

### Group 2 — 说明书信息 (Specification) — 3 fields

| Field | Backend Type | TS Type | Form Widget | Label |
|-------|-------------|---------|-------------|-------|
| `spec_pages` | int \| None | `number \| undefined` | `el-input-number` | 说明书页数 |
| `claim_count` | int \| None | `number \| undefined` | `el-input-number` | 权利要求项数 |
| `has_exam_request` | bool \| None | `boolean \| undefined` | `el-switch` | 已提实审请求 |

### Group 3 — 代理人分配 (Agent Assignment) — 3 fields

| Field | Backend Type | TS Type | Form Widget | Label |
|-------|-------------|---------|-------------|-------|
| `primary_agent_id` | str \| None | `string \| undefined` | `el-input` | 主办代理人 |
| `second_agent_id` | str \| None | `string \| undefined` | `el-input` | 辅办代理人 |
| `draftor_id` | str \| None | `string \| undefined` | `el-input` | 撰写人 |

> Note: Agent ID fields use `el-input` (text input for UUID). A user/admin select dropdown requires fetching users from `/api/v1/admin/users`, which is out of scope for FB3. Text input with placeholder "请输入代理人ID" is the pragmatic approach.

### Group 4 — 控制标记 (Control Flags) — 3 fields

| Field | Backend Type | TS Type | Form Widget | Label |
|-------|-------------|---------|-------------|-------|
| `is_fee_monitor` | bool \| None | `boolean \| undefined` | `el-switch` | 费用监控 |
| `fee_reduction` | str \| None | `string \| undefined` | `el-select` | 减免类型 |
| `applicant_kind` | str \| None | `string \| undefined` | `el-select` | 申请人类型 |

**Enum options:**
- `fee_reduction`: `NONE`=不减免, `PARTIAL`=部分减免, `FULL`=全额减免
- `applicant_kind`: `INDIVIDUAL`=个人, `ENTITY`=企业, `UNIV`=高校, `GOV`=政府

---

## 4. File-by-File Change Specification

### 4.1 `cases.types.ts` — Type Expansion

**Add 15 fields to `Case` interface** (after line 33, before `created_at`):

```typescript
// --- Group 1: Publication & Grant ---
pub_date?: string
pub_no?: string
grant_date?: string
grant_no?: string
patent_no?: string
valid_until?: string
// --- Group 2: Specification ---
spec_pages?: number
claim_count?: number
has_exam_request?: boolean
// --- Group 3: Agent Assignment ---
primary_agent_id?: string
second_agent_id?: string
draftor_id?: string
// --- Group 4: Control Flags ---
is_fee_monitor?: boolean
fee_reduction?: string
applicant_kind?: string
```

**Expand `CaseCreatePayload`** — add all 15 fields as optional:

```typescript
export interface CaseCreatePayload {
    case_no: string
    title?: string
    client_id: string | number
    patent_category?: string
    // A3 fields (all optional on create)
    pub_date?: string
    pub_no?: string
    grant_date?: string
    grant_no?: string
    patent_no?: string
    valid_until?: string
    spec_pages?: number
    claim_count?: number
    has_exam_request?: boolean
    primary_agent_id?: string
    second_agent_id?: string
    draftor_id?: string
    is_fee_monitor?: boolean
    fee_reduction?: string
    applicant_kind?: string
}
```

**Expand `CaseUpdatePayload`** — add all 15 fields as optional:

```typescript
export interface CaseUpdatePayload {
    title?: string
    status?: string
    filing_date?: string
    app_date?: string
    notes?: string
    // A3 fields (all optional on update)
    pub_date?: string | null
    pub_no?: string | null
    grant_date?: string | null
    grant_no?: string | null
    patent_no?: string | null
    valid_until?: string | null
    spec_pages?: number | null
    claim_count?: number | null
    has_exam_request?: boolean | null
    primary_agent_id?: string | null
    second_agent_id?: string | null
    draftor_id?: string | null
    is_fee_monitor?: boolean | null
    fee_reduction?: string | null
    applicant_kind?: string | null
}
```

> Note: `CaseUpdatePayload` fields use `| null` to allow explicit clearing (send `null` to backend to unset a value). `CaseCreatePayload` fields use plain `?` (simply omit if not provided).

### 4.2 `cases.ts` — API Layer Fix (REQUIRES ALLOWLIST APPROVAL)

**a) Expand `BackendCase` interface** — add 15 fields matching backend `CaseDetail` schema:

```typescript
// After line 20 (before closing brace)
pub_date?: string | null
pub_no?: string | null
grant_date?: string | null
grant_no?: string | null
patent_no?: string | null
valid_until?: string | null
spec_pages?: number | null
claim_count?: number | null
has_exam_request?: boolean | null
primary_agent_id?: string | null
second_agent_id?: string | null
draftor_id?: string | null
is_fee_monitor?: boolean | null
fee_reduction?: string | null
applicant_kind?: string | null
```

**b) Expand `mapCase()` function** — add 15 field mappings after line 41:

```typescript
// Publication & Grant
pub_date: input.pub_date || undefined,
pub_no: input.pub_no || undefined,
grant_date: input.grant_date || undefined,
grant_no: input.grant_no || undefined,
patent_no: input.patent_no || undefined,
valid_until: input.valid_until || undefined,
// Specification
spec_pages: input.spec_pages ?? undefined,
claim_count: input.claim_count ?? undefined,
has_exam_request: input.has_exam_request ?? undefined,
// Agent Assignment
primary_agent_id: input.primary_agent_id || undefined,
second_agent_id: input.second_agent_id || undefined,
draftor_id: input.draftor_id || undefined,
// Control Flags
is_fee_monitor: input.is_fee_monitor ?? undefined,
fee_reduction: input.fee_reduction || undefined,
applicant_kind: input.applicant_kind || undefined,
```

> **IMPORTANT**: Use `??` (nullish coalescing) for numeric/boolean fields (`spec_pages`, `claim_count`, `has_exam_request`, `is_fee_monitor`) because `||` would incorrectly convert `0` and `false` to `undefined`.

**c) Expand `createCase()` payload builder** — add new fields to the payload object:

```typescript
export async function createCase(data: CaseCreatePayload): Promise<Case> {
    const payload: Record<string, unknown> = {
        case_no: data.case_no,
        client_id: data.client_id,
        title_cn: data.title || undefined,
        patent_category: data.patent_category || undefined,
        // A3 fields — only include if provided
        pub_date: data.pub_date || undefined,
        pub_no: data.pub_no || undefined,
        grant_date: data.grant_date || undefined,
        grant_no: data.grant_no || undefined,
        patent_no: data.patent_no || undefined,
        valid_until: data.valid_until || undefined,
        spec_pages: data.spec_pages ?? undefined,
        claim_count: data.claim_count ?? undefined,
        has_exam_request: data.has_exam_request ?? undefined,
        primary_agent_id: data.primary_agent_id || undefined,
        second_agent_id: data.second_agent_id || undefined,
        draftor_id: data.draftor_id || undefined,
        is_fee_monitor: data.is_fee_monitor ?? undefined,
        fee_reduction: data.fee_reduction || undefined,
        applicant_kind: data.applicant_kind || undefined,
    }
    ...
}
```

> `updateCase()` already sends `data` directly (`http.put(..., data)`) — no change needed for that function.

### 4.3 `CaseCreate.vue` — New Collapsible Sections

**Template changes:**

After the existing `form-section` (基础信息, closes at line 64), add 4 collapsible sections inside the `el-form`:

```vue
<!-- After 基础信息 section, still inside <el-form> -->
<el-collapse v-model="expandedSections" class="case-extra-sections">
  <!-- Group 1: Publication & Grant -->
  <el-collapse-item title="公告与授权" name="pub_grant">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="公告日">
          <el-date-picker v-model="form.pub_date" type="date" placeholder="请选择公告日"
            format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="公告号">
          <el-input v-model="form.pub_no" placeholder="请输入公告号" />
        </el-form-item>
      </el-col>
    </el-row>
    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="授权日">
          <el-date-picker v-model="form.grant_date" type="date" placeholder="请选择授权日"
            format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="授权号">
          <el-input v-model="form.grant_no" placeholder="请输入授权号" />
        </el-form-item>
      </el-col>
    </el-row>
    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="专利号">
          <el-input v-model="form.patent_no" placeholder="请输入专利号" />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="有效期至">
          <el-date-picker v-model="form.valid_until" type="date" placeholder="请选择有效期至"
            format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
      </el-col>
    </el-row>
  </el-collapse-item>

  <!-- Group 2: Specification -->
  <el-collapse-item title="说明书信息" name="spec">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-form-item label="说明书页数">
          <el-input-number v-model="form.spec_pages" :min="0" controls-position="right"
            placeholder="页数" style="width: 100%" />
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="权利要求项数">
          <el-input-number v-model="form.claim_count" :min="0" controls-position="right"
            placeholder="项数" style="width: 100%" />
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="已提实审请求">
          <el-switch v-model="form.has_exam_request" />
        </el-form-item>
      </el-col>
    </el-row>
  </el-collapse-item>

  <!-- Group 3: Agent Assignment -->
  <el-collapse-item title="代理人分配" name="agent">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-form-item label="主办代理人">
          <el-input v-model="form.primary_agent_id" placeholder="请输入代理人ID" />
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="辅办代理人">
          <el-input v-model="form.second_agent_id" placeholder="请输入代理人ID" />
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="撰写人">
          <el-input v-model="form.draftor_id" placeholder="请输入撰写人ID" />
        </el-form-item>
      </el-col>
    </el-row>
  </el-collapse-item>

  <!-- Group 4: Control Flags -->
  <el-collapse-item title="控制标记" name="flags">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-form-item label="费用监控">
          <el-switch v-model="form.is_fee_monitor" />
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="减免类型">
          <el-select v-model="form.fee_reduction" placeholder="请选择" clearable style="width:100%">
            <el-option label="不减免" value="NONE" />
            <el-option label="部分减免" value="PARTIAL" />
            <el-option label="全额减免" value="FULL" />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="申请人类型">
          <el-select v-model="form.applicant_kind" placeholder="请选择" clearable style="width:100%">
            <el-option label="个人" value="INDIVIDUAL" />
            <el-option label="企业" value="ENTITY" />
            <el-option label="高校" value="UNIV" />
            <el-option label="政府" value="GOV" />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>
  </el-collapse-item>
</el-collapse>
```

**Script changes:**

```typescript
// Add ref for collapse state (default: all collapsed)
const expandedSections = ref<string[]>([])

// Expand form reactive with new fields (defaults to undefined/empty)
const form = reactive<CaseCreatePayload>({
    case_no: '',
    title: '',
    client_id: '',
    // New fields — all undefined by default (optional)
})
```

> Note: `CaseCreatePayload` already has the 15 new optional fields from types expansion. We don't need to explicitly list them in `reactive()` — Vue 3 reactive handles them. But `el-input-number` and `el-switch` need explicit defaults if we want to avoid `undefined` binding warnings. We initialize them only when the user interacts (leave as `undefined` in reactive, which is fine for `v-model` on these components).

**No additional scoped style changes needed** — the existing `.case-form` styles apply, and `el-collapse` provides built-in styling.

### 4.4 `CaseEdit.vue` — New Collapsible Sections

**Template changes:**

After the existing "备注" section (closes at line 108), add the same 4 collapsible sections as CaseCreate (identical template structure).

**Script changes:**

```typescript
// Add ref for collapse state
const expandedSections = ref<string[]>([])

// Expand CaseUpdatePayload in form reactive
const form = reactive<CaseUpdatePayload>({
    title: '',
    status: '',
    filing_date: '',
    app_date: '',
    notes: '',
    // New fields will be populated from fetchCase()
})

// In fetchCase(), after existing field population (line 165):
form.pub_date = caseData.value.pub_date || ''
form.pub_no = caseData.value.pub_no || ''
form.grant_date = caseData.value.grant_date || ''
form.grant_no = caseData.value.grant_no || ''
form.patent_no = caseData.value.patent_no || ''
form.valid_until = caseData.value.valid_until || ''
form.spec_pages = caseData.value.spec_pages ?? undefined
form.claim_count = caseData.value.claim_count ?? undefined
form.has_exam_request = caseData.value.has_exam_request ?? undefined
form.primary_agent_id = caseData.value.primary_agent_id || ''
form.second_agent_id = caseData.value.second_agent_id || ''
form.draftor_id = caseData.value.draftor_id || ''
form.is_fee_monitor = caseData.value.is_fee_monitor ?? undefined
form.fee_reduction = caseData.value.fee_reduction || ''
form.applicant_kind = caseData.value.applicant_kind || ''
```

> **Important nuance**: For date/string fields, use `|| ''` (empty string for cleared state). For number/boolean fields, use `?? undefined` to preserve `0`/`false` as valid values.

### 4.5 `CaseDetail.vue` — Display New Fields in Overview Tab

**Template changes:**

After the existing `info-grid` (closes at line 92) and before the `notes-section` (line 93), add 4 new display sections:

```vue
<!-- After existing info-grid, before notes-section -->

<!-- Group 1: Publication & Grant -->
<div v-if="caseData.pub_date || caseData.pub_no || caseData.grant_date || caseData.grant_no || caseData.patent_no || caseData.valid_until" class="info-section">
  <h4 class="info-section-title">公告与授权</h4>
  <div class="info-grid">
    <div class="info-item">
      <span class="info-label">公告日</span>
      <span class="info-value">{{ caseData.pub_date || '-' }}</span>
    </div>
    <div class="info-item">
      <span class="info-label">公告号</span>
      <span class="info-value">{{ caseData.pub_no || '-' }}</span>
    </div>
    <div class="info-item">
      <span class="info-label">授权日</span>
      <span class="info-value">{{ caseData.grant_date || '-' }}</span>
    </div>
    <div class="info-item">
      <span class="info-label">授权号</span>
      <span class="info-value">{{ caseData.grant_no || '-' }}</span>
    </div>
    <div class="info-item">
      <span class="info-label">专利号</span>
      <span class="info-value">{{ caseData.patent_no || '-' }}</span>
    </div>
    <div class="info-item">
      <span class="info-label">有效期至</span>
      <span class="info-value">{{ caseData.valid_until || '-' }}</span>
    </div>
  </div>
</div>

<!-- Group 2: Specification -->
<div v-if="caseData.spec_pages != null || caseData.claim_count != null || caseData.has_exam_request != null" class="info-section">
  <h4 class="info-section-title">说明书信息</h4>
  <div class="info-grid">
    <div class="info-item">
      <span class="info-label">说明书页数</span>
      <span class="info-value">{{ caseData.spec_pages ?? '-' }}</span>
    </div>
    <div class="info-item">
      <span class="info-label">权利要求项数</span>
      <span class="info-value">{{ caseData.claim_count ?? '-' }}</span>
    </div>
    <div class="info-item">
      <span class="info-label">已提实审请求</span>
      <span class="info-value">{{ caseData.has_exam_request === true ? '是' : caseData.has_exam_request === false ? '否' : '-' }}</span>
    </div>
  </div>
</div>

<!-- Group 3: Agent Assignment -->
<div v-if="caseData.primary_agent_id || caseData.second_agent_id || caseData.draftor_id" class="info-section">
  <h4 class="info-section-title">代理人分配</h4>
  <div class="info-grid">
    <div class="info-item">
      <span class="info-label">主办代理人</span>
      <span class="info-value">{{ caseData.primary_agent_id || '-' }}</span>
    </div>
    <div class="info-item">
      <span class="info-label">辅办代理人</span>
      <span class="info-value">{{ caseData.second_agent_id || '-' }}</span>
    </div>
    <div class="info-item">
      <span class="info-label">撰写人</span>
      <span class="info-value">{{ caseData.draftor_id || '-' }}</span>
    </div>
  </div>
</div>

<!-- Group 4: Control Flags -->
<div v-if="caseData.is_fee_monitor != null || caseData.fee_reduction || caseData.applicant_kind" class="info-section">
  <h4 class="info-section-title">控制标记</h4>
  <div class="info-grid">
    <div class="info-item">
      <span class="info-label">费用监控</span>
      <span class="info-value">{{ caseData.is_fee_monitor ? '是' : '否' }}</span>
    </div>
    <div class="info-item">
      <span class="info-label">减免类型</span>
      <span class="info-value">{{ feeReductionText }}</span>
    </div>
    <div class="info-item">
      <span class="info-label">申请人类型</span>
      <span class="info-value">{{ applicantKindText }}</span>
    </div>
  </div>
</div>
```

**Script changes:**

Add computed helpers for enum display:

```typescript
const FEE_REDUCTION_MAP: Record<string, string> = {
    NONE: '不减免', PARTIAL: '部分减免', FULL: '全额减免'
}
const APPLICANT_KIND_MAP: Record<string, string> = {
    INDIVIDUAL: '个人', ENTITY: '企业', UNIV: '高校', GOV: '政府'
}

const feeReductionText = computed(() =>
    caseData.value?.fee_reduction
        ? FEE_REDUCTION_MAP[caseData.value.fee_reduction] || caseData.value.fee_reduction
        : '-'
)
const applicantKindText = computed(() =>
    caseData.value?.applicant_kind
        ? APPLICANT_KIND_MAP[caseData.value.applicant_kind] || caseData.value.applicant_kind
        : '-'
)
```

**Style note:** The existing `.info-grid`, `.info-item`, `.info-label`, `.info-value` classes from the detail page are reused. Add minimal styling for `.info-section` and `.info-section-title`:

```css
.info-section {
    margin-top: 20px;
}
.info-section-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-main);
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--color-border);
}
```

---

## 5. Task Breakdown

| Task | Files | Dependencies | Estimated Lines |
|------|-------|-------------|----------------|
| **T0** | `cases.ts` (REQUIRES APPROVAL) | None | ~30 lines added |
| **T1** | `cases.types.ts` | None | ~30 lines added |
| **T2** | `CaseCreate.vue` | T0, T1 | ~100 lines added |
| **T3** | `CaseEdit.vue` | T0, T1 | ~120 lines added |
| **T4** | `CaseDetail.vue` | T0, T1 | ~90 lines added |

**Dependency graph:**
```
T0 + T1 (parallel, no deps)
   └──> T2, T3, T4 (parallel after T0+T1 done)
         └──> Quality Gate (lint + typecheck + build)
               └──> Review Agent
```

---

## 6. Acceptance Criteria Checklist

- [ ] `Case` interface in `cases.types.ts` has all 15 new optional fields
- [ ] `CaseCreatePayload` has all 15 new optional fields
- [ ] `CaseUpdatePayload` has all 15 new optional fields (with `| null` for clearability)
- [ ] `BackendCase` in `cases.ts` has all 15 fields (if approved)
- [ ] `mapCase()` maps all 15 fields using correct `||` vs `??` operators (if approved)
- [ ] `createCase()` payload includes all 15 fields (if approved)
- [ ] CaseCreate.vue has 4 collapsible sections with all 15 fields
- [ ] CaseCreate.vue sections are collapsed by default
- [ ] CaseEdit.vue has 4 collapsible sections with all 15 fields
- [ ] CaseEdit.vue populates new fields from `getCase()` response
- [ ] CaseEdit.vue sections are collapsed by default
- [ ] CaseDetail.vue overview tab shows 4 new info sections
- [ ] CaseDetail.vue sections use `v-if` to hide when all fields in group are empty
- [ ] CaseDetail.vue boolean fields display as 是/否
- [ ] CaseDetail.vue enum fields display Chinese labels (not raw enum values)
- [ ] Date fields use `value-format="YYYY-MM-DD"` and `format="YYYY-MM-DD"`
- [ ] Number fields use `el-input-number` with `min="0"`
- [ ] Boolean fields use `el-switch`
- [ ] `npm run lint` passes
- [ ] `npm run typecheck` passes
- [ ] `npm run build` succeeds

---

## 7. Risk / Issues Log

| # | Risk | Severity | Mitigation |
|---|------|----------|-----------|
| R1 | `cases.ts` not in allowlist — mapCase() strips new fields | **CRITICAL** | Recommend Option A: add to allowlist. Team lead must approve. |
| R2 | `el-input-number` with `undefined` initial value may show `0` | LOW | Test behavior; if issue, initialize to `null` and handle in payload |
| R3 | Agent ID fields show raw UUIDs, not user-friendly names | LOW | Out of scope for FB3. Future batch can add user dropdown. |
| R4 | `createCase()` sends `undefined` values in payload | LOW | Backend ignores `None`/missing fields. Axios strips `undefined` from JSON. |
| R5 | CaseEdit uses `updateCase()` which passes form data directly — new fields with empty string `''` may overwrite existing values with empty | MEDIUM | Handle in payload cleanup: convert empty strings to `undefined` before sending, or rely on backend to treat empty string as no-op. Verify backend behavior. |
| R6 | Collapsible sections add visual weight to CaseCreate for simple cases | LOW | Default collapsed — users only expand when needed. |

---

## 8. Out of Scope (Explicit)

- No changes to `CaseList.vue` (list columns unchanged)
- No changes to `labels.zh.ts` (inline Chinese labels used in forms/detail)
- No changes to `displayText.ts` (enum maps defined locally in CaseDetail.vue)
- No conditional display based on `case_type`
- No user dropdown for agent ID fields
- No form validation rules for new fields (all optional)
