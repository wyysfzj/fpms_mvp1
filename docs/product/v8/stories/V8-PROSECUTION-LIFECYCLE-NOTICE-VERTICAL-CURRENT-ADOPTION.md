# Story V8-PROSECUTION-LIFECYCLE-NOTICE-VERTICAL-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Outcome: adopt and prove the exact notice-driven lifecycle rules from application
  acceptance through preliminary examination, publication, substantive examination and
  the first or later office-action notice, while preserving the rectification branch and
  all legal-status, deadline and evidence-lineage fail-closed boundaries.
- Change mode: exact current adoption of the independently accepted archived product/test
  slices. No historical RED is rerun and no later lifecycle rule is adopted.
- Authority: lifecycle, deadline and evidence-lineage invariants in
  `docs/product/v8/domain-contract.md`, frozen catalog rows 22–28 and their exact task
  contracts.
- Archive comparison anchor: `6b2ef89da447353380b99853168d4d38aaf9210a`.

## Catalog IDs and dependency order

1. `FPMS-V8-LC-ACCEPTANCE-NOTICE-RECORDED-20260712-01` (ordinal 22)
2. `FPMS-V8-LC-PRELIMINARY-EXAMINATION-STARTED-20260712-01` (ordinal 23)
3. `FPMS-V8-LC-PRELIMINARY-EXAMINATION-PASSED-20260712-01` (ordinal 24)
4. `FPMS-V8-LC-RECTIFICATION-NOTICE-RECORDED-20260712-01` (ordinal 25)
5. `FPMS-V8-LC-PUBLICATION-NOTICE-RECORDED-20260712-01` (ordinal 26)
6. `FPMS-V8-LC-SUBSTANTIVE-EXAMINATION-STARTED-20260712-01` (ordinal 27)
7. `FPMS-V8-LC-OA-NOTICE-RECORDED-20260712-01` (ordinal 28)

The current-reviewed filing lifecycle story is the exact predecessor. Catalog order is
implementation/ownership order, not permission to invent a runtime transition:
rectification and publication are separate events from the exact preliminary-examination
projection, and this story adds no uncontracted rectification-response completion event.

## Observable lifecycle decisions

| Event | Exact prior | Result |
| --- | --- | --- |
| `ACCEPTANCE_NOTICE_RECORDED` | prosecution / submission confirmed waiting acceptance / application pending | official stage becomes `ACCEPTED`; other statuses stay unchanged |
| `PRELIMINARY_EXAMINATION_STARTED` | prosecution / accepted / application pending | official stage becomes `PRELIMINARY_EXAMINATION`; other statuses stay unchanged |
| `PRELIMINARY_EXAMINATION_PASSED` | prosecution / preliminary examination / application pending | projection remains exactly unchanged |
| `RECTIFICATION_NOTICE_RECORDED` | prosecution / preliminary examination / application pending | business becomes `OA_REPLY_IN_PROGRESS`; official becomes `RECTIFICATION_RESPONSE`; legal remains application pending |
| `PUBLICATION_NOTICE_RECORDED` | prosecution / preliminary examination / application pending | official becomes `PUBLISHED`; business remains prosecution; legal remains application pending |
| `SUBSTANTIVE_EXAMINATION_STARTED` | prosecution / published / application pending | official becomes `SUBSTANTIVE_EXAMINATION`; other statuses stay unchanged |
| `OA_NOTICE_RECORDED` | prosecution / substantive examination / application pending | business becomes `OA_REPLY_IN_PROGRESS`; official becomes `OFFICE_ACTION_RESPONSE`; legal remains application pending; exact `oa_sequence` is returned |

Every accepted prior projection is `CONFIRMED`, and every result preserves `CONFIRMED`.
All decisions except `OA_NOTICE_RECORDED` return `oa_sequence=None`.

## Exact notice, deadline and evidence boundaries

- Each registry entry accepts only its exact uppercase event key, lifecycle lane, confirmed
  command, exact predecessor projection, bounded identities and naive timestamps.
- Acceptance requires exactly one `ACCEPTANCE_NOTICE` evidence version.
- Preliminary start and pass require exactly one
  `PRELIMINARY_EXAMINATION_SOURCE` or
  `PRELIMINARY_EXAMINATION_PASS_NOTICE` evidence version respectively.
- Rectification requires exactly one `RECTIFICATION_NOTICE` evidence version plus the
  exact confirmed official-due-date payload. Publication and substantive start require
  exactly one `PUBLICATION_NOTICE` or `SUBSTANTIVE_EXAMINATION_SOURCE` evidence version
  and an empty payload.
- OA notice requires exactly one `OA_NOTICE` evidence version and exactly:
  `official_due_date`, `official_due_date_source`,
  `official_due_date_status=CONFIRMED`, positive integer `oa_sequence`, and bounded
  nonblank `source_template_code`.
- Official due dates must be canonical ISO dates. The only accepted source values are
  `MANUAL_OFFICIAL_NOTICE` and `IMPORTED_OFFICIAL_NOTICE`.
- Evidence is exact `DocumentEvidenceVersion` lineage for the transitioning case, with a
  nonblank identity and each task's exact trim/length boundary, lowercase
  `sha256:[0-9a-f]{64}` hash and naive capture time. Missing, extra, malformed, cross-case
  or non-exact evidence/payload returns no decision.
- All seven rules are pure and transaction-independent. They do not query, write, flush,
  commit, roll back, resolve documents or create deadlines.

## Exact paths

- `backend/app/modules/cases/lifecycle_rules.py`
- `backend/tests/test_v8_lifecycle_acceptance_notice.py`
- `backend/tests/test_v8_lifecycle_preliminary_started.py`
- `backend/tests/test_v8_lifecycle_preliminary_passed.py`
- `backend/tests/test_v8_lifecycle_rectification_notice.py`
- `backend/tests/test_v8_lifecycle_publication_notice.py`
- `backend/tests/test_v8_lifecycle_substantive_started.py`
- `backend/tests/test_v8_lifecycle_oa_notice.py`

The seven decisive tests are byte-identical to the archive anchor. The shared rule file
adopts only the seven named rule/validator blocks, the required `date` import and their
registry entries. The independently approved filing nonblank evidence guard remains
unchanged.

## Verification

After the controller grants the serialized SQLite/shared verification lane, run the seven
decisive files together with the current-reviewed filing predecessor and apply-event
regressions. Result: `577 passed`, with only the inherited third-party `passlib`
deprecation warning. Scoped Ruff check and exact diff-check pass.

Ruff format-check reports that the seven decisive tests are formatted but would reformat
the shared rule file, including broad byte-only layout changes to the already reviewed
filing predecessor. The archive full rule file produces the same diagnostic under the
current formatter. That adjacent reformat is intentionally not applied: exact accepted
rule/test adoption and the no-adjacent-cleanup boundary take precedence over a formatter
version migration that this story does not own.

An independent High reviewer must review the exact two-tree candidate comparison against
the current filing story commit, rerun the decisive tranche, verify the exact Git
path/mode/blob fingerprint and confirm that no archived later-rule hunk entered the
candidate.

## Non-goals and rollback

No filing-story rewrite, rectification-response completion event, OA receipt, reexamination,
grant, rejection or later lifecycle rule; no adapter/resolver, API/UI, persistence,
activity, document creation, fee, payment, permission, schema/migration, historical
evidence mutation, ledger edit or milestone claim. Rollback reverts the seven decisive
tests, seven rule/validator blocks, `date` import, registry entries and story card as one
exact candidate while retaining the independently approved filing story.
