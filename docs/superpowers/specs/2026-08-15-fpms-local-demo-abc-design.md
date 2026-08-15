# FPMS Local ABC End-to-End Demo Design

Date: 2026-08-15
Status: REVIEW — chat design approved; written specification review pending
Risk: PROTECTED
Baseline: `d1df69e649f5d28cb192d347d25c8d775663aaf2`

## 1. Outcome

Deliver one repeatable, customer-visible local demonstration that starts with a fictional client
and case and ends with one customer AR bill fully settled by one recorded payment and one active
offset. The same run also demonstrates filing preparation, an OA reply/receipt lifecycle, one
neutral internal template preview, and one customer service-price input supplied at runtime.

The accepted terminal state is `DEMO_READY`. It is not `RELEASE_PASS`, production readiness,
security acceptance, official submission, official payment, or activation of a customer or legal
source.

## 2. Authority and fixed interpretation

The controlling customer decision is
`docs/product/v8/customer-decisions/2026-08-15-local-demo-abc.txt`, adopted in
`DEC-LOCAL-DEMO-ABC-20260815`. It accepts the cumulative scopes presented immediately before the
approval:

- A: client/case, filing preparation, OA and receipt archive;
- B: runtime template and service-price input, template preview and fee draft;
- C: one unique AR bill, one customer payment and one offset that settles the bill.

This design also preserves:

- `docs/product/v8/domain-contract.md`;
- `docs/product/v8/source-decision-registry.md`;
- the V7 lifecycle design, script and runbook;
- the independent High audit findings `DEPLOY-PKG-002`, `STATE-UI-002`, `EVID-RETRY-003`,
  `TXN-DOCFEE-008`, `FIN-BILL-001`, `FIN-OFFSET-001`, `FIN-DASH-004` and
  `FIN-ADAPTER-005`.

The current production service-price and payment-workbook gates remain pending. The demo bundle
cannot satisfy or mutate either gate.

## 3. Approaches considered

### 3.1 Reuse historical seed/enrichment

This would be quickest, but existing seeds hard-code amounts and downstream objects and can mark
unapproved sources as confirmed. It would make the UI appear to complete work that was actually
inserted beforehand. Rejected.

### 3.2 Build the full production input administration and production deployment

This would add persistent upload/version/review/activation UI, PostgreSQL and public deployment
hardening before the demo. It is the right later production direction but conflicts with the
approved speed and security-deferral constraints. Rejected for this demo.

### 3.3 Immutable local demo bundle plus real product transactions — selected

An externally supplied, read-only `DEMO_ONLY` bundle is validated before services open and exposed
through a demo-profile provider. Product writes then use the existing lifecycle, obligation,
fee-draft, billing, payment and offset domains. No core business object is pre-created and no
runtime input is promoted to a production table or decision gate.

## 4. Topology and baseline

- Create all work from a clean isolated branch based on the exact baseline above. The dirty shared
  `master` worktree is not modified, cleaned, stashed or absorbed.
- Run backend and frontend only on loopback, with a unique `FPMS_DEMO_RUN_ID`, disposable SQLite
  database and disposable storage directory per run.
- Use fictional data only. Do not connect to a shared or production database or storage location.
- Use a single existing `admin` demo operator. No authentication bypass, finance-role claim or
  new permission broadening is allowed even though security remediation is deferred.
- The canonical runner starts from an empty run directory, migrates, installs only demo-safe master
  data, validates the runtime bundle, starts the API and UI, and exposes health/readiness.
- Baseline startup must declare `openpyxl`; a clean declared-dependency environment must import
  `app.main` before any journey verification.

The first implementation plan may choose local uvicorn plus Vite or repair the existing demo
container, but there is one canonical command at acceptance. It may not use the production Compose
path. If the container is selected, bundle and run storage are read-only/isolated mounts and the
fixed shared volume is removed from the accepted path.

## 5. Customer-visible journey

The live presentation contains seven checkpoints. Negative and concurrency cases stay in the
automated gate so the customer story remains approximately 25–30 minutes.

| ID | Customer action | Required observable result |
| --- | --- | --- |
| `ABC-01` | Create one fictional client, primary contact and domestic invention case through UI. | One client/contact/case identity; case `NOT_FILED`; no package, draft, bill or payment exists. |
| `ABC-02` | Enter filing preparation, select the runtime internal template and render a preview. Resolve the preparation package twice. | Both resolves return the same package; template version/hash and rendered case values are visible; legal status remains `NOT_FILED`; preparation is explicitly not official submission. |
| `ABC-03` | Register an OA notice with exact due date, explicit source and `CONFIRMED`; resolve its OA package and create the linked OA_OUT. | One source/package/task identity; OA task remains `OPEN`; case remains in the observed OA stage; package awaits receipt. |
| `ABC-04` | Select the eligible same-case receipt attachment, complete the checklist and archive. | Package `ARCHIVED`; exactly the target OA task becomes `DONE`; the case projection is the actual reviewed post-receipt state; no presenter-invented transition. |
| `ABC-05` | Select the one runtime service-price item, record customer `PAY`, prepare and lock the draft. | Bundle/version/hash/item and Simplified-Chinese demo disclaimer are visible; one SERVICE obligation and one linked `LOCKED` draft; `total_service` equals the exact bundle amount; no official-fee or PayList line is created. |
| `ABC-06` | Generate an AR bill from that locked draft and repeat the same user intent. | Exactly one AR bill; source draft/item lineage visible; first result created, exact retry reused; bill `UNSETTLED`, balance equals amount. |
| `ABC-07` | Record one equal CNY bank payment and offset it to the bill. Reload payment, bill, case-finance and dashboard views. | Before offset the payment is `UNALLOCATED`; after one offset the bill is `SETTLED` with zero balance, payment is `FULLY_ALLOCATED` with zero unapplied amount, and case/dashboard projections show the same CNY truth. |

The live script keeps only two deliberate positive boundary demonstrations: repeated package
resolve returns the same identity, and OA_OUT creation does not close the task. Other negative
cases run automatically.

## 6. Runtime bundle v1

### 6.1 Packaging and activation

The external directory contains exactly `manifest.json` and allowlisted files below
`templates/`. It is never committed as production input. The loader accepts it only when all of
the following are exact:

- `FPMS_ENV=demo`;
- `FPMS_DEMO_SCOPE=LOCAL_ABC_E2E`;
- a non-empty `FPMS_DEMO_RUN_ID`;
- an explicit bundle path outside product storage;
- an external expected canonical-manifest SHA-256;
- the reviewed specification reference and content digest recorded by the manifest.

Import means offline validation into a content-addressed, read-only run location. Activation means
startup-time validation and an immutable in-process snapshot. There is no hot reload or mutation
API. A changed bundle requires a new run ID and process restart. Rollback selects a previous exact
path/digest and starts a new run; it never rewrites prior business history.

The process must fail before migration/seed and before opening a port when a required bundle is
missing or invalid. A missing optional capability during a request returns
`409 DEMO_INPUT_CONFIG_REQUIRED` with no business write.

### 6.2 Manifest contract

The canonical UTF-8 JSON rejects unknown fields and contains at least:

- `schema_version = fpms.demo-input-bundle/v1`;
- `bundle_id`, `bundle_version`, `classification = DEMO_ONLY`;
- `purpose = LOCAL_ABC_E2E`, validity interval and provenance;
- exact `contract_ref` and `contract_sha256`;
- an exact capability allowlist with no wildcard;
- one neutral internal DOCX template with relative path, media type, byte size, SHA-256 and exact
  required variables;
- one `SERVICE_DEMO_PRICE` item with unique code, Simplified-Chinese name, `CNY`, fixed positive
  two-decimal amount, source reference/version/hash and a Simplified-Chinese disclaimer.

The initial bundle contains no official-fee amount. `total_gov=0` means that this scenario has no
official-fee line, not that an unknown official fee was converted to zero.

This design freezes the bundle schema and fail-closed behavior, not the actual template or price.
Product development may use an isolated fixture marked `TEST_ONLY`, but `DEMO_READY` requires one
exact external bundle whose template bytes, price amount, validity, disclaimer and hashes are
separately supplied or explicitly accepted as `DEMO_ONLY`. The implementation must not invent
those values or promote a development fixture merely to make the rehearsal pass.

Paths must be normalized relatives beneath the bundle root. Reject `..`, absolute paths,
symlinks, extra files, macro-enabled files, external DOCX relationships, duplicate identities,
variable drift, non-finite numbers, floating-point JSON amounts and hash/size mismatch. The
template itself must carry a visible local-demo marker.

### 6.3 Provider and durable usage lineage

Do not extend or populate `OfficialRateBook`, `ServicePriceBook`, `FeeRate`, `Template` or
`CustomerDecisionGate` with `DEMO_ONLY` data.

The demo provider exposes only the allowlisted template and service-price item. It is not
registered outside the exact demo profile and never falls back to seed or production sources.

Selecting the runtime service item is a real authenticated UI/API action, not bootstrap
enrichment. The adapter resolves and validates the complete immutable item before writing. In one
transaction it appends a fee-lane source activity whose payload/evidence carries bundle ID,
bundle version, manifest hash, item code, item snapshot/hash, amount, currency and disclaimer,
then creates or reuses one SERVICE obligation through the existing obligation service. Existing
customer-instruction and draft-preparation services create the linked draft only after `PAY`.
Same idempotency key and payload reuse the same source/obligation; key drift returns 409.

Template preview is read-only and returns only a visibly demo-marked rendering. It creates no
official document, submission, letter-handoff or email fact.

## 7. Lifecycle, document and UI reliability

- Filing and OA resolve use existing-first identity; repeated calls do not duplicate packages.
- OA notices require exact due date, source and `CONFIRMED`; no relative-month calculation or
  title inference is accepted.
- OA_OUT linkage is atomic and leaves the task open.
- Receipt candidates are same-case and eligible-source attachments returned by the API; users do
  not paste raw attachment IDs.
- Cross-case and wrong-source receipt requests return 4xx with zero write. A valid receipt archive
  closes exactly one matching task in the same transaction.
- Attachment review consumes the POST result. An uncertain transport failure first reconciles
  durable state, then reuses the exact key/time/payload.
- Every demo page observes the complete route identity. On A-to-B navigation it clears stale
  state, rejects late A responses and binds mutations to the loaded B identity.
- Main-journey navigation contains no placeholder or inert control. All new visible text is
  Simplified Chinese and the demo boundary is visible on every runtime-input/finance page.

## 8. Fee-draft to bill contract

The source-of-truth consumption carrier is billing-owned
`t_bill_draft_source(bill_id, draft_id UNIQUE NOT NULL)`, avoiding a reverse fees-to-billing
foreign-key cycle. A non-null `BillItem.fee_item_id` is also unique.

`POST /bills/from-drafts` accepts the strict command
`{draft_ids, bill_no?, bill_date, due_date?, idempotency_key}` and persists a canonical command
hash while preserving the existing route and permission. Amount and currency are derived only
from the locked source drafts; the form cannot override them. `bill_date` is explicit and
`due_date` is either an explicit approved demo value or null; neither is guessed. The demo UI
generates one key per form intent and reuses it across transport retries.

Creation is allowed only when every source draft:

- exists, is `LOCKED`, has positive finite items, and has not been consumed;
- belongs to the same client and currency;
- has source items that have not appeared in another bill.

The service resolves drafts in stable order and, in one caller-owned transaction, claims all
sources, creates the bill and items, and commits. The existing `OPEN|LOCKED` fee-draft status model
is preserved; a consumed locked draft cannot be unlocked. The UI lists only locked, unconsumed
drafts.

Bill creation derives the authenticated actor from the request context and persists it through the
existing audit fields; actor identity is never accepted from the client body.

Same key plus the same normalized payload (including order-insensitive source identity) returns
the same complete bill detail with `reused=true` and no new rows. Same key plus different payload,
a different key for a consumed source, partial prior ownership or concurrent loss returns 409/no
write. First creation and exact replay both preserve the create endpoint's 201 status and identify
the outcome through `reused=false|true` and `idempotency_key`. Migration preflight detects
historical duplicate source ownership and fails without guessing a winner.

## 9. Customer payment and offset contract

### 9.1 Payment

Payment is a customer receipt, not an allocation. `bill_id` on the create form is only a target
used to validate/prefill client and currency; the UI must say so. The authoritative payment-to-bill
relationship is an active Offset. Payment lists must not infer bill identity from matching
client/currency/case.

The accepted demo command requires positive fixed-two-decimal CNY amount, explicit payment date,
a non-empty unique payment number, `BANK_TRANSFER`, a required bank reference, server-derived
actor/time and a strict idempotency key. Persist payment method, bank reference and command
identity. An optional target bill is validation/prefill context only and must not be returned or
displayed as an applied relationship before an Offset exists.

The create response is the authoritative Payment plus its sole PaymentLine and
`idempotency_key/reused`; the UI consumes that response instead of depending on follow-up GETs.
Same key/same command returns the same composite with 201 and `reused=true`; key drift or duplicate
external identity returns 409. Zero, negative, non-finite, wrong-client or wrong-currency input
creates nothing.

### 9.2 Offset

Offset create and reverse have strict idempotency keys and canonical command hashes. Create
validates the real payment line, customer, currency, active payment balance and bill balance, then
atomically writes exactly one Offset and updates payment-line, bill and canonical CaseReceipt
projections. Fixed lock/CAS ordering is `PaymentLine -> Bill -> CaseReceipt`. SQLite uses an
explicit serialized write boundary; the implementation remains portable to row locking or CAS in
PostgreSQL.

Database constraints protect positive offset amount and non-negative projections, including
`raw_amount = allocated_amt + balance_amt`. CaseReceipt receives a durable unique key formed from
case, fee code/type, normalized year and currency; nullable-field equality is not used as an
identity.

Create returns an authoritative composite containing Offset, Bill status/balance/currency,
PaymentLine allocated/balance/currency, receipt summary and `idempotency_key/reused`. The UI
consumes this transaction result. If transport outcome is uncertain it replays the same command
and key before issuing reconciliation reads; it never creates a new intent merely because a GET
failed.

An exact create retry returns the same composite with 201 and `reused=true`. A second intent that
would over-allocate, a stale balance, wrong client/currency or command drift returns 409 and rolls
back every projection. Reverse is not shown live but its 200 response has the same authoritative
shape; affected regressions must prove exact replay restores only once and a different-key second
reverse is rejected.

Strict schema/format failures return 422, absent resources return 404, deterministic domain
validation such as customer/currency mismatch or amount exceeding a balance retains 400, and 409
is reserved for lifecycle/source consumption, idempotency drift, unique/concurrent ownership or
repeat reversal conflicts. Every 4xx path is no-write.

Bill, payment, offset and reverse commands all derive the current authenticated actor from the
request context and persist create/update/reversal attribution. Command ownership is included in
the durable idempotency record; a different actor cannot silently reuse another actor's intent.
Reverse persists `reversed_by/reversed_at` rather than accepting or discarding an actor argument.

## 10. Finance adapters and dashboard

- Required monetary fields reject null, empty, NaN, infinity and malformed values with a typed
  `FINANCE_CONTRACT_INVALID` error. Nullable amounts stay null and display `待确认`; currency is
  never silently defaulted.
- Keep canonical decimal strings through adapters and commands. Formatting occurs only at the
  presentation boundary.
- The demo scope is one CNY bucket. Dashboard KPI uses the backend
  `remaining_prepayment_balance`; the queue requests only `unapplied_amt > 0` and displays that
  amount. It never totals the first 100 `Payment.amount` rows.
- After full allocation, the payment disappears from the pending-allocation queue. Case finance,
  bill, payment and dashboard must agree after reload.
- Payment and offset selectors expose only matching-client, matching-currency, positive-balance
  records; bill choices are limited to `UNSETTLED|PARTIALLY_SETTLED`. Offset defaults to the exact
  decimal minimum of payment-line and bill balances, never a hard-coded currency/number value.
- Create/reverse views consume the authoritative mutation composite and refresh every affected
  projection together; a page may not show a new Offset beside a stale Payment, Bill or dashboard.

## 11. Atomic implementation slices

Only two implementation lanes run concurrently, and shared migrations/models/routers/SQLite tests
are serialized.

1. `ABC-DEMO-BUNDLE-PARSER`: canonical manifest, path/DOCX/rate validation and digest binding.
2. `ABC-DEMO-LOCAL-BOOT`: declared dependency, run-ID environment, demo-safe bootstrap and one
   canonical start/reset/stop command.
3. `ABC-DEMO-RUNTIME-PROVIDERS`: template preview and authenticated service-price-to-obligation
   adapter with durable source activity.
4. `ABC-DEMO-LIFECYCLE`: fresh verification and only actual blockers for client/case, filing,
   OA, OA_OUT, receipt and route/evidence reliability.
5. `ABC-FIN-BILL`: source-consumption/idempotency migration, service/API and bill UI.
6. `ABC-FIN-PAYMENT`: truthful payment model/API/UI and idempotency.
7. `ABC-FIN-OFFSET`: atomic allocation/reversal, CaseReceipt identity and projections.
8. `ABC-FIN-ADAPTER-DASH`: strict money contracts and authoritative dashboard.
9. `ABC-DEMO-LIVE-E2E`: one browser-driven seven-checkpoint spec and negative no-write matrix.
10. `ABC-DEMO-READY`: two fresh runs, headed rehearsal, independent High review and operator pack.

Dependency spine:

```text
bundle parser -> local boot -> runtime provider -> ABC-05
clean baseline -> lifecycle -> ABC-01..04
runtime provider -> bill -> payment -> offset -> ABC-05..07
lifecycle + finance APIs -> frontend adapters/navigation -> live E2E -> Demo Ready
```

Every product slice uses targeted RED, minimum GREEN, affected regressions, scoped lint/type/diff,
an atomic commit and independent review appropriate to its risk. A discovered problem outside the
slice becomes a separate blocker story; it does not reopen this design.

## 12. Verification and acceptance

The final targeted gate must prove:

1. clean declared-dependency import and one-command fresh migrate/bootstrap/start;
2. invalid/missing bundle fails before ports open or returns the exact optional-capability 409 with
   zero business writes;
3. all seven checkpoints use real Vue, API and SQLite, with no `page.route` response mock, direct
   database write, lifecycle enrichment, fixed downstream object ID or skipped checkpoint;
4. repeated resolve, bundle selection, obligation/draft command, bill creation, payment creation
   and offset command are safe under exact replay;
5. wrong OA deadline/source/receipt, bundle hash/version/item, draft state/source, payment
   customer/currency/reference and offset amount produce the expected 4xx and no partial write;
6. one locked draft creates one bill; one payment plus one active offset settles it; all reloaded
   balances and statuses agree;
7. route A-to-B and commit-then-drop reconciliation do not target or display the wrong object;
8. the exact live spec passes on two different fresh run IDs, followed by one headed operator
   rehearsal;
9. candidate SHA/tree, bundle manifest/file hashes, run IDs, object IDs, screenshots, request IDs,
   focused results and cleanup receipts are recorded without token/password/full-HAR leakage;
10. an independent High reviewer returns zero findings for the exact integrated demo scope.

The final acceptance evidence must bind the separately supplied/accepted bundle manifest digest.
Without that exact input, implementation may be code-complete and testable but remains
`DEMO_INPUT_REQUIRED`, not `DEMO_READY`.

Existing tests that create a bill from an `OPEN` draft must be changed to lock it first and add a
no-write rejection assertion. Existing payment-linkage tests that infer a bill from matching
client/currency/case must instead assert no allocation relationship before an active Offset.
Those expectations are known defects, not compatibility contracts.

The final label is `DEMO_READY`. Product-wide audit status remains blocked until its separate
release work is completed. No broad/release gate is run for this milestone.

## 13. Explicit non-goals

- Security remediation, public/remote hosting, PostgreSQL production migration, production
  Compose/nginx/TLS, release evidence or disaster recovery.
- Production input upload/approval/activation UI, real customer service rates, current legal or
  official fees, official payment workbook/VBA, PayList, official payment or receipt verification.
- Finance-role permission repair; the accepted journey is operated only by the existing demo
  `admin` account and makes no claim that the Finance role can perform it.
- Automatic CPC/official-system login, submission, signature, receipt download, email or RPA.
- Manual/AP bills, tax/FX, partial or multi-bill allocation as a new product story, prepayment
  distribution, refund, bank reconciliation, bad debt, dunning, commission, annuity or complete
  reminder behavior.
- Treating a prepared package as submitted, OA_OUT as officially received, a demo template as an
  official form, or a demo price as a production receivable source.

Audit-claim boundaries are equally narrow. `FIN-BILL-001` is blocked for the fresh demo database,
but historical production duplicate remediation is not claimed. `FIN-OFFSET-001` remains open for
PostgreSQL until a real two-connection PostgreSQL gate passes; the demo proves file-backed SQLite
serialization only. `FIN-DASH-004` is corrected only for the explicitly labelled CNY card, not a
general multi-currency dashboard. `FIN-ADAPTER-005` is corrected only for adapters reached by this
ABC journey; untouched official-payment, annuity, commission, expense and collection adapters
remain outside closure.

If the customer later requests a remote URL, official payment, real price/template activation or
the excluded finance variants, that is a new authority and closure. It cannot be absorbed into the
ABC demo.

## 14. Rollback and recovery

- Product slices land as atomic commits. Roll back an accepted slice with `git revert`, never
  reset/stash/clean user work.
- A failed run keeps its exact DB/storage/screenshots until evidence is captured. The next attempt
  uses a new run ID instead of mutating the failed run.
- Bundle rollback selects a prior immutable digest and restarts. It never changes stored demo
  obligations, drafts, bills, payments or offsets.
- Demo cleanup stops exact PIDs and removes only validated, run-ID-owned temporary locations after
  evidence capture. The shared worktree and external input source are never deleted.

## 15. Written-design completion

This specification is ready for implementation planning only after its exact commit is reviewed by
an independent High reviewer with zero P0/P1/P2 findings and the customer confirms that the written
specification faithfully records the approved ABC scope.
