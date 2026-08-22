# FPMS-V8-OFFICIAL-RATE-BOOK-CARRIER-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `12. Wave 4 — fee-obligation module and fixed rules`
Catalog ordinal: `156`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `612`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: low
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-SCHEMA`

- RED expectation: Exact schema test fails because the named table/column/index is absent.
- GREEN expectation: Exact schema test, task-scoped Ruff, unique-head check and clean temporary SQLite `upgrade head` pass.

## Ultra Contract Freeze — 2026-07-13

This section removes the schema ambiguity that previously blocked High. High must
implement exactly this carrier contract; it must not infer fields from the customer
`标准费率.XLS`, the Tianyue webpage, current seed values or a future service API.

### Frozen legal-source boundary

- This carrier is for official government fees only. `source_authority` is exactly
  `CNIPA`. A Ministry of Finance, NDRC, WIPO or other cited instrument may appear inside
  the retained CNIPA source snapshot only when the CNIPA source itself cites or adopts it.
- The primary sources for this contract are the CNIPA fee-standard page, the CNIPA
  payment service guide and applicable CNIPA announcements, including Announcement 594.
  Their URLs are provenance examples, not rows or rates to insert in this schema task:
  - `https://www.cnipa.gov.cn/art/2024/8/6/art_1518_155983.html`
  - `https://www.cnipa.gov.cn/attach/0/b2d5a31081404b83a36c0df1ebe591e7.pdf`
  - `https://www.cnipa.gov.cn/art/2024/8/6/art_2468_205759.html`
- Customer workbooks, `docs/postdemo/标准费率.XLS`, customer scenario documents and
  `http://www.tianyueip.com/product/612` are business/reference inputs only. They cannot
  be represented as `source_authority=CNIPA`, cannot activate a book and cannot make a
  linked `FeeRate` executable.
- This task inserts no source row, fee code, amount, reduction rule or effective legal
  date. Those remain data owned by the separately serialized source-activation and
  per-rule tasks.

### Frozen migration identity and order

| Item | Exact contract |
| --- | --- |
| migration file | `backend/alembic/versions/v8_w4_official_rate_book.py` |
| `revision` | `v8_w4_official_rate_book_01` |
| `down_revision` | `v8_post_w1_customer_decision_gate_01` |
| branch / dependency labels | `None` / `None` |
| direction | forward-only; `downgrade()` raises `NotImplementedError("This is a forward-only migration")` |

The migration creates `t_fee_rate_book` first, then uses SQLite-safe
`op.batch_alter_table("t_fee_rate")` to add the compatibility link and its named FK/check.
It creates the two named indexes after their columns exist. It performs no data update,
backfill, delete, enable/disable change or source-status coercion. It must not silently
skip an existing table/column/constraint: an unexpected collision is a failed precheck
that requires replanning, not an idempotent success.

If the unique Alembic head is no longer
`v8_post_w1_customer_decision_gate_01` when High starts, High must stop this lane and
return it for migration-order re-freeze. It must not guess a new `down_revision`.

### Frozen ORM and table names

- ORM class: `OfficialRateBook`
- ORM table: `t_fee_rate_book`
- Existing compatibility model: `FeeRate`
- Existing compatibility table: `t_fee_rate`
- Compatibility field: `FeeRate.official_rate_book_id`
- No SQLAlchemy relationship property, item table, association table, enum class or
  second carrier is added by this task.

`OfficialRateBook` uses explicit mapped columns rather than `AuditMixin`, so ORM metadata
matches the migration's `timezone=False` and `CURRENT_TIMESTAMP` audit defaults exactly.
Its application UUID is generated with `str(uuid4())`; correctness does not rely on
SQLite `RETURNING`.

### Frozen `t_fee_rate_book` physical schema

The table has exactly these 22 columns and no others:

| Column | SQLAlchemy / ORM type | Nullable | Server default | Meaning |
| --- | --- | --- | --- | --- |
| `id` | `String(36)` / `Mapped[str]` | no | none | application-generated UUID primary key |
| `book_code` | `String(64)` / `Mapped[str]` | no | none | stable uppercase official-book series code |
| `version_code` | `String(128)` / `Mapped[str]` | no | none | immutable version label inside the series |
| `source_authority` | `String(32)` / `Mapped[str]` | no | none | exactly `CNIPA` |
| `source_reference` | `String(512)` / `Mapped[str]` | no | none | primary canonical CNIPA URL |
| `source_version` | `String(128)` / `Mapped[str]` | no | none | official page/document version or publication label |
| `source_published_on` | `Date` / `Mapped[date]` | no | none | CNIPA publication/update date asserted by the snapshot |
| `source_snapshot` | `Text` / `Mapped[str]` | no | none | canonical JSON provenance snapshot described below |
| `source_snapshot_hash` | `String(64)` / `Mapped[str]` | no | none | lowercase SHA-256 hex of the exact canonical snapshot text |
| `approval_status` | `String(32)` / `Mapped[str]` | no | `'PENDING'` | `PENDING`, `APPROVED` or `REJECTED` |
| `approved_by` | `String(36)` / `Mapped[str \| None]` | yes | none | internal approver user |
| `approved_at` | `DateTime(timezone=False)` / `Mapped[datetime \| None]` | yes | none | approval/rejection time |
| `effective_from` | `Date` / `Mapped[date]` | no | none | inclusive legal applicability start |
| `effective_to` | `Date` / `Mapped[date \| None]` | yes | none | inclusive end; `NULL` means open-ended |
| `activation_status` | `String(32)` / `Mapped[str]` | no | `'INACTIVE'` | `INACTIVE`, `ACTIVE` or `RETIRED` |
| `activated_by` | `String(36)` / `Mapped[str \| None]` | yes | none | user who first activated the version |
| `activated_at` | `DateTime(timezone=False)` / `Mapped[datetime \| None]` | yes | none | first activation time, retained after retirement |
| `current_identity_key` | `String(128)` / `Mapped[str \| None]` | yes | none | current-only identity described below |
| `created_at` | `DateTime(timezone=False)` / `Mapped[datetime]` | no | `CURRENT_TIMESTAMP` | audit creation time |
| `updated_at` | `DateTime(timezone=False)` / `Mapped[datetime]` | no | `CURRENT_TIMESTAMP` | audit update time |
| `created_by` | `String(36)` / `Mapped[str \| None]` | yes | none | generic audit actor |
| `updated_by` | `String(36)` / `Mapped[str \| None]` | yes | none | generic audit actor |

### Frozen provenance snapshot

`source_snapshot` is UTF-8 canonical JSON serialized with
`ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False`. Its exact
top-level contract for the later activation service is:

```json
{
  "schema_version": "CNIPA_RATE_SOURCE_V1",
  "sources": [
    {
      "content_sha256": "<64 lowercase hex>",
      "document_no": null,
      "published_on": "YYYY-MM-DD",
      "retrieved_at": "<UTC ISO-8601 ending Z>",
      "title": "<CNIPA title>",
      "url": "https://www.cnipa.gov.cn/..."
    }
  ]
}
```

`sources` is non-empty. The first source must equal the explicit
`source_reference/source_published_on`; additional entries are CNIPA sources or instruments
explicitly cited/adopted by them. Customer documents and commercial webpages are
prohibited. The carrier task stores the Text/hash fields and database length constraint;
semantic JSON, URL, content-hash and cross-field validation belongs to
`FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01` and is not implemented here.
Every source entry has exactly the six keys shown above: `content_sha256`, `document_no`,
`published_on`, `retrieved_at`, `title` and `url`; `document_no` is `str | null` and every
other value is a string. The first entry's `url` and `published_on` exactly equal the
explicit `source_reference` and ISO value of `source_published_on`.

### Frozen identities and transitions represented by the carrier

- A series version identity is `(source_authority, book_code, version_code)`.
- `current_identity_key` is exactly `f"{source_authority}|{book_code}"` only while
  `activation_status == "ACTIVE"`.
- `INACTIVE` has no activation actor/time and a `NULL` current key.
- `ACTIVE` requires `approval_status == "APPROVED"`, non-null approval actor/time,
  non-null activation actor/time and the exact non-null current key.
- `RETIRED` retains its original activation actor/time, remains approved and has a `NULL`
  current key.
- `REJECTED` can only remain `INACTIVE`.
- `effective_to` is inclusive and must be absent or on/after `effective_from`.
- The carrier's nullable unique current key allows many historical/inactive `NULL` rows
  but only one current version per `(source_authority, book_code)`.
- SQLite cannot enforce date-range exclusion. The later source-activation service must
  reject overlapping `ACTIVE`/`RETIRED` intervals within the same series and must not
  infer or shorten an official interval to resolve an overlap.
- Source identity, source snapshot and hash are immutable after first activation.
  Retirement may update only `activation_status`, `current_identity_key`, `updated_at`
  and `updated_by`; it does not rewrite source facts or fee amounts.

No four-eyes rule is invented here: `approved_by` and `activated_by` may be the same user.
If separation of duties is later required, it needs its own approved task.

### Frozen constraints, foreign keys and indexes

`t_fee_rate_book` has exactly these named constraints in addition to its primary key:

| Name | Exact contract |
| --- | --- |
| `uq_t_fee_rate_book_series_version` | `UNIQUE(source_authority, book_code, version_code)` |
| `uq_t_fee_rate_book_current_identity_key` | `UNIQUE(current_identity_key)`; multiple `NULL` values remain valid on SQLite |
| `fk_t_fee_rate_book_approved_by` | `approved_by -> t_user.id`, `ON DELETE RESTRICT` |
| `fk_t_fee_rate_book_activated_by` | `activated_by -> t_user.id`, `ON DELETE RESTRICT` |
| `ck_t_fee_rate_book_source_authority` | `source_authority = 'CNIPA'` |
| `ck_t_fee_rate_book_source_hash` | `length(source_snapshot_hash) = 64` |
| `ck_t_fee_rate_book_effective_interval` | `effective_to IS NULL OR effective_to >= effective_from` |
| `ck_t_fee_rate_book_approval_status` | status is one of `PENDING/APPROVED/REJECTED` |
| `ck_t_fee_rate_book_approval_tuple` | `PENDING` has null approval actor/time; `APPROVED/REJECTED` have both |
| `ck_t_fee_rate_book_activation_status` | status is one of `INACTIVE/ACTIVE/RETIRED` |
| `ck_t_fee_rate_book_activation_tuple` | enforces the exact inactive/active/retired tuple and exact active current key above |

The check expressions are exact:

```sql
source_authority = 'CNIPA'
length(source_snapshot_hash) = 64
effective_to IS NULL OR effective_to >= effective_from
approval_status IN ('PENDING', 'APPROVED', 'REJECTED')
(approval_status = 'PENDING' AND approved_by IS NULL AND approved_at IS NULL)
OR (approval_status IN ('APPROVED', 'REJECTED') AND approved_by IS NOT NULL AND approved_at IS NOT NULL)
activation_status IN ('INACTIVE', 'ACTIVE', 'RETIRED')
(activation_status = 'INACTIVE' AND activated_by IS NULL AND activated_at IS NULL AND current_identity_key IS NULL)
OR (activation_status = 'ACTIVE' AND approval_status = 'APPROVED' AND approved_by IS NOT NULL AND approved_at IS NOT NULL AND activated_by IS NOT NULL AND activated_at IS NOT NULL AND current_identity_key = source_authority || '|' || book_code)
OR (activation_status = 'RETIRED' AND approval_status = 'APPROVED' AND approved_by IS NOT NULL AND approved_at IS NOT NULL AND activated_by IS NOT NULL AND activated_at IS NOT NULL AND current_identity_key IS NULL)
```

The migration and ORM may wrap these expressions for Python formatting only; they must
not weaken or add branches.

The table has exactly one explicit non-unique index:

`ix_t_fee_rate_book_series_interval(source_authority, book_code, activation_status, effective_from, effective_to)`.

The existing `t_fee_rate` receives only:

| Kind | Exact contract |
| --- | --- |
| column | nullable `official_rate_book_id String(36)`, no default |
| FK | `fk_t_fee_rate_official_rate_book_id`: `official_rate_book_id -> t_fee_rate_book.id`, `ON DELETE RESTRICT` |
| check | `ck_t_fee_rate_official_book_gov_only`: `official_rate_book_id IS NULL OR fee_type = 'GOV'` |
| index | `ix_t_fee_rate_official_rate_book_id(official_rate_book_id)` |

The link is deliberately nullable for every legacy row. It is not added to `FeeItem`, a
service-fee row cannot use it, and deletion cannot erase the provenance of a linked rate.

### Frozen migration precheck and compatibility behavior

High must prove both upgrade shapes on isolated temporary SQLite databases with foreign
keys enabled:

1. clean `upgrade head` from base creates the exact table, link, constraints and indexes;
2. upgrade from `v8_post_w1_customer_decision_gate_01` after inserting representative
   legacy GOV and SERVICE `t_fee_rate` rows preserves their IDs and all existing values,
   leaves `official_rate_book_id=NULL`, creates no rate-book rows and changes no `enabled`
   or `source_status` value.

The migration does not repair current customer-derived `source_*` metadata and does not
link or activate existing seed rows. That fail-closed replacement belongs to the source
activation task. No downgrade cleanup, destructive rebuild of the developer database or
production-data mutation is authorized.

### Frozen RED / GREEN schema test contract

`backend/tests/test_v8_official_rate_book_schema.py` must prove all of the following and
must not assert or insert a real legal fee amount:

1. RED fails because `OfficialRateBook`, `t_fee_rate_book` or
   `FeeRate.official_rate_book_id` is absent before implementation.
2. ORM metadata and reflected migrated-SQLite metadata expose the exact columns,
   nullability, lengths, defaults, constraint names, FK targets/delete actions and indexes.
3. Migration identity is exactly the frozen revision/down-revision and Alembic has one
   head: `v8_w4_official_rate_book_01`.
4. An application UUID appears after `flush()` without `RETURNING`; one valid inactive
   CNIPA candidate succeeds.
5. invalid authority, 63-character snapshot hash, reversed interval, invalid status,
   inconsistent approval tuple and inconsistent activation/current tuple each fail.
6. duplicate series/version and duplicate non-null current identity fail; multiple
   historical/inactive `NULL` current keys succeed.
7. valid GOV `FeeRate` linkage succeeds; a missing book FK, a SERVICE link and deletion of
   a linked book fail with SQLite foreign keys enabled.
8. the clean-upgrade and legacy-preservation upgrade described above both pass.

The schema test may use a synthetic CNIPA URL, snapshot, hash and version. It must not
claim the synthetic values are an approved official rate book.

## Exact Closure Slice

Add only the frozen 22-column `OfficialRateBook` / `t_fee_rate_book` carrier and the
nullable GOV-only `FeeRate.official_rate_book_id` compatibility link with its exact named
constraints and indexes.

## Explicit Non-Closure

No rate/source row, amount, backfill, activation, non-overlap service, endpoint, seed, UI
or second table/carrier. Do not absorb another V8 catalog row, a second closure slice, an
unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-DECISION-GATE-CARRIER-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): decision-gate carrier complete; global Alembic lock

### Shared ownership serialization

- `GLOBAL_ALEMBIC_HEAD` order key `13`; project this order only across owners present in the active manifest.
- `backend/app/modules/fees/models.py` order key `6`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- `FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01`

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-OFFICIAL-RATE-BOOK-CARRIER-20260712-01.md`
- `backend/alembic/versions/v8_w4_official_rate_book.py`
- `backend/app/modules/fees/models.py`
- `backend/tests/test_v8_official_rate_book_schema.py`
- `artifacts/FPMS-V8-OFFICIAL-RATE-BOOK-CARRIER-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_official_rate_book_schema.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_official_rate_book_schema.py`
- `cd backend && .venv/bin/ruff check --fix alembic/versions/v8_w4_official_rate_book.py app/modules/fees/models.py tests/test_v8_official_rate_book_schema.py && .venv/bin/ruff format alembic/versions/v8_w4_official_rate_book.py app/modules/fees/models.py tests/test_v8_official_rate_book_schema.py && .venv/bin/ruff check alembic/versions/v8_w4_official_rate_book.py app/modules/fees/models.py tests/test_v8_official_rate_book_schema.py`
- `cd backend && PYTHONPATH=. .venv/bin/alembic heads  # exact output: v8_w4_official_rate_book_01 (head)`
- `cd backend && tmp_dir="$(mktemp -d)" && DATABASE_URL="sqlite:///${tmp_dir}/rate-book.db" PYTHONPATH=. .venv/bin/alembic upgrade head && DATABASE_URL="sqlite:///${tmp_dir}/rate-book.db" PYTHONPATH=. .venv/bin/alembic current  # isolated clean SQLite; exact current: v8_w4_official_rate_book_01 (head)`
- `git diff --check -- backend/alembic/versions/v8_w4_official_rate_book.py backend/app/modules/fees/models.py backend/tests/test_v8_official_rate_book_schema.py tasks/postdemo/v8/FPMS-V8-OFFICIAL-RATE-BOOK-CARRIER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-OFFICIAL-RATE-BOOK-CARRIER-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-OFFICIAL-RATE-BOOK-CARRIER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-OFFICIAL-RATE-BOOK-CARRIER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OFFICIAL-RATE-BOOK-CARRIER-20260712-01` pass. Only then may this task be reported PASS.
