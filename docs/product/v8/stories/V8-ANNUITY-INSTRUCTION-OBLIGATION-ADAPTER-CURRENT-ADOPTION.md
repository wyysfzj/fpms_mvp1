# Story V8-ANNUITY-INSTRUCTION-OBLIGATION-ADAPTER-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Outcome: current-adopt the frozen Task-121 annuity-task instruction adapter on the lean
  integrated tree.
- Catalog ID: `FPMS-V8-ANNUITY-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01` (ordinal `121`).
- Authority: the exact task's Delta-4 latest-wins appendix, accepted
  `V8-FUTURE-ANNUITY-OBLIGATION-CURRENT-ADOPTION`, and current-verified
  `V8-FEE-CLIENT-INSTRUCTION-RECOGNITION-LINK-CORRECTION`.

## Current prerequisites and exact paths

- The D4-11 six-field annuity-task carrier and Task-133 sourced Future Annuity obligation
  seam are current-adopted.
- The row-107 client-instruction service is current-verified for the Task-133 recognition
  child/source-activity shape on both first write and exact replay.
- `backend/app/modules/annuity/service.py`
- `backend/tests/test_v8_annuity_instruction_obligation_adapter.py`

## Observable contract

The adapter accepts exactly `annuity_task_id`, `instruction`, `actor_id`, and
`idempotency_key`. It accepts only exact `PAY`, `HOLD`, and `ABANDON`, resolves only the
named persisted task and its exact obligation, validates the complete six-field carrier
and the same-case Task-133 obligation/recognition/document/evidence identities, then
delegates once to `record_client_instruction()` without changing the actor or key.

Missing task/link/cardinality facts fail with the accepted 404 partition. Partial or
malformed carrier facts, cross-case/type/year/source/document/evidence contradictions and
replay drift fail with the accepted 409 partition before delegation or mutation. Exact
replay reuses the original deep result and activity; a changed same-key fact or a new key
for the current instruction remains 409. The caller owns the transaction.

## Test provenance and current verification state

The focused 17-named-test acceptance matrix is freshly derived from the frozen Delta-4
contract and the two accepted current prerequisite stories. It is not represented as an
archive-byte restoration: the earlier uncommitted transient test was never accepted
authority and is not present in the repository object graph. The current matrix covers
strict command validation, identity-preserving mapping, exact task selection,
link/cardinality and lineage fail-closed behavior, deep replay/conflict preservation,
caller rollback, empty instruction evidence, and non-mutation of legacy annuity-task
fields.

The first controller-granted focused SQLite RED produced `45 failed`: the public
command/result/callable were absent, and the new fixture also exposed a client-before-case
flush ordering defect. The fixture was corrected before product implementation. The
minimum local adapter then produced `45 passed` with one inherited passlib `crypt`
deprecation warning. Scoped Ruff and exact diff checks passed. Independent High review,
ledger/review updates and commit remain pending.

## Non-goals and rollback

No deep fee-service rule, Task-133 writer, carrier/schema/migration, API/UI, source/rate or
reduction fact, legacy `client_instruction`, lifecycle/status, draft, payment, evidence,
document, PayList, task/ledger/review/artifact, broad test or unrelated cleanup is changed.
Rollback removes only this story card and the Task-121 focused test until product
implementation is separately authorized.
