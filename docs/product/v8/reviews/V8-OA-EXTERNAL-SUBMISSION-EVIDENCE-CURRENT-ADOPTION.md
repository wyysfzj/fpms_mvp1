# Independent Review — V8 OA External Submission Evidence Current Adoption

- Review class: `PROTECTED`
- Reviewer: independent High reviewer `/root/row69_independent_review`
- Product commit: `545079d279b5296ec9cc101d1dc05b31ac2e7d3f`
- Parent: `e8686177be694f74d0cfc06310a496977fb43f2d`
- Story: `docs/product/v8/stories/V8-OA-EXTERNAL-SUBMISSION-EVIDENCE-CURRENT-ADOPTION.md`
- Verdict: `APPROVED`
- P0: 0
- P1: 0
- P2: 0

The independent review verified the exact Row 69 closure. The adapter accepts only one
exact `OA_REPLY` package with a coherent same-case source/reply chain and resolve key, one
unique present `OFFICIAL_SUBMISSION_LIST` manifest, and the exact linked evidence version
and attachment. The evidence must belong to the reply document, remain current, `FINAL`
and independently `APPROVED`, and carry the same exact lowercase SHA-256 identity through
the evidence, attachment and manifest. Missing, ambiguous, stale, cross-case, self-reviewed
or hash-inconsistent carriers fail closed before external finalization.

The adapter delegates to the unchanged, independently accepted
`finalize_external_submission()` seam with the exact persisted case/evidence identities and
the namespaced `oa-external:{package_id}:{idempotency_key}` key. The deep seam's current
positive role allowlist includes `OFFICIAL_SUBMISSION_LIST`; its final/current/review
guards, caller-owned transaction and projection-neutral `DOCUMENT` activity remain
unchanged. The adapter validates the returned deep identity, writes or reuses one exact
`SUBMISSION_CONFIRMED` checklist item, rejects upstream key, actor, time, carrier and hash
drift, and replays without an additional activity or checklist write. It performs no
commit, rollback or close. The OA task stays open; package, source/reply document, legacy
case status and central lifecycle projection remain unchanged, and no receipt or lifecycle
lane event is created.

Fresh independent verification from the serialized SQLite lane:

- `cd backend && pytest -q tests/test_v8_oa_external_submission_evidence.py` — `44 passed`,
  exit `0`, with only the two documented inherited passlib and Pydantic deprecation
  warnings. The lane was released immediately after this command.
- An earlier invocation from the repository root was harness-invalid because Alembic's
  relative script location requires the `backend` working directory. All 44 cases stopped
  at fixture setup, no Row 69 behavior executed, and that attempt is not product evidence.
- Scoped Ruff check-only on the exact product and focused-test paths passed; the exact
  commit diff check passed; the commit contains only the two frozen allowlist paths.
- The implementer's durable affected tranche remains `98 passed, 2 warnings`; it was not
  repeated during this review, as required by the controller's bounded verification
  contract.

## Shared-path successor attestation

The parent-to-product diff adds only the Row 69 imports, constants, frozen DTOs, helpers
and entrypoint plus the new focused test. It edits no pre-existing shared-service
definition. The current integration tip's Row 69 product/test paths are byte-identical to
`545079d`, so the accepted behavior of all requested shared-path stories remains intact:

- `V8-ACTIVITY-ADAPTERS-CURRENT-ADOPTION`;
- `V8-DOCUMENT-ATTACHMENT-EVIDENCE-REVIEW-VERTICAL-CURRENT-ADOPTION`;
- `V8-OA-RECEIPT-LIFECYCLE-ADAPTER-CURRENT-ADOPTION`;
- `V8-OA-REPLY-DATE-RECEIPT-PROJECTION-CURRENT-ADOPTION`;
- `V8-WORK-PACKAGE-MANIFEST-EVIDENCE-VERSION-CURRENT-ADOPTION`;
- `V8-FILING-PREPARATION-STARTED-ADAPTER-CURRENT-ADOPTION`;
- `V8-FILING-FULL-WORD-READINESS-GATE-CURRENT-ADOPTION`;
- `V8-FILING-EXTERNAL-SUBMISSION-ADAPTER-CURRENT-ADOPTION`;
- `V8-APPLICATION-FEE-NOTICE-ACTIVATION-CURRENT-ADOPTION`;
- `V8-FILING-RECEIPT-LIFECYCLE-ADAPTER-CURRENT-ADOPTION`;
- Row 67 `V8-OA-OUT-PACKAGE-ATOMIC-LINK-CURRENT-ADOPTION`; and
- Row 68 `V8-OA-PREPARED-DOCUMENT-ACTIVITY-CURRENT-ADOPTION`.

The exact focused-test SHA-256 is
`031dfc9c62ad0631e85e4fbecd86b59d382b4b1ffa97499ab87ed27124fb9d17`, matching the
declared archive-restored test. The exact two-path Git tree fingerprint is
`3fabdac4c0ac7ede26c1af46b2025492e335854cb88e0f2b2def77f970b8d1f2`. The complete binary
product patch SHA-256 is
`f5182fcb863597c12d4766e1b20f81ae755bbc6e43534b987b64846dca7500f0`, and the reviewed
story SHA-256 is
`3b1bc26ab5a78447be95417f56b3affcf5912e969d1c62b740d811ff8bdcf946`.
