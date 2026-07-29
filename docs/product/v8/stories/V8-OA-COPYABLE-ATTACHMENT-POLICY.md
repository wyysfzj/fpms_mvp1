# Story V8-OA-COPYABLE-ATTACHMENT-POLICY

- Risk: `PROTECTED`
- Catalog ID: `FPMS-V8-OA-COPYABLE-ATTACHMENT-POLICY-20260712-01`
  (frozen catalog row 72, profile `TC-RULE`, Foundation phase).
- Outcome: require the exact copyable OA attachment combination from typed, promoted
  evidence-version results and package-manifest authority.
- Change mode: minimum row-72 product correction, focused contract test and this story
  record.
- Authority: `docs/product/v8/domain-contract.md`,
  `docs/product/v8/source-decision-registry.md`, and the exact frozen row-72 task.
- Base: `d5d6a6f605a0f96a34c35baebb1b72ad44006ae0`.

## Dependency chain

The accepted prerequisite chain is:

1. D4-06 evidence-role extension at
   `6b61f681cc0df4ff472388edd577c1633f5a6827`;
2. D4-07 registration matrix at
   `86c6c8e3b05232a31745ebce976be7cd3330950d`;
3. D4-08 OA structured-attachment promotion at
   `87a7205452c813d7be02b4d2b4c70bab37db3c16`;
4. the document-evidence register/derivation core at
   `6672d239e4f0aa7c0575ad5392987ef954140f0f`;
5. this row-72 copyable policy; and
6. parked row 73 noncopyable policy and all later submission/lifecycle consumers.

## Exact closure

`CopyableOaAttachmentEvidence` is a frozen, slotted, keyword-only DTO. It carries one typed
`EvidenceVersionResult` plus the exact manifest identity, case, package, role,
evidence-version link and content hash. The policy accepts only a tuple of exact DTOs for
the named case and package.

Every accepted evidence version must be:

- `OA_STRUCTURED_ATTACHMENT`;
- current;
- independently `APPROVED`;
- in a valid `DRAFT`/non-final or `FINAL`/final state pairing; and
- linked by exact manifest evidence-version ID and exact SHA-256 content hash.

The manifest must contain exactly one `OA_STATEMENT_WORD`, exactly one
`OA_MODIFIED_CLAIMS`, at most one `OA_AMENDMENT_COMPARISON`, and zero or more
`OA_OTHER_PROOF` and `OA_ADDITIONAL_FILE` entries. The policy fails closed on malformed
typed context, duplicate evidence or manifest identities, cross-case or cross-package
input, RAW/non-promoted evidence, stale or unapproved evidence, invalid independent
review, state mismatch, link/hash mismatch, unknown roles and invalid singleton
cardinality. It does not infer from filenames or ORM roles, select among duplicates,
collapse entries or reconstruct links.

Rejected combined commit `d108a8754b1dbb84480df5d67ab37a579f889bef` was used only as
read-only comparison evidence. Only the independently authorized row-72 behavior was
reimplemented; no row-73 bytes were adopted.

## RED → GREEN evidence

The focused row-72 test was corrected in place before product code changed. A transient
file-removal state during patch construction was restored before any test execution and
was not used to manufacture RED.

The observed targeted RED was:

- `34 failed, 1 warning`;
- all failures rooted at the absent `CopyableOaAttachmentEvidence` and pure DTO/manifest
  policy contract; and
- the product path was untouched when this result was observed.

After the minimum product implementation:

- row-72 primary: `34 passed, 1 warning`;
- D4-08 structured-attachment promotion: `40 passed, 1 warning`;
- document-evidence derivation: `20 passed, 1 warning`; and
- filing-XML shared-file regression: `22 passed, 1 warning`.

Each warning is the existing passlib `crypt` deprecation. Scoped Ruff check-only returned
`All checks passed!`; its only output besides that result was the repository's existing
top-level-settings deprecation notice. `git diff --check` returned clean.

## Exact paths

### Product

- `backend/app/modules/documents/evidence_policy.py`

### Primary test

- `backend/tests/test_v8_oa_copyable_attachment_policy.py`

### Story

- `docs/product/v8/stories/V8-OA-COPYABLE-ATTACHMENT-POLICY.md`

### Focused regressions

- `backend/tests/test_v8_oa_structured_attachment_promotion.py`
- `backend/tests/test_v8_document_evidence_derivation.py`
- `backend/tests/test_v8_filing_xml_derivation_gate.py`

The controller granted and then released the single SQLite/shared verification lane. An
independent High reviewer must review the exact one-commit range and independently rerun
the decisive checks. The implementer does not approve this `PROTECTED` story.

## Parked work and rollback

The existing row-63/64 filing-XML policy remains unchanged. Row 73/noncopyable attachment
policy, external submission, lifecycle transitions, APIs, routers, models, schemas,
migrations, seeds and UI remain explicitly parked. No task file, ledger, disposition,
review receipt, old evidence or old taskctl artifact changed.

Rollback reverts only the one story commit containing the row-72 policy, its focused test
and this story card.
