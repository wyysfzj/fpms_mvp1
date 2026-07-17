# FPMS-V8-W1-F3-OBLIGATION-DRAFT-LINK-CARRIER-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `8. Wave 1 — schema spine, globally serialized`
Catalog ordinal: `11`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `360`
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

- RED expectation: Exact schema test fails because `FeeObligationDraftItemLink` / `t_fee_obligation_draft_item_link`, revision `v8_w1_f3_draft_item_link_01`, the seven frozen columns or the three named constraints are absent.
- GREEN expectation: Exact ORM and migrated-SQLite tests prove the seven frozen columns, physical types, nullability/defaults, exact link uniqueness, both endpoint FKs and cascade behavior; task-scoped Ruff, unique-head check and clean temporary SQLite `upgrade head` pass.

## Ultra Replan Record — 2026-07-13

- Blocker found before RED/source edits: the canonical design and plan froze an obligation-line to draft-item link carrier, but not its physical column names, types, nullability, audit defaults, link cardinality or delete actions.
- Resolution: the physical contract below is frozen from the canonical V8 fee design, frozen F2 line contract and existing `FeeDraft`/`FeeItem` endpoint conventions. The exact closure remains one relationship carrier; no draft creation, service behavior or target-table prerequisite is absorbed.
- Story Shape Classification remains unchanged: shared fee-model ownership and the globally serialized Alembic/SQLite chain still make this a high-cost prerequisite.
- `chosen_runbook` remains `P0-prereq-heavy-story`.
- Implementation resumes only after dependency `FPMS-V8-W1-F2-FEE-OBLIGATION-LINE-CARRIER-20260712-01` is PASS and the unique Alembic head is `v8_w1_f2_fee_obligation_line_01`.

## Frozen Physical Schema Contract

ORM class and table:

- Class: `FeeObligationDraftItemLink`
- Table: `t_fee_obligation_draft_item_link`
- Migration revision: `v8_w1_f3_draft_item_link_01`
- Migration `down_revision`: `v8_w1_f2_fee_obligation_line_01`
- Migration policy: forward-only; `downgrade()` raises `NotImplementedError`.

The table has exactly these seven columns:

| Column | SQLAlchemy / Alembic type | ORM annotation | Nullable | Server default | Meaning |
| --- | --- | --- | --- | --- | --- |
| `id` | `String(36)` | `Mapped[str]` | no | none; application UUID | link identity |
| `obligation_line_id` | `String(36)` | `Mapped[str]` | no | none | exact F2 obligation line represented by the draft item |
| `fee_item_id` | `String(36)` | `Mapped[str]` | no | none | exact existing `FeeItem` row |
| `created_at` | `DateTime(timezone=False)` | `Mapped[datetime]` | no | `CURRENT_TIMESTAMP` | link creation time |
| `updated_at` | `DateTime(timezone=False)` | `Mapped[datetime]` | no | `CURRENT_TIMESTAMP` | audit update time; later writes update it explicitly |
| `created_by` | `String(36)` | `Mapped[str \| None]` | yes | none | link creator snapshot; no user FK |
| `updated_by` | `String(36)` | `Mapped[str \| None]` | yes | none | link updater snapshot; no user FK |

Exact named keys and constraints:

| Name | Contract |
| --- | --- |
| primary key | `PRIMARY KEY (id)`; repository-default unnamed PK |
| `fk_t_fee_obligation_draft_item_link_obligation_line_id` | `obligation_line_id -> t_fee_obligation_line.id`, `ON DELETE CASCADE` |
| `fk_t_fee_obligation_draft_item_link_fee_item_id` | `fee_item_id -> t_fee_item.id`, `ON DELETE CASCADE` |
| `uq_t_fee_obligation_draft_item_link_pair` | `UNIQUE (obligation_line_id, fee_item_id)` in exactly this order |

Frozen invariants and exclusions:

- F3 freezes relationship identity, not draft-generation policy. The exact pair is idempotent; the carrier does not invent a stronger one-to-one rule because no such cardinality is approved by the canonical design. Any stricter allocation rule belongs to the later service contract.
- `ON DELETE CASCADE` removes a relationship whose endpoint is removed. It does not authorize a later service to delete obligation truth or financial history; deletion policy remains outside F3.
- There is no `case_id`. Both endpoints lack an approved composite parent-key path that would enforce the full same-case invariant without modifying F2 or legacy `t_fee_item`; a redundant case column would therefore provide only partial/misleading integrity. `FPMS-V8-FO-PREPARE-DRAFT-20260712-01` must validate that the obligation line, `FeeItem` and owning `FeeDraft` belong to the same case before inserting the link.
- There is no `draft_id`: `fee_item_id -> t_fee_item.draft_id` is the existing authoritative draft association. Duplicating it would create an avoidable consistency surface.
- Do not use `AuditMixin`: its application-side timezone defaults do not satisfy the frozen migration-level `CURRENT_TIMESTAMP` contract.
- No activity id, amount, status, source, payload, idempotency key, enum/CHECK, business index, extra UNIQUE or extra FK is added. F3 does not create a `FeeDraft`/`FeeItem`, append an activity or update F1/F2 status.

## Frozen RED / GREEN Contract

- RED must assert `FeeObligationDraftItemLink` / `t_fee_obligation_draft_item_link`, revision/down-revision identity, the exact seven columns, their physical types/nullability/defaults and the three named constraints above; before implementation it fails because the model/table/migration is absent.
- GREEN must prove ORM and reflected migrated-SQLite metadata match exactly, an application UUID survives `flush()`, a valid obligation-line/item pair succeeds, missing obligation-line or fee-item references fail, and an exact duplicate pair fails.
- GREEN must prove deleting either endpoint cascades only its link, multiple distinct items may link to the same obligation line, multiple distinct obligation lines may link to the same item at carrier level, audit timestamps use `CURRENT_TIMESTAMP`, and no `case_id`, `draft_id`, service behavior or unapproved field is present.

## Exact Closure Slice

Add only the frozen seven-column `FeeObligationDraftItemLink` / `t_fee_obligation_draft_item_link` carrier with exact obligation-line and existing `FeeItem` FKs, pair uniqueness, SQLite-safe audit fields and endpoint-delete cascades; no draft creation or same-case service behavior.

## Explicit Non-Closure

No backfill, service, endpoint, seed, UI or second table/carrier. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-W1-F2-FEE-OBLIGATION-LINE-CARRIER-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): F2

### Shared ownership serialization

- `GLOBAL_ALEMBIC_HEAD` order key `9`; project this order only across owners present in the active manifest.
- `backend/app/modules/fees/models.py` order key `3`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-W1-F3-OBLIGATION-DRAFT-LINK-CARRIER-20260712-01.md`
- `backend/alembic/versions/v8_w1_f3_obligation_draft_link.py`
- `backend/app/modules/fees/models.py`
- `backend/tests/test_v8_w1_f3_obligation_draft_link.py`
- `artifacts/FPMS-V8-W1-F3-OBLIGATION-DRAFT-LINK-CARRIER-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Run in the frozen global Alembic order; use SQLite-safe forward-only migration semantics, unique-head check and clean temporary upgrade head.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_w1_f3_obligation_draft_link.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_w1_f3_obligation_draft_link.py`
- `cd backend && .venv/bin/ruff check --fix alembic/versions/v8_w1_f3_obligation_draft_link.py app/modules/fees/models.py tests/test_v8_w1_f3_obligation_draft_link.py && .venv/bin/ruff format alembic/versions/v8_w1_f3_obligation_draft_link.py app/modules/fees/models.py tests/test_v8_w1_f3_obligation_draft_link.py && .venv/bin/ruff check alembic/versions/v8_w1_f3_obligation_draft_link.py app/modules/fees/models.py tests/test_v8_w1_f3_obligation_draft_link.py`
- `cd backend && PYTHONPATH=. .venv/bin/alembic heads && PYTHONPATH=. .venv/bin/alembic upgrade head  # clean temporary SQLite database`
- `git diff --check -- backend/alembic/versions/v8_w1_f3_obligation_draft_link.py backend/app/modules/fees/models.py backend/tests/test_v8_w1_f3_obligation_draft_link.py tasks/postdemo/v8/FPMS-V8-W1-F3-OBLIGATION-DRAFT-LINK-CARRIER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-W1-F3-OBLIGATION-DRAFT-LINK-CARRIER-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-W1-F3-OBLIGATION-DRAFT-LINK-CARRIER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-W1-F3-OBLIGATION-DRAFT-LINK-CARRIER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-W1-F3-OBLIGATION-DRAFT-LINK-CARRIER-20260712-01` pass. Only then may this task be reported PASS.
