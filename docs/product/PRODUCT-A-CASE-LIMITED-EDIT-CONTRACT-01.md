# PRODUCT-A-CASE-LIMITED-EDIT-CONTRACT-01

## Scope

This contract freezes the TC-A-010 MVP assertion surface for A-wave close.

## TC-A-010 MVP Contract

The limited-edit entry is a separate case edit path protected by `Case.EditLimited`. It allows a user with that permission to update only non-critical supplemental fields and must not trigger status, task, fee, billing, payment, or commission side effects.

## Whitelist Fields

For Batch 4/A-wave close, the backend-supported whitelist is:

- `title_cn`
- `title_en`
- `spec_pages`
- `draw_pages`
- `claim_count`
- `claim_pages`
- `manuscript_words`
- `inventors`

`inventors` means replacing the case inventor list with the submitted rows following existing `CaseInventorIn` shape.

## Blacklist Fields

The limited-edit endpoint must not mutate:

- `case_no`
- `status`
- `filing_date`
- `app_no`
- `client_id`
- `case_type`
- `patent_category`
- `flow_dir`
- `applicant_kind`
- `fee_reduction`
- `has_exam_request`

For MVP, extra blacklist fields submitted to the limited-edit endpoint may be ignored by the request parser or rejected by validation. The stable automation assertion is that these fields do not change in the case detail after the request.

## Remarks / Notes Decision

The broader product spec mentions limited remarks or description, and current frontend types include `notes`. The current backend case model and case response schema do not persist a notes field. Batch 4/A-wave close explicitly defers persisted remarks/notes to a future product/data-model task.

Follow-up if required later:

- PRODUCT-A-CASE-LIMITED-REMARKS-CONTRACT-01
- BE-A-CASE-LIMITED-REMARKS-DATA-MODEL-01
- FE-A-CASE-LIMITED-EDIT-UI-ALIGN-01

## Response Contract

The endpoint returns the updated case detail using the existing case response shape. Existing clients that only check HTTP 200 remain compatible.

## Side-Effect Contract

Limited edit must not:

- change case status;
- create task records;
- create fee drafts or fee items;
- modify filing/application/publication/grant dates or numbers;
- trigger batch filing, fee draft, pay list, bill, payment, or commission flows.

## Automation Assertion Surface

`A-AUTO-PY-A-LIMITED-EDIT-P0-01` must assert:

- whitelist fields persist through real backend API;
- blacklist fields do not mutate;
- status remains unchanged;
- no task/fee side effects are observed through available query paths;
- `handle_tc_a_010` is the only handler unskeletoned by that automation task.
