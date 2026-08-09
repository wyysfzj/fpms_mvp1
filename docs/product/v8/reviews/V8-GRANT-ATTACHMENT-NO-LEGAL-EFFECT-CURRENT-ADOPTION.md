# Independent Review — Grant Attachment No Legal Effect Current Adoption

- Review class: `PROTECTED`
- Reviewer: independent High reviewer `/root/row155_independent_review`
- Integration parent: `0a9b8b92e65c883995f0f54144023fad3ebc14b5`
- Product/test commit: `541d25397bd285985b14b4b5c6a09feca15e5cbd`
- Review test correction: `0b54fe9fc884fe22fc0e5deb5aeea2be923149b6`
- Adoption-story commit: `1833ecf37cf23f06cde05261979e121aa73ff776`
- Frozen task:
  `tasks/postdemo/v8/FPMS-V8-GRANT-ATTACHMENT-NO-GRANTED-20260712-01.md`
- Story:
  `docs/product/v8/stories/V8-GRANT-ATTACHMENT-NO-LEGAL-EFFECT-CURRENT-ADOPTION.md`
- Integration binding: `UNBOUND` (the controller alone owns coverage-ledger binding and
  ordinal-75 activation)
- Verdict: `APPROVED`
- P0: 0
- P1: 0
- P2: 0

## Independent contract and implementation review

The exact two-path product closure removes only the grant-notice attachment shortcut that
validated grant-ready fields and directly wrote legacy `Case.status = GRANTED`. The
private `_advance_grant_notice_case_after_attachment` symbol remains present and continues
to delegate to `ensure_grant_fee_task_for_notice_document()`. The attachment and initial
evidence version remain persisted in the caller-owned transaction, and the grant-fee task
retains its source-document and confirmed due-date lineage.

The corrected focused test proves the precise authority boundary. Attachment upload leaves
legacy status and the three central lifecycle axes unchanged. The current-verified
`register_evidence_version` deep seam still owns exactly one sequence-1
`DOCUMENT_EVIDENCE_VERSION_REGISTERED` activity in the DOCUMENT lane, with identical old
and new central projections, so lifecycle revision advances exactly from 0 to 1. Row75
does not delete or suppress that evidence-lineage activity. Task, attachment and evidence
linkage assertions remain intact.

The initial independent review raised one P1 because the first focused test asserted only
legacy status and persistence, leaving the central projection and activity boundary
unproved. Test-only correction `0b54fe9` closes that finding by asserting the complete
refined boundary above. No product byte changed after `541d253`. The Row75 product commit
does not change the current-verified Row74 dispatcher, API, schema or focused tests; the
fresh combined tranche confirms their preserved behavior and helper-source compatibility.

## Fresh independent verification

From `backend/`, the exact serialized command was:

```text
/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/.venv/bin/pytest -q \
  tests/test_v8_grant_attachment_no_legal_effect.py \
  tests/test_v8_grant_notice_lifecycle_api.py \
  tests/test_v8_grant_notice_lifecycle_adapter.py
```

Result: `74 passed, 3 warnings in 23.17s`, exit `0`. The warnings are inherited passlib
`crypt` and Pydantic `strip_whitespace` deprecations. The SQLite lane was released
immediately afterward.

Scoped Ruff check on the exact two Python paths returned `All checks passed!`, exit `0`.
Exact two-path cumulative `git diff --check` returned exit `0`. `ruff format --check`
reported the corrected test already formatted and only one pre-existing formatting delta
in `documents/service.py`: the unchanged two-literal Row61 impact-preview message at lines
1093-1094, blamed to `ae26fc6`, outside every Row75 hunk. It is not absorbed by this
receipt. The worktree was clean before receipt creation.

## Exact identities

- cumulative two-path binary patch SHA-256 for `0a9b8b9..0b54fe9`:
  `695d01b921416227ef4e2eebd8479ae0e0635320ffa0e545493a44280ef604e0`;
- test-correction two-path binary patch SHA-256 for `541d253..0b54fe9`:
  `09073fd77a5e1bc747fd17e5020b6076e36ec4b534757cc0537f12f9cecc799e`;
- exact two-path Git-tree fingerprint at `0b54fe9`:
  `942362f9954afe7829cf2dfee3f395aa096f95cfdeb2eb91bf66ba562e991588`;
- adoption-story SHA-256 at `1833ecf`:
  `a1ef9b7de1b884b990822d053c664da604224209490ce256c63cad6125b6f9b9`;
- adoption-story Git blob:
  `bb5176ecbd0ebc288235ee28530fd869f37f7b93`.

This receipt approves only the exact removal of the attachment-to-`GRANTED` shortcut and
its corrected focused proof. It does not bind the coverage ledger, activate ordinal 75,
change the evidence-registration activity, dispatch the Row74 lifecycle event, approve or
promote evidence, change fee/deadline behavior, absorb Row76 or another catalog row, fix
the inherited format baseline, or claim a Foundation, release or production milestone.
