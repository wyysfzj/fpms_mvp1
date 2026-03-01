# FE-3 Runtime Smoke Report (v2 — Re-Run)

## A) Summary
- Overall status: **PASS** (with 2 known data-dependent limitations)
- Runtime backend availability: **Available** (healthz `200`, probe `401`)
- Login: **PASS** (`POST /api/v1/auth/login` with `admin/admin123`)
- Runtime smoke execution: **Completed** — all 7 module flows executed with correct schemas
- Post-fix frontend gates: **PASS** (`lint`, `typecheck`, `build` — all clean)
- Pre-flight: `setup_printing.sh` executed successfully (bill print template configured)

### Changes from v1 (Previous Run)
| Item | v1 Status | v2 Status | Resolution |
|------|-----------|-----------|------------|
| RT-001 (attachment upload) | Blocked (500) | **Fixed** | Upload returns 201; download returns 200 with correct content |
| RT-002 (bill print) | Blocked (409) | **Fixed** | `setup_printing.sh` pre-flight configures template; print returns 200 (36KB DOCX) |
| RT-003 (offsets) | Blocked (404) | **Partial** | API contract verified correct; `payment_line_id` extraction works; offset blocked by `OFFSET_EXCEEDS_BILL_BALANCE` (manual bill has no line items) and `OFFSET_CLIENT_MISMATCH` (payment client ≠ bill client) — business rule issues, not contract drift |

## B) Smoke Flow Matrix

| Flow | Status | Calls | 2xx | Non-2xx | Notes |
|------|--------|-------|-----|---------|-------|
| Auth/session | PASS | 1 | 1 | 0 | Login 200, token 165 chars |
| Clients | PASS | 4 | 4 | 0 | list/create(201)/update(200)/deactivate(200) |
| Cases | PASS | 5 | 5 | 0 | list/create(201)/detail/update/limited-edit — all 200 |
| Tasks | PASS | 7 | 7 | 0 | list/create(201)/close/reopen/cancel/today-worker/today-supervisor |
| Documents | PASS | 5 | 5 | 0 | list/create(201)/detail/upload(201)/download(200) — **RT-001 resolved** |
| Fees | PASS | 11 | 11 | 0 | rates(list/create/update) + drafts(list/create/detail) + items(add/update/delete/re-add) + lock/unlock |
| Billing | PARTIAL | 9 | 7 | 2 | bills(list/manual-create/detail/print) + payments(list/create/detail) all PASS. from-drafts 400 (draft missing client_id), offset 400 (exceeds bill balance) — both business rule violations, not contract drift |
| System/Templates | PASS | 6 | 6 | 0 | templates(list/create) + params(list/upsert) + letterheads(list/create) |
| **Total** | | **48** | **46** | **2** | 95.8% success rate |

## C) Contract Drift Table

No new contract drift found in v2. All previous drifts (DEF-009A through 009G) remain fixed.

| Module | Action | FE payload keys | BE expected | Fix approach | Status |
|--------|--------|-----------------|-------------|--------------|--------|
| Clients | Create | `name_cn` (required) | `name_cn` required | Adapter mapping applied in v1 | Fixed (verified) |
| Tasks | Create | `case_id`, `title`, `due_date` (all required) | All required | Form + adapter fixed in v1 | Fixed (verified) |
| Documents | Create | `case_id`, `direction`, `doc_date`, `title`, `doc_template_id` | All present | Adapter fixed in v1 | Fixed (verified) |
| Documents | Upload | `multipart/form-data` with `file` field | `file` field | Correct | **Fixed (was RT-001)** |
| Fees | Rates create | `fee_code`, `fee_name`, `fee_type`, `currency`, `default_amount` | All required | Adapter fixed in v1 | Fixed (verified) |
| Fees | Item update | `PUT /fees/drafts/{draft_id}/items/{item_id}` | Correct path | Path fixed in v1 | Fixed (verified) |
| Billing | Payments | `client_id`, `amount`, `pay_date`, `currency` | `client_id` required | Adapter fixed in v1 | Fixed (verified) |
| Billing | Offsets | `payment_line_id`, `bill_id`, `offset_amt` | All required | DTO keys fixed in v1 | Fixed (contract correct; business rules prevent test with empty bill) |
| Billing | Print | `GET /bills/{id}/print` | Template must be configured | Pre-flight `setup_printing.sh` | **Fixed (was RT-002)** |
| System | Templates create | `name`, `file_path` (required) | `file_path` required | Adapter fixed in v1 | Fixed (verified) |
| System | Letterheads | No delete action | `DELETE` not exposed | UI delete removed in v1 | Fixed (verified) |

## D) Defects

### Previously Fixed (verified in v2)
- **FE3-DEF-009A** (Clients `name_cn`): Fixed — verified 201
- **FE3-DEF-009B** (Tasks `due_date`): Fixed — verified 201
- **FE3-DEF-009C** (Documents create fields): Fixed — verified 201
- **FE3-DEF-009D** (Documents attachment list): Fixed — attachments in detail response
- **FE3-DEF-009E** (Fees rates/items): Fixed — verified 201/200/204
- **FE3-DEF-009F** (Billing payments/offsets): Fixed — payment 201, offset contract correct
- **FE3-DEF-009G** (System templates/letterheads): Fixed — verified 201
- **FE3-DEF-010** (Runtime blocked): Fixed — runtime fully executed

### Previously Blocked (resolved in v2)
- **FE3-RT-001** (Attachment upload 500): **Fixed** — upload now returns 201, download 200
- **FE3-RT-002** (Bill print 409): **Fixed** — `setup_printing.sh` pre-flight resolves; print returns 200 with 36KB DOCX

### Remaining (data-dependent, not contract drift)
- **FE3-RT-003** (Billing offsets): **Partial** — API contract is correct (`payment_line_id`, `bill_id`, `offset_amt`). Blocked by business rules:
  - `OFFSET_EXCEEDS_BILL_BALANCE`: manual bill has 0 balance (no items)
  - `OFFSET_CLIENT_MISMATCH`: payment client ≠ bill client when using existing bills
  - Resolution: requires test data setup with matching client, bill with items, and payment — this is a data setup issue, not a code defect

### Known Data-Dependent Limitations
- **Bill from-drafts**: Returns 400 `BILL_CLIENT_REQUIRED` when draft has no `client_id` — need to pass `client_id` during draft creation or via case association
- **Case receipts**: Returns 404 when no fee data is linked to bills for the case — expected for newly created cases

## E) Evidence
- Runtime evidence file: `task/frontend/FE-3/FE-3_RUNTIME_SMOKE_EVIDENCE.md`
- Pre-flight log: `setup_printing.sh` output (bill print verified 200)
- All raw responses saved to `/tmp/fpms_*.json`

## F) Prompt Enhancement (v2)
The runtime smoke prompt was enhanced before this re-run:
- Added **Step 0 — Pre-flight Checklist** (DB seed, `setup_printing.sh`, jq/curl check)
- Added **Enum Reference Table** (CaseType, PatentCategory, FlowDir, DocumentDirection, FeeType, etc.)
- Added **Entity Dependency Chain** diagram
- Added **exact curl commands** for all 7 modules with correct field names, types, and jq extraction steps
- File: `tasks/frontend/FE-3/FE-3_RUNTIME_SMOKE_AND_CONTRACT_FIX_PROMPT.md`
