# Story V8-ANNUITY-TASK-OBLIGATION-LINEAGE-CARRIER-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Product/test commit: `83d014fb825c76e90c53821c7db9ed7f3cd49436`
- Outcome: adopt the frozen D4-11 six-field annuity task-to-obligation lineage carrier on
  the current integrated tree.
- External prerequisite ID:
  `FPMS-V8-ANNUITY-TASK-OBLIGATION-LINEAGE-CARRIER-20260715-01`.
- Authority: its frozen task contract and Delta-4 D4-11.

## Exact paths and behavior

- `backend/app/modules/annuity/models.py`
- `backend/alembic/versions/v8_delta4_annuity_obligation_lineage.py`
- `backend/tests/test_v8_annuity_task_obligation_lineage_carrier.py`

The carrier has exactly six nullable legacy-safe fields. They are all null for a legacy row
or all non-null with a positive grant-year key. Four identities use `RESTRICT` foreign
keys, the obligation link is unique, and new hashes use the exact lowercase SHA-256
grammar. The migration is SQLite-safe and reversible. It performs no backfill and exposes
no service or API behavior.

## Verification and non-goals

The focused SQLite migration/persistence probe passed `3/3`; exact three-path Ruff passed.
Independent High review approved P0/P1/P2 `0/0/0`. The three current paths are
byte-identical to the original product commit. No backfill, service, API, fee rule,
instruction adapter, rate candidate or future-annuity behavior enters this adoption.

