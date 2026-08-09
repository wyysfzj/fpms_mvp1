# Story V8-FEE-CLIENT-INSTRUCTION-RECOGNITION-LINK-CORRECTION

- Risk: `PROTECTED`
- Outcome: restore the accepted row-107 client-instruction contract for obligations whose
  durable source activity is the source of their unique recognition activity, rather than
  the recognition activity itself.
- Successor to: `FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01` (ordinal `107`, profile
  `TC-SERVICE`).
- Authority: the exact accepted row-107 task contract and the current Task-133 Future
  Annuity obligation shape.

## Exact correction

`_instruction_recognition` continues to require exactly one same-case `FEE` activity of
type `FEE_OBLIGATION_RECOGNIZED` whose canonical
`FPMS_FEE_OBLIGATION_RECOGNIZED_V1` payload names the obligation. It no longer rejects that
unique payload-linked recognition merely because its activity ID differs from the
obligation header's `source_activity_id`.

This permits the Task-133 lineage shape: the obligation header and line retain the grant
source activity, while the recognition is a child whose `source_activity_id` names that
grant source. A new client instruction still names the unique recognition activity as its
own source.

## Exact paths and verification

- `backend/app/modules/fees/obligation_service.py`
- `backend/tests/test_v8_fee_obligation_instruction.py`
- `docs/product/v8/stories/V8-FEE-CLIENT-INSTRUCTION-RECOGNITION-LINK-CORRECTION.md`

The focused regression constructs the Task-133 linkage and requires instruction recording
to succeed with the recognition activity as the instruction source. Existing malformed,
duplicate, stored-chain, replay, race and no-side-effect assertions remain unchanged; the
same-case filter continues to reject cross-linked recognition. Run the focused instruction
test and scoped Ruff check-only under the controller-granted serialized SQLite lane,
followed by exact diff inspection and independent High review of the exact commit.

## Non-goals and rollback

No recognition cardinality, canonical-payload, same-case, lane, activity-type, stored-chain,
replay or instruction-source rule changes; no Task-133 writer change; no API/UI,
schema/migration/seed, source activation, fee amount, deadline, legal status, customer
policy, ledger/disposition/review, old task/evidence, broad test or adjacent cleanup.

Rollback reverts only this story's service predicate, targeted regression and story card.
