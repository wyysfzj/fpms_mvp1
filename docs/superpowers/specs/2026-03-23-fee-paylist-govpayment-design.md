# FR-FE-04 Design Spec: 官费清单与缴费

Date: 2026-03-23
Scope item: P0 #1 官费清单与缴费 (FR-FE-04)
Source review: `docs/FPMS_SPEC2_2nd_Review.md`
Primary spec reference: `docs/FPMS SPEC 2.0.md`
Process: Brainstorming approved by user section-by-section

## 1. Goal

Define the Fee Management story for official payment lists and government payment registration as a planning container only. This document does not authorize story-level implementation closure. It exists to define atomic slices that may be planned and executed under repository `AGENTS.md` constraints.

Implementation must be decomposed into AGENTS-compliant atomic tasks:

- one task file path
- one closure slice
- one explicit non-closure statement
- one allowlist
- one verification set

## 2. Authoritative Constraints

This design is governed by:

- repository `AGENTS.md`
- Superpowers workflow
- `docs/FPMS SPEC 2.0.md`
- current Phase 3 constraints

Phase constraints that materially affect this design:

- no database schema changes
- no Alembic migration edits
- use existing ORM models only
- implement endpoints only in module-level `api.py`
- preserve existing response envelope conventions
- keep SQLite compatibility

## 3. Story Boundary

### 3.1 In Scope

The story-level product intent spans the following user-visible workflow:

1. Generate a pay list from GOV fee items in fee drafts.
2. Create a historical pay list manually.
3. Register government payments under a pay list.
4. Support historical/manual government payment entry.
5. Query pay lists and inspect pay-list details.
6. Export a pay list for official-client use.
7. Track pay-list status through the workflow.
8. Expose the feature under Fee Management product semantics, even if implementation temporarily reuses annuity routes/pages.

### 3.2 Out of Scope

This story does not close:

- `FR-FE-07` case receipt registration
- `FR-FE-09` dual-table fee status overview
- XML/text multi-format exports
- schema completion for missing `SPEC` fields
- audit-log subsystem for privileged edits of already-paid records
- unrelated fee, annuity, billing, or reporting work

## 4. Product Intent

The target product entry is:

- Fee Management -> 官费清单

Implementation may temporarily reuse existing annuity-based code paths such as:

- `/annuity/pay-lists`
- `/annuity/gov-payments/new`

But the design target is a generic official-payment-list capability under Fee Management rather than an annuity-only feature.

## 5. User-Approved Functional Decisions

The following decisions were explicitly approved during brainstorming:

- story boundary includes:
  - draft-sourced flow
  - query/detail
  - export
  - historical paid-data backfill
  - manual non-draft entry
- historical/manual flow rule:
  - support both
    - normal pay-list then payment entry
    - historical pay-list with manual rows
  - do not support standalone `GovPayment` outside a pay list
- acceptance baseline:
  - primary acceptance aligns to `SPEC`
  - implementation plan must also define a Phase 3-compatible subset
- IA decision:
  - final menu semantics under Fee Management
  - implementation may temporarily reuse annuity pages/routes
- export decision:
  - official-client export required
  - format for this round: Excel template
- pay-list state machine:
  - `DRAFT -> EXPORTED -> PAID`
  - `CANCELLED` allowed
- manual-row rule:
  - prefer binding `fee_item_id`
  - allow manual rows with no `fee_item_id` when no draft source exists
- query baseline:
  - business-level query target includes list no, client, status, planned-pay-date range, type, currency, historical/manual marker, case/app no, fee code, invoice/voucher references

## 6. Spec-Target Model

Per `docs/FPMS SPEC 2.0.md`, the ideal target includes:

### 6.1 `T_PayList`

- `ListNo`
- `Type`
- `FlowDir`
- `PlannedPayDate`
- `ActualPayDate`
- `Currency`
- `TotalAmt`
- `InvoiceNoFrom`
- `InvoiceNoTo`
- `Status`

### 6.2 `T_GovPayment`

- `PayListID`
- `CaseID`
- `ItemID` (nullable)
- `FeeCode`
- `YearNo`
- `PlannedAmt`
- `PlannedCurrency`
- `PaidAmt`
- `PaidCurrency`
- `VoucherNo`
- `InvoiceNo`
- `PlannedPayDate`
- `PaidDate`
- `Remark`

### 6.3 Spec-State Semantics

Primary acceptance status semantics:

- `DRAFT`
- `EXPORTED`
- `PAID`
- `CANCELLED`

## 7. Current Model Reality

Current model support in [`backend/app/modules/annuity/models.py`](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/annuity/models.py):

### 7.1 Current `PayList` fields

- `id`
- `client_id`
- `pay_list_no`
- `status`
- `currency`
- `planned_pay_date`
- `paid_date`
- `total_amount`
- `remark`
- audit fields

### 7.2 Current `GovPayment` fields

- `id`
- `pay_list_id`
- `case_id`
- `fee_item_id` (nullable)
- `status`
- `currency`
- `paid_date`
- `paid_amount`
- `official_receipt_no`
- `remark`
- audit fields

### 7.3 Existing partial implementation already present

Current codebase already contains partial capability in:

- [`backend/app/modules/annuity/api.py`](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/annuity/api.py)
- [`backend/app/modules/annuity/service.py`](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/annuity/service.py)
- [`frontend/src/api/govPayments.ts`](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/govPayments.ts)
- [`frontend/src/modules/annuity/pages/PayList.vue`](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/annuity/pages/PayList.vue)
- [`frontend/src/modules/annuity/pages/GovPaymentCreate.vue`](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/annuity/pages/GovPaymentCreate.vue)

These must be treated as incomplete remnants, not as proof of story closure.

## 8. Phase 3-Compatible Scope

This round must ship a compatible subset without schema changes.

### 8.1 Compatible `PayList` behavior

Supported:

- auto-generated or user-created list number
- client-bound pay list
- currency
- planned pay date
- actual paid date using current `paid_date`
- total amount
- status transitions using existing string field
- remarks

Not structurally supported in this round:

- `Type`
- `FlowDir`
- `InvoiceNoFrom/To`

### 8.2 Compatible `GovPayment` behavior

Supported:

- row linked to pay list
- linked case
- optional fee item
- paid amount
- paid date
- current currency field
- remark
- current `official_receipt_no`

Not structurally supported in this round:

- `FeeCode`
- `YearNo`
- `PlannedAmt/PlannedCurrency`
- `PaidCurrency`
- `VoucherNo`
- `InvoiceNo`

### 8.3 Compatibility Rule

The implementation must not claim the unsupported fields are complete. Missing fields must be tracked as blocked follow-up work rather than hidden inside `remark` and declared done.

## 9. Executable Slice Matrix

This section is authoritative for `writing-plans`. Each row must become either:

- one executable atomic task, or
- one explicit blocked follow-up task

No executor may treat this entire story as one closure slice.

| Slice ID | Capability | Primary file ownership | This round | Exact closure slice | Explicit non-closure statement |
| --- | --- | --- | --- | --- | --- |
| SL-01 | Generate pay list from GOV fee items | backend annuity module | Executable | Accept selected GOV `FeeItem` rows and create one `PayList` plus planned `GovPayment` rows under same-client same-currency rules. | Does not add pay-list query, detail, export, historical creation, manual-item endpoint, or schema fields. |
| SL-02 | Create historical pay-list header | backend annuity module | Executable | Create one empty historical `PayList` header using current model fields only. | Does not add manual rows, export, detail, query, or missing `SPEC` fields such as `Type` or `InvoiceNoFrom/To`. |
| SL-03 | Query pay-list headers | backend annuity module | Executable | Return paginated pay-list list with Phase 3-supported filters only. | Does not provide detail rows, export, or blocked filters relying on missing structured fields. |
| SL-04 | Read pay-list detail | backend annuity module | Executable | Return one pay-list header plus associated `GovPayment` rows. | Does not mutate status, export files, or add blocked `SPEC` fields. |
| SL-05 | Export pay list to Excel | backend annuity module | Executable | Generate one real Excel export for one pay list and advance `DRAFT -> EXPORTED` when valid. | Does not implement XML/text export, remote client integration, or schema fields for full official invoice range support. |
| SL-06 | Mark pay list paid | backend annuity module | Executable | Record compatible header paid date and advance `EXPORTED -> PAID` when row-level paid conditions are satisfied. | Does not backfill blocked `SPEC` fields or permit bypassing the required prior export state. |
| SL-07 | Register gov-payment row from planned/generated item | backend annuity module | Executable | Create or complete one `GovPayment` row under an existing `PayList`, with duplicate protection and positive amount validation. | Does not create standalone `GovPayment`, audit-log redesign, or blocked fields like `VoucherNo` and `InvoiceNo`. |
| SL-08 | Add manual/historical gov-payment row under pay list | backend annuity module | Executable | Add one manual `GovPayment` row under an existing historical `PayList`, allowing nullable `fee_item_id`. | Does not create a separate convenience endpoint unless that endpoint is planned as its own atomic task. |
| SL-09 | Fee Management list page | frontend fee/annuity UI | Executable | Present the pay-list list/query/export/create-history entry under Fee Management semantics with Simplified Chinese UI. | Does not close detail registration page, full router refactor, or blocked filters lacking backend structure. |
| SL-10 | Pay-list detail and registration page | frontend fee/annuity UI | Executable | Present one pay-list detail view with row registration actions and status display in Simplified Chinese UI. | Does not close list page IA migration, dual-table fee overview, or blocked structured fields. |
| SL-11 | Historical/manual row entry UI | frontend fee/annuity UI | Executable | Present a UI for adding manual gov-payment rows under an existing historical pay list. | Does not create standalone receipts or expand into `FR-FE-07`. |
| SL-12 | Cancel pay list | backend/frontend pay-list workflow | Deferred | None in this round by default. | Cancellation is not part of the default execution batch unless a dedicated atomic task is explicitly planned. |
| SL-13 | Structured `SPEC` fields missing from current models | models/migrations | Blocked | None in this round. | Requires schema and migration work prohibited by Phase 3. |
| SL-14 | Query by `Type`, history marker, fee code, invoice/voucher refs | backend/frontend query stack | Blocked | None in this round. | Depends on structured fields missing from current models. |
| SL-15 | Multi-format official export | export stack | Blocked | None in this round. | Excel only this round; XML/text remain follow-up. |
| SL-16 | Privileged edit audit log for paid rows | audit/logging | Blocked | None in this round. | Requires separate audit design beyond this story. |

## 10. Page Design

### 9.1 Main List Page

Target semantic page:

- Fee Management -> 官费清单

Required capabilities:

- list/query pay lists
- filter by:
  - list no
  - client
  - status
  - planned pay date range
  - currency
- navigate to detail
- create historical pay list
- trigger export

Phase 3 note:

- `Type`
- historical/manual explicit marker
- invoice/voucher-based filtering
- fee-code filtering

may need to be marked unsupported or follow-up where no backing field exists.

### 9.2 Pay List Detail / Registration Page

Required capabilities:

- show pay-list header
- show detail rows
- register official payment for rows
- mark pay list exported
- mark pay list paid
- expose status trace in current-state form
- trigger export

### 9.3 Manual Historical Entry

Required capabilities:

- create a historical pay-list header
- add manual rows under that pay list
- allow:
  - with `fee_item_id`
  - without `fee_item_id`

Minimum manual-row payload when no fee item exists:

- `case_id`
- `paid_amount`
- `paid_date`
- `remark`

## 11. API Design Slices

These are candidate endpoint slices. `writing-plans` must map each one to an atomic task or a blocked follow-up, using Section 9 as the source of truth.

### 10.1 Pay-list generation from fee items

- `POST /pay-lists/from-fee-items`

Purpose:

- create one pay list from selected GOV fee items

Rules:

- only GOV fee items
- same client
- same currency
- duplicate protection against already-paid or already-associated items as defined by implementation

### 10.2 Historical pay-list creation

- `POST /pay-lists`

Purpose:

- create a pay-list header without fee-draft generation

This endpoint is executable this round.

### 10.3 Pay-list query

- `GET /pay-lists`

Purpose:

- query pay-list headers for operational follow-up

This endpoint is executable this round for supported filters only.

### 10.4 Pay-list detail

- `GET /pay-lists/{id}`

Purpose:

- return pay-list header plus related `GovPayment` rows

This endpoint is executable this round.

### 10.5 Pay-list export

- `POST /pay-lists/{id}/export`

Purpose:

- generate Excel export suitable for official-client processing
- move status to `EXPORTED` only from `DRAFT`

This endpoint is executable this round.

### 10.6 Pay-list paid transition

- `POST /pay-lists/{id}/mark-paid`

Purpose:

- record actual pay date on the header
- move status to `PAID` only from `EXPORTED` once row-level paid conditions are satisfied by the compatible model

This endpoint is executable this round.

### 10.7 Gov-payment registration

- `POST /gov-payments`

Purpose:

- create or register one row under a pay list
- support both normal rows and historical/manual rows

This endpoint is executable this round only if planning keeps generated-row registration and manual-row creation as separate closure slices.

### 10.8 Gov-payment update

- `PUT /gov-payments/{id}`

Purpose:

- adjust a row before completion, subject to business rules

This endpoint is deferred unless required by a specific executable slice. It must not be silently absorbed into another endpoint task.

### 10.9 Manual-item convenience endpoint

Deferred design slice, not executable by default in this round:

- `POST /pay-lists/{id}/manual-items`

Purpose:

- add manual rows under a historical pay list

This endpoint is follow-up only unless `writing-plans` explicitly creates a separate atomic task for it. It must not be merged into another first-pass backend task by convenience.

## 12. Status Rules

Main acceptance status flow:

- `DRAFT -> EXPORTED -> PAID`
- `CANCELLED`

Compatible implementation note:

- current code contains `PARTIAL`
- this may remain as an internal compatibility state
- it must not become the primary accepted workflow state for this story

Finite transition table for planning:

| From | To | Allowed this round | Rule |
| --- | --- | --- | --- |
| `DRAFT` | `EXPORTED` | Yes | Requires successful Excel export artifact generation. |
| `DRAFT` | `PAID` | No | Header cannot skip export state in this round. |
| `DRAFT` | `CANCELLED` | Deferred | Only allowed if dedicated slice `SL-12` is explicitly planned. |
| `EXPORTED` | `PAID` | Yes | Requires compatible row-level paid registration and header paid date. |
| `EXPORTED` | `DRAFT` | No | Rewind is not in scope this round. |
| `EXPORTED` | `CANCELLED` | Deferred | Only allowed if dedicated slice `SL-12` is explicitly planned. |
| `PAID` | any other state | No | Paid lists are terminal in this round. |
| `CANCELLED` | any other state | No | Cancelled lists are terminal in this round. |

Row-level compatibility note:

- current code may continue to use `PARTIAL` internally
- planners and reviewers must treat `PARTIAL` as non-primary compatibility state only
- no task may claim that `PARTIAL` extends the approved primary status machine

## 13. Validation Rules

### 12.1 Rules aligned to current implementation and spec intent

- only GOV fee items can generate a pay list
- selected generated rows must belong to same client
- selected generated rows must use same currency
- pay amount must be positive when explicitly provided
- duplicate payment registration must be blocked
- paid rows cannot be silently re-registered

### 12.2 Spec-target rules to preserve in design

- `Status != PAID` should not carry paid-only header fields in the ideal model
- `Status = PAID` should require actual pay date and at least one payment row
- row-level paid amount should default from planned amount where supported
- row-level date mismatch around actual pay date should be warned or validated in future enhancements

## 14. Query Design

### 13.1 Approved query target

Business target query dimensions:

- list number
- client
- status
- planned pay date range
- type
- currency
- historical/manual marker
- case no / application no
- fee code
- invoice / voucher references

### 13.2 This-round query commitment

Guaranteed for Phase 3-compatible delivery:

- list number
- client
- status
- planned pay date range
- currency
- case/application via join where feasible

Blocked or follow-up due to missing structure:

- type
- historical/manual explicit marker
- fee code
- invoice/voucher references

## 15. Export Design

This round export decision:

- official-client export is required
- format is standardized Excel template

Not in this round:

- XML export
- text-format export
- direct remote official-client integration

Acceptance target:

- exported file is real output, not a placeholder action
- export action is available from pay-list workflow
- export status transition is explicit and testable

## 16. Non-Closure Boundaries

This story must not silently absorb:

- case receipt workflow
- fee-status dual-table overview
- grant-fee workflow
- annuity workflow completion beyond reused support code
- report building
- schema unblock work
- permission/audit redesign outside exact endpoint needs

## 17. Risks

### 16.1 Structural risk

The `SPEC` requires fields that current models do not have. Any attempt to claim full `SPEC` completion without schema work would be inaccurate.

### 16.2 Scope risk

This story naturally tends to absorb:

- fee overview
- receipt registration
- annuity closure
- export-format variants

The implementation plan must keep those in separate follow-up tasks.

### 16.3 UX risk

If UI remains fully annuity-branded, the story may appear implemented but still fail the approved information-architecture requirement.

## 18. This-Round Slice Ledger

### 18.1 Default executable slices only

- generation of pay lists from GOV fee items
- historical pay-list header creation
- pay-list list query with supported filters only
- pay-list detail read
- Excel export with explicit `DRAFT -> EXPORTED` transition
- compatible `EXPORTED -> PAID` transition
- gov-payment registration under an existing pay list
- manual/historical gov-payment row creation under an existing pay list
- Fee Management-semantic frontend entry and pages in Simplified Chinese

These are planning buckets, not a story-level done claim. `writing-plans` must convert each bucket into one or more atomic tasks with their own closure and non-closure statements.

### 18.2 Deferred or blocked slices

- pay-list cancellation unless dedicated slice `SL-12` is explicitly planned
- any missing `SPEC` data field requiring schema change
- structured query by type, history marker, fee code, invoice, or voucher
- XML or text export
- standalone `GovPayment` outside a pay list
- paid-row audit-log redesign
- fee dual-table overview
- case receipt workflow

## 19. Per-Slice Acceptance Rules

Planning and execution must use per-slice acceptance only. No agent may claim the whole story complete from this section.

### 19.1 Every executable slice must independently prove

- its exact closure slice is complete
- its explicit non-closure boundary was respected
- its verification commands passed
- its evidence requirements were produced
- it did not silently absorb another slice from Section 9
- any user-visible frontend text introduced by that slice is Simplified Chinese

Capability acceptance such as generation, query, detail, export, mark-paid, or manual-row entry must be attached only to the slice that explicitly closes that capability.

### 19.2 Truth-in-acceptance rules

The story must not be marked fully `SPEC-complete` for blocked fields. The final acceptance output must explicitly separate:

- completed Phase 3-compatible closure
- blocked `SPEC` closure requiring schema work

## 20. Follow-Up Ledger

Separate follow-up task families should be generated for:

- schema unblock for missing `T_PayList` fields
- schema unblock for missing `T_GovPayment` fields
- query enhancement for missing structured filters
- audit/logging for privileged paid-row edits
- multi-format export enhancement
- full Fee Management integration beyond reused annuity routes

## 21. Recommended Planning Mode

The next step should use `writing-plans` and produce atomic task files under `tasks/` where each task specifies:

- exact closure slice
- explicit non-closure statement
- allowlist
- verification commands
- evidence expectations

The plan should distinguish:

- executable Phase 3-compatible tasks
- blocked schema-dependent tasks
