# Story V8-FILING-FULL-WORD-READINESS-GATE-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Integration parent: `6e0f5c5a9fa6217198ec2cf2c4099d9526867cc1`
- Catalog row: `63`,
  `FPMS-V8-FILING-FULL-WORD-READINESS-GATE-20260712-01`.
- Outcome: current-adopt the frozen filing full-Word readiness gate so filing preparation
  projects only the current, approved and independently reviewed `FILING_FULL_WORD` into
  its required manifest and remains blocked when that manifest role is absent.
- Authority: the frozen row-63 task contract; the current-verified document-evidence
  review API and work-package manifest evidence-version dependencies.

## Exact behavior and paths

The read-only evidence predicate returns ready only for an exact `DocumentEvidenceVersion`
whose case matches, role is exactly `FILING_FULL_WORD`, current identity matches the case
and lineage, review state is `APPROVED`, and nonblank reviewer differs from creator with a
naive `reviewed_at` timestamp. Invalid, arbitrary-role, stale, unreviewed and self-reviewed
versions fail closed.

Filing-package refresh selects at most one evidence version for the full-Word attachment.
It projects the attachment into a required `FILING_FULL_WORD` manifest role only when that
single version passes the predicate; ambiguous or ineligible evidence clears readiness.
Package evaluation adds a `MANIFEST_MISSING` maintenance blocker when a filing package has
no full-Word manifest role.

Story-owned paths:

- `backend/app/modules/documents/evidence_policy.py`
- `backend/app/modules/official_workflows/service.py`
- `backend/tests/test_v8_filing_full_word_gate.py`
- this story card.

The focused public test is adopted byte-for-byte from archive checkpoint `6b2ef89` with
SHA-256 `8533756ac91837de572e4ece6a1743a8bf14a2b902f984ea782385baef0898b6`.

## Verification, integration concern and rollback

The focused test produced the contract RED with `4 failed, 1 passed`: the predicate,
eligible manifest projection and absent-role blocker were missing. After the minimum port,
the focused GREEN passed `3` tests and `6` subtests. The current dependency-aligned affected
bundle passed `276` tests and the same `6` subtests.

The frozen inherited add-gap bundle is no longer fully compatible with the integrated
tree: eight ensure-service tests omit the now-required `actor_id`, and its resolve-API happy
path conflicts with the current lifecycle-decision contract. Those nine failures are
outside this story's allowlist and behavior; the remaining `37` inherited tests and the
row-63 subtests passed. No compatibility shim or inherited-test rewrite is absorbed here.

No underlying evidence review rule, evidence mutation, second entrypoint, API, UI, schema,
migration, lifecycle decision, XML derivation rule, second catalog row or adjacent refactor
is included. Rollback removes only the readiness predicate, its filing-package projection
and blocker, the focused test and this story card.
