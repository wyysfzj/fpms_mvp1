# Story V8-D4-07-REGISTRATION-MATRIX-CURRENT-VERIFICATION

- Risk: `PROTECTED`
- Outcome: prove on the current lean tree that external frozen prerequisite
  `FPMS-V8-DE-DELTA4-REGISTRATION-MATRIX-CORRECTION-20260715-01` (`D4-07`) preserves its
  exact fail-closed evidence registration matrix after current D4-06 and the RAW guard.
- Change mode: current verification only; no service, test, contract, catalog, ledger,
  disposition or review byte changes.
- Authority: the document/evidence lineage rules in
  `docs/product/v8/domain-contract.md`; the source-precedence rules in
  `docs/product/v8/source-decision-registry.md`; and the frozen D4-07 task contract.
- Reachability role: this is an external frozen prerequisite, not a frozen catalog row.
  Its independently reviewed commit becomes the current reachable prerequisite for
  D4-08 `FPMS-V8-DE-OA-STRUCTURED-ATTACHMENT-PROMOTION-20260715-01`.

## Dependencies

- D4-06 evidence-role extension and the inherited RAW-registration guard are bound on the
  current tree by `V8-DOCUMENT-EVIDENCE-CONTRACTS-CURRENT-VERIFICATION` at
  `6b61f681cc0df4ff472388edd577c1633f5a6827`.
- The accepted public `register_evidence_version()` service is bound by
  `V8-DOCUMENT-EVIDENCE-CORE-CURRENT-VERIFICATION` at
  `6672d239e4f0aa7c0575ad5392987ef954140f0f`.
- Ordering remains strict: current D4-06/RAW guard → this D4-07 story → D4-08.

## Exact matrix

The service must retain an explicit positive role/state matrix:

- each original formal role is allowed for `DRAFT` and `FINAL`;
- `RAW_ATTACHMENT` is allowed only for `DRAFT`;
- `GENERATED_ATTACHMENT` is allowed only for `DRAFT`;
- `OA_STRUCTURED_ATTACHMENT` is allowed for `DRAFT` and `FINAL`; and
- every unknown or future role is denied for both states before transaction or activity
  access.

`GENERATED_ATTACHMENT` / `FINAL` retains the exact
`400 EVIDENCE_VERSION_INVALID` state-field error. Unknown or future roles retain the
exact `400 EVIDENCE_VERSION_INVALID` role-field error. No enum-derived allowlist,
catch-all or automatic future-role authority is permitted.

## Archive comparison

- Archive comparison anchor:
  `6b2ef89da447353380b99853168d4d38aaf9210a`.
- The registration-policy and public registration seam in
  `backend/app/modules/documents/evidence_service.py` is byte-identical to the archive.
  The full current service blob `cf221a7ed258a3fd42b97dfb27630beee304c015`
  intentionally differs from archive blob `eada96e29cd6e4931a452cde35633d46424446be`
  only in later serialized review behavior outside this closure; no wholesale archive
  adoption is authorized.
- All four decisive tests remain byte-identical to the archive:
  - D4-07 matrix: `77b3683742cc2eb885fe1a092fc9d94259e73c4a`
  - RAW guard: `56b041b9563014843dc703de1eb120818f806ce9`
  - register-version suite: `f979e16db4937f06d3675408de522c7849f6ff1e`
  - external-submission allowlist:
    `7f58d071d2cd6d197c84d489d3bbf41a931c83f5`

## Exact paths and verification

### Product and primary test

- `backend/app/modules/documents/evidence_service.py`
- `backend/tests/test_v8_delta4_registration_matrix.py`

### Exact inherited regressions

- `backend/tests/test_v8_raw_attachment_registration_guard.py`
- `backend/tests/test_v8_document_evidence_register_version.py`
- `backend/tests/test_v8_external_submission_role_allowlist.py`

Run the four tests once, in the listed order, under the granted serialized SQLite lane
from this worktree's `backend` directory:

```text
/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/.venv/bin/pytest -q tests/test_v8_delta4_registration_matrix.py tests/test_v8_raw_attachment_registration_guard.py tests/test_v8_document_evidence_register_version.py tests/test_v8_external_submission_role_allowlist.py
```

Observed current-tree result: `62 passed, 1 warning`; the warning is the existing passlib
`crypt` deprecation.

Run scoped Ruff check-only on the exact product and primary-test paths, followed by exact
diff-check and commit-range inspection. An independent High reviewer must review the
exact commit and independently rerun the decisive checks; the implementer does not
approve this `PROTECTED` story.

## Non-goals and rollback

No evidence-role enum change, RAW-to-OA promotion, D4-08 behavior, generated-attachment
adapter, derivation, manifest link, external-submission allowlist expansion, review
behavior adoption, lifecycle/legal change, API/router/schema/model/migration/seed/UI
change, catalog-row mapping, coverage-ledger/disposition/review mutation, old
taskctl/evidence mutation or Foundation claim. Rollback reverts only this story-card
commit; the already-integrated product and test bytes remain unchanged.
