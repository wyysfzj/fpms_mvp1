# Independent Review — V8 Filing Lifecycle Vertical Current Verification

- Review class: `PROTECTED`
- Reviewed range:
  `ed86cadc74e48a1fab4d156360dbacb1bdc9780e..6834710cae300aa2b748268a909f11a8239b9977`
- Reviewer: independent GPT-5.6 High review lane
- Verdict: `APPROVED`
- P0: 0
- P1: 0
- P2: 0

The exact range binds catalog rows 19–21 to the filing lifecycle sequence. Preparation
changes only the business stage; external submission moves the business and official
procedure stages but does not establish legal status; only the archived valid filing
receipt moves the case to prosecution management and establishes `APPLICATION_PENDING`.
All three rules preserve `CONFIRMED` and return `oa_sequence=None`.

The first independent review found that the external-submission rule accepted a blank
evidence `object_id`. The implementer added four exact blank/whitespace RED cases, observed
all four returning an invalid transition, and applied only a nonblank identity guard. The
same four cases then passed. The final reviewer confirmed that the correction is
fail-closed, preserves distinct identity and transaction purity, and changes no adjacent
lifecycle event.

Fresh independent verification:

- serialized seven-file lifecycle tranche: 204 passed in 49.73 seconds, with only the
  inherited third-party `passlib` deprecation warning;
- scoped Ruff check and Ruff format-check: passed;
- exact-range diff-check: passed;
- exact four product/test path Git fingerprint:
  `2366cee203485357e11fbe505b9483d3722ed3a15740f6f75a108356c0a6b049`;
- patch SHA-256:
  `0459265bfa2862f1c57f66be3833ed32790474205b5f0923006db9f39eb09a29`;
- story SHA-256:
  `77f2c5cf98ad641803375deb069b2e4fc0cde4892360fb21669f9413a289ab4c`.

The preparation and receipt test blobs remain archive-identical. Historical task RED was
not rerun. The exact range contains only the shared lifecycle rule, external-submission
regression and story card; it adds no later event, adapter, API/UI, persistence, fee,
deadline, permission, schema/migration, ledger or release behavior. The final reviewed
worktree was clean, and the corrected rollback boundary matches the product/test change.
