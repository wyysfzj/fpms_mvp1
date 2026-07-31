# Independent Review — V8 PCT Fee Policy

- Review class: `PROTECTED`
- Full exact range:
  `dfc312b4fde48872ebb11b940167fa0cbc0f8bb2..b155bd5`
- Mechanical fix range: `cbe3173..b155bd5`
- Verdict: `APPROVED`
- P0: 0
- P1: 0
- P2: 0

The independent High review confirmed the latest-wins Delta-4 contract rather than the
superseded archive behavior: the command has exactly six fields and no
`national_stage_entry_date`; the evidence validator accepts
`(case_id, effective_on, evidence)`; and the effective boundary is `2024-08-06`.

The review covered exact typed evidence identity and cardinality, the five application
fee exemptions, ISR xor IPRP substantive-examination exemption, the six domestic
per-fee reductions through accepted validators, exact Decimal/error/result semantics
including large finite amounts, and the pure no-database/I/O/clock/activation boundary.

The independent decisive command passed `194` tests with one inherited third-party
passlib warning. Scoped Ruff, exact four-path diff-check, disposition inventory and
worktree cleanliness passed. The two product/test paths move from
`V8-ADOPT-FEE-OBLIGATION` to this story, changing the former count from 8 to 6 and adding
the new owner with count 2.

The initial review found one P1 documentation binding error: the story retained the
pre-merge disposition SHA-256. The one-line correction binds the story to the exact
current disposition SHA-256
`260d770ff703b3675d32f06e1ae56888dfa037d0be92b999ef312110f87a5d6e`.
The independent re-review reused the completed behavioral verification, confirmed that
the fix changed no other byte, and returned zero findings.

The final binary patch SHA-256 is
`0a02a0d1ec9bbda8b8a9919d5d4419d3db8368082b08cda29c30fd8a64f9c13f`.
The exact product/test Git tree fingerprint under the C3 checker algorithm is
`d7c7e2210d3da4a4012729c8b9b29037099712c8ef64bd100cc68a0fcc1c5dfd`.
