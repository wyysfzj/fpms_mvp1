# Story V8-D4-08-OA-STRUCTURED-ATTACHMENT-PROMOTION

- Risk: `PROTECTED`
- Outcome: implement and current-verify external frozen prerequisite
  `FPMS-V8-DE-OA-STRUCTURED-ATTACHMENT-PROMOTION-20260715-01` (`D4-08`) after current
  D4-06/D4-07.
- Change mode: minimum replay-carrier correction plus focused contract tests; no archive
  wholesale adoption.
- Authority: the document/evidence lineage rules in
  `docs/product/v8/domain-contract.md`; the source-precedence rules in
  `docs/product/v8/source-decision-registry.md`; and the exact frozen D4-08 task.
- Reachability role: this is an external frozen prerequisite, not a frozen catalog row.

## Dependencies

- D4-06 evidence-role extension:
  `V8-DOCUMENT-EVIDENCE-CONTRACTS-CURRENT-VERIFICATION` at
  `6b61f681cc0df4ff472388edd577c1633f5a6827`.
- D4-07 registration matrix:
  `V8-D4-07-REGISTRATION-MATRIX-CURRENT-VERIFICATION` at
  `86c6c8e3b05232a31745ebce976be7cd3330950d`.
- Register-version, register-derivation and caller-owned activity seams:
  `V8-DOCUMENT-EVIDENCE-CORE-CURRENT-VERIFICATION` at
  `6672d239e4f0aa7c0575ad5392987ef954140f0f`.

## Exact closure

`promote_oa_structured_attachment()` preserves the frozen public command/result shape and
promotes exactly one reviewed same-case `OA_REPLY` manifest plus its current
`RAW_ATTACHMENT` / `DRAFT` parent into a same-content exact-lineage
`OA_STRUCTURED_ATTACHMENT` child.

- The five exact manifest roles and `DRAFT|FINAL` targets remain explicit.
- The child remains `PENDING`, with no reviewer, review time or external-submission time.
- Exactly one `OFFICIAL_RECOGNITION` derivation, one canonical
  `OA_STRUCTURED_ATTACHMENT_PROMOTED` activity and two exact evidence references remain in
  the caller-owned transaction.
- Only manifest `evidence_version_id` and `content_hash` may change.
- Exact replay is resolved before the fresh path and must validate the canonical carrier,
  promotion identity, unique named child, derivation, manifest and two references.

The minimum production correction:

1. restores the frozen exactly-one same-lineage child cardinality check on replay;
2. rejects replay when the named `PENDING` child has `final_submitted_at`; and
3. removes the uncontracted requirement that a reusable same-content child must have been
   created by the promotion actor.

No fresh-path, canonical JSON, hash, derivation, activity, reference, manifest-write or
transaction behavior changed.

## Archive reconciliation

- Read-only comparison anchor:
  `6b2ef89da447353380b99853168d4d38aaf9210a`.
- Base service blob:
  `07da3a3578544e93da21f5a5a41d998413f2804f`.
- The contract-reconciled service blob is
  `55fa8a88bf43379792d880a161cec9708cdb1a1e`, which equals the archive blob only because
  the complete source difference was exactly the three frozen replay conditions above.
  The archive was not copied wholesale.
- Base focused-test blob:
  `ebed4d7547889be8debc17a9145b68319f0a9d8f`.
- The corrected focused-test blob is
  `b2e6fee15b4e905e1ef993d48bb8452bce4d26a1`; it intentionally remains different from
  archive blob `e9883840558656ddb6010c56fb96a892e7251e2a` and adds only the reconciled replay
  expectations.

## RED → GREEN evidence

The untouched current primary test first returned `39 passed, 1 warning`; this was not an
acceptable RED because the reduced test omitted the two frozen replay conflicts and
asserted one uncontracted creator restriction.

After only the focused test correction, the serialized primary produced the exact RED:

- `3 failed, 37 passed, 1 warning`;
- duplicate same-lineage child did not return `409`;
- non-null child `final_submitted_at` did not return `409`; and
- exact replay of a valid reusable child created by another actor incorrectly returned
  `409`.

After the minimum production correction, the exact combined serialized GREEN/regression
tranche returned `101 passed, 1 warning`. The warning is the existing passlib `crypt`
deprecation.

## Exact paths and verification

### Product and primary test

- `backend/app/modules/documents/oa_attachment_promotion_service.py`
- `backend/tests/test_v8_oa_structured_attachment_promotion.py`

### Exact required regressions

- `backend/tests/test_v8_delta4_evidence_role_extension.py`
- `backend/tests/test_v8_delta4_registration_matrix.py`
- `backend/tests/test_v8_document_evidence_register_version.py`
- `backend/tests/test_v8_document_evidence_derivation.py`
- `backend/tests/test_v8_external_submission_role_allowlist.py`

The controller-granted combined tranche ran these six files once with one SQLite writer.
Scoped Ruff check-only covers the product and primary-test paths, followed by exact
diff-check and commit-range inspection. An independent High reviewer must review the exact
commit and independently rerun the decisive checks; the implementer does not approve
this `PROTECTED` story.

## Non-goals and rollback

No OA reply preparation, external submission, lifecycle transition, legal-status change,
self-approval, customer decision, API/router/UI, model/schema/migration/seed, new role,
filename inference, bulk/background work, catalog mapping, coverage-ledger/disposition/
review mutation, old taskctl/evidence mutation or Foundation claim. Rollback reverts only
this story, the focused test correction and the three replay conditions in the same
commit.
