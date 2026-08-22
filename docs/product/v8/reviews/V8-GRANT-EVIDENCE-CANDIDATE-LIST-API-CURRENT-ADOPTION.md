# Independent Review — Grant Evidence Candidate List API

- Review class: `PROTECTED`.
- Frozen task commit: `dcd75d84e0ef49d0e92728ca39972900d95e418d`.
- Implementation commit: `89e632309619b56e890d632206f7e30d280a8d7d`.
- Task SHA-256:
  `17af351f8d9e1a752c9279f01231073bbdd5bec09fbc54f0242e8212eeedd4b5`.
- Verdict: `APPROVED`.
- P0/P1/P2: `0/0/0`.

The exact three-path story adds one bodyless and queryless UUID GET at
`/documents/{document_id}/grant-evidence-candidates`. It requires `Doc.Read`, injects one
server UTC-naive `read_at`, constructs one exact `ListGrantEvidenceCandidatesCommand`, and
delegates once to the accepted candidate-read service. Strict output-only models preserve the
ordered projection, raw conflicts, review data, authority identities and hashes without
normalizing or selecting a conflict value.

The adapter performs no direct product query, write, flush, commit, rollback or close. Empty
results remain `[]`; service 404/409 and framework 401/403/422 semantics remain unchanged. The
existing ingestion POST bytes and 201 contract are identical before and after this story.

Fresh verification passed: focused candidate-list API plus ingestion POST, candidate-read and
shared-router regressions `32 passed`; scoped Ruff, owned-new-file format check and exact
three-path diff-check passed. Independent High review approved `P0/P1/P2 = 0/0/0`. The exact
three-path Git tree fingerprint is
`0c12e8948aaf629b8008edae50490b3213aa4b6565a9b560e0d46da399246e20`.
