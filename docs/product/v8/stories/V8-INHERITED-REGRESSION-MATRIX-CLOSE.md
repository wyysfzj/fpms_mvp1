# V8 Full Inherited Regression Matrix Current Adoption

- Story ID: `V8-FULL-INHERITED-REGRESSION-MATRIX-CURRENT-ADOPTION`
- Catalog owner: `FPMS-V8-INHERITED-REGRESSION-MATRIX-20260712-01` (Row281)
- Review class: `PROTECTED`
- Effective dependencies: `243`
- Effective dependency SHA-256:
  `6b17123b63d5a862a5f702454e38d2bab1e5a41512a4ed177b79957946c362b7`

## Authority and scope

This adoption consumes the current Row199 Full capability story, the independently reviewed
Row278 input-capability/live-workbook story, the current Foundation Tasks01–70 authority map and
the frozen Row281 catalog dependencies. The declared input audit contains `306` unique paths:
`244` primary inputs plus `62` regression inputs. The sole absent historical Row199 path is
replaced by the two current Full successor contracts; no other missing input is accepted.

The matrix partitions execution without duplicate claims. The 55 backend regressions are covered
by the disjoint Tasks01–70, current-V8 and five-file declared-nonoverlap tranches. The seven
Playwright regressions are contained in the eleven non-live Tasks01–70 specs. The mock Playwright
paths use a dynamic strict-port Vite child. The independent lifecycle live spec and Row278 workbook
live spec use isolated migrated SQLite databases and real strict-port services with no route
fulfillment.

## Fresh results

- `backend_tasks01_70`: `400 passed, 4 warnings in 157.10s`
- `backend_current_v8`: `5206 passed, 24 skipped, 4 warnings, 114 subtests passed in 1390.36s`
- `backend_declared_nonoverlap`: `17 passed, 4 warnings in 8.48s`
- `full_successor_contracts`: `5 passed in 0.10s`
- `lean_governance_contract`: `32 passed in 1.14s`
- `frontend_typecheck`: `vue-tsc --noEmit passed`
- `frontend_contracts`: `row217 and row221 executable contracts passed`
- `playwright_tasks01_70_mock`: `22 passed in 2.3m`
- `playwright_declared_primary`: `52 passed in 4.8m`
- `playwright_lifecycle_live`: `1 passed in 4.1s`
- `playwright_workbook_live`: `1 passed in 9.5s`
- `focused_contract`: `4 pre-adoption contract tests passed; ledger adoption remains independently reviewed`

Every test-alignment commit consumed by this close received an independent High review with
P0/P1/P2 `0/0/0`. They changed only obsolete test inputs or expectations to match separately
reviewed current contracts; they did not change product code, weaken assertions, add skips/xfails,
or infer customer decisions.

## Production non-closure

Both `DG-PAYMENT-WORKBOOK:GLOBAL` and `DG-SERVICE-RATE-VERSION:GLOBAL` remain
`CONFIG_REQUIRED`; registry decisions remain `PENDING`; production attempts remain
`409 / NO WRITE`; TEST_ONLY stays isolated. This story claims no production activation and makes
no schema, migration, seed, runtime-data or product change. Rows282 and 283 remain pending.

## Rollback

Rollback removes only this story, matrix/contract metadata and the Row281 ledger adoption. It
does not alter the independently reviewed alignment commits, product configuration or business
data.
