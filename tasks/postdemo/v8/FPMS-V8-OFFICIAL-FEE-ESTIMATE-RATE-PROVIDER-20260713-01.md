# FPMS-V8-OFFICIAL-FEE-ESTIMATE-RATE-PROVIDER-20260713-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01` (`V8`)
Wave: `M4 — foundation external prerequisites`
Phase: `foundation_external_prerequisite` (outside the immutable baseline)
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-13-fpms-v8-ultra-contract-freeze-delta.md`
- `docs/superpowers/plans/2026-07-13-fpms-v8-ultra-contract-materialization.md`
- `tasks/postdemo/v8/FPMS-V8-FO-PREVIEW-ESTIMATE-20260712-01.md`
- `tasks/postdemo/v8/FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01.md`
- `tasks/postdemo/v8/FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01.md`
- Materialization row: `12`
- Expected manifest phase: `foundation_external_prerequisite`
- Immutable baseline membership: `outside`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high — the activation task owns the same production file first.
- `prereq_dependency_density`: high — preview contract, activation and approval records must be PASS first.
- `be_fe_coupling`: low — this closure is a backend read provider; HTTP remains a follow-up.
- `evidence_cost`: high — interval, provenance, reduction and no-write branches require SQLite evidence.
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-SERVICE`

- RED expectation: The exact provider test fails because the production Protocol implementation is absent.
- GREEN expectation: The exact provider and inherited preview tests pass and prove deterministic fail-closed reads with no mutation.

## Exact Closure Slice

Add exactly one read-only `SqlAlchemyOfficialFeeEstimateRateProvider(Session)` implementation of the existing `OfficialFeeEstimateRateProvider` Protocol that resolves only the baseline `FILING_ACCEPTED` and `REEXAM_REQUESTED` trigger candidates from one trusted effective CNIPA rate book, its linked rates, exact Case facts and any uniquely applicable confirmed fee-reduction approval.

## Ultra Contract Freeze — 2026-07-13

This is the complete High implementation contract for this one provider closure. The
initial implementation owns only the two already-existing baseline trigger mappings. It
does not consume or activate any V8 layout-design, patent-term-compensation,
compensation-period-annuity or open-license special-rate rule.

### Frozen public Python interface

`backend/app/modules/fees/official_rate_book.py` must expose this synchronous production
class and no second provider implementation:

```python
class SqlAlchemyOfficialFeeEstimateRateProvider:
    def __init__(self, transaction: Session) -> None: ...

    def select_rate_candidates(
        self,
        *,
        command: PreviewFeeEstimateCommand,
        rate_effective_on: date,
    ) -> tuple[OfficialFeeEstimateRateCandidate, ...]: ...
```

- The class structurally implements the existing
  `OfficialFeeEstimateRateProvider` Protocol from
  `backend/app/modules/fees/obligation_service.py`; do not duplicate, widen or replace
  the Protocol, its DTOs, `FeeEstimatePreviewErrorCode` or `FeeEstimatePreviewError`.
- The constructor accepts the caller-owned exact SQLAlchemy `Session` and retains no
  mutable cache or process-global state. It does not open or close a session.
- The method remains keyword-only and returns an exact tuple of the existing frozen
  `OfficialFeeEstimateRateCandidate` DTO in the display order frozen below.
- No repository abstraction, async variant, clock dependency, second callable or legacy
  response dictionary is authorized.

### Exact supported triggers and Case facts

The supported trigger vocabulary is closed in this initial provider:

1. exact `FILING_ACCEPTED`;
2. exact `REEXAM_REQUESTED`.

Every other syntactically valid trigger raises `TRIGGER_UNSUPPORTED` with exactly
`{"trigger": command.trigger_context.trigger}` before any rate-book or approval query.
This explicitly includes every layout-design registration/reexamination/restoration/
bibliographic-change/extension/nonvoluntary-license/remuneration-adjudication trigger,
every patent-term-compensation or compensation-period-annuity trigger, and every
open-license trigger, even if rows for those codes happen to exist. They remain disabled
until their separate rate-rule and obligation/provider-adapter tasks are PASS and a later
atomic provider-extension contract explicitly admits them.

For either supported trigger, load exactly one `Case` by the exact, unmodified
`command.case_id`. The provider reads only these Case fields:

- `id`, `case_type`, `flow_dir`, `patent_category`;
- `claim_count` and `has_exam_request` for `FILING_ACCEPTED`;
- `fee_reduction` as the sole stored reduction-ratio input.

The initial mapping supports only `case_type == "NORMAL"`,
`flow_dir == "CN_DOMESTIC"` and exact patent categories `INV`, `UM` or `DES`.
`PCT_INTL`, `PCT_NATL`, any PCT/non-domestic case or any other category is rejected;
the provider must not infer domestic filing rates from international identifiers or PCT
dates. PCT fee policy remains a separate integration task.

`claim_count` must have exact non-boolean integer type and be at least zero.
For `INV`, `has_exam_request` must be exact `bool`; only `True` admits the substantive
examination line. No missing field is coerced to zero or false. Case absence or an
unsupported/malformed Case fact raises `CANDIDATE_INVALID` with exactly
`{"fee_code": None, "fee_year_key": 0, "field": <Case-field-name>}`. The later HTTP
adapter may perform its own Case existence preflight to preserve its frozen 404; this
provider introduces no new service error code.

### Exact baseline trigger-to-rate mapping

Every candidate has `fee_year_key=0`. Required fee codes and output order are exact:

#### `FILING_ACCEPTED`

1. Application fee selected by `Case.patent_category`:
   - `INV` -> `CN_INV_APPLICATION_FEE`;
   - `UM` -> `CN_UM_APPLICATION_FEE`;
   - `DES` -> `CN_DES_APPLICATION_FEE`.
2. If and only if `Case.claim_count > 10`,
   `CN_EXCESS_CLAIM_FEE`, whose returned full-line amount is the linked unit
   `FeeRate.default_amount * (Case.claim_count - 10)`.
3. For `INV` only, `CN_PUBLICATION_PRINT_FEE`.
4. For `INV` only and only when `Case.has_exam_request is True`,
   `CN_SUBSTANTIVE_EXAM_FEE`.

The application, publication-print and substantive-examination rates must have exact
`calc_mode == "FIXED"`; the excess-claim rate must have exact
`calc_mode == "PER_CLAIM"`. No `calc_params`, fee name/category/subtype text or legacy
helper may change this mapping. A count of ten produces no excess-claim line.

#### `REEXAM_REQUESTED`

Return exactly one fixed candidate selected by `Case.patent_category`:

- `INV` -> `CN_REEXAM_FEE_INV`;
- `UM` -> `CN_REEXAM_FEE_UM`;
- `DES` -> `CN_REEXAM_FEE_DES`.

The selected row must have exact `calc_mode == "FIXED"`. The provider performs no
reexamination-deadline, source-document-state or lifecycle-state decision.

These two baseline mappings are wholly frozen by this provider task. No separate V8
special-rate-rule task is consumed by this initial implementation.

### Trusted rate-book and linked-rate selection

For the caller-supplied `rate_effective_on`, which must be an exact `date` and not a
`datetime`, select exactly one `OfficialRateBook` satisfying all of the following:

- `source_authority == "CNIPA"`, `approval_status == "APPROVED"` and
  `activation_status == "ACTIVE"`;
- `effective_from <= rate_effective_on` and
  `effective_to is None or rate_effective_on <= effective_to`; both ends are inclusive;
- `current_identity_key == f"CNIPA|{book_code}"`;
- `book_code`, `version_code`, `source_version` and `source_reference` are nonblank exact
  strings; `source_reference` is canonical HTTPS on exact host `www.cnipa.gov.cn` with
  no credentials, explicit port, query or fragment;
- the canonical `source_snapshot` and lowercase `source_snapshot_hash` still satisfy the
  activation task's frozen CNIPA trust/hash contract.

Zero effective trusted books is fail-closed; more than one is ambiguous. An effective
candidate book that is not APPROVED/ACTIVE is unapproved, and a malformed trust or
provenance tuple is invalid. Do not select a customer workbook, Tianyue source, legacy
unlinked row or RETIRED/INACTIVE book.

For each required code, select exactly one `FeeRate` linked by
`official_rate_book_id == selected_book.id` with exact `fee_type == "GOV"`,
`currency == "CNY"`, `enabled is True`, the required `calc_mode`, and an inclusive rate
interval containing `rate_effective_on`. `effective_from` is mandatory;
`effective_to=None` is open-ended. The command currency must be exact `CNY`; no currency
conversion or fallback is permitted. The linked rate's `fee_name` must be a nonblank
exact string and `default_amount` must be a finite positive `Decimal` already at two-
decimal precision. Zero matches is missing; multiple matches for one required code is
ambiguous. Do not use `RETURNING`, an unlinked `FeeRate`, or any legacy source fields as a
fallback.

Each returned candidate maps exact fields as follows:

| Candidate field | Exact value |
| --- | --- |
| `fee_code` | selected `FeeRate.fee_code` |
| `fee_name` | selected `FeeRate.fee_name` |
| `fee_year_key` | `0` |
| `official_full_amount` | fixed `FeeRate.default_amount`, or excess-claim unit amount multiplied by the exact excess count |
| `source.rate_id` | selected `FeeRate.id` |
| `source.source_document_id` | `command.trigger_context.source_document_id` |
| `source.source_doc` | selected `OfficialRateBook.source_version` |
| `source.source_url` | selected `OfficialRateBook.source_reference` |
| `source.source_policy` | selected `OfficialRateBook.book_code` |
| `source.source_version` | selected `OfficialRateBook.version_code` |
| `source.status` | `FeeSourceStatus.VERIFIED` |

Provider order is the exact trigger order above. No source field is flattened, replaced
with a rate-row legacy value or omitted.

### Exact reduction and confirmed-approval mapping

- `Case.fee_reduction` is the only reduction-ratio source. It must be an exact stored
  string equal to `"0"`, `"0.7"` or `"0.85"`; do not trim, normalize percentages,
  read `discount_rate`, inspect applicant attributes or infer eligibility.
- Map it to the corresponding `Decimal` and
  `FeeReductionInputProvenance.EXPLICIT_ENTRY`. A rate with
  `allow_reduction is True` receives that explicit ratio. A rate with
  `allow_reduction is False` receives explicit zero and no approval; a null/non-boolean
  `allow_reduction` is invalid.
- Ratio zero requires no approval query and maps `reduction_approval=None`.
- For an allowed-reduction line with ratio `0.7` or `0.85`, select exactly one applicable
  `FeeReductionApproval`: `scope_type == "CASE"`, `case_id == Case.id`, exact ratio,
  `confirmation_status == "CONFIRMED"`, fee-scope snapshot/hash containing the exact
  fee code, non-annual scope with both year bounds `None`, and an inclusive effective
  interval containing `rate_effective_on`. Its source evidence ID, canonical snapshots,
  hashes and confirmation facts must be structurally valid.
- The current carrier has no current/supersede field. Exactly one applicable confirmed
  row is therefore the only basis for setting the existing
  `FeeReductionApprovalContext.is_current=True`. Zero or multiple applicable rows fail
  closed; the provider never chooses newest/oldest, rewrites history or infers replacement.
  `APPLICANT_SET` rows are not applicable until a separate persisted Case-to-applicant-set
  resolution contract exists.
- Map the unique row without loss into the existing `FeeReductionApprovalContext`, with
  `fee_codes` parsed from its verified canonical fee-scope snapshot. Build
  `FeeReductionEvaluationContext` from exact Case ID, `applicant_set_key=None`, candidate
  code, `fee_year_key=0` and caller date. The provider does not call
  `validate_fee_reduction`; the existing preview service calls it exactly once.

Missing, ambiguous or malformed required approval mapping raises `CANDIDATE_INVALID`
with exactly `{"fee_code": <required-code>, "fee_year_key": 0,
"field": "reduction_approval"}`. An invalid stored Case ratio uses the same code/detail
shape with `field="fee_reduction"`. No new reduction eligibility or provider error type
is introduced.

### Exact error mapping

The provider raises only the existing `FeeEstimatePreviewError` with an existing
`FeeEstimatePreviewErrorCode`; it must not invent a second exception family.

| Condition | Existing code | Exact details |
| --- | --- | --- |
| trigger other than the two exact values | `TRIGGER_UNSUPPORTED` | `{"trigger": <exact-trigger>}` |
| malformed command currency/date at direct provider use | `INVALID_COMMAND` | `{"field": "currency"}` or `{"field": "rate_effective_on"}` |
| missing/malformed/unsupported Case fact | `CANDIDATE_INVALID` | `{"fee_code": None, "fee_year_key": 0, "field": <field>}` |
| no trusted effective book or no linked rate for a required code | `RATE_MISSING` | `{"fee_code": <required-code>, "fee_year_key": 0, "rate_effective_on": <ISO-date>}` |
| effective book/rate exists but is not APPROVED/ACTIVE | `RATE_SOURCE_UNAPPROVED` | `{"fee_code": <required-code>, "fee_year_key": 0, "rate_id": <id-or-None>}` |
| multiple effective books or linked rates | `RATE_SOURCE_AMBIGUOUS` | `{"fee_code": <required-code>, "fee_year_key": 0, "rate_effective_on": <ISO-date>}` |
| malformed trust, linkage, interval, amount, calc mode or provenance | `RATE_SOURCE_INVALID` | `{"fee_code": <required-code>, "fee_year_key": 0, "field": <field>}` |
| invalid ratio or missing/ambiguous/corrupt approval | `CANDIDATE_INVALID` | `{"fee_code": <code-or-None>, "fee_year_key": 0, "field": "fee_reduction"}` or `field="reduction_approval"` |

When book selection fails before a rate ID exists, use the first required code in the
frozen display order and `rate_id=None`. Validation order is trigger, direct command
currency/date, Case existence/facts, required-code mapping, book selection/trust, each
linked rate in display order, then reduction/approval mapping in display order.

### Deterministic SELECT and no-write plan

Use one fixed read plan and no lazy relationship access:

1. one `SELECT Case ... WHERE Case.id == command.case_id`;
2. one ordered `SELECT` for candidate `OfficialRateBook` rows and their linked
   `FeeRate` rows needed by the frozen required-code tuple;
3. only when an allowed line carries `0.7` or `0.85`, one ordered
   `SELECT FeeReductionApproval` for the Case/ratio/date and then deterministic in-memory
   fee-scope validation for every required reducible line.

All statements have deterministic primary-key tie-break ordering. The provider executes
no query for an unsupported trigger and no approval query for ratio zero. It performs no
`add`, `add_all`, `delete`, object mutation, `flush`, `commit`, `rollback`, `begin`,
`begin_nested`, `close`, DDL, seed call, clock read, UUID generation, file/network access
or legacy helper/fallback. A before/after identity-map and database snapshot must remain
unchanged on success and every error branch.

### Frozen RED / GREEN / no-write test matrix

`backend/tests/test_v8_official_fee_estimate_rate_provider.py` must prove through the
public class:

1. RED is the missing class/constructor/Protocol method; no fake provider satisfies RED.
2. Exact constructor and keyword-only method signature structurally satisfy the existing
   Protocol and return only existing DTO types.
3. `FILING_ACCEPTED` maps INV/UM/DES application codes in exact order, applies the
   above-ten excess unit calculation, includes publication print for INV, and includes
   substantive examination only for exact `has_exam_request=True`.
4. `REEXAM_REQUESTED` maps INV/UM/DES to exactly one corresponding reexamination code.
5. Every other trigger, including representative layout, compensation and open-license
   values, fails before SQL rate/approval lookup; PCT and malformed/missing Case facts
   fail without inferred rates.
6. Exactly one trusted ACTIVE/APPROVED effective CNIPA book is required; interval ends are
   inclusive; absence, overlap, unapproved/retired state, non-CNIPA URL, current-key,
   snapshot/hash and provenance corruption raise the exact frozen code/details.
7. Every required rate must be exactly one enabled linked GOV/CNY row with inclusive
   effective interval, exact calc mode, positive two-place amount and nonblank name;
   missing, duplicate, unlinked, disabled, wrong-currency and malformed rows fail closed.
8. Full-line amounts, `fee_year_key=0`, candidate order and all seven
   `FeeEstimateSource` provenance fields match the exact selected rows/book without
   mutation or flattening.
9. Exact stored ratios `0`, `0.7`, `0.85`, reducible/non-reducible rows and validator DTO
   contexts map exactly. Zero performs no approval query; `0.7/0.85` require one
   applicable confirmed CASE approval; missing, duplicate, wrong ratio/scope/fee/year/
   date/status, corrupt snapshot/hash or APPLICANT_SET-only rows fail closed.
10. SQL spying proves the fixed SELECT order/count and deterministic tie-breaks. Database
    row counts, ORM objects, identity-map dirty/new/deleted sets and transaction state are
    unchanged after success and every error; forbidden transaction/write/clock/UUID/
    network/legacy-helper calls fail the test immediately.
11. The inherited pure preview regression
    `tests/test_v8_fee_estimate_read_only.py` remains green when fed provider candidates;
    the test uses synthetic, explicitly non-authoritative CNIPA fixtures and asserts no
    real legal amount.

GREEN is only the minimum production provider plus this exact test. No API, preview
calculation, obligation or special-rate extension is part of GREEN.

## Explicit Non-Closure

No API/router/schema/migration/seed/UI, HTTP status mapping, preview calculation change,
fee obligation, draft, activity, fee item, PayList, payment, source activation, approval
record creation, customer eligibility inference, PCT fee policy, legacy fallback or
write. Do not implement or consume any V8 layout-design, patent-term-compensation,
compensation-period-annuity or open-license rate rule/adapter, absorb the follow-up HTTP
adapter, add another trigger, or change any existing source/test/task file.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-FO-PREVIEW-ESTIMATE-20260712-01` — existing provider Protocol/DTO/error contract; accepted `PASS` before implementation.
- `FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01` — serialized owner/order key `1`; must be `PASS` before this provider starts.
- `FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01` — exact confirmed approval carrier/writer semantics; must be `PASS` before this provider starts.

### Actually consumed rate-rule dependencies

- None. This initial provider owns only the frozen baseline `FILING_ACCEPTED` and
  `REEXAM_REQUESTED` mapping above and consumes no V8 special-rate-rule task.

### External, gate and inherited prerequisites

- Customer gate: `None`.
- All three canonical dependencies must have accepted PASS evidence and task gates before
  implementation begins; ordering alone is not acceptance.

### Shared ownership serialization

- `backend/app/modules/fees/official_rate_book.py`: source-activation task order key `1`,
  this provider task order key `2`. They must never run concurrently.
- SQLite-writing provider verification runs through the global serialized queue.

## Remaining Follow-Up Task IDs

- `FPMS-V8-FO-PREVIEW-HTTP-ADAPTER-20260712-01`

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-OFFICIAL-FEE-ESTIMATE-RATE-PROVIDER-20260713-01.md`
- `backend/app/modules/fees/official_rate_book.py`
- `backend/tests/test_v8_official_fee_estimate_rate_provider.py`
- `artifacts/FPMS-V8-OFFICIAL-FEE-ESTIMATE-RATE-PROVIDER-20260713-01/**`

No other source, test, task, manifest, schema, migration, seed, API, router or shared
ownership file is authorized. Inherited regressions are read-only. Preserve the captured
dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md SQLite and caller-owned transaction rules; all interval comparisons
  are application/SQLite-safe and inclusive.
- This task owns no endpoint, permission injection, response envelope or HTTP body/status.
- Read only through the caller-owned `Session`; never flush, commit, roll back, close or
  mutate caller-owned ORM objects.

## Verification Commands

- RED: `cd backend && .venv/bin/pytest -q tests/test_v8_official_fee_estimate_rate_provider.py`; run before implementation and preserve the expected missing-production-provider failure.
- GREEN: `cd backend && .venv/bin/pytest -q tests/test_v8_official_fee_estimate_rate_provider.py tests/test_v8_fee_estimate_read_only.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/fees/official_rate_book.py tests/test_v8_official_fee_estimate_rate_provider.py && .venv/bin/ruff format app/modules/fees/official_rate_book.py tests/test_v8_official_fee_estimate_rate_provider.py && .venv/bin/ruff check app/modules/fees/official_rate_book.py tests/test_v8_official_fee_estimate_rate_provider.py`
- Scoped diff: `git diff --check -- backend/app/modules/fees/official_rate_book.py backend/tests/test_v8_official_fee_estimate_rate_provider.py tasks/postdemo/v8/FPMS-V8-OFFICIAL-FEE-ESTIMATE-RATE-PROVIDER-20260713-01.md`
- Task gate: `./scripts/task_validate.sh FPMS-V8-OFFICIAL-FEE-ESTIMATE-RATE-PROVIDER-20260713-01`
- Evidence gate: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-OFFICIAL-FEE-ESTIMATE-RATE-PROVIDER-20260713-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

Expected HTTP status codes: `N/A` — this task owns no HTTP endpoint.

## Evidence Path

- `artifacts/FPMS-V8-OFFICIAL-FEE-ESTIMATE-RATE-PROVIDER-20260713-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, plus dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted provider and exact test make GREEN
and the inherited pure preview regression pass; scoped Ruff/diff and the deterministic
no-write matrix pass; activation/provider shared ownership and SQLite verification are
serialized; baseline-subtracted scope evidence proves no second closure was absorbed;
an independent reviewer approves the exact two-trigger closure and special-rule/PCT/HTTP/
write non-closure; task and evidence gates pass. Only then may this implementation task
be reported PASS.
