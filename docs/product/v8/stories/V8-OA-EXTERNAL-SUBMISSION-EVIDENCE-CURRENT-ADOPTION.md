# Story V8-OA-EXTERNAL-SUBMISSION-EVIDENCE-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Integration parent: `e8686178af26`
- Outcome: the existing OA submission service finalizes the exact current, independently
  reviewed `OFFICIAL_SUBMISSION_LIST` evidence linked to the exact OA reply package by
  calling `finalize_external_submission()` in the caller-owned transaction, then records
  one submission-confirmed package checklist item without closing the OA task or changing
  the central lifecycle projection.
- Catalog ID: `FPMS-V8-OA-EXTERNAL-SUBMISSION-EVIDENCE-20260712-01` (ordinal `69`,
  profile `TC-ADAPTER`).
- Authority: frozen catalog row `69`, `docs/product/v8/domain-contract.md`, the accepted
  `finalize_external_submission()` seam and role allowlist, and the independently accepted
  Row 67/68 product and review chain through `e8686178af26`.
- Archive comparison anchor: `6b2ef89da447353380b99853168d4d38aaf9210a`.

## Dependency and exact paths

The current Row 67 package link and Row 68 prepared-document activity are prerequisites.
The deep finalization seam remains unchanged and retains its exact positive role allowlist,
review/current/final evidence validation, caller-owned transaction and projection-neutral
`DOCUMENT` activity behavior.

- `backend/app/modules/official_workflows/service.py`
- `backend/tests/test_v8_oa_external_submission_evidence.py`
- `docs/product/v8/stories/V8-OA-EXTERNAL-SUBMISSION-EVIDENCE-CURRENT-ADOPTION.md`

The shared service and all SQLite-writing verification remain serialized.

## Observable contract

`finalize_oa_external_submission()` accepts one exact `OA_REPLY` package whose source and
reply documents form the persisted reply chain, whose resolve key matches that source, and
whose unique present `OFFICIAL_SUBMISSION_LIST` manifest links the requested evidence and
attachment. The evidence must belong to the same case and reply document, be current,
`FINAL`, independently `APPROVED`, and carry one exact lowercase SHA-256 identity shared by
the manifest and attachment. Missing, ambiguous or inconsistent carriers fail closed before
the deep finalizer.

The adapter calls `finalize_external_submission()` with the exact persisted case and
evidence identities and the namespaced key
`oa-external:{package_id}:{idempotency_key}`. It reuses the deep seam's exact external-
submission `DOCUMENT` activity on replay, rejects upstream key or payload drift, and writes
or reuses one `SUBMISSION_CONFIRMED` checklist item linked to the exact evidence version and
activity. It does not commit, roll back or close the caller-owned transaction.

The OA task remains open. Package identity and status, source/reply document fields, legacy
case status and central lifecycle projection remain unchanged. No receipt or lifecycle event
is created by this adapter.

## TDD and verification

The archived focused test was restored byte-for-byte with SHA-256
`031dfc9c62ad0631e85e4fbecd86b59d382b4b1ffa97499ab87ed27124fb9d17`.
Under the controller-granted serialized SQLite lane, focused RED produced `44 failed, 2
warnings` because the public Row 69 command, result and entrypoint were absent. The minimum
archived adapter then produced focused GREEN `44 passed, 2 warnings`. The exact Row 69,
affected Row 67/68, role-allowlist and finalization-seam tranche produced `98 passed, 2
warnings`. The warnings are inherited passlib and Pydantic deprecations. The serialized lane
was released immediately after the final test command.

Scoped Ruff and exact diff checks run on the three owned paths. Independent High review of
the eventual exact commit/range remains required; this implementer does not approve the
`PROTECTED` story.

## Non-goals and rollback

No change to `finalize_external_submission()`, its role allowlist or deep validation; no OA
task close; no Row 70 receipt/lifecycle behavior; no filing adapter; no API/UI,
schema/model/migration/seed, ledger, review receipt, old task/evidence or broad tests. No
new source, customer, legal, fee or lifecycle decision is introduced.

Rollback reverts only the focused test, this story card and the Row 69 adapter hunk in
`backend/app/modules/official_workflows/service.py`.
