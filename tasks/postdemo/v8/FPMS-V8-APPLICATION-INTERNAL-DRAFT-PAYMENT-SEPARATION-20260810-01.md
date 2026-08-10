# FPMS-V8-APPLICATION-INTERNAL-DRAFT-PAYMENT-SEPARATION-20260810-01

Status: CONTRACT FROZEN / PRODUCT NOT STARTED / MANIFEST REBIND REQUIRED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Successor of: `FPMS-V8-APPLICATION-AUTO-DRAFT-POLICY-20260712-01`
Executor role: Backend Developer / worker
Repository risk: `HIGH`

## Authority and Design References

- `AGENTS.md`
- `docs/agents/README.md`
- `docs/agents/execution.md`
- `docs/agents/evidence.md`
- `docs/agents/domain-safety.md`
- `docs/agents/source-authority.md`
- `docs/product/v8/customer-decisions/2026-08-10-v8-full-batch-scheme-a.txt`
- `docs/product/v8/source-decision-registry.md`, decision
  `DEC-V8-FULL-BATCH-SCHEME-A-20260810`
- `docs/product/v8/stories/V8-FULL-BATCH-CUSTOMER-DECISION-CURRENT-ADOPTION.md`
- `docs/product/v8/reviews/V8-APPLICATION-FEE-NOTICE-OBLIGATION-CURRENT-ADOPTION.md`
- `tasks/batches/FPMS-POSTDEMO-V8-APPLICATION-DRAFT-GATE-20260712-01.md`
- `tasks/postdemo/v8/FPMS-V8-APPLICATION-DRAFT-SUCCESSOR-ACTIVATION-20260810-01.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`

Frozen customer authority:

- Gate identity: `DG-FEE-APPLICATION-DRAFT:GLOBAL`
- Decision value: `APPROVED_POLICY`
- Decision version: `customer-decision:2026-08-10:v8-full-batch-scheme-a:v1`
- Decision source:
  `docs/product/v8/customer-decisions/2026-08-10-v8-full-batch-scheme-a.txt`
- Decision source SHA-256:
  `e6cfd648f1d366e27bde3f74310f00033a6db60ce55d850d2e668764745faace`
- Trigger: `reviewed-real-application-fee-notice`
- Result: `one-internal-pending-review-draft`
- Payment boundary: `client-instruction-required`

The current application-draft manifest names the superseded product task. Before any product
edit, `FPMS-V8-APPLICATION-DRAFT-SUCCESSOR-ACTIVATION-20260810-01` must be re-frozen to this
corrected task hash, independently accepted at HIGH, and reach terminal PASS after replacing that
row with this exact task path while retaining the frozen source/version/hash and two-task lane
shape. The old and successor product rows must never both execute. Until that exact binding has a
terminal PASS receipt, this task is product-blocked; this task file alone does not activate runtime
behavior.

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`
- One worker owns the complete slice. Do not split its five shared source files across concurrent
  implementers because the authority, instruction and payment guards form one acceptance unit.

## Why the Superseded Contract Is Insufficient

Calling `prepare_draft` from the notice adapter alone is unsafe. The accepted deep service
currently requires `PAY` before draft creation; after a pre-PAY draft exists, the current
instruction compare-and-set rejects later `PAY`, while the existing pay-list path treats linked
draft items as payment candidates without rechecking client instruction. The successor therefore
closes the smallest complete boundary: authority-specific draft creation, later explicit `PAY`,
and payment creation gated by that `PAY`.

## Exact Closure Slice

For one exact persisted, current Scheme A global decision and one real application-fee notice
whose official evidence graph has already passed the existing strict review validation:

1. Recognize/reuse the `GOV` / `APPLICATION_FEE` obligation through the existing
   `recognize_application_fee_notice_obligation` adapter.
2. In the same caller-owned transaction, create/reuse exactly one existing-model internal
   `FeeDraft(status="OPEN", draft_type="GENERIC")`, its `FeeItem` rows, obligation-line links and
   one `FEE_DRAFT_CREATED` activity. The obligation remains
   `client_instruction_status=PENDING`, `payment_status=UNPAID`, and
   `official_evidence_status=PENDING`.
3. Permit the existing `record_client_instruction` service to record a later explicit `PAY` for
   only that exact auto-draft graph, without creating, replacing or mutating the draft graph.
4. Reject pay-list/payment creation for every linked obligation lacking persisted explicit `PAY`
   before any `PayList`, `GovPayment` or activity write.
5. Preserve lifecycle-overlay readability for both the accepted PAY-first draft activity and the
   new reviewed-notice draft activity, with schema-specific payload and predecessor validation.

Recognition and draft creation are one atomic policy action: failure after recognition but before
draft completion rolls back both. Exact replay and concurrent attempts reuse the same obligation,
draft, items, links and activity; they never create a second draft or duplicate activity.

## Frozen Public Interfaces

### Draft authority contract

`backend/app/modules/fees/obligation_contracts.py` adds exactly:

```python
class FeeDraftAuthority(str, Enum):
    CLIENT_PAY_INSTRUCTION = "CLIENT_PAY_INSTRUCTION"
    REVIEWED_APPLICATION_FEE_NOTICE = "REVIEWED_APPLICATION_FEE_NOTICE"


@dataclass(frozen=True, slots=True)
class PrepareFeeObligationDraftCommand:
    obligation_id: str
    actor_id: str
    idempotency_key: str
    authority: FeeDraftAuthority = FeeDraftAuthority.CLIENT_PAY_INSTRUCTION
```

The default is mandatory. It preserves every existing caller and freezes all ordinary draft paths
to the current PAY-first behavior. No boolean, free-form string, nullable authority or generic
policy bypass is permitted. `FeeDraftAuthority` is added exactly once to
`obligation_contracts.__all__`; the existing exact-export contract test is updated only for that
new public enum and defaulted command field.

### Application policy entrypoint

`backend/app/modules/documents/fee_linking_service.py` adds exactly:

```python
@dataclass(frozen=True, slots=True)
class ApplicationFeeAutoDraftPolicyResult:
    recognition: RecognizeFeeObligationResult
    draft: PrepareFeeObligationDraftResult


def apply_application_fee_auto_draft_policy(
    *,
    transaction: Session,
    source: ApplicationFeeNoticeSource,
    review_activity_id: str,
    reviewed_evidence_version_id: str,
    reviewer_id: str,
    official_preview: FeeEstimate,
    as_of: datetime,
    confirmed_pct_evidence: tuple[ConfirmedPctEvidence, ...] = (),
) -> ApplicationFeeAutoDraftPolicyResult:
    ...
```

The entrypoint must:

- first validate the caller-owned notice carrier and canonical hash through the existing strict
  carrier validator. Malformed type, fields, bytes or caller-supplied canonical hash retain
  `APPLICATION_FEE_NOTICE_SOURCE_INVALID` with status `400`; they are not relabelled as stored-state
  conflicts;
- after caller validation but before decision-gate read, transaction connection or savepoint,
  reject `transaction.new`, `transaction.dirty` or `transaction.deleted` with the existing
  `FEE_OBLIGATION_TRANSACTION_DIRTY` status `409`. The dirty-session test must prove the gate and
  both business writers were never called;
- establish a real SQLite outer `BEGIN` before the gate read and policy savepoint when the driver
  connection is not already in a transaction, using a task-local private helper with the same
  semantics as the accepted obligation-service SQLite helper; do not expose a new public API;
- call the existing `resolve_decision_gate` with
  `DecisionGateCode.FEE_APPLICATION_DRAFT`, `scope_key="GLOBAL"`, and the exact caller-supplied
  naive `as_of` value;
- require the returned gate to resolve to `GLOBAL`, with decision value `APPROVED_POLICY`, the
  frozen decision source path and frozen decision version above; missing, revoked, future,
  corrupt, fallback, source-mismatched or version-mismatched authority is `409` and zero write;
- rely on the independently accepted manifest/adoption bytes for the frozen source SHA; do not
  add runtime filesystem hashing or a second decision store;
- enter one policy savepoint only after the gate succeeds, then call the existing strict notice
  recognition adapter and `prepare_draft` with
  `authority=FeeDraftAuthority.REVIEWED_APPLICATION_FEE_NOTICE`;
- use `reviewer_id` as the draft actor and the exact deterministic draft idempotency key
  `application-fee-auto-draft:{reviewed_evidence_version_id}:{source.due_date_source}`;
- never call `commit()` or `rollback()` and never convert an error into a partial success. A fault
  after recognition and caller rollback must remove both recognition and draft even on SQLite.

`recognize_application_fee_notice_obligation` remains public and unchanged for existing callers;
calling it alone continues to recognize without creating a draft.

### Deep prepare-draft behavior

`prepare_draft(command, transaction)` keeps its signature and result type. Its two authority modes
are exhaustive:

- `CLIENT_PAY_INSTRUCTION`: byte-for-behavior compatible with the accepted current path, including
  PAY eligibility, activity source, `FPMS_FEE_DRAFT_CREATED_V1` payload, errors, idempotent replay
  and compare-and-set behavior.
- `REVIEWED_APPLICATION_FEE_NOTICE`: actionable only for the exact persisted
  `GOV` / `APPLICATION_FEE`, `VERIFIED` / `RECOGNIZED`, instruction `PENDING` with no instruction
  activity, draft `NOT_CREATED`, payment `UNPAID`, official evidence `PENDING` graph produced from
  the current reviewed-notice recognition chain. The current recognition, source document,
  source activity and current obligation lines must be unique and mutually consistent; a caller
  supplying the enum is not by itself sufficient authority.

For the reviewed-notice mode, current lines may be only `MATCHED` or `REVIEW_REQUIRED`; mixed
sets are valid because this is a pending-review internal draft. `SOURCE_PENDING`, unknown,
superseded, non-current, duplicate or malformed lines fail `409`. Draft item amounts and totals
copy the persisted notice-authoritative `payable_amount` values exactly; estimates never replace
those values.

The reviewed-notice draft activity remains `FEE_DRAFT_CREATED`, uses the recognition activity as
`source_activity_id`, and uses a new exact schema
`FPMS_FEE_DRAFT_CREATED_FROM_REVIEWED_APPLICATION_NOTICE_V1` with an authority field equal to
`REVIEWED_APPLICATION_FEE_NOTICE`. It must not reuse or weaken the accepted ordinary PAY-draft
payload schema or replay checks. Its exact canonical payload keys are `actor_id`, `authority`,
`center_changes`, `draft_id`, `links`, `obligation_id`, and `schema`; the accepted V1 payload keeps
its exact six keys without `authority`.

Caller validation failures remain `400`. Once caller inputs are valid, any missing, duplicated,
non-current, malformed or mutually inconsistent persisted obligation, recognition, notice-review,
evidence, activity, draft, item or link graph is a `409` stored-authority conflict with zero write.
Do not collapse these two error classes.

### Exact replay after later state

The reviewed-notice `prepare_draft` replay branch must resolve and validate the existing activity
and original draft graph before current actionability checks. Repeating the exact authority,
obligation and idempotency key returns the original draft/items/links/activity with reused flags
even after a later explicit `PAY`, PayList/GovPayment creation, `payment_status=PAID`, or official
evidence verification. Replay observes but never rewinds those later states and performs no write.
A changed command, authority, key payload, activity payload or graph remains an idempotency/stored
state `409`, not a new draft.

### Lifecycle-overlay dual-schema branch

`backend/app/modules/cases/lifecycle_overlay_service.py` keeps the public
`read_lifecycle_overlay` API and output schema unchanged. Its `FEE_DRAFT_CREATED` handling accepts
exactly two closed alternatives:

- `FPMS_FEE_DRAFT_CREATED_V1`: the existing six-key payload and existing direct predecessor
  `FEE_CLIENT_INSTRUCTION_RECORDED`, whose predecessor is the matching
  `FEE_OBLIGATION_RECOGNIZED` activity;
- `FPMS_FEE_DRAFT_CREATED_FROM_REVIEWED_APPLICATION_NOTICE_V1`: the exact seven-key payload above,
  `authority == REVIEWED_APPLICATION_FEE_NOTICE`, and a direct predecessor that is the matching
  `FEE_OBLIGATION_RECOGNIZED` activity.

Schema selection must choose its own exact key set and lineage branch; it must not implement a
union of optional keys. The ordinary schema with a recognition predecessor, reviewed-notice
schema with an instruction predecessor, unknown schema, missing/extra/wrong authority, malformed
payload, or recognition/obligation/source mismatch is
`LIFECYCLE_OVERLAY_FEE_CONFLICT` (`409`). Both valid schemas project the same existing DRAFT fact
without writes.

### Explicit PAY after the internal draft

`record_client_instruction(command, transaction)` keeps its public interface, existing activity
schema and all ordinary eligibility/replay/error semantics. Add one narrow branch only when:

- `command.instruction is FeeClientInstruction.PAY`;
- the obligation and its unique current draft/items/links/activity form the exact valid
  `REVIEWED_APPLICATION_FEE_NOTICE` graph above;
- instruction is still `PENDING`, payment is `UNPAID`, official evidence is not verified, and no
  previous instruction activity exists.

That branch performs only the existing `PENDING -> PAY` status change and appends/reuses the normal
`FEE_CLIENT_INSTRUCTION_RECORDED` activity. It must use a compare-and-set that requires the same
already-created draft graph and must not create, replace, update or delete any draft/item/link or
draft activity. `NO_PAY`, a second instruction, a malformed graph, or any other draft-created
obligation remains locked with the existing `409` boundary.

### PAY-before-payment guard

`create_pay_list_from_fee_items(...)` keeps its public signature and successful response shape.
After resolving all obligation links but before adding/flushing a `PayList`, every selected linked
obligation must have `client_instruction_status == PAY`. Otherwise raise
`PAY_LIST_CLIENT_INSTRUCTION_REQUIRED` with status `409`; the whole call produces zero `PayList`,
zero `GovPayment`, zero `PAY_LIST_CREATED` activity and no other write. All previously valid
explicit-PAY batches and all other existing validation/error behavior remain unchanged.

## Non-Weakenable Invariants

- Never synthesize, infer, backfill or silently record `PAY` from a reviewed notice, decision gate,
  draft, draft item or reviewer action.
- A pre-PAY internal draft never creates or authorizes `PayList`, `GovPayment`, payment evidence,
  export, submission, official receipt, payment status transition or external side effect.
- The accepted notice review/evidence lineage remains mandatory and exact. Preview/estimate data
  cannot become official-fee authority or overwrite notice amounts.
- The decision gate is read before business writes. Every authority, graph, replay or concurrency
  conflict is fail-closed and leaves no partial recognition/draft/payment residue.
- The caller owns the transaction. Services may `flush()` and use nested savepoints, but may not
  `commit()`, `rollback()`, close the session or make caller rollback ineffective.
- One obligation has at most one current draft graph and one applicable draft-created activity.
- Existing `CLIENT_PAY_INSTRUCTION` draft semantics, instruction payload bytes, payment-evidence
  behavior, legacy `/fees/drafts/apply-fee/generate`, future-annuity behavior, grant-year behavior,
  API/status/envelope/permission semantics and unrelated lifecycle state remain unchanged.
- SQLite compatibility and globally serialized SQLite-writing verification are mandatory.

## Explicit Non-Closure

- No authorization-year/grant-year auto-draft implementation; that independently governed lane
  may reuse the explicit-authority pattern only under its own exact contract and evidence.
- No future-annuity exception, service receivable, fee calculation/rate/reduction, payment
  execution, workbook/export, official receipt or payment-evidence change.
- No API, router, UI, permission, schema, migration, model column, enum-backed database status,
  seed or data-repair change. Existing `FeeDraft(status="OPEN")` is sufficient.
- No decision-gate record/read-service change, source/registry/adoption change, manifest or
  coverage-ledger edit in this product task.
- No API/router/runtime-trigger wiring in this task. The callable policy is a service closure only
  and is not end-to-end reachable until the named runtime-adapter follow-up is independently
  contracted, activated and accepted.
- No second entrypoint, generic PENDING-obligation bypass, adjacent refactor, rename, formatting
  sweep, test weakening or unrelated cleanup.

## Dependencies and Activation Gate

Required current accepted prerequisites:

- `FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01`
- `V8-FEE-OBLIGATION-READ-DRAFT-CURRENT-ADOPTION`
- `V8-APPLICATION-FEE-NOTICE-OBLIGATION-CURRENT-ADOPTION`
- terminal independent HIGH PASS of
  `FPMS-V8-APPLICATION-DRAFT-SUCCESSOR-ACTIVATION-20260810-01`, re-frozen to this corrected task
  hash, binding this exact task path and removing the superseded product row
- exact current persisted `DG-FEE-APPLICATION-DRAFT:GLOBAL` Scheme A decision at runtime

Any missing, stale, revoked, conflicting or scope/source/version-mismatched dependency blocks this
task or request; it does not authorize a fallback.

## Shared Ownership and Serialization

This is one HIGH shared-file owner. Acquire all five source files together only after every prior
accepted owner has released them; release them only after this task has independent terminal
acceptance. Do not run the superseded application-auto-draft task.

- `backend/app/modules/fees/obligation_contracts.py`: successor order key `2`, after the accepted
  fee-obligation contracts owner.
- `backend/app/modules/fees/obligation_service.py`: successor order key `9`, after accepted order
  keys `1` through `8`.
- `backend/app/modules/annuity/service.py`: successor order key `13`, after accepted order keys `1`
  through `12`.
- `backend/app/modules/documents/fee_linking_service.py`: successor inherits/replaces application
  auto-draft order key `13`; it does not add a second order-13 owner.
- `backend/app/modules/cases/lifecycle_overlay_service.py`: successor order key `6`, after accepted
  overlay order keys `1` through `5`.

All edits, RED/GREEN runs, targeted SQLite regressions, independent review and evidence close are
serialized. A concurrent owner, unaccepted predecessor, manifest still naming the superseded row,
or changed authority hash is a stop condition, not permission to rebase or absorb work.

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-APPLICATION-INTERNAL-DRAFT-PAYMENT-SEPARATION-20260810-01.md`
- `backend/app/modules/documents/fee_linking_service.py`
- `backend/app/modules/fees/obligation_contracts.py`
- `backend/app/modules/fees/obligation_service.py`
- `backend/app/modules/annuity/service.py`
- `backend/app/modules/cases/lifecycle_overlay_service.py`
- `backend/tests/test_v8_application_auto_draft_policy.py`
- `backend/tests/test_v8_fee_obligation_contracts.py`
- `backend/tests/test_v8_lifecycle_overlay_fees.py`
- `artifacts/FPMS-V8-APPLICATION-INTERNAL-DRAFT-PAYMENT-SEPARATION-20260810-01/**`

No other source, test, task, manifest, ledger or artifact path is authorized. Named inherited
regression tests are read-only inputs. Preserve and subtract the complete initial dirty baseline,
including unrelated tracked and untracked paths.

## Immutable RED Acceptance Matrix

The new test file must first fail against the current implementation and prove all of these missing
behaviors without weakening existing assertions:

1. Exact Scheme A gate plus a valid reviewed real notice creates/reuses one recognized obligation
   and one `OPEN` draft with exact items, links and reviewed-notice activity in one transaction;
   instruction remains `PENDING`, payment remains `UNPAID`, and no instruction/payment facts exist.
2. One success fixture contains both `MATCHED` and `REVIEW_REQUIRED` lines and proves draft amounts
   equal persisted notice amounts. A `SOURCE_PENDING` line is rejected with `409` and zero write.
3. Same-command replay and two serialized/concurrent attempts produce the same obligation, draft,
   items, links and activity with no duplicates.
4. Missing, revoked, future, corrupt, case-scope fallback, decision-value, source-path or version
   mismatch fails `409` before recognition or draft writes.
5. Malformed caller carrier/bytes/hash fails with the existing `400`; after valid caller input,
   unreviewed, cross-case, stale/non-current or corrupted persisted evidence/hash/review activity,
   reference, source document, recognition or draft graph fails `409` with no draft.
6. Dirty caller state fails `409` before gate/connection/savepoint/writer calls. A forced fault
   after recognition and before draft creation and a caller rollback leave no recognition/draft
   residue; the SQLite case proves a real outer transaction exists before the policy savepoint.
7. Creating a pay list from the internal draft before explicit `PAY` raises
   `PAY_LIST_CLIENT_INSTRUCTION_REQUIRED` (`409`) before any PayList/GovPayment/activity write.
8. Explicit `PAY` after auto-draft records exactly one normal instruction activity, preserves the
   same draft/items/links/activity byte-for-byte, and then permits the unchanged pay-list path.
9. `NO_PAY`, repeated/mismatched instruction, non-application draft, arbitrary authority enum use,
   malformed auto-draft activity and non-PAY mixed-item batch all fail closed without a second
   draft or partial payment write.
10. Default `CLIENT_PAY_INSTRUCTION` command construction and the existing PAY-first prepare path
    retain their exact accepted behavior and payload schema.
11. Exact reviewed-notice same-key replay after later explicit `PAY`, PayList/GovPayment,
    `payment_status=PAID` and official-evidence verification returns the original graph/reused flags,
    preserves all later state and performs no write; changed-key/command/graph remains `409`.
12. Lifecycle overlay accepts and projects each exact draft schema through only its matching
    predecessor branch; crossed predecessors, unknown schema, malformed authority/payload and
    persisted recognition mismatch are `409` and read-only.
13. `FeeDraftAuthority` is in the exact contracts `__all__`, its default preserves existing
    construction, and the named read-only draft/detail/instruction API regressions remain unchanged.

## Verification Commands

Initialize evidence only after the successor manifest binding is independently accepted and the
serialized owner receives the execution grant.

- RED, preserve expected failures for the missing service, export and overlay branches before
  product edits:
  `cd backend && .venv/bin/pytest -q tests/test_v8_application_auto_draft_policy.py tests/test_v8_fee_obligation_contracts.py tests/test_v8_lifecycle_overlay_fees.py`
- Canonical GREEN:
  `cd backend && .venv/bin/pytest -q tests/test_v8_application_auto_draft_policy.py tests/test_v8_fee_obligation_contracts.py tests/test_v8_lifecycle_overlay_fees.py`
- Read-only targeted regressions:
  `cd backend && .venv/bin/pytest -q tests/test_v8_decision_gate_read_service.py tests/test_v8_application_fee_notice_obligation.py tests/test_v8_fee_obligation_prepare_draft.py tests/test_v8_fee_obligation_instruction.py tests/test_v8_pay_list_create_activity_adapter.py tests/test_v8_fee_obligation_payment_evidence.py tests/test_v8_generic_fee_draft_activity_adapter.py tests/test_v8_generic_fee_draft_obligation_api.py tests/test_v8_fee_obligation_detail_api.py tests/test_v8_fee_obligation_instruction_api.py`
- Task-owned formatting followed by final check-only lint:
  `cd backend && .venv/bin/ruff check --fix app/modules/documents/fee_linking_service.py app/modules/fees/obligation_contracts.py app/modules/fees/obligation_service.py app/modules/annuity/service.py app/modules/cases/lifecycle_overlay_service.py tests/test_v8_application_auto_draft_policy.py tests/test_v8_fee_obligation_contracts.py tests/test_v8_lifecycle_overlay_fees.py && .venv/bin/ruff format app/modules/documents/fee_linking_service.py app/modules/fees/obligation_contracts.py app/modules/fees/obligation_service.py app/modules/annuity/service.py app/modules/cases/lifecycle_overlay_service.py tests/test_v8_application_auto_draft_policy.py tests/test_v8_fee_obligation_contracts.py tests/test_v8_lifecycle_overlay_fees.py && .venv/bin/ruff check app/modules/documents/fee_linking_service.py app/modules/fees/obligation_contracts.py app/modules/fees/obligation_service.py app/modules/annuity/service.py app/modules/cases/lifecycle_overlay_service.py tests/test_v8_application_auto_draft_policy.py tests/test_v8_fee_obligation_contracts.py tests/test_v8_lifecycle_overlay_fees.py`
- Scope check:
  `git diff --check -- tasks/postdemo/v8/FPMS-V8-APPLICATION-INTERNAL-DRAFT-PAYMENT-SEPARATION-20260810-01.md backend/app/modules/documents/fee_linking_service.py backend/app/modules/fees/obligation_contracts.py backend/app/modules/fees/obligation_service.py backend/app/modules/annuity/service.py backend/app/modules/cases/lifecycle_overlay_service.py backend/tests/test_v8_application_auto_draft_policy.py backend/tests/test_v8_fee_obligation_contracts.py backend/tests/test_v8_lifecycle_overlay_fees.py`
- Task gate:
  `./scripts/task_validate.sh FPMS-V8-APPLICATION-INTERNAL-DRAFT-PAYMENT-SEPARATION-20260810-01`
- Atomic evidence:
  `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-APPLICATION-INTERNAL-DRAFT-PAYMENT-SEPARATION-20260810-01 --required-step lint --required-step test --required-step independent_review --required-step scope --required-step task_gate`

No repo-wide tests, broad Playwright, release gate or unrelated formatter run belongs to this task.

## Evidence Path

Evidence path:

- `artifacts/FPMS-V8-APPLICATION-INTERNAL-DRAFT-PAYMENT-SEPARATION-20260810-01/**`

Required PASS evidence:

- `task.json`, `results.jsonl`, `summary.md`, `git/diff.patch`, all command logs, and complete dirty
  baseline artifacts;
- preserved RED proving the exact current failure, followed by one canonical GREEN and the complete
  targeted regression command above, all against the final candidate;
- explicit assertions/counts proving zero pre-PAY `PayList`, `GovPayment`, payment evidence and
  payment/instruction activity, plus dirty-order, SQLite rollback, post-payment replay,
  concurrency and overlay read-only residue counts;
- scope evidence covering tracked and untracked allowlist state and identifying every concrete
  outside-dirty path;
- one independent HIGH reviewer, not the implementer, with one final `Verdict: APPROVED`,
  `P0: 0`, `P1: 0`, `P2: 0`, binding the final baseline-subtracted patch hash and current task and
  summary hashes;
- latest successful `lint`, `test`, `scope`, `independent_review`, `task_gate` and
  `atomic_evidence` results. SQLite-writing checks must record global serialized execution.

## Remaining Follow-Up Task IDs

- `FPMS-V8-APPLICATION-INTERNAL-DRAFT-RUNTIME-ADAPTER-20260810-01` — separately materialize and
  activate the exact existing reviewed-application-notice runtime/API/worker seam that invokes
  `apply_application_fee_auto_draft_policy`; freeze its permission, request/response, commit/
  rollback and idempotency behavior without duplicating this service logic.

The independently governed grant-year auto-draft row also remains outside this task. Neither the
runtime adapter nor grant-year behavior may be represented as reachable or completed by this
service-task evidence.

## Done Definition

The exact named successor activation, re-frozen to the current corrected task hash, has terminal
independent HIGH PASS; the exact RED is preserved; the
minimum allowlisted implementation makes the complete immutable matrix GREEN; all named read-only
regressions, scoped lint, scope and task gates pass; caller rollback, no-PAY/no-payment,
idempotency, post-payment replay, lifecycle-overlay and concurrency evidence are current; shared
files and SQLite runs were serialized;
the independent HIGH review has zero findings and binds current hashes; atomic evidence validates.
Only then may the implementation task report PASS for its service closure. It must not claim
runtime/API reachability; that remains the named follow-up. Contract correction alone may report
only `CORRECTED_CONTRACT_READY`.
