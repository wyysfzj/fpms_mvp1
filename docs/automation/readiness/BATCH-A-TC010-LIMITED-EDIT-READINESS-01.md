# BATCH-A-TC010-LIMITED-EDIT-READINESS-01

## 1. Batch Scope

| Testcase | Priority | Category | Topic | Close Need |
|---|---:|---|---|---|
| TC-A-010 | P0 | Happy, Unhappy | A1 限制修改视图 | Limited-edit endpoint must persist approved whitelist fields, reject or ignore blacklist mutation, and avoid status/task/fee side effects. |

`TC-A-010` is included in `FPMS_Automation_Skeleton_Pack/data/manifests/smoke_p0.yaml`, and `handle_tc_a_010` remains the only A-wave P0 smoke handler still marked with `@skeleton_case` after the A-wave close audit.

## 2. Capability Matrix

| Capability | Current State | Evidence | Readiness |
|---|---|---|---|
| Backend route | `POST /api/v1/cases/{case_id}/limited-edit` exists with `Case.EditLimited` permission. | `backend/app/modules/cases/api.py` | partial |
| Service helper | `update_case_limited` exists and supports title/spec subset plus inventors and `updated_by`. | `backend/app/modules/cases/service.py` | partial |
| API to service wiring | Route currently uses inline `dict[str, Any]` logic and does not call the service helper. | `backend/app/modules/cases/api.py` | blocked |
| Schema whitelist | `CaseUpdateLimited` exists but lacks some spec fields such as `draw_pages`, `claim_pages`, and `manuscript_words`. | `backend/app/modules/cases/schemas.py` | blocked |
| Remarks/notes | Frontend exposes `notes`, but backend case model/schema does not expose a persisted notes field. | `frontend/src/modules/cases/components/LimitedEditDialog.vue`, backend cases model/schema | product decision required |
| Blacklist protection | Current route only writes selected keys, so blacklist fields sent to limited-edit do not mutate. | `backend/app/modules/cases/api.py` | ready after contract |
| No side effects | Current limited-edit path does not call status/task/fee generation. | backend route/service inspection | ready after contract |

## 3. Blocker Ledger

| Blocker | Type | Testcase | Required Task | Decision |
|---|---|---|---|---|
| Limited-edit product surface includes remarks/description but backend has no field. | product contract | TC-A-010 | PRODUCT-A-CASE-LIMITED-EDIT-CONTRACT-01 | Freeze MVP: title/spec/inventors are automation surface; dedicated remarks field deferred. |
| API route does not use `CaseUpdateLimited` / service helper. | backend capability | TC-A-010 | BE-A-CASE-LIMITED-EDIT-RULE-01 | Wire route to schema/service and return stable case detail. |
| Schema/service whitelist lacks all MVP spec fields. | backend capability | TC-A-010 | BE-A-CASE-LIMITED-EDIT-RULE-01 | Add `draw_pages`, `claim_pages`, `manuscript_words` support without schema migration. |
| Existing tests assert TC-A-010 remains skeleton. | test maintenance | TC-A-010 | A-AUTO-PY-A-LIMITED-EDIT-P0-01 | Update only stale skeleton-boundary assertions in allowlisted files. |

## 4. State-Machine Reachability

TC-A-010 can arrange its own case through public API using existing A-wave helpers for client, applicant, and case creation. Batch 1 rules require valid applicants; the automation task must include applicant prerequisites and legal date/status payloads so unrelated applicant/date validation does not mask limited-edit behavior.

## 5. Allowlist Matrix

| Task | Allowed Files | Shared File Notes |
|---|---|---|
| PRODUCT-A-CASE-LIMITED-EDIT-CONTRACT-01 | `tasks/product/PRODUCT-A-CASE-LIMITED-EDIT-CONTRACT-01.md`, `docs/product/PRODUCT-A-CASE-LIMITED-EDIT-CONTRACT-01.md`, artifacts | no shared source files |
| BE-A-CASE-LIMITED-EDIT-RULE-01 | `backend/app/modules/cases/api.py`, `backend/app/modules/cases/schemas.py`, `backend/app/modules/cases/service.py`, `backend/tests/test_case_limited_edit_rule.py`, task/artifacts | serialize with any cases service/schema edits |
| A-AUTO-PY-A-LIMITED-EDIT-P0-01 | `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py`, `tests/test_a_limited_edit_handler.py`, stale TC-A-010 skeleton assertion files, task/artifacts | serialize `wave_a.py` |

## 6. Automation Landing Readiness

Automation should wait for:

1. `PRODUCT-A-CASE-LIMITED-EDIT-CONTRACT-01` PASS.
2. `BE-A-CASE-LIMITED-EDIT-RULE-01` PASS.

After those pass, `A-AUTO-PY-A-LIMITED-EDIT-P0-01` can implement `handle_tc_a_010` by asserting:

- whitelisted fields persist: title, selected spec fields, inventors;
- blacklist fields do not mutate through limited-edit;
- `updated_at` changes and `updated_by` is populated when backend exposes it;
- status, filing/application identifiers, task generation, and fee draft generation remain unchanged.
