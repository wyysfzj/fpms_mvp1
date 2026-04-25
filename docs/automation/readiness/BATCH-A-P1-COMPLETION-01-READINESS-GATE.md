# BATCH-A-P1-COMPLETION-01-READINESS-GATE

## 1. Batch Scope

Batch 4 covers the remaining A-wave P1 completion cases:

| Testcase | Priority | Category | Topic | Proposed automation task |
| --- | --- | --- | --- | --- |
| `TC-A-002` | P1 | Happy | A1 新案立案-完整字段 | `A-AUTO-PY-A-MINIMAL-REQUIRED-P1-01` |
| `TC-A-007` | P1 | Happy, Unhappy | A1 发明人与地址 | `A-AUTO-PY-A-FOREIGN-COMBO-P1-01` |
| `TC-A-009` | P1 | Boundary | A1 规格/费减/折扣边界 | `A-AUTO-PY-A-SPEC-FEE-DISCOUNT-P1-01` |
| `TC-A-014` | P1 | Happy, Boundary | A3 时限基准与提醒 | `A-AUTO-PY-A-TASK_REASSIGN-P1-01` |

Dependency order:

1. A1 case-create rules: `TC-A-002`, `TC-A-007`, `TC-A-009`.
2. A3 deadline task rule: `TC-A-014`.
3. Automation landing must edit `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py` serially.

## 2. Capability Matrix

| Testcase | Backend endpoint(s) | Service/model support | Response stable | Readiness |
| --- | --- | --- | --- | --- |
| `TC-A-002` | `POST /api/v1/cases`, `GET /api/v1/cases/{id}` | Most full fields persist: applicants, inventors, priorities, bio deposits, spec fields, addresses. `GeneralPowerUsed` has no backend/API field. `PrioDate` is represented by priority rows, not a persisted case-level field. | Detail response returns sub-table rows and audit timestamps. | blocked |
| `TC-A-007` | `POST /api/v1/cases`, address APIs | Inventors are optional. Address ownership is validated when an address id is supplied. No current rule for country-driven inventor-required behavior or empty doc/bill address warning/block. | Existing address mismatch error is stable; missing-address warning semantics are not. | blocked |
| `TC-A-009` | `POST /api/v1/cases`, `PUT /api/v1/cases/{id}` | Non-negative integer fields and `discount_rate` 0..1 are schema-backed. `fee_reduction` is free text and not save-time range validated. Applicant-kind mismatch exists, but fee-policy mismatch warning/block is not frozen. | Schema 422 for numeric bounds is stable; fee-reduction/product warning surface is not. | blocked |
| `TC-A-014` | task-template APIs, batch filing submit, task query/log APIs | Template date/reminder fields exist. `BE-A-APPLY-FEE-LIMIT-BASE-SOURCE-01` makes batch filing honor `CASE_EVENT` and `FILING_DATE`. `BE-A-TASK-REMINDER-RESPONSE-01` exposes reminder fields through task APIs. | Task detail/list/log response is stable. | ready / landed |

## 3. Backend Rule / Side Effect Matrix

| Testcase | Required behavior | Current support | Missing behavior | Proposed blocker |
| --- | --- | --- | --- | --- |
| `TC-A-002` | Full field save, earliest priority surfaced, general power suggestion/auto-check | Full field persistence mostly exists. Priorities are returned in detail. | Product must decide whether `PrioDate` is a derived assertion from priorities or a case-level field, and whether `GeneralPowerUsed` is backend, UI, or deferred. | `PRODUCT-A-CASE-A2-FULL-FIELDS-CONTRACT-01` |
| `TC-A-007` | No inventor allowed in non-strict country; strict country warning/block; disabled address rejected; no doc/bill address warning/block | Inventors optional, address ownership checked. | Strict-country inventor config and warning/block envelope are absent. Client address has no active flag today, so "disabled address" is not expressible through current address API/model. | `PRODUCT-A-CASE-A7-INVENTOR-ADDRESS-CONTRACT-01` |
| `TC-A-009` | Spec numeric bounds, fee reduction and discount 0..1, applicant-kind/fee-policy warning/block | Spec fields and discount are schema-backed. Applicant-kind rule exists. | `fee_reduction` save-time numeric range and fee-policy warning/block are product_decision_required. | `PRODUCT-A-CASE-SPEC-FEE-DISCOUNT-CONTRACT-01` |
| `TC-A-014` | CASE_EVENT and FILING_DATE template base sources, inner/deadline reminders, daily remind | PASS via `BE-A-APPLY-FEE-LIMIT-BASE-SOURCE-01`, `BE-A-TASK-REMINDER-RESPONSE-01`, and `A-AUTO-PY-A-TASK_REASSIGN-P1-01`. | None inside approved TC-A-014 scope. | closed |

## 4. Test-Maintenance Matrix

| File | Stale pattern | Required later update |
| --- | --- | --- |
| `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_create_handler.py` | `handle_tc_a_002` remains skeleton | Update only when `A-AUTO-PY-A-MINIMAL-REQUIRED-P1-01` lands |
| `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_duplicate_handler.py` | `handle_tc_a_002` remains skeleton | Update only when `A-AUTO-PY-A-MINIMAL-REQUIRED-P1-01` lands |
| `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_invalid_combo_handler.py` | `handle_tc_a_002` remains skeleton | Update only when `A-AUTO-PY-A-MINIMAL-REQUIRED-P1-01` lands |
| `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_apply_fee_limit_handler.py` | `handle_tc_a_014` remains skeleton | Update only when `A-AUTO-PY-A-TASK_REASSIGN-P1-01` lands |

## 5. Seed / Config Matrix

| Seed/config | Exists | Notes |
| --- | --- | --- |
| Case clients/applicants | yes | Batch 1 applicant type support exists; automation setup must include applicants. |
| Case addresses | partial | Client address exists, but no active/disabled flag was found for address records. |
| Task templates | yes | `TaskTemplate` has deadline/reminder fields and API CRUD. |
| APPLY_FEE_LIMIT trigger | partial | Batch filing creates tasks; FILING_DATE source needs backend readiness. |

## 6. State-Machine Reachability Matrix

| Testcase | Prerequisite state | Public API arrange possible | Blockers |
| --- | --- | --- | --- |
| `TC-A-002` | New domestic case with full sub-tables | yes for most fields | General power and case-level priority contract |
| `TC-A-007` | Cases with missing inventors/addresses and disabled address | partial | No disabled address model/API and no strict-country rule |
| `TC-A-009` | Case save/update boundaries | partial | `fee_reduction` and fee-policy warning semantics |
| `TC-A-014` | APPLY_FEE_LIMIT task generated from selected base source | partial | Batch filing base-source behavior |

## 7. Allowlist Matrix

| Task ID | Task file path | Allowed files | Serialization |
| --- | --- | --- | --- |
| `PRODUCT-A-CASE-A2-FULL-FIELDS-CONTRACT-01` | `tasks/product/PRODUCT-A-CASE-A2-FULL-FIELDS-CONTRACT-01.md` | task doc, product doc, artifacts | independent |
| `BE-A-CASE-A2-FULL-FIELDS-READINESS-01` | `tasks/backend/business_logic/BE-A-CASE-A2-FULL-FIELDS-READINESS-01.md` | cases service/api/schemas/tests only after contract | serialize `cases/service.py` |
| `PRODUCT-A-CASE-A7-INVENTOR-ADDRESS-CONTRACT-01` | `tasks/product/PRODUCT-A-CASE-A7-INVENTOR-ADDRESS-CONTRACT-01.md` | task doc, product doc, artifacts | independent |
| `BE-A-CASE-A7-INVENTOR-ADDRESS-RULE-01` | `tasks/backend/business_logic/BE-A-CASE-A7-INVENTOR-ADDRESS-RULE-01.md` | cases service/schemas/tests only after contract | serialize `cases/service.py` |
| `PRODUCT-A-CASE-SPEC-FEE-DISCOUNT-CONTRACT-01` | `tasks/product/PRODUCT-A-CASE-SPEC-FEE-DISCOUNT-CONTRACT-01.md` | task doc, product doc, artifacts | independent |
| `BE-A-CASE-SPEC-FEE-DISCOUNT-RULE-01` | `tasks/backend/business_logic/BE-A-CASE-SPEC-FEE-DISCOUNT-RULE-01.md` | cases schemas/service/tests only after contract | serialize `cases/service.py` |
| `BE-A-APPLY-FEE-LIMIT-BASE-SOURCE-01` | `tasks/backend/business_logic/BE-A-APPLY-FEE-LIMIT-BASE-SOURCE-01.md` | cases service and focused tests | serialize `cases/service.py` |
| `BE-A-TASK-REMINDER-RESPONSE-01` | `tasks/backend/apis_ext/BE-A-TASK-REMINDER-RESPONSE-01.md` | tasks schemas/api and focused tests | independent after base-source |

## 8. Blocker Drain Manifest

See `tasks/batches/BATCH-A-P1-COMPLETION-01-BLOCKER-DRAIN.md`.

Execution order:

1. Product contracts for `TC-A-002`, `TC-A-007`, `TC-A-009`.
2. Backend readiness/rule tasks only for contracts that PASS.
3. `BE-A-APPLY-FEE-LIMIT-BASE-SOURCE-01` for `TC-A-014`.
4. `BE-A-TASK-REMINDER-RESPONSE-01` for TC-A-014 API assertion surface.
5. Automation landing in `tasks/batches/BATCH-A-P1-COMPLETION-01.md`.

## 9. Automation Landing Readiness

| Automation task | Can start now | Required blockers first |
| --- | --- | --- |
| `A-AUTO-PY-A-MINIMAL-REQUIRED-P1-01` | no | `PRODUCT-A-CASE-A2-FULL-FIELDS-CONTRACT-01`, then backend if needed |
| `A-AUTO-PY-A-FOREIGN-COMBO-P1-01` | no | `PRODUCT-A-CASE-A7-INVENTOR-ADDRESS-CONTRACT-01`, then backend if needed |
| `A-AUTO-PY-A-SPEC-FEE-DISCOUNT-P1-01` | no | `PRODUCT-A-CASE-SPEC-FEE-DISCOUNT-CONTRACT-01`, then backend if needed |
| `A-AUTO-PY-A-TASK_REASSIGN-P1-01` | completed | `BE-A-APPLY-FEE-LIMIT-BASE-SOURCE-01` and `BE-A-TASK-REMINDER-RESPONSE-01` PASS |

## Execution Prompt To Reuse

You are in the real FPMS repository root. Execute `BATCH-A-P1-COMPLETION-01-READINESS-GATE` before any Batch 4 automation. Do not stop at the first blocker. Confirm `TC-A-002/007/009/014` from skeleton data, build capability, seed/config, state-machine, allowlist, stale-test, and automation-readiness matrices, then create `BATCH-A-P1-COMPLETION-01-BLOCKER-DRAIN` and `BATCH-A-P1-COMPLETION-01`. Do not implement `wave_a.py` until all prerequisite product/backend blockers for that testcase have PASS evidence. Keep shared `cases/service.py` and `wave_a.py` serialized. Do not fake warning/block semantics; if current product semantics are unclear, mark `product_decision_required`.
