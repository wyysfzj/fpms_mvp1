# Independent Review — D4-08 OA Structured Attachment Promotion

- Review class: `PROTECTED`
- Exact commit: `87a7205452c813d7be02b4d2b4c70bab37db3c16`
- Parent: `b9b6d74ecc8eba85d534fd3023295fa37d7ffcd7`
- Verdict: `APPROVED`
- P0: 0
- P1: 0
- P2: 0

The Spec axis confirmed the frozen D4-08 hash and current D4-06, D4-07, registration and
derivation prerequisites. Test reconciliation produced an exact three-case RED: duplicate
same-lineage children and externally submitted children were incorrectly reused, while an
otherwise valid child created by another actor was incorrectly rejected. The product
correction changes only those three replay conditions.

The independent reviewer reran the six-file serialized tranche: 101 tests passed with one
unrelated dependency warning. Canonical identity and carrier bytes, derivation, activity,
references, manifest two-field mutation, replay-first 409/no-growth behavior, PENDING
review, no self-approval and caller-owned rollback all conform.

The Standards axis confirmed the exact three-path range, observed RED/GREEN story record,
minimal product/test correction and complete non-goals. Scoped Ruff and diff-check passed.
No OA reply, external submission, lifecycle, API/UI, catalog, ledger or old evidence
behavior was absorbed.
