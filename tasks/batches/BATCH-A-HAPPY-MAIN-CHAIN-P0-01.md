# BATCH-A-HAPPY-MAIN-CHAIN-P0-01

## Batch ID

- Batch manifest path: `tasks/batches/BATCH-A-HAPPY-MAIN-CHAIN-P0-01.md`
- Batch ID: `BATCH-A-HAPPY-MAIN-CHAIN-P0-01`
- Role: lead / worker coordinator
- chosen_runbook: `P0-prereq-heavy-story`

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: high
- chosen_runbook: `P0-prereq-heavy-story`

## Batch Goal

Serialize A wave Happy main chain P0 automation:

1. `A-AUTO-PY-A-BATCH-SUBMIT-P0-01` / `TC-A-011`
2. `A-AUTO-PY-A-APPLY-FEE-LIMIT-P0-01` / `TC-A-013`
3. `A-AUTO-PY-A-APPLY-FEE-DRAFT-P0-01` / `TC-A-015`
4. `A-AUTO-PY-A-GOV-PAYLIST-P0-01` / `TC-A-017`
5. `A-AUTO-PY-A-APPLY-BILL-P0-01` / `TC-A-019`
6. `A-AUTO-PY-A-PAYMENT-OFFSET-P0-01` / `TC-A-021`
7. `A-AUTO-PY-A-COMMISSION-P0-01` / `TC-A-023`

## Shared File Serialization

- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py` must be edited serially.
- Existing A handler regression tests may only be changed for explicit stale skeleton-state assertions when allowlisted by the atomic task.
- Automation tasks must not modify backend or frontend files.

## Wave 0 Discovery Result

`TC-A-011` is currently blocked for full closure:

- Present backend support:
  - `GET /api/v1/cases/batch-filing/candidates`
  - `POST /api/v1/cases/batch-filing/submit`
  - selected cases can move from `NOT_FILED` to `WAITING_RECEIPT`
  - `apply_exam_now` sets `has_exam_request`
- Missing / explicitly not supported in current product surface:
  - submission list document generation
  - `T_Document` / `T_DocAttachment` registration for the batch submit action
  - automatic application-fee deadline task generation after batch filing
- Evidence source:
  - `frontend/src/modules/cases/pages/CaseBatchFiling.vue` states the first version does not generate the submission list document and does not auto-generate application-fee deadline tasks.
  - `backend/app/modules/cases/service.py::execute_batch_filing` only updates case status/submitted date/exam request.

Because `TC-A-013` depends on the application-fee deadline task being generated after filing, downstream Happy main-chain automation should not proceed as PASS until the backend submit side-effect contract is implemented.

## Per-Task Closure / Non-Closure

### `A-AUTO-PY-A-BATCH-SUBMIT-P0-01`

- Exact closure: `TC-A-011` batch filing happy path, including status transition, exam-request effect, submission list document registration, and trigger path for application-fee task generation.
- Non-closure: does not implement `TC-A-013` deadline assertions or later fee/billing/payment/commission tasks.
- Current status: `BLOCKED`.
- Follow-up: `BE-A-BATCH-SUBMIT-SIDE-EFFECTS-01`.

### `A-AUTO-PY-A-APPLY-FEE-LIMIT-P0-01`

- Exact closure: `TC-A-013` application-fee deadline task generation after submitted case.
- Non-closure: does not implement fee draft generation.
- Current status: not started because upstream `TC-A-011` side effects are blocked.
- Follow-up: `BE-A-APPLY-FEE-LIMIT-GENERATION-01` if not covered by the batch submit side-effects task.

### `A-AUTO-PY-A-APPLY-FEE-DRAFT-P0-01`

- Exact closure: `TC-A-015` application-fee draft generation and fee total assertions.
- Non-closure: no pay list, billing, payment, or commission assertions.
- Current status: pending upstream Happy-chain prerequisites.
- Follow-up: `BE-A-APPLY-FEE-DRAFT-RULE-01` if backend generation is missing.

### `A-AUTO-PY-A-GOV-PAYLIST-P0-01`

- Exact closure: `TC-A-017` official-fee pay list and payment happy path.
- Non-closure: no bill/payment-offset/commission assertions.
- Current status: pending upstream Happy-chain prerequisites.
- Follow-up: `BE-A-GOV-PAYLIST-PAYMENT-01` if backend support is incomplete.

### `A-AUTO-PY-A-APPLY-BILL-P0-01`

- Exact closure: `TC-A-019` application-fee AR bill generation.
- Non-closure: no customer payment or commission assertions.
- Current status: pending upstream Happy-chain prerequisites.
- Follow-up: `BE-A-APPLY-BILL-GENERATION-01` if backend support is incomplete.

### `A-AUTO-PY-A-PAYMENT-OFFSET-P0-01`

- Exact closure: `TC-A-021` payment and offset happy path.
- Non-closure: no over-offset or unhappy validation.
- Current status: pending upstream Happy-chain prerequisites.
- Follow-up: `BE-A-PAYMENT-OFFSET-01` if backend support is incomplete.

### `A-AUTO-PY-A-COMMISSION-P0-01`

- Exact closure: `TC-A-023` commission generation and available-to-settle entry.
- Non-closure: no commission settlement execution.
- Current status: pending upstream Happy-chain prerequisites.
- Follow-up: `BE-A-COMMISSION-GENERATION-01` if backend support is incomplete.

## Verification Commands

Wave 0 / blocker evidence:

```bash
rg -n "batch-filing|execute_batch_filing|APPLY_FEE_LIMIT|第一版不生成递交清单文档" backend/app frontend/src FPMS_Automation_Skeleton_Pack/data
./scripts/task_validate.sh BATCH-A-HAPPY-MAIN-CHAIN-P0-01
```

## Evidence Path

- `artifacts/BATCH-A-HAPPY-MAIN-CHAIN-P0-01/`

## Remaining Follow-Up Task IDs

- `BE-A-BATCH-SUBMIT-SIDE-EFFECTS-01`
- `BE-A-APPLY-FEE-LIMIT-GENERATION-01`
- `A-AUTO-PY-A-BATCH-SUBMIT-P0-01`
- `A-AUTO-PY-A-APPLY-FEE-LIMIT-P0-01`
- `A-AUTO-PY-A-APPLY-FEE-DRAFT-P0-01`
- `A-AUTO-PY-A-GOV-PAYLIST-P0-01`
- `A-AUTO-PY-A-APPLY-BILL-P0-01`
- `A-AUTO-PY-A-PAYMENT-OFFSET-P0-01`
- `A-AUTO-PY-A-COMMISSION-P0-01`
