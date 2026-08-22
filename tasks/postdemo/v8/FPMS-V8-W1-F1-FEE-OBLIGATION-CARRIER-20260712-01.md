# FPMS-V8-W1-F1-FEE-OBLIGATION-CARRIER-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `8. Wave 1 — schema spine, globally serialized`
Catalog ordinal: `9`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `358`
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

- RED expectation: Exact schema tests require `FeeObligation` / `t_fee_obligation`, revision `v8_w1_f1_fee_obligation_01` over `v8_w1_d3_workpkg_evidence_01`, the frozen 20 columns, five named FK/UQ constraints, and nullable `source_document_id`, `due_date`, `supersedes_obligation_id` and `supersede_reason`; before implementation they fail because the model/table/migration is absent.
- GREEN expectation: ORM and migrated SQLite metadata match the exact 20-column contract, revision lineage and five named constraints; nullable source/due/supersede fields are accepted; no amount/line-identity columns or business-state defaults appear; task-scoped Ruff, unique-head check and clean temporary SQLite `upgrade head` pass.

## Exact Closure Slice

Add only the frozen 20-column `FeeObligation` / `t_fee_obligation` itemized-obligation header, including source and supersede fields; no line identity.

## Explicit Non-Closure

No backfill, service, endpoint, seed, UI or second table/carrier. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Ultra Replan Record — 2026-07-13

- Blocker found before RED/source edits: the canonical design and implementation plan named the header concepts but did not freeze physical column names, types, nullability, defaults or constraints.
- Resolution: the physical contract below is frozen from the canonical V8 design/plan and existing SQLite-safe fee/lifecycle carrier conventions. The exact closure slice is unchanged and no second carrier is absorbed.
- Story Shape Classification remains unchanged: shared ownership and Alembic serialization are still high-cost schema prerequisites.
- `chosen_runbook` remains `P0-prereq-heavy-story`.
- Implementation resumes only after dependency `FPMS-V8-W1-D3-WORK-PACKAGE-EVIDENCE-LINK-CARRIER-20260712-01` is PASS and the unique Alembic head is `v8_w1_d3_workpkg_evidence_01`.

## Frozen Physical Schema Contract

ORM class and table:

- Class: `FeeObligation`
- Table: `t_fee_obligation`
- Migration revision: `v8_w1_f1_fee_obligation_01`
- Migration `down_revision`: `v8_w1_d3_workpkg_evidence_01`
- Migration policy: forward-only; `downgrade()` raises `NotImplementedError`.

The table has exactly these 20 columns:

| Column | SQLAlchemy / Alembic type | ORM annotation | Nullable | Server default | Meaning |
| --- | --- | --- | --- | --- | --- |
| `id` | `String(36)` | `Mapped[str]` | no | none; application UUID | obligation-header identity |
| `case_id` | `String(36)` | `Mapped[str]` | no | none | owning case |
| `source_activity_id` | `String(36)` | `Mapped[str]` | no | none | same-case fee activity that recognizes this header |
| `source_document_id` | `String(36)` | `Mapped[str \| None]` | yes | none | optional official/customer source document |
| `fee_domain` | `String(16)` | `Mapped[str]` | no | none | explicit `GOV` or `SERVICE` domain; vocabulary validation is later service-contract work |
| `obligation_type` | `String(64)` | `Mapped[str]` | no | none | header-level obligation kind; line fee-code/year identity is not stored here |
| `obligation_status` | `String(32)` | `Mapped[str]` | no | none | real-obligation state |
| `due_date` | `Date` | `Mapped[date \| None]` | yes | none | explicit source-backed due date; missing date remains review-blocked and is never guessed |
| `currency` | `String(8)` | `Mapped[str]` | no | none | explicit obligation currency; no implicit `CNY` |
| `source_status` | `String(32)` | `Mapped[str]` | no | none | source-verification state |
| `client_instruction_status` | `String(32)` | `Mapped[str]` | no | none | customer instruction fact |
| `draft_status` | `String(32)` | `Mapped[str]` | no | none | internal-draft fact |
| `payment_status` | `String(32)` | `Mapped[str]` | no | none | actual-payment fact |
| `official_evidence_status` | `String(32)` | `Mapped[str]` | no | none | official-evidence verification fact |
| `supersedes_obligation_id` | `String(36)` | `Mapped[str \| None]` | yes | none | same-case prior header replaced by this header |
| `supersede_reason` | `Text` | `Mapped[str \| None]` | yes | none | source-backed replacement reason |
| `created_at` | `DateTime(timezone=False)` | `Mapped[datetime]` | no | `CURRENT_TIMESTAMP` | audit creation time |
| `updated_at` | `DateTime(timezone=False)` | `Mapped[datetime]` | no | `CURRENT_TIMESTAMP` | audit update time; later writes update it explicitly |
| `created_by` | `String(36)` | `Mapped[str \| None]` | yes | none | audit creator snapshot; no user FK |
| `updated_by` | `String(36)` | `Mapped[str \| None]` | yes | none | audit updater snapshot; no user FK |

Exact named keys and constraints:

| Name | Contract |
| --- | --- |
| primary key | `PRIMARY KEY (id)` |
| `fk_t_fee_obligation_case_id` | `case_id -> t_case.id`, `ON DELETE CASCADE` |
| `fk_t_fee_obligation_source_document_id` | `source_document_id -> t_document.id`; nullable; no delete cascade |
| `fk_t_fee_obligation_source_activity_same_case` | composite `(case_id, source_activity_id) -> t_case_activity_event(case_id, id)` |
| `fk_t_fee_obligation_supersedes_same_case` | composite `(case_id, supersedes_obligation_id) -> t_fee_obligation(case_id, id)` |
| `uq_t_fee_obligation_case_id` | `UNIQUE (case_id, id)`; composite-parent key for the same-case self-FK |

Frozen invariants and exclusions:

- `source_activity_id` is mandatory and database-enforced to belong to the same case. `source_document_id` is optional because service-domain obligations may not originate from an official document; its same-case rule remains later service validation because `t_document` does not expose an approved `(case_id, id)` parent key and F1 must not alter that table.
- A correcting header points from the new row to the prior row through `supersedes_obligation_id`; `created_at`, `created_by` and `supersede_reason` retain when, who and why. F1 does not add mutable `superseded_by_*`, a speculative supersede idempotency key or a second current-identity mechanism.
- No business-state column has a server default. Recognition must explicitly provide each independent fact so one fee state cannot silently imply another.
- `due_date` is nullable because the approved plan requires an absent official deadline to remain review-blocked rather than guessed.
- There is no `estimate_status`: preview estimates are read-only and non-persistent. There is no `pay_list_status`: PayList/export artifacts are separate later carriers. Neither omission collapses those facts into another status.
- There are no amount, reduction, fee-code, fee-name, fee-year, source-amount/date, difference-review or `current_identity_key` columns. Those belong to W1-F2.
- There are no draft-item/payment-evidence link columns or relationships. Those belong to W1-F3/F4.
- Do not use `AuditMixin`: its application-side timezone defaults do not satisfy the frozen migration-level `CURRENT_TIMESTAMP` contract.
- No enum, CHECK, business index or extra UNIQUE constraint is added in F1. Status vocabulary and transition validation belong to `FPMS-V8-FO-CONTRACTS-20260712-01` and later service tasks.

## Frozen RED / GREEN Contract

- RED must define assertions requiring `FeeObligation` / `t_fee_obligation` and the exact 20 columns, types, nullability/defaults and five named constraints above; before implementation it fails because the model/table is absent.
- GREEN must prove ORM and migrated SQLite metadata match exactly, application-generated UUID IDs work after `flush()`, source activity is same-case enforced, source document FK is enforced, cross-case supersede is rejected, and nullable source document/due date/supersede fields remain accepted.
- GREEN must also prove there are no amount/line-identity columns and no business-state server defaults.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-W1-L2-CASE-ACTIVITY-EVENT-CARRIER-20260712-01`
- `FPMS-V8-W1-D3-WORK-PACKAGE-EVIDENCE-LINK-CARRIER-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): L2

### Shared ownership serialization

- `GLOBAL_ALEMBIC_HEAD` order key `7`; project this order only across owners present in the active manifest.
- `backend/app/modules/fees/models.py` order key `1`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-W1-F1-FEE-OBLIGATION-CARRIER-20260712-01.md`
- `backend/alembic/versions/v8_w1_f1_fee_obligation.py`
- `backend/app/modules/fees/models.py`
- `backend/tests/test_v8_w1_f1_fee_obligation.py`
- `artifacts/FPMS-V8-W1-F1-FEE-OBLIGATION-CARRIER-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Run in the frozen global Alembic order; use SQLite-safe forward-only migration semantics, unique-head check and clean temporary upgrade head.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_w1_f1_fee_obligation.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_w1_f1_fee_obligation.py`
- `cd backend && .venv/bin/ruff check --fix alembic/versions/v8_w1_f1_fee_obligation.py app/modules/fees/models.py tests/test_v8_w1_f1_fee_obligation.py && .venv/bin/ruff format alembic/versions/v8_w1_f1_fee_obligation.py app/modules/fees/models.py tests/test_v8_w1_f1_fee_obligation.py && .venv/bin/ruff check alembic/versions/v8_w1_f1_fee_obligation.py app/modules/fees/models.py tests/test_v8_w1_f1_fee_obligation.py`
- `cd backend && PYTHONPATH=. .venv/bin/alembic heads && PYTHONPATH=. .venv/bin/alembic upgrade head  # clean temporary SQLite database`
- `git diff --check -- backend/alembic/versions/v8_w1_f1_fee_obligation.py backend/app/modules/fees/models.py backend/tests/test_v8_w1_f1_fee_obligation.py tasks/postdemo/v8/FPMS-V8-W1-F1-FEE-OBLIGATION-CARRIER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-W1-F1-FEE-OBLIGATION-CARRIER-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-W1-F1-FEE-OBLIGATION-CARRIER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-W1-F1-FEE-OBLIGATION-CARRIER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-W1-F1-FEE-OBLIGATION-CARRIER-20260712-01` pass. Only then may this task be reported PASS.
