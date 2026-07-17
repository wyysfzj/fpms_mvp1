# FPMS V8 — Annuity task→obligation lineage carrier

Status: PASS / INDEPENDENT REREVIEW APPROVED 2026-07-16 / ULTRA CONTRACT FROZEN 2026-07-15

## Task Contract

- Task ID: `FPMS-V8-ANNUITY-TASK-OBLIGATION-LINEAGE-CARRIER-20260715-01`
- Risk: `HIGH`
- Priority: `P0-prereq-heavy-story`
- Parent task: `v8_w5_pay_list_export_artifact_01`
- Revision: `v8_d4_annuity_lineage_01`
- Authority: Delta-4 specification lines 560–594, decision `D4-11`.
- Atomic ownership: exactly this task-file path and the closure below.

## Exact Closure Slice

Add one exact six-column annuity-task-to-obligation lineage carrier through the
annuity ORM model, one SQLite-safe Alembic migration, and one focused backend
test module. The carrier records an explicit task/obligation relationship and
must fail closed when either required identity or the relationship constraints
are invalid.

Add exactly these six nullable legacy-safe columns to `t_annuity_task`:

1. `source_activity_id`: foreign key to `t_case_activity_event.id`, `RESTRICT`.
2. `source_document_id`: foreign key to `t_document.id`, `RESTRICT`.
3. `source_evidence_version_id`: foreign key to
   `t_document_evidence_version.id`, `RESTRICT`.
4. `source_evidence_content_hash`: `String(128)`.
5. `fee_obligation_id`: foreign key to `t_fee_obligation.id`, `RESTRICT`, and
   unique.
6. `grant_fee_year_key`: integer.

All six fields MUST be null together for a legacy row, or all six MUST be
non-null with `grant_fee_year_key >= 1`. Service input and new writes require
`source_evidence_content_hash` to full-match `sha256:[0-9a-f]{64}`. Preserve
existing SQLite `INTEGER PRIMARY KEY` identities. No inferred column, default,
compatibility alias, or seventh persistence field is permitted.

## Explicit Non-Closure

- No data backfill, legacy-row inference, repair, or migration-time synthesis.
- No service, API, schema, worker, UI, export, payment, fee, or deadline change.
- No change to annuity task or obligation business semantics.
- No broad refactor, adjacent cleanup, seed change, or unrelated test change.
- No customer-dependent decision may be guessed or activated.

## Remaining Follow-Up Task IDs

- `FPMS-V8-LEGACY-FEE-REDUCTION-PROVENANCE-CARRIER-20260715-01` is the next
  serialized migration and must use revision `v8_d4_annuity_lineage_01` as its
  exact parent.
- `FPMS-V8-FUTURE-ANNUITY-OBLIGATION-20260712-01` remains the separate service
  consumer; this carrier task does not absorb it.

## Dependencies and Serialization

- Parent dependency: `v8_w5_pay_list_export_artifact_01` must have durable PASS
  evidence before implementation begins.
- This HIGH schema/migration closure is serialized with every other migration
  and SQLite-writing test lane.
- The implementer must announce `READY_FOR_SERIAL_TEST` and wait for explicit
  controller `GRANT` before acquiring the repository serialization lock or
  starting pytest.
- Migration ownership remains exclusive until targeted verification and
  evidence capture finish.

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-ANNUITY-TASK-OBLIGATION-LINEAGE-CARRIER-20260715-01.md`
- `backend/app/modules/annuity/models.py`
- `backend/alembic/versions/v8_delta4_annuity_obligation_lineage.py`
- `backend/tests/test_v8_annuity_task_obligation_lineage_carrier.py`
- `artifacts/FPMS-V8-ANNUITY-TASK-OBLIGATION-LINEAGE-CARRIER-20260715-01/**`

No other file is allowed. Stop and replan if another source, test, migration,
shared-ownership file, or artifact family is required.

## Implementation Requirements

1. Add only the authoritative six-column lineage ORM carrier to
   `backend/app/modules/annuity/models.py`.
2. Add one migration at the exact allowed path, with upgrade and downgrade
   operations matching the ORM contract.
3. Keep the migration SQLite-safe: use repository-established SQLite-compatible
   operations, deterministic names, and reversible downgrade behavior.
4. Permit the six fields to be all null only for legacy-safe persistence; reject
   partial lineage, year keys below one, duplicate obligation links, invalid
   hash grammar on new writes, and violated foreign-key constraints.
5. Do not inspect or derive existing rows and do not backfill.
6. Do not add a service path or expose the carrier through an API.

## TDD

1. RED: add focused public persistence/migration assertions for the exact six
   columns, required constraints, valid linkage, invalid linkage rejection,
   upgrade, and downgrade; record the expected failing result.
2. GREEN: implement the smallest ORM and migration change that satisfies those
   assertions; record the passing targeted result.
3. REFACTOR: only simplify code introduced by this task while the same focused
   test remains green.
4. Run no broad or full-repository suite except at an explicitly authorized
   manifest close point.

## Verification Commands

After controller `GRANT` and repository-lock acquisition, run the repository's
targeted backend environment command for:

```bash
pytest -q backend/tests/test_v8_annuity_task_obligation_lineage_carrier.py
```

Then run only the repository task gate and atomic evidence validation required
for this task. If the repository environment requires a documented command
prefix, preserve this exact test target.

## Evidence Path

- `artifacts/FPMS-V8-ANNUITY-TASK-OBLIGATION-LINEAGE-CARRIER-20260715-01/**`

## Serialized Evidence

- Initialize evidence only through:
  `./scripts/evidence_init.sh FPMS-V8-ANNUITY-TASK-OBLIGATION-LINEAGE-CARRIER-20260715-01 --task-file tasks/postdemo/v8/FPMS-V8-ANNUITY-TASK-OBLIGATION-LINEAGE-CARRIER-20260715-01.md --allowlist tasks/postdemo/v8/FPMS-V8-ANNUITY-TASK-OBLIGATION-LINEAGE-CARRIER-20260715-01.md backend/app/modules/annuity/models.py backend/alembic/versions/v8_delta4_annuity_obligation_lineage.py backend/tests/test_v8_annuity_task_obligation_lineage_carrier.py artifacts/FPMS-V8-ANNUITY-TASK-OBLIGATION-LINEAGE-CARRIER-20260715-01`
- Preserve task-local `results.jsonl`, `summary.md`, scoped `git/diff.patch`,
  dirty-baseline artifacts when applicable, targeted logs, scope validation,
  repository task-gate output, and atomic-evidence validation output.
- The latest required result and log must be non-stale and successful.
- An independent reviewer must issue an approved, zero-finding verdict for this
  exact task; the implementer cannot self-approve.
- Record lock acquisition/release and the controller `GRANT` with the targeted
  SQLite-writing test evidence.

## Done Definition

- Exactly one authoritative six-column annuity task→obligation lineage carrier
  exists in the allowed ORM file and exact migration path.
- ORM and migration agree exactly on all six columns and authoritative
  constraints; upgrade and downgrade are SQLite-safe and verified.
- Invalid or incomplete lineage fails closed, with no silent default or inferred
  relationship.
- No backfill, service behavior, API exposure, or non-closure work exists.
- The targeted test passes after serialized execution.
- Baseline-subtracted scope validation reports no path outside Allowed Files.
- Task-local Evidence 1.1 artifacts are complete and current.
- Independent review is approved with zero findings.
- Repository task gate and atomic evidence validation both PASS.

## Stop Conditions

Stop and report BLOCKED with evidence if the authoritative six-column contract
cannot be read unambiguously, the parent lacks PASS evidence, another migration
or SQLite lane owns the lock, an outside-allowlist file is required, or a new
business/customer decision is discovered.
