# FPMS Local ABC End-to-End Demo Design

Date: 2026-08-15
Status: REVIEW — high-level scope selected; written specification adoption pending
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

## 2. Authority and proposed interpretation

### 2.1 Customer scope selection and written adoption

The high-level customer scope selection is the exact 87-byte message in
`docs/product/v8/customer-decisions/2026-08-15-local-demo-abc.txt`, recorded by
`DEC-LOCAL-DEMO-ABC-20260815` from Codex task
`019ffc07-14a5-7dc2-9536-f2047327e14a`. It selects the cumulative labels discussed immediately
before the approval:

- A: client/case, an evidence-reachable filing/OA lifecycle and receipt archive;
- B: runtime template and service-price input, template preview and fee draft;
- C: one unique AR bill, one customer payment and one offset that settles the bill.

The 87-byte message does not itself contain the detailed semantics below. This document is the
exact proposed expansion. It remains non-executable until an independent High reviewer approves
its exact commit and the customer explicitly confirms that reviewed commit. That later confirmation
is preserved as a second exact decision source before any product story starts.

This design also preserves:

- `docs/product/v8/domain-contract.md`;
- `docs/product/v8/source-decision-registry.md`;
- the exact baseline versions of the V7 lifecycle design
  (`docs/postdemo/postdemo_p1_lifecycle_demo_design_v7_20260711.md`, SHA-256
  `02ba842f812f5999c3e7cc72f59d3f8568bf2a47d31335573b6db6b3c768dc29`), script
  (`docs/postdemo/postdemo_p1_lifecycle_demo_script_v7_20260711.md`, SHA-256
  `20b63ebf1a5aee8e3b3a7a86634e3af9c35a7a7f7abf657fdf99e82ff55c393b`) and runbook
  (`docs/postdemo/postdemo_p1_v7_ui_e2e_success_runbook_20260711.md`, SHA-256
  `e1d6fc0beeeacd32edf2d8bc1a6ad6fbb2bb674c9b2959b34d527459a573b677`).

The current production service-price and payment-workbook gates remain pending. The demo bundle
cannot satisfy or mutate either gate.

The pinned V7 files are reusable presentation/history inputs only. Their historical jump from
filing preparation to OA cannot override the current lifecycle graph; section 5's full prerequisite
ladder is the controlling successor behavior.

### 2.2 Durable High-audit finding snapshot

The planning input was the independent High report bound to the baseline above, external artifact
SHA-256 `0e49c6997c9ebd52de1eb8c4bee9550f130ee2552c246b02ef5a3053758e5ed9`. External artifact
availability is not required to interpret this design; the exact finding meanings used here are:

| ID | Baseline defect that controls this demo | Exact demo closure |
| --- | --- | --- |
| `DEPLOY-PKG-002` | `backend/pyproject.toml` omits `openpyxl` although importing `app.main` reaches `verified_official_payment_workbook.py` and imports it. | Clean declared dependencies import/start the local runner. |
| `STATE-UI-002` | Main detail/edit pages bind route identity only at mount or retain prior async/form/artifact state. | Every ABC page clears, reloads and mutates the complete current route identity. |
| `EVID-RETRY-003` | Attachment review discards the authoritative POST result; a later GET failure plus regenerated timestamp makes exact retry conflict. | Consume POST truth; on uncertainty reconcile durable state first, then reuse one immutable intent. |
| `TXN-DOCFEE-008` | Document fee creation can add a partial zero draft before a swallowed downstream exception and outer commit. | Runtime template/rate failure rolls back source activity, obligation, draft and items together. |
| `FIN-BILL-001` | `from-drafts` accepts OPEN/unconsumed sources and lacks source uniqueness/idempotency, so one draft can create multiple AR bills. | The single ABC locked draft/item is atomically claimed once; exact replay reuses it. |
| `FIN-OFFSET-001` | Offset/reverse use check-then-write without durable idempotency or a concurrency boundary. | File-backed SQLite concurrent allocation/reversal is serialized, atomic and replay-safe. |
| `FIN-DASH-004` | Dashboard totals the first 100 raw payments and labels allocated payments as pending. | The labelled CNY card consumes a server-side CNY unapplied summary/filter. |
| `FIN-ADAPTER-005` | Financial adapters coerce absent, malformed or non-finite money to zero. | ABC-reached adapters preserve decimal strings and fail closed on invalid required values. |

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
- Use two distinct per-run demo identities: existing `admin` performs customer/lifecycle/finance
  actions and `demo_evidence_reviewer` performs only evidence review. Both use the existing Admin
  role in the disposable demo DB, so no new permission vocabulary is invented; backend review
  still requires different uploader/reviewer IDs. Credentials are supplied to the local runner,
  not committed to source or evidence. No authentication bypass, Finance-role claim or production
  permission broadening is allowed even though general security remediation is deferred.
- The canonical runner starts from an empty run directory and validates/copies the required runtime
  bundle before creating a database, running migration/seed or opening a port. Only after that
  preflight succeeds does it migrate, install demo-safe master data, start API/UI and expose
  health/readiness.
- Baseline startup must declare `openpyxl`; a clean declared-dependency environment must import
  `app.main` before any journey verification.

The first implementation plan may choose local uvicorn plus Vite or repair the existing demo
container, but there is one canonical command at acceptance. It may not use the production Compose
path. If the container is selected, bundle and run storage are read-only/isolated mounts and the
fixed shared volume is removed from the accepted path.

## 5. Customer-visible journey

The live presentation contains seven checkpoints. Negative and concurrency cases stay in the
automated gate so the customer story remains approximately 30–40 minutes.

| ID | Customer action | Required observable result |
| --- | --- | --- |
| `ABC-01` | Create one fictional client, primary contact and domestic invention case through UI. | One client/contact/case identity; case `NOT_FILED`; no package, draft, bill or payment exists. |
| `ABC-02` | Enter filing preparation, render the runtime internal-template preview, then use visible evidence actions to record the fictional external filing, receipt, acceptance, preliminary examination, publication and substantive-examination prerequisites. | Repeated preparation resolve returns one package. Preparation alone remains `NOT_FILED`; only the ordered reviewed evidence ladder below reaches `PROSECUTION_MANAGEMENT / SUBSTANTIVE_EXAMINATION / APPLICATION_PENDING / CONFIRMED` and legacy display `SUB_EXAM`. |
| `ABC-03` | Upload/register the bundle OA notice through `OA_NOTICE_RECORDED` with exact due date, source and `CONFIRMED`; resolve its OA package and create the linked OA_OUT. | One source/package/task identity; OA task remains `OPEN`; case is exactly `OA_REPLY_IN_PROGRESS / OFFICE_ACTION_RESPONSE / APPLICATION_PENDING / CONFIRMED` with legacy display `OA1`; package awaits receipt. |
| `ABC-04` | Select the eligible same-case OA receipt attachment, complete the checklist and archive through `OA_RECEIPT_ARCHIVED`. | Package `ARCHIVED`; exactly the target OA task becomes `DONE`; case returns exactly to `PROSECUTION_MANAGEMENT / SUBSTANTIVE_EXAMINATION / APPLICATION_PENDING / CONFIRMED` with legacy display `SUB_EXAM`. |
| `ABC-05` | Select the one runtime service-price item, record customer `PAY`, prepare and lock the draft. | Bundle/version/hash/item and Simplified-Chinese demo disclaimer are visible; one SERVICE obligation and one linked `LOCKED` draft; `total_service` equals the exact bundle amount; no official-fee or PayList line is created. |
| `ABC-06` | Generate an AR bill from that locked draft and repeat the same user intent. | Exactly one AR bill; source draft/item lineage visible; first result created, exact retry reused; bill `UNSETTLED`, balance equals amount. |
| `ABC-07` | Record one equal CNY bank payment and offset it to the bill. Reload payment, bill, case-finance and dashboard views. | Before offset the payment is `UNALLOCATED`; after one offset the bill is `SETTLED` with zero balance, payment is `FULLY_ALLOCATED` with zero unapplied amount, and case/dashboard projections show the same CNY truth. |

The live script keeps only two deliberate positive boundary demonstrations: repeated package
resolve returns the same identity, and OA_OUT creation does not close the task. Other negative
cases run automatically.

`ABC-02` is one customer checkpoint but its prerequisite ladder is not compressed into a seed or
status edit. Each row is an authenticated visible UI action and the after-state is read back before
the next row:

| Ordered action/event | Required evidence identity | Exact projection after success |
| --- | --- | --- |
| Create case / `CASE_OPENED` | `CASE_RECORD` | `NEW_CASE / NOT_SUBMITTED / NOT_ESTABLISHED / CONFIRMED`; legacy `NOT_FILED` |
| Resolve filing preparation / `FILING_PREPARATION_STARTED` | `FILING_WORK_PACKAGE / OfficialWorkPackage` | `FILING_PREPARATION / NOT_SUBMITTED / NOT_ESTABLISHED / CONFIRMED` |
| Record fictional external submission / `FILING_EXTERNAL_SUBMISSION_RECORDED` | approved `FINAL_SUBMISSION_VERSION / DocumentEvidenceVersion` plus `MANUAL_EXTERNAL_SUBMISSION_RECORD / CaseActivityEvent` | `WAITING_EXTERNAL_RECEIPT / SUBMITTED_WAITING_RECEIPT / NOT_ESTABLISHED / CONFIRMED`; legacy `WAITING_RECEIPT` |
| Archive bundle filing receipt / `FILING_RECEIPT_ARCHIVED` | the same final version plus reviewed `VALID_FILING_RECEIPT / OfficialWorkPackageReceipt` | `PROSECUTION_MANAGEMENT / SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE / APPLICATION_PENDING / CONFIRMED`; legacy `WAITING_RECEIPT` |
| Register bundle acceptance notice / `ACCEPTANCE_NOTICE_RECORDED` | approved `ACCEPTANCE_NOTICE / DocumentEvidenceVersion` | `PROSECUTION_MANAGEMENT / ACCEPTED / APPLICATION_PENDING / CONFIRMED`; legacy `ACCEPTED` |
| Start preliminary examination / `PRELIMINARY_EXAMINATION_STARTED` | approved `PRELIMINARY_EXAMINATION_SOURCE / DocumentEvidenceVersion` | `PROSECUTION_MANAGEMENT / PRELIMINARY_EXAMINATION / APPLICATION_PENDING / CONFIRMED`; legacy `PRELIM_EXAM` |
| Register publication / `PUBLICATION_NOTICE_RECORDED` | approved `PUBLICATION_NOTICE / DocumentEvidenceVersion` | `PROSECUTION_MANAGEMENT / PUBLISHED / APPLICATION_PENDING / CONFIRMED`; legacy `PUBLISHED` |
| Start substantive examination / `SUBSTANTIVE_EXAMINATION_STARTED` | approved `SUBSTANTIVE_EXAMINATION_SOURCE / DocumentEvidenceVersion` | `PROSECUTION_MANAGEMENT / SUBSTANTIVE_EXAMINATION / APPLICATION_PENDING / CONFIRMED`; legacy `SUB_EXAM` |

The demo documents are visibly fictional inputs from the customer-authorized bundle. They prove
the software's ordered evidence processing for a fictional case; the presenter must not describe
them as a real filing, official receipt or real legal status.

The external-submission command uses operation code `EXTERNAL_SUBMISSION_RECORDED`, server-checked
naive `occurred_at`, the approved final submission version and its manual external-submission
activity. Filing receipt archive requires same-case reviewed bytes/hash, `received_at`,
`archive_status=ARCHIVED` and a receipt kind in `RECEIPT_PDF|MERGED_PDF|ELECTRONIC_APPLICATION_RECEIPT`.
The acceptance/preliminary/publication/substantive/OA evidence adapters accept only
`{evidence_version_id, effective_at, occurred_at?, idempotency_key}`; the evidence supplies role
and case. OA metadata additionally carries exact `official_due_date=YYYY-MM-DD`,
`official_due_date_source=MANUAL_OFFICIAL_NOTICE|IMPORTED_OFFICIAL_NOTICE`,
`official_due_date_status=CONFIRMED`, sequence 1 and an inbound executable OA template code.
`PRELIMINARY_EXAMINATION_PASSED` is deliberately absent because the frozen lifecycle graph does
not require it between preliminary examination and publication.

## 6. Runtime bundle v1

### 6.1 Packaging and activation

The external directory contains exactly `manifest.json` and allowlisted files below `templates/`
and `evidence/`. It is never committed as production input. The loader accepts it only when all of
the following are exact:

- `FPMS_ENV=demo`;
- `FPMS_DEMO_SCOPE=LOCAL_ABC_E2E`;
- a non-empty `FPMS_DEMO_RUN_ID`;
- an explicit bundle path outside product storage;
- an external expected SHA-256 of the exact raw `manifest.json` bytes;
- the reviewed specification reference and content digest recorded by the manifest.

Import means offline validation into a content-addressed, read-only run location. Activation means
startup-time validation and an immutable in-process snapshot. There is no hot reload or mutation
API. A changed bundle requires a new run ID and process restart. Rollback selects a previous exact
path/digest and starts a new run; it never rewrites prior business history.

The process must fail before migration/seed and before opening a port when a required bundle is
missing or invalid. All three v1 capabilities are required. A later request for any capability
outside the exact allowlist returns `409 DEMO_INPUT_CONFIG_REQUIRED` with no business write; that
request failure can never substitute for the startup gate.

### 6.2 Exhaustive manifest contract

`manifest.json` is UTF-8 without BOM, uses LF and ends with one LF. The external digest is
`sha256(raw_manifest_bytes)`; the loader never reserializes JSON to compute it. Parsing rejects
duplicate keys, unknown keys and unknown enum values. The exhaustive v1 shape is:

Angle-bracket strings below are schema metavariables, not literal bundle values; `or null` means
the JSON null value, never the text `"null"`.

```json
{
  "schema_version": "fpms.demo-input-bundle/v1",
  "bundle_id": "<1..64 lowercase ASCII [a-z0-9._-]>",
  "bundle_version": "<1..64 ASCII [A-Za-z0-9._-]>",
  "classification": "DEMO_ONLY",
  "purpose": "LOCAL_ABC_E2E",
  "valid_from": "<YYYY-MM-DD>",
  "valid_until": "<YYYY-MM-DD, not before valid_from>",
  "authority": {
    "decision_ref": "<1..240 repository-relative path>",
    "decision_version": "<1..120 identifier>"
  },
  "provenance": {
    "label_zh_cn": "<1..120 characters>",
    "source_ref": "<1..240 characters>",
    "source_version": "<1..120 characters>",
    "source_sha256": "<64 lowercase hex>"
  },
  "contract": {
    "ref": "docs/superpowers/specs/2026-08-15-fpms-local-demo-abc-design.md",
    "sha256": "<SHA-256 of exact adopted specification bytes>"
  },
  "capabilities": [
    "FICTIONAL_LIFECYCLE_EVIDENCE",
    "INTERNAL_TEMPLATE_PREVIEW",
    "SERVICE_PRICE_TO_OBLIGATION"
  ],
  "templates": [{
    "consumer": "DOCUMENT_RENDER",
    "template_code": "<1..64 uppercase ASCII [A-Z0-9_]>",
    "group": "INTERNAL_DEMO",
    "language": "zh-CN",
    "path": "templates/<normalized filename>.docx",
    "media_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "size_bytes": 1,
    "sha256": "<64 lowercase hex>",
    "required_variables": ["<unique sorted names matching [a-z][a-z0-9_]{0,63}>"]
  }],
  "evidence": [{
    "role": "<one exact required lifecycle role>",
    "title_zh_cn": "<1..120 characters>",
    "classification": "FICTIONAL_DEMO_EVIDENCE",
    "path": "evidence/<normalized filename>.pdf",
    "media_type": "application/pdf",
    "size_bytes": 1,
    "sha256": "<64 lowercase hex>",
    "metadata": {
      "effective_at": "<YYYY-MM-DDTHH:MM:SS or null>",
      "received_at": "<YYYY-MM-DDTHH:MM:SS or null>",
      "receipt_kind": "<RECEIPT_PDF|MERGED_PDF|ELECTRONIC_APPLICATION_RECEIPT or null>",
      "official_due_date": "<YYYY-MM-DD or null>",
      "official_due_date_source": "<MANUAL_OFFICIAL_NOTICE|IMPORTED_OFFICIAL_NOTICE or null>",
      "official_due_date_status": "<CONFIRMED or null>",
      "oa_sequence": 1,
      "source_template_code": "<1..64 uppercase ASCII [A-Z0-9_] or null>"
    }
  }],
  "rates": [{
    "domain": "SERVICE_DEMO_PRICE",
    "item_code": "<1..64 uppercase ASCII [A-Z0-9_]>",
    "name_zh_cn": "<1..120 characters>",
    "currency": "CNY",
    "calc_mode": "FIXED",
    "amount": "<positive decimal string with exactly two fractional digits>",
    "source_ref": "<1..240 characters>",
    "source_version": "<1..120 characters>",
    "source_sha256": "<64 lowercase hex>",
    "disclaimer_zh_cn": "<1..200 characters>"
  }]
}
```

Arrays contain exactly the shown capability values, one template, one rate and one evidence entry
for each of these eight roles, sorted in this order:
`FILING_FINAL_SUBMISSION`, `FILING_RECEIPT`, `ACCEPTANCE_NOTICE`,
`PRELIMINARY_EXAMINATION_SOURCE`, `PUBLICATION_NOTICE`, `SUBSTANTIVE_EXAMINATION_SOURCE`,
`OA_NOTICE`, `OA_RECEIPT`. No other role or wildcard is legal.
Every PDF visibly says `FICTIONAL_DEMO_EVIDENCE / 仅用于本地虚构演示` on its first page. JSON
numbers are permitted only for `size_bytes` (`1..10485760`) and the exact integer OA sequence 1;
all money is a string. Every metadata key is present. Filing-final and non-OA notice roles have
only `effective_at`; receipt roles have only `received_at/receipt_kind`; OA notice has
`effective_at`, all four official-due-date/sequence/template values; all inapplicable values are
JSON null. The loader validates the adopted specification bytes/hash and the separate
bundle-authority record before it trusts self-declared authority/provenance fields.

The initial bundle contains no official-fee amount. `total_gov=0` means that this scenario has no
official-fee line, not that an unknown official fee was converted to zero.

This design freezes the bundle schema and fail-closed behavior, not the actual template or price.
Product development may use an isolated fixture marked `TEST_ONLY`, but `DEMO_READY` requires an
exact customer-authorized bundle decision recorded in the source registry with actor, approval
time, decision version, raw manifest digest and every template/evidence/rate source digest. The
exact template/evidence bytes, price amount, validity and disclaimer must be part of that approved
bundle. The implementation must not invent those values or promote a development fixture merely
to make the rehearsal pass.

Paths must be normalized relatives beneath the bundle root. Reject `..`, absolute paths,
symlinks, extra files, macro-enabled files, external DOCX relationships, duplicate identities,
variable drift, non-finite numbers, floating-point JSON amounts and hash/size mismatch. The
template itself must carry a visible local-demo marker. Reject a DOCX with more than 200 ZIP
entries, more than 20 MiB total uncompressed bytes or any entry compression ratio above 100:1.

### 6.3 Provider and durable usage lineage

Do not extend or populate `OfficialRateBook`, `ServicePriceBook`, `FeeRate`, `Template` or
`CustomerDecisionGate` with `DEMO_ONLY` data.

The demo provider exposes only the allowlisted template and service-price item. It is not
registered outside the exact demo profile and never falls back to seed or production sources.
For the `OA_NOTICE` evidence role it also exposes the manifest-bound inbound executable semantic
identified by `source_template_code` directly to the dedicated OA evidence adapter; it does not
create or activate a production `Template` row.

Selecting the runtime service item is a real authenticated UI/API action, not bootstrap
enrichment. The adapter resolves and validates the complete immutable item before writing. In one
transaction it appends a fee-lane source activity whose payload/evidence carries bundle ID,
bundle version, manifest hash, item code, item snapshot/hash, amount, currency and disclaimer,
then creates or reuses one SERVICE obligation through the existing obligation service. Existing
customer-instruction and draft-preparation services create the linked draft only after `PAY`.
Same idempotency key and payload reuse the same source/obligation; key drift returns 409.

The source-selection command derives `actor_id` and `occurred_at` from authenticated request/server
context and binds the idempotency record to that actor. Its durable activity stores the manifest
fields under the same bounded names above without truncation. The later `PAY` instruction is a
separate authenticated, actor-bound idempotent command against the exact current obligation; it
persists actor, server time, obligation ID/version and source-activity ID before draft preparation.
A stale/superseded obligation, actor drift or payload drift returns 409/no write.

Template preview is read-only and returns only a visibly demo-marked rendering. It creates no
official document, submission, letter-handoff or email fact.

### 6.4 Durable command identity

Every idempotent write first validates and normalizes its typed fields, then stores a snapshot with
exact operation name, authenticated actor ID and the command fields named in this specification.
IDs have surrounding whitespace rejected; dates use ISO form; CNY decimals use exactly two digits;
set-like ID arrays are de-duplicated and sorted; optional values remain explicit null. The backend
serializes that snapshot with UTF-8, `ensure_ascii=false`, lexicographically sorted object keys,
separators `,` and `:`, and no trailing LF, then stores its SHA-256. Floats, NaN, infinity, omitted
versus null ambiguity and unlisted fields are rejected before hashing. Replay equality compares the
stored snapshot bytes/hash, not a newly interpreted raw request.

### 6.5 Public evidence-review prerequisite

Ordinary upload remains honest: it creates only a DRAFT attachment/evidence candidate and cannot
advance lifecycle. The operator uploads all bundle evidence to the newly created case through UI.
In a separate authenticated browser context, `demo_evidence_reviewer` uses a visible review queue
to compare case, bundle/manifest digest, role, bytes/hash, first-page fictional marker and required
metadata, then approves each exact candidate. Batch UI is allowed for speed, but every item has its
own immutable command/result.

The review service enforces reviewer ID different from uploader/creating actor, current unmodified
attachment bytes, one allowlisted bundle role and actor-bound idempotency. Success stores reviewer,
server time, source attachment ID/hash, bundle ID/version/manifest hash, role and metadata without
truncation. It produces:

- one independently approved `FINAL` filing evidence version for `FILING_FINAL_SUBMISSION`;
- independently approved `FINAL / OFFICIAL_FINAL_PDF` versions for acceptance, preliminary,
  publication, substantive-examination and OA notice roles;
- reviewed filing/OA receipt attachments that can later become the corresponding
  `OfficialWorkPackageReceipt` only through the existing archive actions.

Same key/same candidate returns the same immutable version; same actor as uploader, role/hash
mismatch, changed bytes, stale metadata, command drift or a second owner returns 409/no write.
There is no public arbitrary evidence-version constructor, self-review switch or test-enrichment
fallback. Until this controlled review capability exists, the fresh journey is blocked after
`FILING_PREPARATION_STARTED` and must not be rehearsed as end to end.

## 7. Lifecycle, document and UI reliability

- Filing and OA resolve use existing-first identity; repeated calls do not duplicate packages.
- The ABC-02 ladder is the sole path from the new case to OA eligibility. No generic status editor,
  bootstrap record, direct lifecycle-event endpoint, Playwright request write or legacy projection
  import may substitute for an ordered dedicated adapter.
- Baseline services/APIs expose external-submission and evidence adapters for acceptance,
  preliminary examination, publication and substantive examination, but no complete public UI
  reaches them from fresh evidence. The accepted journey adds visible Simplified-Chinese controls
  on the filing/reviewed-document page. Each control displays the current prerequisite projection,
  exact evidence version/hash and resulting projection before confirmation.
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

The accepted ABC command is deliberately narrower than the plural legacy shape: `draft_ids`
contains exactly one ID, and that draft contains exactly one positive SERVICE fee item for one
case. A multi-draft, multi-case, mixed-fee or multi-item request returns 409/no write in this
closure. General grouped billing and item-level partial allocation require a separate design; no
implementer may invent an allocation rule here.

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
identity. The exact key bytes are UTF-8
`case_id|fee_code|fee_type|year_or_-|currency`, with `-` as the sole no-year sentinel, and the DB
owns a unique constraint on that stored key. Each component rejects `|` and surrounding
whitespace before key construction.

Create returns an authoritative composite containing Offset, Bill status/balance/currency,
PaymentLine allocated/balance/currency, receipt summary and `idempotency_key/reused`. The UI
consumes this transaction result. If transport outcome is uncertain, the UI first queries durable
command state by the exact idempotency key. If that read proves completion it consumes the stored
composite; only an explicit incomplete/not-found result permits replay of the identical key and
payload. An inconclusive reconciliation remains pending and never creates a new intent.

An exact create retry returns the same composite with 201 and `reused=true`. A second intent that
would over-allocate, a stale balance, wrong client/currency or command drift returns 409 and rolls
back every projection. Reverse is not shown live but its 200 response has the same authoritative
shape; affected regressions must prove exact replay restores only once and a different-key second
reverse is rejected.

Reverse acquires the same `PaymentLine -> Bill -> CaseReceipt` lock/CAS boundary, verifies that the
target Offset is active, and in one transaction marks it reversed, restores PaymentLine and Bill
balances/status, reverses the exact CaseReceipt delta, persists `reversed_by/reversed_at` and owns
the reverse idempotency command. Any failure rolls back every mutation. Exact replay returns the
stored composite; command drift, different-key second reverse or a lost concurrent guard returns
409/no write.

Strict schema/format failures return 422, absent resources return 404, deterministic domain
validation such as customer/currency mismatch or amount exceeding a balance retains 400, and 409
is reserved for lifecycle/source consumption, idempotency drift, unique/concurrent ownership or
repeat reversal conflicts. Every 4xx path is no-write.

Read-only reconciliation endpoints are fixed as
`GET /bills/from-drafts/idempotency/{key}`, `GET /payments/idempotency/{key}`,
`GET /offsets/idempotency/{key}` and `GET /offsets/reversals/idempotency/{key}`, under the same
read permission as their resource. They return 200 plus the stored authoritative composite for a
completed command, 202 for a durable in-progress owner and 404 only when no command exists. The UI
waits/reconciles on 202, consumes 200, and may replay the identical mutation only after 404.

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
- The demo scope is one CNY bucket. The backend read contract accepts and applies
  `currency=CNY` before both row selection and `remaining_prepayment_balance` aggregation; the
  queue also applies `has_unapplied_only=true` and displays each `unapplied_amt`. The CNY card never
  totals the first 100 `Payment.amount` rows or includes another currency. A mixed-CNY/USD focused
  test proves bucket isolation.
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

1. `ABC-DEMO-BUNDLE-PARSER`: raw-manifest, path/DOCX/evidence/rate validation and digest binding.
2. `ABC-DEMO-LOCAL-BOOT`: declared dependency, run-ID environment, demo-safe bootstrap and one
   canonical start/reset/stop command.
3. `ABC-DEMO-RUNTIME-PROVIDERS`: template preview and authenticated service-price-to-obligation
   adapter with durable source activity.
4. `ABC-DEMO-EVIDENCE-REVIEW`: distinct-actor upload/review, immutable final versions and visible
   review queue/actions.
5. `ABC-DEMO-LIFECYCLE`: visible evidence adapters and exact client/case, filing prerequisite, OA,
   OA_OUT, receipt and route/evidence reliability.
6. `ABC-FIN-BILL`: source-consumption/idempotency migration, service/API and bill UI.
7. `ABC-FIN-PAYMENT`: truthful payment model/API/UI and idempotency.
8. `ABC-FIN-OFFSET`: atomic allocation/reversal, CaseReceipt identity and projections.
9. `ABC-FIN-ADAPTER-DASH`: strict money contracts and authoritative dashboard.
10. `ABC-DEMO-LIVE-E2E`: one browser-driven seven-checkpoint spec and negative no-write matrix.
11. `ABC-DEMO-READY`: two fresh runs, headed rehearsal, independent High review and operator pack.

Dependency spine:

```text
bundle parser -> local boot -> {runtime provider, evidence review}
runtime provider + evidence review -> lifecycle -> ABC-01..04
runtime provider -> bill -> payment -> offset -> ABC-05..07
lifecycle + finance APIs -> frontend adapters/navigation -> live E2E -> Demo Ready
```

Every product slice uses targeted RED, minimum GREEN, affected regressions, scoped lint/type/diff,
an atomic commit and independent review appropriate to its risk. A discovered problem outside the
slice becomes a separate blocker story; it does not reopen this design.

## 12. Verification and acceptance

The final targeted gate must prove:

1. clean declared-dependency import and one-command bundle-preflight/migrate/bootstrap/start;
2. a missing/invalid bundle or any missing required capability exits before database
   creation/migration/seed and before ports open; separately, a request outside the validated
   allowlist returns `409 DEMO_INPUT_CONFIG_REQUIRED` with zero business writes;
3. all seven checkpoints use real Vue, API and SQLite. Every checkpoint business mutation is
   performed through a visible UI control; Playwright request APIs are read-only after-state
   verification. There is no `page.route` response mock, direct database write, lifecycle
   enrichment, fixed downstream object ID or skipped checkpoint;
4. two distinct authenticated browser contexts prove uploader/reviewer separation; DRAFT evidence
   cannot drive lifecycle and every approved version binds the bundle/source bytes and reviewer;
5. ABC-02 reaches every exact projection in order, and repeated resolve, bundle selection,
   obligation/draft command, bill creation, payment creation and offset command are safe under
   exact replay;
6. missing/out-of-order/unreviewed lifecycle evidence, self-review, wrong OA
   deadline/source/receipt, bundle hash/version/item, draft state/source, payment
   customer/currency/reference and offset amount produce the expected 4xx and no partial write;
7. one locked draft creates one bill; one payment plus one active offset settles it; all reloaded
   balances and statuses agree;
8. route A-to-B and commit-then-drop reconciliation do not target or display the wrong object;
9. the exact live spec passes on two different fresh run IDs, followed by one headed operator
   rehearsal;
10. candidate SHA/tree, bundle manifest/file hashes, run IDs, object IDs, screenshots, request IDs,
   focused results and cleanup receipts are recorded without token/password/full-HAR leakage;
11. an independent High reviewer returns zero findings for the exact integrated demo scope.

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
- General production evidence-ingestion/approval administration; this closure exposes only the
  bundle-bound fictional local-demo review path and does not activate its evidence outside demo.
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
