# FPMS-V8-GRANT-EVIDENCE-OFFICIAL-COPY-VERIFICATION-CARRIER-SCHEMA-20260810-01

Status: FROZEN / READY FOR IMPLEMENTATION
Risk class: `PROTECTED`
Runbook: `P0-prereq-heavy-story`

## Authority and prerequisites

- Scheme A customer source SHA-256
  `e6cfd648f1d366e27bde3f74310f00033a6db60ce55d850d2e668764745faace`.
- Accepted grant source carrier/service/API.
- Accepted grant manual-review role carrier/service/API.
- Accepted immutable `DocumentEvidenceVersion` carrier.
- Current Alembic head must be exactly `v8_grant_manual_review_role_01` before implementation.

The customer requires retention of official raw evidence, acquisition facts, reasons, actors and
complete audit, with different actual users for first and second verification. Existing
`GrantEvidenceCandidate` contains a proposer/reviewer workflow and cannot prove who acquired or
twice verified the official copy. It must not be overloaded or altered.

## Exact closure

Add one empty SQLite-safe append-lineage event carrier:

- ORM class `GrantOfficialCopyVerificationEvent` in
  `backend/app/modules/documents/models.py`;
- table `t_grant_official_copy_verification_event`;
- registry import/export in `backend/app/models/__init__.py`;
- forward-only migration
  `backend/alembic/versions/v8_grant_official_copy_verification_carrier.py` with revision
  `v8_grant_official_copy_01`, down revision `v8_grant_manual_review_role_01`;
- focused schema test
  `backend/tests/test_v8_grant_official_copy_verification_carrier_schema.py`.

The event chain is exactly `ACQUIRED -> FIRST_VERIFIED -> SECOND_VERIFIED`. Every event copies and
binds the exact official evidence version, source record/configuration, institution role
configuration, scope, raw-evidence content hash, source/config/role snapshot hashes, acquisition
reference and method, actor, action time and reason. A later service owns role membership,
actual-user separation, canonical snapshot construction, predecessor/current CAS and progression.

## Exact 23-column table

In this exact order:

1. `id String(36)` primary key, application UUID;
2. `evidence_version_id String(36)` non-null;
3. `source_config_id String(36)` non-null;
4. `source_record_id String(36)` non-null;
5. `role_config_id String(36)` non-null;
6. `evidence_scope String(32)` non-null;
7. `event_type String(32)` non-null;
8. `actor_id String(36)` non-null;
9. `action_at DateTime(timezone=False)` non-null;
10. `reason Text` non-null;
11. `original_reference String(512)` non-null;
12. `acquisition_method_snapshot String(64)` non-null;
13. `evidence_content_hash String(128)` non-null;
14. `source_config_snapshot_hash String(64)` non-null;
15. `source_snapshot_hash String(64)` non-null;
16. `role_config_snapshot_hash String(64)` non-null;
17. `predecessor_event_id String(36)` nullable;
18. `event_snapshot Text` non-null;
19. `event_snapshot_hash String(64)` non-null;
20. `idempotency_key String(128)` non-null;
21. `current_identity_key String(96)` nullable;
22. `created_at DateTime(timezone=False)` non-null, server `CURRENT_TIMESTAMP`;
23. `updated_at DateTime(timezone=False)` non-null, server `CURRENT_TIMESTAMP`.

No other column or business default is allowed.

## Constraints and index

Unique constraints:

- `uq_t_grant_official_copy_event_stage` on `(evidence_version_id, event_type)`;
- `uq_t_grant_official_copy_event_idempotency_key` on `idempotency_key`;
- `uq_t_grant_official_copy_event_current_identity_key` on `current_identity_key`.

All foreign keys are `ON DELETE RESTRICT`:

- evidence version -> `t_document_evidence_version.id`;
- source configuration -> `t_grant_evidence_source_config.id`;
- source record -> `t_grant_evidence_source_record.id`;
- role configuration -> `t_grant_manual_review_role_config.id`;
- actor -> `t_user.id`;
- predecessor -> the same event table `id`.

Named checks:

- scope is `GRANT_ANNOUNCEMENT` or `PATENT_REGISTER`;
- event type is `ACQUIRED`, `FIRST_VERIFIED` or `SECOND_VERIFIED`;
- `ACQUIRED` has null predecessor and both verification stages have a predecessor;
- the four 64-character snapshot hashes are lowercase hexadecimal;
- `evidence_content_hash` is nonblank, trimmed, NUL-free and at most its carrier length;
- current identity is null or exactly
  `'GRANT_OFFICIAL_COPY|' || evidence_version_id`.

Create one non-unique index
`ix_t_grant_official_copy_event_evidence_stage` on
`(evidence_version_id, event_type, action_at)`.

## Frozen later-service boundary

Canonical event JSON has exactly: `schema`, `evidence_version_id`, `source_config_id`,
`source_record_id`, `role_config_id`, `evidence_scope`, `event_type`, `actor_id`, `action_at`,
`reason`, `original_reference`, `acquisition_method_snapshot`, `evidence_content_hash`,
`source_config_snapshot_hash`, `source_snapshot_hash`, `role_config_snapshot_hash`, and
`predecessor_event_id`. Schema is `CNIPA_GRANT_OFFICIAL_COPY_VERIFICATION_EVENT_V1`.

The later service must resolve accepted source and role configurations at each action time, prove
the actor is active in the exact configured duty role, require first verifier and second verifier
to be different actual users, copy all lineage bytes, progress exact predecessor stages, and use a
nested-savepoint current-pointer CAS. A current terminal second-verification event is necessary but
does not itself confirm legal status or authorize candidate review.

## Non-closure

No event insert/transition service or API; no source/role/default/seed; no modification to
`GrantEvidenceCandidate`, evidence version, attachment or existing table; no ingestion/review/legal
status/lifecycle/deadline/document/fee/payment behavior; no UI or generic event abstraction.

## Allowed files

- this task file;
- migration file above;
- `backend/app/modules/documents/models.py`;
- `backend/app/models/__init__.py`;
- focused test above.

## Frozen acceptance matrix

1. ORM and reflected SQLite expose exactly 23 ordered columns, six RESTRICT FKs, three uniques,
   six named checks and one exact index, matching the migration.
2. A fully referenced synthetic ACQUIRED row inserts; UUID generation works without `RETURNING`.
3. Missing referenced rows, duplicate stage/idempotency/current identity, invalid scope/event,
   invalid predecessor shape, bad hashes/content/current key are rejected independently.
4. FIRST/SECOND rows require predecessor FKs; deleting any referenced authority/evidence/actor or
   predecessor is restricted.
5. Registry bootstrap resolves all FK targets; fresh clean upgrade reaches the one exact head and
   leaves the new table empty. No role/user/source/event/default row is inserted.

## Verification

- Focused RED/GREEN pytest for the named schema test.
- Scoped Ruff on migration/model/registry/test.
- `PYTHONPATH=. .venv/bin/alembic heads` is exactly `v8_grant_official_copy_01 (head)`.
- Clean temporary SQLite `upgrade head/current` reaches that head with zero new-table rows.
- Exact allowed-path diff-check.

One independent High reviewer reviews the exact implementation commit/range and reruns decisive
checks. PASS requires `P0/P1/P2 = 0/0/0`; no Full or release gate belongs here.
