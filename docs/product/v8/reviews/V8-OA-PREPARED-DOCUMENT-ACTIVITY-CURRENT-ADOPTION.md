# Independent Review — V8 OA Prepared Document Activity Current Adoption

- Review class: `PROTECTED`
- Product commit: `430023242ec4dcbff7ecc72072c71c4f2dd7bb20`
- Correction commit: `20b49c05ff8744dc466c40ce9ab66778a9a03e1d`
- Exact reviewed range:
  `1f7f6a188aa6e3d5c347e3f1e019de2f455400c9..20b49c05ff8744dc466c40ce9ab66778a9a03e1d`
- Reviewer: independent GPT-5.6 High review lane
- Verdict: `APPROVED`
- P0: 0
- P1: 0
- P2: 0

The initial independent review rejected the product commit because its prepared-derivation
query filtered by the requested case before evaluating exact parent/child/type cardinality.
That could hide a wrong-case carrier and append a confirmed activity instead of failing
closed. The correction loads the complete exact carrier set, requires cardinality one, and
only then validates the sole carrier's case identity.

The new regression injects a second wrong-case derivation with the exact returned source
and reply evidence identities. It receives typed `OA_REPLY_IDENTITY_CONFLICT` / HTTP 409,
proves rollback of the reply document, package link, preparation derivations and stored
output, preserves the OA task as OPEN, and confirms that no `OA_REPLY_PREPARED` activity
survives. The independent correction rerun passed this exact test: `1 passed, 2 warnings in
1.21s`.

Earlier in this same exact review, the focused Row 68 file passed `3 passed, 2 warnings`
and the decisive accepted Row 67 plus lifecycle-append tranche passed `63 passed, 2
warnings`. Those unchanged tests were not repeated after the surgical correction. All
warnings are inherited passlib and Pydantic deprecations. The SQLite lane was released
immediately after each final test command.

The combined product range appends one confirmed `OA_REPLY_PREPARED` DOCUMENT activity with
the exact package and prepared reply evidence, identical projections and
`center_changes={}`. Replay preserves a later lifecycle projection and does not duplicate
the activity or evidence links. The OA task and legacy status remain unchanged. No Row 69
external submission, task close, lifecycle transition, API/UI, schema/migration/seed,
source/customer decision, ledger or adjacent behavior entered the range.

Fresh scoped Ruff and Ruff format checks pass on both product paths. Correction-only and
full-range `git diff --check` pass, and the exact product paths have no drift from the
correction commit. The exact two-path Git tree fingerprint is
`983453b8014c56dc33fa08c6d60437a4b8d7398db3fd236289975c8a9279a868`.
The full binary patch SHA-256 is
`b6ced49e9e5b35fe3ffde5496793d4a5b17ec2ccf63ff6ea5bd75c27a4ad9ca9`;
the correction-only patch SHA-256 is
`9227dd9b3d6fb31ac143745b3f2f6024f764c4eff1e2e4d788c16148af965ace`;
the reviewed story SHA-256 is
`3f665dddad1bef8b68136e2a6e732c21a59c70cfae76fac525abbbafe977c0eb`.
