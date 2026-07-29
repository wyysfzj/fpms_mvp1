# Story V8-OA-NONCOPYABLE-APPENDIX-POLICY

- Risk: `PROTECTED`
- Catalog ID: `FPMS-V8-OA-NONCOPYABLE-APPENDIX-POLICY-20260712-01`
  (frozen catalog row 73, profile `TC-RULE`, Foundation phase).
- Outcome: preserve the exact full-reply-PDF to extracted-appendix derivation and permit
  only that appendix as `OA_OTHER_PROOF`.
- Change mode: minimum row-73 product implementation followed by the minimum independent
  P1 carrier-consistency correction, focused contract test and this story record.
- Authority: `docs/product/v8/domain-contract.md`,
  `docs/product/v8/source-decision-registry.md`, the exact frozen row-73 task, and the
  accepted Delta-4 document/evidence chain.
- Base: `e1957b3d77e4f54f20a695823b857bc25790ba82`.

## Dependency and ownership chain

The accepted prerequisite chain is:

1. D4-06 evidence-role extension at
   `6b61f681cc0df4ff472388edd577c1633f5a6827`;
2. D4-07 registration matrix at
   `86c6c8e3b05232a31745ebce976be7cd3330950d`;
3. D4-08 OA structured-attachment promotion at
   `87a7205452c813d7be02b4d2b4c70bab37db3c16`;
4. document-evidence register/derivation core at
   `6672d239e4f0aa7c0575ad5392987ef954140f0f`;
5. row-72 copyable policy implementation at
   `8341a7a4146494af6038f72bc26d6e2efd028038`, independently accepted and mapped by
   `e1957b3d77e4f54f20a695823b857bc25790ba82`; and
6. this row-73 noncopyable appendix policy.

The accepted row-72 policy remains immutable. This story neither edits nor bypasses its
typed manifest policy; it closes only the separate noncopyable appendix lineage gate.

## Exact closure

`require_noncopyable_oa_appendix_derivation()` is a read-only, keyword-only pure policy.
It accepts only the exact same-case carrier graph:

- one `OA_REPLY` package;
- one `GENERATED_ATTACHMENT` full-reply evidence version linked to an
  `application/pdf` attachment and present `OA_STATEMENT_PDF` manifest; this parent is a
  positive-numbered current `DRAFT` and has no `final_submitted_at`;
- one distinct `OA_STRUCTURED_ATTACHMENT` appendix evidence version linked to a distinct
  attachment and present `OA_OTHER_PROOF` manifest; this child is positive-numbered,
  current and may be `DRAFT` or `FINAL`;
- exact `OA_STATEMENT_APPENDIX` source-role aliases on the appendix attachment and
  manifest; and
- one exact `COMPONENT_EXTRACTION` parent-to-child derivation with canonical source
  snapshot
  `{"component":"OA_STATEMENT_APPENDIX","schema":"FPMS_OA_NONCOPYABLE_APPENDIX_V1"}`.

Package, document, attachment, evidence-version and manifest links must match exactly.
Each attachment/manifest hash must equal its named evidence version's exact lower-case
SHA-256 carrier. Parent and child evidence, attachment and document identities must be
distinct. The selected `other_proof_evidence_version_id` must equal the extracted appendix
and must not name the full reply.

Each evidence version must also carry a known, internally coherent review tuple:

- `PENDING` has no reviewer or review time;
- `APPROVED` and `REJECTED` have a non-self reviewer and naive review time.

This lineage policy does not require `APPROVED`. D4-08 deliberately produces a `PENDING`
structured child, while the accepted row-72 policy and later reply preparation own the
independent-approval consumption gate.

Malformed carrier shape, cross-case input, wrong full-reply identity, wrong appendix
identity, package/link/hash/derivation mismatch and selecting anything except the exact
appendix fail closed with stable error codes. The policy does not mutate inputs, infer
from filenames, search for a likely file, collapse identities or reconstruct lineage.

Rejected combined commit `d108a8754b1dbb84480df5d67ab37a579f889bef` was used only as
read-only comparison evidence. Only the independently authorized row-73 behavior was
reimplemented. Its row-72 differences and all unrelated bytes were excluded.

## Initial RED → GREEN evidence

The row-73 focused test was added before product code changed. With the product path still
identical to the accepted base, the controller-granted targeted RED returned:

- `105 failed, 1 warning`;
- the failures consistently rooted at the absent
  `require_noncopyable_oa_appendix_derivation` and
  `NoncopyableOaAppendixPolicyError` public contract.

After the minimum product implementation, the controller-granted serial GREEN/regression
tranche returned:

- row-73 primary: `105 passed, 1 warning`;
- accepted row-72 policy: `34 passed, 1 warning`;
- document-evidence derivation: `20 passed, 1 warning`; and
- D4-08 structured-attachment promotion: `40 passed, 1 warning`.

Each warning is the existing passlib `crypt` deprecation. The controller released the
SQLite/shared lane after each tranche. Scoped Ruff check-only returned
`All checks passed!`; its only other output was the repository's existing top-level
settings deprecation notice.

Commit `d66ab96cee2878215d3a9ac81d7390b75ab6e5b1` preserved this initial evidence but was
rejected by independent High review at P1 because the policy still accepted invalid stored
version carriers. It remains durable rejected history, not an acceptance point.

## Independent P1 correction

The reviewer verified that `d66ab96` omitted version ordinal, current identity,
role/state-matrix, review-tuple and parent final-submission validation. The correction
first changed only the focused test:

- the valid fixture now uses exact current identities;
- the generated parent is `DRAFT`;
- the appendix explicitly proves both permitted `DRAFT` and `FINAL` states;
- coherent `PENDING`, `APPROVED` and `REJECTED` review tuples remain positive; and
- malformed scalar shape, nonpositive ordinals, stale identities, wrong states,
  incoherent/unknown/self-review tuples and a submitted generated parent are negative on
  the existing exact error surfaces.

With product still at rejected `d66ab96`, the controller-granted correction RED returned
`41 failed, 110 passed, 1 warning`. The 41 failures were exactly the missing validations;
the corrected positive cases passed.

After the minimum product correction, the controller-granted serial tranche returned:

- corrected row-73 primary: `151 passed, 1 warning`;
- accepted row-72 policy: `34 passed, 1 warning`;
- document-evidence derivation: `20 passed, 1 warning`; and
- D4-08 structured-attachment promotion: `40 passed, 1 warning`.

The warning remains the existing passlib `crypt` deprecation. Approval was not introduced
as a row-73 requirement, no row-72 line changed, and the controller released the shared
SQLite lane after the final result.

## Exact paths

### Product

- `backend/app/modules/documents/evidence_policy.py`

### Primary test

- `backend/tests/test_v8_oa_noncopyable_appendix_policy.py`

### Story

- `docs/product/v8/stories/V8-OA-NONCOPYABLE-APPENDIX-POLICY.md`

### Focused regressions

- `backend/tests/test_v8_oa_copyable_attachment_policy.py`
- `backend/tests/test_v8_document_evidence_derivation.py`
- `backend/tests/test_v8_oa_structured_attachment_promotion.py`

An independent High reviewer must review the exact correction commit and effective
two-commit story range and independently rerun the decisive checks. The implementer does
not approve this `PROTECTED` story.

## Parked work and rollback

OA reply preparation, external submission, lifecycle transitions, APIs, routers, models,
schemas, migrations, seeds, UI, filename inference and row 74 remain explicitly parked.
No task file, coverage ledger, disposition, review receipt, old evidence or old taskctl
artifact changed.

The correction commit repairs but does not rewrite rejected `d66ab96`. Rolling back the
correction returns to rejected P1 behavior; removing the effective story omits both row-73
commits. No other row is part of either rollback boundary.
