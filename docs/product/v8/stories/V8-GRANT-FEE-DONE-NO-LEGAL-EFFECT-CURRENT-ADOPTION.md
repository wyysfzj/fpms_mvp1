# Story V8-GRANT-FEE-DONE-NO-LEGAL-EFFECT-CURRENT-ADOPTION

- Status: `READY_FOR_INDEPENDENT_REVIEW`.
- Risk: `PROTECTED`.
- Catalog ID: `FPMS-V8-GRANT-FEE-DONE-NO-GRANTED-20260712-01` (ordinal `76`).
- Product/test commit: `bd73ceb851e7b4b4b8ba87a9914eeac283079d53`.
- Parent: `541d25397bd285985b14b4b5c6a09feca15e5cbd`.
- Authority: frozen Row76 task, lifecycle activity append contract, and current-verified
  Row74 grant-notice lifecycle adapter.

## Exact outcome and scope

`mark_done` no longer writes `Case.status = GRANTED`. In the same service transaction it
appends exactly one confirmed `GRANT_FEE_TASK_DONE` activity in the `FEE` lane with
`center_changes={}` and deterministic key `grant-fee-task:{task_id}:done`. The activity
preserves the business-stage, official-procedure, legal-status, verification-status and
legacy-status values on both sides; the shared activity sequence and
`lifecycle_revision` correctly advance by one.

The actor is resolved only from `task.updated_by or task.created_by`. Missing, malformed
or over-length audit identity fails closed with HTTP-domain code
`GRANT_FEE_TASK_DONE_ACTOR_REQUIRED` and Simplified Chinese text. No client, evidence or
system fallback is invented. Append or commit failure rolls back the task mutation, case
revision and activity together.

Exact product/test paths:

- `backend/app/modules/grant_fees/service.py`
- `backend/tests/test_v8_grant_fee_done_no_legal_effect.py`

No Row74 dispatcher/API behavior, grant-announcement legal transition, obligation/draft,
fee amount, schema/migration, endpoint or UI is changed.

## TDD and verification

- final real RED: `3 failed`; it proved old `Case.status = GRANTED`, absent FEE activity,
  absent actor gate and absent injected-append rollback;
- focused GREEN: `3 passed`;
- current Row74 dependency plus Row75 tranche: `74 passed` after the Row76 product change;
- two nearest inherited files: `10 passed, 9 failed`; all nine failures stopped before
  Row76 code at the known CaseCreate fixture baseline because `fee_reduction` was absent;
- scoped Ruff check, format check and exact diff-check: PASS.

Independent High review must inspect `bd73ceb`, rerun the exact Row76 focused test and an
appropriate current Row74 dependency tranche under the serialized SQLite lane, and
approve with P0/P1/P2 zero before ledger adoption.

## Rollback

Rollback reverts only `bd73ceb` and this story. It restores the prohibited `mark_done ->
GRANTED` shortcut and therefore must not be used after Row76 adoption without explicitly
reopening the fee/lifecycle contract.
