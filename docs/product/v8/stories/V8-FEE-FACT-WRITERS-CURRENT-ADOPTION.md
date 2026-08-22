# Story V8-FEE-FACT-WRITERS-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Outcome: prove on the current lean tree that the already-integrated fee-reduction
  approval writer and fee-obligation client-instruction writer satisfy their exact frozen
  contracts.
- Change mode: current adoption only; no product or test byte changes because both
  untouched focused tests and all named inherited regressions pass.
- Authority: the fee, source-provenance, evidence-lineage, customer-decision and SQLite
  rules in `docs/product/v8/domain-contract.md`; the no-default/no-source-activation rules
  in `docs/product/v8/source-decision-registry.md`; frozen catalog rows `94` and `107`;
  and their exact task contracts.
- Archive comparison anchors:
  `83d014f` for the original implementation and `6b2ef89` for the later pre-lean
  checkpoint.
- Base: `745d376e8d42934d83abea18b0e53e849217a7df`.

## Catalog IDs and dependencies

1. `FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01` (ordinal `94`,
   profile `TC-SERVICE`) depends on:
   - `FPMS-V8-W1-F5-FEE-REDUCTION-APPROVAL-CARRIER-20260712-01`; and
   - `FPMS-V8-DE-REGISTER-VERSION-20260712-01`.
2. `FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01` (ordinal `107`, profile
   `TC-SERVICE`) depends on
   `FPMS-V8-FO-RECOGNIZE-OBLIGATION-20260712-01`.

The required F5 carrier, document-evidence registration/review behavior, fee-obligation
recognition seam and lifecycle append seam remain current prerequisites. This story does
not reactivate a source or absorb any successor row.

## Exact row-94 current boundary

`record_fee_reduction_approval` records or exactly reuses one immutable confirmed `CASE`
or canonical `APPLICANT_SET` approval. It accepts only exact typed values, the allowed
reduction ratios, a sorted explicit fee scope, valid year/date intervals, and strict
canonical JSON snapshots. It derives the canonical applicant-set, scope, snapshot and
approval identities without coercion or policy inference.

Creation requires the exact same-case source evidence version to be `FINAL`, `APPROVED`,
independently reviewed, content-hash matched and current for its lineage. Exact replay
remains valid after that evidence is no longer current, while any changed immutable
projection conflicts. Overlapping approvals are retained; no current/supersede state is
invented.

The write uses one nested savepoint and flush inside the caller-owned transaction. A
recognized unique race rereads and reuses only the exact winner. The service does not
commit, roll back or close the caller transaction.

The product and focused-test blobs are byte-identical on the current base, original
implementation anchor and later archive checkpoint:

- product: `8380e295ce79d1a162415624f1c3423f8dbbd6ee`;
- focused test: `5cde130c88745c269663dba68154a8b0d21abe19`.

## Exact row-107 current boundary

`record_client_instruction` records only `PAY`, `HOLD` or `ABANDON` against one recognized
fee obligation. Replay is checked before current eligibility, but it must reproduce the
same exact fact and valid stored activity chain. A new instruction is allowed only while
the obligation is recognized, has no draft, remains unpaid and lacks verified official
evidence. Requesting the current state conflicts.

Each new fact appends exactly one confirmed `FEE_CLIENT_INSTRUCTION_RECORDED` `FEE`
activity with the recognition source, the prior instruction activity as superseded fact,
an empty evidence set, one timestamp and an unchanged lifecycle projection. The same
nested savepoint then compare-and-swaps only the obligation's instruction and update
metadata. Race recovery never rolls back or retries the caller transaction.

`ABANDON` is an obligation instruction only. No instruction creates a draft, records
payment, verifies official evidence, or changes `Case.status`, business stage, official
procedure stage or legal status.

The focused test is byte-identical on the current base and both archive anchors:
`bd346ebe3013e647c7ded511cfdbd38c69c04d91`. The whole current shared service is
byte-identical to the original implementation anchor. The later archive contains
unrelated successor functions, so file-wide adoption is prohibited. The exact
`record_client_instruction` block and all `_instruction_*` helpers are nevertheless
byte-identical across current, original and later archive:

- public writer slice:
  `9fd6d95e7ba6b76454b1c6ea9f67d296926114b053f1d3c85ed048d33922c327`;
- helper slice:
  `973a3993772cbe04c02c34e3d3ea433610da18224b6ff859f10ea75d742c273d`.

## Exact paths

### Product verified unchanged

- `backend/app/modules/fees/fee_reduction_approval_service.py`
- `backend/app/modules/fees/obligation_service.py`

### Focused tests verified unchanged

- `backend/tests/test_v8_fee_reduction_approval_record.py`
- `backend/tests/test_v8_fee_obligation_instruction.py`

### Story

- `docs/product/v8/stories/V8-FEE-FACT-WRITERS-CURRENT-ADOPTION.md`

## Verification and review

Under the controller-granted serialized SQLite/shared lane, the untouched current tree
returned:

- row 94 focused: `66 passed, 1 warning`;
- row 94 named inherited regressions: `120 passed, 1 warning`;
- row 107 focused: `33 passed, 1 warning`; and
- row 107 named inherited regressions: `102 passed, 1 warning`.

The warning in each command is the existing third-party passlib `crypt` deprecation. The
lane was released immediately after the fourth command. Because both rows were already
GREEN, no RED was manufactured and no product or test bytes changed.

Run scoped Ruff check-only on the two exact product/test pairs, exact story-only
diff-check, and inspect the commit range and file list. An independent High reviewer must
review the exact commit and independently rerun the decisive checks under the serialized
lane. The implementer does not approve this `PROTECTED` story; it remains pending
independent review.

## Non-goals and rollback

No API/UI, schema/migration/seed, source activation, fee amount or deadline inference,
new reduction policy, official receipt verification, service-receivable rule,
draft/payment creation, case or legal-status implication, adjacent fee successor,
customer decision, ledger/disposition/review edit, old task/evidence mutation or
Foundation claim.

Rollback reverts only this story-card commit; the current product and test bytes remain
unchanged.
