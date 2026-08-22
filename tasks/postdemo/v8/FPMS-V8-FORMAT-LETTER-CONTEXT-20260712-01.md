# FPMS-V8-FORMAT-LETTER-CONTEXT-20260712-01

Status: READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-13 / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `11. Wave 2C/3 — document evidence and existing workflow adapters`
Catalog ordinal: `89`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `494`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-SERVICE`

- RED expectation: Exact service/dataset test fails on missing behavior, data or prohibited side effect.
- GREEN expectation: Exact service/dataset test and named inherited regressions pass with caller-owned transaction semantics where writes are transactional.

## Ultra Contract Freeze — 2026-07-13

This section is the complete High implementation contract. It reconciles the customer
workflow Word, the eight rendered customer Word templates, V8 design, accepted carriers
and the earlier blocker without changing the customer workflow or inventing a generic
mail/template engine.

### Exact public contract

`backend/app/modules/documents/letter_context.py` exposes these task-owned types and one
public callable; helpers remain private:

```python
class FormatLetterNoticeVariant(str, Enum):
    REJECTION_DECISION = "REJECTION_DECISION"
    PRELIMINARY_PASS = "PRELIMINARY_PASS"
    PUBLICATION_NOTICE = "PUBLICATION_NOTICE"
    SUBSTANTIVE_ENTRY_NOTICE = "SUBSTANTIVE_ENTRY_NOTICE"
    ACCEPTANCE_NOTICE = "ACCEPTANCE_NOTICE"
    GRANT_REGISTRATION_NOTICE = "GRANT_REGISTRATION_NOTICE"
    OA_FIRST = "OA_FIRST"
    OA_SUBSEQUENT = "OA_SUBSEQUENT"
    REEXAMINATION_NOTICE = "REEXAMINATION_NOTICE"
    PATENT_CERTIFICATE = "PATENT_CERTIFICATE"

@dataclass(frozen=True, slots=True)
class BuildFormatLetterContextCommand:
    case_id: str
    source_document_id: str
    selected_contact_id: str | None = None

@dataclass(frozen=True, slots=True)
class FormatLetterContextResult:
    case_id: str
    source_document_id: str
    source_evidence_version_id: str
    mapping_id: str
    template_id: str
    template_family_code: str
    template_variant_code: str
    template_file_path: str
    notice_variant: FormatLetterNoticeVariant
    selected_contact_id: str | None
    contact_selection_source: str
    salutation_source: str
    context: Mapping[str, str]

def build_format_letter_context(
    command: BuildFormatLetterContextCommand,
    transaction: Session,
) -> FormatLetterContextResult:
    ...
```

- Parameter order and result fields are exact. Do not accept dictionaries, infer a case
  from a document alone or add an optional template/contact policy callback.
- Return `context` as a fresh `types.MappingProxyType` so neither caller nor renderer can
  mutate the reviewed snapshot. Every key and value is `str`.
- The function is read-only: no `add`, `delete`, `flush`, `commit`, `rollback`, clock read,
  UUID generation, rendering, attachment creation, evidence registration or handoff write.
- Expected failures use existing `app.core.errors.BusinessError`; do not create a second
  exception family or import FastAPI.

### Source selection: explicit, IN, current, approved and latest

The command always names the source. The service never silently substitutes another
document. Validate in this exact order:

1. command is the exact frozen type; `case_id`, `source_document_id` and non-null
   `selected_contact_id` are nonempty stripped strings of at most 36 characters;
   otherwise `FORMAT_LETTER_CONTEXT_INVALID` (400) with `details.field`;
2. missing case is `CASE_NOT_FOUND` (404);
3. missing source document is `FORMAT_LETTER_SOURCE_NOT_FOUND` (404);
4. source in another case is `FORMAT_LETTER_SOURCE_CASE_MISMATCH` (400), and a source
   whose normalized `direction` is not exactly `IN` is
   `FORMAT_LETTER_SOURCE_DIRECTION_INVALID` (400);
5. the source must have exactly one current reviewed official-PDF evidence row satisfying
   all of: same case/document, `role=OFFICIAL_FINAL_PDF`, `state=FINAL`,
   `review_state=APPROVED`, and non-null `current_identity_key`. Zero rows is
   `FORMAT_LETTER_SOURCE_UNREVIEWED` (409); more than one is
   `FORMAT_LETTER_SOURCE_EVIDENCE_AMBIGUOUS` (409). Pending/rejected, non-current, draft,
   XML, receipt and client-letter rows never qualify;
6. among all same-case IN documents having that exact eligible evidence shape, the supplied
   document must be the latest by `(doc_date, created_at, id)` descending. A null date is
   ineligible. An older supplied source is `FORMAT_LETTER_SOURCE_NOT_LATEST` (409). Ties
   are resolved by the full deterministic tuple, never by query order.

This implements customer `信函生成操作` P0001–P0003 and V8 §8.4: an explicit latest
official IN source, not an arbitrary OUT document or attachment.

### Mapping, template family and notice variant

Select enabled `FormatLetterMapping` rows in this strict precedence order and take only a
unique winner at the first nonempty level:

1. exact `official_doc_template_id`;
2. exact normalized `official_doc_template_code`;
3. exact stripped `official_doc_name_pattern == Document.title`;
4. stripped name pattern contained in `Document.title`.

No winner is `FORMAT_LETTER_MAPPING_MISSING` (409); multiple winners at the same winning
level is `FORMAT_LETTER_MAPPING_AMBIGUOUS` (409). Lower-precedence matches do not conflict
with one unique higher-precedence winner. Do not reproduce the current silent
"highest score then earliest row" fallback.

The winner must have non-null mapping/template IDs, a code in
`FORMAT_LETTER_001..FORMAT_LETTER_008`, and reference one enabled `Template` with
`group == "FORMAT_LETTER"`, `name == mapping.format_letter_template_code` and a nonempty
file path. Missing/inactive/mismatched rows use `FORMAT_LETTER_TEMPLATE_INVALID` (409).
The result maps `template_family_code="FORMAT_LETTER"` and
`template_variant_code` to that exact template code.

Notice variant is fixed by the winning template and normalized title:

| Template | Allowed notice variant |
| --- | --- |
| `001` | `REJECTION_DECISION` |
| `002` | `PRELIMINARY_PASS` |
| `003` | `PUBLICATION_NOTICE` |
| `004` | `SUBSTANTIVE_ENTRY_NOTICE` |
| `005` | `ACCEPTANCE_NOTICE` |
| `006` | `GRANT_REGISTRATION_NOTICE` |
| `007` | `OA_FIRST`, `OA_SUBSEQUENT`, or `REEXAMINATION_NOTICE` |
| `008` | `PATENT_CERTIFICATE` |

For `007`, exact title `第一次审查意见通知书` is `OA_FIRST`; a title matching
`第<正整数或中文序数>次审查意见通知书` other than first is `OA_SUBSEQUENT`; exact
`复审通知书` is `REEXAMINATION_NOTICE`. Any template/title combination outside this table
is `FORMAT_LETTER_NOTICE_VARIANT_INVALID` (409). Template `002` is not a generic fallback:
another notice may reuse it only through a separately reviewed explicit mapping row.

### Exact predecessor template interface

`FPMS-V8-FORMAT-LETTER-REAL-TEMPLATE-SET-20260712-01` must PASS before High starts this
task. Its converted real templates must expose no undeclared Jinja variable and must accept
these exact keys from this result:

- all eight: `salutation_text`, `client_reference_no`, `case_no`, `invention_title`,
  `application_no`, `filing_date_text`, `applicant_names_text`, `source_notice_name`;
- `003`: `publication_date_text`, `deadline_text`;
- `005` and `008`: `inventor_names_text`;
- `001`, `006`, `007`: `deadline_text`;
- `006`: `amount_lines_text`;
- `007`: `notice_variant_code`, used to render exactly one OA/reexamination row.

The predecessor must replace the eight current placeholder DOCX files, not wrap them. In
particular, template `006` must put `amount_lines_text` in the customer table's existing
“登记金额” cell; template `007` must not retain hard-coded “发文日后 N 个月”; template
`001` must not state the unsupported fixed reason “因没有创造性而驳回”. The builder has
no verified rejection-reason field. Static firm/signature content remains template-owned.

### Case and applicant context

Build applicants in `T_CaseApplicant.seq` ascending order, using stripped `name_cn`, then
`name_en`. Exactly one `is_first=True` row, when present, must also have the smallest
sequence; more than one or disagreement is `FORMAT_LETTER_APPLICANT_CONFLICT` (409).
With no first marker, the lowest sequence is the compatibility fallback. No usable
applicant is `FORMAT_LETTER_APPLICANT_MISSING` (409). Preserve every usable applicant in
order and join with the Chinese delimiter `、`; do not truncate at three names.

The context values are exact:

- `client_reference_no=""`; current `Case.foreign_ref` is not silently relabeled as the
  customer template's “贵方案号” because no approved dedicated carrier exists;
- `case_no=Case.case_no.strip()`;
- `invention_title=title_cn.strip()` falling back to `title_en.strip()`;
- `application_no=(app_no or "").strip()`;
- `filing_date_text=filing_date.isoformat()` or `""`;
- `applicant_names_text` as above;
- `source_notice_name=Document.title.strip()`.

Missing/blank `case_no`, invention title, application number or source notice name is
`FORMAT_LETTER_CASE_CONTEXT_MISSING` (409) with `details.field`. Empty filing date and
client reference remain visible empty strings because customer sources do not prove those
fields are mandatory in every historical case. For `005`/`008`, inventor names use
`T_CaseInventor.seq`, Chinese then English, joined by `、`; no usable inventor is
`FORMAT_LETTER_CASE_CONTEXT_MISSING` with field `inventor_names_text`.

### Contact precedence and exact salutation

Contact selection is deterministic:

1. non-null `selected_contact_id` is an explicit override; missing row is
   `FORMAT_LETTER_CONTACT_NOT_FOUND` (404), and no case client or another client is
   `FORMAT_LETTER_CONTACT_CASE_MISMATCH` (400);
2. otherwise, if the case has exactly one `ClientContact.is_primary=True`, select it;
3. more than one primary is `FORMAT_LETTER_PRIMARY_CONTACT_AMBIGUOUS` (409);
4. no primary, no client, or no contacts selects none. Do not fall back to the oldest
   arbitrary non-primary contact.

Selected contact name must be nonempty stripped text or
`FORMAT_LETTER_CONTACT_INVALID` (409). Its optional title is stripped. Exact outputs are:

- selected: `contact_selection_source="EXPLICIT"|"PRIMARY"`,
  `salutation_source="SELECTED_CONTACT"`, and
  `salutation_text=f"尊敬的{name}{title}：您好"` (omit title when blank);
- none: `selected_contact_id=None`, `contact_selection_source="DEFAULT"`,
  `salutation_source="DEFAULT"`, `salutation_text="尊敬的：您好"`.

Do not append `！`, duplicate `尊敬的`, or emit the current incomplete
`"{name}{title}：您好"` form.

### Deadline and amount rules

Dates render only as ISO `YYYY-MM-DD`; decimals render with comma grouping, exactly two
places and suffix ` 元`. Do not calculate a deadline from `doc_date` or hard-code a month
offset.

- `001`, `003`, `006` and all `007` variants require the existing `Document.extra_data`
  triple `OfficialDueDate`, `OfficialDueDateSource`, `OfficialDueDateStatus`. Status must be
  `CONFIRMED`, source must be `MANUAL_OFFICIAL_NOTICE` or `IMPORTED_OFFICIAL_NOTICE`, and
  the parsed date becomes `deadline_text`. Missing is
  `FORMAT_LETTER_DEADLINE_MISSING` (409); legacy/unconfirmed/invalid is
  `FORMAT_LETTER_DEADLINE_UNCONFIRMED` (409).
- The current customer templates expose one deadline cell for the selected variant, not a
  multi-deadline list. If another persisted reviewed candidate date disagrees, do not join
  dates: raise `FORMAT_LETTER_DEADLINE_CONFLICT` (409).
- `003` additionally requires `Case.pub_date` and maps its ISO value to
  `publication_date_text`; other variants set unused conditional keys to `""`.
- Only `006` emits money. Select the unique `FeeObligation` for the same case and exact
  source document with `fee_domain=GOV`, `obligation_status=RECOGNIZED`,
  `source_status=VERIFIED`, and not superseded. Zero is
  `FORMAT_LETTER_AMOUNT_MISSING` (409), more than one is
  `FORMAT_LETTER_AMOUNT_CONFLICT` (409). Its due date must exist and equal the confirmed
  source deadline or the deadline conflict code applies.
- Use only effective lines having non-null `current_identity_key`, sorted by
  `(fee_year_key, fee_code, id)`. Every line needs non-null, finite, non-negative,
  two-decimal `source_amount`; obligation currency must be exactly `CNY`.
  `difference_review_state=REVIEW_REQUIRED`, malformed values or mixed facts use
  `FORMAT_LETTER_AMOUNT_CONFLICT`; missing source amounts use
  `FORMAT_LETTER_AMOUNT_UNVERIFIED`. `MATCHED` and `SOURCE_PENDING` are accepted only when
  the obligation source itself is `VERIFIED` and a source amount exists; the letter uses
  `source_amount`, never a rate estimate or silently substituted `payable_amount`.
- Format each line as `"{fee_name}：{source_amount:,.2f} 元"` and join lines with `\n` into
  `amount_lines_text`. No lines is the amount-missing error. Non-`006` variants set
  `amount_lines_text=""` and do not infer a fee node.

### Complete context map and validation order

Return exactly these 14 keys in this order when materialized from the mapping:

```text
salutation_text
client_reference_no
case_no
invention_title
application_no
filing_date_text
applicant_names_text
inventor_names_text
source_notice_name
notice_variant_code
publication_date_text
deadline_text
amount_lines_text
template_variant_code
```

`notice_variant_code` and `template_variant_code` echo the frozen result values. There are
no hidden aliases, nested dictionaries, `None`, `date` or `Decimal` values.

After source and template selection, validate case/applicant facts, then contact, then
deadline, then amount. The first failure wins. Any failure performs no write. The result
returns the selected evidence/mapping/template identities so the render/archive tasks can
persist exact provenance without reselecting them.

### Frozen RED/GREEN dataset

`backend/tests/test_v8_format_letter_context.py` must use real foreign-key-enabled SQLite
sessions and prove at least:

1. exact enum/dataclass/signature, read-only transaction behavior and immutable 14-key map;
2. invalid command fields and every source case/direction/current/review/latest failure in
   the frozen order;
3. unique mapping precedence, same-level ambiguity, invalid template linkage and all ten
   notice variants, including the three `007` subvariants;
4. applicant ordering, all-name join, first-marker conflict, Chinese/English fallback,
   required inventor rules and the deliberate blank client reference;
5. explicit same-client contact override, unique-primary selection, multiple-primary
   conflict, no-primary default and exact salutation punctuation;
6. required confirmed deadlines, unconfirmed/missing/conflicting dates, ISO formatting and
   no hard-coded month arithmetic;
7. grant verified multi-line source amounts, deterministic ordering/formatting, exact due
   agreement, missing/unverified/conflicting/ambiguous obligation failures, and no rate or
   payable-amount substitution;
8. all non-grant variants return empty `amount_lines_text` and do not create or mutate an
   obligation, template, document, evidence version, contact or handoff.

The inherited read-only regression command is:

```bash
cd backend && .venv/bin/pytest -q \
  tests/test_v8_document_evidence_contracts.py \
  tests/test_v8_document_evidence_current_version.py \
  tests/test_v8_document_evidence_review.py \
  tests/test_v8_format_letter_real_template_set.py \
  tests/test_format_letter_mapping_seed.py \
  tests/test_pd_p1_letter_handoff_api.py
```

### Reaffirmed non-closure and customer gates

No schema/API/UI/render/archive/email/handoff mutation, no generic template engine, no
automatic generic-template fallback, no source parser/OCR, no new customer-reference
carrier, no sender/signature policy and no legal deadline/amount calculation. The eight
provided customer templates, default/selected salutation, source-notice mapping and
specific-notice amount/deadline precedence are already source-backed; this task has no
customer decision gate. Adding other notices to template `002` still requires an explicit
reviewed mapping row; this task does not guess that catalog.

## Exact Closure Slice

Build source notice, case/applicant, selected contact, default/selected salutation, amount/deadline and template-variant context.

## Explicit Non-Closure

No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-FORMAT-LETTER-REAL-TEMPLATE-SET-20260712-01`
- `FPMS-V8-DE-REVIEW-SERVICE-20260712-01`
- `FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): template set
- Ultra freeze dependency delta: source eligibility requires the evidence-review service;
  template `006` amount/deadline truth requires the source-linked grant-year obligation.

### Shared ownership serialization

- No shared ownership chain beyond the global serialized SQLite verification queue.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-FORMAT-LETTER-CONTEXT-20260712-01.md`
- `backend/app/modules/documents/letter_context.py`
- `backend/tests/test_v8_format_letter_context.py`
- `artifacts/FPMS-V8-FORMAT-LETTER-CONTEXT-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_format_letter_context.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_format_letter_context.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/documents/letter_context.py tests/test_v8_format_letter_context.py && .venv/bin/ruff format app/modules/documents/letter_context.py tests/test_v8_format_letter_context.py && .venv/bin/ruff check app/modules/documents/letter_context.py tests/test_v8_format_letter_context.py`
- `git diff --check -- backend/app/modules/documents/letter_context.py backend/tests/test_v8_format_letter_context.py tasks/postdemo/v8/FPMS-V8-FORMAT-LETTER-CONTEXT-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-FORMAT-LETTER-CONTEXT-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-FORMAT-LETTER-CONTEXT-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-FORMAT-LETTER-CONTEXT-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FORMAT-LETTER-CONTEXT-20260712-01` pass. Only then may this task be reported PASS.
