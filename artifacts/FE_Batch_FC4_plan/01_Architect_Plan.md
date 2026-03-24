# FC4 Architect Plan — Billing Offset Reversal + Receipt Enrichment

## 1. Backend API Contract Summary

### Offset Endpoints (Confirmed)
| Method | Path | Permission | Response Shape |
|--------|------|-----------|----------------|
| POST | `/api/v1/offsets` | Payment.Create | `OffsetResponse` |
| POST | `/api/v1/offsets/{offset_id}/reverse` | Billing.Edit | `OffsetResponse` |

**OffsetResponse** (from `schemas.py:89-97`):
```python
{
    id: str,
    payment_line_id: str,
    bill_id: str,
    offset_amt: Decimal,
    offset_date: date | None,
    is_reversed: bool
}
```

**Offset ORM model** (from `models.py:100-114`) also has:
- `reversed_at: datetime | None` — set in `reverse_offset()` service but **NOT returned by OffsetResponse schema**

### Bill Detail Endpoint
| Method | Path | Permission | Response |
|--------|------|-----------|----------|
| GET | `/api/v1/bills/{bill_id}` | Bill.Read | Minimal dict (id, bill_no, client_id, currency, direction, status) |

**Critical**: `GET /bills/{bill_id}` does NOT include offsets, items, amounts, or balance. The frontend `getBill()` currently works because it maps missing fields with defaults.

### Case Receipt Endpoint
| Method | Path | Permission | Response |
|--------|------|-----------|----------|
| GET | `/api/v1/cases/{case_id}/receipts` | CaseReceipt.Read | Single CaseReceipt row |

**Actual backend response** (from `api.py:576-589`):
```python
{
    id: str,
    case_id: str,
    fee_type: str | None,
    currency: str,
    receivable_amt: Decimal,
    received_amt: Decimal,
    last_receipt_date: date | None,
    fee_code: str | None,       # B5 NEW
    year_no: int | None,         # B5 NEW
    is_arrears: bool | None,     # B5 NEW
    invoice_no: str | None,      # B5 NEW
    is_commissionable: bool | None  # B5 NEW
}
```

---

## 2. Pre-Existing Implementation Inventory

### Already Done (DO NOT duplicate)
| File | Line | What's Done |
|------|------|-------------|
| `billing.ts:66-73` | `BackendOffset` interface | Has `is_reversed: boolean` |
| `billing.ts:144-155` | `mapOffset()` function | Maps `is_reversed` |
| `billing.ts:309-312` | `reverseOffset()` API fn | `POST /offsets/{id}/reverse` |
| `billing.types.ts:120-129` | `OffsetListItem` type | Has `is_reversed: boolean` |

### NOT Done (needs implementation)
| Item | Status | File |
|------|--------|------|
| `reversed_at` in BackendOffset | Missing | `billing.ts` |
| `reversed_at` in OffsetListItem | Missing | `billing.types.ts` |
| `reversed_at` in mapOffset() | Missing | `billing.ts` |
| Offsets section in BillDetail | Missing entirely | `BillDetail.vue` |
| Enriched CaseReceipt fields in types | Missing | `billing.types.ts` |
| CaseReceipt backend-to-frontend mapper | Missing | `billing.ts` |
| Enriched fields display | Missing | `CaseReceiptsSummary.vue` |

---

## 3. Resolution of Investigation Items

### A. How to Get Offsets for a Bill — RESOLVED

**Finding**: There is NO `GET /offsets?bill_id=X` backend endpoint. The only offset-related endpoints are `POST /offsets` (create) and `POST /offsets/{id}/reverse` (reverse). The `GET /bills/{bill_id}` response does NOT include offsets.

**Frontend `getOffsets()`** (billing.ts:284-296) is a confirmed stub returning empty `{ items: [], page, page_size, total: 0 }`.

**Resolution**: Since this is a frontend-only batch and we cannot add backend endpoints:
1. Update the `getOffsets()` stub signature to accept `bill_id?: string` parameter (future-proofing the interface)
2. Add the complete offsets UI section in BillDetail with proper table, reverse button, and empty state
3. When the stub is called, the empty state `"暂无抵扣记录"` will display
4. The `reverseOffset(id)` function IS functional (real backend endpoint) — wire the reverse button to it
5. **Document in findings.md** that backend needs `GET /offsets?bill_id=X` to make the UI functional

### B. CaseReceipt API Shape Mismatch — RESOLVED

**Finding**: The backend returns a SINGLE `CaseReceipt` row with flat fields (`receivable_amt`, `received_amt`, `fee_type`, etc.). The frontend `CaseReceiptsSummary` type expects an aggregated summary (`total_billed`, `total_paid`, `total_outstanding`, `bills[]`). These are completely different shapes.

The current `getCaseReceipts()` does `http.get<CaseReceiptsSummary>(...)` and returns `response.data` directly — this means the summary cards (`total_billed`, `total_paid`, `total_outstanding`) are all showing `undefined`/`0` because the backend never returns those fields.

**Resolution**:
1. Add a `BackendCaseReceipt` interface in `billing.ts` matching the actual backend response
2. Add a `mapCaseReceipt()` mapper:
   - `receivable_amt` → `total_billed`
   - `received_amt` → `total_paid`
   - `receivable_amt - received_amt` → `total_outstanding`
   - `bills` → `[]` (backend doesn't return a bill list)
   - Pass through enriched fields: `fee_code`, `year_no`, `is_arrears`, `invoice_no`, `is_commissionable`
3. Update `CaseReceiptsSummary` type to include optional enriched fields
4. Update `getCaseReceipts()` to use `BackendCaseReceipt` as generic and apply mapper
5. Update `CaseReceiptsSummary.vue` to display the enriched fields

---

## 4. File-by-File Changes

### File 1: `frontend/src/api/billing.types.ts`

**Change 1a** — Add `reversed_at` to `OffsetListItem` (line 120-129):
```typescript
export interface OffsetListItem {
    id: string
    payment_line_id: string
    bill_id: string
    amount: number
    currency: string
    offset_date?: string
    is_reversed: boolean
    reversed_at?: string          // NEW — from B5 backend
    created_at: string
}
```

**Change 1b** — Add enriched fields to `CaseReceiptsSummary` (line 139-146):
```typescript
export interface CaseReceiptsSummary {
    case_id: string
    total_billed: number
    total_paid: number
    total_outstanding: number
    currency: string
    bills: CaseReceiptBill[]
    // B5 enriched fields
    fee_type?: string
    fee_code?: string
    year_no?: number
    is_arrears?: boolean
    invoice_no?: string
    is_commissionable?: boolean
}
```

### File 2: `frontend/src/api/billing.ts`

**Change 2a** — Add `reversed_at` to `BackendOffset` (line 66-73):
```typescript
interface BackendOffset {
    id: string
    payment_line_id: string
    bill_id: string
    offset_amt: string | number
    offset_date?: string | null
    is_reversed: boolean
    reversed_at?: string | null    // NEW
}
```

**Change 2b** — Update `mapOffset()` to include `reversed_at` (line 144-155):
```typescript
function mapOffset(input: BackendOffset): OffsetListItem {
    return {
        id: input.id,
        payment_line_id: input.payment_line_id,
        bill_id: input.bill_id,
        amount: asNumber(input.offset_amt),
        currency: 'CNY',
        offset_date: input.offset_date || undefined,
        is_reversed: input.is_reversed,
        reversed_at: input.reversed_at || undefined,  // NEW
        created_at: input.offset_date || '',
    }
}
```

**Change 2c** — Add `BackendCaseReceipt` interface and mapper (before `getCaseReceipts`):
```typescript
interface BackendCaseReceipt {
    id: string
    case_id: string
    fee_type?: string | null
    currency: string
    receivable_amt: string | number
    received_amt: string | number
    last_receipt_date?: string | null
    fee_code?: string | null
    year_no?: number | null
    is_arrears?: boolean | null
    invoice_no?: string | null
    is_commissionable?: boolean | null
}

function mapCaseReceipt(input: BackendCaseReceipt): CaseReceiptsSummary {
    const totalBilled = asNumber(input.receivable_amt)
    const totalPaid = asNumber(input.received_amt)
    return {
        case_id: input.case_id,
        total_billed: totalBilled,
        total_paid: totalPaid,
        total_outstanding: totalBilled - totalPaid,
        currency: input.currency || 'CNY',
        bills: [],
        fee_type: input.fee_type || undefined,
        fee_code: input.fee_code || undefined,
        year_no: input.year_no ?? undefined,
        is_arrears: input.is_arrears ?? undefined,
        invoice_no: input.invoice_no || undefined,
        is_commissionable: input.is_commissionable ?? undefined,
    }
}
```

**Change 2d** — Update `getCaseReceipts()` (line 319-322):
```typescript
export async function getCaseReceipts(caseId: number | string): Promise<CaseReceiptsSummary> {
    const response = await http.get<BackendCaseReceipt>(`/cases/${caseId}/receipts`)
    return mapCaseReceipt(response.data)
}
```

**Change 2e** — Update `getOffsets()` signature to accept `bill_id` (line 284-296):
```typescript
export async function getOffsets(
    params: { page?: number; page_size?: number; bill_id?: string } = {}
): Promise<Pagination<OffsetListItem>> {
    const page = params.page || 1
    const pageSize = params.page_size || 20

    // TODO: Backend needs GET /offsets?bill_id=X endpoint
    return {
        items: [],
        page,
        page_size: pageSize,
        total: 0,
    }
}
```

### File 3: `frontend/src/modules/billing/pages/BillDetail.vue`

**Change 3a** — Add new tab "抵扣" with offsets table after the "overview" tab pane:
```html
<el-tab-pane label="抵扣记录" name="offsets">
  <div class="case-panel">
    <h3 class="panel-heading">抵扣记录</h3>

    <div v-if="offsetsLoading" class="items-empty">
      <el-skeleton :rows="3" animated />
    </div>

    <div v-else-if="offsets.length === 0" class="items-empty">
      <p>暂无抵扣记录。</p>
    </div>

    <el-table
      v-else
      :data="offsets"
      stripe
      size="small"
      class="compact-table"
    >
      <el-table-column label="抵扣日期" width="130">
        <template #default="{ row }">
          {{ row.offset_date ? formatDate(row.offset_date) : '—' }}
        </template>
      </el-table-column>
      <el-table-column label="抵扣金额" width="140" align="right">
        <template #default="{ row }">
          <span class="mono-num">{{ formatAmount(row.amount) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="120">
        <template #default="{ row }">
          <el-tag v-if="row.is_reversed" type="danger" size="small">已撤销</el-tag>
          <el-tag v-else type="success" size="small">有效</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-popconfirm
            v-if="!row.is_reversed"
            title="确定撤销此抵扣？"
            confirm-button-text="确定"
            cancel-button-text="取消"
            @confirm="handleReverseOffset(row.id)"
          >
            <template #reference>
              <el-button type="danger" size="small" text>撤销</el-button>
            </template>
          </el-popconfirm>
          <span v-else class="text-muted">—</span>
        </template>
      </el-table-column>
    </el-table>
  </div>
</el-tab-pane>
```

**Change 3b** — Add script imports and state:
```typescript
// Add to imports
import { getBill, printBill, getOffsets, reverseOffset } from '../../../api/billing'
import type { BillDetail, OffsetListItem } from '../../../api/billing.types'

// Add state refs
const offsets = ref<OffsetListItem[]>([])
const offsetsLoading = ref(false)
```

**Change 3c** — Add fetch and reverse functions:
```typescript
async function fetchOffsets() {
  if (!billId.value) return
  offsetsLoading.value = true
  try {
    const result = await getOffsets({ bill_id: billId.value })
    offsets.value = result.items
  } catch {
    // Silent fail — offsets are supplementary
  } finally {
    offsetsLoading.value = false
  }
}

async function handleReverseOffset(offsetId: string) {
  try {
    await reverseOffset(offsetId)
    ElMessage.success('抵扣已撤销')
    // Refresh both bill and offsets
    await Promise.all([fetchBill(), fetchOffsets()])
  } catch (err) {
    error.value = err as ApiError
  }
}
```

**Change 3d** — Call `fetchOffsets()` in `onMounted`:
```typescript
onMounted(() => {
  fetchBill()
  fetchOffsets()
})
```

**Change 3e** — Add CSS for `.text-muted`:
```css
.text-muted {
  color: var(--text-sub);
  font-size: 13px;
}
```

### File 4: `frontend/src/modules/cases/components/CaseReceiptsSummary.vue`

**Change 4a** — Add enriched fields info section between summary cards and bills table:
```html
<!-- Enriched Receipt Info (B5) -->
<div v-if="hasEnrichedFields" class="enriched-info">
  <div class="info-grid">
    <div v-if="receipts.fee_code" class="info-item">
      <span class="info-label">费用代码</span>
      <span class="info-value mono-num">{{ receipts.fee_code }}</span>
    </div>
    <div v-if="receipts.fee_type" class="info-item">
      <span class="info-label">费用类型</span>
      <span class="info-value">{{ receipts.fee_type }}</span>
    </div>
    <div v-if="receipts.year_no != null" class="info-item">
      <span class="info-label">年度</span>
      <span class="info-value">{{ receipts.year_no }}</span>
    </div>
    <div v-if="receipts.invoice_no" class="info-item">
      <span class="info-label">发票号</span>
      <span class="info-value mono-num">{{ receipts.invoice_no }}</span>
    </div>
    <div class="info-item">
      <span class="info-label">欠费状态</span>
      <el-tag v-if="receipts.is_arrears" type="danger" size="small">欠费</el-tag>
      <span v-else class="info-value">正常</span>
    </div>
    <div v-if="receipts.is_commissionable != null" class="info-item">
      <span class="info-label">可提成</span>
      <span class="info-value">{{ receipts.is_commissionable ? '是' : '否' }}</span>
    </div>
  </div>
</div>
```

**Change 4b** — Add computed for `hasEnrichedFields`:
```typescript
const hasEnrichedFields = computed(() => {
  if (!receipts.value) return false
  return !!(
    receipts.value.fee_code ||
    receipts.value.fee_type ||
    receipts.value.year_no != null ||
    receipts.value.invoice_no ||
    receipts.value.is_arrears != null ||
    receipts.value.is_commissionable != null
  )
})
```

**Change 4c** — Add CSS for enriched info:
```css
.enriched-info {
  margin-bottom: 20px;
  padding: 12px 16px;
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  border-radius: 8px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 12px;
  color: var(--text-sub);
}

.info-value {
  font-size: 14px;
  color: var(--text-main);
}
```

---

## 5. Chinese Label Mapping

| Key | Chinese | Context |
|-----|---------|---------|
| Offsets tab label | 抵扣记录 | BillDetail tab |
| Offsets panel heading | 抵扣记录 | BillDetail panel |
| Offset date column | 抵扣日期 | Offsets table |
| Offset amount column | 抵扣金额 | Offsets table |
| Status column | 状态 | Offsets table |
| Actions column | 操作 | Offsets table |
| Reversed tag | 已撤销 | Offset row danger tag |
| Active tag | 有效 | Offset row success tag |
| Reverse button | 撤销 | Popconfirm trigger |
| Popconfirm title | 确定撤销此抵扣？ | Popconfirm |
| Popconfirm confirm | 确定 | Button text |
| Popconfirm cancel | 取消 | Button text |
| Reverse success msg | 抵扣已撤销 | ElMessage |
| Empty offsets | 暂无抵扣记录。 | Empty state |
| Fee code | 费用代码 | Receipt info |
| Fee type | 费用类型 | Receipt info |
| Year | 年度 | Receipt info |
| Invoice no | 发票号 | Receipt info |
| Arrears status | 欠费状态 | Receipt info |
| Arrears tag | 欠费 | Danger tag |
| Normal | 正常 | No arrears |
| Commissionable | 可提成 | Receipt info |
| Yes / No | 是 / 否 | Boolean display |

**Note**: Labels are hardcoded inline (matching `CaseReceiptsSummary.vue` existing pattern of inline Chinese strings) rather than added to `labels.zh.ts`, since the existing component uses inline Chinese (lines 18-28). The BillDetail labels for offsets are also inline, consistent with how the existing tab labels are already defined via `ZH.billDetail` constants — but since FC4 doesn't modify `labels.zh.ts` (not in allowlist), we use inline strings.

---

## 6. Risk Areas and Edge Cases

### Risk 1: `getOffsets()` stub returns empty
- **Impact**: Offsets tab always shows "暂无抵扣记录" until backend adds `GET /offsets?bill_id=X`
- **Mitigation**: UI is fully wired — when backend adds endpoint, only `getOffsets()` body needs updating
- **Severity**: Low (known limitation, documented)

### Risk 2: `reversed_at` not in backend OffsetResponse
- **Impact**: `reversed_at` will always be `undefined` from backend responses since `OffsetResponse` schema doesn't include it
- **Mitigation**: The field is optional in frontend types. Backend model has it (`models.py:114`), but schema needs update. Frontend is ready.
- **Severity**: Low

### Risk 3: CaseReceipt mapper — single row assumption
- **Impact**: Backend returns only ONE `CaseReceipt` per case (first match). If a case has multiple receipt rows, only the first is returned.
- **Mitigation**: Mapper handles the single-row case correctly. Multiple-row aggregation would require backend changes.
- **Severity**: Low

### Risk 4: CSS variable references
- **Variables used**: `--text-sub`, `--text-main`, `--font-mono`, `--bg-card`, `--border-light`, `--color-success`
- All confirmed to exist in the project's CSS variable system (from MEMORY.md)

### Risk 5: `computed` import needed in CaseReceiptsSummary.vue
- Currently imports: `ref, onMounted, watch` — must add `computed`

---

## 7. Quality Gate Checklist

- [ ] `cd frontend && npm run lint` — passes
- [ ] `cd frontend && npm run typecheck` — passes
- [ ] `cd frontend && npm run build` — passes
- [ ] Only 4 allowlisted files modified
- [ ] No `@/` path aliases used
- [ ] No inline hex colors — CSS variables only
- [ ] All UI labels in 简体中文
- [ ] Element Plus components only (el-table, el-tag, el-popconfirm, el-button, el-skeleton)
- [ ] No backend files modified
- [ ] `reverseOffset()` wired to real endpoint
- [ ] Empty state shown for stub `getOffsets()`

---

## 8. Acceptance Criteria

1. **billing.types.ts**: `OffsetListItem` has `reversed_at?: string`. `CaseReceiptsSummary` has enriched fields (`fee_code`, `year_no`, `is_arrears`, `invoice_no`, `is_commissionable`, `fee_type`).
2. **billing.ts**: `BackendOffset` has `reversed_at`. `mapOffset()` maps it. `BackendCaseReceipt` interface added. `mapCaseReceipt()` bridges backend→frontend shape. `getCaseReceipts()` uses mapper. `getOffsets()` accepts `bill_id`.
3. **BillDetail.vue**: New "抵扣记录" tab with offsets table. Reverse button with `el-popconfirm` ("确定撤销此抵扣？"). "已撤销" danger tag for reversed offsets. "有效" success tag for active offsets. Empty state "暂无抵扣记录" (due to stub). `handleReverseOffset()` calls `reverseOffset()` and refreshes.
4. **CaseReceiptsSummary.vue**: Enriched info grid showing fee_code, fee_type, year_no, invoice_no. "欠费" danger tag when `is_arrears === true`. "可提成" field showing 是/否.
5. **Quality gates pass**: lint + typecheck + build all green.

---

## 9. Task Dependency Graph

```
Task #2 (billing.types.ts) ──┐
                              ├──→ Task #4 (BillDetail.vue)
Task #3 (billing.ts)     ────┤
                              └──→ Task #5 (CaseReceiptsSummary.vue)
                                        │
                                        ▼
                              Task #6 (Quality Gate)
                                        │
                                        ▼
                              Task #7 (Review)
```

Tasks #2 and #3 can run in parallel. Tasks #4 and #5 depend on #2 and #3. Task #6 depends on all impl tasks. Task #7 depends on #6.
