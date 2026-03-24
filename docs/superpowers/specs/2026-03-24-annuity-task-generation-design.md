# FR-FE-06: Annuity Task Generation + Model Extension — Design Spec

**Date**: 2026-03-24
**Priority**: P0 #3 (from FPMS_SPEC2_2nd_Review.md)
**SPEC Reference**: SPEC 2.0 §5.8 FR-FE-06, §13.3-13.8 Scene D
**Status**: Approved

---

## 1. Overview

The annuity module already implements: task list with filters, client instruction update, fee draft generation, PayList/GovPayment CRUD, Excel export. **This spec addresses 3 remaining gaps:**

1. **AnnuityTask multi-year generation API** — create annuity tasks for GRANTED cases
2. **6 missing model fields** — gov_fee_amt, service_fee_amt, notify_count, pay_next_year, draft_generated, notice_sent
3. **Computed is_overdue** — virtual field returned in list response

### Decisions

| Decision | Choice |
|----------|--------|
| Generation trigger | Manual endpoint only (auto-trigger on GRANTED deferred to P1) |
| Amount initialization | Pre-calculate from FeeRate at generation time |
| is_overdue | Computed at query time (not stored) |
| Notice generation | OUT OF SCOPE (document generation) |

### Out of Scope

- Auto-trigger on case status change to GRANTED (deferred to P1)
- Notice letter generation (document generation — excluded per project constraint)
- New frontend pages — only updating existing `AnnuityTaskList.vue` + adding small dialog

---

## 2. Data Model Changes

### New Migration: `pe_fr_fe_06_annuity_task_ext`

**Revision ID**: `pe_fr_fe_06_01`. Depends on `pe_fr_fe_07_01` (latest head). Adds 6 columns to `t_annuity_task` using `batch_alter_table` (SQLite compat). Forward-only. Idempotent column existence check.

| Column | Type | Nullable | Default | Purpose |
|--------|------|----------|---------|---------|
| `gov_fee_amt` | Numeric(18,2) | Yes | `0` | Estimated government fee |
| `service_fee_amt` | Numeric(18,2) | Yes | `0` | Estimated service fee |
| `notify_count` | Integer | Yes | `0` | Number of notices sent |
| `pay_next_year` | Boolean | Yes | `0` | Include next year in same draft |
| `draft_generated` | Boolean | Yes | `0` | Fee draft has been generated |
| `notice_sent` | Boolean | Yes | `0` | Notice has been sent |

### Model Update (`annuity/models.py`)

Add 6 new `mapped_column` fields to existing `AnnuityTask` class:

```python
gov_fee_amt: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True, server_default=text("0"))
service_fee_amt: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True, server_default=text("0"))
notify_count: Mapped[int | None] = mapped_column(Integer, nullable=True, server_default=text("0"))
pay_next_year: Mapped[bool | None] = mapped_column(Boolean, nullable=True, server_default=text("0"))
draft_generated: Mapped[bool | None] = mapped_column(Boolean, nullable=True, server_default=text("0"))
notice_sent: Mapped[bool | None] = mapped_column(Boolean, nullable=True, server_default=text("0"))
```

### `is_overdue` — NOT stored

Computed at query time: `due_date < date.today() and status == 'OPEN'`. Returned as virtual field in list response.

---

## 3. API Contract

### New Endpoint

| Method | Path | Permission | Response | Description |
|--------|------|-----------|----------|-------------|
| `POST` | `/api/v1/annuity/tasks/generate` | `AnnuityTask.Action` | 201 + AnnuityTaskGenerateResult | Generate multi-year tasks for GRANTED case |

### New Schemas

**AnnuityTaskGenerateIn**:
```python
class AnnuityTaskGenerateIn(BaseModel):
    case_id: str = Field(..., min_length=1)
```

**AnnuityTaskGenerateResult**:
```python
class AnnuityTaskGenerateResult(BaseModel):
    case_id: str
    case_no: str | None = None
    first_year: int
    last_year: int
    tasks_created: int
    tasks_skipped: int
```

### Validation Rules

- **V-AG-01**: Case must exist → 404 "案卷不存在"
- **V-AG-02**: Case status must be GRANTED → 400 "案卷状态不是已授权"
- **V-AG-03**: Case must have `first_annuity_year` set → 400 "未设置首年年费年度"
- **V-AG-04**: Idempotent — skip years that already have an AnnuityTask (count as `tasks_skipped`)

### Existing Endpoint Changes

**`GET /api/v1/annuity/tasks`** — update response items to include:
- `gov_fee_amt: Decimal | None`
- `service_fee_amt: Decimal | None`
- `notify_count: int | None`
- `pay_next_year: bool | None`
- `draft_generated: bool | None`
- `notice_sent: bool | None`
- `is_overdue: bool` (computed)

---

## 4. Service Layer

### `generate_annuity_tasks_for_case(db: Session, payload: AnnuityTaskGenerateIn) → dict`

1. Validate case exists (404 if not)
2. Validate case.status == 'GRANTED' (400 if not)
3. Validate case.first_annuity_year is set (400 if not)
4. Calculate `last_year`: use `valid_until.year` if set, else `filing_date.year + 20` (standard CN patent term)
5. For each year_no from `first_annuity_year` to `last_year`:
   - Skip if AnnuityTask already exists for this case_id + year_no
   - Calculate `due_date`: `filing_date + year_no years` (CN rule: annuity due on filing anniversary)
   - Look up `T_FeeRate(rate_group='ANNUITY', year_no=year_no)` for gov_fee_amt and service_fee_amt — default to 0 if not found
   - Create `AnnuityTask` record
6. Return `{case_id, case_no, first_year, last_year, tasks_created, tasks_skipped}`

### Update `list_annuity_tasks` response

Add 6 new fields + computed `is_overdue` to each returned item:
```python
"is_overdue": task.due_date < date.today() and task.status == "OPEN"
```

### Update `generate_fee_drafts_from_annuity_tasks`

After successfully generating a draft for a task, set `task.draft_generated = True`.

---

## 5. Frontend

### 5a. Update `AnnuityTaskList.vue`

- Add table columns: 官费预估, 服务费预估, 通知次数, 是否逾期
- `is_overdue`: el-tag type=danger "逾期" / type=info "正常"
- `draft_generated`, `notice_sent`: el-tag 是/否
- Add "生成年费任务" button in toolbar → opens `AnnuityGenerateDialog`

### 5b. New `AnnuityGenerateDialog.vue`

- Title: "生成年费任务"
- Single field: 案卷 (el-select remote search by case_no)
- Confirm → POST /annuity/tasks/generate
- Success: ElMessage.success(`已生成 ${tasks_created} 条年费任务，跳过 ${tasks_skipped} 条已存在记录`)
- Errors (Chinese): "案卷不存在", "案卷状态不是已授权", "未设置首年年费年度"
- After success, reload task list

### 5c. Update TypeScript types (`annuity.types.ts`)

Add:
- `AnnuityTaskGeneratePayload { case_id: string }`
- `AnnuityTaskGenerateResult { case_id, case_no, first_year, last_year, tasks_created, tasks_skipped }`
- Update `AnnuityTask` interface with 6 new fields + `is_overdue`

### 5d. Update API client (`annuity.ts`)

Add: `generateAnnuityTasks(payload): Promise<AnnuityTaskGenerateResult>`

### 5e. Frontend Error Messages (简体中文)

| Scenario | Message |
|----------|---------|
| Case not found | `案卷不存在` |
| Not GRANTED | `案卷状态不是已授权` |
| No first_annuity_year | `未设置首年年费年度` |
| Success | `已生成 N 条年费任务，跳过 M 条已存在记录` |
| Failure | `生成失败，请重试` |
| Load failure | `加载数据失败` |

---

## 6. Testing & Acceptance Criteria

### Backend Tests (`tests/test_annuity_generate.py`)

| Test | Description |
|------|-------------|
| `test_generate_annuity_tasks_success` | POST GRANTED case → 201, tasks_created > 0 |
| `test_generate_case_not_found` | POST non-existent → 404 |
| `test_generate_case_not_granted` | POST NOT_FILED case → 400 |
| `test_generate_no_first_annuity_year` | POST GRANTED without year → 400 |
| `test_generate_idempotent` | POST twice → second tasks_created=0, tasks_skipped=N |
| `test_generate_prefills_fee_amounts` | Create ANNUITY rates → gov_fee_amt/service_fee_amt populated |
| `test_list_includes_new_fields` | GET list → response has new fields |
| `test_list_is_overdue_computed` | Past due_date + OPEN → is_overdue=true |
| `test_list_is_overdue_false_when_done` | Past due_date + DONE → is_overdue=false |
| `test_draft_generated_flag_set` | Generate drafts → draft_generated=true |
| `test_permissions_generate` | POST without auth → 401 |

### Migration Test

`rm -f fpms_dev.db && alembic upgrade head && python scripts/seed_dev.py` → success

### Frontend Quality Gates

- `npm run lint` → PASS
- `npm run typecheck` → PASS
- `npm run build` → PASS

### Acceptance Checklist

- [ ] Migration adds 6 columns, clean rebuild passes
- [ ] POST /annuity/tasks/generate creates tasks for GRANTED case
- [ ] Idempotent — re-running skips existing years
- [ ] Fee amounts pre-calculated from FeeRate
- [ ] GET /annuity/tasks returns new fields + computed is_overdue
- [ ] draft_generated flag updated after draft generation
- [ ] V-AG-01..04 enforced
- [ ] Permission AnnuityTask.Action enforced
- [ ] Frontend list shows new columns (Chinese)
- [ ] Frontend generate dialog works
- [ ] All 11 backend tests pass
- [ ] Frontend lint + typecheck + build pass

---

## Appendix: File Impact Summary

| File | Change |
|------|--------|
| `backend/alembic/versions/pe_fr_fe_06_annuity_task_ext.py` | NEW — migration |
| `backend/app/modules/annuity/models.py` | EDIT — add 6 columns |
| `backend/app/modules/annuity/api.py` | EDIT — add generate endpoint, update list response |
| `backend/app/modules/annuity/service.py` | EDIT — add generate_annuity_tasks_for_case, update list response, update draft_generated flag |
| `backend/tests/test_annuity_generate.py` | NEW — 11 tests |
| `frontend/src/api/annuity.types.ts` | EDIT — add types, update AnnuityTask interface |
| `frontend/src/api/annuity.ts` | EDIT — add generateAnnuityTasks function |
| `frontend/src/modules/annuity/components/AnnuityGenerateDialog.vue` | NEW — dialog |
| `frontend/src/modules/annuity/pages/AnnuityTaskList.vue` | EDIT — add columns + generate button |

---

**Document Version**: 1.0
**Author**: Claude Code (brainstorming session)
**Approved by**: User (2026-03-24)
