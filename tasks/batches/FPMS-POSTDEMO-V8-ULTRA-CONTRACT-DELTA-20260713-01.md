# FPMS Post-demo V8 Ultra Contract Delta Materialization Batch

Status: PASS
Controller task: `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01`
Story Shape Classification: `shared_file_density=high`,
`prereq_dependency_density=high`, `be_fe_coupling=medium`, `evidence_cost=high`
Chosen runbook: `P0-prereq-heavy-story`

This is a contract-materialization manifest only. It is not product implementation
authorization, and it never permits one worker to implement more than one product task.
Each row is one exact task-file owner; shared ownership and SQLite-writing verification
remain serialized under AGENTS.md.

| Row | Wave | Exact task-file path | Owner role | Runbook | Exact materialization closure | Direct dependency | Allowed materialization edit | Explicit non-closure |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 01 | M1 | `tasks/postdemo/v8/FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01.md` | Architect worker | `P0-prereq-heavy-story` | Freeze lazy lifecycle registry/rule decision/replay/projector/error/TDD contract. | activity append + legacy projection | this task file + its artifact family only | no product implementation or event-rule absorption |
| 02 | M1 | `tasks/postdemo/v8/FPMS-V8-LC-CASE-OPENED-20260712-01.md` | Architect worker | `P0-prereq-heavy-story` | Freeze first `lifecycle_rules` registry implementation and CASE_OPENED only. | row 01 | this task file + its artifact family only | no later lifecycle event rule |
| 03 | M1 | `tasks/postdemo/v8/FPMS-V8-CASE-UPDATE-STATUS-INPUT-GATE-20260712-01.md` | Architect worker | `P0-prereq-heavy-story` | Freeze five-carrier predicate, no-op, exact 409 and CAS contract. | legacy projection | this task file + its artifact family only | no legacy data repair or other case-update behavior |
| 04 | M2 | `tasks/postdemo/v8/FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01.md` | Architect worker | `P0-prereq-heavy-story` | Freeze instruction transition/activity/idempotency/transaction service contract. | recognize obligation + activity append | this task file + its artifact family only | no HTTP, UI, draft, payment or lifecycle change |
| 05 | M2 | `tasks/postdemo/v8/FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01.md` | Architect worker | `P0-prereq-heavy-story` | Freeze CNIPA snapshot, effective interval, activation/replay/CAS/seed contract. | official-rate-book carrier | this task file + its artifact family only | no candidate import, real-rate activation or provider implementation |
| 06 | M2 | `tasks/postdemo/v8/FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01.md` | Architect worker | `P0-prereq-heavy-story` | Freeze DTO, canonical identity/evidence/hash/replay/race contract. | F5 carrier + DE register + DE review | this task file + its artifact family only | no eligibility inference, read selection, API or UI |
| 07 | M3 | `tasks/postdemo/v8/FPMS-V8-PAYLIST-EXPORT-ARTIFACT-CARRIER-20260712-01.md` | Architect worker | `P0-prereq-heavy-story` | Freeze exact export carrier table/ORM/constraints/migration/SQLite tests. | rate-book carrier + GLOBAL_ALEMBIC_HEAD | this task file + its artifact family only | no export generation, upload, payment or ticket semantics |
| 08 | M3 | `tasks/postdemo/v8/FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01.md` | Architect worker | `P0-prereq-heavy-story` | Freeze scope precedence/as-of/current/error/single-query read contract. | decision-gate record service | this task file + its artifact family only | no write, history reconstruction, API or decision inference |
| 09 | M3 | `tasks/postdemo/v8/FPMS-V8-GRANT-NOTICE-FEE-LINE-SNAPSHOT-20260713-01.md` | Architect worker | `P0-single-lane-story` | Create one pure canonical reviewed grant fee-line snapshot/parser task. | DE review service | this task file + its artifact family only | no OCR, rate lookup, obligation, schema or API |
| 10 | M4 | `tasks/postdemo/v8/FPMS-V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-20260712-01.md` | Architect worker | `P0-prereq-heavy-story` | Require immutable fee-line snapshot/hash in exact lifecycle activity payload. | row 09 + grant lifecycle rule + document semantics | this task file + its artifact family only | no fee obligation, OCR, PDF parsing or direct status write |
| 11 | M4 | `tasks/postdemo/v8/FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01.md` | Architect worker | `P0-prereq-heavy-story` | Consume only activity-bound reviewed fee lines to recognize annuity obligations. | rows 09–10 + recognize obligation | this task file + its artifact family only | no amount guessing, draft, OCR or extra fee lines |
| 12 | M4 | `tasks/postdemo/v8/FPMS-V8-OFFICIAL-FEE-ESTIMATE-RATE-PROVIDER-20260713-01.md` | Architect worker | `P0-prereq-heavy-story` | Create one read-only production provider task for supported baseline triggers. | preview service + row 05 + row 06 | this task file + its artifact family only | no HTTP, calculation duplication, fallback or write |
| 13 | M5 | `tasks/postdemo/v8/FPMS-V8-FO-PREVIEW-HTTP-ADAPTER-20260712-01.md` | Architect worker | `P0-prereq-heavy-story` | Freeze strict V8 request/response/provider/error/no-write HTTP contract. | preview service + row 12 | this task file + its artifact family only | no legacy request compatibility, obligation or draft |
| 14 | M5 | `tasks/postdemo/v8/FPMS-V8-OFFICIAL-FEE-PREVIEW-LEGACY-TEST-MIGRATION-20260713-01.md` | Architect worker | `P0-single-lane-story` | Create one test-only post-HTTP obsolete-semantic migration task. | row 13 | this task file + its artifact family only | no product or backward-compatibility path |
| 15 | M5 | `tasks/postdemo/v8/FPMS-V8-FOUNDATION-CLOSE-20260712-01.md` | Architect worker | `P0-prereq-heavy-story` | Require all three external tasks plus controller/overlay validation before close. | immutable Foundation gates + rows 09, 12, 14 | this task file + its artifact family only | no baseline manifest rewrite or premature release close |
| 16 | M6 | `tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01.md` | Ultra controller | `P0-prereq-heavy-story` | Create and audit this manifest plus deterministic overlay/validator. | rows 01–15 materialized | controller task, this manifest and controller artifact family only | no row 01–15 or product/baseline edit; no self-approval |

## Wave and shared-file order

1. M1–M5 task-file owners remain distinct and conflict-free.
2. M6 is the sole writer of this manifest and the additive overlay artifact family.
3. Later High execution uses one full effective
   `backend/app/modules/fees/official_rate_book.py` chain: keep all eleven baseline owners
   in their relative order and insert Provider exactly after activation. This is not a
   two-owner replacement chain.
4. Later High execution orders snapshot → grant adapter → annuity.
5. `GLOBAL_ALEMBIC_HEAD` and `GLOBAL_SQLITE_SERIAL_QUEUE` remain single-owner queues.
6. Final close orders provider → HTTP → legacy test migration → Foundation close.

## Batch done definition

- All sixteen unique task-file paths and row order validate against the approved plan.
- Fifteen product task contracts remain High-ready/Ultra-frozen/not-started.
- Deterministic overlay validates unchanged baseline hashes/counts, exact task hashes,
  dependencies, serialization and effective Foundation closure.
- Two independent controller reviews approve before the controller may become PASS.
