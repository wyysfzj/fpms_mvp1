# FPMS Governance Reset Implementation Plan

> **For agentic workers:** Use the one-active-task-per-agent and minimal-context dispatch portion of `superpowers:subagent-driven-development`; this repository's frozen contracts override that generic skill's worktree, commit, extra-review, final-branch, and integration defaults. Use task-scoped TDD and atomic evidence exactly as each task prescribes. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the monolithic repository governance/evidence workflow with the approved thin governance kernel and `taskctl`, while preserving every existing fail-closed domain, scope, evidence, compatibility, and activation guarantee.

**Architecture:** Execute exactly three pre-materialized HIGH tasks in strict dependency order. GVR-1 builds inactive governance candidates, GVR-2 builds inactive Evidence v2 tooling, and GVR-3 performs the only compatibility/activation transition; no product lane resumes before GVR-3 state PASS.

**Tech Stack:** Markdown governance modules, Python 3 standard library, POSIX shell adapters, Git baseline-subtracted scope, unittest, Ruff, repository Evidence 1.1 and task/atomic gates.

---

## Frozen authority

| Artifact | SHA-256 |
| --- | --- |
| `docs/superpowers/specs/2026-07-16-fpms-governance-reset-design.md` | `84a74f1a3570dfc418178d2295e5a9a2e57e9aedda78472137d05081c2b8bc29` |
| `tasks/repo/REPO-GOVERNANCE-RESET-MODULES-20260716-01.md` | `e92d7a8e42a47d2e58c0986318ac0b40913bd24e04e5e58c4b557b9cbe75d6b9` |
| `tasks/repo/REPO-GOVERNANCE-RESET-TASKCTL-20260716-01.md` | `3a18154b8b3783b30b09be9d433d3ab03b2441c8099897d45732df833af15b4c` |
| `tasks/repo/REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01.md` | `9f23cc60913f87484ef6ed78c21a5e44e34eb82319f736623c2079e998750a7b` |

User freeze approval was given on 2026-07-17. Governance and tooling design axes both
approved Revision 4 with P0/P1/P2 all zero. The three task files pass the atomic task-shape
check. These bytes are the implementation authority; do not reinterpret or rematerialize
their closure, non-closure, allowlist, commands, evidence, review, or gate contracts.

## Story shape and operating boundary

- `shared_file_density`: high, but serialized by the three-task dependency chain.
- `prereq_dependency_density`: high; GVR-2 requires accepted GVR-1, and GVR-3 requires both.
- `be_fe_coupling`: none; this is repository governance/evidence tooling only.
- `evidence_cost`: high because the work changes authoritative governance and acceptance.
- `chosen_runbook`: `P0-prereq-heavy-story` for all three tasks.
- Run in the current checkout because the approved contracts require preservation and
  subtraction of its dirty baseline. Do not create another worktree.
- Do not commit, push, reset, clean, stash, discard, run product full tests, Playwright,
  frontend builds, migrations, SQLite product tests, or the release gate.
- One implementer owns one exact task at a time. Reviewers never edit reviewed source/task
  bytes. No task starts before its predecessor has a durable accepted PASS. Run only the
  frozen per-task independent review: one checksum-bound reviewer for GVR-1/GVR-2 and the
  exact two distinct axes for GVR-3; do not add generic extra or final-branch reviews.

### Task 1: GVR-1 — Governance modules and inactive candidates

**Files:** Exactly the Allowed Files in
`tasks/repo/REPO-GOVERNANCE-RESET-MODULES-20260716-01.md`.

- [ ] Verify the frozen spec/task hashes, current dirty baseline, dependency readiness, and
  exact absence of another owner.
- [ ] Load only Karpathy discipline, task-scoped TDD, atomic evidence, and verification;
  do not reopen source-document or governance-design analysis.
- [ ] Execute numbered Verification Commands 1–5 verbatim, including one genuine RED and
  the minimum GREEN implementation inside the allowlist.
- [ ] Execute the task's exact Evidence 1.1 content-finalization and scope/hash sequence.
- [ ] Obtain one independent HIGH governance review of the final task/summary/patch bytes;
  require reviewer-owned checksum binding and zero P0/P1/P2.
- [ ] Execute canonical close, the post-close checksum recheck, and final atomic validation
  verbatim. Record durable PASS under
  `artifacts/REPO-GOVERNANCE-RESET-MODULES-20260716-01/**`.
- [ ] Confirm root `AGENTS.md`, active manifest, adapters/consumers, products, Goal state,
  and every non-closure path remain unchanged.

### Task 2: GVR-2 — Inactive taskctl and Evidence v2 core

**Files:** Exactly the Allowed Files in
`tasks/repo/REPO-GOVERNANCE-RESET-TASKCTL-20260716-01.md`.

- [ ] Require GVR-1 durable accepted PASS and recheck its candidate hashes without editing
  them; stop only this lane on mismatch.
- [ ] Execute the task's exact Evidence 1.1 initialization and contract-complete RED.
- [ ] Implement the smallest public-interface/state/event/lease/review/adopt/scope behavior
  needed to make the frozen fault matrix GREEN; do not activate it or edit adapters.
- [ ] Run every exact test, format-check, lint, compile, diff, scope, and content-finalization
  command in the task contract; no substitute argv.
- [ ] Obtain one independent HIGH evidence/tooling review of final task/summary/patch bytes;
  require reviewer-owned checksum binding and zero P0/P1/P2.
- [ ] Execute canonical Evidence 1.1 close, post-close checksum recheck, and final atomic
  validation verbatim. Record durable PASS under
  `artifacts/REPO-GOVERNANCE-RESET-TASKCTL-20260716-01/**`.
- [ ] Confirm active governance, legacy adapters/consumers, products, and Goal state remain
  unchanged.

### Task 3: GVR-3 — Compatibility, dual review, and atomic activation

**Files:** Exactly the Allowed Files in
`tasks/repo/REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01.md`.

- [ ] Require durable accepted PASS for GVR-1 and GVR-2, exact dependency hashes, no product
  owner, and no shared/SQLite/migration verification.
- [ ] Run Evidence 1.1 init and genuine RED before any source edit, then run the exact
  bootstrap `taskctl start` to adopt the non-PASS bundle without recapturing baseline.
- [ ] Implement only the named adapters/consumers/legacy ledger/review-bound frozen-v1
  runner/activation tests; all later acceptance facts must be v2 events.
- [ ] Run the exact GREEN, shell, Ruff, compile, frozen-v1, final summary/scope, and virtual
  `prepare-review` commands from the task contract.
- [ ] Obtain distinct governance and tooling reviewer leases and two independent APPROVED
  zero-finding reports bound to the same candidate fingerprint/patch/governance triple.
- [ ] Run exact root-first/manifest-second `activate`; require `GOVERNANCE_STAGED`, never
  PASS, until the only v2 `close` completes all consumers.
- [ ] Require `state.json: PASS` as the final receipt and verify actual installed bytes equal
  the dual-reviewed candidate. Record evidence under
  `artifacts/REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01/**`.
- [ ] Only after this durable PASS may the controller report Governance Reset complete and
  make the separate decision to resume the product Goal; this plan itself starts no product task.

## Completion gate

- [ ] All three task IDs have independent evidence-backed PASS in dependency order.
- [ ] GVR-3 has two distinct approved axes with P0/P1/P2 zero and an identical triple.
- [ ] Active root/manifest bytes equal the reviewed candidate; root is at most 300 lines.
- [ ] Legacy PASS ledger and v2 state branches remain mutually exclusive and fail closed.
- [ ] No outside-allowlist or non-closure change was absorbed; dirty baseline was preserved.
- [ ] No product/release command, commit, push, reset, clean, stash, or discard occurred.
