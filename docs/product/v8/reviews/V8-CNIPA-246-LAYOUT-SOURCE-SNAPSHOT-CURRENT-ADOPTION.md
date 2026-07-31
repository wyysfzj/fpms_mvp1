# Independent Review — V8 CNIPA 246 Layout Source Snapshot

- Review class: `PROTECTED`
- Exact integration range:
  `0516701da7834ea0ca12e8c3119173da314d1096..65efb39db3837f1bf94af192c230713d4794ccfe`
- Verdict: `APPROVED`
- P0: 0
- P1: 0
- P2: 0

The initial independent review rejected the three-path candidate with two P1 findings:
the two Announcement 246 source paths were still assigned to the broad
`V8-ADOPT-ANNUITY-RATE-SOURCES` owner, and the required first-reliance source-registry
record was absent.

The independently reviewed correction changes exactly those two disposition owners,
reduces the former owner count from 36 to 34, adds the exact source story with count 2,
and adds one `source-metadata-reviewed/not activated` registry record. The record contains
the exact source identity, dates, retrieval method/time, both locked hashes, acceptance
authority, effective scope/time and rollback impact. It explicitly creates no source,
rate-book, rate, legal or customer activation.

Both independent review axes returned `APPROVED` with zero findings. The reviewer
independently confirmed:

- exactly five changed paths;
- all 474 dirty-path disposition entries remain unique and their counts reconcile;
- normalized and provenance blobs match archive commit `6b2ef89da447353380b99853168d4d38aaf9210a`;
- normalized SHA-256
  `13a487ed0575e86412830420fdb652d93ba0a8eb915bfeecd02097d75631d2b8`;
- provenance SHA-256
  `2ff9eb7e84253359b2075e972bdd955313b95955f0ebad5e3d1b9fe9ec642377`;
- canonical eight-key provenance, normalized-source coherence and the exact
  `IC_LAYOUT_REGISTRATION_FEE=1000.00 CNY` source fact;
- zero content-aware secret or personal-data findings; and
- clean worktree and exact diff-check.

No pytest applies to this non-executable source-evidence story. No runtime, materializer,
candidate, canonical rate-data, activation, schema, API, UI or customer-decision byte
entered the range.

The full binary patch SHA-256 is
`013925f890a21c2fbf0e942b8d679053aa09e455fd225d29e48dd207b8db5947`.
The exact two-source-path Git tree fingerprint is
`fb4b9e7cf30c33f5e5dc1d9488ed0360c3e79ed5359e5dccacd8cc1dcf053ecc`.
The source-registry successor fingerprint for the original C3 governance custody paths is
`f1568815f1c3c9c9a1e57d48afcd10f323a8adf626d9c2866cd2f11953995908`;
the other four C3 custody paths are unchanged.
