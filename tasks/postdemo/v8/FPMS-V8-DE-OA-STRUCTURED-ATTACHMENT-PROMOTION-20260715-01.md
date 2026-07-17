# FPMS-V8-DE-OA-STRUCTURED-ATTACHMENT-PROMOTION-20260715-01

Status: READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-15 / NOT STARTED

## Risk and scheduling

- Risk: HIGH — document/evidence identity, derivation, provenance, and lineage.
- Priority: `P0-prereq-heavy-story`.
- Execution: serialized after every dependency below is evidenced PASS; this task owns only this task path while active.

## Frozen authority

- `docs/superpowers/specs/2026-07-15-fpms-v8-ultra-contract-freeze-delta-4.md`, lines 360–422 and decision `D4-08`.
- This task is contract frozen. Do not reopen broad source analysis or change the accepted behavior.

## Dependencies

- `D4-06` is PASS.
- `D4-07` is PASS.
- The accepted attachment register/version prerequisite is PASS and exposes the frozen register-version operation used here.
- The accepted derivation prerequisite is PASS and exposes the frozen derivation/link operation used here.
- Missing, ambiguous, stale, or non-PASS dependency evidence is a hard blocker; do not infer compatibility or substitute another path.

## Exact Closure Slice

Implement exactly this service function:

```python
def promote_oa_structured_attachment(
    command: PromoteOaStructuredAttachmentCommand,
    transaction: Session,
) -> PromoteOaStructuredAttachmentResult:
    ...
```

`PromoteOaStructuredAttachmentCommand` has exactly `case_id`, `package_id`, `manifest_id`, `raw_evidence_version_id`, `target_state`, `actor_id`, `promoted_at`, and `idempotency_key`. `target_state` is only `DRAFT` or `FINAL`.

The only closure is formal promotion of one reviewed manifest classification plus one current `RAW_ATTACHMENT` `DRAFT` parent version into a typed `OA_STRUCTURED_ATTACHMENT` child version, with the exact derivation, activity, references, manifest pointer update, replay behavior, and caller-owned atomic transaction below.

## Explicit Non-Closure

- No bulk, batch, retry-queue, background-job, controller, route, UI, migration, seed, or release work.
- No OCR, parsing, filename-driven reclassification, content transformation, template generation, or business interpretation.
- No mutation, deletion, replacement, relocation, or re-versioning of the parent.
- Promotion leaves child review `PENDING`; creator self-approval is forbidden.
- No external submission, OA reply preparation, lifecycle status, customer decision, permission expansion, or new attachment type.
- Do not alter manifest `official_file_role` or any manifest field other than `evidence_version_id` and `content_hash`.
- No refactor or cleanup outside the allowlist.

## Remaining Follow-Up Task IDs

- None inside this frozen closure. Any additional behavior or prerequisite must receive its own approved atomic task ID.

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-DE-OA-STRUCTURED-ATTACHMENT-PROMOTION-20260715-01.md`
- `backend/app/modules/documents/oa_attachment_promotion_service.py`
- `backend/tests/test_v8_oa_structured_attachment_promotion.py`
- `artifacts/FPMS-V8-DE-OA-STRUCTURED-ATTACHMENT-PROMOTION-20260715-01/**`

Every tracked or untracked path outside this allowlist is out of scope. Pre-existing dirty paths must be captured by Evidence 1.1 and baseline-subtracted; they must not be edited, absorbed, staged, or reported as this task's work.

## Observable contract

### Fresh-call eligibility and typed child

1. The package exists in `case_id`, is exactly same-case `OA_REPLY`, and contains the present `manifest_id`.
2. The manifest belongs to that package, links the named raw attachment/version, and carries exactly one permitted role: `OA_STATEMENT_WORD`, `OA_MODIFIED_CLAIMS`, `OA_AMENDMENT_COMPARISON`, `OA_OTHER_PROOF`, or `OA_ADDITIONAL_FILE`.
3. The named parent is the current `RAW_ATTACHMENT` `DRAFT` version; its hash matches both manifest and attachment state. Upload filename never supplies or changes its classification.
4. Create or reuse a same-content `OA_STRUCTURED_ATTACHMENT` child version with the same content hash, `target_state`, review `PENDING`, and exact lineage `<parent.lineage_key>|OA|<manifest-role>`.
5. Register exactly one `OFFICIAL_RECOGNITION` derivation from that parent to that child. Update only manifest `evidence_version_id` and `content_hash` to the child, in the same transaction; preserve `official_file_role`.
6. Missing, stale, multiple, mismatched, or conflicting package, manifest, role, parent, hash, child, lineage, or derivation state fails closed before a fresh write; never guess, select-first, repair, or infer from filename.

### Canonical command/source identity

Before any fresh write, serialize exactly the following object as UTF-8 JSON with sorted keys, compact separators, and no ASCII escaping, hash those bytes with SHA-256, and set `promotion_identity_key = "sha256:" + <64-lower-hex-digest>`:

```json
{"actor_id":"<actor_id>","case_id":"<case_id>","command_idempotency_key":"<idempotency_key>","manifest_id":"<manifest_id>","manifest_role":"<exact-OA-role>","package_id":"<package_id>","promoted_at":"<promoted_at.isoformat()>","raw_content_hash":"<raw-version.content_hash>","raw_evidence_version_id":"<raw-version.id>","target_state":"<DRAFT-or-FINAL>"}
```

No key may be added, omitted, renamed, normalized, or derived from another carrier.

### Canonical derivation and activity carrier

Append exactly one `OA_STRUCTURED_ATTACHMENT_PROMOTED` DOCUMENT activity with `confirmation_status=CONFIRMED`, unchanged central projection, and durable idempotency `oa-structured-promotion:<command.idempotency_key>`. Its payload and the `OFFICIAL_RECOGNITION` derivation `source_snapshot` are byte-identical canonical JSON, encoded by the same rules above, with exactly these keys:

```json
{"actor_id":"<actor_id>","case_id":"<case_id>","command_idempotency_key":"<idempotency_key>","manifest_id":"<manifest_id>","manifest_role":"<exact-OA-role>","package_id":"<package_id>","promoted_at":"<promoted_at.isoformat()>","promotion_identity_key":"sha256:<64-lower-hex>","raw_content_hash":"<raw-version.content_hash>","raw_evidence_version_id":"<raw-version.id>","schema":"FPMS_OA_STRUCTURED_ATTACHMENT_PROMOTION_V1","target_state":"<DRAFT-or-FINAL>","typed_content_hash":"<child-version.content_hash>","typed_evidence_version_id":"<child-version.id>"}
```

The activity has exactly two references captured at `promoted_at`: `RAW_ATTACHMENT_VERSION / DocumentEvidenceVersion / parent.id / parent.content_hash` and `OA_STRUCTURED_ATTACHMENT_VERSION / DocumentEvidenceVersion / child.id / child.content_hash`.

### Replay-first idempotency and 409 matrix

Before any fresh-write validation or write, look up the unique same-case activity key `oa-structured-promotion:<command.idempotency_key>`. No carrier enters the fresh path. Exactly one carrier enters replay validation. Multiple carriers are `409`.

Replay must parse the exact payload, require its exact key set/schema/canonical values, recompute and compare `promotion_identity_key`, resolve exactly one named child plus exactly one matching `OFFICIAL_RECOGNITION` derivation, require the manifest still names that child/hash, and compare both exact evidence references before reuse.

Return `409` with no write for every replay conflict: missing, multiple, malformed, or tampered activity/payload/child/derivation/manifest/reference carrier; promotion identity mismatch; or different role, raw hash, target state, actor, promoted time, source version, package, manifest, or case under the same idempotency key. Only a fully validated replay returns reuse, and it creates no second child, derivation, activity, reference, or manifest mutation.

### Caller transaction and review boundary

Every fresh-path child/version, derivation, activity, reference, and manifest-pointer write uses the caller-provided `transaction` as one atomic unit. The function must not open or commit an independent transaction. Any failure leaves the caller able to roll back the whole promotion with no partial child, derivation, activity, reference, or manifest update. Promotion itself never self-approves the `PENDING` child and never performs external submission, OA reply preparation, lifecycle transition, or customer decision.

## TDD contract

Use public service behavior and one behavior at a time.

1. RED/GREEN: exact function signature, exact eight command fields, and only `DRAFT|FINAL` target state.
2. RED/GREEN: same-case `OA_REPLY`, present linked manifest, each of the five exact single roles, and current `RAW_ATTACHMENT` `DRAFT` parent/hash; reject every missing, multiple, stale, wrong-kind, wrong-case, wrong-package, wrong-role, non-current, or hash-mismatch state without filename inference.
3. RED/GREEN: same-content typed child reuse/create, identical hash, exact lineage, requested target state, review `PENDING`, exact one `OFFICIAL_RECOGNITION` derivation, and only the two allowed manifest field updates.
4. RED/GREEN: exact command/source canonical key set and bytes produce the expected prefixed lower-hex `promotion_identity_key`.
5. RED/GREEN: byte-identical exact-key activity payload/derivation snapshot, exact `CONFIRMED` DOCUMENT activity idempotency, unchanged central projection, and exact two timestamped references.
6. RED/GREEN: lookup precedes fresh validation; a complete exact carrier reuses without row growth, while every enumerated replay carrier/identity difference returns `409` with no write.
7. RED/GREEN: injected failure at each write boundary proves caller-transaction rollback; creator cannot self-approve and promotion performs none of the frozen non-closures.
8. Refactor only while targeted tests remain green; add no speculative adapter or fallback.

## Verification Commands

Run only task-scoped checks unless the frozen controller explicitly grants a broader close point:

```bash
./scripts/evidence_init.sh FPMS-V8-DE-OA-STRUCTURED-ATTACHMENT-PROMOTION-20260715-01 \
  --task-file tasks/postdemo/v8/FPMS-V8-DE-OA-STRUCTURED-ATTACHMENT-PROMOTION-20260715-01.md \
  --allowlist tasks/postdemo/v8/FPMS-V8-DE-OA-STRUCTURED-ATTACHMENT-PROMOTION-20260715-01.md \
  --allowlist backend/app/modules/documents/oa_attachment_promotion_service.py \
  --allowlist backend/tests/test_v8_oa_structured_attachment_promotion.py \
  --allowlist artifacts/FPMS-V8-DE-OA-STRUCTURED-ATTACHMENT-PROMOTION-20260715-01
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/v8/FPMS-V8-DE-OA-STRUCTURED-ATTACHMENT-PROMOTION-20260715-01.md
pytest -q backend/tests/test_v8_oa_structured_attachment_promotion.py
./scripts/task_validate.sh FPMS-V8-DE-OA-STRUCTURED-ATTACHMENT-PROMOTION-20260715-01
python scripts/atomic_evidence_validate.py FPMS-V8-DE-OA-STRUCTURED-ATTACHMENT-PROMOTION-20260715-01
```

SQLite-writing verification must wait for the controller's explicit `GRANT`, acquire the repository serialization lock, and release it after pytest.

## Evidence Path

- `artifacts/FPMS-V8-DE-OA-STRUCTURED-ATTACHMENT-PROMOTION-20260715-01/`

## Done Definition

- The exact service and command accept only a reviewed same-case `OA_REPLY` manifest classification plus current `RAW_ATTACHMENT` `DRAFT` parent and create/reuse the same-hash, exact-lineage `OA_STRUCTURED_ATTACHMENT` child in `DRAFT|FINAL` with review `PENDING`.
- Exactly one `OFFICIAL_RECOGNITION` derivation, one exact `CONFIRMED` promotion activity, two exact references, and only the manifest child ID/hash update commit in the caller transaction.
- Both canonical JSON objects, `promotion_identity_key`, activity idempotency, replay-first carrier validation, no-growth reuse, and the complete `409` matrix match this contract byte-for-byte.
- Every fresh validation conflict or persistence failure closes without partial writes; no self-approval, external submission, OA preparation, lifecycle transition, or customer decision occurs.
- Task-scoped TDD, serialized targeted pytest, scope/evidence gates, and independent zero-finding approval all pass while the explicit non-closure remains untouched.

## Acceptance gate

- All dependencies are evidenced PASS before implementation begins.
- Targeted RED/GREEN evidence covers exact command/function shape, five-role eligibility, parent/hash/currentness, typed child/hash/lineage/review, derivation, both canonical carriers, identity hash, activity/references, manifest field boundary, replay/`409`, and caller-transaction rollback.
- Targeted pytest exits `0` under the serialized SQLite protocol.
- The baseline-subtracted diff contains only allowlisted task work.
- Task-local Evidence 1.1 contains latest required logs/results, PASS summary, dirty baseline when applicable, scoped `git/diff.patch`, and no stale/nonzero required result.

## Independent review gate

One independent HIGH reviewer, who did not implement this task, must issue a task-local `APPROVED` verdict with zero unresolved findings after checking the frozen authority, baseline-subtracted diff, exact command/function and role set, typed child rules, canonical JSON/key computation, derivation/activity/reference carriers, replay-first `409` behavior, manifest mutation boundary, caller-transaction rollback, and allowlist. The implementer cannot self-approve.

## Scope gate

`python scripts/check_task.py`, repository task validation, and atomic evidence validation must all pass. Any outside-allowlist tracked/untracked delta, missing dirty-baseline subtraction, or mismatch between the task contract and evidence is FAIL.

## Closure gate

Report PASS only after the exact D4-08 reviewed-manifest plus current-RAW-parent promotion into the same-hash exact-lineage typed child, its `OFFICIAL_RECOGNITION` derivation, exact canonical `CONFIRMED` activity/two refs, manifest pointer update, replay/`409`, `PENDING` review, and caller-transaction atomicity are verified; every required command and independent verdict is latest and passing; and every non-closure remains untouched. Otherwise report FAIL or BLOCKED with the exact evidence path and unmet condition.
