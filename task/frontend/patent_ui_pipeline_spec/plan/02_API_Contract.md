# API Contract — Pipeline Dashboard Backend Enrichment

**Agreed by**: Backend Agent + Frontend Agent
**Date**: 2026-02-22
**Status**: AGREED

---

## Overview

Four existing list endpoints are enriched with additional fields to support the Pipeline Dashboard UI. All changes are **additive** — no existing fields are removed or renamed. No new endpoints are created.

All list endpoints continue to use the standard pagination wrapper:

```json
{
  "items": [...],
  "page": 1,
  "page_size": 20,
  "total": 42
}
```

---

## BE-01: Enrich `GET /api/v1/bills` List Response

### Current Response Item
```json
{
  "id": "uuid",
  "bill_no": "BILL-2023-109",
  "client_id": "uuid",
  "currency": "CNY"
}
```

### Enhanced Response Item
```json
{
  "id": "uuid",
  "bill_no": "BILL-2023-109",
  "client_id": "uuid",
  "client_name": "小米移动",
  "currency": "CNY",
  "status": "UNSETTLED",
  "amount": "8500.00",
  "balance": "8500.00",
  "bill_date": "2023-10-15",
  "due_date": "2023-11-10"
}
```

### Field Details

| Field | Type | Source | Nullable | Notes |
|-------|------|--------|----------|-------|
| `status` | string | `Bill.status` column | No | Values: "UNSETTLED", "PARTIALLY_SETTLED", "SETTLED" |
| `amount` | string (Decimal) | `Bill.amount` column | No | Serialized as string for precision, e.g. `"8500.00"` |
| `balance` | string (Decimal) | `Bill.balance` column | No | Serialized as string for precision |
| `bill_date` | string (ISO date) | `Bill.bill_date` column | Yes | e.g. `"2023-10-15"` or `null` |
| `due_date` | string (ISO date) | `Bill.due_date` column | Yes | e.g. `"2023-11-10"` or `null` |
| `client_name` | string | LEFT JOIN `t_client` on `client_id` → `Client.name_cn` | Yes | `null` if no matching client |

### Implementation
- **Backend**: Add 6 fields to the item dict in `billing/api.py:get_bills()`. Add LEFT JOIN or secondary query to resolve `client_name` from `t_client`.
- **Frontend**: `BackendBill` interface already has `status`, `amount`, `balance`, `due_date`. Add `bill_date?: string | null`. Update `mapBillListItem()` to map `bill_date` → `issue_date`.

---

## BE-02: Enrich `GET /api/v1/payments` List Response

### Current Response Item
```json
{
  "id": "uuid",
  "pay_no": "PAY-2023-055",
  "client_id": "uuid",
  "pay_date": "2023-11-12"
}
```

### Enhanced Response Item
```json
{
  "id": "uuid",
  "pay_no": "PAY-2023-055",
  "client_id": "uuid",
  "pay_date": "2023-11-12",
  "currency": "CNY",
  "amount": "50000.00"
}
```

### Field Details

| Field | Type | Source | Nullable | Notes |
|-------|------|--------|----------|-------|
| `currency` | string | `Payment.currency` column | No | e.g. `"CNY"` |
| `amount` | string (Decimal) | `Payment.amount` column | No | Serialized as string for precision |

### Implementation
- **Backend**: Add 2 fields to the item dict in `billing/api.py:get_payments()`. No JOINs needed — both fields are on the `Payment` model.
- **Frontend**: No changes needed. `BackendPayment` already has `currency` and `amount`, and `mapPayment()` already handles them via `asNumber()`.

---

## BE-03: Enrich `GET /api/v1/tasks` List Response

### Current Response Item (TaskListItemOut)
```json
{
  "id": "uuid",
  "case_id": "uuid",
  "document_id": null,
  "task_template_id": null,
  "title": "答复第一次审查意见 (OA1)",
  "due_date": "2023-11-15",
  "internal_due_date": null,
  "worker_id": null,
  "supervisor_id": null,
  "status": "OPEN"
}
```

### Enhanced Response Item
```json
{
  "id": "uuid",
  "case_id": "uuid",
  "case_no": "P2310-008",
  "document_id": null,
  "task_template_id": null,
  "title": "答复第一次审查意见 (OA1)",
  "due_date": "2023-11-15",
  "internal_due_date": null,
  "worker_id": null,
  "supervisor_id": null,
  "remark": null,
  "status": "OPEN",
  "created_at": "2023-10-01T00:00:00",
  "updated_at": "2023-10-01T00:00:00"
}
```

### Field Details

| Field | Type | Source | Nullable | Notes |
|-------|------|--------|----------|-------|
| `case_no` | string | LEFT JOIN `t_case` on `case_id` → `Case.case_no` | Yes | `null` if no matching case. **P0 requirement.** |
| `remark` | string | `Task.remark` column (via `AuditMixin`) | Yes | Nice-to-have for frontend; already expected by `BackendTask` |
| `created_at` | string (ISO datetime) | `Task.created_at` column | No | Nice-to-have; already expected by `BackendTask` |
| `updated_at` | string (ISO datetime) | `Task.updated_at` column | No | Nice-to-have; already expected by `BackendTask` |

### Implementation
- **Backend**: Modify `tasks/api.py:get_tasks()` to perform LEFT JOIN on `t_case` to fetch `case_no`. Add `case_no` field to `TaskListItemOut` schema (or switch to dict-based response). Also include `remark`, `created_at`, `updated_at`.
- **Frontend**: Add `case_no?: string | null` to `BackendTask` interface. Update `mapTask()` to pass through `case_no: input.case_no || undefined`.

---

## BE-04: Enrich `GET /api/v1/cases` List Response

### Current Response Item
```json
{
  "id": "uuid",
  "case_no": "P2310-008",
  "case_type": "NORMAL",
  "patent_category": "INV"
}
```

### Enhanced Response Item
```json
{
  "id": "uuid",
  "case_no": "P2310-008",
  "case_type": "NORMAL",
  "patent_category": "INV",
  "client_id": "uuid",
  "client_name": "蔚来汽车",
  "title_cn": "一种激光雷达避障系统",
  "status": "ACTIVE"
}
```

### Field Details

| Field | Type | Source | Nullable | Notes |
|-------|------|--------|----------|-------|
| `client_id` | string | `Case.client_id` column | Yes | Already on model, just not returned in list |
| `title_cn` | string | `Case.title_cn` column | Yes | Already on model |
| `status` | string | `Case.status` column | No | e.g. "NOT_FILED", "ACTIVE", etc. |
| `client_name` | string | LEFT JOIN `t_client` on `client_id` → `Client.name_cn` | Yes | `null` if no matching client or `client_id` is null |

### Implementation
- **Backend**: Add 4 fields to the item dict in `cases/api.py:get_cases()`. Add LEFT JOIN or secondary query to resolve `client_name` from `t_client`.
- **Frontend**: `Case` interface already has `client_name?: string`, `client_id`, `status`. Map `title_cn` → `title` in frontend if needed (currently `getCases()` returns `response.data` directly).

---

## Key Constraints

1. **Additive only** — no existing fields removed or renamed
2. **Decimal/money fields** serialized as **strings** for precision (e.g. `"8500.00"`)
3. **Nullable fields** (`client_name`, `case_no`, `due_date`, `bill_date`) return `null` when not available
4. **SQLite compatible** — LEFT JOINs use standard SQL; no PG-only functions
5. **No new endpoints** — only enriching existing list responses
6. **Pagination wrapper unchanged** — `{items, page, page_size, total}`
