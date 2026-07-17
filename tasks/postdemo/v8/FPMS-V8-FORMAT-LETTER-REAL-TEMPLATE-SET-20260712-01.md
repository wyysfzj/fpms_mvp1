# FPMS-V8-FORMAT-LETTER-REAL-TEMPLATE-SET-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `11. Wave 2C/3 — document evidence and existing workflow adapters`
Catalog ordinal: `88`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `493`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: low
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Task Contract Profile

Task Contract Profile: `TC-SERVICE`

- RED expectation: Exact service/dataset test fails on missing behavior, data or prohibited side effect.
- GREEN expectation: Exact service/dataset test and named inherited regressions pass with caller-owned transaction semantics where writes are transactional.

## Ultra Contract Freeze — 2026-07-13

This section is the complete High implementation contract. It reconciles the customer
workflow Word, all eight customer `.doc` sources, their rendered structure, the existing
eight generated placeholders, current seed/mapping behavior, V8 §8.4 and the frozen
`FPMS-V8-FORMAT-LETTER-CONTEXT-20260712-01` predecessor interface. High must not design a
second template family, add customer wording or change the mapping semantics below.

### Dataset identity and version boundary

- Dataset ID: `FPMS-FORMAT-LETTER-CUSTOMER-20260610-V1`.
- Dataset source: `docs/postdemo/文件样例及模版/常用邮件模板/**` plus the eight-row
  mapping in `docs/postdemo/信函生成操作.docx` P0007 TABLE 001.
- This task installs exactly one current source-backed dataset. The semantic template
  version IDs below are persisted in each mapping's canonical JSON `remark`; they are not
  database primary keys and do not authorize a schema change.
- `Template.name` remains the stable code `FORMAT_LETTER_001` through `_008`, because the
  frozen context task validates that exact name. Existing Template and mapping primary
  keys are preserved during the placeholder-to-real-template update.
- A later customer template revision needs a new atomic dataset/version task. This task
  does not claim an immutable multi-version template repository or rewrite historical
  handoffs.

### Exact eight-entry catalog

The seed catalog is frozen to the following rows and order. Source SHA-256 is over the
repository customer `.doc` binary. `template_version_id` is exact and is included in the
canonical provenance remark.

| # | Stable code / `Template.name` | Template version ID | Customer source and SHA-256 | Customer format-letter name | Official document name pattern | Committed output |
| --- | --- | --- | --- | --- | --- | --- |
| 001 | `FORMAT_LETTER_001` | `FPMS-FORMAT-LETTER-CUSTOMER-20260610-V1-001` | `docs/postdemo/文件样例及模版/常用邮件模板/驳回通知.doc`; `4f8f24d83bb3ca84f4663a0c46a1a84fa060ceb5881d2b9d3001fd074e81b4f2` | `官文转发-国内客户-驳回通知` | `驳回决定` | `templates/format_letters/format_letter_001.docx` |
| 002 | `FORMAT_LETTER_002` | `FPMS-FORMAT-LETTER-CUSTOMER-20260610-V1-002` | `docs/postdemo/文件样例及模版/常用邮件模板/初审合格.doc`; `979713345eb2d5d8f4ee02421ebf5de6936b9f4418648dcffbe7a71f4cd62724` | `官文转发-国内客户-初审合格` | `初步审查合格` | `templates/format_letters/format_letter_002.docx` |
| 003 | `FORMAT_LETTER_003` | `FPMS-FORMAT-LETTER-CUSTOMER-20260610-V1-003` | `docs/postdemo/文件样例及模版/常用邮件模板/公布通知.doc`; `01502d4d3329adff358b3dfa0f995c5bcebb831b02155524140fbdf4995a81da` | `官文转发-国内客户-公布通知` | `公布通知书` | `templates/format_letters/format_letter_003.docx` |
| 004 | `FORMAT_LETTER_004` | `FPMS-FORMAT-LETTER-CUSTOMER-20260610-V1-004` | `docs/postdemo/文件样例及模版/常用邮件模板/实审通知.doc`; `dec38f3f2999b35c39b6d9cfa9f204bd0c930132da750170b1cdf90bd4666c00` | `官文转发-国内客户-实审通知` | `进入实审通知` | `templates/format_letters/format_letter_004.docx` |
| 005 | `FORMAT_LETTER_005` | `FPMS-FORMAT-LETTER-CUSTOMER-20260610-V1-005` | `docs/postdemo/文件样例及模版/常用邮件模板/受通.doc`; `acc06a13d4b09349d2eb81fadd31509ca7e260047df21ab38d65621d4607fff0` | `官文转发-国内客户-受通` | `受理通知-电子` | `templates/format_letters/format_letter_005.docx` |
| 006 | `FORMAT_LETTER_006` | `FPMS-FORMAT-LETTER-CUSTOMER-20260610-V1-006` | `docs/postdemo/文件样例及模版/常用邮件模板/授权通知.doc`; `83c14cf4b6514bee2c3f084cb13d2fb66f067dbeb8260de659f9ffb18e542974` | `官文转发-国内客户-授权通知` | `授权通知书-电子` | `templates/format_letters/format_letter_006.docx` |
| 007 | `FORMAT_LETTER_007` | `FPMS-FORMAT-LETTER-CUSTOMER-20260610-V1-007` | `docs/postdemo/文件样例及模版/常用邮件模板/审查意见或复审通知.doc`; `59322585ca96505fd1f38536ffa02e7afd3825df74c750e5256708b3869484cc` | `官文转发-国内客户-一通` | `第一次审查意见通知书` | `templates/format_letters/format_letter_007.docx` |
| 008 | `FORMAT_LETTER_008` | `FPMS-FORMAT-LETTER-CUSTOMER-20260610-V1-008` | `docs/postdemo/文件样例及模版/常用邮件模板/专利证书.doc`; `5e9cf0638f02f98784c177e586f1127dc9fc0cc4e902596f61b368bb777c8be6` | `官文转发-专利证书` | `专利证书` | `templates/format_letters/format_letter_008.docx` |

The repository output paths are exactly the eight allowlisted
`backend/storage/templates/format_letters/format_letter_00N.docx` files. The database
stores the `templates/...` path shown in the table. Row `007` does not silently seed
subsequent-OA or reexamination aliases: those variants may use the same template only when
a separately reviewed explicit mapping row selects code `007`; the context task rejects
unsupported titles after mapping selection.

### Exact template-variable contract

The common undeclared Jinja variable set in every template is exactly:

```text
salutation_text
client_reference_no
case_no
invention_title
application_no
filing_date_text
applicant_names_text
source_notice_name
```

The exact additions are:

| Template | Additional variables; no others |
| --- | --- |
| `001` | `deadline_text` |
| `002` | None |
| `003` | `publication_date_text`, `deadline_text` |
| `004` | None |
| `005` | `inventor_names_text` |
| `006` | `deadline_text`, `amount_lines_text` |
| `007` | `deadline_text`, `notice_variant_code` |
| `008` | `inventor_names_text` |

`template_variant_code` and the other unused keys returned by the context builder are
allowed in the render context but must not be inserted as hidden template variables. Each
template exposes no Word `MERGEFIELD`, undeclared alias, nested lookup, date arithmetic,
fee arithmetic or hard-coded case value.

### Source-to-placeholder replacement and placement rules

High converts each exact customer `.doc` source to the corresponding committed `.docx`
and replaces fields in place. It must not wrap the customer document inside the current
generated placeholder or rebuild the letter from generic paragraphs.

For all eight templates:

1. Replace the complete existing greeting line with `{{ salutation_text }}`. The context
   owns `尊敬的…：您好`; the template must not prepend/append duplicate greeting text or
   punctuation.
2. Replace the table value positions `申请人案号`, `案件文号`, `中文发明名称`, `申请号` and
   `申请日` with `client_reference_no`, `case_no`, `invention_title`, `application_no` and
   `filing_date_text` respectively.
3. Replace the first applicant merge position with `{{ applicant_names_text }}` and remove
   the remaining numbered applicant merge fields and their template-owned separators.
   The single value remains in the original applicant-name cell and may contain all
   applicants; it is not truncated to three.
4. Replace the existing file-name value in the `文件名称` cell with
   `{{ source_notice_name }}`. Where the source has a highlighted notice name in its lead
   sentence, retain that run's highlight and replace only the name with the same variable.
5. Preserve the customer source's A4 landscape section, margins, one primary table,
   column order/widths, header labels, visible borders, paragraph order, attachment
   sentence, static customer-owned signature/firm block and their formatting. Do not copy
   those potentially identifying static values into evidence logs.

Template-specific placement is exact:

- `001`: put `deadline_text` in the existing `复审期限` value cell. Remove only the
  unsupported fixed clause asserting a particular rejection reason; the retained customer
  sentence still reports receipt of the official rejection and introduces the table. Remove
  the hard-coded relative-month suffix.
- `002`: preserve the customer highlighted notice-name positions; both use
  `source_notice_name`. This seed row remains the confirmed preliminary-pass mapping.
  Customer `注.txt` permits later reuse only through an explicit reviewed mapping, not an
  automatic seed fallback.
- `003`: put `publication_date_text` and `deadline_text` in the existing `公开日` and
  `实审期限` value cells. Do not calculate either value in the template.
- `004`: no additional value is introduced; preserve the source's substantive-examination
  wording and table.
- `005`: replace the existing inventor merge position with `inventor_names_text`.
- `006`: put `deadline_text` in the existing `登记期限` value cell and
  `amount_lines_text` in the already present, blank `登记金额` value cell. Newline-separated
  verified fee lines stay within that cell. Do not add or infer an amount sentence.
- `007`: retain one customer table header plus one customer data-row layout. Guard that
  single data row with docxtpl table-row condition tags accepting only `OA_FIRST`,
  `OA_SUBSEQUENT` or `REEXAMINATION_NOTICE`, so a valid render has exactly one data row.
  Use `source_notice_name` and `deadline_text` in its file/deadline cells; remove all three
  hard-coded `发文日后 N 个月` suffixes. In the lead sentence, replace only the notice name
  with `source_notice_name`, which covers the customer source's OA and reexamination
  variants without inventing a new sentence.
- `008`: replace the existing inventor merge position with `inventor_names_text` and
  preserve the certificate-specific wording. It remains separate from `006`.

These edits introduce variables only at an existing semantic value position (or the
existing blank authorization-amount cell). No customer wording is missing for this eight-
template family, so this task has no customer-wording decision gate. If implementation
finds that a required value cannot be placed without inventing substantive prose, it must
stop with `CUSTOMER_TEMPLATE_WORDING_REQUIRED:<code>` and return to Ultra; it must not
write substitute wording.

### Exact seed and idempotency behavior

`FORMAT_LETTER_MAPPING_CATALOG` becomes one immutable eight-entry dataset carrying every
field in the table above. The old `_ensure_format_letter_docx_template` placeholder
generator is removed or changed to a read-only validator; seed execution never creates or
rewrites a binary template.

Before the first database mutation, `seed_format_letter_mappings(db)` validates all eight
committed outputs as readable OOXML/docxtpl packages and validates their exact undeclared
variable sets. Missing/corrupt output, any Word merge field, wrong variables or a generated
placeholder raises `RuntimeError` with one of these exact prefixes and leaves the session
with no format-letter seed mutation:

```text
FORMAT_LETTER_TEMPLATE_MISSING:<code>
FORMAT_LETTER_TEMPLATE_INVALID:<code>
FORMAT_LETTER_TEMPLATE_VARIABLES_MISMATCH:<code>
FORMAT_LETTER_TEMPLATE_PLACEHOLDER_REMAINS:<code>
```

The customer `.doc` sources are build/test provenance and are not required in a production
seed runtime. Their exact SHA-256 values are frozen in the catalog and verified by the
task test without logging document text.

For each row, seed behavior is deterministic:

1. Resolve at most one mapping by exact `format_letter_template_code`; duplicates fail
   closed with `FORMAT_LETTER_MAPPING_AMBIGUOUS:<code>`.
2. Reuse the mapping's linked Template when it exists and is the legacy/current row for
   this code; otherwise reuse the unique `group="FORMAT_LETTER"`, `name=<code>` row. An
   ambiguous or unrelated linked row fails with
   `FORMAT_LETTER_TEMPLATE_ROW_AMBIGUOUS:<code>` rather than stealing it.
3. Create a Template only when neither row exists. Update the chosen row in place to exact
   `name=<code>`, `group="FORMAT_LETTER"`, `language="zh-CN"`, frozen file path and
   `enabled=True`; preserve its primary key.
4. Create or update exactly one mapping with the frozen official-name pattern, chosen
   template ID, stable code, output rule
   `{case_no}-给{applicant_name}的邮件.docx`,
   `salutation_rule_code="PRIMARY_CONTACT_TITLE"`,
   `contact_rule_code="CLIENT_PRIMARY_CONTACT"`, `enabled=True`, and both official
   template ID/code fields `None`.
5. Set `remark` to canonical UTF-8 JSON produced with
   `ensure_ascii=False, sort_keys=True, separators=(",", ":")`, containing exactly:

```text
customer_format_letter_name
dataset_id
source_path
source_sha256
template_version_id
```

   `source_sha256` is the lowercase wire value `sha256:<64 table hex characters>`; the
   other values are exactly the catalog strings above. No timestamp, local absolute path,
   output-binary digest or database ID is added to this remark.

6. Count each created/updated Template or mapping row once; field count is irrelevant.
   `flush` only as needed for FK identity. The helper does not commit, roll back, delete,
   create an evidence version or modify a handoff.

A second run against the completed dataset returns `0`, preserves all Template/mapping
IDs and creates no duplicate. Existing unrelated/manual mappings and Templates are not
deleted or normalized.

### Frozen RED/GREEN and binary/render verification

`backend/tests/test_v8_format_letter_real_template_set.py` uses a foreign-key-enabled
SQLite session where database writes occur and proves at least:

1. the current RED fails because the committed files are generated placeholders and the
   frozen real-template dataset/provenance contract is absent;
2. all eight customer source paths exist and match the exact SHA-256 catalog without
   emitting their text or identifying static content to logs;
3. every committed output is a valid OOXML Word package, has the exact variable set above,
   contains no `MERGEFIELD`, no current generic-placeholder sentence, no fixed unsupported
   rejection reason and no hard-coded relative-month deadline;
4. each template has one A4 landscape section (`w=16838`, `h=11906`), one primary table,
   preserved source header order and the exact placeholder in its specified table cell.
   Header order is frozen as:
   - `001`: `序号/贵方案号/我方案号/发明创造名称/申请号/申请日/申请人名称/文件名称/复审期限`;
   - `002` and `004`: `序号/贵方案号/我方案号/发明创造名称/申请号/申请日/申请人名称/文件名称`;
   - `003`: the common eight plus `公开日/实审期限`;
   - `005` and `008`: `序号/贵方案号/我方案号/发明创造名称/申请号/申请日/发明人/申请人名称/文件名称`;
   - `006`: the common eight plus `登记期限/登记金额`;
   - `007`: the common eight plus `答复期限`;
5. `DocxTemplate` can render every template with a complete representative 14-key context;
   the rendered DOCX reopens through `python-docx`, contains all task-relevant sample
   values, has no unresolved Jinja/merge marker and preserves the landscape table shape;
6. each representative rendered DOCX converts headlessly to a one-page A4 landscape PDF;
   `007` is rendered separately for all three allowed variants and each output has exactly
   one data row after its header;
7. a clean seed produces exactly eight enabled Templates and eight enabled mappings with
   exact code/name/path/mapping/output-rule/canonical-provenance values;
8. a second seed returns zero, preserves IDs/counts and does not commit; a legacy
   placeholder-linked row is updated in place without changing its Template or mapping ID;
9. missing/corrupt/wrong-variable/placeholder output and ambiguous database carriers fail
   with the exact prefix before dataset mutation and never generate a replacement DOCX.

The inherited read-only regressions are:

```bash
cd backend && .venv/bin/pytest -q \
  tests/test_format_letter_mapping_seed.py \
  tests/test_pd_p1_letter_handoff_carriers.py \
  tests/test_pd_p1_letter_handoff_api.py
```

### Reaffirmed non-closure and decision gates

No schema, API, UI, context builder, renderer service, archive/evidence registration,
email send, generic fallback, source-document resolver, customer-reference carrier,
deadline calculation, fee calculation or other template family. This task neither
classifies these internal customer letters as current official forms nor depends on
`DG-LEGACY-FORM-CLASS`. There is no residual customer gate for the exact eight provided
letters. Any ninth mapping, new customer wording or later binary version is a follow-up
atomic task, not an expansion of this one.

## Exact Closure Slice

Replace generated placeholders with the frozen eight customer templates and exact mappings as one versioned seed dataset.

## Explicit Non-Closure

No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-DE-REGISTER-VERSION-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): evidence version; not blocked by legacy-form gate

### Shared ownership serialization

- `backend/scripts/seed_dev.py` order key `1`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-FORMAT-LETTER-REAL-TEMPLATE-SET-20260712-01.md`
- `backend/scripts/seed_dev.py`
- `backend/tests/test_v8_format_letter_real_template_set.py`
- `backend/storage/templates/format_letters/format_letter_001.docx`
- `backend/storage/templates/format_letters/format_letter_002.docx`
- `backend/storage/templates/format_letters/format_letter_003.docx`
- `backend/storage/templates/format_letters/format_letter_004.docx`
- `backend/storage/templates/format_letters/format_letter_005.docx`
- `backend/storage/templates/format_letters/format_letter_006.docx`
- `backend/storage/templates/format_letters/format_letter_007.docx`
- `backend/storage/templates/format_letters/format_letter_008.docx`
- `artifacts/FPMS-V8-FORMAT-LETTER-REAL-TEMPLATE-SET-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_format_letter_real_template_set.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_format_letter_real_template_set.py`
- `cd backend && .venv/bin/pytest -q tests/test_format_letter_mapping_seed.py tests/test_pd_p1_letter_handoff_carriers.py tests/test_pd_p1_letter_handoff_api.py`
- `cd backend && .venv/bin/ruff check --fix scripts/seed_dev.py tests/test_v8_format_letter_real_template_set.py && .venv/bin/ruff format scripts/seed_dev.py tests/test_v8_format_letter_real_template_set.py && .venv/bin/ruff check scripts/seed_dev.py tests/test_v8_format_letter_real_template_set.py`
- `git diff --check -- backend/scripts/seed_dev.py backend/tests/test_v8_format_letter_real_template_set.py backend/storage/templates/format_letters/format_letter_001.docx backend/storage/templates/format_letters/format_letter_002.docx backend/storage/templates/format_letters/format_letter_003.docx backend/storage/templates/format_letters/format_letter_004.docx backend/storage/templates/format_letters/format_letter_005.docx backend/storage/templates/format_letters/format_letter_006.docx backend/storage/templates/format_letters/format_letter_007.docx backend/storage/templates/format_letters/format_letter_008.docx tasks/postdemo/v8/FPMS-V8-FORMAT-LETTER-REAL-TEMPLATE-SET-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-FORMAT-LETTER-REAL-TEMPLATE-SET-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-FORMAT-LETTER-REAL-TEMPLATE-SET-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-FORMAT-LETTER-REAL-TEMPLATE-SET-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FORMAT-LETTER-REAL-TEMPLATE-SET-20260712-01` pass. Only then may this task be reported PASS.
