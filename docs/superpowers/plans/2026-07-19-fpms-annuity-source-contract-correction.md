# FPMS Annuity Source Contract Correction R3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` for each atomic task. Preserve current-v2
> taskctl state, existing baselines and serialized SQLite verification.

**Goal:** Break the source-index/canary activation cycle without compatibility work:
close OA Reply Seam as the unchanged-current-v2 fast-close canary, activate fast-close,
activate the reviewed CNIPA annuity source index under the new dynamic governance
authority, and then resume the existing annuity candidate.

**Architecture:** The hash-locked Delta-4 and Delta-7 files remain immutable. The R3 design
is a latest-wins overlay only for D4-10 source identity, fast-close canary/order and the
Delta-7 fresh-write flush count proven incompatible with the current ORM mapping. Every
implementation task keeps one exact owner and allowlist. Live governance changes only
through a reviewed activation candidate; ordinary tasks never edit governance bytes
directly.

**Tech Stack:** Python 3.11, SQLAlchemy, SQLite, pytest/unittest, Ruff, Poppler, canonical
UTF-8 JSON, current-v2 taskctl/Evidence 1.1, then activated `fast-close-1`.

---

## 1. Frozen facts and immutable state

- R3 design:
  `docs/superpowers/specs/2026-07-19-fpms-annuity-source-contract-correction-design.md`.
- OA canary:
  `FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01`.
- Fast-close:
  `REPO-GOVERNANCE-FAST-CLOSE-CUTOVER-20260719-01`.
- Source activation:
  `REPO-CNIPA-ANNUITY-SOURCE-AUTHORITY-ACTIVATION-20260719-01`.
- Existing annuity task:
  `FPMS-V8-CNIPA-ANNUITY-RATE-CANDIDATE-20260715-01`.
- Immutable Delta-4 SHA-256:
  `7c2a8c5947136be8434ba963616473c39158f25cbd2abb4a8fae23f0f6a4fff8`.
- Official PDF SHA-256:
  `3792384f32e782c96e5630a6ac42892d8b8cd272a219a7d674ceebf16ec7cdce`.
- Exact snapshot SHA-256:
  `e8599a13429e3f536312eaeed0ec1a09b5f91533caacf2d8514dbeef1533d544`.

The shared workspace is required because OA, fast-close and annuity already captured
current baselines. Do not create a worktree, push, reset, clean, stash, discard or recapture
any baseline.

## 2. Task A — freeze R3 planning

- [ ] Independently review the entire R3 design against `AGENTS.md`, selected modules,
  active task states, fast-close design/plan, immutable Delta-4 and the supplied PDF.
- [ ] Require one verdict with `P0: 0`, `P1: 0`, `P2: 0`.
- [ ] Set the design status to approved only after that review.
- [ ] Independently review this whole plan. Confirm the sequence is acyclic, every edited
  path has one owner, live governance changes only through activation, and no existing
  baseline/evidence prefix is rewritten.
- [ ] Run `git diff --check` on the two planning documents.
- [ ] Commit only those planning documents; do not push.

## 3. Task B — close OA Reply Seam as current-v2 canary

### Existing durable state

The exact task and allowlist remain unchanged:

- `tasks/postdemo/v8/FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01.md`;
- `backend/app/modules/documents/evidence_workflow_service.py`;
- `backend/tests/test_v8_prepare_oa_reply_seam.py`;
- its task-local artifact tree.

Preserve:

- controller/implementer `lead/lead`;
- current-v2 digest and legacy-adopt baseline;
- valid RED ordinal 11;
- latest failed GREEN ordinal 12;
- previous successful product/lint/scope evidence as history;
- Delta-7 latest-wins contract and terminal prerequisite
  `FPMS-V8-DE-OA-REPLY-PREPARATION-DERIVATION-TYPE-20260719-01`.

### Diagnostic and TDD steps

- [ ] Reproduce only the latest focused failure through the serialized SQLite runner if
  new evidence is required; do not rerun older ordinals.
- [ ] Trace the first foreign-key failure from
  `DocumentEvidenceDerivation.actor_id/parent/child` through the fixture and model
  relationships. Compare with a working derivation fixture before editing.
- [ ] Record the confirmed root cause: case and parent already exist, actor is not an FK,
  but the pending child version has no ORM relationship edge to the pending derivation, so
  the single flush may insert the derivation first.
- [ ] Append to the already allowlisted task file an R3 latest-wins section that supersedes
  only Delta-7 fresh creation's single-flush wording with exactly two ordered flushes in
  the same caller-owned transaction:
  1. `add(version)` and `flush([version])`;
  2. set the package reply link, add the derivation and final `flush()`.
  Preserve every validation, canonical snapshot, replay, rollback, no-activity and
  no-internal-commit/rollback requirement.
- [ ] Update the focused canonical-receipt test to assert exactly two flushes and retain
  the rollback test proving that caller rollback removes version, package link and
  derivation. Do not authorize Core INSERT, runtime mapper mutation, `models.py`, another
  transaction or another allowlisted path.
- [ ] Record a new valid review-finding RED after the task/test contract edit and before
  production edits. Preserve ordinal-11 and ordinal-12 as immutable history; do not rerun
  older ordinals.
- [ ] Make the smallest service change: flush only the child version first, then create/add
  the derivation and perform the existing final flush.
- [ ] Run the exact task test file through `taskctl backend-test test`; require all tests
  pass, not merely the first failure.
- [ ] Run scoped Ruff check/format-check and three-path `git diff --check`.
- [ ] Refresh summary and canonical current-v2 scope once.
- [ ] Prepare a new review generation, obtain one independent zero-finding domain/spec
  review, then run current-v2 close. Do not self-approve.
- [ ] Require terminal PASS before changing any fast-close source byte.

## 4. Task C — apply the fast-close R3 overlay and activate

Only after OA terminal PASS:

- [ ] In the existing fast-close task file (already allowlisted), append one latest-wins
  R3 section that:
  - replaces only the exact product canary with the OA task;
  - binds OA terminal task/candidate/patch/governance hashes;
  - adds
    `REPO-CNIPA-ANNUITY-SOURCE-AUTHORITY-ACTIVATION-20260719-01`
    to the candidate manifest's expanded-acceptance task IDs;
  - preserves the fast-close task ID, closure, non-closure, allowlist, baseline and
    current-v2 protocol.
- [ ] Validate the amended task contract without restarting or recapturing its baseline.
- [ ] Continue the already-approved fast-close plan from its first missing RED step. Do not
  repeat design, materialization or OA work.
- [ ] Implement the minimum `fast-close-1`, shadow, dynamic activation and simplicity
  closure under the existing fast-close allowlist and exact canonical selectors.
- [ ] Independently review the complete fast-close patch and shadow binding.
- [ ] Atomically activate only after OA terminal PASS and matching shadow receipt.
- [ ] Require fast-close terminal PASS and an active manifest that supports dynamic
  activation tasks. No source-authority fact changes in this task.

## 5. Task D — activate the CNIPA annuity source authority

This task may be materialized only after Task C terminal PASS. At materialization, freeze
the exact active manifest version/digest and generalized activation contract produced by
Task C; never guess them in advance.

### Exact closure

Create
`tasks/repo/REPO-CNIPA-ANNUITY-SOURCE-AUTHORITY-ACTIVATION-20260719-01.md`
with risk `HIGH`, closure tags `["fee", "governance", "source-authority"]`, expanded
acceptance and exactly one closure:

1. stage a candidate `docs/agents/source-authority.md` that indexes:
   - metadata article
     `https://www.cnipa.gov.cn/art/2026/3/30/art_1518_205552.html`;
   - exact PDF
     `https://www.cnipa.gov.cn/module/download/down.jsp?i_ID=205552&colID=1518`;
   - title/date/32 pages/2478214 bytes/content hash/retrieval time;
   - old attachment explicitly as superseded history, not current D4-10 authority;
2. stage the minimum candidate manifest transition naming this activation task while
   retaining `fast-close-1` and all expanded task IDs;
3. independently review and atomically install the candidate through dynamic activation.

### Exact non-closure and allowlist

No product/task data, rate value, Delta-4, canary, runtime selection, API, UI, schema,
migration or compatibility work.

Allow only:

- its task file;
- `docs/agents/source-authority.md`;
- `docs/agents/manifest.json`;
- `scripts/tests/test_v8_annuity_source_contract_correction.py`;
- its artifact tree.

Kernel and generalized activation tooling are read-only accepted prerequisites.

### TDD and close

- [ ] Write the focused unittest first. It checks exact source facts, immutable Delta-4,
  candidate manifest transition and fail-closed old/current distinction. When
  `CNIPA_SOURCE_PDF` is explicitly set, it also checks PDF bytes/metadata/Annex 2; without
  it, only the external-file subtest may skip.
- [ ] Record the legal `shasum -a 256` source proof and an executed nonzero unittest RED
  against the old index.
- [ ] Stage candidate governance bytes under the task artifact; do not edit live
  governance before activation.
- [ ] Run the focused GREEN, scoped Ruff/diff, candidate scope, independent source plus
  governance review, task gate and atomic evidence gate.
- [ ] Activate serially and require terminal PASS with exact installed hashes.

## 6. Task E — adopt governance and resume the existing annuity task

- [ ] Enumerate actual non-PASS states whose selected modules include
  `docs/agents/source-authority.md`; do not rely on a stale list.
- [ ] For each, replay its exact `start --task-file` as recorded controller/implementer to
  generate task-local `GOVERNANCE_DIGEST_MISMATCH` without baseline recapture.
- [ ] Obtain one task-specific independent approval for each
  `governance_change.change_sha256`, then run `governance-adopt` serially.
- [ ] Assert task ID/path, ordered allowlist, complete baseline and existing command/result/
  event bytes are preserved as prefixes.

For the annuity task:

- [ ] Add the R3 latest-wins source overlay only to its already allowlisted task file.
- [ ] Record the legal source hash once; do not repeat its historical invalid RED.
- [ ] Create the focused public test and run the first valid behavioral RED.
- [ ] Create the canonical offline JSON and minimum strict parser/selector/materializer.
- [ ] Run focused GREEN, scoped Ruff/diff/scope, independent source/domain review and
  current-v2/expanded close according to its recorded protocol.
- [ ] Keep the candidate `PENDING/INACTIVE`; no activation or runtime fee selection.

## 7. Completion boundary

This plan is complete only when:

- OA is terminal PASS under unchanged current-v2;
- fast-close is terminal activation PASS;
- the reviewed live source index is terminal activation PASS;
- every actual non-PASS selected consumer safely adopts the new digest;
- the original annuity task is terminal PASS with unchanged identity/baseline and exact
  source provenance; and
- no compatibility task, direct evidence-state edit, baseline recapture, broad release
  gate or push occurred.
