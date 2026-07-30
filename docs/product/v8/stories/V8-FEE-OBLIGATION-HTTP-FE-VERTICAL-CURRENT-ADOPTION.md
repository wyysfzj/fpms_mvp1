# Story V8-FEE-OBLIGATION-HTTP-FE-VERTICAL-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Base: `08fd297bce682f3011b30add1918354db4e6d896`
- Outcome: expose the already accepted client-instruction writer and obligation-detail
  reader through their exact backend and frontend adapters while preserving separated fee
  states, decimal strings, permissions, caller-owned transactions and fail-closed errors.
- Authority: frozen catalog rows 108, 109, 111 and 112; their exact task contracts and
  preserved historical evidence; `docs/product/v8/domain-contract.md`; and
  `docs/product/v8/source-decision-registry.md`.
- Change mode: current-tree verification of rows 108–109 already present in the clean
  parent, exact archive-hunk adoption of rows 111–112, and one successor-only regression
  alignment for the new bodyless GET route.

## Catalog IDs and dependencies

1. `FPMS-V8-FO-INSTRUCTION-HTTP-20260712-01` (ordinal `108`)
2. `FPMS-V8-FO-INSTRUCTION-FE-ADAPTER-20260712-01` (ordinal `109`)
3. `FPMS-V8-FO-OBLIGATION-DETAIL-HTTP-20260712-01` (ordinal `111`)
4. `FPMS-V8-FO-OBLIGATION-DETAIL-FE-ADAPTER-20260712-01` (ordinal `112`)

Rows 107 and 110 are current verified and reachable from the base. Rows 108→109 and
108+110→111→112 are serialized in this story because the adapters share
`fees/api.py`, `obligation_schemas.py`, `fees.ts` and `fees.types.ts`.

## Exact product and test paths

- `backend/app/modules/fees/api.py`
- `backend/app/modules/fees/obligation_schemas.py`
- `backend/tests/test_v8_fee_obligation_instruction_api.py`
- `backend/tests/test_v8_fee_obligation_detail_api.py`
- `frontend/src/api/fees.ts`
- `frontend/src/api/fees.types.ts`
- `frontend/src/api/contracts/v8_fee_obligation_instruction.contract.ts`
- `frontend/src/api/contracts/v8_fee_obligation_detail.contract.ts`

No old task, taskctl, evidence, manifest or shared-ownership file enters the story.

## Observable contracts

- The sole instruction write is
  `POST /api/v1/fees/obligations/{obligation_id}/instruction`, requires `Fee.Edit`, owns
  no actor/body identity, delegates exactly once, commits one accepted result and preserves
  direct success/replay and fail-closed error facts.
- The sole detail read is bodyless
  `GET /api/v1/fees/obligations/{obligation_id}`, requires `Fee.Read`, delegates exactly
  once, performs no transaction action and preserves persisted source, seven independent
  statuses, lines, decimal/date values and supersession facts.
- The frontend functions return each direct server response without envelope, mapping,
  default or inference. Decimal money remains a string.
- Adding the GET successor legitimately makes
  `POST /api/v1/fees/obligations/instruction` return 405 through dynamic-route method
  matching. The aligned predecessor regression also proves no exact collection POST route
  exists; the legacy body-ID route remains 404 and neither request invokes the service or
  transaction.
- The row 109 probe now uses the installed Axios declarations directly. Removing its
  stale local Axios redeclaration fixes current-version type incompatibility without
  assertion weakening, compiler suppression or product change.

## TDD and current verification

- Historical RED/GREEN and independent reviews are preserved and were not rerun:
  row 108 recorded 24 missing-route/schema failures followed by 27 passing tests; row 109
  recorded missing-export RED and isolated type GREEN; row 111 recorded 10 missing-route
  failures followed by 10 passing tests and terminal PASS; row 112 recorded terminal PASS
  after its exact-file type compatibility close. The stale READY headings in rows 111–112
  are old task-file state and are not adopted.
- Current serialized backend tranche initially produced 167 passes and one obsolete
  predecessor assertion. After the minimum successor alignment, the two affected API files
  produced 37 passes; the other 131 successful current results were not repeated.
- Both exact frontend contract probes pass strict isolated TypeScript verification.
  Exact-file ESLint passes.
- Full frontend typecheck reproduces exactly the seven inherited integration-base errors:
  billing one, http one, officialWorkflows three and CaseFeesTab two. No new or owned-path
  error is present.
- Scoped Ruff, Ruff format-check and exact diff-check pass.

## Non-goals and rollback

No page/UI behavior, fee calculation or rate/source activation, status inference, draft,
PayList, payment/evidence, lifecycle/legal-state write, schema/migration, second endpoint,
router rewiring, adjacent obligation row, old evidence mutation or milestone claim.
Rollback reverts only this story commit.
