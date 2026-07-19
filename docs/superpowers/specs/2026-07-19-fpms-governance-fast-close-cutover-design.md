# FPMS Governance Fast-Close Cutover Design

Status: APPROVED DESIGN / READY FOR INDEPENDENT SPEC REVIEW
Date: 2026-07-19
Decision owner: User
Implementation task: `REPO-GOVERNANCE-FAST-CLOSE-CUTOVER-20260719-01`

## 1. Decision

Keep atomic tasks and the FPMS high-risk safety rules. Remove the accidental fixed cost
created by repeated scope reconstruction, duplicated acceptance scans, handwritten status
summaries, and open-ended legacy-controller compatibility.

Newly started tasks after activation use exactly:

1. targeted RED/GREEN and required scoped checks;
2. one canonical baseline-subtracted scope candidate;
3. one independent review for ordinary HIGH work;
4. one atomic `accept` transaction that validates the candidate, review, required results,
   ownership and current scope key, then writes terminal PASS.

Foundation, Full, Final and Release remain serialized and retain any explicitly contracted
additional review axes and broad final verification.

## 2. Evidence for the change

The active governance implementation has crossed the boundary from guardrail to subsystem:

- core governance execution scripts contain about 14,188 lines and their focused tests
  about 13,445 lines;
- the repository contains 53 `REPO-*` governance artifact directories;
- `scripts/taskctl` has grown to 7,365 lines and `scripts/evidence_scope.py` to 3,686 lines;
- among 68 v2 PASS states, the median task has 19 event results and three scope attempts;
- 35 of those 68 tasks required more than one review generation;
- recent product tasks show a median scope runtime near 101 seconds;
- ordinary `task_gate` and `atomic_evidence` both delegate to
  `scripts/evidence_validate.py` and repeat most task, candidate, result, event and review
  validation;
- the scope snapshot key fingerprints the whole worktree, every untracked file and deep
  peer-artifact authority, so unrelated evidence progress can invalidate a stable task;
- immutable-catalog overlays and legacy-shape compatibility have generated repeated
  governance work without advancing user-visible V8 paths.

The repository explicitly trusts the local OS, filesystem, checkout, Git, Python and
repository scripts. Ordinary task scope is not a hostile-builder proof. The active
peer-artifact reconstruction exceeds that threat model.

## 3. Goals

- Preserve exact closure, non-closure, allowlist and one-task ownership.
- Preserve dirty-baseline subtraction and reject unowned changes.
- Preserve targeted TDD and fresh task-required verification.
- Preserve an independent zero-finding review for ordinary HIGH tasks.
- Preserve all legal, lifecycle, deadline, official-fee, receivable, lineage, permission,
  migration, customer-decision and source-authority fail-closed rules.
- Preserve shared-file, migration and SQLite serialization.
- Preserve independent Foundation/Full/Final/Release acceptance and release-last.
- Reduce a stable task's formal close to one scope candidate, one review and one accept.
- Make the terminal state machine the only status authority.
- Stop creating compatibility tasks for work that has not started.

## 4. Non-goals

- No product behavior, schema, API, UI, legal rule or fee rule changes.
- No rewrite of atomic tasks or the approved V8 product design.
- No new LOW/MEDIUM risk inference engine. Existing V8 work remains HIGH unless a future
  separately approved design changes its authoritative classification.
- No new parallel controller or `taskctl v3`.
- No reinterpretation of historical terminal PASS.
- No weakening of peer-manifest isolation when an explicit concurrent atomic validation
  requests it.
- No migration of every historical evidence file into a new format.
- No catalog/decision-gate redesign in this cutover.

## 5. Cutover boundary

### 5.1 Historical and in-flight work

- Existing terminal PASS receipts remain read-only accepted history.
- Existing nonterminal tasks retain their original baseline and evidence prefix.
- A governance digest change uses the existing explicit governance-adoption operation; it
  must not recapture or absorb the original baseline.
- The two currently known in-flight tasks may close under their recorded legacy close
  protocol. They do not justify a new compatibility branch.
- No task that has not started may select legacy-adopt or any post-checkpoint compatibility
  profile.

### 5.2 Two-stage activation and new work

- The single governance implementation task owns both activation stages and remains
  nonterminal between them. Stage 1 installs and hash-binds the reviewed fast-close bytes,
  transitions that governance task to `STAGED_PENDING_CANARY`, and leaves the existing
  protocol as the repository default. It permits `fast-close-1` only for the exact named
  product canary task.
- The canary state records `acceptance_protocol: "fast-close-1"` and no other task may
  select that protocol during Stage 1.
- Canary PASS is a prerequisite for the Stage 2 default-switch receipt. Stage 2 changes
  only the default-selection marker to `fast-close-1`; the same still-nonterminal
  governance task writes that receipt, performs its final activation checks and then reaches
  terminal PASS. Stage 2 does not change executable bytes, recapture any baseline or create
  a second governance task.
- A canary failure leaves the old protocol as default and records rollback without changing
  historical evidence or product code; the governance task closes BLOCKED/FAIL rather than
  claiming PASS.
- After the Stage 2 receipt, every newly started eligible ordinary HIGH task records
  `acceptance_protocol: "fast-close-1"`. Existing states keep their recorded protocol.
  Foundation, Full, Final, Release, governance activation, hostile-builder and any task
  whose exact contract requires expanded or multi-axis close never inherit this ordinary
  default; they retain their explicitly contracted close protocol.
- New fast-close work begins only from an explicit integration checkpoint. The checkpoint
  is committed locally and is not pushed.
- A maximal safe wave registers all task owners before product edits begin. Changes owned
  by a disjoint registered peer are not treated as unowned drift.
- A path without exactly one registered owner remains outside dirt and fails closed if it
  changes.

Legacy validation remains available for historical release acceptance, but legacy start
and new compatibility growth are closed.

## 6. Fast-close protocol

### 6.1 Start

`taskctl start` continues to bind:

- exact task path and task ID;
- closure tags and HIGH risk;
- exact allowlist;
- controller and implementer identities;
- governance digest and selected modules;
- tracked and untracked task baseline;
- integration checkpoint and active owner registry.

It additionally binds the immutable `fast-close-1` protocol. A later downgrade or protocol
change fails closed.

### 6.2 Required work

The implementer records the task's exact RED, canonical GREEN/test and scoped lint or other
contract-required checks. Diagnostic reruns may exist, but the latest matching result for
each required step must itself be executed, log-bound and `rc=0`. An earlier success never
masks a later matching failure.

No manual `scope` result is required before review preparation.

### 6.3 Candidate preparation

One `prepare-review` action:

1. builds the baseline-subtracted allowlist patch;
2. verifies current outside paths against the integration checkpoint and active owner
   registry;
3. records one successful `scope` result and immutable scope key;
4. binds the task, patch, required result/log hashes, governance digest and review
   generation into one candidate fingerprint;
5. writes a compact review packet.

The fast scope key contains only facts relevant to this task:

- integration checkpoint;
- task metadata, baseline and governance hashes;
- current allowlist path/content facts;
- exact outside-dirt facts captured for the task;
- active owner-registry identity and the state identity of owners whose paths intersect the
  observed dirty-path inventory.

It does not hash unrelated peer outputs, reports, event files or artifact trees.

### 6.4 Independent review

- The implementer cannot review its own task.
- The reviewer checks the exact task contract, candidate patch, required result bindings
  and applicable domain rules.
- Approval remains one exact `APPROVED`, `P0: 0`, `P1: 0`, `P2: 0` report bound to the
  candidate fingerprint and patch hash.
- A read-only reviewer may inspect at most four disjoint candidates in one turn. Each task
  still receives its own lease, report, hashes and verdict. The reviewer edits no product,
  task or evidence authority other than its task-specific report.
- Any product or task change invalidates only the affected candidate.

### 6.5 Atomic accept

One `taskctl accept` action replaces the ordinary fast-path sequence
`scope_refresh → independent_review checkpoint → task_gate → atomic_evidence → close`.

The accept consumer performs one fail-closed pass over:

- task/state/protocol/governance binding;
- latest required result and log bindings;
- final scope patch and scope-key identity;
- independent reviewer identity, generation, candidate and zero-finding report;
- event-prefix integrity and absence of incomplete actions;
- active ownership and serialization requirements.

Immediately before PASS it recomputes the lightweight task-relevant scope key. A mismatch
invalidates the candidate and requires a new review. A match writes one immutable terminal
acceptance receipt containing the individual scope, review, task-gate and atomic-acceptance
claims and their hashes.

The old ordinary `task_gate` and non-peer `atomic_evidence` commands remain compatibility
readers for existing in-flight states only. Explicit peer-manifest atomic validation keeps
its unique manifest-membership, allowlist-overlap, ownership and isolated-validation checks.

## 7. One status authority

For `fast-close-1`:

- `state.json` plus its terminal acceptance receipt is authoritative.
- `summary.md` is generated from state and receipt data and is non-authoritative.
- The task Markdown status is an input contract/readiness label, not terminal acceptance.
- Release and progress reports read terminal state/receipt first and never infer completion
  from summary prose.

This prevents stale `NOT STARTED`, `READY_FOR_REVIEW` or rejected-review prose from
overriding a later terminal receipt.

## 8. Git and wave discipline

- Accepted work is checkpointed at bounded integration boundaries so Git is the normal
  provenance and baseline mechanism.
- No push occurs unless separately requested.
- A wave starts owners before edits, runs disjoint implementation concurrently, and
  serializes SQLite/shared verification.
- Reviewer work is read-only and may be batched; acceptance remains per task.
- A disconnect resumes from durable events and does not repeat accepted work.

## 9. Simplicity budget

This migration is one HIGH governance implementation task and one independent review.

It must satisfy all of the following:

- no new controller executable;
- no new compatibility task or legacy shape;
- no new risk-classification subsystem;
- no product task edits;
- no manual status-summary authority;
- the implementation task captures the complete repository inventory and line count of all
  active non-test governance execution code selected by the manifest or invoked by its
  consumers, including shell entry points; the accepted result must have a smaller total;
- governance execution logic may not be moved to a file outside that captured inventory to
  evade the reduction, and no new executable/module is permitted;
- duplicated validation removed or replaced by one canonical receipt;
- existing terminal PASS and release consumers remain accepted;
- negative tests prove stale scope, self-review, nonzero findings, missing results,
  governance drift, owner conflict and protocol downgrade all fail closed.

If the task cannot meet this budget, it stops for design reconsideration instead of
creating a follow-up governance task.

## 10. Verification and canary

The implementation task uses targeted TDD and proves:

1. old terminal PASS remains accepted;
2. an existing in-flight old-protocol fixture can adopt the new governance digest without
   baseline recapture;
3. a new fast task records one canonical scope and one terminal accept receipt;
4. task gate and atomic acceptance claims remain individually visible in that receipt;
5. unrelated peer evidence output does not invalidate a candidate;
6. an intersecting owner/path change does invalidate it;
7. tracked and untracked unowned drift fails;
8. stale or self-authored review fails;
9. missing/nonzero required results fail, including success followed by a later matching
   failure;
10. concurrent manifest peer checks remain fail closed;
11. Foundation/Full/Final/Release, governance activation, hostile-builder and explicitly
    expanded/multi-axis close profiles cannot select the ordinary fast close;
12. generated summary cannot override terminal state.

After focused tests, one real frozen HIGH product task is the canary. It must close with:

- exactly one successful final scope candidate;
- exactly one independent review generation unless the reviewer finds a real defect;
- exactly one terminal accept action;
- no compatibility task;
- no scope rebuild caused solely by unrelated peer evidence.

Only the Stage 2 default-switch receipt, written by the still-nonterminal governance task
after canary PASS, makes the new protocol the default for remaining eligible ordinary HIGH
V8 work. The governance task then performs its final checks and reaches terminal PASS.

## 11. Failure handling

- A real contract or domain ambiguity pauses only the affected product lane.
- A fast-close implementation defect blocks Stage 1 activation and leaves governance v2
  active.
- A canary failure leaves Stage 1 installed bytes inactive for general work, keeps the
  existing close protocol as default, records rollback without changing historical
  evidence or product code, and prevents the governance task from reaching PASS.
- A legacy edge case after activation is archived as evidence; it does not automatically
  authorize a compatibility implementation.
- Governance work ends after activation/canary PASS or a documented rollback. It may not
  recursively create another governance repair without an independently demonstrated P0/P1
  safety defect and explicit user approval.

## 12. Alternatives rejected

### Patch the existing compatibility system indefinitely

This has the lowest immediate design change but preserves the dominant cost and has already
created repeated governance tasks. Rejected.

### Add LOW/MEDIUM automated acceptance profiles now

Current V8 metadata resolves effectively to HIGH, so a new classifier would add complexity
without accelerating the active program. Rejected for this cutover.

### Replace taskctl with a new controller

This would duplicate migration, recovery and release compatibility and repeat the same
failure mode. Rejected.

## 13. Completion and post-change estimate

After activation and canary PASS, the coordinator must recompute:

- exact Foundation and full-catalog terminal PASS counts;
- remaining customer-dependent/full-only rows;
- critical-path serial depth;
- median fast-close active runtime and tool-event count from the canary and first wave;
- expected Foundation and full-program duration as a range, with customer-decision waiting
  shown separately.

No duration claim may be made from the old close-cost average after the new protocol is
active.
