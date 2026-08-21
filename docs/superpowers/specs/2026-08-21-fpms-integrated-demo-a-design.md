# FPMS Integrated Demo A Design

Date: 2026-08-21
Status: REVIEW
Risk: PROTECTED / HIGH
Baseline candidate: `1bb329bf5fb2dfdae3c5771ea7f04a83f632bb20`

## 1. Outcome

The upcoming customer demonstration uses one fictional client and one fictional case to show the
complete prior V7 lifecycle journey and then continue, without changing identity, into the newly
accepted runtime-input and customer-finance journey. The presentation must make the three weeks of
remediation observable: lineage stays explicit, invalid actions make no write, retries do not
duplicate facts, and the final financial projections agree.

The accepted technical terminal state is `INTEGRATED_TECHNICAL_REHEARSAL_PASS`. Customer-specific
template or price truth additionally requires an exact customer-authorized runtime bundle. Without
that external input, the presentation may use only visibly labelled `SYNTHETIC_TEST_ONLY` data and
must say that the amount and document are fictional demo inputs.

This design is not product release, production readiness, security acceptance, PostgreSQL
acceptance, remote deployment, official submission or official-fee activation.

## 2. Authority and customer decision

The exact customer messages preserved in
`docs/product/v8/customer-decisions/2026-08-21-integrated-demo-a.txt` require the upcoming demo to
cover both the prior demonstration and the new changes and then confirm selected Scheme A.

This successor preserves the business intent of:

- `docs/postdemo/postdemo_p1_v7_ui_e2e_success_runbook_20260711.md`;
- `docs/superpowers/specs/2026-08-15-fpms-local-demo-abc-design.md`;
- the accepted local ABC candidate and seventh independent High review.

Where an old V7 expectation conflicts with the current source/fee boundary, the successor keeps
the customer-visible workflow but uses the current fail-closed rule. In particular, a historical
hard-coded amount, fixture or enrichment cannot stand in for an official fee or customer-approved
service price.

## 3. Approaches considered

### 3.1 One client, one case, one continuous journey — selected

Run the former lifecycle and new finance chapters on the same dynamic case. This is the clearest
proof that the refactoring connects business work to receivables and settlement. It requires the
strongest identity and state assertions but is the only approach that fully satisfies the customer
request.

### 3.2 Same build, two independent cases — rejected

Run the previous V7 story and ABC finance story independently. It is easier to rehearse, but it
does not prove that the lifecycle and financial changes compose on one case.

### 3.3 Preserve the old story as screenshots or video — rejected

This reduces live risk but cannot establish that the previous behavior still works on the current
candidate.

## 4. Runtime topology and identities

- Work only in a clean isolated worktree and bind every rehearsal to one exact commit and tree.
- Use loopback API/UI, a new `FPMS_DEMO_RUN_ID`, fresh SQLite file and fresh storage directory for
  each run. Never connect to a shared or production database.
- Standard seed may create authentication and static master data only. It may not create the
  presentation client, contact, case, lifecycle documents, work packages, tasks, obligations,
  drafts, bills, payments, offsets or receipts.
- Every presentation business object is created by a visible UI action or the same public API
  invoked by that UI. Route mocks, request interception, direct database insertion and lifecycle
  enrichment are forbidden.
- One authenticated demo administrator performs the visible journey. Evidence review continues to
  require a different actual reviewer where the current product contract requires actor
  separation; no authentication or permission bypass is introduced.
- All customer-visible labels and errors introduced for the journey are Simplified Chinese.

## 5. Integrated checkpoint contract

The live presentation may compress narration, but the canonical rehearsal executes and records all
checkpoints below in order.

| ID | Prior/new mapping | Visible action | Required observable result |
| --- | --- | --- | --- |
| `IA-00` | preflight | Start a fresh local run with the exact bundle digest and candidate identity. | Bundle classification, version, hash and disclaimer are visible; database/business counts start at zero; readiness opens only after validation. |
| `IA-01` | `V7-01` | Create the fictional client and primary contact. | Exactly one dynamic client/contact identity and correct ownership. |
| `IA-02` | `V7-02` | Create one domestic invention case for that client. | Case is reloadable and initially `NOT_FILED`; package, task, draft, bill, payment and offset counts are zero. |
| `IA-03` | `V7-03` | Open the document wizard and official-document catalog. | Template request succeeds without 422; all 60 catalog rows are visible; one executable example can be located and one reference-only example is visibly disabled. |
| `IA-04` | `V7-04` | Resolve filing preparation twice. | Both actions return the same filing package; preparation does not claim official filing or advance legal status. |
| `IA-05` | `V7-05` | Complete the reviewed fictional filing-evidence ladder, then record first OA with exact confirmed deadline and resolve it twice. | Ordered evidence identities are visible; one OA source/package/task exists; the same complete due-date date/source/status triple appears on create response, read, content-only edit, impact preview and wizard recall; repeated resolve reuses the same package/task. Missing or changed deadline truth rejects with no write. |
| `IA-06` | `V7-06` | Create OA_OUT linked to the first OA source/package. | OA_OUT linkage is unique; the OA task remains `OPEN`; package awaits receipt. |
| `IA-07` | `V7-07` | Exercise cross-case and same-case-wrong-source receipt attempts in the automated gate; optionally show one concise Chinese rejection live. | Both attempts are rejected and source/package/task/case/receipt counts are byte-for-byte unchanged. |
| `IA-08` | `V7-08` | Upload the correct receipt, refresh/check the OA package and archive it. | Package is `ARCHIVED`; exactly the first OA task becomes `DONE`; no other task closes; case returns exactly to `PROSECUTION_MANAGEMENT / SUBSTANTIVE_EXAMINATION / APPLICATION_PENDING / CONFIRMED` (legacy `SUB_EXAM`). |
| `IA-09` | `V7-09` | Create and complete a second OA using new source/package/task/OA_OUT/receipt identities. | Every second-OA identity differs from the first; its own task alone closes; first-OA history remains immutable; case again returns exactly to `PROSECUTION_MANAGEMENT / SUBSTANTIVE_EXAMINATION / APPLICATION_PENDING / CONFIRMED` (legacy `SUB_EXAM`). |
| `IA-10` | `V7-10` | Record a reviewed fictional grant-registration notice with exact confirmed source/date. | One source-linked grant task is created; projection is exactly `GRANT_REGISTRATION_IN_PROGRESS / GRANT_REGISTRATION / APPLICATION_PENDING / CONFIRMED`; no fee draft appears automatically and no patent-in-force conclusion is claimed. |
| `IA-11` | `V7-11` | Replace the grant source/task through the public replacement action. | Old source/task is visibly superseded; exactly one current task remains actionable; lineage shows old and new identities; the exact grant-registration projection remains unchanged. |
| `IA-12` | `V7-12` | Against the superseded task attempt direct draft preparation, batch customer instruction, notice generation and status mutation; then record the customer's `PAY` instruction on the current task. | Each of the four old-task mutation classes is disabled or returns 409/no-write with unchanged counts/state; the current instruction persists once. Missing official-fee authority creates no official fee item, obligation, draft or amount. |
| `IA-13` | `V7-13` successor + ABC runtime input | Select the exact runtime service-price item for the same case, create/reuse its obligation, record `PAY`, prepare and lock the service draft. | Bundle/version/hash/item/disclaimer are visible; exactly one SERVICE obligation and one linked `LOCKED` draft exist; service amount equals the bundle. No official fee item, obligation, draft or amount exists; the UI shows `未配置` and excludes official fees from every total. |
| `IA-14` | ABC bill | Create the AR bill and repeat the same intent. | Exactly one AR bill consumes the locked service draft/item; replay returns the same bill; it starts `UNSETTLED` with the exact CNY balance. |
| `IA-15` | ABC payment | Record one equal CNY bank receipt and repeat the same intent. | Exactly one payment and one payment line exist; before offset it is `UNALLOCATED`; target bill is a suggestion, not a false applied link. |
| `IA-16` | ABC offset | Offset the payment line to the AR bill. | Exactly one active offset; bill becomes `SETTLED/0.00`; payment becomes `FULLY_ALLOCATED/0.00`; canonical case receipt equals the service amount. |
| `IA-17` | new integrated summary | Reload case lifecycle, tasks, fee draft, bill, payment and case-finance views. | All displayed IDs, states, amounts and currency agree with authoritative responses; no stale route object or synthetic zero appears. |
| `IA-18` | `V7-14` successor | Present the final four-dimensional lifecycle/finance summary and perform exact cleanup. | Checkpoint ledger is 19/19; dynamic IDs and screenshots are indexed; only the exact run root is removed; no child process or port remains. |

### 5.1 Filing prerequisite ladder

`IA-05` retains the current approved evidence-driven order; it cannot jump directly from filing
preparation to OA:

1. reviewed final submission version;
2. fictional external-submission record;
3. reviewed filing receipt and archive;
4. reviewed acceptance notice;
5. preliminary-examination source;
6. publication notice;
7. substantive-examination source;
8. first OA notice with exact confirmed due-date triple.

Every step must read back the same case/evidence identity before the next write. These inputs prove
only product behavior for a fictional case; they are not claims of a real filing or real legal
status.

### 5.2 Exact lifecycle projections

The checkpoint ledger records all four values after every lifecycle event. `CONFIRMED` below is the
lifecycle verification state, not authority for any fee or external legal fact.

| Event/checkpoint | Exact projection after success | Legacy display |
| --- | --- | --- |
| case opened / `IA-02` | `NEW_CASE / NOT_SUBMITTED / NOT_ESTABLISHED / CONFIRMED` | `NOT_FILED` |
| filing preparation / `IA-04` | `FILING_PREPARATION / NOT_SUBMITTED / NOT_ESTABLISHED / CONFIRMED` | `NOT_FILED` |
| fictional external submission | `WAITING_EXTERNAL_RECEIPT / SUBMITTED_WAITING_RECEIPT / NOT_ESTABLISHED / CONFIRMED` | `WAITING_RECEIPT` |
| filing receipt archived | `PROSECUTION_MANAGEMENT / SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE / APPLICATION_PENDING / CONFIRMED` | `WAITING_RECEIPT` |
| acceptance notice recorded | `PROSECUTION_MANAGEMENT / ACCEPTED / APPLICATION_PENDING / CONFIRMED` | `ACCEPTED` |
| preliminary examination started | `PROSECUTION_MANAGEMENT / PRELIMINARY_EXAMINATION / APPLICATION_PENDING / CONFIRMED` | `PRELIM_EXAM` |
| publication recorded | `PROSECUTION_MANAGEMENT / PUBLISHED / APPLICATION_PENDING / CONFIRMED` | `PUBLISHED` |
| substantive examination started | `PROSECUTION_MANAGEMENT / SUBSTANTIVE_EXAMINATION / APPLICATION_PENDING / CONFIRMED` | `SUB_EXAM` |
| first OA notice recorded (`oa_sequence=1`) | `OA_REPLY_IN_PROGRESS / OFFICE_ACTION_RESPONSE / APPLICATION_PENDING / CONFIRMED` | `OA1` |
| second OA notice recorded (`oa_sequence=2`) | `OA_REPLY_IN_PROGRESS / OFFICE_ACTION_RESPONSE / APPLICATION_PENDING / CONFIRMED` | `OA2` |
| either OA receipt archived | `PROSECUTION_MANAGEMENT / SUBSTANTIVE_EXAMINATION / APPLICATION_PENDING / CONFIRMED` | `SUB_EXAM` |
| grant-registration notice recorded or exact source replacement | `GRANT_REGISTRATION_IN_PROGRESS / GRANT_REGISTRATION / APPLICATION_PENDING / CONFIRMED` | `GRANT_PENDING` |

`IA-12` through `IA-17` do not change this lifecycle projection. A grant announcement or patent
register confirmation is not part of Scheme A and cannot be narrated from the grant-registration
notice.

### 5.3 V7 successor coverage ledger

| Prior checkpoint | Successor checkpoint | Preserved contract |
| --- | --- | --- |
| `V7-01` | `IA-01` | UI-created client and primary contact |
| `V7-02` | `IA-02` | UI-created case and exact initial four-state tuple |
| `V7-03` | `IA-03` | wizard request, 60-row catalog, executable/reference gate |
| `V7-04` | `IA-04` | filing-package existing-first resolve |
| `V7-05` | `IA-05` | confirmed deadline across create/read/edit/impact-preview/wizard surfaces |
| `V7-06` | `IA-06` | OA_OUT linkage while task stays open |
| `V7-07` | `IA-07` | cross-case and wrong-source receipt no-write gates |
| `V7-08` | `IA-08` | valid receipt archives one package and closes one task |
| `V7-09` | `IA-09` | independent later OA lineage and closure |
| `V7-10` | `IA-10` | grant-registration notice, exact projection, no automatic draft |
| `V7-11` | `IA-11` | source/task replacement and single actionable successor |
| `V7-12` | `IA-12` | four superseded-task mutation gates and current customer instruction |
| `V7-13` | `IA-13` | blocked enrichment replaced by validated runtime SERVICE input; no official-fee inference |
| `V7-14` | `IA-18` | evidence summary, exact non-goals and cleanup |

### 5.4 Fee and runtime-input correction to the prior demo

The old V7 flow expected a later fee draft but its blocked enrichment had no safe source. Scheme A
replaces that gap with a visible runtime boundary:

- grant-task `PAY` proves the customer-instruction and superseded-task behavior;
- no official amount is inferred from a historical fixture or service rate;
- the runtime bundle supplies one separately labelled SERVICE price on the same case;
- that service obligation and locked draft are the only source consumed by the AR bill;
- the presentation states explicitly that a service receivable is not an official government fee.

## 6. Error handling and recovery

- Missing, malformed, unapproved or changed runtime bundle: fail before business services open, or
  return `409` with no write when a capability is unavailable.
- Incomplete deadline/source/status, wrong-case/wrong-source receipt, superseded grant task, OPEN
  or already consumed draft, duplicate bank identity, client/currency mismatch, over-allocation or
  idempotency drift: deterministic 4xx and zero side effects.
- Unknown transport outcome: query the durable command by its immutable intent key. Completed
  intent returns its stored result; pending intent is polled within the bounded contract; a
  deterministic rejection is never masked by an older result.
- A failed checkpoint preserves its run directory and evidence and stops that rehearsal. The next
  attempt uses a new run ID; it does not repair facts directly in SQLite.

## 7. Presentation shape

The customer presentation has two connected chapters:

1. **业务办理** — `IA-01` through `IA-12`: client/case, filing, two independent OA cycles,
   receipt archive, grant source replacement and customer instruction.
2. **收费回款** — `IA-13` through `IA-17`: runtime service price, locked draft, unique bill,
   bank receipt, offset and consistent summary.

Negative/concurrency probes remain in the automated gate so the live narrative is not dominated by
test mechanics. The presenter may show one receipt rejection and one idempotent replay because they
make the refactoring visible without lengthening the story materially.

## 8. Acceptance and evidence

Technical acceptance requires all of the following on one exact candidate:

The terminal finance proof is one unique AR bill, one bank receipt and one full offset. Evidence
must bind two distinct per-run identity sets rather than replaying or cleaning a shared fixture.

1. focused backend lifecycle, lineage, fee and finance contract tests pass;
2. focused frontend route-identity, command-reconciliation, strict-money and integrated-journey
   contracts pass;
3. a static test rejects `page.route`, `route.fulfill`, direct DB business writes, lifecycle
   enrichment, fixed business IDs and skipped checkpoints in the canonical browser spec;
4. the canonical visible Chromium spec executes `IA-00` through `IA-18` on a fresh isolated run;
5. the same spec passes twice with different run, client, case, OA, task, draft, bill, payment,
   offset and receipt identities;
6. each run retains checkpoint results, request/object identities, authoritative postconditions,
   key screenshots, process/port metadata and exact cleanup receipt;
7. all artifacts are checksum-bound to candidate commit/tree and contain no password, token, PII,
   full HAR or customer-secret bytes;
8. an independent High reviewer of the exact candidate and evidence returns `APPROVED` with
   `P0/P1/P2 = 0/0/0` for the integrated local technical scope.

Actual customer activation additionally requires an immutable customer-authorized runtime bundle
and authority record whose manifest/files/digests pass the existing activation contract. The
synthetic technical bundle cannot confer that authority.

## 9. Implementation slicing rule

Implementation planning starts by running the integrated browser contract against the accepted ABC
candidate and recording a contract-complete RED. Existing behavior that already passes receives no
product diff. Each real blocker becomes one separately materialized atomic task with its own exact
allowlist and evidence. Shared lifecycle services, migrations, routers, frontend API/types/routes
and SQLite-writing checks are serialized. The plan cannot reopen general architecture or absorb
production/security/release work.

## 10. Rollback and non-goals

Each implementation task is one atomic commit. A failed integration is rolled back with `git
revert` of the exact task commit; reset, stash, clean and deletion of unrelated artifacts are
forbidden. Each rehearsal uses a disposable exact run root, so rollback never rewrites historical
business data.

Explicit non-goals remain: real external submission, CPC/RPA, real official receipt or legal-state
claim, official payment, PayList, annuity, bad debt, dunning, commission, refund, multi-currency,
production PostgreSQL migration, public hosting, security remediation, broad product gate and
release approval.
