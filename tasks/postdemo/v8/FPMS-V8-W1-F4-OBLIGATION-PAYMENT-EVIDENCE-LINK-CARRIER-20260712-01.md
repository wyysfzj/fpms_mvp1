# FPMS-V8-W1-F4-OBLIGATION-PAYMENT-EVIDENCE-LINK-CARRIER-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `8. Wave 1 — schema spine, globally serialized`
Catalog ordinal: `12`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `361`
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

- RED expectation: Exact schema test fails because `FeeObligationPaymentEvidenceLink` / `t_fee_obligation_payment_evidence_link`, revision `v8_w1_f4_payment_link_01`, the seven frozen columns or the three named constraints are absent.
- GREEN expectation: Exact ORM and migrated-SQLite tests prove the seven frozen columns, physical types, nullability/defaults, exact obligation-line/GovPayment FKs and pair uniqueness; task-scoped Ruff, unique-head check and clean temporary SQLite `upgrade head` pass.

## Ultra Replan Record — 2026-07-13

- Blocker found before RED/source edits: the canonical design and plan required a separate obligation-line/payment-evidence link and same-case validation, but did not freeze whether the evidence reference was polymorphic or a concrete legacy adapter, nor its physical columns, audit fields, FK/delete actions or uniqueness.
- Resolution: freeze the minimum concrete link to the existing `GovPayment` adapter. The carrier stores no duplicated `case_id`; the later payment-evidence service loads the F2 line and GovPayment and enforces their same-case invariant before writing.
- This remains exactly one link-table carrier. It does not change the closure slice, non-closure boundary, allowlist, customer-gate classification or shared-file serialization.
- Story Shape Classification remains unchanged and `chosen_runbook` remains `P0-prereq-heavy-story`.
- Implementation resumes only after F3 is PASS and the unique Alembic head is `v8_w1_f3_draft_item_link_01`.

## Frozen Physical Schema Contract

ORM class and table:

- Class: `FeeObligationPaymentEvidenceLink`
- Table: `t_fee_obligation_payment_evidence_link`
- Migration revision: `v8_w1_f4_payment_link_01`
- Migration `down_revision`: `v8_w1_f3_draft_item_link_01`
- Migration policy: forward-only; `downgrade()` raises `NotImplementedError`.

The table has exactly these seven columns:

| Column | SQLAlchemy / Alembic type | ORM annotation | Nullable | Server default | Meaning |
| --- | --- | --- | --- | --- | --- |
| `id` | `String(36)` | `Mapped[str]` | no | none; application UUID | link identity |
| `obligation_line_id` | `String(36)` | `Mapped[str]` | no | none | linked F2 obligation line |
| `gov_payment_id` | `Integer` | `Mapped[int]` | no | none | linked existing `GovPayment`, representing actual payment evidence |
| `created_at` | `DateTime(timezone=False)` | `Mapped[datetime]` | no | `CURRENT_TIMESTAMP` | link creation time |
| `updated_at` | `DateTime(timezone=False)` | `Mapped[datetime]` | no | `CURRENT_TIMESTAMP` | link update time; later writes update it explicitly |
| `created_by` | `String(36)` | `Mapped[str \| None]` | yes | none | audit creator snapshot; no user FK |
| `updated_by` | `String(36)` | `Mapped[str \| None]` | yes | none | audit updater snapshot; no user FK |

Exact named keys and constraints:

| Name | Contract |
| --- | --- |
| primary key | `PRIMARY KEY (id)`; repository-default unnamed PK |
| `fk_t_fee_obligation_payment_evidence_link_obligation_line_id` | `obligation_line_id -> t_fee_obligation_line.id`, `ON DELETE CASCADE` |
| `fk_t_fee_obligation_payment_evidence_link_gov_payment_id` | `gov_payment_id -> t_gov_payment.id`, `ON DELETE CASCADE` |
| `uq_t_fee_obligation_payment_evidence_link_pair` | `UNIQUE (obligation_line_id, gov_payment_id)` in exactly this order |

Frozen invariants and exclusions:

- `gov_payment_id` is a concrete `Integer` FK because the approved design keeps existing `GovPayment` as the actual-payment adapter and the later GovPayment activity task registers that adapter against the obligation seam. Do not replace it with unverified polymorphic `object_type/object_id` fields or a new payment-evidence carrier.
- The relation is many-to-many: one payment may evidence multiple obligation lines and one line may have multiple payments; only the exact repeated pair is rejected.
- `ON DELETE CASCADE` removes only the relationship when either endpoint is removed. It does not authorize a later service to delete obligation truth or payment history; endpoint deletion policy remains outside F4.
- The database proves both referenced rows exist. It does not claim to prove they belong to the same case: the frozen F2 line and legacy `t_gov_payment` do not both expose an approved composite parent key usable here, and F4 must not alter either parent carrier. `FPMS-V8-FO-PAYMENT-EVIDENCE-20260712-01` must load both rows, require `line.case_id == gov_payment.case_id`, and return 409/no write for a mismatch before `flush`.
- `GovPayment` is actual-payment evidence only at this seam. An official receipt, ticket, official-site acceptance fact or legacy `official_receipt_no` must not set or imply `official_evidence_status`; the separate official-payment-evidence adapter owns that later transition.
- `created_at`/`created_by` are sufficient to record when/by whom the link was created. Do not add `linked_at`, `linked_by`, `case_id`, `obligation_id`, `pay_list_id`, `fee_item_id`, payment amount/status snapshots or official-evidence columns.
- Do not use `AuditMixin`: its application-side timezone defaults do not satisfy the frozen migration-level `CURRENT_TIMESTAMP` contract.
- No enum, CHECK, secondary/business index, extra UNIQUE or extra FK is added. Same-case validation, idempotent service behavior, status transitions and activity append belong to later tasks.

## Frozen RED / GREEN Contract

- RED must assert `FeeObligationPaymentEvidenceLink` / `t_fee_obligation_payment_evidence_link`, revision/down-revision identity, the exact seven columns, their types/nullability/defaults and the three named constraints above; before implementation it fails because the model/table/migration is absent.
- GREEN must prove ORM and reflected migrated-SQLite metadata match exactly, an application UUID survives `flush()`, a valid line/GovPayment pair succeeds, either missing parent fails with SQLite foreign keys enabled, and the exact duplicate pair fails.
- GREEN must prove deleting either endpoint cascades only its link, distinct payments may link to one line and one payment may link to distinct lines, audit timestamps use `CURRENT_TIMESTAMP`, and no `case_id`, polymorphic reference, official-evidence field or F3 draft-item behavior is present.

## Exact Closure Slice

Add only the frozen seven-column `FeeObligationPaymentEvidenceLink` / `t_fee_obligation_payment_evidence_link` carrier, concretely linking an F2 obligation line to an existing `GovPayment` actual-payment evidence row with exact pair uniqueness and SQLite-safe audit fields.

## Explicit Non-Closure

No backfill, service, endpoint, seed, UI or second table/carrier. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-W1-F2-FEE-OBLIGATION-LINE-CARRIER-20260712-01`
- `FPMS-V8-W1-F3-OBLIGATION-DRAFT-LINK-CARRIER-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): F2

### Shared ownership serialization

- `GLOBAL_ALEMBIC_HEAD` order key `10`; project this order only across owners present in the active manifest.
- `backend/app/modules/fees/models.py` order key `4`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-W1-F4-OBLIGATION-PAYMENT-EVIDENCE-LINK-CARRIER-20260712-01.md`
- `backend/alembic/versions/v8_w1_f4_obligation_payment_link.py`
- `backend/app/modules/fees/models.py`
- `backend/tests/test_v8_w1_f4_obligation_payment_link.py`
- `artifacts/FPMS-V8-W1-F4-OBLIGATION-PAYMENT-EVIDENCE-LINK-CARRIER-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Run in the frozen global Alembic order; use SQLite-safe forward-only migration semantics, unique-head check and clean temporary upgrade head.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_w1_f4_obligation_payment_link.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_w1_f4_obligation_payment_link.py`
- `cd backend && .venv/bin/ruff check --fix alembic/versions/v8_w1_f4_obligation_payment_link.py app/modules/fees/models.py tests/test_v8_w1_f4_obligation_payment_link.py && .venv/bin/ruff format alembic/versions/v8_w1_f4_obligation_payment_link.py app/modules/fees/models.py tests/test_v8_w1_f4_obligation_payment_link.py && .venv/bin/ruff check alembic/versions/v8_w1_f4_obligation_payment_link.py app/modules/fees/models.py tests/test_v8_w1_f4_obligation_payment_link.py`
- `cd backend && PYTHONPATH=. .venv/bin/alembic heads && PYTHONPATH=. .venv/bin/alembic upgrade head  # clean temporary SQLite database`
- `git diff --check -- backend/alembic/versions/v8_w1_f4_obligation_payment_link.py backend/app/modules/fees/models.py backend/tests/test_v8_w1_f4_obligation_payment_link.py tasks/postdemo/v8/FPMS-V8-W1-F4-OBLIGATION-PAYMENT-EVIDENCE-LINK-CARRIER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-W1-F4-OBLIGATION-PAYMENT-EVIDENCE-LINK-CARRIER-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-W1-F4-OBLIGATION-PAYMENT-EVIDENCE-LINK-CARRIER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-W1-F4-OBLIGATION-PAYMENT-EVIDENCE-LINK-CARRIER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-W1-F4-OBLIGATION-PAYMENT-EVIDENCE-LINK-CARRIER-20260712-01` pass. Only then may this task be reported PASS.
