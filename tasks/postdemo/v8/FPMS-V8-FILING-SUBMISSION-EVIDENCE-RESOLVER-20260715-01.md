# FPMS-V8-FILING-SUBMISSION-EVIDENCE-RESOLVER-20260715-01

Status: PASS / INDEPENDENT REREVIEW APPROVED 2026-07-16 / ULTRA CONTRACT FROZEN 2026-07-15
Risk Tier: HIGH
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Phase: Foundation
Delta-4 Batch Row: `D4-05`
Executor: High

## Authoritative Contract

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-15-fpms-v8-ultra-contract-freeze-delta-4.md`
- Frozen Delta-4 spec SHA-256:
  `7c2a8c5947136be8434ba963616473c39158f25cbd2abb4a8fae23f0f6a4fff8`
- Accepted document-evidence external-finalization seam:
  `backend/app/modules/documents/evidence_workflow_service.py::finalize_external_submission`
- Accepted Delta-3 positive external-submission role allowlist in that seam.

If the recorded Delta-4 spec hash changes, this task is no longer contract-ready until the
affected lane revalidates the exact changed contract. Do not reopen broad V8 source analysis.

## Story Shape Classification

- `shared_file_density`: high (inherited from the authoritative Delta-4 design)
- `prereq_dependency_density`: high
- `be_fe_coupling`: low for this closure
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Implement exactly one read-only service that resolves, for one exact `FILING_PREP` package,
the one current/final/independently-approved externally-submittable evidence version and,
when already finalized, its one exact persisted external-submission activity plus the
deterministic hash of that activity's frozen canonical snapshot.

The only public seam is:

```python
def resolve_filing_final_evidence(
    package_id: str,
    transaction: Session,
) -> FilingFinalEvidenceResolution:
    ...
```

## Explicit Non-Closure

This task does not:

- create, update, review, switch, finalize or externally submit an evidence version;
- create or update a package, manifest, attachment, receipt, document or case activity;
- apply a lifecycle event or change any lifecycle/legal/legacy case projection;
- change any evidence-role enum, registration matrix or external-submission allowlist;
- implement Tasks 59, 60, 65 or 66, their API actor propagation, or their transactions;
- change routers, schemas, migrations, seeds, source activation, customer decisions or UI;
- refactor an accepted document-evidence service or broaden this task into adapter work.

## Remaining Follow-Up Task IDs

- `FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01` (existing V8 catalog Task 59)
- `FPMS-V8-CASE-BATCH-FILING-EVENT-ADAPTER-20260712-01` (existing V8 catalog Task 60)
- `FPMS-V8-FILING-EXTERNAL-SUBMISSION-ADAPTER-20260712-01` (existing V8 catalog Task 65)
- `FPMS-V8-FILING-RECEIPT-LIFECYCLE-ADAPTER-20260712-01` (existing V8 catalog Task 66)

Their exact existing task-file paths and separately owned closures remain unchanged. They
consume this resolver only after this task is PASS.

## Exact Result Contract

`FilingFinalEvidenceResolution` MUST be a frozen, slotted, keyword-only dataclass with exact
fields in this order:

1. `package_id: str`
2. `case_id: str`
3. `evidence_version_id: str`
4. `content_hash: str`
5. `reviewer_id: str`
6. `reviewed_at: datetime`
7. `final_submitted_at: datetime | None`
8. `submission_activity_id: str | None`
9. `submission_activity_hash: str | None`

The two activity fields are both null or both non-null. A mixed tuple fails closed.

## Input and Selection Contract

1. `package_id` must be an exact nonblank string no longer than the persisted UUID carrier;
   malformed input is 400 before database selection.
2. Resolve the package by exact ID and require `package_kind == "FILING_PREP"`.
3. Select exactly one `present=True` `OfficialWorkPackageManifest` row that has a non-null
   `evidence_version_id`. Zero or multiple candidates fail closed.
4. Resolve that exact `DocumentEvidenceVersion`; a dangling referenced ID is not treated as
   an empty package.
5. Require package, manifest, evidence version, its `Document`, and its `DocAttachment` to
   belong to the same case and to preserve the persisted manifest/version/attachment link.
6. Require manifest `content_hash` to equal the version `content_hash` byte-for-byte and the
   version hash to full-match `sha256:[0-9a-f]{64}`.
7. Require the version to be current through exact identity
   `f"{case_id}|{lineage_key}"`, state `FINAL`, review state `APPROVED`, and role in the
   accepted exact nine-role Delta-3 positive external-submission allowlist.
8. Require a nonblank creator, a nonblank reviewer different from creator, and a non-null
   naive `reviewed_at`. Malformed stored lineage, role, review or time fails closed.
9. Do not select a latest, first, filename-derived, customer-derived or fallback version.

## Finalized-Activity Contract

### Not yet finalized

When `version.final_submitted_at is None`, there MUST be no same-case
`DOCUMENT_EVIDENCE_EXTERNAL_SUBMISSION_FINALIZED` activity linked to that evidence version.
Return both activity fields as `None`. A matching activity without the carrier timestamp, or
any ambiguous matching activity, is a 409 conflict rather than a guessed recovery.

### Already finalized

When `version.final_submitted_at` is non-null, require it to be a naive `datetime` and resolve
exactly one same-case `CaseActivityEvent` with:

- `activity_type="DOCUMENT_EVIDENCE_EXTERNAL_SUBMISSION_FINALIZED"`;
- `lane="DOCUMENT"` and `confirmation_status="CONFIRMED"`;
- nonblank actor and exact reviewer equal to the approved version reviewer;
- `effective_at == occurred_at == version.final_submitted_at`;
- an idempotency key beginning with the accepted exact
  `document-external-submission:` namespace;
- exactly one evidence link:
  `DOCUMENT_EVIDENCE_VERSION / DocumentEvidenceVersion / version.id /
  version.content_hash / version.final_submitted_at`;
- the exact four-key canonical payload:

```json
{"evidence_version_id":"<version.id>","lineage_key":"<version.lineage_key>","role":"<version.role>","submitted_at":"<final_submitted_at.isoformat()>"}
```

Zero, multiple, missing-link, extra-link, malformed, cross-case, wrong-reviewer, wrong-time,
wrong-payload or carrier/activity mismatch fails closed.

## Canonical Activity Snapshot and Hash

After the persisted activity passes every check, construct exactly this JSON object:

```json
{"activity_id":"<activity.id>","activity_type":"DOCUMENT_EVIDENCE_EXTERNAL_SUBMISSION_FINALIZED","actor_id":"<activity.actor_id>","case_id":"<case_id>","confirmation_status":"CONFIRMED","effective_at":"<final_submitted_at.isoformat()>","evidence":[{"captured_at":"<final_submitted_at.isoformat()>","content_hash":"<version.content_hash>","evidence_kind":"DOCUMENT_EVIDENCE_VERSION","object_id":"<version.id>","object_type":"DocumentEvidenceVersion"}],"idempotency_key":"<persisted document-external-submission key>","lane":"DOCUMENT","occurred_at":"<final_submitted_at.isoformat()>","payload":{"evidence_version_id":"<version.id>","lineage_key":"<version.lineage_key>","role":"<version.role>","submitted_at":"<final_submitted_at.isoformat()>"},"reviewer_id":"<version.reviewer_id>"}
```

Serialize as UTF-8 with sorted object keys, compact separators, no ASCII escaping, no NaN
and no trailing newline. Compute
`submission_activity_hash = "sha256:" + sha256(exact_bytes).hexdigest()`.

The one-element evidence array order is fixed. Created/updated timestamps, database row
order and mutable carrier fields are excluded. Return the persisted activity ID and this
hash; never store or rewrite either value from this read service.

## Error Contract

| Condition | HTTP status | Error code |
| --- | ---: | --- |
| malformed `package_id` or transaction boundary input | 400 | `FILING_FINAL_EVIDENCE_INVALID` |
| exact package does not exist | 404 | `OFFICIAL_WORK_PACKAGE_NOT_FOUND` |
| manifest references a version that does not exist | 404 | `EVIDENCE_VERSION_NOT_FOUND` |
| wrong package kind; zero/multiple candidate; malformed/dangling ownership; hash, role, current, final, review, manifest, activity, evidence-link, payload or replay mismatch | 409 | `FILING_FINAL_EVIDENCE_CONFLICT` |

Do not downgrade a stored contradiction to 400/404, return partial data, or choose one row
from an ambiguous set. Preserve the repository `BusinessError` surface; no invented response
envelope is part of this service-only task.

## Transaction and Read-Only Contract

- Execute explicit bounded SELECTs under `transaction.no_autoflush`.
- Do not call a clock, `add`, `delete`, `update`, `flush`, `commit`, `rollback`, `refresh`,
  `expire`, `expire_all`, `begin_nested`, or any mutating service.
- Do not mutate ORM objects or the identity map.
- Do not call `finalize_external_submission()` or `apply_lifecycle_event()`.
- Entry and return MUST leave `transaction.new`, `transaction.dirty` and
  `transaction.deleted` unchanged and empty for this closure.

## Dependencies

All dependencies are accepted immutable prerequisites, not new work in this task:

1. accepted `DocumentEvidenceVersion` and work-package/manifest/activity/evidence-link models;
2. accepted `finalize_external_submission()` persisted event/payload contract;
3. accepted exact nine-role Delta-3 external-submission positive allowlist;
4. Delta-4 D4-05 contract at the frozen hash above.

If any prerequisite's persisted shape or accepted hash has changed, stop only this lane and
escalate the exact mismatch. Do not modify the prerequisite inside this task.

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-FILING-SUBMISSION-EVIDENCE-RESOLVER-20260715-01.md`
- `backend/app/modules/official_workflows/filing_evidence_resolver.py`
- `backend/tests/test_v8_filing_submission_evidence_resolver.py`
- `artifacts/FPMS-V8-FILING-SUBMISSION-EVIDENCE-RESOLVER-20260715-01/**`

No package export, common schema, router or shared ownership file is authorized.

## Verification Commands

```bash
cd backend
ruff check --fix app/modules/official_workflows/filing_evidence_resolver.py tests/test_v8_filing_submission_evidence_resolver.py
ruff format app/modules/official_workflows/filing_evidence_resolver.py tests/test_v8_filing_submission_evidence_resolver.py
ruff check app/modules/official_workflows/filing_evidence_resolver.py tests/test_v8_filing_submission_evidence_resolver.py
pytest -q tests/test_v8_filing_submission_evidence_resolver.py
```

Final task-local gates:

```bash
./scripts/task_validate.sh FPMS-V8-FILING-SUBMISSION-EVIDENCE-RESOLVER-20260715-01
python3 scripts/atomic_evidence_validate.py \
  FPMS-V8-FILING-SUBMISSION-EVIDENCE-RESOLVER-20260715-01 \
  --required-step lint \
  --required-step test \
  --required-step independent_review \
  --required-step scope
```

## TDD and Targeted Verification

High MUST capture the dirty baseline and initialize Evidence 1.1 before product/test edits.
The test owns one behavior surface through the public resolver seam.

### RED

Create the target test first and record the expected failure caused only by the missing
resolver module/public seam:

```bash
cd backend
pytest -q tests/test_v8_filing_submission_evidence_resolver.py
```

Required RED coverage defines fixtures and assertions for:

- exact successful unfinalized resolution;
- exact successful finalized resolution and byte-for-byte snapshot hash;
- zero/multiple manifest candidates;
- wrong package kind and dangling version;
- cross-case/document/attachment/manifest mismatch;
- malformed or unequal content hash;
- non-current, non-FINAL, unapproved, self-reviewed and ineligible-role versions;
- finalized timestamp/activity absence, multiplicity, extra/missing evidence link, wrong
  payload/reviewer/time/idempotency namespace;
- null/non-null activity-field pairing;
- read-only/no-autoflush/no-clock/no identity-map mutation;
- exact 400/404/409 codes above.

Do not accept collection/import failures unrelated to the absent resolver as valid RED.

### GREEN

Implement the smallest resolver satisfying the frozen contract, then run only:

```bash
cd backend
ruff check --fix app/modules/official_workflows/filing_evidence_resolver.py tests/test_v8_filing_submission_evidence_resolver.py
ruff format app/modules/official_workflows/filing_evidence_resolver.py tests/test_v8_filing_submission_evidence_resolver.py
ruff check app/modules/official_workflows/filing_evidence_resolver.py tests/test_v8_filing_submission_evidence_resolver.py
pytest -q tests/test_v8_filing_submission_evidence_resolver.py
```

No repo-wide Ruff, pytest, frontend build, Playwright or release gate is authorized here.

## Evidence Path

- `artifacts/FPMS-V8-FILING-SUBMISSION-EVIDENCE-RESOLVER-20260715-01/**`

## Evidence, Review and Serialization

- Initialize only through:

```bash
./scripts/evidence_init.sh FPMS-V8-FILING-SUBMISSION-EVIDENCE-RESOLVER-20260715-01 \
  --task-file tasks/postdemo/v8/FPMS-V8-FILING-SUBMISSION-EVIDENCE-RESOLVER-20260715-01.md \
  --allowlist backend/app/modules/official_workflows/filing_evidence_resolver.py \
  --allowlist backend/tests/test_v8_filing_submission_evidence_resolver.py
```

- Preserve the pre-existing dirty worktree; use Evidence 1.1 baseline subtraction and never
  attribute peer/user changes to this task.
- Record RED, GREEN, targeted lint/test, independent review and scope through the shared
  Evidence 1.1 producer. Do not hand-author `results.jsonl`.
- The resolver is read-only, but its test fixtures write SQLite. Report
  `READY_FOR_SERIAL_TEST`, wait for controller `GRANT`, acquire the repository serialization
  lock, run pytest, then release the lock. Ruff may run outside the SQLite lock.
- One independent reviewer must review the frozen contract, baseline-subtracted diff,
  targeted results and task-local evidence. The implementer cannot approve this task.
- PASS requires task-local `results.jsonl`, `summary.md`, scoped `git/diff.patch`, dirty
  baseline artifacts when applicable, scope validation, an approved zero-finding independent
  verdict, the repository task gate and atomic evidence validation.

## Final Gates

After updating this task to PASS and finalizing its scoped Evidence 1.1 bundle, run:

```bash
./scripts/task_validate.sh FPMS-V8-FILING-SUBMISSION-EVIDENCE-RESOLVER-20260715-01
python3 scripts/atomic_evidence_validate.py \
  FPMS-V8-FILING-SUBMISSION-EVIDENCE-RESOLVER-20260715-01 \
  --required-step lint \
  --required-step test \
  --required-step independent_review \
  --required-step scope
```

## Done Definition

This task is PASS only when the exact public resolver and DTO implement the one frozen
D4-05 read-only closure; every selection, ownership, current/final/review/role/hash and
finalized-activity contradiction fails closed with the exact error surface; the canonical
activity snapshot/hash is deterministic and independently reconstructible; the transaction
and identity map remain unmodified; RED and GREEN are recorded; scoped lint/test pass under
the required SQLite serialization; an independent reviewer approves with zero findings;
Evidence 1.1 scope/baseline artifacts validate; and both repository task gates pass.

No follow-up behavior is absorbed, no external submission or lifecycle write occurs, and
the non-closure boundary is preserved.
