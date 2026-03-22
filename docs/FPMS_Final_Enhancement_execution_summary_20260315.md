# FPMS Final Enhancement Execution Summary (2026-03-15)

## Executive Summary

This document records the actual Batch 1 implementation outcome under the approved native workflow.

Current overall result:
- `Batch 1` original scope: `complete`
- deferred `Batch 1` follow-up (`FR-CM-03` + `FR-CM-05`): `complete`
- `Batch 2`: `complete`
- `Batch 3`: `complete`
- `Batch 4`: `complete`
- original mixed `Batch 5` scope: `not complete`
- adjusted `Batch 5A` scope: `complete`

Execution stayed inside:
- `Batch 1`
- Case-domain enhancement scope
- approved bounded schema/model expansion for deferred Batch 1 only
- no `document generation` implementation

Additional execution status:
- `Batch 2` implementation started and stayed inside Documents + Tasks scope
- `Batch 2` remaining-scope follow-up started on `2026-03-16`
- `Batch 2` remaining-scope follow-up passed dedicated task gates and close audit
- `Batch 3` fees / annuity / receipt follow-up started on `2026-03-17`
- `Batch 3` passed serialized wave execution and final close audit
- `Batch 4` billing / collections follow-up started on `2026-03-18`
- `Batch 4` passed serialized wave execution and final close audit on `2026-03-21`
- `Batch 5` commission / consulting follow-up started on `2026-03-21`
- `Batch 5` completed all executable commission slices under the approved no-schema assumptions
- `Batch 5` close audit showed consulting/search residual scope had no no-schema exact closure slice
- approved scope-adjustment moved consulting/search residual scope out of Batch 5
- adjusted `Batch 5A` closes on commission-only evidence

## Progress Snapshot (As of 2026-03-21)

| Batch | Status | Completed Task IDs | Remaining Task IDs | Blockers |
|---|---|---|---|---|
| `Batch 1` | `complete` | `PE-BE-CM-01`, `PE-FE-CM-02`, `PE-BE-DB-CM-02`, `PE-BE-CM-02`, `PE-FE-CM-03`, `PE-QA-CM-03` | none | none |
| `Batch 2` | `complete` | `PE-BE-WD-02`, `PE-FE-WD-02`, `PE-BE-DL-02`, `PE-FE-DL-02`, `PE-BE-WD-03`, `PE-FE-WD-03`, `PE-BE-DL-03`, `PE-FE-DL-03`, `PE-QA-B2-02` | none | none |
| `Batch 3` | `complete` | `PE-BE-FE-03`, `PE-FE-FE-03`, `PE-BE-AN-08`, `PE-FE-AN-06`, `PE-BE-FE-04`, `PE-FE-FE-04`, `PE-QA-B3-01` | none | none |
| `Batch 4` | `complete` | `PE-BE-BL-01`, `PE-FE-BL-01`, `PE-BE-BL-02`, `PE-FE-BL-02`, `PE-BE-BL-03`, `PE-FE-BL-03`, `PE-QA-B4-01` | none | none |
| `Batch 5` | `complete (adjusted scope)` | `PE-BE-COM-01`, `PE-FE-COM-01`, `PE-BE-COM-02`, `PE-FE-COM-02`, `PE-BE-COM-03`, `PE-FE-COM-03`, `PE-QA-B5-01` | none inside adjusted Batch 5 scope | consulting/search residuals moved out by scope adjustment |

Progress notes:
- `Batch 4` manifest is already in place: `tasks/postenhancement/BATCH4_BILLING_COLLECTIONS_MANIFEST_20260318.md`
- `Batch 4` completed slices already passed task gates with evidence under:
  - `artifacts/PE-BE-BL-01`
  - `artifacts/PE-FE-BL-01`
  - `artifacts/PE-BE-BL-02`
  - `artifacts/PE-FE-BL-02`
- `Batch 4` still requires:
  - none
- `Batch 5` manifest is in place: `tasks/postenhancement/BATCH5_COMMISSION_CONSULTING_MANIFEST_20260321.md`
- `Batch 5` commission slices passed task gates with evidence under:
  - `artifacts/PE-BE-COM-01`
  - `artifacts/PE-FE-COM-01`
  - `artifacts/PE-BE-COM-02`
  - `artifacts/PE-FE-COM-02`
  - `artifacts/PE-BE-COM-03`
  - `artifacts/PE-FE-COM-03`
- `Batch 5` still requires:
  - none inside adjusted Batch 5 scope

## Batch 5 Covered Scope

Execution baseline:
- `AGENTS.md`
- `docs/FPMS_Final_Enhancement_Plan_Native_20260315.md`
- `docs/FPMS_Code_Review_Report_SPEC_2.0_20260227.md`
- `docs/FPMS_Final_Enhancement_Plan_and_Task_Breakdown_SPEC_2.0_20260228.md`
- `docs/Batch_Execution_Improvement_Plan_20260316.md`
- `docs/BATCH_EXECUTION_TASK_TEMPLATE_20260318.md`
- `docs/BATCH_EXECUTION_QA_LEDGER_TEMPLATE_20260318.md`
- `docs/BATCH_EXECUTION_TAKEOVER_RULES_20260318.md`

Batch 5 manifest:
- `tasks/postenhancement/BATCH5_COMMISSION_CONSULTING_MANIFEST_20260321.md`
- `docs/FPMS_Batch5_Scope_Adjustment_20260321.md`

Atomic task files executed:
- `tasks/postenhancement/backend/PE-BE-COM-01.md`
- `tasks/postenhancement/frontend/PE-FE-COM-01.md`
- `tasks/postenhancement/backend/PE-BE-COM-02.md`
- `tasks/postenhancement/frontend/PE-FE-COM-02.md`
- `tasks/postenhancement/backend/PE-BE-COM-03.md`
- `tasks/postenhancement/frontend/PE-FE-COM-03.md`
- `tasks/postenhancement/backend/PE-QA-B5-01.md`

Task-level outcome:
- `PE-BE-COM-01` -> `PASS`
- `PE-FE-COM-01` -> `PASS`
- `PE-BE-COM-02` -> `PASS`
- `PE-FE-COM-02` -> `PASS`
- `PE-BE-COM-03` -> `PASS`
- `PE-FE-COM-03` -> `PASS`
- `PE-QA-B5-01` -> `PASS` for adjusted-scope close audit

Covered slices:
- Commission backend:
  - manual bill creation now triggers existing commission auto-generation hook
  - settlement line generation now marks `s1_done / s2_done` and moves rows to `SETTLED`
  - settlement report detail now exposes `s1_done`, `s2_done`, `is_settleable`
- Commission frontend:
  - commission list now shows settleability and stage visibility
  - settlement page now shows readable status tags and stage completion overview
  - settlement report detail now renders `S1 / S2 / 可结算` visibility using the existing query contract
- Consulting/search:
  - moved out of adjusted Batch 5 close scope by `docs/FPMS_Batch5_Scope_Adjustment_20260321.md`

## Batch 5 Agent-to-Task Mapping

| Role | Task ID | Task File | Outcome |
|---|---|---|---|
| `worker` | `PE-BE-COM-01` | `tasks/postenhancement/backend/PE-BE-COM-01.md` | `PASS` |
| `worker` | `PE-FE-COM-01` | `tasks/postenhancement/frontend/PE-FE-COM-01.md` | `PASS` |
| `worker` | `PE-BE-COM-02` | `tasks/postenhancement/backend/PE-BE-COM-02.md` | `PASS` |
| `worker` | `PE-FE-COM-02` | `tasks/postenhancement/frontend/PE-FE-COM-02.md` | `PASS` |
| `worker` | `PE-BE-COM-03` | `tasks/postenhancement/backend/PE-BE-COM-03.md` | `PASS` |
| `worker` | `PE-FE-COM-03` | `tasks/postenhancement/frontend/PE-FE-COM-03.md` | `PASS` |
| `monitor` | `PE-QA-B5-01` | `tasks/postenhancement/backend/PE-QA-B5-01.md` | `PASS` |

## Batch 5 Execution Waves

### Wave 1

- Role: backend `worker`
- Task: `PE-BE-COM-01`
- Mode: serialized
- Result: `PASS`

### Wave 2

- Role: frontend `worker`
- Task: `PE-FE-COM-01`
- Mode: serialized
- Result: `PASS`

### Wave 3

- Role: backend `worker`
- Task: `PE-BE-COM-02`
- Mode: serialized
- Result: `PASS`

### Wave 4

- Role: frontend `worker`
- Task: `PE-FE-COM-02`
- Mode: serialized
- Result: `PASS`

### Wave 5

- Role: backend `worker`
- Task: `PE-BE-COM-03`
- Mode: serialized
- Result: `PASS`

### Wave 6

- Role: frontend `worker`
- Task: `PE-FE-COM-03`
- Mode: serialized
- Result: `PASS`

### Wave 7

- Role: `monitor`
- Task: `PE-QA-B5-01`
- Mode: serialized
- Result: `PASS`

## Batch 5 Partially Implemented Repair Matrix

| Item | Implemented Task IDs | Status | Notes |
|---|---|---|---|
| `US-COM-02` | `PE-BE-COM-01`, `PE-FE-COM-01` | `covered` | auto-generation + visibility slice completed |
| `FR-COM-02` | `PE-BE-COM-01`, `PE-FE-COM-01` | `covered` | same narrowed interpretation as Batch 5 freeze |
| `US-COM-06` | `PE-BE-COM-02`, `PE-FE-COM-02` | `covered` | settlement stage completion slice completed |
| `FR-COM-06` | `PE-BE-COM-02`, `PE-FE-COM-02` | `covered` | same narrowed interpretation as Batch 5 freeze |
| `FR-COM-07` | `PE-BE-COM-03`, `PE-FE-COM-03` | `covered` | report completeness / visibility slice completed |

## Batch 5 Validation Results

- `./scripts/task_validate.sh PE-BE-COM-01` -> `PASS`
- `./scripts/task_validate.sh PE-FE-COM-01` -> `PASS`
- `./scripts/task_validate.sh PE-BE-COM-02` -> `PASS`
- `./scripts/task_validate.sh PE-FE-COM-02` -> `PASS`
- `./scripts/task_validate.sh PE-BE-COM-03` -> `PASS`
- `./scripts/task_validate.sh PE-FE-COM-03` -> `PASS`
- `cd backend && pytest -q tests/test_commission_e2e.py tests/test_consulting_e2e.py` -> `5 passed`
- `cd frontend && npm run lint` -> `PASS`
- `cd frontend && npm run typecheck` -> `PASS`

## Batch 5 QA Item-to-Slice Ledger

| Item | Required Slices | Implemented Task IDs | Evidence | Residual Gap | Close Decision |
|---|---|---|---|---|---|
| `US-COM-02` | auto-generation hook + list visibility | `PE-BE-COM-01`, `PE-FE-COM-01` | task artifacts + commission regression | none | `covered` |
| `FR-COM-02` | same narrowed auto-generation slice | `PE-BE-COM-01`, `PE-FE-COM-01` | task artifacts + commission regression | none for Batch 5 freeze | `covered` |
| `US-COM-06` | settlement completion semantics + settlement UI visibility | `PE-BE-COM-02`, `PE-FE-COM-02` | settlement generation regression + settlement page visibility | none | `covered` |
| `FR-COM-06` | same narrowed settlement completion slice | `PE-BE-COM-02`, `PE-FE-COM-02` | task artifacts + settlement regression | none for Batch 5 freeze | `covered` |
| `FR-COM-07` | report completeness backend + report visibility frontend | `PE-BE-COM-03`, `PE-FE-COM-03` | report regression + report detail UI visibility | none | `covered` |

QA ledger conclusion:
- adjusted Batch 5 scope contains only commission items
- every in-scope adjusted Batch 5 item has a close decision and required evidence
- consulting/search residuals are moved out of adjusted Batch 5 scope and are not counted in the close decision

## Batch 5 Residual Risks / Blockers

- Frontend confidence still relies on lint/typecheck and contract-aligned visibility slices, not full browser replay.
- Consulting/search residual scope was intentionally moved out of Batch 5 rather than misreported as covered.

## Batch 5 Ready-for-Merge Checklist

- [x] Batch 5 stayed inside commission / consulting Batch 5 scope
- [x] No post-Batch-5 work started
- [x] No document-generation implementation
- [x] Shared ownership stayed serialized
- [x] Dirty baseline was handled by scoped evidence
- [x] All executable Batch 5 implementation task gates passed
- [x] Batch 5 close audit passed
- [x] Item-to-slice ledger completed
- [x] All adjusted Batch 5 in-scope items closed as `covered`

## Batch 5 Next Steps

- If consulting/search residual scope is pursued later, start from a new explicit manifest outside adjusted Batch 5.
- Do not reopen commission slices unless a new atomic task is approved.

## Batch 5 Stop Line

Stopped after Batch 5.
Batch 5 complete under adjusted scope, next batch not started.

## Batch 1 Covered Scope

Execution baseline:
- `docs/FPMS_Final_Enhancement_Plan_Native_20260315.md`
- `docs/FPMS_Code_Review_Report_SPEC_2.0_20260227.md`
- `docs/FPMS_Final_Enhancement_Plan_and_Task_Breakdown_SPEC_2.0_20260228.md`

Covered Case-domain items:
- `US-CM-01`
- `US-CM-02`
- `US-CM-03`
- `FR-CM-02`
- `FR-CM-03`
- `FR-CM-04`
- `FR-CM-05`

Batch manifests:
- `tasks/postenhancement/BATCH1_CASES_MANIFEST_20260315.md`
- `tasks/postenhancement/BATCH1A_CASES_FOLLOWUP_MANIFEST_20260315.md`
- `tasks/postenhancement/BATCH1B_CASES_DEFERRED_MANIFEST_20260315.md`

Atomic task files completed in the final close chain:
- `tasks/postenhancement/backend/PE-BE-CM-01.md`
- `tasks/postenhancement/frontend/PE-FE-CM-02.md`
- `tasks/postenhancement/backend/PE-BE-DB-CM-02.md`
- `tasks/postenhancement/backend/PE-BE-CM-02.md`
- `tasks/postenhancement/frontend/PE-FE-CM-03.md`
- `tasks/postenhancement/backend/PE-QA-CM-03.md`

## Agent-to-Task Mapping

| Role | Task ID | Task File | Outcome |
|---|---|---|---|
| `worker` | `PE-BE-CM-01` | `tasks/postenhancement/backend/PE-BE-CM-01.md` | `PASS` |
| `worker` | `PE-FE-CM-02` | `tasks/postenhancement/frontend/PE-FE-CM-02.md` | `PASS` |
| `worker` | `PE-BE-DB-CM-02` | `tasks/postenhancement/backend/PE-BE-DB-CM-02.md` | `PASS` |
| `worker` | `PE-BE-CM-02` | `tasks/postenhancement/backend/PE-BE-CM-02.md` | `PASS` |
| `worker` | `PE-FE-CM-03` | `tasks/postenhancement/frontend/PE-FE-CM-03.md` | `PASS` |
| `monitor` | `PE-QA-CM-03` | `tasks/postenhancement/backend/PE-QA-CM-03.md` | `PASS` |

## Execution Waves

### Wave 1

- Role: backend `worker`
- Task: `PE-BE-CM-01`
- Mode: serialized
- Result: `PASS`

### Wave 2

- Role: frontend `worker`
- Task: `PE-FE-CM-02`
- Mode: serialized
- Result: `PASS`

### Wave 3

- Role: backend `worker`
- Task: `PE-BE-DB-CM-02`
- Mode: serialized
- Reason: extends shared Case persistence and migration chain
- Result: `PASS`

### Wave 4

- Role: backend `worker`
- Task: `PE-BE-CM-02`
- Mode: serialized
- Reason: depends on `PE-BE-DB-CM-02`
- Result: `PASS`

### Wave 5

- Role: frontend `worker`
- Task: `PE-FE-CM-03`
- Mode: serialized
- Reason: depends on backend deferred-field contract
- Result: `PASS`

### Wave 6

- Role: `monitor`
- Task: `PE-QA-CM-03`
- Mode: serialized
- Reason: final Batch 1 deferred close audit
- Result: `PASS`

## Partially Implemented Repair Matrix

| Item | Final Result | Evidence-backed Outcome | Status |
|---|---|---|---|
| `US-CM-01` | validation hardening | backend + frontend evidence present | `covered` |
| `US-CM-02` | conditional case fields / mapping | backend + frontend evidence present | `covered` |
| `US-CM-03` | participant quick-create | customer + applicant path covered | `covered` |
| `FR-CM-02` | validation / field rules | backend + frontend evidence present | `covered` |
| `FR-CM-03` | participant quick-create | foreign-agent select + quick-create + backfill completed | `covered` |
| `FR-CM-04` | status linkage / readonly hint | backend + frontend evidence present | `covered` |
| `FR-CM-05` | extended case specifics | bio-deposit, PCT, invalidation, priority paths completed | `covered` |

## Detailed Changes

### Backend

Modified files:
- `backend/alembic/versions/pe_be_db_cm_02_case_ext_fields.py`
- `backend/app/modules/cases/enums.py`
- `backend/app/modules/cases/models.py`
- `backend/app/modules/cases/schemas.py`
- `backend/app/modules/cases/service.py`
- `backend/app/modules/cases/api.py`
- `backend/tests/test_case_fields.py`

Change description:
- added Case persistence for foreign-agent, PCT, invalidation, and bio-deposit fields
- added `T_BioDeposit` and SQLite-safe migration support
- enforced foreign-flow foreign-agent validation
- enforced bio-deposit completeness / duplicate-seq validation
- enforced PCT international / national phase required-field validation
- enforced invalidation required-field validation
- added deferred Batch 1 create/detail/update round-trip coverage

Intended diff scope:
- Case-domain backend and migration support only

### Frontend

Modified files:
- `frontend/src/api/cases.ts`
- `frontend/src/api/cases.types.ts`
- `frontend/src/modules/cases/pages/CaseCreate.vue`
- `frontend/src/modules/cases/pages/CaseEdit.vue`
- `frontend/src/modules/cases/pages/CaseDetail.vue`

Change description:
- extended case API/types to map foreign-agent, bio-deposit, PCT, and invalidation fields
- added foreign-agent select + quick-create + backfill on create/edit pages
- added bio-deposit repeatable rows on create/edit pages
- added conditional PCT and invalidation sections on create/edit pages
- added matching frontend validation for deferred Batch 1 rules
- added detail-page rendering for deferred Batch 1 case fields

Intended diff scope:
- Case create/edit/detail pages and cases API/type mapping only

## Validation Results

### Backend validation

- targeted Ruff on allowlist files: `passed`
- targeted pytest on deferred scope:
  - `cd backend && pytest -q tests/test_case_fields.py -k "DeferredBatch1Fields or foreign_agent or pct or invalidation or bio_deposit"`
  - result: `11 passed`
- full case regression:
  - `cd backend && pytest -q tests/test_case_fields.py`
  - result: `28 passed`

Backend evidence:
- `artifacts/PE-BE-DB-CM-02/results.jsonl`
- `artifacts/PE-BE-DB-CM-02/summary.md`
- `artifacts/PE-BE-DB-CM-02/git/diff.patch`
- `artifacts/PE-BE-CM-02/results.jsonl`
- `artifacts/PE-BE-CM-02/summary.md`
- `artifacts/PE-BE-CM-02/git/diff.patch`

### Frontend validation

- `cd frontend && npm run lint`
- result: `passed`
- `cd frontend && npm run typecheck`
- result: `passed`

Frontend evidence:
- `artifacts/PE-FE-CM-03/results.jsonl`
- `artifacts/PE-FE-CM-03/summary.md`
- `artifacts/PE-FE-CM-03/git/diff.patch`

### Gate status

- `./scripts/task_validate.sh PE-BE-DB-CM-02` -> `PASS`
- `./scripts/task_validate.sh PE-BE-CM-02` -> `PASS`
- `./scripts/task_validate.sh PE-FE-CM-03` -> `PASS`

## Residual Risks / Blockers

- No functional blocker remains for Batch 1 Case-domain closure.
- Frontend manual browser replay for every deferred field combination was not executed in this run; current FE confidence is based on lint/typecheck and backend round-trip tests.
- `T_BioDepositUnit` masterdata is still intentionally out of scope; this batch stores `deposit_unit_name` as text.

## Ready-for-Merge Checklist

- [x] Batch 1 stayed inside Case-domain scope
- [x] No Batch 2 work started
- [x] No document-generation implementation
- [x] Deferred schema expansion stayed bounded to Case-domain needs
- [x] Backend deferred-field validation passed
- [x] Full case backend regression passed
- [x] Frontend lint passed
- [x] Frontend typecheck passed
- [x] Deferred Batch 1 task gates passed
- [x] `FR-CM-03` fully closed
- [x] `FR-CM-05` fully closed

## Next Steps

- Start any further work from `Batch 2` planning or from new atomic tasks only.
- If later needed, split `T_BioDepositUnit` masterdata into a dedicated follow-up task rather than expanding Batch 1 retrospectively.

## Explicit Stop Line

Batch 1 complete.
Batch 2 complete.
Batch 3 complete, Batch 4 not started.

## Batch 3 Covered Scope

Execution baseline:
- `docs/FPMS_Final_Enhancement_Plan_Native_20260315.md`
- `docs/FPMS_Code_Review_Report_SPEC_2.0_20260227.md`
- `docs/FPMS_Final_Enhancement_Plan_and_Task_Breakdown_SPEC_2.0_20260228.md`
- `docs/Batch_Execution_Improvement_Plan_20260316.md`
- `tasks/postenhancement/BATCH3_EXECUTION_RUNBOOK_20260316.md`

Batch 3 manifest:
- `tasks/postenhancement/BATCH3_FEES_ANNUITY_MANIFEST_20260317.md`

Covered Cluster C4 items:
- `US-FE-02`
- `US-FE-03`
- `US-FE-04`
- `US-FE-05`
- `US-FE-06`
- `US-FE-08`
- `FR-FE-03`
- `FR-FE-04`
- `FR-FE-05`
- `FR-FE-06`
- `FR-FE-07`
- `FR-FE-09`

Atomic task files executed in this run:
- `tasks/postenhancement/backend/PE-BE-FE-03.md`
- `tasks/postenhancement/frontend/PE-FE-FE-03.md`
- `tasks/postenhancement/backend/PE-BE-AN-08.md`
- `tasks/postenhancement/frontend/PE-FE-AN-06.md`
- `tasks/postenhancement/backend/PE-BE-FE-04.md`
- `tasks/postenhancement/frontend/PE-FE-FE-04.md`
- `tasks/postenhancement/backend/PE-QA-B3-01.md`

## Batch 3 Agent-to-Task Mapping

| Role | Task ID | Task File | Outcome |
|---|---|---|---|
| `worker` | `PE-BE-FE-03` | `tasks/postenhancement/backend/PE-BE-FE-03.md` | `PASS` |
| `worker` | `PE-FE-FE-03` | `tasks/postenhancement/frontend/PE-FE-FE-03.md` | `PASS` |
| `worker` | `PE-BE-AN-08` | `tasks/postenhancement/backend/PE-BE-AN-08.md` | `PASS` |
| `worker` | `PE-FE-AN-06` | `tasks/postenhancement/frontend/PE-FE-AN-06.md` | `PASS` |
| `worker` | `PE-BE-FE-04` | `tasks/postenhancement/backend/PE-BE-FE-04.md` | `PASS` |
| `worker` | `PE-FE-FE-04` | `tasks/postenhancement/frontend/PE-FE-FE-04.md` | `PASS` |
| `monitor` | `PE-QA-B3-01` | `tasks/postenhancement/backend/PE-QA-B3-01.md` | `PASS` |

## Batch 3 Execution Waves

### Wave 1

- Role: backend `worker`
- Task: `PE-BE-FE-03`
- Mode: serialized
- Result: `PASS`

### Wave 2

- Role: frontend `worker`
- Task: `PE-FE-FE-03`
- Mode: serialized
- Result: `PASS`

### Wave 3

- Role: backend `worker`
- Task: `PE-BE-AN-08`
- Mode: serialized
- Result: `PASS`

### Wave 4

- Role: frontend `worker`
- Task: `PE-FE-AN-06`
- Mode: serialized
- Result: `PASS`

### Wave 5

- Role: backend `worker`
- Task: `PE-BE-FE-04`
- Mode: serialized
- Result: `PASS`

### Wave 6

- Role: frontend `worker`
- Task: `PE-FE-FE-04`
- Mode: serialized
- Result: `PASS`

### Wave 7

- Role: `monitor`
- Task: `PE-QA-B3-01`
- Mode: serialized
- Result: `PASS`

## Batch 3 Partially Implemented Repair Matrix

| Item | Final Result | Evidence-backed Outcome | Status |
|---|---|---|---|
| `US-FE-02 / FR-FE-03` | fee calc slice | `PER_CLAIM` + reduction/discount backend/frontend parity landed | `covered` |
| `US-FE-03 / FR-FE-04` | pay-list / gov-payment chain | annuity draft generation currency normalization and chain stability covered | `covered` |
| `US-FE-04 / FR-FE-05` | annuity / authorization-fee chain | annuity task and gov-payment workflow remained inside non-document-generation chain | `covered` |
| `US-FE-05 / FR-FE-06` | multi-year annuity handling | annuity task instruction / draft generation chain remained stable and validated | `covered` |
| `US-FE-06 / FR-FE-07` | case receipt visibility | receipt endpoint contract + frontend receipt summary visibility covered | `covered` |
| `US-FE-08 / FR-FE-09` | fee overview visibility | receipt bills overview + frontend summary visibility covered | `covered` |

## Batch 3 Detailed Changes

### Backend

Modified files:
- `backend/app/modules/fees/service.py`
- `backend/app/modules/annuity/service.py`
- `backend/app/modules/billing/api.py`
- `backend/app/modules/billing/schemas.py`
- `backend/tests/test_annuity_e2e.py`

Change description:
- implemented one fee-calculation closure slice for `PER_CLAIM` with reduction/discount handling
- normalized annuity draft-generation currency before rate lookup and draft persistence
- enriched case receipt read endpoint with stable response model and bills overview list
- added focused regression coverage for fee calculation, annuity draft generation, and receipt overview behavior

Intended diff scope:
- Batch 3 fee / annuity / receipt read-query semantics only

### Frontend

Modified files:
- `frontend/src/modules/fees/components/FeeRateForm.vue`
- `frontend/src/api/annuity.ts`
- `frontend/src/modules/cases/components/CaseReceiptsSummary.vue`

Change description:
- exposed `PER_CLAIM` calc-params guidance in fee-rate form
- normalized annuity draft-generation currency client-side before request
- added receipt currency visibility in case receipt summary

Intended diff scope:
- Batch 3 fee / annuity / receipt visibility only

## Batch 3 Validation Results

### Backend validation

- `ruff check backend/app/modules/fees/api.py backend/app/modules/fees/service.py backend/app/modules/fees/schemas.py backend/tests/test_annuity_e2e.py`
- `cd backend && pytest -q tests/test_annuity_e2e.py -k 'calculate_fee_amount_per_claim_with_reduction_and_discount or annuity_generate_drafts_pay_list_gov_payment_chain'`
- `ruff check backend/app/modules/annuity/api.py backend/app/modules/annuity/service.py backend/app/modules/tasks/task_generation_service.py backend/tests/test_annuity_e2e.py`
- `cd backend && pytest -q tests/test_annuity_e2e.py -k 'annuity_generate_drafts_normalizes_currency_case or annuity_generate_drafts_pay_list_gov_payment_chain'`
- `ruff check backend/app/modules/fees/api.py backend/app/modules/fees/service.py backend/app/modules/billing/api.py backend/app/modules/billing/schemas.py backend/tests/test_annuity_e2e.py`
- `cd backend && pytest -q tests/test_annuity_e2e.py -k 'receipt or overview or pay_list or gov_payment'`
- result: `all passed`

### Frontend validation

- `cd frontend && npm run lint`
- `cd frontend && npm run typecheck`
- result: `all passed`

### Task gate status

- `./scripts/task_validate.sh PE-BE-FE-03` -> `PASS`
- `./scripts/task_validate.sh PE-FE-FE-03` -> `PASS`
- `./scripts/task_validate.sh PE-BE-AN-08` -> `PASS`
- `./scripts/task_validate.sh PE-FE-AN-06` -> `PASS`
- `./scripts/task_validate.sh PE-BE-FE-04` -> `PASS`
- `./scripts/task_validate.sh PE-FE-FE-04` -> `PASS`

## Batch 3 Residual Risks / Blockers

- No functional blocker remains for Batch 3 close.
- Frontend confidence still relies on lint/typecheck and API-aligned slices, not full browser replay.
- `PER_PAGE` and `TIER` fee calc modes remain available for future refinement if the SPEC demands deeper parity, but Batch 3 close criteria for the implemented slice were satisfied.

## Batch 3 Ready-for-Merge Checklist

- [x] Batch 3 stayed inside Cluster C4 scope
- [x] No Batch 4 work started
- [x] No document-generation implementation
- [x] Shared ownership stayed serialized
- [x] Dirty baseline was handled by scoped evidence
- [x] All Batch 3 implementation task gates passed
- [x] Batch 3 close audit passed

## Batch 3 Next Steps

- Start any further work from `Batch 4` planning / freeze / manifest conversion only.
- Do not reopen Batch 3 unless a new explicit atomic task is approved.

## Batch 3 Stop Line

Stopped after Batch 3.
Batch 3 complete, Batch 4 not started.

## Batch 4 Covered Scope

Execution baseline:
- `AGENTS.md`
- `docs/FPMS_Final_Enhancement_Plan_Native_20260315.md`
- `docs/FPMS_Code_Review_Report_SPEC_2.0_20260227.md`
- `docs/FPMS_Final_Enhancement_Plan_and_Task_Breakdown_SPEC_2.0_20260228.md`
- `docs/Batch_Execution_Improvement_Plan_20260316.md`
- `docs/BATCH_EXECUTION_TASK_TEMPLATE_20260318.md`
- `docs/BATCH_EXECUTION_QA_LEDGER_TEMPLATE_20260318.md`
- `docs/BATCH_EXECUTION_TAKEOVER_RULES_20260318.md`

Batch 4 manifest:
- `tasks/postenhancement/BATCH4_BILLING_COLLECTIONS_MANIFEST_20260318.md`

Covered Cluster C5 items:
- `US-BL-02`
- `US-BL-06`
- `US-BL-07`
- `FR-BL-01`
- `FR-BL-03`
- `FR-BL-07`
- `FR-BL-08`
- `FR-BL-09`

Atomic task files executed in this run:
- `tasks/postenhancement/backend/PE-BE-BL-01.md`
- `tasks/postenhancement/frontend/PE-FE-BL-01.md`
- `tasks/postenhancement/backend/PE-BE-BL-02.md`
- `tasks/postenhancement/frontend/PE-FE-BL-02.md`
- `tasks/postenhancement/backend/PE-BE-BL-03.md`
- `tasks/postenhancement/frontend/PE-FE-BL-03.md`
- `tasks/postenhancement/backend/PE-QA-B4-01.md`

## Batch 4 Agent-to-Task Mapping

| Role | Task ID | Task File | Outcome |
|---|---|---|---|
| `worker` | `PE-BE-BL-01` | `tasks/postenhancement/backend/PE-BE-BL-01.md` | `PASS` |
| `worker` | `PE-FE-BL-01` | `tasks/postenhancement/frontend/PE-FE-BL-01.md` | `PASS` |
| `worker` | `PE-BE-BL-02` | `tasks/postenhancement/backend/PE-BE-BL-02.md` | `PASS` |
| `worker` | `PE-FE-BL-02` | `tasks/postenhancement/frontend/PE-FE-BL-02.md` | `PASS` |
| `worker` | `PE-BE-BL-03` | `tasks/postenhancement/backend/PE-BE-BL-03.md` | `PASS` |
| `worker` | `PE-FE-BL-03` | `tasks/postenhancement/frontend/PE-FE-BL-03.md` | `PASS` |
| `monitor` | `PE-QA-B4-01` | `tasks/postenhancement/backend/PE-QA-B4-01.md` | `PASS` |

## Batch 4 Execution Waves

### Wave 1

- Role: backend `worker`
- Task: `PE-BE-BL-01`
- Mode: serialized
- Result: `PASS`

### Wave 2

- Role: frontend `worker`
- Task: `PE-FE-BL-01`
- Mode: serialized
- Result: `PASS`

### Wave 3

- Role: backend `worker`
- Task: `PE-BE-BL-02`
- Mode: serialized
- Result: `PASS`

### Wave 4

- Role: frontend `worker`
- Task: `PE-FE-BL-02`
- Mode: serialized
- Result: `PASS`

### Wave 5

- Role: backend `worker`
- Task: `PE-BE-BL-03`
- Mode: serialized
- Result: `PASS`

### Wave 6

- Role: frontend `worker`
- Task: `PE-FE-BL-03`
- Mode: serialized
- Result: `PASS`

### Wave 7

- Role: `monitor`
- Task: `PE-QA-B4-01`
- Mode: serialized
- Result: `PASS`

## Batch 4 Partially Implemented Repair Matrix

| Item | Final Result | Evidence-backed Outcome | Status |
|---|---|---|---|
| `US-BL-02 / FR-BL-01 / FR-BL-03` | manual bill contract and form parity | backend manual-bill contract + frontend AR/AP/manual payload mapping completed | `covered` |
| `US-BL-06 / FR-BL-07 / FR-BL-08` | bad-debt / dunning visibility | backend dunning detail endpoint + frontend detail visibility completed; no document generation added | `covered` |
| `US-BL-07 / FR-BL-09` | prepayment / offset visibility | payment read-path exposes allocation progress and frontend payment visibility shows prepayment state and unapplied amount | `covered` |

## Batch 4 Detailed Changes

### Backend

Modified files:
- `backend/app/modules/billing/api.py`
- `backend/app/modules/billing/service.py`
- `backend/app/modules/billing/schemas.py`
- `backend/app/modules/collections/api.py`
- `backend/app/modules/collections/service.py`
- `backend/tests/test_b5_billing_polish.py`
- `backend/tests/test_collections_e2e.py`

Change description:
- hardened `POST /bills/manual` for typed item rows, AR/AP direction, and deterministic status handling
- added `GET /dunning/{id}` to expose one dunning batch head plus `DunningLine` detail rows
- enriched `GET /payments` with prepayment allocation progress (`allocated_amt`, `unapplied_amt`, `line_count`, `prepayment_status`)
- added focused regression coverage for manual bill creation, dunning detail visibility, and payment prepayment progress after offset/reverse-offset

Intended diff scope:
- Batch 4 billing / collections read-path and contract slices only

### Frontend

Modified files:
- `frontend/src/modules/billing/pages/BillCreate.vue`
- `frontend/src/modules/billing/pages/PaymentCreate.vue`
- `frontend/src/modules/billing/pages/PaymentList.vue`
- `frontend/src/modules/collections/pages/DunningDetail.vue`
- `frontend/src/api/billing.ts`
- `frontend/src/api/billing.types.ts`
- `frontend/src/api/collections.ts`
- `frontend/src/api/collections.types.ts`

Change description:
- aligned BillCreate manual mode with AR/AP direction and manual item-row backend contract
- switched DunningDetail to the dedicated dunning detail endpoint instead of scanning paginated list results
- surfaced payment prepayment status and unapplied amount in PaymentList
- added minimal PaymentCreate guidance so newly registered payments are understood as prepayments until offset allocation

Intended diff scope:
- Batch 4 manual-bill, dunning-detail, and prepayment-visibility slices only

## Batch 4 Validation Results

### Implementation task gates

- `./scripts/task_validate.sh PE-BE-BL-01` -> `PASS`
- `./scripts/task_validate.sh PE-FE-BL-01` -> `PASS`
- `./scripts/task_validate.sh PE-BE-BL-02` -> `PASS`
- `./scripts/task_validate.sh PE-FE-BL-02` -> `PASS`
- `./scripts/task_validate.sh PE-BE-BL-03` -> `PASS`
- `./scripts/task_validate.sh PE-FE-BL-03` -> `PASS`

### Batch-level validation

- `cd backend && pytest -q tests/test_b5_billing_polish.py tests/test_collections_e2e.py`
- result: `15 passed`
- `cd frontend && npm run lint`
- result: `passed`
- `cd frontend && npm run typecheck`
- result: `passed`

## Batch 4 QA Item-to-Slice Ledger

| Item | Required Slices | Implemented Task IDs | Evidence | Residual Gap | Close Decision |
|---|---|---|---|---|---|
| `US-BL-02` | manual bill backend + frontend | `PE-BE-BL-01`, `PE-FE-BL-01` | task artifacts + manual-bill tests | none | `covered` |
| `FR-BL-01` | manual bill header/detail/status semantics | `PE-BE-BL-01`, `PE-FE-BL-01` | task artifacts + manual-bill tests | none for Batch 4 narrowed scope | `covered` |
| `FR-BL-03` | manual AR/AP bill creation | `PE-BE-BL-01`, `PE-FE-BL-01` | task artifacts + manual-bill tests | none | `covered` |
| `US-BL-06` | bad-debt / dunning visibility slice | `PE-BE-BL-02`, `PE-FE-BL-02` | dunning detail endpoint + frontend detail visibility | none | `covered` |
| `FR-BL-07` | bad-debt distinction in billing visibility | `PE-BE-BL-02`, `PE-FE-BL-02` | dunning detail endpoint + close audit | none for Batch 4 narrowed scope | `covered` |
| `FR-BL-08` | dunning batch + line visibility without letter generation | `PE-BE-BL-02`, `PE-FE-BL-02` | dunning detail endpoint + detail page visibility | document generation intentionally excluded | `covered` |
| `US-BL-07` | prepayment / allocation progress visibility | `PE-BE-BL-03`, `PE-FE-BL-03` | payment list progress regression + frontend visibility | none | `covered` |
| `FR-BL-09` | prepayment state and later offset deduction visibility | `PE-BE-BL-03`, `PE-FE-BL-03` | payment list progress regression + frontend visibility | none | `covered` |

QA ledger conclusion:
- every in-scope Batch 4 item has a close decision
- no unresolved residual gap remains for Batch 4 `complete`
- document generation remained explicitly excluded

## Batch 4 Residual Risks / Blockers

- No functional blocker remains for Batch 4 close.
- Frontend confidence still relies on lint/typecheck and API-aligned visibility slices, not full browser replay.
- Payment create/detail UX is intentionally kept minimal; no broader redesign was introduced beyond the approved exact closure slices.

## Batch 4 Ready-for-Merge Checklist

- [x] Batch 4 stayed inside Cluster C5 scope
- [x] No Batch 5 work started
- [x] No document-generation implementation
- [x] Shared ownership stayed serialized
- [x] Dirty baseline was handled by scoped evidence
- [x] All Batch 4 implementation task gates passed
- [x] Batch 4 close audit passed
- [x] Item-to-slice ledger completed

## Batch 4 Next Steps

- Start any further work from `Batch 5` planning / freeze / manifest conversion only.
- Do not reopen Batch 4 unless a new explicit atomic task is approved.

## Batch 4 Stop Line

Stopped after Batch 4.
Batch 4 complete, Batch 5 not started.

## Batch 2 Covered Scope

Execution baseline:
- `docs/FPMS_Final_Enhancement_Plan_Native_20260315.md`
- `docs/FPMS_Code_Review_Report_SPEC_2.0_20260227.md`
- `docs/FPMS_Final_Enhancement_Plan_and_Task_Breakdown_SPEC_2.0_20260228.md`

Batch 2 manifest:
- `tasks/postenhancement/BATCH2_DOCS_TASKS_MANIFEST_20260315.md`
- `tasks/postenhancement/BATCH2_REMAINING_MANIFEST_20260316.md`

Atomic task files executed in this run:
- `tasks/postenhancement/backend/PE-BE-WD-02.md`
- `tasks/postenhancement/frontend/PE-FE-WD-02.md`
- `tasks/postenhancement/backend/PE-BE-DL-02.md`
- `tasks/postenhancement/frontend/PE-FE-DL-02.md`
- `tasks/postenhancement/backend/PE-BE-WD-03.md`
- `tasks/postenhancement/frontend/PE-FE-WD-03.md`
- `tasks/postenhancement/backend/PE-BE-DL-03.md`
- `tasks/postenhancement/frontend/PE-FE-DL-03.md`
- `tasks/postenhancement/backend/PE-QA-B2-02.md`
- `tasks/postenhancement/backend/PE-QA-B2-01.md`

Task-level outcome:
- `PE-BE-WD-02` -> `PASS`
- `PE-FE-WD-02` -> `PASS`
- `PE-BE-DL-02` -> `PASS`
- `PE-FE-DL-02` -> `PASS`
- `PE-BE-WD-03` -> `PASS`
- `PE-FE-WD-03` -> `PASS`
- `PE-BE-DL-03` -> `PASS`
- `PE-FE-DL-03` -> `PASS`
- `PE-QA-B2-01` -> `FAIL` for earlier batch close audit
- `PE-QA-B2-02` -> `PASS` for final batch close audit

Covered slices:
- Documents backend:
  - document-driven case status transition guard
  - `/documents` reply-state query filters (`need_reply`, `replied`)
  - create/get/update responses now carry `case_no`
  - update flow now reapplies template-backed defaults
  - reply templates can apply `status_restore`
- Documents frontend:
  - advanced document list filters (keyword, template, date range, reply state)
  - case-context-aware document create flow
  - template-rule visibility in create / edit / detail views
- Tasks backend:
  - manual task delete API/service
  - 204 no-body contract fix for delete route
  - `/tasks?as=worker|supervisor` current-user role view
  - `/tasks/today` enriched output with `case_no`, `client_name`, timestamps
- Tasks frontend:
  - manual task delete wiring in task list and task detail
  - task list role-view toggle
  - today reminders richer metadata display
  - dashboard `TodoTable` wired to today's tasks

## Batch 2 Agent-to-Task Mapping

| Role | Task ID | Task File | Outcome |
|---|---|---|---|
| `worker` | `PE-BE-WD-02` | `tasks/postenhancement/backend/PE-BE-WD-02.md` | `PASS` |
| `worker` | `PE-FE-WD-02` | `tasks/postenhancement/frontend/PE-FE-WD-02.md` | `PASS` |
| `worker` | `PE-BE-DL-02` | `tasks/postenhancement/backend/PE-BE-DL-02.md` | `PASS` |
| `worker` | `PE-FE-DL-02` | `tasks/postenhancement/frontend/PE-FE-DL-02.md` | `PASS` |
| `worker` | `PE-BE-WD-03` | `tasks/postenhancement/backend/PE-BE-WD-03.md` | `PASS` |
| `worker` | `PE-FE-WD-03` | `tasks/postenhancement/frontend/PE-FE-WD-03.md` | `PASS` |
| `worker` | `PE-BE-DL-03` | `tasks/postenhancement/backend/PE-BE-DL-03.md` | `PASS` |
| `worker` | `PE-FE-DL-03` | `tasks/postenhancement/frontend/PE-FE-DL-03.md` | `PASS` |
| `monitor` | `PE-QA-B2-01` | `tasks/postenhancement/backend/PE-QA-B2-01.md` | `FAIL` for earlier close audit |
| `monitor` | `PE-QA-B2-02` | `tasks/postenhancement/backend/PE-QA-B2-02.md` | `PASS` |

## Batch 2 Execution Waves

### Wave 1

- Role: backend `worker`
- Task: `PE-BE-WD-02`
- Mode: serialized
- Result: `PASS`

### Wave 2

- Role: frontend `worker`
- Task: `PE-FE-WD-02`
- Mode: serialized
- Result: `PASS`

### Wave 3

- Role: backend `worker`
- Task: `PE-BE-DL-02`
- Mode: serialized
- Result: `PASS`

### Wave 4

- Role: frontend `worker`
- Task: `PE-FE-DL-02`
- Mode: serialized
- Result: `PASS`

### Wave 5

- Role: `monitor`
- Task: `PE-QA-B2-01`
- Mode: serialized
- Result: `FAIL` for batch close

### Wave 6

- Role: backend `worker`
- Task: `PE-BE-DL-03`
- Mode: serialized
- Result: `PASS`

### Wave 7

- Role: frontend `worker`
- Task: `PE-FE-DL-03`
- Mode: serialized
- Result: `PASS`

### Wave 8

- Role: backend `worker`
- Task: `PE-BE-WD-03`
- Mode: serialized
- Result: `PASS`

### Wave 9

- Role: frontend `worker`
- Task: `PE-FE-WD-03`
- Mode: serialized
- Result: `PASS`

### Wave 10

- Role: `monitor`
- Task: `PE-QA-B2-02`
- Mode: serialized
- Result: `PASS`

## Batch 2 Repair Matrix

| Item Cluster | Current Batch 2 Result | Evidence-backed Outcome | Status |
|---|---|---|---|
| Documents defaults | complete | template-backed defaults now visible in FE and applied in backend update/create response flow | `covered` |
| Documents reply/deadline linkage | complete | reply chain, status restore, task/fee linkage regression all green | `covered` |
| Documents query capability | complete | advanced FE filters + BE reply-state filters landed | `covered` |
| Tasks manual maintenance | complete | create/list/detail/update/delete chain available; delete path regression-proven | `covered` |
| Tasks worker/supervisor views | complete | current-user role views landed in BE/FE list and today flows | `covered` |
| Tasks today reminders/dashboard entry | complete | today reminders enriched and dashboard TodoTable wired | `covered` |

## Batch 2 Validation Results

- `./scripts/task_validate.sh PE-BE-WD-02` -> `PASS`
- `./scripts/task_validate.sh PE-FE-WD-02` -> `PASS`
- `./scripts/task_validate.sh PE-BE-DL-02` -> `PASS`
- `./scripts/task_validate.sh PE-FE-DL-02` -> `PASS`
- `./scripts/task_validate.sh PE-BE-WD-03` -> `PASS`
- `./scripts/task_validate.sh PE-FE-WD-03` -> `PASS`
- `./scripts/task_validate.sh PE-BE-DL-03` -> `PASS`
- `./scripts/task_validate.sh PE-FE-DL-03` -> `PASS`
- `./scripts/task_validate.sh PE-QA-B2-02` -> `PASS`
- `cd backend && pytest -q tests/test_task_template.py -k 'today_returns_enriched_fields_and_role_filtered or current_user_role_view'` -> `2 passed`
- `cd backend && pytest -q tests/test_b2_reply_chain.py -k 'case_no or template_defaults or status_restore'` -> `2 passed`
- `cd backend && pytest -q tests/test_task_template.py tests/test_b2_reply_chain.py` -> `25 passed`
- `cd backend && pytest -q tests/test_b2_reply_chain.py tests/test_b3_fee_linking.py tests/test_task_template.py` -> `34 passed`
- `cd frontend && npm run lint` -> `PASS`
- `cd frontend && npm run typecheck` -> `PASS`

Batch 2 evidence:
- `artifacts/PE-BE-WD-02/**`
- `artifacts/PE-FE-WD-02/**`
- `artifacts/PE-BE-DL-02/**`
- `artifacts/PE-FE-DL-02/**`
- `artifacts/PE-BE-WD-03/**`
- `artifacts/PE-FE-WD-03/**`
- `artifacts/PE-BE-DL-03/**`
- `artifacts/PE-FE-DL-03/**`
- `artifacts/PE-QA-B2-02/**`

## Batch 2 Residual Risks / Blockers

- No functional blocker remains for Batch 2 closure.
- No browser/manual FE smoke was run for documents/tasks/dashboard flows; FE confidence is based on lint/typecheck and backend/API regression.
- Dirty worktree contamination remains a review hygiene risk, but task-scoped diffs and gates for the Batch 2 remaining tasks passed.
- No `document generation` implementation was added in this run.

## Batch 2 Ready-for-Merge Checklist

- [x] Execution stayed inside Batch 2
- [x] No Batch 3 work started
- [x] No document-generation implementation added
- [x] All Batch 2 remaining task gates passed
- [x] Batch 2 minimal regression gate passed
- [x] Batch 2 fully closed against all 21 Partially Implemented items
- [x] Batch 2 close audit passed

## Batch 2 Next Steps

- Batch 2 is complete.
- Start any further work from Batch 3 planning / manifest conversion only.
