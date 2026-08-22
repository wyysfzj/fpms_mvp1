# Story V8-DOCUMENT-EVIDENCE-CONTRACTS-CURRENT-VERIFICATION

- Risk: `PROTECTED`
- Outcome: prove on the current lean tree that the original ordinal-42 enums and dataclass
  shapes remain preserved, `EvidenceRole` is current-verified through its approved additive
  successor contracts as the exact ordered twelve-role interface, and
  `EvidenceDerivationType` remains the original exact seven values with no
  `OA_REPLY_PREPARATION`.
- Change mode: current verification only; no product, test, ledger, disposition or review
  byte changes.
- Authority: the document/evidence lineage rules in `docs/product/v8/domain-contract.md`,
  the source-precedence rules in `docs/product/v8/source-decision-registry.md`, and the
  frozen contract in `tasks/postdemo/v8/FPMS-V8-DE-CONTRACTS-20260712-01.md`.
- Dependencies: the D1-D3 carriers are current-verified through
  `V8-CANARY-SCHEMA-SPINE-CURRENT-VERIFICATION`.

## Catalog ID

- `FPMS-V8-DE-CONTRACTS-20260712-01` (ordinal 42)

## Additive successor authority

These are approved successor contracts, not additional frozen-catalog rows in this story:

- `tasks/postdemo/v8/FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01.md` authorizes
  `RAW_ATTACHMENT` as the exact tenth role only behind the accepted registration and
  external-submission guards.
- `tasks/postdemo/v8/FPMS-V8-DE-DELTA4-EVIDENCE-ROLE-EXTENSION-20260715-01.md` authorizes
  `GENERATED_ATTACHMENT` and `OA_STRUCTURED_ATTACHMENT` as the exact ordered suffix,
  producing exactly twelve unique roles while preserving the inherited original-nine
  external-submission positive allowlist.

The complete current role order is:

```text
FILING_FULL_WORD
TRACKED_REVISED_WORD
FILING_COMPONENT
EXTERNAL_XML_PACKAGE
OFFICIAL_SUBMISSION_LIST
OFFICIAL_FINAL_PDF
SUBMITTED_XML
OFFICIAL_RECEIPT
CLIENT_LETTER_WORD
RAW_ATTACHMENT
GENERATED_ATTACHMENT
OA_STRUCTURED_ATTACHMENT
```

## Exact verification paths

### Product

- `backend/app/modules/documents/evidence_contracts.py`
- `backend/app/modules/documents/evidence_service.py`
- `backend/app/modules/documents/evidence_workflow_service.py`

### Tests

- `backend/tests/test_v8_document_evidence_contracts.py`
- `backend/tests/test_v8_delta4_evidence_role_extension.py`
- `backend/tests/test_v8_raw_attachment_registration_guard.py`
- `backend/tests/test_v8_external_submission_role_allowlist.py`

## Verification

From this worktree's `backend` directory, run the two pure contract tests:

```text
/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/.venv/bin/pytest -q tests/test_v8_document_evidence_contracts.py tests/test_v8_delta4_evidence_role_extension.py
```

After controller grant, run the full four-test tranche in one serialized invocation with
maximum writers `1`:

```text
/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/.venv/bin/pytest -q tests/test_v8_document_evidence_contracts.py tests/test_v8_delta4_evidence_role_extension.py tests/test_v8_raw_attachment_registration_guard.py tests/test_v8_external_submission_role_allowlist.py
```

Run scoped Ruff on all seven exact paths and exact diff-check. Prove the role tests enforce
the twelve-role sequence and inherited positive allowlist, while current source and test
contain the same seven ordered `EvidenceDerivationType` values and contain no
`OA_REPLY_PREPARATION`. The independent High reviewer reruns the same decisive checks on
the exact story correction range.

## Later-hunk exclusion and supersession boundary

Archive commit `6b2ef89` adds exactly one `OA_REPLY_PREPARATION` line to the production enum
and one matching line to the expected test vocabulary. Those two lines belong to the later
OA-reply lane, whose catalog story
`FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01` is not current-verified, so they are
deliberately excluded from this ordinal-42 verification.

A future independently reviewed current-verification story for that later lane may
supersede only the derivation vocabulary through its own explicit authority, matching
product/test change, coverage mapping and exact commit/range. It must preserve or explicitly
supersede the separately authorized twelve-role interface and its guard boundaries. Until
then, the current contract remains twelve evidence roles and exactly seven derivation
values.

## Non-goals and rollback

No new role, role reorder, positive-allowlist expansion, registration-policy change,
persistence, business adapter, endpoint, UI, OA-reply implementation, later-task derivation
adoption, schema/migration, old taskctl/evidence mutation or Foundation claim. Rollback
removes only this story record, its correction and its later coverage-ledger mapping;
current product/test bytes and the independently approved successor contracts remain
unchanged.
