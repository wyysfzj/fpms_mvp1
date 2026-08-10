# Story V8-FEE-ESTIMATE-PREVIEW-HTTP-FE-VERTICAL-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Base: `434378756fe02a937b32127dbbe5605b8fad7c3d`
- Outcome: current-adopt the already integrated official-fee estimate preview HTTP and
  frontend adapters while preserving one explicit caller-owned estimate context, the
  `ESTIMATE` label, decimal strings, source metadata and the no-obligation boundary.
- Authority: frozen catalog rows `105` and `106`, their exact task contracts and
  preserved historical RED/GREEN; `docs/product/v8/domain-contract.md`; and
  `docs/product/v8/source-decision-registry.md`.
- Change mode: current verification only. The row-105 product/test seams and row-106
  product/assertion seams already match archive anchor
  `6b2ef89da447353380b99853168d4d38aaf9210a`; current successor bytes win around those
  seams.

## Catalog IDs and dependencies

1. `FPMS-V8-FO-PREVIEW-HTTP-ADAPTER-20260712-01` (ordinal `105`, profile `TC-API`)
   depends on `FPMS-V8-FO-PREVIEW-ESTIMATE-20260712-01`.
2. `FPMS-V8-FO-PREVIEW-FE-ADAPTER-20260712-01` (ordinal `106`, profile
   `TC-FE-ADAPTER`) depends on row `105`.

The row-104 read-only preview service is current-verified by
`V8-FEE-OBLIGATION-CORE-CURRENT-VERIFICATION` at
`f89d222861d6ebda88ead322cfd7254e8fb26e64`. This story consumes that dependency and
the existing production rate provider without changing either.

## Exact product and test paths

- `backend/app/modules/fees/schemas.py`
- `backend/app/modules/fees/api.py`
- `backend/tests/test_v8_fee_estimate_preview_api.py`
- `frontend/src/api/fees.ts`
- `frontend/src/api/fees.types.ts`
- `frontend/src/api/contracts/v8_fee_estimate_preview.contract.ts`
- `docs/product/v8/stories/V8-FEE-ESTIMATE-PREVIEW-HTTP-FE-VERTICAL-CURRENT-ADOPTION.md`

No old task, taskctl, evidence, ledger, review, manifest or shared-ownership file enters
this story.

## Observable HTTP contract

`POST /api/v1/fees/official-fee-preview` requires `Fee.Read` through a function
parameter. Its strict body requires the case ID, nested trigger and explicit nullable
source-document ID, literal `CNY`, and one caller-supplied ISO effective date. Legacy
top-level trigger/source fields, missing nested fields, defaults and extra keys are not
accepted.

The handler checks the exact case without autoflush, constructs the production provider
from the request session and delegates exactly once to `preview_estimate`. It performs no
clock read, fallback, add, delete, flush, commit, rollback or model mutation. Exact
business codes and details remain mapped to the frozen `400`, `404` and `409` responses;
authentication, permission and request-shape failures remain `401`, `403` and `422`.

The direct response preserves `ESTIMATE`, `CNY`, caller context, provider order, nested
line/source association, fixed two-place money strings, fixed four-place reduction
strings, nullable dates and all source provenance. It exposes no obligation, draft,
activity, PayList/export, payment, idempotency, deadline or legacy-preview identity.

## Observable frontend contract

`OfficialFeeEstimateContext` requires the same single explicit request object and
`OfficialFeeEstimateResult` preserves the direct server shape. The adapter posts that
object unchanged and returns `response.data` without mapping, number conversion,
calculation, sorting, grouping, defaults, overloads or legacy compatibility.

The dedicated contract probe proves the literals, nullable wire fields, decimal strings,
nested provenance and prohibited persistence identities. Foundation typecheck found that
its obsolete 32-line Axios module augmentation globally replaced the real Axios instance
with a stale interface, causing unrelated valid `patch`, Blob and interceptor calls to
fail compilation. Commit `b2da634` removes only that test-owned augmentation; all fee
preview assertions, including all 20 negative probes, remain byte-identical.

No page or `CaseFeesTab.vue` behavior is adopted. Supplying a user-selected context and
effective date remains the separately owned UI successor.

## Archive and historical reconciliation

The original pre-implementation parent `4e679dbdadfd7307e6dd82732e8caaf9dd5691b8`
contains the legacy preview shapes and neither focused contract file. Implementation
anchor `83d014fb825c76e90c53821c7db9ed7f3cd49436` introduced the exact row-105/106
contracts. That historical RED is preserved by reference and is not manufactured on the
already-GREEN current tree.

Current/archive comparison proves:

- row-105 request models:
  `784178d953eb025386c793dbf99d1c278d0cf1d7abc3cb60d31e9f5512407cf3`;
- row-105 response models:
  `1968cb6b4bb56cd15671973aec770263c0a62f495204d32cc0b73afa4cc9de20`;
- row-105 HTTP handler:
  `8f1f01b2a149f9336aa46de296d4c9fc5c81ddbab8b3bedf13f46271f05914b3`;
- row-105 focused-test blob:
  `f12f49d48c040c4c131c8c6a90b35fdc6f65f143`;
- row-106 public types:
  `d6ca1ba8e54e654e2c706e8554de53d8604cccd0c30f199f3c77ab61b77bfb46`;
- row-106 frontend adapter:
  `6e62fa6f91bf893353e17139ddf103e38042436e0bb20f48a17124d66265e027`;
  and
- row-106 archive assertions retained beneath the current Axios isolation:
  `1420d0c464e763857462909c49899949910b7a3f41eb27f4ab86a18cbcca929b`.

The shared backend and frontend files also contain later unrelated fee successors. No
file-wide archive replacement is allowed.

## Verification and review

Fresh pre-SQLite verification from this worktree:

- isolated row-106 TypeScript contract: exit `0`;
- exact row-106 three-file ESLint: exit `0`;
- scoped row-105 Ruff check-only: exit `0`, with only the repository's existing
  top-level Ruff configuration deprecation notice; and
- exact diff check: exit `0`.

Under the controller-granted serialized SQLite lane, each backend command ran exactly
once in the declared order:

- untouched row-105 focused test: `40 passed, 3 warnings in 14.38s`; and
- exact row-103/104 predecessor regression: `101 passed, 1 warning in 25.58s`.

The focused warnings are the existing passlib `crypt` deprecation and two inherited
Pydantic `Field` deprecations. The predecessor warning is the same passlib deprecation.
The lane was released immediately after the second command. Because the current tree was
already GREEN, no RED was manufactured and no product or test bytes changed.

An independent High reviewer must review the exact commit and independently rerun the
decisive checks under the serialized lane. The implementer does not approve this
`PROTECTED` story.

The Foundation correction passed full frontend lint, typecheck and production build.
Independent High review approved `b2da634` with P0/P1/P2 `0/0/0`, confirming no runtime
code, fee-preview assertion or type-safety boundary was changed. The current exact
six-path fingerprint is
`04eeb6928f6df356fcd897ece89745af198896d4c417a11a573dc7bc24f15bed`.

## Non-goals and rollback

No fee/rate/reduction/source rule, source activation, obligation recognition, draft,
PayList, payment/evidence, lifecycle/legal state, schema/migration/seed, second endpoint,
router rewiring, page/UI behavior, legacy compatibility, broad frontend typecheck,
ledger/disposition/review edit, old evidence mutation or milestone claim.

Rollback reverts only this story-card commit; all current product and test bytes remain
unchanged.
