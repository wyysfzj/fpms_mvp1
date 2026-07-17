# FPMS-V8-W1-F2-FEE-OBLIGATION-LINE-CARRIER-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `8. Wave 1 — schema spine, globally serialized`
Catalog ordinal: `10`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `359`
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

- RED expectation: Exact schema test fails because `FeeObligationLine` / `t_fee_obligation_line`, revision `v8_w1_f2_fee_obligation_line_01`, the 18 frozen columns or the four named constraints are absent.
- GREEN expectation: Exact ORM and migrated-SQLite tests prove the 18 frozen columns, physical types, nullability/defaults, nullable unique current identity, same-case obligation/activity constraints and SQLite-safe audit defaults; task-scoped Ruff, unique-head check and clean temporary SQLite `upgrade head` pass.

## Ultra Replan Record — 2026-07-13

- Blocker found before RED/source edits: the canonical plan froze the line concepts and identity formula, but not the complete physical types, nullability, defaults, FK names or the boundary between explicit normalization and database defaults.
- Resolution: the physical contract below is frozen from the canonical V8 fee design, the already-frozen F1 parent contract and existing repository `Numeric`/`Date` conventions. The exact closure slice remains one line carrier and no F3/F4 link or service behavior is absorbed.
- Story Shape Classification remains unchanged: shared fee-model ownership and global Alembic/SQLite serialization still make this a high-cost schema prerequisite.
- `chosen_runbook` remains `P0-prereq-heavy-story`.
- Implementation resumes only after dependency `FPMS-V8-W1-F1-FEE-OBLIGATION-CARRIER-20260712-01` is PASS and the unique Alembic head is `v8_w1_f1_fee_obligation_01`.

## Frozen Physical Schema Contract

ORM class and table:

- Class: `FeeObligationLine`
- Table: `t_fee_obligation_line`
- Migration revision: `v8_w1_f2_fee_obligation_line_01`
- Migration `down_revision`: `v8_w1_f1_fee_obligation_01`
- Migration policy: forward-only; `downgrade()` raises `NotImplementedError`.

The table has exactly these 18 columns:

| Column | SQLAlchemy / Alembic type | ORM annotation | Nullable | Server default | Meaning |
| --- | --- | --- | --- | --- | --- |
| `id` | `String(36)` | `Mapped[str]` | no | none; application UUID | obligation-line identity |
| `obligation_id` | `String(36)` | `Mapped[str]` | no | none | owning F1 obligation header; same-case composite FK below |
| `case_id` | `String(36)` | `Mapped[str]` | no | none | denormalized owning case for identity and same-case enforcement |
| `source_activity_id` | `String(36)` | `Mapped[str]` | no | none | fee-recognition activity; same-case composite FK below |
| `fee_code` | `String(64)` | `Mapped[str]` | no | none | stable fee item code snapshot |
| `fee_name` | `String(256)` | `Mapped[str]` | no | none | fee item name snapshot |
| `fee_year_key` | `Integer` | `Mapped[int]` | no | none | explicit normalized year identity; `0` means non-annual |
| `official_full_amount` | `Numeric(18, 2)` | `Mapped[Decimal \| None]` | yes | none | applicable full official-policy amount, if verified/available |
| `reduction_ratio` | `Numeric(5, 4)` | `Mapped[Decimal]` | no | none | explicit reduction ratio snapshot; vocabulary/rule validation is later work |
| `payable_amount` | `Numeric(18, 2)` | `Mapped[Decimal]` | no | none | effective amount payable for this line |
| `source_amount` | `Numeric(18, 2)` | `Mapped[Decimal \| None]` | yes | none | amount explicitly carried by reviewed source evidence, if present |
| `source_date` | `Date` | `Mapped[date \| None]` | yes | none | source-backed amount/effect date, if present |
| `difference_review_state` | `String(32)` | `Mapped[str]` | no | none | independent rate/source difference-review fact |
| `current_identity_key` | `String(64)` | `Mapped[str \| None]` | yes | none | SHA-256 hex identity only while this is the effective line |
| `created_at` | `DateTime(timezone=False)` | `Mapped[datetime]` | no | `CURRENT_TIMESTAMP` | audit creation time |
| `updated_at` | `DateTime(timezone=False)` | `Mapped[datetime]` | no | `CURRENT_TIMESTAMP` | audit update time; later writes update it explicitly |
| `created_by` | `String(36)` | `Mapped[str \| None]` | yes | none | audit creator snapshot; no user FK |
| `updated_by` | `String(36)` | `Mapped[str \| None]` | yes | none | audit updater/superseding actor snapshot; no user FK |

Exact named keys and constraints:

| Name | Contract |
| --- | --- |
| primary key | `PRIMARY KEY (id)`; repository-default unnamed PK |
| `fk_t_fee_obligation_line_case_id` | `case_id -> t_case.id`, `ON DELETE CASCADE` |
| `fk_t_fee_obligation_line_obligation_same_case` | composite `(case_id, obligation_id) -> t_fee_obligation(case_id, id)`, `ON DELETE CASCADE` |
| `fk_t_fee_obligation_line_source_activity_same_case` | composite `(case_id, source_activity_id) -> t_case_activity_event(case_id, id)`; default `NO ACTION` |
| `uq_t_fee_obligation_line_current_identity_key` | `UNIQUE (current_identity_key)`; equal non-null effective identities conflict while multiple historical `NULL` values remain valid under SQLite |

Frozen invariants and exclusions:

- `current_identity_key` is exactly the lowercase 64-character SHA-256 hex digest of the UTF-8 string `case_id|source_activity_id|fee_code|fee_year_key`. The later recognition service computes it; the carrier supplies no database-generated key.
- `fee_year_key` has no server or ORM default. A caller must explicitly provide `0` for a non-annual item or the applicable positive annual year. The later contracts/recognition layer owns normalization and rejects missing, negative or otherwise invalid values; F2 does not guess `0`.
- `official_full_amount` is nullable because an independently reviewed source amount can exist before a verified rate-book amount is available. `source_amount` and `source_date` are nullable because not every reviewed source exposes structured amount/date facts. Missing-source/rate and mismatch semantics remain explicit in the required `difference_review_state`; they are not silently converted to zero or equality.
- `reduction_ratio`, `payable_amount` and `difference_review_state` are mandatory snapshots and have no defaults. F2 does not silently infer no reduction, an amount or a completed review.
- A superseded line is retained by clearing its `current_identity_key`, updating its audit fields and creating/reusing the new effective row in the later recognition service. The canonical F2 contract does not authorize `supersedes_line_id`, `supersede_reason`, `superseded_at` or `superseded_by` line columns; header-level supersede metadata remains on F1.
- Do not use `AuditMixin`: its application-side timezone defaults do not satisfy the frozen migration-level `CURRENT_TIMESTAMP` contract.
- There is no line-level currency (currency is on the F1 header), rate-book FK/version, source-document FK, draft-item link or payment-evidence link. F3/F4 own their link carriers; later rate-book and service-price tasks own pricing-source carriers.
- No enum, CHECK, secondary/business index, extra UNIQUE or extra FK is added. Fee/status vocabulary, amount arithmetic, difference transitions, current-key rotation and actor authorization belong to later contract/service tasks.

## Frozen RED / GREEN Contract

- RED must assert `FeeObligationLine` / `t_fee_obligation_line`, revision/down-revision identity, the exact 18 columns, their types/nullability/defaults and the four named constraints above; before implementation it fails because the model/table/migration is absent.
- GREEN must prove ORM and reflected migrated-SQLite metadata match exactly, an application UUID survives `flush()`, a valid same-case header/activity line succeeds, missing/cross-case header or activity references fail, duplicate non-null `current_identity_key` fails, and multiple historical `NULL` keys succeed.
- GREEN must prove `fee_year_key=0` is accepted only when explicitly supplied, omitting it fails rather than receiving a default, nullable official/source facts remain accepted, audit timestamps use `CURRENT_TIMESTAMP`, and no F3/F4 link or unapproved line-supersede field is present.

## Exact Closure Slice

Add only the frozen 18-column `FeeObligationLine` / `t_fee_obligation_line` carrier with explicit year/source/amount/review snapshots, same-case obligation/activity FKs, SQLite-safe audit fields and nullable unique `current_identity_key`; no link table or service behavior.

## Explicit Non-Closure

No backfill, service, endpoint, seed, UI or second table/carrier. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-W1-F1-FEE-OBLIGATION-CARRIER-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): F1

### Shared ownership serialization

- `GLOBAL_ALEMBIC_HEAD` order key `8`; project this order only across owners present in the active manifest.
- `backend/app/modules/fees/models.py` order key `2`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-W1-F2-FEE-OBLIGATION-LINE-CARRIER-20260712-01.md`
- `backend/alembic/versions/v8_w1_f2_fee_obligation_line.py`
- `backend/app/modules/fees/models.py`
- `backend/tests/test_v8_w1_f2_fee_obligation_line.py`
- `artifacts/FPMS-V8-W1-F2-FEE-OBLIGATION-LINE-CARRIER-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Run in the frozen global Alembic order; use SQLite-safe forward-only migration semantics, unique-head check and clean temporary upgrade head.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_w1_f2_fee_obligation_line.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_w1_f2_fee_obligation_line.py`
- `cd backend && .venv/bin/ruff check --fix alembic/versions/v8_w1_f2_fee_obligation_line.py app/modules/fees/models.py tests/test_v8_w1_f2_fee_obligation_line.py && .venv/bin/ruff format alembic/versions/v8_w1_f2_fee_obligation_line.py app/modules/fees/models.py tests/test_v8_w1_f2_fee_obligation_line.py && .venv/bin/ruff check alembic/versions/v8_w1_f2_fee_obligation_line.py app/modules/fees/models.py tests/test_v8_w1_f2_fee_obligation_line.py`
- `cd backend && PYTHONPATH=. .venv/bin/alembic heads && PYTHONPATH=. .venv/bin/alembic upgrade head  # clean temporary SQLite database`
- `git diff --check -- backend/alembic/versions/v8_w1_f2_fee_obligation_line.py backend/app/modules/fees/models.py backend/tests/test_v8_w1_f2_fee_obligation_line.py tasks/postdemo/v8/FPMS-V8-W1-F2-FEE-OBLIGATION-LINE-CARRIER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-W1-F2-FEE-OBLIGATION-LINE-CARRIER-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-W1-F2-FEE-OBLIGATION-LINE-CARRIER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-W1-F2-FEE-OBLIGATION-LINE-CARRIER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-W1-F2-FEE-OBLIGATION-LINE-CARRIER-20260712-01` pass. Only then may this task be reported PASS.
