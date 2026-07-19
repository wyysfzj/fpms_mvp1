# FPMS Governance Fast-Close Cutover Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` to execute this plan. Use
> `superpowers:test-driven-development` for behavior changes,
> `atomic-evidence-gates` for the two atomic task closures, and
> `superpowers:verification-before-completion` before any PASS or completion claim.
> Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the repeated ordinary-HIGH close chain with one canonical scope
candidate, one independent review and one atomic accept, while preserving every FPMS
legal/fee/lineage/migration fail-closed rule, historical acceptance, explicit concurrent
peer validation and release-last.

**Architecture:** Extend the existing `TaskController`; do not create another controller
or executable. Keep current v2 as the sole authority while candidate code is tested and a
real product task closes under v2. Evaluate that frozen canary non-authoritatively through
the candidate fast path, then use the current crash-safe governance activation mechanism to
install the reviewed kernel/module/manifest candidate. Newly started eligible tasks select
`fast-close-1`; historical and already-started tasks retain their recorded protocol.

**Tech Stack:** Python 3.11 standard library, Bash, Git, unittest, Ruff, the existing FPMS
`taskctl`, evidence consumers and atomic evidence gate.

---

- Governance task:
  `REPO-GOVERNANCE-FAST-CLOSE-CUTOVER-20260719-01`
- Current-v2 product canary:
  `FPMS-V8-CNIPA-ANNUITY-RATE-CANDIDATE-20260715-01`
- Approved design:
  `docs/superpowers/specs/2026-07-19-fpms-governance-fast-close-cutover-design.md`
- Plan status: `APPROVED — independent review P0: 0 / P1: 0`
- Runtime lane: High for implementation and independent review. Escalate to Ultra only for
  a newly exposed semantic/authority/architecture contradiction; do not silently switch.
- Git: local commits only; never push, reset, clean, stash or discard.

## 1. Frozen execution topology

This plan creates exactly one new repository governance implementation task. The canary is
an already-materialized V8 product task, not another governance task.

| Lane | Atomic owner | Writable scope | Serialization |
| --- | --- | --- | --- |
| Governance candidate | one `fast-close-high` worker | exact governance task allowlist | exclusive ownership of governance scripts/tests |
| Governance review | one independent High reviewer | governance task review report only | starts after candidate bytes and prospective governance diff freeze |
| Product canary | its recorded `lead` implementer | exact existing canary allowlist | runs after governance task start but before governance edits; all backend pytest uses the SQLite queue |
| Canary review | one independent High reviewer | canary review report only | no self-approval |
| Activation | recorded governance controller | exact reviewed candidate + governance state | globally serialized; no product start during staged activation |

No lane may edit the other lane's source, test, task or evidence authority. The existing
`FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01` lane remains paused and outside both
allowlists during the cutover. The two historical tasks recorded with `implementer=lead`
must not execute concurrently.

The chronological execution order is **A → E → B → C → D → F → G**. Phase E is written
later only to keep the canary runbook together. It runs immediately after the governance
task is started and before any governance script or candidate byte is edited. This ensures
the authoritative canary is closed by the unchanged, already-terminal current-v2
controller; candidate fast-close code is used only for the later non-authoritative shadow.

## 2. Why this canary is exact

`FPMS-V8-CNIPA-ANNUITY-RATE-CANDIDATE-20260715-01` is selected instead of creating a
synthetic task:

- its Ultra-frozen contract defines exact source URL/date/hash rules, exact canonical JSON,
  three exact rate rows and byte-identical tier strings;
- its only hard dependency,
  `FPMS-V8-OFFICIAL-RATE-BOOK-CARRIER-20260712-01`, is accepted by the current release
  consumer;
- it is already `IMPLEMENTING` under current v2, has no review candidate or review
  generation, and only its task metadata currently differs;
- its source/data/test paths do not intersect either governance files or the other in-flight
  V8 lane;
- it exercises official-fee/source fail-closed behavior without authorizing activation,
  selection, receivable truth or customer fallback.

The canary may not weaken or reinterpret that contract. A genuine source or contract defect
stops the canary and therefore stops activation. No compatibility task may be created.

## 3. Governance task contract and allowlist

Before any governance implementation edit, materialize:

`tasks/repo/REPO-GOVERNANCE-FAST-CLOSE-CUTOVER-20260719-01.md`

The task has one closure slice: implement, shadow-prove and activate the approved
`fast-close-1` cutover. Its explicit non-closure is all product behavior, any new risk
classifier, new controller/executable/module, compatibility profile, historical evidence
rewrite, catalog redesign or release execution.

Its exact writable allowlist is:

- `tasks/repo/REPO-GOVERNANCE-FAST-CLOSE-CUTOVER-20260719-01.md`
- `AGENTS.md`
- `docs/agents/execution.md`
- `docs/agents/evidence.md`
- `docs/agents/manifest.json`
- `scripts/taskctl`
- `scripts/evidence_scope.py`
- `scripts/evidence_validate.py`
- `scripts/release_gate.sh`
- `scripts/governance_validate.py`
- `scripts/tests/test_taskctl.py`
- `scripts/tests/test_evidence_scope_snapshot_cache.py`
- `scripts/tests/test_evidence_scope_v2.py`
- `scripts/tests/test_governance_reset_consumers.py`
- `scripts/tests/test_atomic_evidence_validate.py`
- `scripts/tests/test_governance_reset_activation.py`
- `scripts/tests/test_governance_validate.py`
- `artifacts/REPO-GOVERNANCE-FAST-CLOSE-CUTOVER-20260719-01/**`

`scripts/task_validate.sh`, `scripts/atomic_evidence_validate.py`,
`scripts/evidence_task.py` and `scripts/frozen_v1_acceptance.py` are read-only regression
inputs. `scripts/scope_protocol_v3.py` is also a read-only active execution input, and
`docs/agents/scope_protocol_v3.json` is its read-only registry input. If implementation
proves that one must change, stop and return to the approved design instead of widening the
task by convenience.

The task file must freeze, before `taskctl start`, the path, line count and SHA-256 of every
active non-test governance execution file selected by the manifest or invoked by its
consumers, including shell entry points. The minimum inventory is:

- `scripts/taskctl`
- `scripts/evidence_scope.py`
- `scripts/scope_protocol_v3.py`
- `scripts/evidence_validate.py`
- `scripts/atomic_evidence_validate.py`
- `scripts/frozen_v1_acceptance.py`
- `scripts/evidence_task.py`
- `scripts/evidence_init.sh`
- `scripts/evidence_run.sh`
- `scripts/task_validate.sh`
- `scripts/release_gate.sh`
- `scripts/governance_validate.py`

The task additionally hash-binds `docs/agents/scope_protocol_v3.json`. The same code
inventory is measured at close. Its total active non-test line count must be lower, no
execution logic may move outside it, and no new executable/module may appear.

## 4. Phase A — materialize and start the one governance task

### Step A1: Reconcile durable state and conflict map

- [ ] Run:

```bash
git status --short
./scripts/taskctl FPMS-V8-CNIPA-ANNUITY-RATE-CANDIDATE-20260715-01 doctor
./scripts/taskctl FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01 doctor
```

- [ ] Confirm the canary remains `IMPLEMENTING`, has no candidate/review, and the other
  in-flight lane does not intersect either task's allowlist.
- [ ] Confirm no process holds a governance task lock and no other active owner lists the
  governance allowlist.
- [ ] Capture the current tracked/untracked dirty baseline; never absorb unrelated dirt.

### Step A2: Freeze the implementation task

- [ ] Create the exact task file above with risk `HIGH`, closure tag `governance`, the
  approved design hash, full allowlist, complete line-count/hash inventory, RED/GREEN
  commands, canary ID and activation prerequisites.
- [ ] Independently read-review the task file against the approved design before starting.
  This is a contract review, not a second governance implementation task.
- [ ] Start it under current terminal v2 authority:

```bash
TASKCTL_ACTOR=fast-close-controller \
TASKCTL_IMPLEMENTER=fast-close-high \
./scripts/taskctl REPO-GOVERNANCE-FAST-CLOSE-CUTOVER-20260719-01 start \
  --task-file tasks/repo/REPO-GOVERNANCE-FAST-CLOSE-CUTOVER-20260719-01.md
```

- [ ] Record the resulting governance digest, selected modules, checkpoint and baseline
  hashes. Do not edit `AGENTS.md` or `docs/agents/*.md` live yet.

## 5. Phase B — RED tests before implementation

### Step B1: Add focused failing tests to existing test modules

- [ ] In `scripts/tests/test_taskctl.py`, add `FastCloseCutoverTests` proving:
  - current manifest starts retain v2 behavior;
  - only terminally activated candidate governance selects `fast-close-1`;
  - explicit expanded profiles cannot select it;
  - `prepare-review` creates one scope result/candidate without a prior manual scope;
  - latest matching lint/test must itself be executed, log-bound and zero;
  - self/stale/nonzero review fails;
  - `accept` writes PASS last and one receipt with separate scope/review/task-gate/atomic
    claims;
  - stale scope, governance drift, owner conflict and protocol downgrade fail;
  - a crash resumes from durable state without repeating accepted effects;
  - fixed governance activation can stage candidate modules, require canary/shadow and
    install reviewed bytes through the current fail-closed activation journal;
  - an existing in-flight old-protocol task adopts the activated governance digest without
    recapturing or changing any baseline identity.
- [ ] In `scripts/tests/test_evidence_scope_snapshot_cache.py`, add
  `FastCloseScopeKeyTests` proving unrelated peer outputs/reports/events do not change the
  fast key, while task bytes, outside dirt, intersecting-owner state and owner conflict do.
- [ ] In `scripts/tests/test_governance_reset_consumers.py`, add
  `FastCloseConsumerTests` proving historical terminal v1/v2 remains accepted, fast terminal
  receipts validate, old task/atomic entry points reject fast in-progress acceptance, and
  generated summary prose cannot override terminal state.
- [ ] Extend `GovernanceActivationTests` and `GovernanceValidateTests` for the new manifest
  version/default marker, dynamic activation-task validation and fail-closed staged
  activation.
- [ ] Extend only the existing peer-manifest tests needed to prove explicit atomic peer
  membership/overlap/isolation behavior is unchanged.

### Step B2: Preserve the expected RED

- [ ] Run the new test classes through the governance task controller:

```bash
TASKCTL_ACTOR=fast-close-controller \
./scripts/taskctl REPO-GOVERNANCE-FAST-CLOSE-CUTOVER-20260719-01 record red -- \
  backend/.venv/bin/python -m unittest -v \
  scripts.tests.test_taskctl.FastCloseCutoverTests \
  scripts.tests.test_evidence_scope_snapshot_cache.FastCloseScopeKeyTests \
  scripts.tests.test_governance_reset_consumers.FastCloseConsumerTests
```

- [ ] Require an executed nonzero result caused by missing `fast-close-1`, `accept`,
  `shadow-canary` and candidate activation behavior—not import, syntax, fixture or
  infrastructure failure.

## 6. Phase C — minimum implementation

### Step C1: Make protocol selection explicit and bounded

Files:

- Modify: `scripts/taskctl`
- Modify: `docs/agents/manifest.json` only in the staged candidate tree
- Test: `scripts/tests/test_taskctl.py`

- [ ] Extend manifest validation with one bounded transition:
  - current terminal `2.0.0` has no fast default and starts old protocol;
  - reviewed candidate version records the exact ordinary default `fast-close-1`;
  - newly started eligible ordinary HIGH state binds that protocol immutably;
  - existing state without the field retains v2;
  - Foundation-close, Full, Final, Release, governance activation, hostile-builder and
    explicit expanded/multi-axis profiles reject the ordinary default.
- [ ] Do not require edits to the 283 already-materialized V8 task files. The reviewed
  candidate manifest freezes `fast-close-1` as the default for a newly started
  approved-manifest HIGH task and one exact `expanded_acceptance_task_ids` set for every
  Foundation-close, Full, Final, Release, governance activation, hostile-builder and
  contractually multi-axis task. Existing unstarted ordinary V8 tasks select the default
  without task-file mutation. Newly created tasks may declare an exact profile, but a
  contradiction with the manifest set fails closed.
- [ ] Test one existing unstarted ordinary V8 fixture and one exact excluded ID. Never
  infer selection from task-name substrings, broad closure prose or a missing new field.
- [ ] Close legacy start and new compatibility-profile selection after activation.
- [ ] Run only `FastCloseCutoverTests` until this slice is green.

### Step C2: Replace whole-worktree scope fingerprinting for fast tasks

Files:

- Modify: `scripts/evidence_scope.py`
- Modify: `scripts/taskctl`
- Test: `scripts/tests/test_evidence_scope_snapshot_cache.py`
- Regression: `scripts/tests/test_evidence_scope_v2.py`

- [ ] Reuse existing baseline capture and patch construction.
- [ ] Build the fast scope key only from checkpoint, task metadata/baseline/governance,
  current allowlist facts, exact outside dirt, owner-registry identity and state identities
  of owners intersecting observed dirty paths.
- [ ] Exclude unrelated peer outputs, review reports, events and artifact trees.
- [ ] Keep unowned tracked/untracked drift, multiple ownership, mismatched owner baseline
  and intersecting owner mutation fail closed.
- [ ] Leave historical v2 replay and explicit peer-manifest isolation semantics intact.
- [ ] Make fast `prepare-review` create the one canonical scope result and immutable review
  packet internally; remove the ordinary fast-path manual-scope prerequisite.

### Step C3: Add one atomic accept in the existing controller

Files:

- Modify: `scripts/taskctl`
- Modify: `scripts/evidence_validate.py`
- Test: `scripts/tests/test_taskctl.py`
- Test: `scripts/tests/test_governance_reset_consumers.py`

- [ ] Add `taskctl TASK accept`; do not add a script or controller.
- [ ] In one lock/CAS/event pass validate:
  - task/state/protocol/governance;
  - latest exact required results and log hashes;
  - candidate patch and lightweight final scope key;
  - reviewer identity/generation/candidate and exact zero findings;
  - event-prefix integrity and no incomplete action;
  - current owner/serialization authority.
- [ ] On success, write one immutable terminal receipt with individually hashed
  `scope`, `independent_review`, `task_gate` and `atomic_evidence` claims, then set PASS last.
- [ ] On failure, write no PASS; candidate-affecting drift returns to implementation and
  requires a new candidate/review.
- [ ] Keep ordinary old `close` only for already-started old-protocol states. Keep explicit
  peer-manifest atomic validation unchanged.
- [ ] Generate `summary.md` from state/receipt for fast tasks and remove it from acceptance
  authority.

### Step C4: Add non-authoritative shadow canary evaluation

Files:

- Modify: `scripts/taskctl`
- Modify: `scripts/evidence_validate.py`
- Test: `scripts/tests/test_taskctl.py`
- Test: `scripts/tests/test_governance_reset_consumers.py`

- [ ] Add:

```text
taskctl GOVERNANCE-TASK shadow-canary --canary-task PRODUCT-TASK
```

- [ ] Restrict it to the fixed governance task and exact reviewed canary ID.
- [ ] Read the canary terminal bundle without editing its task/state/evidence/receipt.
- [ ] Require terminal current-v2 PASS and recompute the fast candidate/accept claims from
  the frozen bundle.
- [ ] Write one non-authoritative shadow receipt only under the governance artifact,
  including canary terminal ordinal, task/candidate/patch/governance hashes, simulated
  claim hashes, event count and elapsed close metrics.
- [ ] A mismatch or missing current-v2 fact fails and blocks activation.

### Step C5: Generalize activation without adding a controller

Files:

- Modify: `scripts/taskctl`
- Modify: `scripts/governance_validate.py`
- Modify: `scripts/release_gate.sh`
- Test: `scripts/tests/test_taskctl.py`
- Test: `scripts/tests/test_governance_reset_activation.py`
- Test: `scripts/tests/test_governance_validate.py`

- [ ] Replace exact `GVR3_ID` assumptions only where required by a fixed reviewed
  activation-task contract. Preserve historical GVR3 release validation.
- [ ] Stage candidate files at:

```text
artifacts/REPO-GOVERNANCE-FAST-CLOSE-CUTOVER-20260719-01/candidate/governance/
```

  with exact prospective destinations for `AGENTS.md`, `docs/agents/execution.md`,
  `docs/agents/evidence.md` and `docs/agents/manifest.json`.
- [ ] Bind all candidate governance bytes, prospective diff, source-script patch, required
  results, canary ID and simplicity inventory into the reviewed candidate fingerprint.
- [ ] Keep live v2 governance unchanged until final activation.
- [ ] Reuse the existing crash-safe root-first activation journal: while candidate files
  are staged but activation state is nonterminal, ordinary starts fail closed; retry
  completes from durable state without accepting a product under staged authority.
- [ ] Remove the release gate's hard-coded activation-task ID. It must read the active
  manifest, then require that exact task's valid terminal activation receipt.

### Step C6: Delete duplication and enforce the simplicity budget

- [ ] Remove dead ordinary-fast calls to repeated scope refresh, task-gate scan and
  non-peer atomic scan instead of wrapping them.
- [ ] Remove open-ended start selection for compatibility shapes not already recorded in a
  nonterminal state.
- [ ] Do not delete readers needed for historical terminal release validation or the two
  recorded old-protocol in-flight tasks.
- [ ] Run the simplicity test that parses the frozen task-file inventory and proves:
  - same inventory paths;
  - lower total active non-test execution line count;
  - no new executable/module;
  - no relocation outside inventory.
- [ ] If total lines do not decrease, stop; do not create a follow-up governance task.

## 7. Phase D — focused GREEN and independent governance review

### Step D1: Run focused governance GREEN

- [ ] Record one complete canonical GREEN:

```bash
TASKCTL_ACTOR=fast-close-controller \
./scripts/taskctl REPO-GOVERNANCE-FAST-CLOSE-CUTOVER-20260719-01 record test -- \
  backend/.venv/bin/python -m unittest -v \
  scripts.tests.test_taskctl.FastCloseCutoverTests \
  scripts.tests.test_evidence_scope_snapshot_cache.FastCloseScopeKeyTests \
  scripts.tests.test_governance_reset_consumers.FastCloseConsumerTests \
  scripts.tests.test_governance_reset_activation.GovernanceActivationTests \
  scripts.tests.test_governance_validate.GovernanceValidateTests
```

- [ ] The canonical GREEN includes the old-protocol governance-adoption regression and
  proves byte-identical baseline identity before and after adoption.
- [ ] Run the exact retained peer-manifest regression methods from
  `AtomicEvidenceValidateTests`.
- [ ] Run the exact retained historical/current-v2 regression methods named in the design,
  not the whole repository or product suite.
- [ ] Record scoped compile, Ruff and shell checks:

```bash
backend/.venv/bin/python -m py_compile \
  scripts/taskctl scripts/evidence_scope.py scripts/evidence_validate.py \
  scripts/governance_validate.py
ruff check \
  scripts/evidence_scope.py scripts/evidence_validate.py scripts/governance_validate.py \
  scripts/tests/test_taskctl.py scripts/tests/test_evidence_scope_snapshot_cache.py \
  scripts/tests/test_evidence_scope_v2.py \
  scripts/tests/test_governance_reset_consumers.py \
  scripts/tests/test_atomic_evidence_validate.py \
  scripts/tests/test_governance_reset_activation.py \
  scripts/tests/test_governance_validate.py
bash -n scripts/release_gate.sh
```

- [ ] Run `git diff --check` only on the governance task allowlist.
- [ ] Run the current-v2 canonical scope once for this expanded governance activation task:

```bash
TASKCTL_ACTOR=fast-close-controller \
./scripts/taskctl REPO-GOVERNANCE-FAST-CLOSE-CUTOVER-20260719-01 record scope -- \
  python3 scripts/evidence_scope.py finalize \
  REPO-GOVERNANCE-FAST-CLOSE-CUTOVER-20260719-01
```

### Step D2: Freeze the prospective governance candidate

- [ ] Render the candidate kernel/modules/manifest into the governance artifact; do not
  change live governance files.
- [ ] Candidate manifest version/default must name this activation task and
  `fast-close-1`.
- [ ] Run special `prepare-review` with the candidate kernel/manifest:

```bash
TASKCTL_ACTOR=fast-close-controller \
./scripts/taskctl REPO-GOVERNANCE-FAST-CLOSE-CUTOVER-20260719-01 prepare-review \
  --kernel artifacts/REPO-GOVERNANCE-FAST-CLOSE-CUTOVER-20260719-01/candidate/governance/AGENTS.md \
  --manifest artifacts/REPO-GOVERNANCE-FAST-CLOSE-CUTOVER-20260719-01/candidate/governance/docs/agents/manifest.json
```

  It must bind the prospective installed diff, all module hashes, source patch, required
  results and simplicity result.
- [ ] Confirm no candidate-affecting edit occurs after preparation.

### Step D3: Independent governance review

- [ ] Lease one independent reviewer who is neither controller nor implementer:

```bash
TASKCTL_ACTOR=fast-close-controller \
./scripts/taskctl REPO-GOVERNANCE-FAST-CLOSE-CUTOVER-20260719-01 review lease independent \
  --reviewer fast-close-independent-r1
```
- [ ] Reviewer checks the exact approved design, prospective governance diff, script/test
  patch, negative tests, historical reader preservation, peer-manifest preservation and
  net code reduction.
- [ ] Require exactly one final `Verdict: APPROVED`, `P0: 0`, `P1: 0`, `P2: 0`, with
  current-v2 headers `Reviewed-Candidate-Fingerprint`, `Reviewed-Patch-SHA256`,
  `Reviewed-Governance-Digest` and the lease-bound `Reviewer-ID`.
- [ ] Submit the task-local report:

```bash
TASKCTL_ACTOR=fast-close-independent-r1 \
./scripts/taskctl REPO-GOVERNANCE-FAST-CLOSE-CUTOVER-20260719-01 review submit independent \
  --report artifacts/REPO-GOVERNANCE-FAST-CLOSE-CUTOVER-20260719-01/review/independent_review.md
```

- [ ] A finding returns only this governance lane to implementation; after a patch,
  regenerate candidate and review. Do not create a compatibility task.

## 8. Phase E — complete the real current-v2 product canary

Execute this phase immediately after Phase A and before Phase B. The governance task exists
and has captured its baseline, but no governance source, candidate or live rule byte has
changed. The live manifest and controller are therefore the already-terminal current v2,
and the canary retains its already-recorded old protocol and baseline.

### Step E1: Implement the exact frozen canary

Writable files remain exactly:

- `tasks/postdemo/v8/FPMS-V8-CNIPA-ANNUITY-RATE-CANDIDATE-20260715-01.md`
- `backend/app/modules/fees/cnipa_annuity_rate_candidate.py`
- `backend/app/modules/fees/data/cnipa_payment_guide_20260330_annuity_rates.json`
- `backend/tests/test_v8_cnipa_annuity_rate_candidate.py`
- `artifacts/FPMS-V8-CNIPA-ANNUITY-RATE-CANDIDATE-20260715-01/**`

- [ ] Reconcile its existing `IMPLEMENTING` state; do not restart or recapture baseline.
- [ ] Verify the accepted carrier dependency with the current release consumer.
- [ ] Run the exact public RED through the serialized backend-test action:

```bash
./scripts/taskctl FPMS-V8-CNIPA-ANNUITY-RATE-CANDIDATE-20260715-01 \
  backend-test red -- -q tests/test_v8_cnipa_annuity_rate_candidate.py
```

- [ ] Implement only the exact inactive candidate, strict parser, exact replay and
  caller-owned transaction behavior in the frozen task.
- [ ] Run the canonical GREEN through the serialized backend-test action:

```bash
./scripts/taskctl FPMS-V8-CNIPA-ANNUITY-RATE-CANDIDATE-20260715-01 \
  backend-test test -- -q tests/test_v8_cnipa_annuity_rate_candidate.py
```

- [ ] Run task-scoped Ruff, format-check and `git diff --check`; do not run broad backend,
  migration, seed, fee or release suites.

### Step E2: Close it normally under current v2

- [ ] Produce its current-v2 summary, record the canonical scope once, then prepare the
  candidate:

```bash
./scripts/taskctl FPMS-V8-CNIPA-ANNUITY-RATE-CANDIDATE-20260715-01 record scope -- \
  python3 scripts/evidence_scope.py finalize \
  FPMS-V8-CNIPA-ANNUITY-RATE-CANDIDATE-20260715-01
./scripts/taskctl FPMS-V8-CNIPA-ANNUITY-RATE-CANDIDATE-20260715-01 prepare-review
```

- [ ] Obtain one independent domain/source review. The implementer cannot approve it.
- [ ] Require one review generation unless the reviewer identifies a genuine defect.
- [ ] Lease and submit its independent report through `taskctl`, then run its current-v2
  close:

```bash
./scripts/taskctl FPMS-V8-CNIPA-ANNUITY-RATE-CANDIDATE-20260715-01 review lease independent \
  --reviewer cnipa-annuity-candidate-independent-r1
TASKCTL_ACTOR=cnipa-annuity-candidate-independent-r1 \
./scripts/taskctl FPMS-V8-CNIPA-ANNUITY-RATE-CANDIDATE-20260715-01 review submit independent \
  --report artifacts/FPMS-V8-CNIPA-ANNUITY-RATE-CANDIDATE-20260715-01/review/independent_review.md
./scripts/taskctl FPMS-V8-CNIPA-ANNUITY-RATE-CANDIDATE-20260715-01 close
```

- [ ] Require terminal PASS and no compatibility task.

## 9. Phase F — shadow proof and atomic activation

### Step F1: Evaluate the frozen canary without authority

- [ ] Run:

```bash
TASKCTL_ACTOR=fast-close-controller \
./scripts/taskctl REPO-GOVERNANCE-FAST-CLOSE-CUTOVER-20260719-01 \
  shadow-canary \
  --canary-task FPMS-V8-CNIPA-ANNUITY-RATE-CANDIDATE-20260715-01
```

- [ ] Verify the canary state, evidence and terminal receipt bytes are unchanged.
- [ ] Require exactly one successful matching shadow receipt and no scope rebuild caused
  solely by unrelated peer evidence.

### Step F2: Activate the reviewed candidate

- [ ] Revalidate candidate hashes, review, focused GREEN, simplicity budget, current-v2
  canary PASS and matching shadow receipt.
- [ ] Run the fixed governance activation command against the staged candidate kernel and
  manifest:

```bash
TASKCTL_ACTOR=fast-close-controller \
./scripts/taskctl REPO-GOVERNANCE-FAST-CLOSE-CUTOVER-20260719-01 activate \
  --kernel artifacts/REPO-GOVERNANCE-FAST-CLOSE-CUTOVER-20260719-01/candidate/governance/AGENTS.md \
  --manifest artifacts/REPO-GOVERNANCE-FAST-CLOSE-CUTOVER-20260719-01/candidate/governance/docs/agents/manifest.json
```

- [ ] During any nonterminal root-first stage, confirm new product starts fail closed.
- [ ] Require intermediate state `GOVERNANCE_STAGED`, then finish the current-v2
  activation acceptance chain:

```bash
TASKCTL_ACTOR=fast-close-controller \
./scripts/taskctl REPO-GOVERNANCE-FAST-CLOSE-CUTOVER-20260719-01 close
```

- [ ] Require terminal governance PASS with activation and terminal receipts bound to
  every installed governance input. A failure leaves/reconciles current v2 and cannot claim
  PASS.
- [ ] Freshly run:

```bash
python3 scripts/evidence_validate.py \
  REPO-GOVERNANCE-FAST-CLOSE-CUTOVER-20260719-01 \
  --acceptance-mode release
```

- [ ] Do not run the repository release gate or any broad product suite here.

## 10. Phase G — checkpoint, prove selection and resume V8

### Step G1: Create a bounded local integration checkpoint

- [ ] Stage only paths proven to belong to the terminal canary or terminal governance task.
  Do not stage the paused DE seam, unowned changes or unrelated user work.
- [ ] Create local commits, with canary and governance separated when their scoped diffs
  remain independently attributable.
- [ ] Do not push.
- [ ] Record the resulting commit SHA as the integration checkpoint and preserve exact
  remaining outside dirt.

### Step G2: Prove the first real fast start

- [ ] Build the next maximal conflict-free wave from the existing approved V8 manifest.
- [ ] Start each eligible ordinary HIGH task only after the checkpoint and owner registry
  are frozen.
- [ ] Confirm state records `acceptance_protocol: fast-close-1`.
- [ ] Excluded profiles must still select their expanded protocol.
- [ ] Do not repeat design, plan, materialization or source review for contract-frozen rows.

### Step G3: Recompute remaining duration

- [ ] Recount terminal PASS from state/receipt authority:
  - Foundation completed/remaining;
  - full catalog completed/remaining;
  - customer-dependent/full-only rows separately;
  - critical-path serial depth.
- [ ] Measure from shadow canary plus the first completed fast wave:
  - median active implementation time;
  - prepare-review time;
  - accept time;
  - total durable event count;
  - review generations and real defects.
- [ ] Report Foundation and full-program remaining duration as ranges. Show customer
  decision waiting separately and do not reuse the old close-cost average.
- [ ] Resume the existing V8 Goal under High using maximal non-conflicting waves. Pause for
  manual Ultra only if a concrete high-risk semantic/authority/architecture ambiguity
  appears.

## 11. Completion gates

The cutover is complete only when all are true:

- [ ] One governance task, no new governance follow-up/compatibility task.
- [ ] Active non-test governance execution LOC is lower on the exact frozen inventory.
- [ ] No new controller, executable, module or risk classifier.
- [ ] Historical terminal PASS and old in-flight protocol readers still validate.
- [ ] Fast scope ignores unrelated peer artifacts but rejects unowned/intersecting drift.
- [ ] Latest failed required result cannot be hidden by an earlier success.
- [ ] Self/stale/nonzero review and protocol downgrade fail.
- [ ] Explicit peer-manifest atomic isolation remains fail closed.
- [ ] The official-fee/source canary closes under current v2 with independent approval.
- [ ] Matching shadow receipt exists only under the governance artifact.
- [ ] Governance activation is terminal PASS before any real task selects fast close.
- [ ] The first actual fast task produces one scope candidate, one review and one accept.
- [ ] A local integration checkpoint exists; nothing was pushed.
- [ ] Updated remaining-duration range is evidence-based.
