# FPMS-V8-FO-CONTRACTS-20260712-01

Status: PASS — ULTRA CONTRACT FROZEN 2026-07-13
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `12. Wave 4 — fee-obligation module and fixed rules`
Catalog ordinal: `102`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `530`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Task Contract Profile

Task Contract Profile: `TC-INTERFACE`

- RED expectation: Exact contract test fails because the named type/enum/interface is absent.
- GREEN expectation: Exact contract test and task-scoped Ruff pass.

## Ultra Contract Freeze — 2026-07-13

This section removes the remaining interface ambiguity without changing the closure slice,
non-closure boundary, allowlist, story shape or `P0-single-lane-story` runbook. The High
implementation must create one dependency-free Python value-contract module at
`app.modules.fees.obligation_contracts`; persistence models, transaction/session types,
FastAPI/Pydantic schemas and business adapters remain outside this interface.

### Public representation and construction rules

- Every enum below is a `str, Enum` with member name equal to its wire/storage value.
- Every value, command and result type below is a
  `@dataclass(frozen=True, slots=True)`. There are no mutable collection fields; repeated
  values use `tuple[...]`.
- Field names, field order and annotations below are exact. Optional annotations do not
  authorize implicit values: callers explicitly pass `None`; the dataclasses define no
  business defaults and generate no identifiers or timestamps.
- Python contracts use `Decimal` for every amount/ratio, `date` for business dates and
  `str` for application UUIDs. Floats are forbidden. HTTP adapters later serialize
  decimals as strings; this module does not stringify or quantize them.
- Every application `_id` is a canonical hyphenated UUID string supplied by the caller or
  service. The one inherited exception is `gov_payment_id: int`, matching the existing
  `GovPayment` carrier. This module neither imports `UUID` nor validates/generates IDs.
- `currency` is an explicit uppercase ISO-4217 string and has no implicit `CNY` default.
  `obligation_type` and estimate `trigger` remain explicit strings because their complete
  customer/business vocabularies are not frozen by V8.

### Exact enum vocabulary and initial states

The seven fee states are independent. No enum member or initial value implies a transition
in any other enum.

| Public enum | Exact members / values | Initial contract |
| --- | --- | --- |
| `FeeEstimateStatus` | `ESTIMATE` | A preview result is always `ESTIMATE`; an obligation snapshot uses `None` when no linked estimate fact exists. |
| `FeeObligationStatus` | `RECOGNIZED`, `SUPERSEDED` | A newly recognized real obligation is `RECOGNIZED`. |
| `FeeClientInstructionStatus` | `PENDING`, `PAY`, `HOLD`, `ABANDON` | A new obligation is `PENDING`; this means no customer instruction has been recorded. |
| `FeeObligationDraftStatus` | `NOT_CREATED`, `CREATED` | A new obligation is `NOT_CREATED`. `CREATED` records only the existence of linked draft items; it is not existing `FeeDraftStatus.OPEN/LOCKED`. |
| `FeePayListStatus` | `NOT_CREATED`, `CREATED` | A new obligation is `NOT_CREATED`. `CREATED` records only a linked PayList fact and does not imply export, official acceptance or payment. |
| `FeePaymentStatus` | `UNPAID`, `PAID` | A new obligation is `UNPAID`; payment never changes official-evidence state. |
| `FeeOfficialEvidenceStatus` | `PENDING`, `VERIFIED`, `NOT_APPLICABLE` | A new `GOV` obligation is `PENDING`; a new `SERVICE` obligation is `NOT_APPLICABLE`. |

Supporting enums are also frozen:

| Public enum | Exact members / values | Meaning |
| --- | --- | --- |
| `FeeDomain` | `GOV`, `SERVICE` | The two separately sourced/approved fee domains; legacy `MISC` is not an obligation domain. |
| `FeeClientInstruction` | `PAY`, `HOLD`, `ABANDON` | Write actions only; `PENDING` is deliberately not an action. |
| `FeeSourceStatus` | `VERIFIED`, `REVIEW_REQUIRED`, `LEGACY_UNVERIFIED` | Source-verification fact; no member authorizes a draft or payment. |
| `FeeDifferenceReviewState` | `MATCHED`, `SOURCE_PENDING`, `REVIEW_REQUIRED` | Independent rate/source comparison fact. Missing values are not converted to zero or `MATCHED`. |

This is the complete foundation vocabulary for this interface. Adding a status value or
reusing a legacy adapter status requires a separately approved contract change; service
tasks may validate transitions but may not invent new strings.

### Exact value shapes

`FeeEstimateContext`

| Field | Annotation |
| --- | --- |
| `trigger` | `str` |
| `source_document_id` | `str | None` |

`FeeEstimateSource` preserves the existing fee-rate/source metadata required by the frozen
frontend probe and remains separate from a recognized obligation source.

| Field | Annotation |
| --- | --- |
| `rate_id` | `str | None` |
| `source_document_id` | `str | None` |
| `source_doc` | `str | None` |
| `source_url` | `str | None` |
| `source_policy` | `str | None` |
| `source_version` | `str | None` |
| `status` | `FeeSourceStatus` |

`FeeObligationSource`

| Field | Annotation |
| --- | --- |
| `source_activity_id` | `str` |
| `source_document_id` | `str | None` |
| `status` | `FeeSourceStatus` |

`source_activity_id` is the pre-existing same-case lifecycle/document source event retained
by W1-F1/F2. It is not the later recognition activity returned by the recognition result.

`FeeObligationStatuses` is the one grouped value used by obligation results and detail
reads. Its seven fields remain independently populated.

| Field | Annotation |
| --- | --- |
| `estimate_status` | `FeeEstimateStatus | None` |
| `obligation_status` | `FeeObligationStatus` |
| `client_instruction_status` | `FeeClientInstructionStatus` |
| `draft_status` | `FeeObligationDraftStatus` |
| `pay_list_status` | `FeePayListStatus` |
| `payment_status` | `FeePaymentStatus` |
| `official_evidence_status` | `FeeOfficialEvidenceStatus` |

`FeeObligationLineInput` is the exact caller-supplied business snapshot for preview and
recognition. It deliberately contains no persistence ID, audit field or computed current
identity.

| Field | Annotation |
| --- | --- |
| `fee_code` | `str` |
| `fee_name` | `str` |
| `fee_year_key` | `int` |
| `official_full_amount` | `Decimal | None` |
| `reduction_ratio` | `Decimal` |
| `payable_amount` | `Decimal` |
| `source_amount` | `Decimal | None` |
| `source_date` | `date | None` |
| `difference_review_state` | `FeeDifferenceReviewState` |

`FeeObligationLine` is the read/result shape aligned to W1-F2, excluding persistence-only
audit timestamps/actors.

| Field | Annotation |
| --- | --- |
| `id` | `str` |
| `obligation_id` | `str` |
| `case_id` | `str` |
| `source_activity_id` | `str` |
| `fee_code` | `str` |
| `fee_name` | `str` |
| `fee_year_key` | `int` |
| `official_full_amount` | `Decimal | None` |
| `reduction_ratio` | `Decimal` |
| `payable_amount` | `Decimal` |
| `source_amount` | `Decimal | None` |
| `source_date` | `date | None` |
| `difference_review_state` | `FeeDifferenceReviewState` |
| `current_identity_key` | `str | None` |

`FeeEstimateCandidate`

| Field | Annotation |
| --- | --- |
| `line` | `FeeObligationLineInput` |
| `source` | `FeeEstimateSource` |

`FeeEstimate` is the preview result; it must not gain an `obligation_id`, draft ID,
activity ID or persistence audit field.

| Field | Annotation |
| --- | --- |
| `case_id` | `str` |
| `estimate_status` | `FeeEstimateStatus` |
| `trigger_context` | `FeeEstimateContext` |
| `currency` | `str` |
| `candidates` | `tuple[FeeEstimateCandidate, ...]` |
| `total_payable_amount` | `Decimal` |

`FeeObligation` is the recognized/read result aligned to W1-F1/F2 plus the separately
derived estimate and PayList facts. The latter two do not become new F1 columns.

| Field | Annotation |
| --- | --- |
| `id` | `str` |
| `case_id` | `str` |
| `source` | `FeeObligationSource` |
| `fee_domain` | `FeeDomain` |
| `obligation_type` | `str` |
| `due_date` | `date | None` |
| `currency` | `str` |
| `statuses` | `FeeObligationStatuses` |
| `lines` | `tuple[FeeObligationLine, ...]` |
| `supersedes_obligation_id` | `str | None` |
| `supersede_reason` | `str | None` |

Link results expose the concrete W1-F3/F4 identity and whether that exact unique pair was
reused; they do not duplicate amount, case or downstream status.

`FeeDraftItemLinkResult`

| Field | Annotation |
| --- | --- |
| `id` | `str` |
| `obligation_line_id` | `str` |
| `fee_item_id` | `str` |
| `reused` | `bool` |

`FeePaymentEvidenceLinkResult`

| Field | Annotation |
| --- | --- |
| `id` | `str` |
| `obligation_line_id` | `str` |
| `gov_payment_id` | `int` |
| `reused` | `bool` |

### Exact command/result interfaces

All transactions remain caller-owned implementation arguments and are intentionally absent
from these pure values. The later module functions consume these commands together with a
caller-owned transaction/session at the implementation seam.

`PreviewFeeEstimateCommand -> FeeEstimate`

| Command field | Annotation |
| --- | --- |
| `case_id` | `str` |
| `trigger_context` | `FeeEstimateContext` |
| `currency` | `str` |

Preview has no actor, idempotency key or write result because it is strictly read-only.

`RecognizeFeeObligationCommand -> RecognizeFeeObligationResult`

| Command field | Annotation |
| --- | --- |
| `case_id` | `str` |
| `source_activity_id` | `str` |
| `source_document_id` | `str | None` |
| `fee_domain` | `FeeDomain` |
| `obligation_type` | `str` |
| `due_date` | `date | None` |
| `currency` | `str` |
| `source_status` | `FeeSourceStatus` |
| `lines` | `tuple[FeeObligationLineInput, ...]` |
| `actor_id` | `str` |
| `idempotency_key` | `str` |
| `supersedes_obligation_id` | `str | None` |
| `supersede_reason` | `str | None` |

| Result field | Annotation |
| --- | --- |
| `obligation` | `FeeObligation` |
| `activity_id` | `str` |
| `idempotency_key` | `str` |
| `reused` | `bool` |
| `superseded_obligation_id` | `str | None` |

Here `reused=True` means the same idempotency key and same canonical payload returned the
already-recognized obligation/activity. A different payload under the same key is a later
409 service rule. A correcting command supplies both supersede fields; the result reports
the actual prior header in `superseded_obligation_id`. Line current identity remains exactly
`sha256(case_id|source_activity_id|fee_code|fee_year_key)` and is returned as lowercase
hex on the effective line; `source_activity_id` in that formula is the command's pre-existing
same-case source lifecycle/document event. Result `activity_id` is instead the distinct
appended/reused `FEE_OBLIGATION_RECOGNIZED` FEE-lane activity. Superseded historical lines
return `current_identity_key=None`.

`RecordFeeObligationInstructionCommand -> RecordFeeObligationInstructionResult`

| Command field | Annotation |
| --- | --- |
| `obligation_id` | `str` |
| `instruction` | `FeeClientInstruction` |
| `actor_id` | `str` |
| `idempotency_key` | `str` |

| Result field | Annotation |
| --- | --- |
| `obligation` | `FeeObligation` |
| `activity_id` | `str` |
| `idempotency_key` | `str` |
| `reused` | `bool` |

`reused=True` has the same-key/same-payload meaning. Recording `PAY`, `HOLD` or `ABANDON`
changes only the instruction fact/activity; the result must not synthesize a draft.

`PrepareFeeObligationDraftCommand -> PrepareFeeObligationDraftResult`

| Command field | Annotation |
| --- | --- |
| `obligation_id` | `str` |
| `actor_id` | `str` |
| `idempotency_key` | `str` |

| Result field | Annotation |
| --- | --- |
| `obligation_id` | `str` |
| `draft_id` | `str` |
| `links` | `tuple[FeeDraftItemLinkResult, ...]` |
| `activity_id` | `str` |
| `activity_reused` | `bool` |
| `idempotency_key` | `str` |

Per-link `reused` reports the exact W1-F3 pair outcome; `activity_reused` independently
reports reuse of `FEE_DRAFT_CREATED`. No result field implies PayList or payment.

`RecordFeePaymentEvidenceCommand -> RecordFeePaymentEvidenceResult`

| Command field | Annotation |
| --- | --- |
| `obligation_id` | `str` |
| `obligation_line_ids` | `tuple[str, ...]` |
| `gov_payment_id` | `int` |
| `actor_id` | `str` |

| Result field | Annotation |
| --- | --- |
| `obligation` | `FeeObligation` |
| `links` | `tuple[FeePaymentEvidenceLinkResult, ...]` |

For payment evidence, the exact `(obligation_line_id, gov_payment_id)` W1-F4 pair is the
idempotency/reuse identity; no unsupported free-form idempotency column is invented. A
payment link may change only `payment_status`. It must not change or imply
`official_evidence_status`, and this result owns no official-receipt/ticket activity.

### Validation boundary

- Enum construction supplies only closed-vocabulary validation. The dataclasses have no
  `__post_init__`, parsing, normalization, hashing, arithmetic, database access or side
  effects.
- Contract tests assert exact exports, enum values, dataclass field order/annotations,
  frozen/slots immutability, tuple collections and the absence of persistence/framework
  imports or methods.
- Later pure-rule/service tasks own: non-empty/UUID/currency validation; `fee_year_key=0`
  versus positive annual years; Decimal scale/sign/arithmetic and fee-reduction rules;
  source confirmation; same-case checks; non-empty line sets; supersede-pair validation;
  current-key hashing/rotation; state transitions; idempotency conflicts; and transaction
  rollback. This contracts module must not pre-implement those tasks.
- Persistence-only W1 audit timestamps/actors stay on ORM carriers. This pure interface
  carries `actor_id` only on write commands and must not import or expose ORM models.

### Exact `__all__`

`obligation_contracts.py` must define `__all__` as this exact tuple in this order, with no
additional public contract:

```python
__all__ = (
    "FeeDomain",
    "FeeEstimateStatus",
    "FeeObligationStatus",
    "FeeClientInstructionStatus",
    "FeeObligationDraftStatus",
    "FeePayListStatus",
    "FeePaymentStatus",
    "FeeOfficialEvidenceStatus",
    "FeeClientInstruction",
    "FeeSourceStatus",
    "FeeDifferenceReviewState",
    "FeeEstimateContext",
    "FeeEstimateSource",
    "FeeObligationSource",
    "FeeObligationStatuses",
    "FeeObligationLineInput",
    "FeeObligationLine",
    "FeeEstimateCandidate",
    "FeeEstimate",
    "FeeObligation",
    "FeeDraftItemLinkResult",
    "FeePaymentEvidenceLinkResult",
    "PreviewFeeEstimateCommand",
    "RecognizeFeeObligationCommand",
    "RecognizeFeeObligationResult",
    "RecordFeeObligationInstructionCommand",
    "RecordFeeObligationInstructionResult",
    "PrepareFeeObligationDraftCommand",
    "PrepareFeeObligationDraftResult",
    "RecordFeePaymentEvidenceCommand",
    "RecordFeePaymentEvidenceResult",
)
```

### Frozen RED / GREEN contract

- RED imports every name in the exact `__all__`, asserts the enum member/value sets and
  exact dataclass fields/annotations above, constructs representative preview/recognize/
  instruction/draft/payment values, proves frozen mutation fails, and proves the module
  imports only Python standard-library contract dependencies. It must initially fail
  because `app.modules.fees.obligation_contracts` is absent.
- GREEN implements only those enums/dataclasses/`__all__`; no helper function, protocol,
  ORM/Pydantic model, validation method, persistence call or service behavior is authorized.
- This freeze makes the task executable for High implementation. It is not implementation
  evidence, independent review or a PASS claim; task status remains `READY / NOT STARTED`.

## Exact Closure Slice

Define obligation/line/status/source and command/result interface only.

## Explicit Non-Closure

No persistence, business adapter, endpoint or UI. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-W1-F1-FEE-OBLIGATION-CARRIER-20260712-01`
- `FPMS-V8-W1-F2-FEE-OBLIGATION-LINE-CARRIER-20260712-01`
- `FPMS-V8-W1-F3-OBLIGATION-DRAFT-LINK-CARRIER-20260712-01`
- `FPMS-V8-W1-F4-OBLIGATION-PAYMENT-EVIDENCE-LINK-CARRIER-20260712-01`
- `FPMS-V8-W1-F5-FEE-REDUCTION-APPROVAL-CARRIER-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): F1–F5

### Shared ownership serialization

- No shared ownership chain beyond the global serialized SQLite verification queue.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-FO-CONTRACTS-20260712-01.md`
- `backend/app/modules/fees/obligation_contracts.py`
- `backend/tests/test_v8_fee_obligation_contracts.py`
- `artifacts/FPMS-V8-FO-CONTRACTS-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_fee_obligation_contracts.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_fee_obligation_contracts.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/fees/obligation_contracts.py tests/test_v8_fee_obligation_contracts.py && .venv/bin/ruff format app/modules/fees/obligation_contracts.py tests/test_v8_fee_obligation_contracts.py && .venv/bin/ruff check app/modules/fees/obligation_contracts.py tests/test_v8_fee_obligation_contracts.py`
- `git diff --check -- backend/app/modules/fees/obligation_contracts.py backend/tests/test_v8_fee_obligation_contracts.py tasks/postdemo/v8/FPMS-V8-FO-CONTRACTS-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-FO-CONTRACTS-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-FO-CONTRACTS-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-FO-CONTRACTS-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FO-CONTRACTS-20260712-01` pass. Only then may this task be reported PASS.
