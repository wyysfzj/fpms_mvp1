# BATCH-B-READINESS-GATE-01

## 1. Batch Scope

Wave: `B OA/补正`

P0 smoke scope from `smoke_p0.yaml`:

- `TC-B-001`
- `TC-B-003`
- `TC-B-004`
- `TC-B-006`
- `TC-B-007`
- `TC-B-008`
- `TC-B-011`

Full B-wave scope from `by_wave/b.yaml`:

| Testcase | Priority | Category | Topic | Handler state | Readiness |
| --- | --- | --- | --- | --- | --- |
| `TC-B-001` | P0 | Happy | B1 OA来文登记 | skeleton | blocked |
| `TC-B-002` | P1 | Happy/Boundary | B1 官方绝限覆盖 | skeleton | product/backend blocker |
| `TC-B-003` | P0 | Unhappy | B1 文档行校验 | skeleton | blocked |
| `TC-B-004` | P0 | Happy | B2 OA答复任务生成 | skeleton | blocked |
| `TC-B-005` | P2 | Happy | B3 内部准备任务 | skeleton | deferred |
| `TC-B-006` | P0 | Happy | B4 OA答复去文 | skeleton | blocked |
| `TC-B-007` | P0 | Unhappy | B4 ReplyTo 约束 | skeleton | blocked |
| `TC-B-008` | P0 | Happy | B5 自动核销任务与状态恢复 | skeleton | blocked |
| `TC-B-009` | P1 | Happy | B6 OA费用草单 | skeleton | backend readiness required |
| `TC-B-010` | P2 | Happy | B7 OA官方费清单 | skeleton | deferred |
| `TC-B-011` | P0 | Happy | B8 OA账单与收款 | skeleton | blocked by upstream OA fee readiness |
| `TC-B-012` | P1 | Happy | B9 OA服务费计入提成 | skeleton | backend readiness required |
| `TC-B-013` | P1 | Happy/Unhappy | 主界面修改 NeedReply/Deadline | skeleton | product decision required |

## 2. Capability Matrix

| Area | Current backend support | Gap |
| --- | --- | --- |
| DocTemplate CRUD | `/api/v1/doc-templates` exists with `status_effect`, `status_restore`, `deadline_template_code`, `fee_draft_type`, `need_reply`, `reply_to_template_code` fields | skeleton seed names do not match backend seed names |
| Document CRUD | `/api/v1/documents` exists with reply fields and attachments | B row validation/error surface needs focused evidence |
| Wizard batch create | `/api/v1/documents/wizard/batch-create` exists | existing backend tests are stale because case helpers miss applicants |
| Task preview/create | wizard task preview and final task rows exist; `TaskGenerationService` creates document tasks | official due date override from skeleton is not clearly supported |
| Reply chain | reply fields, auto write-off, status effect/restore exist in service/tests | same-case and template-code constraint needs focused rule evidence |
| Attachment generation | wizard attachment preview/final rows exist | real template source/storage behavior must be constrained in automation |
| OA fee draft | document fee-linking supports template `fee_draft_type` and `fee_item_list` | backend seed has no OA fee template equivalent to skeleton `OA_FEE` |
| OA bill/payment | A-wave billing/payment capabilities exist | need readiness proof for OA draft lineage and CaseReceipt |
| OA commission | commission hook exists for bills | need readiness proof for OA scope/source remark semantics |

## 3. Product Contract Matrix

| Topic | Ambiguity | Required task |
| --- | --- | --- |
| Template naming | skeleton uses `OA_NOTICE`, `OA_REPLY`, `OA_REPLY_LIMIT`; backend uses `OA_IN`, `OA_OUT`, `OA_REPLY` | `PRODUCT-B-OA-WIZARD-CONTRACT-01` |
| OfficialDueDate override | skeleton says deadline should use `OfficialDueDate`, base remains `DispatchDate`; current task generation uses document/case dates and template offsets | `PRODUCT-B-OA-WIZARD-CONTRACT-01`, then backend task if confirmed |
| NeedReply/Deadline edit | skeleton expects update/cancel task side effects from main screen | product decision required before backend |
| OA fee draft | skeleton expects `OA_FEE` with SERVICE and optional GOV items | contract must define template/rate/fee item semantics |
| OA commission | skeleton asks新增或累加 BaseFee and traceable OA stage remark | contract must define update vs new row semantics |

Read-only backend discovery found existing routes and frontend pages for the major B slices. The primary capability gaps are not router wiring gaps; they are assertion-surface and seed/config gaps.

## 4. Test-Maintenance Matrix

Backend readiness test run showed B/document tests are currently blocked before target assertions by `CASE_APPLICANT_REQUIRED`.

Known stale files:

- `backend/tests/test_b2_reply_chain.py`
- `backend/tests/test_b3_fee_linking.py`
- `backend/tests/test_document_wizard_batch_create.py`
- `backend/tests/test_document_wizard_task_preview.py`
- `backend/tests/test_document_wizard_fee_preview.py`
- `backend/tests/test_document_wizard_attachment_preview.py`

Required blocker:

- `BE-B-DOCUMENT-TEST-MAINT-01`

Scope: add valid applicants to helper-created cases only, preserving existing business assertions.

## 5. Seed / Config Matrix

| Seed/config | Skeleton expectation | Current backend seed | Status |
| --- | --- | --- | --- |
| OA incoming template | `OA_NOTICE` | `OA_IN` | mismatch |
| OA reply template | `OA_REPLY` | `OA_OUT` | mismatch |
| OA deadline template | `OA_REPLY_LIMIT` | `OA_REPLY` | mismatch |
| OA fee draft type | `OA_FEE` | not clearly seeded as doc template fee draft | blocker |
| OA service fee rate | `OA_SERVICE_STANDARD` in skeleton seed | fee seed exists in skeleton; backend seed path unclear | readiness required |
| OA commission rule | scope `OA` in skeleton seed | commission model supports rules | readiness required |

## 6. State-Machine Reachability Matrix

| Testcase | Prerequisite | Public API reachable now | Blocker |
| --- | --- | --- | --- |
| `TC-B-001` | SUB_EXAM case + OA template | likely reachable after valid applicant setup | stale tests + template naming |
| `TC-B-004` | successful OA incoming document | likely reachable after `TC-B-001` readiness | task field evidence |
| `TC-B-006` | OA incoming + open reply task | likely reachable after `TC-B-004` readiness | reply contract |
| `TC-B-008` | OA reply submission | likely reachable after `TC-B-006` readiness | auto write-off evidence |
| `TC-B-011` | OA fee draft | not proven | OA fee draft blocker |

Mandatory setup lesson: every public API case creation must include valid applicants unless the testcase intentionally exercises applicant-list errors.

## 7. Allowlist Matrix

| Proposed task | Type | Required files | Serialization |
| --- | --- | --- | --- |
| `BE-B-DOCUMENT-TEST-MAINT-01` | test maintenance | B/document backend tests only | SQLite tests serialized |
| `PRODUCT-B-OA-WIZARD-CONTRACT-01` | product contract | product task/doc/artifacts only | can run before backend |
| `BE-B-OA-WIZARD-READINESS-01` | backend readiness/rule | documents service/api/schemas + focused tests | serial with other document service tasks |
| `BE-B-OA-REPLY-READINESS-01` | backend readiness/rule | documents service/api/schemas + focused tests | serial with other document service tasks |
| `BE-B-OA-FINANCE-READINESS-01` | backend readiness/rule | document/fees/billing/commission service + focused tests | serial shared services |

## 8. Env Matrix

Local backend was not assumed as testcase PASS evidence during readiness. Future automation PASS must run real smoke with:

`FPMS_DB_DSN=`

and a fresh `FPMS_RUN_ID`.

## 9. Blocker Drain Manifest

See `tasks/batches/BATCH-B-BLOCKER-DRAIN-01.md`.

## 10. Readiness Decision

Decision: **BLOCKED for B-wave automation landing. PASS for readiness gate.**

Automation must not start until at least:

1. `BE-B-DOCUMENT-TEST-MAINT-01` PASS
2. `PRODUCT-B-OA-WIZARD-CONTRACT-01` PASS
3. relevant backend readiness tasks PASS

Readiness did not stop at the first blocker: it scanned all 13 B-wave cases and categorized B1 through B9 dependencies.

## 11. Subagent Discovery Notes

Read-only explorer findings incorporated:

- all 13 `wave_b.py` handlers are still decorated with `@skeleton_case`; a green `pytest tests/test_wave_b.py` currently proves only skip behavior.
- backend already exposes document, task, fee, pay-list, billing, payment, and commission endpoints relevant to B.
- `OfficialDueDate` is not consumed by current task generation.
- default backend seeds use `OA_IN`, `OA_OUT`, and `OA_REPLY`, while skeleton data uses `OA_NOTICE`, `OA_REPLY`, and `OA_REPLY_LIMIT`.
- reply-to constraints are weaker than skeleton wording and need product/backend confirmation.
- default `OA_OUT` seed has no `status_restore=SUB_EXAM`, so B5 restoration needs seed/config or contract alignment.
