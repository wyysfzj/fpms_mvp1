# Documents Step1-2 Wizard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Step 1-2 intermediate document wizard so users can parse multiple cases, edit per-case rows using the current document contract, and batch-create documents.

**Architecture:** Add a wizard-specific batch-create backend contract, then implement a dedicated frontend wizard page in serialized slices: shell, Step 1 parsing, and Step 2 editing/submission. Reuse existing document creation side effects but do not expose Step 3-5 UI. Step 2 is explicitly narrowed to fields already supported by the current documents contract.

**Tech Stack:** FastAPI, SQLAlchemy, Vue 3, Element Plus, TypeScript

---

## Story Shape Classification

- `shared_file_density`: `medium-high`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `chained (BE -> FE)`
- `evidence_cost`: `high`
- `chosen_runbook`: `P0-frontend-heavy-story`

## Batch Manifest

| Task ID | Role | Wave | Closure Slice | Shared Files |
|---|---|---|---|---|
| `DOCWIZ-BE-01` | `worker` | 1 | 向导批量创建 contract 与服务编排 | `backend/app/modules/documents/api.py`, `backend/app/modules/documents/schemas.py`, `backend/app/modules/documents/service.py` |
| `DOCWIZ-FE-SHELL-01` | `worker` | 2 | 向导页面壳、stepper、内存状态容器 | `frontend/src/router/index.ts`, `frontend/src/api/documents.ts`, `frontend/src/api/documents.types.ts`, `frontend/src/modules/documents/pages/DocumentWizard.vue` |
| `DOCWIZ-FE-STEP1-01` | `worker` | 3 | Step 1 案件逐行解析与错误回显 | `frontend/src/api/documents.ts`, `frontend/src/api/documents.types.ts`, `frontend/src/modules/documents/pages/DocumentWizard.vue` |
| `DOCWIZ-FE-STEP2-01` | `worker` | 4 | Step 2 逐案编辑与批量提交 | `frontend/src/api/documents.ts`, `frontend/src/api/documents.types.ts`, `frontend/src/modules/documents/pages/DocumentWizard.vue` |
| `DOCWIZ-QA-01` | `monitor` | 5 | item-to-slice ledger 与故事收口 | `artifacts/DOCWIZ-QA-01/**` |

## Serialized Ownership

- `backend/app/modules/documents/api.py|schemas.py|service.py` 全程串行。
- `frontend/src/api/documents.ts|documents.types.ts` 全程串行。
- `frontend/src/modules/documents/pages/DocumentWizard.vue` 由三个 FE 任务串行编辑。

## Task Notes

### Task 1: `DOCWIZ-BE-01`

- Add a failing test covering batch create success and validation failure.
- Add wizard request/response schemas for:
  - batch defaults
  - per-row payloads
  - created-row summaries
- Implement one wizard batch-create endpoint in `documents/api.py`.
- Implement minimal service orchestration that validates rows, reuses existing document creation logic, and returns created summaries.
- Run:
  - `ruff check backend/app/modules/documents/api.py backend/app/modules/documents/schemas.py backend/app/modules/documents/service.py backend/tests/test_document_wizard_batch_create.py`
  - `cd backend && pytest -q tests/test_document_wizard_batch_create.py`
  - `./scripts/task_validate.sh DOCWIZ-BE-01`

### Task 2: `DOCWIZ-FE-SHELL-01`

- Add the failing FE type/lint checks after introducing a wizard page shell.
- Add route entry for the wizard page.
- Add API/type stubs for the wizard contract without Step 1/Step 2 details.
- Build the page shell with:
  - stepper header
  - shared batch defaults model
  - in-memory wizard state container
  - next/back navigation shell
- Run:
  - `cd frontend && npm run lint -- src/router/index.ts src/api/documents.ts src/api/documents.types.ts src/modules/documents/pages/DocumentWizard.vue`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh DOCWIZ-FE-SHELL-01`

### Task 3: `DOCWIZ-FE-STEP1-01`

- Add failing FE coverage via type/lint-driven state usage and local parsing helpers.
- Implement Step 1 UI:
  - multiline case input
  - `DocType / Template / DispatchDate`
  - parse results and per-line errors
  - step gate requiring at least one valid case
- Keep parsing client-side using an explicit lookup API or existing case query if available; if not available, this task must stop and return to planning for a backend prerequisite.
- Run:
  - `cd frontend && npm run lint -- src/api/documents.ts src/api/documents.types.ts src/modules/documents/pages/DocumentWizard.vue`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh DOCWIZ-FE-STEP1-01`

### Task 4: `DOCWIZ-FE-STEP2-01`

- Add failing FE coverage for row editing and batch submission state.
- Implement Step 2 UI:
  - editable row table
  - narrowed field set: `title / doc_date / ref_no / need_reply / reply_to_id / extra_data`
  - `extra_data` text area for summary / remark / simple supplemental text
  - batch submit button
  - success/error feedback
- Wire submit to the wizard batch endpoint.
- Run:
  - `cd frontend && npm run lint -- src/api/documents.ts src/api/documents.types.ts src/modules/documents/pages/DocumentWizard.vue`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh DOCWIZ-FE-STEP2-01`

### Task 5: `DOCWIZ-QA-01`

- Build item-to-slice ledger and evidence audit.
- Confirm all four implementation tasks are PASS.
- Run:
  - `./scripts/task_validate.sh DOCWIZ-BE-01`
  - `./scripts/task_validate.sh DOCWIZ-FE-SHELL-01`
  - `./scripts/task_validate.sh DOCWIZ-FE-STEP1-01`
  - `./scripts/task_validate.sh DOCWIZ-FE-STEP2-01`
  - `./scripts/task_validate.sh DOCWIZ-QA-01`

## Acceptance / Test Scenarios

- Batch wizard can create documents for multiple valid cases in one submit.
- Invalid input lines remain visible with error text and do not wipe valid rows.
- Step 2 cannot submit rows missing required minimum fields.
- Existing single-document create/list/detail pages keep working.
- All new UI text remains Simplified Chinese.

## Assumptions

- `DocTemplate.input_fields` are not rendered as structured dynamic fields in this story.
- Existing document create side effects are acceptable for Step 1-2 completion.
- If case lookup by case number/application number lacks a reusable API, implementation must stop and return to planning rather than silently overextending another task.
