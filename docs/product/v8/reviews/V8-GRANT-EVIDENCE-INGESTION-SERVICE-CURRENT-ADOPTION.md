# Independent Review — Grant Evidence Ingestion Service

- Review class: `PROTECTED`.
- Reviewed story range: `665ab9d..c686c19`.
- Implementation commits: `34329371306e1561526b0f9855eedb405bd6c510`,
  `cada0a256b2170eab934b5a3a55711880abd1466`,
  `c686c19429ea79f82cbaadb6182d849c75c3133d`.
- Task SHA-256:
  `330d7274cd63ecab10a8898c42dbf01e219db98ccbcc34b6b7c41838a45e8c0a`.
- Verdict: `APPROVED`.
- P0/P1/P2: `0/0/0`.

The exact two-path story creates a PENDING grant-evidence candidate only from the current canonical
`ACQUIRED -> FIRST_VERIFIED -> SECOND_VERIFIED` official-copy chain. It validates the evidence and
attachment identity, every stored event and predecessor, the event-time CNIPA source and duty-role
authority, distinct actual verifiers, and the separately configured active proposer. Source,
source-config and role-config snapshot bytes are rebound to their carrier columns before candidate
derivation, closing the initial independent-review finding.

Candidate and acquisition snapshots are deterministic and hash-bound. Exact replay is reused only
when every persisted domain field and canonical byte remains identical; changed, corrupt,
ambiguous or unauthorized lineage fails closed. A later independent finding identified that an
insert-time `IntegrityError` could incorrectly reinterpret a concurrent winner as exact replay.
The successor commit now distinguishes the two paths exactly: a row found by the immutable
pre-insert replay lookup remains `REUSED`, while any insert-time race is a 409 conflict with no
candidate residue. The nested savepoint leaves transaction ownership with the caller, and the
service changes no legal status, lifecycle, document/evidence state, deadline, fee or payment fact.

Fresh successor verification passed: focused service pytest `22 passed`, including the injected
concurrent `IntegrityError` regression; scoped Ruff and exact two-path diff-check passed.
Independent High successor review approved `P0/P1/P2 = 0/0/0`. The exact two-path Git tree
fingerprint is `2db66d3920284ddbd9d2e064a78c1fe30dc8ea2d59c12aaad46bf47624ba3956`.
